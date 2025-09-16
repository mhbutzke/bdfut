# ============================================
# BDFut Multi-Stage Dockerfile
# ============================================
# Otimizado para produção com multi-stage build

# ============================================
# STAGE 1: Base Dependencies
# ============================================
FROM python:3.11-slim as base

# Metadados
LABEL maintainer="BDFut Team <team@bdfut.com>"
LABEL description="Sistema ETL para dados de futebol da Sportmonks API"
LABEL version="2.0.0"

# Variáveis de ambiente globais
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Instalar dependências do sistema essenciais
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# STAGE 2: Build Dependencies
# ============================================
FROM base as builder

# Instalar dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt pyproject.toml ./

# Criar virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependências Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# ============================================
# STAGE 3: Development Image
# ============================================
FROM base as development

# Instalar dependências de desenvolvimento
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    htop \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar virtual environment do builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Criar usuário não-root
RUN groupadd -r bdfut && useradd -r -g bdfut -s /bin/bash bdfut

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências de desenvolvimento
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"

# Copiar código fonte
COPY --chown=bdfut:bdfut . .

# Criar diretórios necessários
RUN mkdir -p logs data && \
    chown -R bdfut:bdfut /app

# Mudar para usuário não-root
USER bdfut

# Comando padrão para desenvolvimento
CMD ["python", "-m", "bdfut.cli", "--help"]

# ============================================
# STAGE 4: Production Image
# ============================================
FROM base as production

# Copiar virtual environment do builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Criar usuário não-root
RUN groupadd -r bdfut && useradd -r -g bdfut -s /bin/bash bdfut

# Definir diretório de trabalho
WORKDIR /app

# Copiar apenas arquivos necessários para produção
COPY --chown=bdfut:bdfut bdfut/ ./bdfut/
COPY --chown=bdfut:bdfut scripts/ ./scripts/
COPY --chown=bdfut:bdfut requirements.txt pyproject.toml ./

# Criar diretórios necessários
RUN mkdir -p logs data && \
    chown -R bdfut:bdfut /app

# Mudar para usuário não-root
USER bdfut

# Expor porta
EXPOSE 8000

# Comando padrão para produção
CMD ["python", "-m", "bdfut.cli", "sync-base"]

# Health check otimizado
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import bdfut; print('OK')" || exit 1

# ============================================
# STAGE 5: Testing Image
# ============================================
FROM development as testing

# Instalar dependências de teste adicionais
RUN pip install --no-cache-dir pytest-xdist pytest-benchmark

# Copiar testes
COPY --chown=bdfut:bdfut tests/ ./tests/

# Comando padrão para testes
CMD ["pytest", "tests/", "-v", "--tb=short"]

# ============================================
# DEFAULT STAGE: Production
# ============================================
FROM production as final
