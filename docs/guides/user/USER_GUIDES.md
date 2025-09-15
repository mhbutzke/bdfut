# Guias para Usuários - BDFut 📖

## Visão Geral

Este documento contém guias passo-a-passo para usuários do sistema BDFut, desde instalação até operação avançada.

## Índice

1. [Guia de Instalação](#guia-de-instalação)
2. [Guia de Configuração](#guia-de-configuração)
3. [Guia de Operação ETL](#guia-de-operação-etl)
4. [Guia de Troubleshooting](#guia-de-troubleshooting)
5. [FAQ](#faq)

---

## Guia de Instalação

### Pré-requisitos

#### Sistema Operacional
- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 9+
- **macOS**: 10.14+
- **Windows**: 10+ (com WSL recomendado)

#### Software Necessário
- **Python**: 3.8 ou superior
- **Git**: Para clonar o repositório
- **Redis**: Para cache (opcional mas recomendado)

#### Contas Necessárias
- **Sportmonks**: Conta com API key
- **Supabase**: Projeto com banco de dados

### Instalação Passo-a-Passo

#### 1. Clone o Repositório

```bash
# Clone o repositório
git clone https://github.com/bdfut/bdfut.git
cd bdfut

# Verifique a estrutura
ls -la
```

#### 2. Instale o Python

**Ubuntu/Debian:**
```bash
# Instalar Python 3.9
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv

# Verificar instalação
python3.9 --version
```

**macOS:**
```bash
# Usando Homebrew
brew install python@3.9

# Verificar instalação
python3.9 --version
```

**Windows:**
```bash
# Download do Python 3.9 do site oficial
# https://www.python.org/downloads/

# Verificar instalação
python --version
```

#### 3. Crie Ambiente Virtual

```bash
# Criar ambiente virtual
python3.9 -m venv venv

# Ativar ambiente virtual
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 4. Instale Dependências

```bash
# Instalação básica
pip install -e .

# Instalação com dependências de desenvolvimento
pip install -e ".[dev]"

# Verificar instalação
bdfut --help
```

#### 5. Configure Redis (Opcional)

**Ubuntu/Debian:**
```bash
# Instalar Redis
sudo apt install redis-server

# Iniciar Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verificar status
redis-cli ping
```

**macOS:**
```bash
# Usando Homebrew
brew install redis

# Iniciar Redis
brew services start redis

# Verificar status
redis-cli ping
```

**Docker:**
```bash
# Executar Redis em container
docker run -d --name redis -p 6379:6379 redis:alpine

# Verificar status
docker exec redis redis-cli ping
```

### Verificação da Instalação

```bash
# Verificar configuração
bdfut show-config

# Testar conectividade
bdfut test-connection

# Executar teste básico
bdfut sync-base
```

---

## Guia de Configuração

### Configuração Inicial

#### 1. Obter API Keys

**Sportmonks API:**
1. Acesse [Sportmonks](https://www.sportmonks.com/)
2. Crie uma conta ou faça login
3. Vá para a seção de API
4. Gere uma nova API key
5. Copie a chave gerada

**Supabase:**
1. Acesse [Supabase Dashboard](https://supabase.com/dashboard)
2. Crie um novo projeto ou selecione existente
3. Vá para Settings > API
4. Copie a URL e a chave anon

#### 2. Criar Arquivo de Configuração

```bash
# Copiar arquivo de exemplo
cp bdfut/config/secrets/env_example.txt .env

# Editar configurações
nano .env
```

#### 3. Configurar Variáveis de Ambiente

```bash
# Arquivo .env
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

#### 4. Configurar Banco de Dados

**Executar Migrações:**
```bash
# Via Supabase CLI
supabase login
supabase link --project-ref seu-project-id
supabase db push

# Ou executar manualmente no SQL Editor
# Arquivo: deployment/supabase/migrations/001_create_sportmonks_schema.sql
```

#### 5. Validar Configuração

```bash
# Verificar configuração
bdfut show-config

# Testar conectividade
bdfut test-connection

# Executar sincronização básica
bdfut sync-base
```

### Configurações Avançadas

#### Configuração de Produção

```bash
# Arquivo .env.production
BDFUT_ENV=production
LOG_LEVEL=WARNING
ENABLE_CACHE=true
REDIS_URL=redis://prod-redis:6379
RATE_LIMIT_PER_HOUR=2500
```

#### Configuração de Desenvolvimento

```bash
# Arquivo .env.development
BDFUT_ENV=development
LOG_LEVEL=DEBUG
ENABLE_CACHE=false
RATE_LIMIT_PER_HOUR=1000
```

#### Configuração de Cache

```bash
# Cache Redis local
REDIS_URL=redis://localhost:6379

# Cache Redis remoto
REDIS_URL=redis://user:password@redis-server:6379

# Cache Redis com SSL
REDIS_URL=rediss://user:password@redis-server:6380
```

---

## Guia de Operação ETL

### Comandos Básicos

#### 1. Sincronização de Dados Base

```bash
# Sincronizar países, estados e tipos
bdfut sync-base

# Verificar logs
tail -f logs/development.log
```

#### 2. Sincronização de Ligas

```bash
# Sincronizar ligas principais
bdfut sync-leagues

# Sincronizar ligas específicas
bdfut sync-leagues -l 648 -l 651

# Verificar dados sincronizados
# Acesse Supabase Dashboard > Table Editor > leagues
```

#### 3. Sincronização Completa

```bash
# Executar sincronização completa
bdfut full-sync

# Monitorar progresso
tail -f logs/development.log
```

#### 4. Sincronização Incremental

```bash
# Sincronização incremental (apenas atualizações)
bdfut incremental

# Executar periodicamente
# Adicionar ao crontab para execução diária
0 2 * * * /path/to/bdfut incremental
```

### Operações Avançadas

#### 1. Sincronização por Script

```bash
# Executar script específico
python bdfut/scripts/etl/01_popular_leagues_seasons.py

# Executar script de sincronização
python bdfut/scripts/sync/sync_brasileirao_final.py

# Executar script de manutenção
python bdfut/scripts/maintenance/cleanup_old_data.py
```

#### 2. Sincronização Programática

```python
from bdfut.core.etl_process import ETLProcess

# Criar instância do ETL
etl = ETLProcess()

# Sincronizar dados base
etl.sync_base_data()

# Sincronizar ligas específicas
etl.sync_leagues([648, 651])  # Brasileirão e Premier League

# Sincronizar partidas recentes
etl.sync_recent_fixtures(days_back=7, days_forward=7)

# Sincronização completa
etl.full_sync()
```

#### 3. Monitoramento de Jobs

```python
from bdfut.core.etl_metadata import ETLMetadataManager

# Criar gerenciador de metadados
metadata = ETLMetadataManager()

# Verificar jobs recentes
recent_jobs = metadata.get_recent_jobs(limit=10)
for job in recent_jobs:
    print(f"Job: {job['job_name']} - Status: {job['status']}")

# Verificar estatísticas
stats = metadata.get_job_stats()
print(f"Total de jobs: {stats['total_jobs']}")
print(f"Taxa de sucesso: {stats['success_rate']}%")
```

### Automação

#### 1. Cron Jobs

```bash
# Editar crontab
crontab -e

# Adicionar jobs
# Sincronização incremental diária às 2h
0 2 * * * /path/to/bdfut incremental

# Sincronização completa semanal aos domingos às 3h
0 3 * * 0 /path/to/bdfut full-sync

# Limpeza de logs semanal
0 4 * * 0 find /path/to/logs -name "*.log" -mtime +7 -delete
```

#### 2. Systemd Service

```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/bdfut.service
```

```ini
[Unit]
Description=BDFut ETL Service
After=network.target redis.service

[Service]
Type=oneshot
User=bdfut
WorkingDirectory=/path/to/bdfut
ExecStart=/path/to/bdfut/venv/bin/bdfut incremental
Environment=BDFUT_ENV=production

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar e iniciar serviço
sudo systemctl enable bdfut.service
sudo systemctl start bdfut.service
```

#### 3. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  bdfut:
    build: .
    environment:
      - BDFUT_ENV=production
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
    command: bdfut incremental

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

```bash
# Executar com Docker Compose
docker-compose up -d
```

---

## Guia de Troubleshooting

### Problemas Comuns

#### 1. Erro de Conectividade

**Sintoma:**
```
❌ Sportmonks: Connection refused
❌ Supabase: Connection timeout
```

**Soluções:**
```bash
# Verificar conectividade de rede
ping api.sportmonks.com
ping seu-projeto.supabase.co

# Verificar configurações
bdfut show-config

# Testar conectividade
bdfut test-connection

# Verificar logs
tail -f logs/development.log
```

#### 2. Rate Limit Excedido

**Sintoma:**
```
❌ Sportmonks: 429 Too Many Requests
```

**Soluções:**
```bash
# Reduzir rate limit
export RATE_LIMIT_PER_HOUR=2000

# Aguardar reset da janela
# Rate limit reseta a cada hora

# Usar cache para reduzir chamadas
export ENABLE_CACHE=true
```

#### 3. Erro de Autenticação

**Sintoma:**
```
❌ Sportmonks: 401 Unauthorized
❌ Supabase: 401 Unauthorized
```

**Soluções:**
```bash
# Verificar API keys
echo $SPORTMONKS_API_KEY
echo $SUPABASE_KEY

# Regenerar API keys
# Sportmonks: Dashboard > API
# Supabase: Settings > API

# Atualizar configurações
nano .env
```

#### 4. Erro de Banco de Dados

**Sintoma:**
```
❌ Supabase: Table 'leagues' doesn't exist
```

**Soluções:**
```bash
# Executar migrações
supabase db push

# Ou executar manualmente
# Acesse Supabase Dashboard > SQL Editor
# Execute: deployment/supabase/migrations/001_create_sportmonks_schema.sql
```

#### 5. Erro de Cache

**Sintoma:**
```
❌ Redis: Connection refused
```

**Soluções:**
```bash
# Verificar status do Redis
redis-cli ping

# Iniciar Redis
sudo systemctl start redis-server

# Ou desabilitar cache temporariamente
export ENABLE_CACHE=false
```

### Logs e Debugging

#### 1. Verificar Logs

```bash
# Logs de desenvolvimento
tail -f logs/development.log

# Logs de produção
tail -f logs/production.log

# Logs com filtro
grep "ERROR" logs/development.log
grep "Sportmonks" logs/development.log
```

#### 2. Debug Mode

```bash
# Habilitar debug
export LOG_LEVEL=DEBUG

# Executar com debug
bdfut sync-base

# Verificar logs detalhados
tail -f logs/development.log
```

#### 3. Verificar Métricas

```python
from bdfut.core.redis_cache import RedisCache
from bdfut.core.etl_metadata import ETLMetadataManager

# Verificar cache
cache = RedisCache()
stats = cache.get_stats()
print(f"Cache hits: {stats['hits']}")
print(f"Cache misses: {stats['misses']}")

# Verificar jobs
metadata = ETLMetadataManager()
recent_jobs = metadata.get_recent_jobs(limit=5)
for job in recent_jobs:
    print(f"Job: {job['job_name']} - Status: {job['status']}")
```

### Recuperação de Falhas

#### 1. Recuperar Job Falhado

```python
from bdfut.core.etl_metadata import ETLMetadataManager

metadata = ETLMetadataManager()

# Verificar jobs falhados
failed_jobs = metadata.get_recent_jobs(limit=10)
for job in failed_jobs:
    if job['status'] == 'FAILED':
        print(f"Job falhado: {job['job_name']}")
        
        # Verificar logs do job
        logs = metadata.get_job_logs(job['id'])
        for log in logs:
            if log['level'] == 'ERROR':
                print(f"Erro: {log['message']}")
```

#### 2. Limpar Dados Corrompidos

```bash
# Limpar cache
redis-cli FLUSHALL

# Limpar logs antigos
find logs -name "*.log" -mtime +30 -delete

# Limpar dados temporários
rm -rf data/temp/*
```

#### 3. Reset Completo

```bash
# Parar todos os processos
pkill -f bdfut

# Limpar cache
redis-cli FLUSHALL

# Limpar logs
rm -rf logs/*

# Reconfigurar
bdfut show-config
bdfut test-connection
```

---

## FAQ

### Perguntas Frequentes

#### 1. Como obter API key da Sportmonks?

1. Acesse [Sportmonks](https://www.sportmonks.com/)
2. Crie uma conta gratuita
3. Vá para a seção de API
4. Gere uma nova API key
5. Copie a chave para o arquivo `.env`

#### 2. Qual é o limite de requests da Sportmonks?

- **Gratuito**: 100 requests/dia
- **Básico**: 1.000 requests/dia
- **Pro**: 10.000 requests/dia
- **Enterprise**: 100.000+ requests/dia

#### 3. Como configurar Supabase?

1. Acesse [Supabase](https://supabase.com/)
2. Crie um novo projeto
3. Vá para Settings > API
4. Copie a URL e a chave anon
5. Configure no arquivo `.env`

#### 4. Posso usar sem Redis?

Sim, o sistema funciona sem Redis, mas com performance reduzida. Configure `ENABLE_CACHE=false` no arquivo `.env`.

#### 5. Como monitorar o sistema?

```bash
# Verificar status
bdfut show-config

# Verificar logs
tail -f logs/development.log

# Verificar métricas
python -c "from bdfut.core.redis_cache import RedisCache; print(RedisCache().get_stats())"
```

#### 6. Como fazer backup dos dados?

```bash
# Backup do Supabase
supabase db dump > backup.sql

# Backup dos logs
tar -czf logs_backup.tar.gz logs/

# Backup das configurações
cp .env .env.backup
```

#### 7. Como atualizar o sistema?

```bash
# Atualizar código
git pull origin main

# Atualizar dependências
pip install -e .

# Verificar configuração
bdfut show-config
```

#### 8. Como reportar problemas?

1. **GitHub Issues**: [Criar issue](https://github.com/bdfut/bdfut/issues)
2. **Email**: support@bdfut.com
3. **Discord**: [Servidor da comunidade](https://discord.gg/bdfut)

#### 9. Quais ligas são suportadas?

- **Brasil**: Serie A, Serie B, Copa do Brasil
- **Argentina**: Liga Profesional
- **Europa**: Premier League, La Liga, Bundesliga, Ligue 1
- **Internacionais**: Champions League, Europa League, Copa Libertadores

#### 10. Como personalizar sincronização?

```python
from bdfut.core.etl_process import ETLProcess

etl = ETLProcess()

# Sincronizar ligas específicas
etl.sync_leagues([648, 651])  # IDs das ligas

# Sincronizar partidas por período
etl.sync_fixtures_by_date_range('2024-01-01', '2024-01-31')

# Sincronização incremental
etl.incremental_sync()
```

---

**Última atualização**: 2025-01-13  
**Versão**: 2.0  
**Responsável**: Technical Writer
