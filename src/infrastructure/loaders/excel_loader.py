import pandas as pd
from pathlib import Path
from typing import List

from entities.product import Product


class ExcelLoader:
    """
    Responsável por carregar planilha de ingestão
    e converter em entidades Product.
    """

    REQUIRED_COLUMNS = [
        "Endereço_Imagem",
    ]

    def load(self, file_path: str) -> List[Product]:
        """
        Lê Excel e retorna lista de Products.
        """

        file_path = Path(file_path)

        df = pd.read_excel(file_path)

        df = df.fillna("")

        self._validate_columns(df)

        products = []

        for _, row in df.iterrows():
            data = row.to_dict()
            products.append(Product(data))

        return products

    def _validate_columns(self, df: pd.DataFrame):

        missing = [
            col for col in self.REQUIRED_COLUMNS
            if col not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Colunas obrigatórias ausentes: {missing}"
            )