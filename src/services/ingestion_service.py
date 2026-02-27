import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import traceback

from config.settings import settings
from models.product import Product
from services.logger_service import build_logger
from utils.utils import process_image
from services.nas_storage_service import NASStorageService
from services.gcs_storage_service import GCSStorageService


class IngestionService:

    def __init__(self):

        self.logger = build_logger("ingest")

        self.nas = NASStorageService(settings.NAS_ROOT)
        self.gcs = GCSStorageService(settings.GCS_BUCKET)

    def process_excel(self, excel_path: str):

        self.logger.info(f"Iniciando ingestão: {excel_path}")

        df = pd.read_excel(excel_path).fillna("")

        processed = []
        landing_files_to_delete = []

        next_id = 1

        for index, row in df.iterrows():

            try:
                product = Product(row.to_dict())

                if not product.id_produto:
                    raise ValueError("Id_produto vazio na planilha")

                product.generate_special_key()
                next_id += 1

                self.logger.info(f"Iniciando produto ID {product.id_produto}")

                result = self._process_product(product)

                if result:
                    if isinstance(result, list):
                        landing_files_to_delete.extend(result)
                    else:
                        landing_files_to_delete.append(result)

                processed.append(product)

                self.logger.info(f"Produto {product.id_produto} processado com sucesso")

            except Exception as e:
                self.logger.error(
                    f"Erro linha {index}: {e}\n{traceback.format_exc()}"
                )

        self._save_excel(processed)
        self._cleanup_landing(landing_files_to_delete)

        self.logger.info("Ingestão finalizada")

        return {"processed": len(processed)}

    def _process_product(self, product: Product):

        try:
            if product.caminho_imagem_secundaria and \
            product.caminho_imagem_secundaria != "Processada":

                return self._process_secondary(product)

            return self._process_primary(product)

        except Exception as e:
            self.logger.error(f"Erro no processamento do produto {product.id_produto}: {e}")
            raise

    def _process_primary(self, product):

        path = settings.LANDING_ROOT / product.caminho_temporario

        if not path.exists():
            self.logger.warning(f"Imagem principal não encontrada: {path}")
            return None

        try:
            filename = f"{product.id_produto}.jpg"

            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)

            temp = temp_dir / filename

            process_image(path, temp)

            relative = Path("images_zone") / str(product.id_produto) / filename

            self.nas.save(temp, relative)
            # bucket_path = self.gcs.save(temp, relative)

            product.set_final_image_path(str(relative))
            # product.caminho_bucket = bucket_path

            self._save_json(product)

            self.logger.info(f"Imagem principal salva: {relative}")

            return path

        except Exception as e:
            self.logger.error(f"Erro processando imagem principal: {e}")
            raise

    def _process_secondary(self, product):

        processed_secondary = []

        images = [
            p.strip()
            for p in product.caminho_imagem_secundaria.split("/")
            if p.strip()
        ]

        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        for i, img_name in enumerate(images):

            path = settings.LANDING_ROOT / img_name

            if not path.exists():
                self.logger.warning(f"Imagem secundária não encontrada: {path}")
                continue

            try:
                suffix = letters[i]
                filename = f"{product.id_produto}{suffix}.jpg"

                temp_dir = Path("temp")
                temp_dir.mkdir(exist_ok=True)

                temp = temp_dir / filename

                process_image(path, temp)

                relative = Path("images_zone") / str(product.id_produto) / filename

                self.nas.save(temp, relative)
                # bucket_path = self.gcs.save(temp, relative)

                processed_secondary.append(path)

                self.logger.info(f"Imagem secundária salva: {relative}")

            except Exception as e:
                self.logger.error(
                    f"Erro imagem secundária {img_name}: {e}\n{traceback.format_exc()}"
                )

        product.caminho_imagem_secundaria = "Processada"

        self._save_json(product)

        return processed_secondary if processed_secondary else None


    def _save_json(self, product):

        try:
            settings.DATA_FOLDER.mkdir(exist_ok=True)

            path = settings.DATA_FOLDER / f"{product.id_produto}.json"

            with open(path, "w", encoding="utf-8") as f:
                json.dump(product.to_dict(), f, indent=2, ensure_ascii=False)

            self.logger.info(f"JSON salvo: {path}")

        except Exception as e:
            self.logger.error(f"Erro salvando JSON {product.id_produto}: {e}")
            raise


    def _save_excel(self, products):

        try:
            data = [p.to_dict() for p in products]
            df = pd.DataFrame(data)

            df.to_excel("catalogo_processado.xlsx", index=False)

            self.logger.info("Excel salvo com sucesso")

        except Exception as e:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fallback = f"catalogo_processado_{ts}.xlsx"

            df.to_excel(fallback, index=False)

            self.logger.warning(f"Erro ao salvar Excel padrão. Criado fallback: {fallback}")

    def _cleanup_landing(self, files):

        self.logger.info("Iniciando limpeza da landing")

        for file_path in files:

            try:
                if file_path.exists():
                    file_path.unlink()
                    self.logger.info(f"Removido da landing: {file_path}")

            except Exception as e:
                self.logger.error(f"Erro removendo {file_path}: {e}")