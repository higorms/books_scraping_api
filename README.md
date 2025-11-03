# Books Scraping API

<img alt="Static Badge" src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white"> <img alt="Static Badge" src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white"> <img alt="Static Badge" src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white"> <img alt="Static Badge" src="https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white">




> API pública para extração, processamento e disponibilização de dados de livros provenientes de `https://books.toscrape.com/`, com suporte a busca tradicional, recomendação semântica, preparação de dados para Machine Learning e observabilidade.

## 1. Visão Geral
A aplicação realiza web scraping para montar um catálogo de livros e o expõe via uma API REST construída em FastAPI. Inclui:
- Scraper automatizado para gerar `data/books.csv`.
- Endpoints de consulta, busca, categorias e recomendações.
- Preparação de dataset para experimentos de Machine Learning (features + target).
- Predição de rating exemplificativa (modelo dummy).
- Autenticação via JWT para rotas sensíveis.
- Observabilidade com logs estruturados e métricas (Datadog opcional).

Autores: Higor Menezes e Narcelio Clemente  
Versão: 1.0.0

## 2. Arquitetura (Camadas)
- Domain: Entidades e protocolos (Book, User, BookRepository, UserRepository, exceções).
- Application: Casos de uso desacoplados (ex.: `SearchBooks`, `RunScraper`, `FindSimilarBooksByText`).
- Infrastructure: Implementações concretas (CSV, Pinecone, SQLite, JWT, Embeddings, Datadog, métricas de sistema).
- Interface (App): FastAPI (rotas, schemas Pydantic, middlewares).

### Pipeline de Dados
1. Scraper coleta e normaliza atributos (título, preço, rating, disponibilidade, categoria, imagem).  
2. Dados estruturados em DataFrame e persistidos em CSV.  
3. (Opcional) Indexação vetorial: geração de embeddings e envio ao Pinecone para recomendações semânticas.  
4. API serve dados brutos, filtrados, categorias, recomendações e dataset ML-ready.  
5. Cientistas de dados consomem endpoints para análises e experimentação.

## 3. Estrutura do Repositório e Arquitetura

### 3.1. Arquitetura Clean Architecture (Hexagonal)

O projeto adota os princípios da **Clean Architecture** (também conhecida como Arquitetura Hexagonal ou Ports & Adapters), garantindo:
- **Independência de frameworks**: A lógica de negócio não depende de bibliotecas externas.
- **Testabilidade**: Casos de uso podem ser testados isoladamente.
- **Independência de UI/Database**: Interfaces e persistência são detalhes de implementação.
- **Flexibilidade**: Facilita substituição de componentes (ex.: trocar CSV por PostgreSQL).

```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERFACE LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          FastAPI (app/)                                  │   │
│  │  • main.py (servidor)                                    │   │
│  │  • routes/ (endpoints HTTP)                              │   │
│  │  • schemas/ (Pydantic models - DTOs)                     │   │
│  │  • middleware/ (auth, logging)                           │   │
│  └────────────────────┬─────────────────────────────────────┘   │
└───────────────────────┼─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │       Use Cases (application/)                           │   │
│  │  • get_all_books.py                                      │   │
│  │  • search_books.py                                       │   │
│  │  • get_book_recommendations.py                           │   │
│  │  • scraper.py (orquestração do scraping)                 │   │
│  │  • login_user.py / register_user.py                      │   │
│  │  • get_training_data.py / run_prediction.py              │   │
│  │  • index_books.py (indexação vetorial)                   │   │
│  └────────────────────┬─────────────────────────────────────┘   │
└───────────────────────┼─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DOMAIN LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │       Entities & Protocols (domain/)                     │   │
│  │  • book.py (Book entity)                                 │   │
│  │  • user.py (User entity)                                 │   │
│  │  • exceptions.py (custom exceptions)                     │   │
│  │  • Protocols: BookRepository, UserRepository             │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                        ▲
                        │
┌───────────────────────┴─────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │    Implementations (infrastructure/)                     │   │
│  │                                                          │   │
│  │  repositories/                                           │   │
│  │    • book_csv_repository.py (CSV persistence)            │   │
│  │    • pinecone_repository.py (vector search)              │   │
│  │    • user_repository.py (SQLite + SQLAlchemy)            │   │
│  │                                                          │   │
│  │  services/                                               │   │
│  │    • embedding_service.py (Sentence-Transformers)        │   │
│  │    • datadog_handler.py (observability)                  │   │
│  │    • system_metrics.py (CPU, memory monitoring)          │   │ 
│  │                                                          │   │
│  │  security/                                               │   │
│  │    • jwt_service.py (autenticação JWT)                   │   │
│  │                                                          │   │
│  │  database.py (SQLAlchemy engine/session)                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
            ┌───────────────────────────────┐
            │   EXTERNAL DEPENDENCIES       │
            │  • BeautifulSoup (scraping)   │
            │  • Pinecone (vector DB)       │
            │  • SQLite (user DB)           │
            │  • Datadog (logs/metrics)     │
            │  • Sentence-Transformers      │
            └───────────────────────────────┘
```

### 3.2. Fluxo de Requisição (Exemplo: GET /api/v1/books/search)

```
1. Cliente HTTP → FastAPI Router (routes/book_routes.py)
2. Router → Use Case (application/search_books.py)
3. Use Case → Repository Protocol (domain/)
4. Repository Implementation (infrastructure/repositories/book_csv_repository.py)
5. CSV Reader → DataFrame → Filtragem
6. Retorno: Book Entities (domain/book.py)
7. Use Case → Serialização (schemas/book_schema.py)
8. Response → Cliente HTTP
```

### 3.3. Estrutura de Diretórios Detalhada

```
books_scraping_api/
│
├── src/
│   ├── app/                          # Interface Layer (FastAPI)
│   │   ├── main.py                   # Inicialização do servidor
│   │   ├── routes/                   # Endpoints HTTP
│   │   │   ├── auth_routes.py        # Login/Register
│   │   │   ├── book_routes.py        # CRUD e busca de livros
│   │   │   ├── health_routes.py      # Health checks
│   │   │   └── ml_routes.py          # Endpoints ML
│   │   ├── middleware/               # Processamento de requisições
│   │   │   ├── auth_middleware.py    # Validação JWT
│   │   │   └── request_logging.py    # Logs estruturados
│   │   └── schemas/                  # DTOs (Pydantic)
│   │       ├── book_schema.py
│   │       ├── auth_schema.py
│   │       └── ml_schema.py
│   │
│   ├── application/                  # Use Cases (Business Logic)
│   │   ├── get_all_books.py
│   │   ├── search_books.py
│   │   ├── get_book_recommendations.py
│   │   ├── scraper.py                # Orquestração do scraping
│   │   ├── index_books.py            # Indexação vetorial
│   │   ├── login_user.py
│   │   ├── register_user.py
│   │   ├── get_training_data.py      # Dataset ML
│   │   └── run_prediction.py         # Inferência
│   │
│   ├── domain/                       # Entities & Business Rules
│   │   ├── book.py                   # Entidade Book + Protocol
│   │   ├── user.py                   # Entidade User + Protocol
│   │   └── exceptions.py             # Exceções customizadas
│   │
│   └── infrastructure/               # External Concerns
│       ├── repositories/             # Persistência
│       │   ├── book_csv_repository.py
│       │   ├── pinecone_repository.py
│       │   └── user_repository.py
│       ├── services/                 # Serviços externos
│       │   ├── embedding_service.py
│       │   ├── datadog_handler.py
│       │   └── system_metrics.py
│       ├── security/
│       │   └── jwt_service.py
│       └── database.py               # SQLAlchemy setup
│
├── data/
│   └── books.csv                     # Dataset gerado pelo scraper
│
├── pyproject.toml                    # Dependências (Poetry)
├── Dockerfile                        # Containerização
├── README.md                         # Este arquivo
└── DOCUMENTATION.md                  # Documentação completa
```

### 3.4. Princípios de Design Aplicados

| Princípio | Implementação |
|-----------|---------------|
| **Separation of Concerns** | Cada camada tem responsabilidade única |
| **Dependency Inversion** | Use Cases dependem de abstrações (Protocols), não de implementações |
| **Single Responsibility** | Cada módulo tem uma única razão para mudar |
| **Open/Closed** | Extensível via novos casos de uso sem modificar existentes |
| **Interface Segregation** | Protocols específicos (BookRepository, UserRepository) |

### 3.5. Vantagens da Arquitetura

✅ **Manutenibilidade**: Mudanças isoladas por camada  
✅ **Testabilidade**: Mocks facilitados por Protocols  
✅ **Escalabilidade**: Fácil adicionar novos casos de uso  
✅ **Portabilidade**: Troca de CSV → PostgreSQL sem afetar Use Cases  
✅ **Clareza**: Estrutura previsível para novos desenvolvedores

## 4. Instalação
Pré-requisitos: Python 3.13+, Poetry instalado.
```powershell
poetry install
```

## 5. Configuração (.env exemplo)
Crie um arquivo `.env` na raiz:
```
PINECONE_API_KEY=seu_api_key
PINECONE_INDEX_NAME=books-index
JWT_SECRET_KEY=uma_chave_longa_segura
DD_API_KEY=opcional
DD_APP_KEY=opcional
DD_ENV=development
DD_SERVICE=books-scraping-api
DD_VERSION=1.0.0
DD_TRACE_ENABLED=false
```

## 6. Execução Local
Iniciar API em desenvolvimento (com reload):
```powershell
poetry run python src/app/main.py
```
Documentação Swagger: http://127.0.0.1:8000/docs  
ReDoc: http://127.0.0.1:8000/redoc

## 7. Scraper
Executado via caso de uso ou endpoint protegido:
- Endpoint: `POST /api/v1/scraper/run` (necessita JWT).  
Persiste resultado em `data/books.csv` com colunas: `id,title,price,rating,avaliability,category,image_url`.

## 8. Indexação Vetorial (Recomendações)
Script para indexar embeddings no Pinecone:
```powershell
poetry run python src/application/index_books.py
```
Endpoint de recomendação semântica:
- `GET /api/v1/books/recommendations?query=texto`

## 9. Endpoints Principais
| Endpoint | Descrição |
|----------|-----------|
| GET /api/v1/books | Lista todos os livros |
| GET /api/v1/books/{id} | Detalhes de um livro específico |
| GET /api/v1/books/search?title=&category= | Busca por título e/ou categoria |
| GET /api/v1/categories | Lista categorias únicas |
| GET /api/v1/health | Status da aplicação |
| GET /api/v1/books/recommendations?query= | Recomendação semântica |
| POST /api/v1/scraper/run | Executa scraping (JWT) |
| POST /api/v1/auth/register | Registro de usuário |
| POST /api/v1/auth/login | Login e obtenção de token JWT |
| GET /api/v1/ml/features | Features para inferência |
| GET /api/v1/ml/training-data | Dataset de treinamento |
| POST /api/v1/ml/predictions | Predição dummy de rating |

## 10. Schemas Principais
- BookSchema, ScraperResponseSchema, HealthSchema.  
- Auth: LoginRequest, RegisterRequest, TokenResponse, UserCreateResponse.  
- ML: BookFeatureSchema, TrainingDataSchema, PredictionInputSchema, PredictionOutputSchema.

## 11. Exemplos (curl)
```bash
# Listar livros
curl -X GET "http://127.0.0.1:8000/api/v1/books" -H "Accept: application/json"

# Buscar por título e categoria
curl -X GET "http://127.0.0.1:8000/api/v1/books/search?title=travel&category=travel" -H "Accept: application/json"

# Livro por ID
curl -X GET "http://127.0.0.1:8000/api/v1/books/10" -H "Accept: application/json"

# Categorias
curl -X GET "http://127.0.0.1:8000/api/v1/categories"

# Registro
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" -H "Content-Type: application/json" -d '{"username":"alice","email":"alice@example.com","password":"senha123"}'

# Login
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" -H "Content-Type: application/json" -d '{"username":"alice","password":"senha123"}'

# Executar scraper (token necessário)
curl -X POST "http://127.0.0.1:8000/api/v1/scraper/run" -H "Authorization: Bearer <TOKEN>"

# Recomendação semântica
curl -X GET "http://127.0.0.1:8000/api/v1/books/recommendations?query=história%20épica"

# Features ML
curl -X GET "http://127.0.0.1:8000/api/v1/ml/features"

# Predição dummy
curl -X POST "http://127.0.0.1:8000/api/v1/ml/predictions" -H "Content-Type: application/json" -d '{"title":"New Fantasy Book","price":35.5,"avaliability":12}'
```

## 12. Machine Learning
- Feature engineering simples: `title_length`, `price`, `avaliability`, `category`.
- Dataset fornece target `rating` (1–5).  
- Predição dummy aplica heurística linear controlada (limite 1–5).  

## 13. Autenticação
- JWT Bearer via `POST /api/v1/auth/login`.
- Rota protegida: `/api/v1/scraper/run` (enviar `Authorization: Bearer <token>`).
- Senhas armazenadas como hash bcrypt (passlib).

## 14. Observabilidade
- Logs em formato JSON e envio opcional ao Datadog.  
- Métricas: latência de requisição, contagem, CPU, memória.  
- Middleware registra IP, método, path, tempo de processamento.

O dashboard de métrica está público no DataDog e pode ser acessado pelo link: <br>
https://p.us5.datadoghq.com/sb/c5e800ef-ab4a-11f0-96b5-2e574486b548-fc30ead7ded0ae02426c1e1c0ffbf493

## 15. Tecnologias
FastAPI, Uvicorn, Requests, BeautifulSoup4, Pandas, Sentence-Transformers, Pinecone, SQLite, SQLAlchemy, Passlib/Bcrypt, PyJWT, Datadog API Client, ddtrace, Psutil, Pydantic v2.

## 16. Scripts Úteis
| Script | Função |
|--------|--------|
| `src/application/index_books.py` | Gera embeddings e indexa livros no Pinecone |
| `delete_pinecone_index.py` | Remove índice Pinecone (confirmação manual) |

## 17. Deploy e Infraestrutura

### 17.1. Ambiente de Produção

A aplicação está hospedada no **Azure Container Apps**, oferecendo alta disponibilidade e escalabilidade automática.

#### Especificações da Instância:
- **Compute**: 0.5 vCPU
- **Memória**: 1 GB RAM
- **Região**: East US 2
- **Container Registry**: Azure Container Registry (ACR)
- **Protocolo**: HTTPS com certificado gerenciado

> ⚠️ **Nota**: A memória RAM de 1GB é necessária devido ao modelo de embedding Sentence-Transformers que carrega em memória.

### 17.2. URLs de Acesso

| Recurso | URL |
|---------|-----|
| **Swagger UI** | https://books-api.jollyground-ed0bc992.eastus2.azurecontainerapps.io/docs |
| **ReDoc** | https://books-api.jollyground-ed0bc992.eastus2.azurecontainerapps.io/redoc |
| **Health Check** | https://books-api.jollyground-ed0bc992.eastus2.azurecontainerapps.io/api/v1/health |
| **API Base** | https://books-api.jollyground-ed0bc992.eastus2.azurecontainerapps.io/api/v1 |

### 17.3. Containerização (Docker)

A aplicação utiliza containerização para garantir consistência entre ambientes.

**Dockerfile** localizado na raiz do projeto:
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install --no-dev
EXPOSE 8000
CMD ["poetry", "run", "python", "src/app/main.py"]
```

#### Build Local:
```powershell
# Construir imagem
docker build -t books-scraping-api:latest .

# Executar container
docker run -p 8000:8000 --env-file .env books-scraping-api:latest
```

### 17.4. Testando a API em Produção

```bash
# Health Check
curl https://books-api.jollyground-ed0bc992.eastus2.azurecontainerapps.io/api/v1/health

# Buscar livros
curl https://books-api.jollyground-ed0bc992.eastus2.azurecontainerapps.io/api/v1/books

# Recomendações
curl https://books-api.jollyground-ed0bc992.eastus2.azurecontainerapps.io/api/v1/books/recommendations?query=fantasy
```

## 18. Créditos
Projeto desenvolvido por Higor Menezes e Narcelio Clemente no contexto de atividade acadêmica de Machine Learning Engineering (FIAP).
