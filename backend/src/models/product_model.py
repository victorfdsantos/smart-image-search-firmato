from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    chave_especial: Optional[str] = None
    id_produto: int
    nome_produto: Optional[str]
    marca: Optional[str]
    categoria_principal: Optional[str]
    subcategoria: Optional[str]
    faixa_preco: Optional[str]

    altura_cm: Optional[str]
    largura_cm: Optional[str]
    profundidade_cm: Optional[str]

    caminho_imagem: Optional[str] = None
    caminho_output: Optional[str] = None
    caminho_thumbnail: Optional[str] = None

    status: Optional[str]