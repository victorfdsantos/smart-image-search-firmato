import hashlib
import logging
from typing import Tuple
from PIL import Image
from io import BytesIO
from config.settings import settings

class ImageProcessingService:

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.s = settings.image

    # --------------------------------------------------
    # PUBLIC
    # --------------------------------------------------

    def process(self, image_bytes: bytes, product_id: str) -> Tuple[bytes, bytes]:
        """
        Processa imagem e retorna:
        (output_bytes, thumbnail_bytes)
        """
        try:
            img = Image.open(BytesIO(image_bytes))
            img = self._to_rgb(img)

            output = self._resize(img, self.s.output_width, self.s.output_height)
            thumb  = self._resize(img, self.s.thumb_width, self.s.thumb_height)

            output_bytes = self._to_jpeg_bytes(output)
            thumb_bytes  = self._to_jpeg_bytes(thumb)

            self.logger.info(f"[Image] Processado: {product_id}")

            return output_bytes, thumb_bytes

        except Exception as exc:
            self.logger.error(f"[Image] Falha ao processar {product_id}: {exc}", exc_info=True)
            raise

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    def _resize(self, img: Image.Image, max_w: int, max_h: int) -> Image.Image:
        img = img.copy()
        img.thumbnail((max_w, max_h), Image.LANCZOS)
        return img

    def _to_rgb(self, img: Image.Image) -> Image.Image:
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
            return bg
        return img.convert("RGB") if img.mode != "RGB" else img

    def _to_jpeg_bytes(self, img: Image.Image) -> bytes:
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=self.s.jpeg_quality, optimize=True)
        return buffer.getvalue()

    # --------------------------------------------------
    # NAMING
    # --------------------------------------------------

    @staticmethod
    def filename(product_id: str) -> str:
        return f"{product_id}.jpg"

    # --------------------------------------------------
    # HASH
    # --------------------------------------------------

    @staticmethod
    def generate_hash(row: dict, hash_columns: list[str]) -> str:
        raw = "|".join(str(row.get(c, "")).strip() for c in hash_columns)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()