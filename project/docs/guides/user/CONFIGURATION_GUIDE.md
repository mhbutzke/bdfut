# Guia de Configuração - BDFut ⚙️

## Visão Geral

Este guia detalha todas as opções de configuração disponíveis no sistema BDFut, incluindo variáveis de ambiente, configurações avançadas e personalizações.

## Índice

1. [Configuração Básica](#configuração-básica)
2. [Variáveis de Ambiente](#variáveis-de-ambiente)
3. [Configurações Avançadas](#configurações-avançadas)
4. [Configuração por Ambiente](#configuração-por-ambiente)
5. [Validação de Configuração](#validação-de-configuração)
6. [Troubleshooting](#troubleshooting)

---

## Configuração Básica

### Arquivo .env

O sistema BDFut usa um arquivo `.env` para configurações. Crie este arquivo na raiz do projeto:

```bash
# Copiar arquivo de exemplo
cp bdfut/config/secrets/env_example.txt .env

# Editar configurações
nano .env
```

### Estrutura Básica

```bash
# ====================================
# CONFIGURAÇÃO SPORTMONKS API
# ====================================
SPORTMONKS_API_KEY=sua_chave_aqui
SPORTMONKS_BASE_URL=https://api.sportmonks.com/v3/football

# ====================================
# CONFIGURAÇÃO SUPABASE
# ====================================
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon_aqui

# ====================================
# CONFIGURAÇÕES DE ETL
# ====================================
RATE_LIMIT_PER_HOUR=3000
BATCH_SIZE=100
MAX_RETRIES=3
RETRY_DELAY=5

# ====================================
# CONFIGURAÇÕES DE CACHE
# ====================================
REDIS_URL=redis://localhost:6379
CACHE_TTL_HOURS=24
ENABLE_CACHE=true

# ====================================
# CONFIGURAÇÕES DE AMBIENTE
# ====================================
BDFUT_ENV=development
LOG_LEVEL=INFO
```

---

## Variáveis de Ambiente

### Configuração Sportmonks

| Variável | Obrigatória | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `SPORTMONKS_API_KEY` | ✅ | - | Chave da API Sportmonks |
| `SPORTMONKS_BASE_URL` | ❌ | `https://api.sportmonks.com/v3/football` | URL base da API |

#### Exemplo de Configuração

```bash
# API Key obrigatória
SPORTMONKS_API_KEY=abc123def456ghi789

# URL base (opcional)
SPORTMONKS_BASE_URL=https://api.sportmonks.com/v3/football
```

### Configuração Supabase

| Variável | Obrigatória | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `SUPABASE_URL` | ✅ | - | URL do projeto Supabase |
| `SUPABASE_KEY` | ✅ | - | Chave anon do Supabase |

#### Exemplo de Configuração

```bash
# URL do projeto
SUPABASE_URL=https://xyz123.supabase.co

# Chave anon
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Configuração ETL

| Variável | Obrigatória | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `RATE_LIMIT_PER_HOUR` | ❌ | `3000` | Limite de requests por hora |
| `BATCH_SIZE` | ❌ | `100` | Tamanho do lote para processamento |
| `MAX_RETRIES` | ❌ | `3` | Máximo de tentativas em caso de erro |
| `RETRY_DELAY` | ❌ | `5` | Delay entre tentativas (segundos) |

#### Exemplo de Configuração

```bash
# Rate limiting conservador
RATE_LIMIT_PER_HOUR=2000

# Processamento em lotes menores
BATCH_SIZE=50

# Mais tentativas
MAX_RETRIES=5

# Delay maior entre tentativas
RETRY_DELAY=10
```

### Configuração Cache

| Variável | Obrigatória | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `REDIS_URL` | ❌ | `redis://localhost:6379` | URL do Redis |
| `CACHE_TTL_HOURS` | ❌ | `24` | TTL do cache em horas |
| `ENABLE_CACHE` | ❌ | `true` | Habilitar cache |

#### Exemplo de Configuração

```bash
# Redis local
REDIS_URL=redis://localhost:6379

# Cache por 12 horas
CACHE_TTL_HOURS=12

# Habilitar cache
ENABLE_CACHE=true
```

### Configuração Ambiente

| Variável | Obrigatória | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `BDFUT_ENV` | ❌ | `development` | Ambiente (development/production) |
| `LOG_LEVEL` | ❌ | `INFO` | Nível de log (DEBUG/INFO/WARNING/ERROR) |

#### Exemplo de Configuração

```bash
# Ambiente de desenvolvimento
BDFUT_ENV=development

# Logs detalhados
LOG_LEVEL=DEBUG
```

---

## Configurações Avançadas

### Configuração de Rate Limiting

#### Rate Limiting Adaptativo

```bash
# Configuração básica
RATE_LIMIT_PER_HOUR=3000

# Configuração conservadora
RATE_LIMIT_PER_HOUR=2000

# Configuração agressiva (cuidado!)
RATE_LIMIT_PER_HOUR=4000
```

#### Configuração por Tipo de Dados

```python
# Configuração programática
from bdfut.config.config import Config

# Rate limiting específico por endpoint
Config.RATE_LIMITS = {
    'countries': 100,      # requests por hora
    'leagues': 200,        # requests por hora
    'fixtures': 1000,      # requests por hora
    'players': 500         # requests por hora
}
```

### Configuração de Cache

#### Cache Redis Avançado

```bash
# Redis com autenticação
REDIS_URL=redis://user:password@redis-server:6379

# Redis com SSL
REDIS_URL=rediss://user:password@redis-server:6380

# Redis cluster
REDIS_URL=redis://node1:6379,node2:6379,node3:6379
```

#### Cache por Tipo de Dados

```python
# Configuração programática
from bdfut.core.redis_cache import RedisCache

# TTL específico por tipo
cache_config = {
    'countries': 24 * 3600,    # 24 horas
    'leagues': 12 * 3600,      # 12 horas
    'fixtures': 2 * 3600,      # 2 horas
    'players': 6 * 3600        # 6 horas
}
```

### Configuração de Logging

#### Níveis de Log

```bash
# Debug - Todos os logs
LOG_LEVEL=DEBUG

# Info - Logs informativos
LOG_LEVEL=INFO

# Warning - Apenas warnings e erros
LOG_LEVEL=WARNING

# Error - Apenas erros
LOG_LEVEL=ERROR
```

#### Configuração de Arquivos de Log

```python
# Configuração programática
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bdfut.log'),
        logging.StreamHandler()
    ]
)
```

### Configuração de Retry

#### Retry com Backoff Exponencial

```bash
# Configuração básica
MAX_RETRIES=3
RETRY_DELAY=5

# Configuração agressiva
MAX_RETRIES=5
RETRY_DELAY=2

# Configuração conservadora
MAX_RETRIES=10
RETRY_DELAY=10
```

#### Configuração por Tipo de Erro

```python
# Configuração programática
from tenacity import retry, stop_after_attempt, wait_exponential

# Retry específico por tipo de erro
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def api_request():
    pass
```

---

## Configuração por Ambiente

### Desenvolvimento

```bash
# Arquivo .env.development
BDFUT_ENV=development
LOG_LEVEL=DEBUG
ENABLE_CACHE=false
RATE_LIMIT_PER_HOUR=1000
BATCH_SIZE=50
MAX_RETRIES=5
RETRY_DELAY=2
```

### Teste

```bash
# Arquivo .env.test
BDFUT_ENV=test
LOG_LEVEL=INFO
ENABLE_CACHE=true
REDIS_URL=redis://localhost:6379/1
RATE_LIMIT_PER_HOUR=500
BATCH_SIZE=25
MAX_RETRIES=3
RETRY_DELAY=5
```

### Produção

```bash
# Arquivo .env.production
BDFUT_ENV=production
LOG_LEVEL=WARNING
ENABLE_CACHE=true
REDIS_URL=redis://prod-redis:6379
CACHE_TTL_HOURS=12
RATE_LIMIT_PER_HOUR=2500
BATCH_SIZE=100
MAX_RETRIES=3
RETRY_DELAY=5
```

### Staging

```bash
# Arquivo .env.staging
BDFUT_ENV=staging
LOG_LEVEL=INFO
ENABLE_CACHE=true
REDIS_URL=redis://staging-redis:6379
CACHE_TTL_HOURS=6
RATE_LIMIT_PER_HOUR=1500
BATCH_SIZE=75
MAX_RETRIES=4
RETRY_DELAY=7
```

### Carregamento de Ambiente

```python
# Carregar configuração baseada no ambiente
import os
from pathlib import Path

def load_environment_config():
    """Carrega configuração baseada no ambiente"""
    env = os.getenv('BDFUT_ENV', 'development')
    env_file = Path(f'.env.{env}')
    
    if env_file.exists():
        # Carregar arquivo específico do ambiente
        load_dotenv(env_file)
    else:
        # Carregar arquivo padrão
        load_dotenv('.env')
```

---

## Validação de Configuração

### Validação Automática

```python
from bdfut.config.config import Config

# Validação automática na inicialização
Config.validate()
```

### Validação Manual

```python
def validate_configuration():
    """Valida configuração manualmente"""
    errors = []
    
    # Validar Sportmonks
    if not os.getenv('SPORTMONKS_API_KEY'):
        errors.append("SPORTMONKS_API_KEY é obrigatória")
    
    # Validar Supabase
    if not os.getenv('SUPABASE_URL'):
        errors.append("SUPABASE_URL é obrigatória")
    
    if not os.getenv('SUPABASE_KEY'):
        errors.append("SUPABASE_KEY é obrigatória")
    
    # Validar formato da URL
    supabase_url = os.getenv('SUPABASE_URL')
    if supabase_url and not supabase_url.startswith('https://'):
        errors.append("SUPABASE_URL deve começar com https://")
    
    # Validar rate limit
    try:
        rate_limit = int(os.getenv('RATE_LIMIT_PER_HOUR', '3000'))
        if rate_limit <= 0:
            errors.append("RATE_LIMIT_PER_HOUR deve ser maior que 0")
    except ValueError:
        errors.append("RATE_LIMIT_PER_HOUR deve ser um número")
    
    return errors

# Executar validação
errors = validate_configuration()
if errors:
    for error in errors:
        print(f"❌ {error}")
else:
    print("✅ Configuração válida")
```

### Teste de Conectividade

```python
def test_connectivity():
    """Testa conectividade com serviços externos"""
    results = {}
    
    # Testar Sportmonks
    try:
        from bdfut.core.sportmonks_client import SportmonksClient
        client = SportmonksClient()
        client.get_countries()
        results['sportmonks'] = True
    except Exception as e:
        results['sportmonks'] = False
        results['sportmonks_error'] = str(e)
    
    # Testar Supabase
    try:
        from bdfut.core.supabase_client import SupabaseClient
        client = SupabaseClient()
        results['supabase'] = True
    except Exception as e:
        results['supabase'] = False
        results['supabase_error'] = str(e)
    
    # Testar Redis
    try:
        from bdfut.core.redis_cache import RedisCache
        cache = RedisCache()
        cache.get_stats()
        results['redis'] = True
    except Exception as e:
        results['redis'] = False
        results['redis_error'] = str(e)
    
    return results

# Executar teste
results = test_connectivity()
for service, status in results.items():
    if isinstance(status, bool):
        print(f"{'✅' if status else '❌'} {service}")
    else:
        print(f"❌ {service}: {status}")
```

---

## Troubleshooting

### Problemas de Configuração

#### 1. Variável não encontrada

**Erro:**
```bash
❌ SPORTMONKS_API_KEY é obrigatória
```

**Solução:**
```bash
# Verificar arquivo .env
cat .env | grep SPORTMONKS_API_KEY

# Adicionar variável
echo "SPORTMONKS_API_KEY=sua_chave_aqui" >> .env

# Recarregar configuração
source .env
```

#### 2. Formato inválido

**Erro:**
```bash
❌ SUPABASE_URL deve começar com https://
```

**Solução:**
```bash
# Verificar URL atual
echo $SUPABASE_URL

# Corrigir URL
# De: http://seu-projeto.supabase.co
# Para: https://seu-projeto.supabase.co
```

#### 3. Valor inválido

**Erro:**
```bash
❌ RATE_LIMIT_PER_HOUR deve ser um número
```

**Solução:**
```bash
# Verificar valor atual
echo $RATE_LIMIT_PER_HOUR

# Corrigir valor
# De: RATE_LIMIT_PER_HOUR=abc
# Para: RATE_LIMIT_PER_HOUR=3000
```

### Problemas de Conectividade

#### 1. API Key inválida

**Erro:**
```bash
❌ Sportmonks: 401 Unauthorized
```

**Solução:**
```bash
# Verificar API key
echo $SPORTMONKS_API_KEY

# Regenerar API key
# Acesse Sportmonks Dashboard > API > Generate New Key

# Atualizar configuração
nano .env
```

#### 2. URL Supabase inválida

**Erro:**
```bash
❌ Supabase: Connection refused
```

**Solução:**
```bash
# Verificar URL
echo $SUPABASE_URL

# URL deve ser: https://seu-projeto.supabase.co
# Não incluir /api/v1 ou outros paths

# Testar conectividade
curl -I $SUPABASE_URL
```

#### 3. Redis indisponível

**Erro:**
```bash
❌ Redis: Connection refused
```

**Solução:**
```bash
# Verificar status do Redis
redis-cli ping

# Iniciar Redis
sudo systemctl start redis-server

# Ou desabilitar cache
echo "ENABLE_CACHE=false" >> .env
```

### Debug de Configuração

```bash
# Habilitar debug
export LOG_LEVEL=DEBUG

# Verificar configuração
bdfut show-config

# Testar conectividade
bdfut test-connection

# Verificar logs
tail -f logs/development.log
```

### Reset de Configuração

```bash
# Backup da configuração atual
cp .env .env.backup

# Reset para configuração padrão
cp bdfut/config/secrets/env_example.txt .env

# Reconfigurar
nano .env
```

---

## Exemplos Práticos

### Configuração para Desenvolvimento

```bash
# .env.development
BDFUT_ENV=development
LOG_LEVEL=DEBUG
ENABLE_CACHE=false
RATE_LIMIT_PER_HOUR=1000
BATCH_SIZE=50
MAX_RETRIES=5
RETRY_DELAY=2

# APIs
SPORTMONKS_API_KEY=dev_key_here
SUPABASE_URL=https://dev-project.supabase.co
SUPABASE_KEY=dev_key_here
```

### Configuração para Produção

```bash
# .env.production
BDFUT_ENV=production
LOG_LEVEL=WARNING
ENABLE_CACHE=true
REDIS_URL=redis://prod-redis:6379
CACHE_TTL_HOURS=12
RATE_LIMIT_PER_HOUR=2500
BATCH_SIZE=100
MAX_RETRIES=3
RETRY_DELAY=5

# APIs
SPORTMONKS_API_KEY=prod_key_here
SUPABASE_URL=https://prod-project.supabase.co
SUPABASE_KEY=prod_key_here
```

### Configuração para Teste

```bash
# .env.test
BDFUT_ENV=test
LOG_LEVEL=INFO
ENABLE_CACHE=true
REDIS_URL=redis://localhost:6379/1
CACHE_TTL_HOURS=1
RATE_LIMIT_PER_HOUR=500
BATCH_SIZE=25
MAX_RETRIES=3
RETRY_DELAY=5

# APIs
SPORTMONKS_API_KEY=test_key_here
SUPABASE_URL=https://test-project.supabase.co
SUPABASE_KEY=test_key_here
```

---

**Última atualização**: 2025-01-13  
**Versão**: 2.0  
**Responsável**: Technical Writer
