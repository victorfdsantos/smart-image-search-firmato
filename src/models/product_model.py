from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ProductModel:
    """Representa um produto do catálogo com todos os seus atributos."""

    # --- Identificação e imagens ---
    chave_especial: Optional[str] = None
    id_produto: Optional[int] = None
    caminho_imagem: Optional[str] = None
    caminho_imagem_secundaria: Optional[str] = None
    caminho_bucket: Optional[str] = None

    # --- Dados do produto ---
    nome_produto: Optional[str] = None
    linha_colecao: Optional[str] = None
    marca: Optional[str] = None
    status: Optional[str] = None
    categoria_principal: Optional[str] = None
    subcategoria: Optional[str] = None
    tipo: Optional[str] = None
    ambiente: Optional[str] = None
    estilo: Optional[str] = None
    forma: Optional[str] = None
    modular: Optional[str] = None
    uso: Optional[str] = None

    # --- Materiais ---
    material_principal: Optional[str] = None
    material_estrutura: Optional[str] = None
    material_revestimento: Optional[str] = None

    # --- Cores ---
    cor_principal: Optional[str] = None
    cores_disponiveis: Optional[str] = None

    # --- Dimensões e especificações ---
    peso_kg: Optional[float] = None
    altura_cm: Optional[float] = None
    largura_cm: Optional[float] = None
    profundidade_cm: Optional[float] = None
    suporta_peso_kg: Optional[float] = None

    # --- Conforto e usabilidade ---
    nivel_conforto: Optional[str] = None
    firmeza: Optional[str] = None
    complexidade_montagem: Optional[str] = None
    indicado_espacos_pequenos: Optional[str] = None
    possui_armazenamento: Optional[str] = None
    multifuncional: Optional[str] = None
    nivel_premium: Optional[str] = None
    faixa_preco: Optional[str] = None

    # --- Logística ---
    fornecedor: Optional[str] = None
    prazo_entrega: Optional[str] = None
    tipo_entrega: Optional[str] = None
    garantia_meses: Optional[str] = None

    # --- Conteúdo descritivo ---
    palavras_chave: Optional[str] = None
    descricao_curta: Optional[str] = None
    descricao_tecnica: Optional[str] = None
    tags: Optional[str] = None
    sinonimos: Optional[str] = None
    perfil_cliente: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


# Mapeamento das colunas do Excel para os campos do model
COLUMN_MAP: dict[str, str] = {
    "Chave_Especial": "chave_especial",
    "Id_produto": "id_produto",
    "Caminho_Imagem": "caminho_imagem",
    "Caminho_Imagem_Secundaria": "caminho_imagem_secundaria",
    "Caminho_Bucket": "caminho_bucket",
    "Nome_Produto": "nome_produto",
    "Linha_Colecao": "linha_colecao",
    "Marca": "marca",
    "Status": "status",
    "Categoria_Principal": "categoria_principal",
    "Subcategoria": "subcategoria",
    "Tipo": "tipo",
    "Ambiente": "ambiente",
    "Estilo": "estilo",
    "Forma": "forma",
    "Modular": "modular",
    "Uso": "uso",
    "Material_Principal": "material_principal",
    "Material_Estrutura": "material_estrutura",
    "Material_Revestimento": "material_revestimento",
    "Cor_Principal": "cor_principal",
    "Cores_Disponiveis": "cores_disponiveis",
    "Peso_kg": "peso_kg",
    "Altura_cm": "altura_cm",
    "Largura_cm": "largura_cm",
    "Profundidade_cm": "profundidade_cm",
    "Suporta_Peso_kg": "suporta_peso_kg",
    "Nivel_Conforto": "nivel_conforto",
    "Firmeza": "firmeza",
    "Complexidade_Montagem": "complexidade_montagem",
    "Indicado_Espacos_Pequenos": "indicado_espacos_pequenos",
    "Possui_Armazenamento": "possui_armazenamento",
    "Multifuncional": "multifuncional",
    "Nivel_Premium": "nivel_premium",
    "Faixa_Preco": "faixa_preco",
    "Fornecedor": "fornecedor",
    "Prazo de Entrega": "prazo_entrega",
    "Tipo de Entrega": "tipo_entrega",
    "Garantia_Meses": "garantia_meses",
    "Palavras_Chave": "palavras_chave",
    "Descricao_Curta": "descricao_curta",
    "Descricao_Tecnica": "descricao_tecnica",
    "Tags": "tags",
    "Sinonimos": "sinonimos",
    "Perfil_Cliente": "perfil_cliente",
}
