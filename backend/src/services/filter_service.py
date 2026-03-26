"""FilterService — retorna opções de filtro em cascata a partir dos data/*.json."""

import json
import logging
import re
from pathlib import Path
from typing import Optional

from config.settings import settings

# Campos suportados como filtro, na ordem de exibição
FILTER_FIELDS = [
    "marca",
    "categoria_principal",
    "subcategoria",
    "faixa_preco",
    "ambiente",
    "forma",
    "material_principal",
]

FILTER_LABELS = {
    "marca":               "Marca",
    "categoria_principal": "Categoria Principal",
    "subcategoria":        "Subcategoria",
    "faixa_preco":         "Faixa de Preço",
    "ambiente":            "Ambiente",
    "forma":               "Forma",
    "material_principal":  "Material Principal",
}


def _split_values(raw: str) -> list[str]:
    """
    Divide valores com '/' ou ' / ' em opções individuais.
    Ex: "Sala de Jantar / Cozinha / Varanda" → ["Sala de Jantar", "Cozinha", "Varanda"]
    """
    parts = re.split(r"\s*/\s*", raw.strip())
    return [p.strip() for p in parts if p.strip()]


class FilterService:

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.data_dir = settings.general.data_path

    def get_options(self, active_filters: dict[str, list[str]]) -> dict[str, list[str]]:
        """
        Retorna as opções disponíveis para cada campo de filtro,
        considerando apenas os produtos que passam nos filtros já ativos.

        active_filters: {field: [valor1, valor2, ...]}
        Retorna: {field: [opcao1, opcao2, ...]} — ordenado alfabeticamente
        """
        products = self._load_active_products()

        # Aplica os filtros ativos para restringir o conjunto base
        filtered = self._apply_filters(products, active_filters)

        # Para cada campo, coleta os valores únicos nos produtos filtrados
        options: dict[str, list[str]] = {}
        for field in FILTER_FIELDS:
            values: set[str] = set()
            for product in filtered:
                raw = product.get(field)
                if raw and str(raw).strip().lower() not in ("nan", "none", ""):
                    for v in _split_values(str(raw)):
                        values.add(v)
            options[field] = sorted(values)

        return options

    def _apply_filters(
        self, products: list[dict], filters: dict[str, list[str]]
    ) -> list[dict]:
        """
        Retorna apenas os produtos que satisfazem TODOS os filtros ativos.
        Para campos com '/', um produto passa se qualquer um dos seus sub-valores
        estiver na lista de filtros selecionados.
        """
        if not filters:
            return products

        result = []
        for product in products:
            match = True
            for field, selected_values in filters.items():
                if not selected_values:
                    continue
                raw = product.get(field)
                if not raw or str(raw).strip().lower() in ("nan", "none", ""):
                    match = False
                    break
                product_values = _split_values(str(raw))
                # Produto passa se tiver ao menos um valor em comum com os selecionados
                if not any(v in selected_values for v in product_values):
                    match = False
                    break
            if match:
                result.append(product)

        return result

    def filter_product_ids(self, filters: dict[str, list[str]]) -> set[int]:
        """
        Retorna o conjunto de IDs dos produtos que passam nos filtros.
        Usado pelo SearchService para pós-filtrar resultados.
        """
        if not filters:
            return None  # None = sem filtro, retorna tudo

        products = self._load_active_products()
        filtered = self._apply_filters(products, filters)
        return {int(p["id_produto"]) for p in filtered if p.get("id_produto")}

    def _load_active_products(self) -> list[dict]:
        products = []
        for json_path in self.data_dir.glob("*.json"):
            try:
                with open(json_path, encoding="utf-8") as f:
                    data = json.load(f)
                if str(data.get("status", "")).strip().lower() == "ativo":
                    products.append(data)
            except Exception as exc:
                self.logger.warning(f"[Filter] Erro ao ler {json_path}: {exc}")
        return products