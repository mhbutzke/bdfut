# Guia de Troubleshooting - BDFut 🔧

## Visão Geral

Este guia fornece soluções detalhadas para problemas comuns no sistema BDFut, incluindo diagnóstico, resolução e prevenção.

## Índice

1. [Problemas de Instalação](#problemas-de-instalação)
2. [Problemas de Configuração](#problemas-de-configuração)
3. [Problemas de Conectividade](#problemas-de-conectividade)
4. [Problemas de ETL](#problemas-de-etl)
5. [Problemas de Performance](#problemas-de-performance)
6. [Problemas de Dados](#problemas-de-dados)
7. [Problemas de Sistema](#problemas-de-sistema)
8. [Procedimentos de Emergência](#procedimentos-de-emergência)

---

## Problemas de Instalação

### Erro: Python não encontrado

**Sintoma:**
```bash
❌ python: command not found
```

**Diagnóstico:**
```bash
# Verificar versão do Python
python3 --version
which python3
```

**Soluções:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install python3 python3-pip

# macOS
brew install python3

# Verificar instalação
python3 --version
pip3 --version
```

### Erro: Dependências não instaladas

**Sintoma:**
```bash
❌ ModuleNotFoundError: No module named 'requests'
```

**Diagnóstico:**
```bash
# Verificar dependências instaladas
pip3 list

# Verificar requirements.txt
cat requirements.txt
```

**Soluções:**
```bash
# Instalar dependências
pip3 install -r requirements.txt

# Instalar dependência específica
pip3 install requests

# Verificar instalação
pip3 show requests
```

### Erro: Permissões insuficientes

**Sintoma:**
```bash
❌ Permission denied: '/usr/local/lib/python3.8/site-packages/'
```

**Diagnóstico:**
```bash
# Verificar permissões
ls -la /usr/local/lib/python3.8/site-packages/

# Verificar usuário atual
whoami
```

**Soluções:**
```bash
# Usar --user flag
pip3 install --user -r requirements.txt

# Usar virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verificar instalação
pip list
```

---

## Problemas de Configuração

### Erro: Arquivo .env não encontrado

**Sintoma:**
```bash
❌ FileNotFoundError: [Errno 2] No such file or directory: '.env'
```

**Diagnóstico:**
```bash
# Verificar arquivos de configuração
ls -la | grep env
ls -la config/
```

**Soluções:**
```bash
# Copiar arquivo de exemplo
cp config/environments/development.env .env

# Criar arquivo .env manualmente
cat > .env << EOF
BDFUT_ENV=development
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SPORTMONKS_API_KEY=your-api-key
REDIS_URL=redis://localhost:6379
EOF

# Verificar configuração
bdfut show-config
```

### Erro: Chaves de API inválidas

**Sintoma:**
```bash
❌ Invalid API key for Sportmonks
❌ Invalid Supabase credentials
```

**Diagnóstico:**
```bash
# Verificar chaves
bdfut show-config

# Testar conectividade
bdfut test-connection
```

**Soluções:**
```bash
# Verificar chave Sportmonks
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.sportmonks.com/v3/football/countries

# Verificar credenciais Supabase
supabase db ping

# Atualizar chaves
export SPORTMONKS_API_KEY="new-api-key"
export SUPABASE_KEY="new-supabase-key"

# Verificar configuração
bdfut show-config
```

### Erro: Configuração de ambiente incorreta

**Sintoma:**
```bash
❌ Environment 'production' not found
```

**Diagnóstico:**
```bash
# Verificar ambientes disponíveis
ls -la config/environments/

# Verificar variável de ambiente
echo $BDFUT_ENV
```

**Soluções:**
```bash
# Definir ambiente correto
export BDFUT_ENV=development

# Verificar configuração
bdfut show-config

# Usar ambiente específico
bdfut --env production show-config
```

---

## Problemas de Conectividade

### Erro: Conexão com Supabase falha

**Sintoma:**
```bash
❌ Connection to Supabase failed: timeout
```

**Diagnóstico:**
```bash
# Verificar conectividade
ping supabase.co

# Verificar DNS
nslookup supabase.co

# Testar conexão
supabase db ping
```

**Soluções:**
```bash
# Verificar URL do Supabase
echo $SUPABASE_URL

# Verificar chave
echo $SUPABASE_KEY

# Testar conexão manual
psql $DATABASE_URL -c "SELECT 1;"

# Verificar firewall
sudo ufw status
```

### Erro: Conexão com Redis falha

**Sintoma:**
```bash
❌ Connection to Redis failed: Connection refused
```

**Diagnóstico:**
```bash
# Verificar status do Redis
sudo systemctl status redis

# Verificar porta
netstat -tlnp | grep 6379

# Testar conexão
redis-cli ping
```

**Soluções:**
```bash
# Iniciar Redis
sudo systemctl start redis
sudo systemctl enable redis

# Verificar configuração
cat /etc/redis/redis.conf | grep bind

# Testar conexão
redis-cli ping
```

### Erro: Rate limit da API Sportmonks

**Sintoma:**
```bash
⚠️ Rate limit exceeded for Sportmonks API
```

**Diagnóstico:**
```bash
# Verificar rate limit atual
bdfut show-rate-limit

# Verificar logs
tail -f logs/api.log
```

**Soluções:**
```bash
# Aumentar intervalo entre requisições
export BDFUT_API_DELAY=2

# Usar cache
bdfut sync-leagues --use-cache

# Verificar rate limit
bdfut show-rate-limit
```

---

## Problemas de ETL

### Erro: Job ETL falha

**Sintoma:**
```bash
❌ ETL job 'sync-leagues' failed after 3 retries
```

**Diagnóstico:**
```bash
# Verificar logs do ETL
tail -f logs/etl.log

# Verificar status do job
bdfut show-etl-status

# Verificar recursos
htop
df -h
```

**Soluções:**
```bash
# Reiniciar serviço ETL
sudo systemctl restart bdfut-etl

# Executar job manualmente
bdfut sync-leagues --force

# Verificar configurações
bdfut show-config

# Limpar cache
redis-cli FLUSHALL
```

### Erro: Dados não sincronizados

**Sintoma:**
```bash
⚠️ Data synchronization incomplete
```

**Diagnóstico:**
```bash
# Verificar status da sincronização
bdfut show-sync-status

# Verificar dados no banco
psql $DATABASE_URL -c "SELECT count(*) FROM leagues;"

# Verificar logs
tail -f logs/sync.log
```

**Soluções:**
```bash
# Forçar sincronização completa
bdfut sync-all --force

# Sincronizar componente específico
bdfut sync-leagues --force

# Verificar integridade dos dados
bdfut test-data-integrity
```

### Erro: Metadados ETL corrompidos

**Sintoma:**
```bash
❌ ETL metadata corrupted
```

**Diagnóstico:**
```bash
# Verificar metadados
bdfut show-etl-metadata

# Verificar tabela de metadados
psql $DATABASE_URL -c "SELECT * FROM etl_metadata;"
```

**Soluções:**
```bash
# Limpar metadados
bdfut clear-etl-metadata

# Recriar metadados
bdfut init-etl-metadata

# Verificar metadados
bdfut show-etl-metadata
```

---

## Problemas de Performance

### Erro: Sistema lento

**Sintoma:**
```bash
⚠️ System performance degraded
```

**Diagnóstico:**
```bash
# Verificar recursos do sistema
htop
free -h
df -h

# Verificar processos
ps aux | grep bdfut

# Verificar logs de performance
tail -f logs/performance.log
```

**Soluções:**
```bash
# Reiniciar serviços
sudo systemctl restart bdfut-prod
sudo systemctl restart redis

# Limpar cache
redis-cli FLUSHALL

# Verificar configurações de performance
bdfut show-config | grep -i performance

# Otimizar banco de dados
psql $DATABASE_URL -c "VACUUM ANALYZE;"
```

### Erro: Memória insuficiente

**Sintoma:**
```bash
❌ Out of memory error
```

**Diagnóstico:**
```bash
# Verificar uso de memória
free -h
ps aux --sort=-%mem | head -10

# Verificar swap
swapon -s
```

**Soluções:**
```bash
# Liberar memória
sudo sync
echo 3 | sudo tee /proc/sys/vm/drop_caches

# Aumentar swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Verificar memória
free -h
```

### Erro: CPU alta

**Sintoma:**
```bash
⚠️ High CPU usage detected
```

**Diagnóstico:**
```bash
# Verificar uso de CPU
top
htop

# Verificar processos
ps aux --sort=-%cpu | head -10
```

**Soluções:**
```bash
# Identificar processo problemático
ps aux --sort=-%cpu | head -5

# Reiniciar serviço
sudo systemctl restart bdfut-prod

# Verificar configurações
bdfut show-config | grep -i cpu

# Otimizar queries
psql $DATABASE_URL -c "ANALYZE;"
```

---

## Problemas de Dados

### Erro: Dados inconsistentes

**Sintoma:**
```bash
⚠️ Data inconsistency detected
```

**Diagnóstico:**
```bash
# Verificar integridade dos dados
bdfut test-data-integrity

# Verificar logs de dados
tail -f logs/data.log

# Verificar tabelas
psql $DATABASE_URL -c "SELECT count(*) FROM leagues;"
```

**Soluções:**
```bash
# Executar verificação de integridade
bdfut test-data-integrity --fix

# Recriar dados
bdfut sync-all --force

# Verificar consistência
bdfut test-data-integrity
```

### Erro: Dados duplicados

**Sintoma:**
```bash
⚠️ Duplicate data detected
```

**Diagnóstico:**
```bash
# Verificar duplicatas
psql $DATABASE_URL -c "SELECT id, count(*) FROM leagues GROUP BY id HAVING count(*) > 1;"

# Verificar logs
tail -f logs/data.log
```

**Soluções:**
```bash
# Remover duplicatas
psql $DATABASE_URL -c "DELETE FROM leagues WHERE id IN (SELECT id FROM leagues GROUP BY id HAVING count(*) > 1);"

# Verificar duplicatas
psql $DATABASE_URL -c "SELECT id, count(*) FROM leagues GROUP BY id HAVING count(*) > 1;"
```

### Erro: Dados corrompidos

**Sintoma:**
```bash
❌ Data corruption detected
```

**Diagnóstico:**
```bash
# Verificar integridade do banco
psql $DATABASE_URL -c "SELECT * FROM pg_stat_database WHERE datname = current_database();"

# Verificar logs de erro
tail -f logs/database.log
```

**Soluções:**
```bash
# Executar VACUUM
psql $DATABASE_URL -c "VACUUM FULL;"

# Verificar integridade
psql $DATABASE_URL -c "SELECT * FROM pg_stat_database WHERE datname = current_database();"

# Restaurar backup se necessário
./scripts/recovery.sh backup_20250113
```

---

## Problemas de Sistema

### Erro: Serviço não inicia

**Sintoma:**
```bash
❌ Failed to start bdfut-prod.service
```

**Diagnóstico:**
```bash
# Verificar status do serviço
sudo systemctl status bdfut-prod

# Verificar logs do sistema
sudo journalctl -u bdfut-prod -f

# Verificar configuração
bdfut show-config
```

**Soluções:**
```bash
# Verificar dependências
sudo systemctl status redis
sudo systemctl status postgresql

# Reiniciar dependências
sudo systemctl restart redis
sudo systemctl restart postgresql

# Iniciar serviço
sudo systemctl start bdfut-prod

# Verificar status
sudo systemctl status bdfut-prod
```

### Erro: Porta já em uso

**Sintoma:**
```bash
❌ Port 8000 already in use
```

**Diagnóstico:**
```bash
# Verificar porta
netstat -tlnp | grep 8000

# Verificar processo
ps aux | grep 8000
```

**Soluções:**
```bash
# Matar processo
sudo kill -9 $(lsof -t -i:8000)

# Usar porta diferente
export BDFUT_PORT=8001

# Verificar porta
netstat -tlnp | grep 8001
```

### Erro: Permissões de arquivo

**Sintoma:**
```bash
❌ Permission denied: '/opt/bdfut/logs/'
```

**Diagnóstico:**
```bash
# Verificar permissões
ls -la /opt/bdfut/logs/

# Verificar usuário
whoami
```

**Soluções:**
```bash
# Corrigir permissões
sudo chown -R bdfut:bdfut /opt/bdfut/logs/
sudo chmod -R 755 /opt/bdfut/logs/

# Verificar permissões
ls -la /opt/bdfut/logs/
```

---

## Procedimentos de Emergência

### Sistema Completamente Inoperante

**Sintoma:**
```bash
❌ System completely down
```

**Procedimento de Emergência:**
```bash
#!/bin/bash
# scripts/emergency_recovery.sh

set -euo pipefail

echo "🚨 PROCEDIMENTO DE EMERGÊNCIA BDFut"
echo "=================================="

# 1. Verificar status dos serviços
echo "📋 Verificando status dos serviços..."
sudo systemctl status bdfut-prod
sudo systemctl status redis
sudo systemctl status postgresql

# 2. Parar todos os serviços
echo "⏹️ Parando todos os serviços..."
sudo systemctl stop bdfut-prod
sudo systemctl stop redis
sudo systemctl stop postgresql

# 3. Verificar recursos do sistema
echo "💻 Verificando recursos do sistema..."
free -h
df -h
top -bn1 | head -5

# 4. Limpar recursos
echo "🧹 Limpando recursos..."
sudo sync
echo 3 | sudo tee /proc/sys/vm/drop_caches

# 5. Reiniciar serviços em ordem
echo "▶️ Reiniciando serviços..."
sudo systemctl start postgresql
sleep 10
sudo systemctl start redis
sleep 5
sudo systemctl start bdfut-prod

# 6. Verificar status
echo "🔍 Verificando status..."
sleep 10
sudo systemctl status bdfut-prod
sudo systemctl status redis
sudo systemctl status postgresql

# 7. Testar conectividade
echo "🔗 Testando conectividade..."
bdfut test-connection

echo "=================================="
echo "🚨 Procedimento de emergência concluído"
```

### Perda de Dados

**Sintoma:**
```bash
❌ Data loss detected
```

**Procedimento de Recuperação:**
```bash
#!/bin/bash
# scripts/data_recovery.sh

set -euo pipefail

BACKUP_FILE="$1"

echo "💾 RECUPERAÇÃO DE DADOS BDFut"
echo "=================================="

# 1. Parar serviços
echo "⏹️ Parando serviços..."
sudo systemctl stop bdfut-prod

# 2. Backup de segurança atual
echo "💾 Criando backup de segurança..."
EMERGENCY_BACKUP="emergency_$(date +%Y%m%d_%H%M%S)"
mkdir -p /opt/backups/emergency
supabase db dump > "/opt/backups/emergency/${EMERGENCY_BACKUP}.sql"

# 3. Restaurar dados
echo "📊 Restaurando dados..."
supabase db reset
supabase db push < "/opt/backups/bdfut/${BACKUP_FILE}.sql"

# 4. Verificar integridade
echo "🔍 Verificando integridade..."
bdfut test-data-integrity

# 5. Reiniciar serviços
echo "▶️ Reiniciando serviços..."
sudo systemctl start bdfut-prod

# 6. Testar sistema
echo "🧪 Testando sistema..."
bdfut test-connection
bdfut sync-leagues --dry-run

echo "=================================="
echo "💾 Recuperação de dados concluída"
```

### Falha de Hardware

**Sintoma:**
```bash
❌ Hardware failure detected
```

**Procedimento de Migração:**
```bash
#!/bin/bash
# scripts/hardware_migration.sh

set -euo pipefail

NEW_SERVER="$1"

echo "🖥️ MIGRAÇÃO DE HARDWARE BDFut"
echo "=================================="

# 1. Backup completo
echo "💾 Criando backup completo..."
./scripts/backup.sh

# 2. Transferir dados
echo "📦 Transferindo dados..."
rsync -avz /opt/bdfut/ $NEW_SERVER:/opt/bdfut/
rsync -avz /opt/backups/ $NEW_SERVER:/opt/backups/

# 3. Configurar novo servidor
echo "⚙️ Configurando novo servidor..."
ssh $NEW_SERVER "cd /opt/bdfut && ./scripts/setup.sh"

# 4. Verificar configuração
echo "🔍 Verificando configuração..."
ssh $NEW_SERVER "cd /opt/bdfut && bdfut show-config"

# 5. Testar sistema
echo "🧪 Testando sistema..."
ssh $NEW_SERVER "cd /opt/bdfut && bdfut test-connection"

echo "=================================="
echo "🖥️ Migração de hardware concluída"
```

---

## Scripts de Diagnóstico

### Health Check Completo

```bash
#!/bin/bash
# scripts/health_check.sh

set -euo pipefail

echo "🏥 HEALTH CHECK BDFut - $(date)"
echo "=================================="

# 1. Verificar serviços
echo "📋 Verificando serviços..."
if systemctl is-active --quiet bdfut-prod; then
    echo "✅ BDFut service: ATIVO"
else
    echo "❌ BDFut service: INATIVO"
fi

if systemctl is-active --quiet redis; then
    echo "✅ Redis service: ATIVO"
else
    echo "❌ Redis service: INATIVO"
fi

# 2. Verificar conectividade
echo "🔗 Verificando conectividade..."
if bdfut test-connection; then
    echo "✅ Conectividade: OK"
else
    echo "❌ Conectividade: FALHA"
fi

# 3. Verificar recursos
echo "💻 Verificando recursos..."
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | cut -d'%' -f1)

echo "CPU: ${CPU_USAGE}%"
echo "Memória: ${MEMORY_USAGE}%"
echo "Disco: ${DISK_USAGE}%"

# 4. Verificar logs de erro
echo "📝 Verificando logs de erro..."
ERROR_COUNT=$(grep -c "ERROR" logs/production.log 2>/dev/null || echo "0")
echo "Erros nas últimas 24h: $ERROR_COUNT"

# 5. Verificar métricas
echo "📊 Verificando métricas..."
if curl -s http://localhost:8000/metrics > /dev/null; then
    echo "✅ Métricas: OK"
else
    echo "❌ Métricas: FALHA"
fi

echo "=================================="
echo "🏥 Health check concluído"
```

### Performance Check

```bash
#!/bin/bash
# scripts/performance_check.sh

set -euo pipefail

echo "⚡ PERFORMANCE CHECK BDFut - $(date)"
echo "=================================="

# 1. Verificar performance do banco
echo "📊 Verificando performance do banco..."
DB_QUERY_TIME=$(psql $DATABASE_URL -c "SELECT pg_sleep(0.1);" -t | grep -o '[0-9.]*' | tail -1)
echo "Tempo de query de teste: ${DB_QUERY_TIME}s"

# 2. Verificar performance do Redis
echo "🔴 Verificando performance do Redis..."
REDIS_PING_TIME=$(redis-cli --latency-history -i 1 | head -1 | awk '{print $3}')
echo "Latência do Redis: ${REDIS_PING_TIME}ms"

# 3. Verificar performance da API
echo "🌐 Verificando performance da API..."
API_RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/health)
echo "Tempo de resposta da API: ${API_RESPONSE_TIME}s"

# 4. Verificar performance do ETL
echo "🔄 Verificando performance do ETL..."
ETL_LAST_DURATION=$(bdfut show-etl-status | grep "Last duration" | awk '{print $3}')
echo "Última duração do ETL: ${ETL_LAST_DURATION}"

# 5. Verificar cache hit rate
echo "💾 Verificando cache hit rate..."
CACHE_HITS=$(redis-cli INFO stats | grep keyspace_hits | cut -d: -f2 | tr -d '\r')
CACHE_MISSES=$(redis-cli INFO stats | grep keyspace_misses | cut -d: -f2 | tr -d '\r')
if [ "$CACHE_HITS" -gt 0 ]; then
    HIT_RATE=$(echo "scale=2; $CACHE_HITS * 100 / ($CACHE_HITS + $CACHE_MISSES)" | bc)
    echo "Cache hit rate: ${HIT_RATE}%"
else
    echo "Cache hit rate: 0%"
fi

echo "=================================="
echo "⚡ Performance check concluído"
```

---

## Contatos de Suporte

### Equipe de Suporte

- **Email**: support@bdfut.com
- **Slack**: #bdfut-support
- **Telefone**: +55 11 99999-9999

### Escalação

1. **Nível 1**: Suporte básico (24h)
2. **Nível 2**: Suporte técnico (12h)
3. **Nível 3**: Desenvolvimento (4h)

### Recursos Adicionais

- **Documentação**: https://docs.bdfut.com
- **Status Page**: https://status.bdfut.com
- **Logs**: https://logs.bdfut.com

---

**Última atualização**: 2025-01-13  
**Versão**: 2.0  
**Responsável**: Technical Writer
