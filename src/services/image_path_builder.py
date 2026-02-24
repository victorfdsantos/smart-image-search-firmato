import os
import re
from entities.product import Product


class ImagePathBuilder:
    """
    Responsável por construir o caminho relativo da imagem
    baseado nos atributos do produto.
    """

    BASE_FOLDER = "images_zone"

    PATH_FIELDS = [
        "Marca",
        "Categoria_Principal",
        "Subcategoria",
        "Estilo",
        "Material_Principal",
        "Material_Estrutura",
        "Material_Revestimento",
        "Nome_Produto",
    ]

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def build_relative_path(self, product: Product) -> str:
        """
        Retorna caminho relativo completo da imagem.
        """

        folder_path = self._build_folder_structure(product)

        filename = f"{product.id_produto}.jpg"

        return os.path.join(self.BASE_FOLDER, folder_path, filename)

    # --------------------------------------------------
    # Internals
    # --------------------------------------------------

    def _build_folder_structure(self, product: Product) -> str:

        parts = []

        for field in self.PATH_FIELDS:
            value = product.data.get(field, "")
            parts.append(self._sanitize(value))

        return os.path.join(*parts)

    def _sanitize(self, value: str) -> str:
        """
        Normaliza nomes de pasta:
        - remove caracteres inválidos
        - evita barras
        - remove espaços extras
        """

        value = str(value).strip()

        if not value:
            return "unknown"

        # remove caracteres proibidos
        value = re.sub(r"[<>:\"/\\|?*]", "", value)

        # troca espaços múltiplos
        value = re.sub(r"\s+", "_", value)

        return value.lower()