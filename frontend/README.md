# Firmato — Frontend (Next.js)

Interface web do buscador de imagens Firmato Móveis, construída com **Next.js 14 + TypeScript + Tailwind CSS**.

Consome a API de catálogo (`/products`, `/search`, `/catalog/register`) e oferece galeria paginada, busca semântica por texto e por imagem, filtros em cascata e pré-visualização com download da imagem selecionada.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Framework | Next.js 14 (App Router) |
| Linguagem | TypeScript |
| Estilo | Tailwind CSS |
| Ícones | Lucide React |
| Proxy de API | Next.js rewrites (`/api/*` → backend) |
| Container | Docker (Node 20 Alpine, standalone output) |

---

## Estrutura de pastas

```
src/
├── app/
│   ├── globals.css        # reset + variáveis CSS
│   ├── layout.tsx         # root layout
│   └── page.tsx           # página raiz → <HomeClient>
├── components/
│   ├── ui/                # Button, Spinner, Modal (componentes base)
│   ├── HomeClient.tsx     # toda a lógica de estado da página
│   ├── Topbar.tsx
│   ├── SearchPanel.tsx
│   ├── FilterDropdown.tsx
│   ├── AppliedFilters.tsx
│   ├── ImageCard.tsx
│   ├── ProductGrid.tsx
│   ├── Pagination.tsx
│   ├── PreviewPanel.tsx
│   ├── ProductDetailPanel.tsx
│   └── ImportModal.tsx
├── hooks/
│   ├── useDebounce.ts     # debounce de 500 ms para busca por texto
│   └── useUrlSync.ts      # helper para pushState na URL
├── lib/
│   ├── api.ts             # todos os fetches para o backend
│   ├── constants.ts       # FILTER_FIELDS
│   └── utils.ts           # cn(), parseFiltersFromUrl(), buildSearchUrl()
└── types/
    └── index.ts           # ProductSummary, ProductDetail, FilterMap, etc.
```

---

## Como rodar localmente

### Pré-requisitos

- Node.js **20+**
- Backend da API rodando (por padrão em `http://localhost:8000`)

### 1. Instalar dependências

```bash
npm install
```

### 2. Configurar variável de ambiente

```bash
cp .env.example .env.local
```

Edite `.env.local` se o backend estiver em um endereço diferente:

```env
API_BASE=http://localhost:8000
```

### 3. Rodar em modo desenvolvimento

```bash
npm run dev
```

Acesse: **http://localhost:3000**

Todas as chamadas de `/api/*` são proxiadas automaticamente para o backend via Next.js rewrites — sem precisar de CORS ou nginx em desenvolvimento.

---

## Como rodar via Docker

### 1. Build da imagem

```bash
docker build -t firmato-frontend .
```

### 2. Rodar o container

**Opção A — backend na mesma rede Docker (mais comum em produção):**

```bash
# Garanta que a rede do backend existe (ou foi criada pelo compose do backend)
docker network create firmato-net

docker run -d \
  --name firmato-frontend \
  --network firmato-net \
  -p 3000:3000 \
  -e API_BASE=http://firmato-api:8000 \
  firmato-frontend
```

**Opção B — usando docker compose:**

```bash
docker compose up -d
```

> Por padrão o `docker-compose.yml` conecta o frontend à rede `firmato-net`.
> Se o backend já criou essa rede, edite o compose e troque o bloco `networks` para `external: true`.

**Opção C — backend em outro servidor ou cloud:**

```bash
docker run -d \
  --name firmato-frontend \
  -p 3000:3000 \
  -e API_BASE=https://api.seudominio.com \
  firmato-frontend
```

### 3. Verificar

```bash
docker logs -f firmato-frontend
# Acesse http://localhost:3000 ou http://IP-DO-SERVIDOR:3000
```

---

## Como funciona o proxy de API

O Next.js redireciona internamente todas as requisições `/api/*` para o backend, sem expor o endereço do backend para o browser:

```
Browser → Next.js :3000 → (rewrite) → Backend :8000
            /api/products              /products
            /api/search                /search
            /api/static/images/1.jpg   /static/images/1.jpg
```

Isso elimina CORS no backend e funciona igual em dev e produção.

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `API_BASE` | `http://localhost:8000` | URL interna do backend FastAPI |

---

## Comandos úteis

```bash
# Desenvolvimento
npm run dev

# Build de produção
npm run build && npm start

# Lint
npm run lint

# Docker — rebuild e restart
docker compose build && docker compose up -d

# Docker — ver logs
docker compose logs -f

# Docker — parar
docker compose down
```
