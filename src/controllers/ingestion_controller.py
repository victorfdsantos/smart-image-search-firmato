from pathlib import Path
import shutil
import uuid

from fastapi import UploadFile, HTTPException
from services.ingestion_service import IngestionService


class IngestionController:

    def __init__(self):
        self.service = IngestionService()

        self.temp_dir = Path("temp_uploads")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def ingest(self, file: UploadFile):

        if not file.filename.endswith((".xlsx", ".xls")):
            raise HTTPException(400, "Arquivo deve ser Excel")

        temp_file = self.temp_dir / f"{uuid.uuid4()}_{file.filename}"

        with temp_file.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = self.service.process_excel(str(temp_file))

        return {
            "status": "finished",
            **result
        }