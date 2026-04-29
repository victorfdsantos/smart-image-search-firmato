import logging
import re
from typing import Dict, List

FILTER_FIELDS = [
    "marca",
    "categoria_principal",
    "subcategoria",
    "faixa_preco",
    "ambiente",
    "forma",
    "material_principal",
]

# Mapeamento coluna SharePoint → campo interno
_COL_TO_FIELD = {
    "Marca":               "marca",
    "Categoria_Principal": "categoria_principal",
    "Subcategoria":        "subcategoria",
    "Faixa_Preco":         "faixa_preco",
    "Ambiente":            "ambiente",
    "Forma":               "forma",
    "Material_Principal":  "material_principal",
}

def _clean(val) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    return "" if s.lower() in ("nan", "none") else s

def _split(raw: str) -> List[str]:
    return [p.strip() for p in re.split(r"\s*/\s*", raw) if p.strip()]


class FilterService:

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.index: Dict[str, Dict[str, List[int]]] = {f: {} for f in FILTER_FIELDS}

    # --------------------------------------------------
    # BUILD (1x após load do catálogo)
    # --------------------------------------------------

    def build(self, rows: List[dict]) -> None:
        index = {f: {} for f in FILTER_FIELDS}

        for row in rows:
            if _clean(row.get("Status")).lower() != "ativo":
                continue

            pid_raw = _clean(row.get("Id_produto"))
            if not pid_raw:
                continue

            try:
                pid = int(float(pid_raw))
            except:
                continue

            for col, field in _COL_TO_FIELD.items():
                raw = _clean(row.get(col))
                if not raw:
                    continue

                for val in _split(raw):
                    index[field].setdefault(val, []).append(pid)

        # opcional: ordenar
        for field in index:
            for val in index[field]:
                index[field][val].sort()

        self.index = index

        self.logger.info(
            "[Filter] Index built: "
            + ", ".join(f"{f}={len(index[f])}" for f in FILTER_FIELDS)
        )

    # --------------------------------------------------
    # GET FILTER OPTIONS (cascata)
    # --------------------------------------------------

    def get_options(self, active_filters: Dict[str, List[str]]) -> Dict[str, List[str]]:
        current_ids = None

        for field, values in active_filters.items():
            if not values:
                continue

            ids = set()
            for v in values:
                ids.update(self.index.get(field, {}).get(v, []))

            if current_ids is None:
                current_ids = ids
            else:
                current_ids &= ids

        if current_ids is None:
            # nenhum filtro → retorna tudo
            return {
                f: sorted(self.index[f].keys())
                for f in FILTER_FIELDS
            }

        # cascata
        options = {}

        for field in FILTER_FIELDS:
            valid = []

            for val, ids in self.index[field].items():
                if current_ids.intersection(ids):
                    valid.append(val)

            options[field] = sorted(valid)

        return options

    # --------------------------------------------------
    # GET IDS (para ProductService)
    # --------------------------------------------------

    def get_filtered_ids(self, active_filters: Dict[str, List[str]]) -> set[int]:
        current_ids = None

        for field, values in active_filters.items():
            if not values:
                continue

            ids = set()
            for v in values:
                ids.update(self.index.get(field, {}).get(v, []))

            if current_ids is None:
                current_ids = ids
            else:
                current_ids &= ids

        return current_ids or set()