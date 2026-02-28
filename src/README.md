# Catalog Processor

Sistema de processamento e cadastro de catálogo de produtos Firmato Móveis.

## Estrutura do Projeto

```
catalog_processor/
├── config.ini                   # ⚙️  Configurações (NAS, GCS, imagens, etc.)
├── requirements.txt
├── main.py                      # 🚀 FastAPI app + endpoint
│
├── config/
│   └── settings.py              # Leitura do config.ini
│
├── controllers/
│   └── catalog_controller.py    # Validação de input, orquestra o service
│
├── services/
│   ├── catalog_service.py       # Lógica principal do fluxo de cadastro
│   ├── image_service.py         # Redimensionamento, conversão, hash, limpeza
│   ├── nas_service.py           # Operações no NAS (filesystem local por enquanto)
│   └── storage_service.py       # Operações no GCS (Google Cloud Storage)
│
├── models/
│   └── product_model.py         # Dataclass do produto + mapeamento de colunas
│
├── utils/
│   └── logger.py                # Setup de logger por execução
│
├── landing/                     # 📥 Imagens originais entram aqui
├── data/                        # 📄 JSONs gerados por produto (1.json, 2.json, ...)
├── logs/                        # 📋 Logs por execução
└── output/nas/                  # 📦 Destino NAS local (configurável)
```

## Pré-requisitos

- Python 3.11+
- (Opcional) Credenciais do GCS em `config/gcs_credentials.json`

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

Edite o `config.ini` antes de rodar:

```ini
[nas]
base_path = ./output/nas          # Caminho de montagem do NAS real (ex: /mnt/nas)

[gcs]
bucket_name = firmato-moveis-catalog
credentials_path = ./config/gcs_credentials.json

[image]
resize_width = 1200
resize_height = 1200
jpeg_quality = 85
```

## Executar a API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Acesse a documentação interativa: [http://localhost:8000/docs](http://localhost:8000/docs)

## Fluxo de uso

1. Coloque as imagens originais na pasta `landing/`
2. Suba a planilha `.xlsx` via endpoint `POST /catalog/register`
3. O sistema:
   - Lê a planilha e detecta linhas novas vs já processadas
   - Redimensiona e converte imagens para JPG
   - Renomeia imagens pelo `Id_produto` (`1.jpg`, `1A.jpg`, `1B.jpg`, ...)
   - Move para o NAS e faz upload para o GCS
   - Gera o hash SHA-256 (`Chave_Especial`)
   - Atualiza `Caminho_Imagem` e `Caminho_Bucket`
   - Salva `data/{ID}.json` por produto
   - Atualiza e salva a planilha original
   - Remove da `landing/` apenas os arquivos processados
   - Gera log em `logs/catalog_register_{datahora}.log`

## Lógica de detecção de status

| `Caminho_Imagem`         | `Caminho_Imagem_Secundaria` | Ação                                    |
|--------------------------|-----------------------------|-----------------------------------------|
| `imagem.jpeg` (solto)    | qualquer valor              | Processo novo completo                  |
| Caminho com `/` (path)   | vazio ou `"Processada"`     | Ignorado (já processado)                |
| Caminho com `/` (path)   | filenames pendentes         | Só processa imagens secundárias         |

## Nomenclatura de imagens

- Imagem principal: `{ID}.jpg` → `1.jpg`
- Imagem secundária 1: `{ID}A.jpg` → `1A.jpg`
- Imagem secundária 2: `{ID}B.jpg` → `1B.jpg`
- E assim por diante...

## Logs

Cada execução gera um arquivo em `logs/`:
```
logs/catalog_register_20250228_143022.log
```

## Estrutura do JSON gerado

```json
{
  "id_produto": 1,
  "chave_especial": "85b628a7cfb1...",
  "caminho_imagem": "/output/nas/Estudiobola/Linha de design/Cadeira/1/1.jpg",
  "caminho_bucket": "gs://firmato-moveis-catalog/products/Estudiobola/.../1/1.jpg",
  "nome_produto": "COTA",
  ...
}
```
