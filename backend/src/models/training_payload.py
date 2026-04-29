from pydantic import BaseModel
from typing import Optional

class TrainingPayload(BaseModel):
    image_ids: list[str]
    data_ids: list[str]