import json
import logging
from pathlib import Path
from typing import Optional

from config.settings import settings
from models.product_model import ProductModel


class JsonService:
    """
    Responsável por salvar e carregar os arquivos JSON
    de cada produto em data/{ID}.json.
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.data_dir = settings.general.data_path

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def save(self, model: ProductModel, product_id: int) -> bool:
        """
        Serializa o ProductModel e salva em data/{product_id}.json.
        Retorna True em sucesso.
        """
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            json_path = self.data_dir / f"{product_id}.json"
            model_data = model.to_dict()

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(model_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"[JSON] Salvo: {json_path}")
            return True
        except Exception as exc:
            self.logger.error(
                f"[JSON] Erro ao salvar produto {product_id}: {exc}", exc_info=True
            )
            return False

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    def load(self, product_id: int) -> Optional[dict]:
        """
        Carrega o JSON de um produto pelo ID.
        Retorna None se não existir ou falhar.
        """
        try:
            json_path = self.data_dir / f"{product_id}.json"
            if not json_path.exists():
                self.logger.debug(f"[JSON] Não encontrado para id {product_id}: {json_path}")
                return None
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.logger.debug(f"[JSON] Carregado: {json_path}")
            return data
        except Exception as exc:
            self.logger.error(
                f"[JSON] Erro ao carregar produto {product_id}: {exc}", exc_info=True
            )
            return None

    # ------------------------------------------------------------------
    # Verificação
    # ------------------------------------------------------------------

    def exists(self, product_id: int) -> bool:
        """Retorna True se o JSON do produto já existe em disco."""
        return (self.data_dir / f"{product_id}.json").exists()
