"""
MirrorService — gerencia o espelho CSV da planilha do SharePoint.

O arquivo utils/catalog_mirror.csv é a "foto" do catálogo após o último
processamento bem-sucedido. É usado para calcular o delta entre execuções:
 - linhas novas   → processar do zero
 - linhas alteradas → atualizar imagens e/ou dados
 - linhas removidas → marcar como inativo no JSON (não deletamos dados)

Colunas que definem "alteração de imagem":
  Caminho_Imagem, Caminho_Imagem_Secundaria1/2/3

Colunas que definem "alteração de dados":
  qualquer outra coluna (exceto as de caminho acima e Id_produto).
"""

import csv
import logging
from pathlib import Path
from typing import Optional

from config.settings import settings

_IMAGE_COLS = {
    "Caminho_Imagem",
    "Caminho_Imagem_Secundaria1",
    "Caminho_Imagem_Secundaria2",
    "Caminho_Imagem_Secundaria3",
}

_MIRROR_FILE = settings.nas.utils / "catalog_mirror.csv"


def _clean(val) -> str:
    if val is None:
        return ""
    return str(val).strip()


class DeltaResult:
    """Resultado da comparação entre planilha atual e mirror CSV."""

    def __init__(self):
        # id → row_dict (planilha atual)
        self.new_products: dict[str, dict] = {}
        # id → row_dict (planilha atual) + flags
        self.image_changed: dict[str, dict] = {}
        self.data_changed: dict[str, dict] = {}
        # id → row_dict (mirror — produto que sumiu da planilha)
        self.removed_ids: set[str] = set()

    @property
    def all_changed_ids(self) -> set[str]:
        return (
            set(self.new_products)
            | set(self.image_changed)
            | set(self.data_changed)
        )

    @property
    def image_ids(self) -> list[str]:
        """IDs que precisam de retreinamento CLIP."""
        return list(set(self.new_products) | set(self.image_changed))

    @property
    def data_ids(self) -> list[str]:
        """IDs que precisam de retreinamento de texto."""
        return list(
            set(self.new_products) | set(self.data_changed) | set(self.image_changed)
        )


class MirrorService:

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    def load_mirror(self) -> dict[str, dict]:
        """
        Carrega o mirror CSV como dict id_produto → row_dict.
        Retorna dict vazio se o arquivo não existir (primeiro carregamento).
        """
        if not _MIRROR_FILE.exists():
            self.logger.info("[Mirror] Nenhum mirror encontrado — primeiro carregamento.")
            return {}

        mirror: dict[str, dict] = {}
        with open(_MIRROR_FILE, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = _clean(row.get("Id_produto"))
                if pid:
                    mirror[pid] = dict(row)

        self.logger.info(f"[Mirror] {len(mirror)} linhas carregadas do mirror.")
        return mirror

    # ------------------------------------------------------------------
    # Comparação
    # ------------------------------------------------------------------

    def compute_delta(
        self,
        current_rows: list[dict],
    ) -> DeltaResult:
        """
        Compara as linhas atuais da planilha com o mirror em disco.
        Retorna um DeltaResult descrevendo o que mudou.
        """
        mirror = self.load_mirror()
        result = DeltaResult()

        current_ids: set[str] = set()

        for row in current_rows:
            pid = _clean(row.get("Id_produto"))
            if not pid:
                continue
            current_ids.add(pid)

            if pid not in mirror:
                # Produto novo
                result.new_products[pid] = row
                self.logger.debug(f"[Mirror] Id {pid}: NOVO")
                continue

            old = mirror[pid]

            img_changed = any(
                _clean(row.get(c)) != _clean(old.get(c))
                for c in _IMAGE_COLS
            )
            data_changed = any(
                _clean(row.get(k)) != _clean(old.get(k))
                for k in row
                if k not in _IMAGE_COLS and k != "Id_produto"
            )

            if img_changed:
                result.image_changed[pid] = row
                self.logger.debug(f"[Mirror] Id {pid}: imagem ALTERADA")
            if data_changed:
                result.data_changed[pid] = row
                self.logger.debug(f"[Mirror] Id {pid}: dados ALTERADOS")

        # Produtos que estavam no mirror mas sumiram
        result.removed_ids = set(mirror) - current_ids
        if result.removed_ids:
            self.logger.info(
                f"[Mirror] {len(result.removed_ids)} produto(s) removido(s) da planilha."
            )

        self.logger.info(
            f"[Mirror] Delta: novos={len(result.new_products)} "
            f"img_changed={len(result.image_changed)} "
            f"data_changed={len(result.data_changed)} "
            f"removed={len(result.removed_ids)}"
        )
        return result

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def save_mirror(self, rows: list[dict]) -> None:
        """
        Salva o espelho CSV com as linhas atuais (após edições de caminho).
        Sobrescreve o arquivo anterior.
        """
        if not rows:
            self.logger.warning("[Mirror] Nenhuma linha para salvar no mirror.")
            return

        _MIRROR_FILE.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys())

        with open(_MIRROR_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        self.logger.info(f"[Mirror] Mirror salvo: {len(rows)} linhas → {_MIRROR_FILE}")