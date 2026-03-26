import logging
import sys
from datetime import datetime
from pathlib import Path

from config.settings import settings


def setup_logger(endpoint_name: str) -> logging.Logger:
    """
    Cria e retorna um logger nomeado para a execução atual.
    Gera um arquivo de log em logs/ com nome: {endpoint}_{YYYYMMDD_HHMMSS}.log
    """
    logs_dir = settings.general.logs_path
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = logs_dir / f"{endpoint_name}_{timestamp}.log"

    logger = logging.getLogger(f"{endpoint_name}_{timestamp}")
    logger.setLevel(logging.DEBUG)

    # Evita duplicar handlers se o logger já foi configurado
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler para arquivo
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logger inicializado. Arquivo de log: {log_filename}")
    return logger
