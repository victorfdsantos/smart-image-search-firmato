from pydantic import BaseModel
from typing import Optional

class ProductSummary(BaseModel):
    id_produto: int
    nome_produto: Optional[str]
    marca: Optional[str]
    categoria_principal: Optional[str]
    faixa_preco: Optional[str]

    altura_cm: Optional[float]
    largura_cm: Optional[float]
    profundidade_cm: Optional[float]

    imagem_url: str