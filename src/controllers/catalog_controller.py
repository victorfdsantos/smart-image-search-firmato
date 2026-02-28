import logging
from pathlib import Path

from services.catalog_service import CatalogService
from utils.logger import setup_logger


class CatalogController:
    """
    Controller responsável por receber a requisição de cadastro,
    validar os inputs e acionar o CatalogService.
    """

    ENDPOINT_NAME = "catalog_register"

    def __init__(self):
        self.logger: logging.Logger = None

    # ------------------------------------------------------------------
    # Ação principal
    # ------------------------------------------------------------------

    def register_from_spreadsheet(self, xlsx_path: str) -> dict:
        """
        Ponto de entrada principal do processo de cadastro.

        Args:
            xlsx_path: Caminho para o arquivo .xlsx recebido.

        Returns:
            Dicionário com resultado da execução (stats + status).
        """
        self.logger = setup_logger(self.ENDPOINT_NAME)
        self.logger.info(f"CatalogController.register_from_spreadsheet iniciado.")
        self.logger.info(f"Planilha recebida: {xlsx_path}")

        try:
            # Validação do arquivo
            path = Path(xlsx_path)
            if not path.exists():
                msg = f"Arquivo não encontrado: {xlsx_path}"
                self.logger.error(msg)
                return {"status": "error", "message": msg}

            if path.suffix.lower() not in (".xlsx", ".xlsm"):
                msg = f"Formato de arquivo inválido: '{path.suffix}'. Esperado .xlsx ou .xlsm."
                self.logger.error(msg)
                return {"status": "error", "message": msg}

            # Executar serviço
            service = CatalogService(self.logger)
            stats = service.process_spreadsheet(path)

            self.logger.info("CatalogController: Processamento finalizado com sucesso.")
            return {
                "status": "success",
                "stats": stats,
            }

        except Exception as exc:
            self.logger.error(
                f"Erro inesperado no CatalogController: {exc}", exc_info=True
            )
            return {
                "status": "error",
                "message": str(exc),
            }
