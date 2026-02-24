from infrastructure.loaders.excel_loader import ExcelLoader
from services.ingestion_service import IngestionService
from config.settings import settings
from infrastructure.storage.nas_storage import NASStorage
from infrastructure.storage.gcs_storage import GCSStorage


class IngestionPipeline:

    def __init__(self):

        self.loader = ExcelLoader()

        self.ingestion_service = IngestionService(
            storages=[
                NASStorage(settings.IMAGES_ZONE_ROOT),
                # GCSStorage("meu-bucket")  # ativa depois
            ]
        )

    # --------------------------------------------------

    def run(self, excel_path: str):

        products = self.loader.load(excel_path)

        processed = []
        errors = []

        for idx, product in enumerate(products):

            try:
                result = self.ingestion_service.ingest(product)
                processed.append(result.to_dict())

            except Exception as e:
                errors.append({
                    "row": idx,
                    "error": str(e)
                })

        return {
            "processed_count": len(processed),
            "error_count": len(errors),
            "errors": errors,
        }