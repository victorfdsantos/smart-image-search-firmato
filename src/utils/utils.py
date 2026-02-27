from PIL import Image
from pathlib import Path


VALID_EXT = [".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"]


def process_image(input_path: Path, output_path: Path):

    ext = input_path.suffix.lower()

    if ext not in VALID_EXT:
        raise ValueError(f"Extensão inválida: {input_path}")

    img = Image.open(input_path)

    # resize proporcional
    img.thumbnail((1080, 1080))

    output_path.parent.mkdir(parents=True, exist_ok=True)

    img.convert("RGB").save(
        output_path,
        "JPEG",
        quality=85,
        optimize=True
    )

    return output_path