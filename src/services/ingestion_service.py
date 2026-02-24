from pathlib import Path
from typing import List
from config.settings import settings

from entities.product import Product
from services.hashing_service import HashingService
from services.image_path_builder import ImagePathBuilder
from infrastructure.image.image_processor import ImageProcessor
from infrastructure.storage.base_storage import BaseStorage


class IngestionService:
    """
    Serviço responsável pela ingestão completa de um produto.
    """

    def __init__(
        self,
        storages: List[BaseStorage],
        temp_dir: str = "/tmp/ai_catalog",
    ):
        self.hashing_service = HashingService()
        self.path_builder = ImagePathBuilder()
        self.image_processor = ImageProcessor()

        self.storages = storages
        self.temp_dir = Path(temp_dir)

        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def ingest(self, product: Product) -> Product:
        """
        Executa ingestão completa de um produto.
        """

        # 1️⃣ gerar ID determinístico
        product_id = self.hashing_service.generate_product_id(product)

        # 2️⃣ construir caminho relativo final
        relative_path = self.path_builder.build_relative_path(product)

        # 3️⃣ processar imagem
        temp_output = self._build_temp_path(product_id)

        relative_image_path = product.data.get("Endereço_Imagem")

        if not relative_image_path:
            raise ValueError("Produto sem Endereço_Imagem")

        input_image_path = (
            settings.LANDING_ZONE_ROOT / relative_image_path
        )

        input_image_path = str(input_image_path)

        if not input_image_path:
            raise ValueError("Produto sem Endereço_Imagem")

        self.image_processor.process(
            input_image_path,
            temp_output,
        )

        # 4️⃣ salvar em todos os storages
        for storage in self.storages:
            storage.save(temp_output, relative_path)

        # 5️⃣ atualizar metadata do produto
        product.set_endereco_imagem(relative_path)

        return product

    def _build_temp_path(self, product_id: str) -> str:
        return str(self.temp_dir / f"{product_id}.jpg")