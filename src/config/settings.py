from pathlib import Path
import os


class Settings:

    # -----------------------------------
    # Ambiente
    # -----------------------------------
    ENV = os.getenv("ENV", "local")
    LANDING_ZONE_ROOT = Path(
        os.getenv("LANDING_ZONE_ROOT", "./landing_zone")
    )

    IMAGES_ZONE_ROOT = Path(
        os.getenv("IMAGES_ZONE_ROOT", "./images_zone")
    )
    GCS_BUCKET = os.getenv("GCS_BUCKET", "")


settings = Settings()