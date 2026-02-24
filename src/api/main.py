from fastapi import FastAPI, UploadFile, File
from controllers.ingestion_controller import IngestionController

app = FastAPI()

controller = IngestionController()

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    return await controller.ingest(file)


@app.get("/health")
def health():
    return {"status": "ok"}