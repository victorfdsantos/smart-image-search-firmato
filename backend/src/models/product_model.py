from dataclasses import dataclass, asdict
from typing import Optional

# Slots de imagens secundárias
SECONDARY_SLOTS: list[int] = [1, 2, 3]

SECONDARY_EXCEL_COLS:    dict[int, str] = {i: f"Caminho_Imagem_Secundaria{i}" for i in SECONDARY_SLOTS}
SECONDARY_NAS_FIELDS:    dict[int, str] = {i: f"caminho_imagem_secundaria{i}" for i in SECONDARY_SLOTS}
SECONDARY_BUCKET_FIELDS: dict[int, str] = {i: f"caminho_bucket_secundaria{i}" for i in SECONDARY_SLOTS}


@dataclass
class ProductModel:
    """
    Representa um produto do catálogo.
    Campos de caminho (NAS/bucket) vivem APENAS no JSON — nunca são lidos do Excel.
    """
    # Identificação
    chave_especial: Optional[str] = None
    id_produto: Optional[int] = None

    # Caminhos — preenchidos programaticamente
    caminho_imagem: Optional[str] = None
    caminho_bucket_principal: Optional[str] = None
    caminho_imagem_secundaria1: Optional[str] = None
    caminho_imagem_secundaria2: Optional[str] = None
    caminho_imagem_secundaria3: Optional[str] = None
    caminho_bucket_secundaria1: Optional[str] = None
    caminho_bucket_secundaria2: Optional[str] = None
    caminho_bucket_secundaria3: Optional[str] = None

    # Dados do produto
    nome_produto: Optional[str] = None
    marca: Optional[str] = None
    status: Optional[str] = None
    categoria_principal: Optional[str] = None
    subcategoria: Optional[str] = None
    ambiente: Optional[str] = None
    forma: Optional[str] = None
    material_principal: Optional[str] = None
    material_estrutura: Optional[str] = None
    material_revestimento: Optional[str] = None
    altura_cm: Optional[str] = None
    largura_cm: Optional[str] = None
    profundidade_cm: Optional[str] = None
    faixa_preco: Optional[str] = None
    descricao_tecnica: Optional[str] = None

    def to_dict(self) -> dict:
        """Serializa descartando campos None."""
        return {k: v for k, v in asdict(self).items() if v is not None}


COLUMN_MAP: dict[str, str] = {
    "Chave_Especial":       "chave_especial",
    "Id_produto":           "id_produto",
    "Nome_Produto":         "nome_produto",
    "Marca":                "marca",
    "Status":               "status",
    "Categoria_Principal":  "categoria_principal",
    "Subcategoria":         "subcategoria",
    "Ambiente":             "ambiente",
    "Forma":                "forma",
    "Material_Principal":   "material_principal",
    "Material_Estrutura":   "material_estrutura",
    "Material_Revestimento":"material_revestimento",
    "Altura_cm":            "altura_cm",
    "Largura_cm":           "largura_cm",
    "Profundidade_cm":      "profundidade_cm",
    "Faixa_Preco":          "faixa_preco",
    "Descricao_Tecnica":    "descricao_tecnica",
}