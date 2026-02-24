import hashlib
from entities.product import Product


class HashingService:
    """
    Responsável por gerar o ID único do produto
    baseado em todas as colunas da planilha.
    """

    SEPARATOR = "|"

    def generate_product_id(self, product: Product) -> str:
        """
        Gera SHA256 determinístico baseado nos dados do produto.
        """

        normalized_values = self._serialize_product(product)

        raw_string = self.SEPARATOR.join(normalized_values)

        sha = hashlib.sha256(raw_string.encode("utf-8")).hexdigest()

        product.set_id_produto(sha)

        return sha

    def _serialize_product(self, product: Product) -> list[str]:
        """
        Serializa dados garantindo:
        - ordem fixa
        - normalização
        - determinismo
        """

        serialized = []

        # ordem fixa das colunas
        for key in sorted(product.data.keys()):

            value = product.data[key]

            if value is None:
                serialized.append("")
                continue

            serialized.append(str(value).strip().lower())

        return serialized