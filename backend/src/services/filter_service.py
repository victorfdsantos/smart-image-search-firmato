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

_INDEX_FILE = settings.nas.utils / "filters.json"

class FilterService:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def get_options(self, active_filters: dict[str, list[str]]) -> dict[str, list[str]]:
        self.logger.info(f"[Filter] active_filters={active_filters}")

        index = self._load()

        all_ids = set()
        for field in index:
            for ids in index[field].values():
                all_ids.update(ids)

        self.logger.debug(f"[Filter] total_ids={len(all_ids)}")

        current_ids = all_ids

        for field, selected_values in active_filters.items():
            if not selected_values:
                continue

            field_ids = set()
            for val in selected_values:
                field_ids.update(index.get(field, {}).get(val, []))

            self.logger.debug(
                f"[Filter] field={field} selected={selected_values} matched_ids={len(field_ids)}"
            )

            current_ids = current_ids.intersection(field_ids)

            self.logger.debug(
                f"[Filter] após '{field}' → current_ids={len(current_ids)}"
            )

        if not current_ids:
            self.logger.warning("[Filter] Nenhum produto após aplicar filtros")

        options = {}

        for field in index:
            valid_values = []

            for val, ids in index[field].items():
                if current_ids.intersection(ids):
                    valid_values.append(val)

            options[field] = sorted(valid_values)

        self.logger.debug(
            "[Filter] options_counts=" +
            ", ".join(f"{f}={len(v)}" for f, v in options.items())
        )

        return options
    
    def get_filtered_ids(self, active_filters: dict[str, list[str]]) -> set[int]:
        index = self._load()

        all_ids = set()
        for field in index:
            for ids in index[field].values():
                all_ids.update(ids)

        current_ids = all_ids

        for field, selected_values in active_filters.items():
            if not selected_values:
                continue

            field_ids = set()
            for val in selected_values:
                field_ids.update(index.get(field, {}).get(val, []))

            current_ids = current_ids.intersection(field_ids)

        return set(int(i) for i in current_ids)
    
    def _load(self) -> dict:
        if not _INDEX_FILE.exists():
            return {f: {} for f in FILTER_FIELDS}
        with open(_INDEX_FILE, encoding="utf-8") as f:
            return json.load(f)