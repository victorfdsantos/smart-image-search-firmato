from pydantic import BaseModel
from typing import List, Dict, Any


class ProcessCatalogResponse(BaseModel):
    status: str
    elapsed_seconds: float

    processed: int
    skipped: int
    errors: int

    updated_ids: List[str]

    # opcionais (debug / interno)
    landing_map: Dict[str, str]
    sharepoint_updates: List[Dict[str, Any]]