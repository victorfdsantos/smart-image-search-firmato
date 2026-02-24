from pathlib import Path
import shutil
import uuid

from fastapi import UploadFile, HTTPException
from pipeline.ingestion_pipeline import IngestionPipeline


class IngestionController:

    def __init__(self):
        self.pipeline = IngestionPipeline()
        self.upload_dir = Path("/tmp/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def ingest(self, file: UploadFile):

        if not file.filename.endswith((".xlsx", ".xls")):
            raise HTTPException(400, "Arquivo deve ser Excel")

        temp_path = self.upload_dir / f"{uuid.uuid4()}_{file.filename}"

        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = self.pipeline.run(str(temp_path))

        return {
            "status": "finished",
            **result
        }