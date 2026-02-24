from typing import Dict, Any


class Product:
    """
    Entidade central do domínio.

    Representa um produto vindo da planilha de ingestão.
    Não possui dependência externa (filesystem, cloud, etc).
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Parameters
        ----------
        data : dict
            Linha da planilha convertida para dict.
        """

        # dados originais normalizados
        self.data = self._normalize_data(data)

        # será definido depois pelo HashingService
        self.id_produto: str | None = None

        # caminho final após ingestão
        self.endereco_imagem: str | None = None

    def _normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza valores para garantir hash determinístico.
        """

        normalized = {}

        for key, value in data.items():

            if value is None:
                normalized[key] = ""
                continue

            if isinstance(value, str):
                normalized[key] = value.strip()
            else:
                normalized[key] = value

        return normalized

    def set_id_produto(self, product_id: str):
        self.id_produto = product_id

    def set_endereco_imagem(self, path: str):
        self.endereco_imagem = path
        self.data["Endereço_Imagem"] = path

    def to_dict(self) -> Dict[str, Any]:
        """
        Retorna representação final do produto.
        """
        output = dict(self.data)

        output["Id_produto"] = self.id_produto
        output["Endereço_Imagem"] = self.endereco_imagem

        return output

    def __repr__(self) -> str:
        return f"<Product id={self.id_produto}>"