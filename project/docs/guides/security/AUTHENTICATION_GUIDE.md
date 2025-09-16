# Guia de Autenticação e Autorização - BDFut 🔐

## Visão Geral

Este documento detalha como configurar e usar autenticação no sistema BDFut, incluindo configuração de API keys, gerenciamento de secrets e práticas de segurança.

## Índice

1. [Configuração de API Keys](#configuração-de-api-keys)
2. [Variáveis de Ambiente](#variáveis-de-ambiente)
3. [Gerenciamento de Secrets](#gerenciamento-de-secrets)
4. [Validação de Configuração](#validação-de-configuração)
5. [Troubleshooting](#troubleshooting)
6. [Práticas de Segurança](#práticas-de-segurança)

---

## Configuração de API Keys

### Sportmonks API

#### 1. Obter API Key

1. Acesse [Sportmonks](https://www.sportmonks.com/)
2. Crie uma conta ou faça login
3. Navegue para a seção de API
4. Gere uma nova API key
5. Copie a chave gerada

#### 2. Configurar no Sistema

```bash
# Adicionar ao arquivo .env
SPORTMONKS_API_KEY=sua_chave_aqui
SPORTMONKS_BASE_URL=https://api.sportmonks.com/v3/football
```

#### 3. Testar Conectividade

```bash
# Via CLI
bdfut test-connection

# Via Python
from bdfut.core.sportmonks_client import SportmonksClient
client = SportmonksClient()
countries = client.get_countries()
print(f"Conectado! {len(countries)} países encontrados")
```

### Supabase

#### 1. Obter Credenciais

1. Acesse [Supabase Dashboard](https://supabase.com/dashboard)
2. Selecione seu projeto
3. Vá para Settings > API
4. Copie a URL e a chave anon

#### 2. Configurar no Sistema

```bash
# Adicionar ao arquivo .env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon_aqui
```

#### 3. Testar Conectividade

```bash
# Via CLI
bdfut test-connection

# Via Python
from bdfut.core.supabase_client import SupabaseClient
client = SupabaseClient()
# Teste simples de conectividade
print("Conectado ao Supabase!")
```

---

## Variáveis de Ambiente

### Arquivo .env

Crie um arquivo `.env` na raiz do projeto:

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

### Variáveis Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `SPORTMONKS_API_KEY` | Chave da API Sportmonks | `abc123def456` |
| `SUPABASE_URL` | URL do projeto Supabase | `https://xyz.supabase.co` |
| `SUPABASE_KEY` | Chave anon do Supabase | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |

### Variáveis Opcionais

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `SPORTMONKS_BASE_URL` | URL base da API Sportmonks | `https://api.sportmonks.com/v3/football` |
| `RATE_LIMIT_PER_HOUR` | Limite de requests por hora | `3000` |
| `BATCH_SIZE` | Tamanho do lote para processamento | `100` |
| `MAX_RETRIES` | Máximo de tentativas em caso de erro | `3` |
| `RETRY_DELAY` | Delay entre tentativas (segundos) | `5` |
| `REDIS_URL` | URL do Redis | `redis://localhost:6379` |
| `CACHE_TTL_HOURS` | TTL do cache em horas | `24` |
| `ENABLE_CACHE` | Habilitar cache | `true` |
| `BDFUT_ENV` | Ambiente (development/production) | `development` |
| `LOG_LEVEL` | Nível de log | `INFO` |

---

## Gerenciamento de Secrets

### Configuração Segura

#### 1. Nunca Commitar Secrets

Adicione ao `.gitignore`:

```gitignore
# Secrets
.env
.env.local
.env.production
*.key
*.pem
```

#### 2. Usar Variáveis de Ambiente

```python
import os
from bdfut.config.config import Config

# Configuração automática via Config
Config.validate()  # Valida todas as variáveis obrigatórias

# Acesso às configurações
api_key = Config.SPORTMONKS_API_KEY
supabase_url = Config.SUPABASE_URL
```

#### 3. Configuração por Ambiente

**Desenvolvimento (.env.development):**
```bash
BDFUT_ENV=development
LOG_LEVEL=DEBUG
ENABLE_CACHE=false
```

**Produção (.env.production):**
```bash
BDFUT_ENV=production
LOG_LEVEL=WARNING
ENABLE_CACHE=true
REDIS_URL=redis://prod-redis:6379
```

### Validação de Secrets

```python
from bdfut.config.config import Config

def validate_credentials():
    """Valida todas as credenciais obrigatórias"""
    try:
        Config.validate()
        print("✅ Todas as credenciais estão configuradas")
        return True
    except ValueError as e:
        print(f"❌ Erro de configuração: {str(e)}")
        return False

# Executar validação
validate_credentials()
```

---

## Validação de Configuração

### Validação Automática

O sistema valida automaticamente as configurações na inicialização:

```python
from bdfut.config.config import Config

# Validação automática
Config.validate()
```

### Validação Manual

```python
def validate_sportmonks_config():
    """Valida configuração do Sportmonks"""
    api_key = os.getenv('SPORTMONKS_API_KEY')
    base_url = os.getenv('SPORTMONKS_BASE_URL', 'https://api.sportmonks.com/v3/football')
    
    if not api_key:
        raise ValueError("SPORTMONKS_API_KEY é obrigatória")
    
    if len(api_key) < 10:
        raise ValueError("SPORTMONKS_API_KEY parece inválida")
    
    return True

def validate_supabase_config():
    """Valida configuração do Supabase"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url:
        raise ValueError("SUPABASE_URL é obrigatória")
    
    if not key:
        raise ValueError("SUPABASE_KEY é obrigatória")
    
    if not url.startswith('https://'):
        raise ValueError("SUPABASE_URL deve começar com https://")
    
    return True
```

### Teste de Conectividade

```python
def test_sportmonks_connection():
    """Testa conexão com Sportmonks"""
    try:
        from bdfut.core.sportmonks_client import SportmonksClient
        client = SportmonksClient()
        countries = client.get_countries()
        print(f"✅ Sportmonks: {len(countries)} países encontrados")
        return True
    except Exception as e:
        print(f"❌ Sportmonks: {str(e)}")
        return False

def test_supabase_connection():
    """Testa conexão com Supabase"""
    try:
        from bdfut.core.supabase_client import SupabaseClient
        client = SupabaseClient()
        # Teste simples de conectividade
        print("✅ Supabase: Conectado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Supabase: {str(e)}")
        return False
```

---

## Troubleshooting

### Problemas Comuns

#### 1. API Key Inválida

**Sintoma:**
```
❌ Sportmonks: 401 Unauthorized
```

**Solução:**
```bash
# Verificar se a chave está correta
echo $SPORTMONKS_API_KEY

# Regenerar chave na Sportmonks
# Atualizar no .env
```

#### 2. Supabase URL Inválida

**Sintoma:**
```
❌ Supabase: Connection refused
```

**Solução:**
```bash
# Verificar URL
echo $SUPABASE_URL

# URL deve ser: https://seu-projeto.supabase.co
# Não incluir /api/v1 ou outros paths
```

#### 3. Rate Limit Excedido

**Sintoma:**
```
❌ Sportmonks: 429 Too Many Requests
```

**Solução:**
```bash
# Reduzir rate limit
RATE_LIMIT_PER_HOUR=2000

# Ou aguardar reset da janela
```

#### 4. Cache Redis Indisponível

**Sintoma:**
```
❌ Redis: Connection refused
```

**Solução:**
```bash
# Desabilitar cache temporariamente
ENABLE_CACHE=false

# Ou configurar Redis
REDIS_URL=redis://localhost:6379
```

### Comandos de Diagnóstico

```bash
# Verificar configuração
bdfut show-config

# Testar conectividade
bdfut test-connection

# Verificar logs
tail -f logs/development.log
```

### Logs de Debug

```python
import logging

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Executar operação
from bdfut.core.etl_process import ETLProcess
etl = ETLProcess()
etl.sync_base_data()
```

---

## Práticas de Segurança

### 1. Proteção de Secrets

#### Nunca Expor em Logs

```python
import logging

# ❌ ERRADO - Expor API key
logging.info(f"API Key: {api_key}")

# ✅ CORRETO - Mascarar API key
masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
logging.info(f"API Key: {masked_key}")
```

#### Rotação de Chaves

```python
def rotate_api_key():
    """Rotaciona API key quando necessário"""
    # Implementar lógica de rotação
    # Notificar sistemas dependentes
    # Atualizar configurações
    pass
```

### 2. Validação de Entrada

```python
def validate_api_key_format(api_key: str) -> bool:
    """Valida formato da API key"""
    if not api_key:
        return False
    
    if len(api_key) < 10:
        return False
    
    # Adicionar outras validações específicas
    return True
```

### 3. Monitoramento de Acesso

```python
def log_api_access(endpoint: str, success: bool):
    """Registra acesso à API"""
    logging.info(f"API Access: {endpoint} - {'SUCCESS' if success else 'FAILED'}")
```

### 4. Backup de Configuração

```bash
# Backup seguro das configurações
cp .env .env.backup
gpg --encrypt .env.backup
```

### 5. Ambiente de Produção

```bash
# Usar secrets manager em produção
# AWS Secrets Manager, Azure Key Vault, etc.

# Exemplo com AWS
aws secretsmanager get-secret-value \
  --secret-id bdfut/production/api-keys \
  --query SecretString --output text
```

---

## Exemplos Práticos

### Exemplo 1: Configuração Completa

```python
import os
from bdfut.config.config import Config
from bdfut.core.etl_process import ETLProcess

def setup_bdfut():
    """Configuração completa do BDFut"""
    
    # Validar configurações
    Config.validate()
    
    # Testar conectividade
    etl = ETLProcess()
    
    # Executar sincronização básica
    etl.sync_base_data()
    
    print("✅ BDFut configurado e funcionando!")

if __name__ == "__main__":
    setup_bdfut()
```

### Exemplo 2: Configuração por Ambiente

```python
import os
from bdfut.config.config import Config

def setup_environment():
    """Configuração baseada no ambiente"""
    
    env = os.getenv('BDFUT_ENV', 'development')
    
    if env == 'development':
        # Configurações de desenvolvimento
        os.environ['LOG_LEVEL'] = 'DEBUG'
        os.environ['ENABLE_CACHE'] = 'false'
        
    elif env == 'production':
        # Configurações de produção
        os.environ['LOG_LEVEL'] = 'WARNING'
        os.environ['ENABLE_CACHE'] = 'true'
        
    # Validar configurações
    Config.validate()

setup_environment()
```

### Exemplo 3: Validação de Conectividade

```python
def validate_all_connections():
    """Valida todas as conexões"""
    
    results = {
        'sportmonks': False,
        'supabase': False,
        'redis': False
    }
    
    # Testar Sportmonks
    try:
        from bdfut.core.sportmonks_client import SportmonksClient
        client = SportmonksClient()
        client.get_countries()
        results['sportmonks'] = True
    except Exception as e:
        print(f"❌ Sportmonks: {str(e)}")
    
    # Testar Supabase
    try:
        from bdfut.core.supabase_client import SupabaseClient
        client = SupabaseClient()
        results['supabase'] = True
    except Exception as e:
        print(f"❌ Supabase: {str(e)}")
    
    # Testar Redis
    try:
        from bdfut.core.redis_cache import RedisCache
        cache = RedisCache()
        cache.get_stats()
        results['redis'] = True
    except Exception as e:
        print(f"❌ Redis: {str(e)}")
    
    return results

# Executar validação
results = validate_all_connections()
print(f"Conectividade: {results}")
```

---

**Última atualização**: 2025-01-13  
**Versão**: 2.0  
**Responsável**: Technical Writer
