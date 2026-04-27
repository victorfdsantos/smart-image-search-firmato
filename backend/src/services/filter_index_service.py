"""
FilterIndexService — constrói e mantém o índice de filtros em utils/filters.json.

Estrutura do JSON de saída:
{
  "marca": {
    "Estudio Bola": [1, 14, 16],
    "Artefacto": [3, 7]
  },
  "categoria_principal": { ... },
  "subcategoria": { ... },
  "faixa_preco": { ... },
  "ambiente": { ... },
  "forma": { ... },
  "material_principal": { ... }
}

Cada chave de filtro mapeia valor → lista de IDs de produto.
Valores compostos com '/' são explodidos em entradas individuais.

Uso no backend/frontend:
  - Para exibir opções do filtro: keys do dict do campo
  - Para filtrar por um valor: lookup direto pelo valor → IDs
  - Para cascata: interseção de IDs entre os filtros selecionados
"""

import json
import logging
import re
from pathlib import Path

from config.settings import settings

FILTER_FIELDS = [
    "marca",
    "categoria_principal",
    "subcategoria",
    "faixa_preco",
    "ambiente",
    "forma",
    "material_principal",
]

_INDEX_FILE = settings.nas.utils / "filters.json"

# Mapeamento coluna Excel → chave JSON
_COL_TO_FIELD = {
    "Marca":               "marca",
    "Categoria_Principal": "categoria_principal",
    "Subcategoria":        "subcategoria",
    "Faixa_Preco":         "faixa_preco",
    "Ambiente":            "ambiente",
    "Forma":               "forma",
    "Material_Principal":  "material_principal",
}


def _split(raw: str) -> list[str]:
    """'Sala / Cozinha / Varanda' → ['Sala', 'Cozinha', 'Varanda']"""
    return [p.strip() for p in re.split(r"\s*/\s*", raw.strip()) if p.strip()]


def _clean(val) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    return "" if s.lower() in ("nan", "none") else s


class FilterIndexService:

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    # ------------------------------------------------------------------
    # Construção completa (primeiro carregamento ou rebuild)
    # ------------------------------------------------------------------

    def build_from_rows(self, rows: list[dict]) -> dict:
        """
        Constrói o índice de filtros a partir das linhas da planilha.
        Considera apenas produtos com Status == 'Ativo'.
        Retorna o índice como dict e salva em disco.
        """
        index: dict[str, dict[str, list[int]]] = {f: {} for f in FILTER_FIELDS}

        for row in rows:
            if _clean(row.get("Status")).lower() != "ativo":
                continue
            pid_raw = _clean(row.get("Id_produto"))
            if not pid_raw:
                continue
            try:
                pid = int(float(pid_raw))
            except ValueError:
                continue

            for col, field in _COL_TO_FIELD.items():
                raw = _clean(row.get(col))
                if not raw:
                    continue
                for val in _split(raw):
                    index[field].setdefault(val, [])
                    if pid not in index[field][val]:
                        index[field][val].append(pid)

        # Ordena IDs e valores
        for field in index:
            index[field] = {
                k: sorted(v)
                for k, v in sorted(index[field].items())
            }

        self._save(index)
        self.logger.info(
            "[FilterIndex] Índice construído: "
            + " | ".join(f"{f}={len(index[f])} vals" for f in FILTER_FIELDS)
        )
        return index

    # ------------------------------------------------------------------
    # Atualização incremental
    # ------------------------------------------------------------------

    def upsert_product(self, pid: int, row: dict, is_active: bool) -> None:
        """
        Atualiza o índice para um único produto.
        Se is_active=False, remove o produto de todos os filtros.
        """
        index = self._load()

        # Remove o pid de todas as entradas atuais
        for field in FILTER_FIELDS:
            for val in list(index[field].keys()):
                if pid in index[field][val]:
                    index[field][val].remove(pid)
                if not index[field][val]:
                    del index[field][val]

        if is_active:
            for col, field in _COL_TO_FIELD.items():
                raw = _clean(row.get(col))
                if not raw:
                    continue
                for val in _split(raw):
                    index[field].setdefault(val, [])
                    if pid not in index[field][val]:
                        index[field][val].append(pid)
                        index[field][val].sort()

        self._save(index)

    def remove_product(self, pid: int) -> None:
        self.upsert_product(pid, {}, is_active=False)

    # ------------------------------------------------------------------
    # I/O
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        if not _INDEX_FILE.exists():
            return {f: {} for f in FILTER_FIELDS}
        with open(_INDEX_FILE, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, index: dict) -> None:
        _INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        self.logger.info(f"[FilterIndex] Salvo em {_INDEX_FILE}")