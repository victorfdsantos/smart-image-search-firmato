from PIL import Image, ImageOps
from pathlib import Path


class ImageProcessor:
    """
    Processa imagens para padronização do catálogo.
    """

    MAX_SIZE = 1080
    QUALITY = 85

    def process(self, input_path: str, output_path: str) -> str:
        """
        Processa imagem:
        - corrige orientação
        - resize proporcional
        - compressão JPEG

        Returns
        -------
        str : caminho da imagem processada
        """

        input_path = Path(input_path)
        output_path = Path(output_path)

        img = Image.open(input_path)

        # corrige rotação de celular (EXIF)
        img = ImageOps.exif_transpose(img)

        # garante RGB (remove RGBA/PNG issues)
        if img.mode != "RGB":
            img = img.convert("RGB")

        img = self._resize_keep_ratio(img)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        img.save(
            output_path,
            format="JPEG",
            quality=self.QUALITY,
            optimize=True,
            progressive=True,
        )

        return str(output_path)

    def _resize_keep_ratio(self, img: Image.Image) -> Image.Image:

        width, height = img.size

        if width >= height:
            new_width = self.MAX_SIZE
            new_height = int(height * (self.MAX_SIZE / width))
        else:
            new_height = self.MAX_SIZE
            new_width = int(width * (self.MAX_SIZE / height))

        return img.resize((new_width, new_height), Image.LANCZOS)