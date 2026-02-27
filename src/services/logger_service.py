import logging
from datetime import datetime
from pathlib import Path
from config.settings import settings


def build_logger(endpoint: str):

    settings.LOG_FOLDER.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_path = settings.LOG_FOLDER / f"{endpoint}_{timestamp}.log"

    logger = logging.getLogger(timestamp)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger