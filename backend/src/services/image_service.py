"""
ImageProcessingService — processa imagens da landing para output e thumbnail.

Estrutura NAS (flat):
  nas/landing/{qualquer_nome}.{ext}   → imagem bruta do usuário
  nas/output/{id}.jpg                 → imagem processada 1080×1080 (máx)
  nas/output/{id}A.jpg                → imagem secundária slot 1
  nas/thumbnail/{id}.jpg              → thumbnail 250×250
  nas/thumbnail/{id}A.jpg             → thumbnail secundária slot 1
"""

import hashlib
import logging
import string
from pathlib import Path
from typing import Optional

from PIL import Image

from config.settings import settings

_SECONDARY_SUFFIX = list(string.ascii_uppercase)  # A, B, C …


def _fit_image(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    """Redimensiona mantendo proporção dentro do bounding box."""
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    return img


def _to_rgb(img: Image.Image) -> Image.Image:
    if img.mode in ("RGBA", "P", "LA"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
        return bg
    return img.convert("RGB") if img.mode != "RGB" else img


class ImageService:

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.s = settings.image
        self.nas = settings.nas

    # ------------------------------------------------------------------
    # Nomenclatura
    # ------------------------------------------------------------------

    @staticmethod
    def primary_filename(product_id: str) -> str:
        return f"{product_id}.jpg"

    @staticmethod
    def secondary_filename(product_id: str, slot_index: int) -> str:
        """slot_index 0 → A, 1 → B, …"""
        suffix = _SECONDARY_SUFFIX[slot_index] if slot_index < len(_SECONDARY_SUFFIX) else f"_{slot_index}"
        return f"{product_id}{suffix}.jpg"

    # ------------------------------------------------------------------
    # Localização na landing
    # ------------------------------------------------------------------

    def find_in_landing(self, name_without_ext: str) -> Optional[Path]:
        """
        Procura {name_without_ext}.{ext} na pasta landing.
        Retorna o Path se encontrar, None caso contrário.
        """
        for ext in self.s.allowed_extensions:
            candidate = self.nas.landing / f"{name_without_ext}{ext}"
            if candidate.exists():
                self.logger.debug(f"[Image] Encontrado na landing: {candidate}")
                return candidate
        self.logger.warning(
            f"[Image] '{name_without_ext}' não encontrado na landing "
            f"(extensões: {self.s.allowed_extensions})"
        )
        return None

    # ------------------------------------------------------------------
    # Processamento
    # ------------------------------------------------------------------

    def process(
        self,
        source: Path,
        output_filename: str,
    ) -> bool:
        """
        Processa uma imagem:
          1. Converte para RGB
          2. Salva em output/ com tamanho máximo output_width × output_height
          3. Salva em thumbnail/ com tamanho máximo thumb_width × thumb_height

        Retorna True em sucesso.
        """
        try:
            self.nas.output.mkdir(parents=True, exist_ok=True)
            self.nas.thumbnail.mkdir(parents=True, exist_ok=True)

            with Image.open(source) as raw:
                img = _to_rgb(raw.copy())

            # — Output (grande) —
            out_img = img.copy()
            _fit_image(out_img, self.s.output_width, self.s.output_height)
            out_path = self.nas.output / output_filename
            out_img.save(out_path, "JPEG", quality=self.s.jpeg_quality, optimize=True)

            # — Thumbnail (pequeno) —
            thumb_img = img.copy()
            _fit_image(thumb_img, self.s.thumb_width, self.s.thumb_height)
            thumb_path = self.nas.thumbnail / output_filename
            thumb_img.save(thumb_path, "JPEG", quality=self.s.jpeg_quality, optimize=True)

            self.logger.info(
                f"[Image] Processado: {source.name} → output/{output_filename} + thumbnail/{output_filename}"
            )
            return True

        except Exception as exc:
            self.logger.error(
                f"[Image] Falha ao processar '{source}': {exc}", exc_info=True
            )
            return False

    def delete(self, filename: str) -> None:
        """Remove imagem de output/ e thumbnail/ (ignora se não existir)."""
        for folder in (self.nas.output, self.nas.thumbnail):
            path = folder / filename
            if path.exists():
                path.unlink()
                self.logger.info(f"[Image] Removido: {path}")

    # ------------------------------------------------------------------
    # Hash
    # ------------------------------------------------------------------

    @staticmethod
    def generate_hash(row: dict, hash_columns: list[str]) -> str:
        raw = "|".join(str(row.get(c, "")).strip() for c in hash_columns)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()