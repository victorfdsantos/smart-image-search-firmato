import hashlib

class Product:

    def __init__(self, row: dict):

        self.chave_especial = str(row.get("Chave_Especial", "")).strip()
        self.id_produto = str(row.get("Id_produto", "")).strip()

        self.caminho_temporario = str(row.get("Caminho_Imagem", "")).strip()
        self.caminho_imagem_secundaria = str(row.get("Caminho_Imagem_Secundaria", "")).strip()
        self.caminho_bucket = str(row.get("Caminho_Bucket", "")).strip()

        self.nome_produto = str(row.get("Nome_Produto", "")).strip()
        self.linha_colecao = str(row.get("Linha_Colecao", "")).strip()
        self.marca = str(row.get("Marca", "")).strip()
        self.status = str(row.get("Status", "")).strip()

        self.categoria_principal = str(row.get("Categoria_Principal", "")).strip()
        self.subcategoria = str(row.get("Subcategoria", "")).strip()
        self.tipo = str(row.get("Tipo", "")).strip()
        self.ambiente = str(row.get("Ambiente", "")).strip()
        self.estilo = str(row.get("Estilo", "")).strip()
        self.forma = str(row.get("Forma", "")).strip()
        self.modular = str(row.get("Modular", "")).strip()
        self.uso = str(row.get("Uso", "")).strip()

        self.material_principal = str(row.get("Material_Principal", "")).strip()
        self.material_estrutura = str(row.get("Material_Estrutura", "")).strip()
        self.material_revestimento = str(row.get("Material_Revestimento", "")).strip()

        self.cor_principal = str(row.get("Cor_Principal", "")).strip()
        self.cores_disponiveis = str(row.get("Cores_Disponiveis", "")).strip()

        self.peso_kg = row.get("Peso_kg", "")
        self.altura_cm = row.get("Altura_cm", "")
        self.largura_cm = row.get("Largura_cm", "")
        self.profundidade_cm = row.get("Profundidade_cm", "")
        self.suporta_peso_kg = row.get("Suporta_Peso_kg", "")

        self.nivel_conforto = row.get("Nivel_Conforto", "")
        self.firmeza = row.get("Firmeza", "")

        self.complexidade_montagem = row.get("Complexidade_Montagem", "")
        self.indicado_espacos_pequenos = row.get("Indicado_Espacos_Pequenos", "")
        self.possui_armazenamento = row.get("Possui_Armazenamento", "")
        self.multifuncional = row.get("Multifuncional", "")
        self.nivel_premium = row.get("Nivel_Premium", "")
        self.faixa_preco = row.get("Faixa_Preco", "")

        self.fornecedor = row.get("Fornecedor", "")
        self.prazo_entrega = row.get("Prazo de Entrega", "")
        self.tipo_entrega = row.get("Tipo de Entrega", "")
        self.garantia_meses = row.get("Garantia_Meses", "")

        self.palavras_chave = row.get("Palavras_Chave", "")
        self.descricao_curta = row.get("Descricao_Curta", "")
        self.descricao_tecnica = row.get("Descricao_Tecnica", "")
        self.tags = row.get("Tags", "")
        self.sinonimos = row.get("Sinonimos", "")
        self.perfil_cliente = row.get("Perfil_Cliente", "")

        self.caminho_final = None

    def generate_special_key(self): # rever dps

        values = [
            self.marca,
            self.categoria_principal,
            self.subcategoria,
            self.nome_produto,
            self.caminho_temporario,
        ]

        raw = "|".join(str(v).lower() for v in values)

        self.id_produto = hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()

        return self.id_produto

    def set_final_image_path(self, path: str):
        self.caminho_final = path

    def to_dict(self):

        return {
            "Chave_Especial": self.chave_especial,
            "Id_produto": self.id_produto,
            "Caminho_Imagem": self.caminho_final,
            "Caminho_Imagem_Secundaria": self.caminho_imagem_secundaria,
            "Caminho_Bucket": self.caminho_bucket,
            "Nome_Produto": self.nome_produto,
            "Linha_Colecao": self.linha_colecao,
            "Marca": self.marca,
            "Status": self.status,
            "Categoria_Principal": self.categoria_principal,
            "Subcategoria": self.subcategoria,
            "Tipo": self.tipo,
            "Ambiente": self.ambiente,
            "Estilo": self.estilo,
            "Forma": self.forma,
            "Modular": self.modular,
            "Uso": self.uso,
            "Material_Principal": self.material_principal,
            "Material_Estrutura": self.material_estrutura,
            "Material_Revestimento": self.material_revestimento,
            "Cor_Principal": self.cor_principal,
            "Cores_Disponiveis": self.cores_disponiveis,
            "Peso_kg": self.peso_kg,
            "Altura_cm": self.altura_cm,
            "Largura_cm": self.largura_cm,
            "Profundidade_cm": self.profundidade_cm,
            "Suporta_Peso_kg": self.suporta_peso_kg,
            "Nivel_Conforto": self.nivel_conforto,
            "Firmeza": self.firmeza,
            "Complexidade_Montagem": self.complexidade_montagem,
            "Indicado_Espacos_Pequenos": self.indicado_espacos_pequenos,
            "Possui_Armazenamento": self.possui_armazenamento,
            "Multifuncional": self.multifuncional,
            "Nivel_Premium": self.nivel_premium,
            "Faixa_Preco": self.faixa_preco,
            "Fornecedor": self.fornecedor,
            "Prazo de Entrega": self.prazo_entrega,
            "Tipo de Entrega": self.tipo_entrega,
            "Garantia_Meses": self.garantia_meses,
            "Palavras_Chave": self.palavras_chave,
            "Descricao_Curta": self.descricao_curta,
            "Descricao_Tecnica": self.descricao_tecnica,
            "Tags": self.tags,
            "Sinonimos": self.sinonimos,
            "Perfil_Cliente": self.perfil_cliente,
        }