from pathlib import Path

class Settings:

    LANDING_ROOT = Path("landing_zone")

    NAS_ROOT = Path("local_nas")

    GCS_BUCKET = "firmato-images"

    DATA_FOLDER = Path("data")

    LOG_FOLDER = Path("logs")

settings = Settings()