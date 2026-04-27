from typing import Optional
from pydantic import BaseModel, Field


class ProcessCatalogResponse(BaseModel):
    """Resposta do endpoint POST /catalog/process."""
    status: str
    elapsed_seconds: float
    total_rows: int
    new_products: int
    images_updated: int
    data_updated: int
    removed: int
    image_errors: int
    retrain_clip_ids: list[str]
    retrain_data_ids: list[str]
    retrain_status: str           # "completed" | "partial" | "skipped" | "error"
    retrain_clip_updated: int
    retrain_text_updated: int
    retrain_errors: list[str]
    errors: list[str]


class TrainingRequest(BaseModel):
    """Payload para POST /catalog/retrain (uso administrativo)."""
    image_ids: list[str] = Field(
        default_factory=list,
        description="IDs com imagem nova ou alterada → regenera embedding CLIP.",
        examples=[["42", "77"]],
    )
    data_ids: list[str] = Field(
        default_factory=list,
        description="IDs com JSON novo ou alterado → regenera embedding de texto + BM25.",
        examples=[["42", "100", "101"]],
    )


class TrainingResponse(BaseModel):
    """Resposta do endpoint POST /catalog/retrain."""
    status: str
    elapsed_seconds: float
    clip_updated: int
    text_updated: int
    bm25_rebuilt: bool
    errors: list[str]