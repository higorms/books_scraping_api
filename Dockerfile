# Stage 1: Builder - Instala dependências
FROM python:3.13-slim AS builder

WORKDIR /app

# Instala dependências do sistema necessárias para compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Instala Poetry com versão específica
RUN pip install --no-cache-dir poetry==1.7.1

# Copia apenas arquivos de dependências (otimiza cache do Docker)
COPY pyproject.toml poetry.lock* ./

# Instala dependências apenas de produção em virtualenv
# --no-cache-dir reduz o tamanho da imagem
RUN poetry config virtualenvs.in-project true && \
    poetry install --only main --no-root --no-interaction --no-ansi && \
    find /app/.venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /app/.venv -type f -name "*.pyc" -delete && \
    find /app/.venv -type f -name "*.pyo" -delete

# Stage 2: Runtime - Imagem final otimizada
FROM python:3.13-slim

WORKDIR /app

# Copia virtualenv do stage anterior (contém apenas dependências necessárias)
COPY --from=builder /app/.venv /app/.venv

# Cria diretório de dados
RUN mkdir -p /app/data

# Cria usuário não-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copia APENAS o código necessário da aplicação (não todos os arquivos)
COPY --chown=appuser:appuser src ./src
COPY --chown=appuser:appuser data/books.csv ./data/books.csv
COPY --chown=appuser:appuser __init__.py ./

USER appuser

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    PATH="/app/.venv/bin:$PATH"

# Health check usando endpoint simples versionado
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/simple')" || exit 1

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]