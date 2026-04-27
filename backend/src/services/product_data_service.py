"""
ProductDataService — gerencia os arquivos data/{id}.json de cada produto.

Campos de caminho (output, thumbnail) são preenchidos pelo CatalogService
e nunca lidos da planilha.
"""

import json
import logging
from typing import Optional

from config.settings import settings

# Colunas da planilha → chaves no JSON
COLUMN_MAP: dict[str, str] = {
    "Id_produto":              "id_produto",
    "Chave_Especial":          "chave_especial",
    "Nome_Produto":            "nome_produto",
    "Marca":                   "marca",
    "Status":                  "status",
    "Categoria_Principal":     "categoria_principal",
    "Subcategoria":            "subcategoria",
    "Ambiente":                "ambiente",
    "Forma":                   "forma",
    "Material_Principal":      "material_principal",
    "Material_Estrutura":      "material_estrutura",
    "Material_Revestimento":   "material_revestimento",
    "Altura_cm":               "altura_cm",
    "Largura_cm":              "largura_cm",
    "Profundidade_cm":         "profundidade_cm",
    "Faixa_Preco":             "faixa_preco",
    "Descricao_Tecnica":       "descricao_tecnica",
}

# Colunas de caminho — nunca lidas da planilha; mantidas programaticamente
PATH_COLS = {
    "caminho_output",
    "caminho_thumbnail"
}


def _clean(val) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip()
    return s if s and s.lower() not in ("nan", "none", "") else None


class ProductDataService:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.data_dir = settings.nas.data

    # ------------------------------------------------------------------
    # Load / Save
    # ------------------------------------------------------------------

    def load(self, product_id: str) -> Optional[dict]:
        path = self.data_dir / f"{product_id}.json"
        if not path.exists():
            return None
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            self.logger.error(f"[Data] Erro ao carregar {product_id}.json: {exc}", exc_info=True)
            return None

    def save(self, product_id: str, data: dict) -> bool:
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            path = self.data_dir / f"{product_id}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump({k: v for k, v in data.items() if v is not None}, f,
                          ensure_ascii=False, indent=2)
            self.logger.info(f"[Data] Salvo: {path}")
            return True
        except Exception as exc:
            self.logger.error(f"[Data] Erro ao salvar {product_id}.json: {exc}", exc_info=True)
            return False

    def delete(self, product_id: str) -> None:
        path = self.data_dir / f"{product_id}.json"
        if path.exists():
            path.unlink()
            self.logger.info(f"[Data] Removido: {path}")

    # ------------------------------------------------------------------
    # Construção do dict a partir da linha da planilha
    # ------------------------------------------------------------------

    def row_to_dict(self, row: dict) -> dict:
        """
        Converte linha da planilha → dict para o JSON.
        Não preenche campos de caminho — esses são adicionados pelo CatalogService.
        """
        result: dict = {}
        for col, key in COLUMN_MAP.items():
            val = _clean(row.get(col))
            if val is not None:
                result[key] = val
        return result

    # ------------------------------------------------------------------
    # Merge de caminhos
    # ------------------------------------------------------------------

    def merge_paths(self, existing: Optional[dict], new_paths: dict) -> dict:
        """
        Mescla new_paths (caminhos atualizados) sobre o JSON existente.
        Campos de dados do JSON existente são preservados se não substituídos.
        """
        base = dict(existing) if existing else {}
        base.update(new_paths)
        return base

    # ------------------------------------------------------------------
    # Marca produto como removido (inativo)
    # ------------------------------------------------------------------

    def mark_removed(self, product_id: str) -> None:
        data = self.load(product_id)
        if data is None:
            return
        data["status"] = "inativo"
        self.save(product_id, data)
        self.logger.info(f"[Data] Produto {product_id} marcado como inativo.")