# Guia de Backup e Recovery - BDFut 💾

## Visão Geral

Este guia detalha os procedimentos completos de backup e recovery para o sistema BDFut, incluindo estratégias, scripts automatizados e procedimentos de recuperação.

## Índice

1. [Estratégia de Backup](#estratégia-de-backup)
2. [Procedimentos de Backup](#procedimentos-de-backup)
3. [Procedimentos de Recovery](#procedimentos-de-recovery)
4. [Testes de Recovery](#testes-de-recovery)
5. [Monitoramento de Backups](#monitoramento-de-backups)
6. [Troubleshooting](#troubleshooting)

---

## Estratégia de Backup

### Tipos de Backup

#### Backup Completo
- **Frequência**: Semanal
- **Conteúdo**: Todos os dados, configurações e logs
- **Retenção**: 4 semanas
- **Tamanho**: ~2GB

#### Backup Incremental
- **Frequência**: Diária
- **Conteúdo**: Apenas dados modificados
- **Retenção**: 7 dias
- **Tamanho**: ~200MB

#### Backup de Configuração
- **Frequência**: Sempre que houver mudanças
- **Conteúdo**: Arquivos de configuração e secrets
- **Retenção**: 12 meses
- **Tamanho**: ~10MB

### Componentes Incluídos

#### Dados do Banco
- Tabelas do Supabase
- Metadados de ETL
- Logs de auditoria
- Configurações do banco

#### Arquivos de Sistema
- Configurações (.env)
- Scripts personalizados
- Dados temporários
- Logs de aplicação

#### Cache Redis
- Dados em cache
- Configurações do Redis
- Métricas de performance

### Estratégia de Retenção

| Tipo | Frequência | Retenção | Localização |
|------|------------|----------|-------------|
| Completo | Semanal | 4 semanas | Local + Remoto |
| Incremental | Diária | 7 dias | Local + Remoto |
| Configuração | On-demand | 12 meses | Local + Remoto |
| Logs | Diária | 30 dias | Local |

---

## Procedimentos de Backup

### Backup Automático

#### Script Principal

```bash
#!/bin/bash
# scripts/backup.sh

set -euo pipefail

# Configurações
BACKUP_DIR="/opt/backups/bdfut"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="bdfut_backup_$DATE"
LOG_FILE="/var/log/bdfut_backup.log"

# Função de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Função de verificação
verify_backup() {
    local file="$1"
    local type="$2"
    
    case "$type" in
        "sql")
            if gzip -t "$file" 2>/dev/null; then
                log "✅ Backup SQL válido: $file"
            else
                log "❌ Backup SQL inválido: $file"
                return 1
            fi
            ;;
        "tar")
            if tar -tzf "$file" >/dev/null 2>&1; then
                log "✅ Backup TAR válido: $file"
            else
                log "❌ Backup TAR inválido: $file"
                return 1
            fi
            ;;
    esac
}

# Criar diretório de backup
mkdir -p "$BACKUP_DIR"

log "🚀 Iniciando backup BDFut - $DATE"

# 1. Backup do banco de dados
log "📊 Fazendo backup do banco de dados..."
if supabase db dump > "$BACKUP_DIR/${BACKUP_FILE}.sql"; then
    verify_backup "$BACKUP_DIR/${BACKUP_FILE}.sql" "sql"
    log "✅ Backup do banco concluído"
else
    log "❌ Falha no backup do banco"
    exit 1
fi

# 2. Backup de configurações
log "⚙️ Fazendo backup de configurações..."
if tar -czf "$BACKUP_DIR/${BACKUP_FILE}_config.tar.gz" .env config/; then
    verify_backup "$BACKUP_DIR/${BACKUP_FILE}_config.tar.gz" "tar"
    log "✅ Backup de configurações concluído"
else
    log "❌ Falha no backup de configurações"
    exit 1
fi

# 3. Backup de logs
log "📝 Fazendo backup de logs..."
if tar -czf "$BACKUP_DIR/${BACKUP_FILE}_logs.tar.gz" logs/; then
    verify_backup "$BACKUP_DIR/${BACKUP_FILE}_logs.tar.gz" "tar"
    log "✅ Backup de logs concluído"
else
    log "❌ Falha no backup de logs"
    exit 1
fi

# 4. Backup de dados
log "💾 Fazendo backup de dados..."
if tar -czf "$BACKUP_DIR/${BACKUP_FILE}_data.tar.gz" data/; then
    verify_backup "$BACKUP_DIR/${BACKUP_FILE}_data.tar.gz" "tar"
    log "✅ Backup de dados concluído"
else
    log "❌ Falha no backup de dados"
    exit 1
fi

# 5. Backup do Redis
log "🔴 Fazendo backup do Redis..."
if redis-cli BGSAVE; then
    # Aguardar conclusão do backup
    while [ "$(redis-cli LASTSAVE)" = "$(redis-cli LASTSAVE)" ]; do
        sleep 1
    done
    
    if cp /var/lib/redis/dump.rdb "$BACKUP_DIR/${BACKUP_FILE}_redis.rdb"; then
        log "✅ Backup do Redis concluído"
    else
        log "❌ Falha no backup do Redis"
        exit 1
    fi
else
    log "❌ Falha no backup do Redis"
    exit 1
fi

# 6. Criar arquivo de metadados
log "📋 Criando metadados do backup..."
cat > "$BACKUP_DIR/${BACKUP_FILE}_metadata.json" << EOF
{
    "backup_date": "$DATE",
    "backup_type": "complete",
    "files": [
        "${BACKUP_FILE}.sql",
        "${BACKUP_FILE}_config.tar.gz",
        "${BACKUP_FILE}_logs.tar.gz",
        "${BACKUP_FILE}_data.tar.gz",
        "${BACKUP_FILE}_redis.rdb"
    ],
    "size_bytes": $(du -sb "$BACKUP_DIR" | cut -f1),
    "version": "2.0",
    "environment": "production"
}
EOF

# 7. Limpar backups antigos
log "🧹 Limpando backups antigos..."
find "$BACKUP_DIR" -name "bdfut_backup_*" -mtime +28 -delete
log "✅ Backups antigos removidos"

# 8. Sincronizar com armazenamento remoto
log "☁️ Sincronizando com armazenamento remoto..."
if aws s3 sync "$BACKUP_DIR" s3://bdfut-backups/ --delete; then
    log "✅ Sincronização remota concluída"
else
    log "⚠️ Falha na sincronização remota"
fi

log "🎉 Backup concluído com sucesso - $BACKUP_FILE"
```

#### Script Incremental

```bash
#!/bin/bash
# scripts/backup_incremental.sh

set -euo pipefail

# Configurações
BACKUP_DIR="/opt/backups/bdfut/incremental"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="bdfut_incremental_$DATE"
LOG_FILE="/var/log/bdfut_backup.log"

# Função de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Criar diretório de backup
mkdir -p "$BACKUP_DIR"

log "🚀 Iniciando backup incremental BDFut - $DATE"

# 1. Backup apenas de dados modificados nas últimas 24h
log "📊 Fazendo backup incremental de dados..."
find data/ -name "*.json" -mtime -1 -exec tar -czf "$BACKUP_DIR/${BACKUP_FILE}_data.tar.gz" {} \;

# 2. Backup de logs do dia
log "📝 Fazendo backup de logs do dia..."
tar -czf "$BACKUP_DIR/${BACKUP_FILE}_logs.tar.gz" logs/production.log

# 3. Backup de metadados de ETL
log "📋 Fazendo backup de metadados ETL..."
python3 -c "
from bdfut.core.etl_metadata import ETLMetadataManager
import json
metadata = ETLMetadataManager()
recent_jobs = metadata.get_recent_jobs(limit=100)
with open('$BACKUP_DIR/${BACKUP_FILE}_metadata.json', 'w') as f:
    json.dump(recent_jobs, f, indent=2)
"

# 4. Criar arquivo de metadados
cat > "$BACKUP_DIR/${BACKUP_FILE}_metadata.json" << EOF
{
    "backup_date": "$DATE",
    "backup_type": "incremental",
    "files": [
        "${BACKUP_FILE}_data.tar.gz",
        "${BACKUP_FILE}_logs.tar.gz",
        "${BACKUP_FILE}_metadata.json"
    ],
    "size_bytes": $(du -sb "$BACKUP_DIR" | cut -f1),
    "version": "2.0",
    "environment": "production"
}
EOF

# 5. Limpar backups incrementais antigos
find "$BACKUP_DIR" -name "bdfut_incremental_*" -mtime +7 -delete

log "🎉 Backup incremental concluído - $BACKUP_FILE"
```

### Backup Manual

#### Backup de Emergência

```bash
#!/bin/bash
# scripts/backup_emergency.sh

set -euo pipefail

BACKUP_DIR="/opt/backups/bdfut/emergency"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="bdfut_emergency_$DATE"

mkdir -p "$BACKUP_DIR"

echo "🚨 BACKUP DE EMERGÊNCIA - $DATE"

# Parar serviços
sudo systemctl stop bdfut-prod
sudo systemctl stop redis

# Backup rápido
supabase db dump > "$BACKUP_DIR/${BACKUP_FILE}.sql"
tar -czf "$BACKUP_DIR/${BACKUP_FILE}_config.tar.gz" .env config/
cp /var/lib/redis/dump.rdb "$BACKUP_DIR/${BACKUP_FILE}_redis.rdb"

# Reiniciar serviços
sudo systemctl start redis
sudo systemctl start bdfut-prod

echo "✅ Backup de emergência concluído"
```

### Agendamento de Backups

#### Crontab

```bash
# Editar crontab
crontab -e

# Backup completo semanal (domingos às 2h)
0 2 * * 0 /opt/bdfut/scripts/backup.sh

# Backup incremental diário (todos os dias às 3h)
0 3 * * * /opt/bdfut/scripts/backup_incremental.sh

# Verificação de integridade (todos os dias às 4h)
0 4 * * * /opt/bdfut/scripts/verify_backups.sh
```

#### Systemd Timer

```ini
# /etc/systemd/system/bdfut-backup.timer
[Unit]
Description=BDFut Backup Timer
Requires=bdfut-backup.service

[Timer]
OnCalendar=weekly
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/bdfut-backup.service
[Unit]
Description=BDFut Backup Service
After=network.target

[Service]
Type=oneshot
User=bdfut
WorkingDirectory=/opt/bdfut
ExecStart=/opt/bdfut/scripts/backup.sh
```

---

## Procedimentos de Recovery

### Recovery Completo

#### Script de Recovery

```bash
#!/bin/bash
# scripts/recovery.sh

set -euo pipefail

BACKUP_FILE="$1"
BACKUP_DIR="/opt/backups/bdfut"
LOG_FILE="/var/log/bdfut_recovery.log"

# Função de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Verificar se backup existe
if [ ! -d "$BACKUP_DIR" ]; then
    log "❌ Diretório de backup não encontrado: $BACKUP_DIR"
    exit 1
fi

if [ ! -f "$BACKUP_DIR/${BACKUP_FILE}.sql" ]; then
    log "❌ Arquivo de backup não encontrado: $BACKUP_FILE"
    exit 1
fi

log "🚀 Iniciando recovery BDFut - $BACKUP_FILE"

# 1. Parar serviços
log "⏹️ Parando serviços..."
sudo systemctl stop bdfut-prod
sudo systemctl stop redis

# 2. Backup de segurança atual
log "💾 Criando backup de segurança atual..."
EMERGENCY_BACKUP="emergency_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR/emergency"
supabase db dump > "$BACKUP_DIR/emergency/${EMERGENCY_BACKUP}.sql"
tar -czf "$BACKUP_DIR/emergency/${EMERGENCY_BACKUP}_config.tar.gz" .env config/

# 3. Restaurar banco de dados
log "📊 Restaurando banco de dados..."
if supabase db reset; then
    if supabase db push < "$BACKUP_DIR/${BACKUP_FILE}.sql"; then
        log "✅ Banco de dados restaurado"
    else
        log "❌ Falha na restauração do banco"
        exit 1
    fi
else
    log "❌ Falha no reset do banco"
    exit 1
fi

# 4. Restaurar configurações
log "⚙️ Restaurando configurações..."
if tar -xzf "$BACKUP_DIR/${BACKUP_FILE}_config.tar.gz"; then
    log "✅ Configurações restauradas"
else
    log "❌ Falha na restauração de configurações"
    exit 1
fi

# 5. Restaurar dados
log "💾 Restaurando dados..."
if tar -xzf "$BACKUP_DIR/${BACKUP_FILE}_data.tar.gz"; then
    log "✅ Dados restaurados"
else
    log "❌ Falha na restauração de dados"
    exit 1
fi

# 6. Restaurar Redis
log "🔴 Restaurando Redis..."
if cp "$BACKUP_DIR/${BACKUP_FILE}_redis.rdb" /var/lib/redis/dump.rdb; then
    log "✅ Redis restaurado"
else
    log "❌ Falha na restauração do Redis"
    exit 1
fi

# 7. Reiniciar serviços
log "▶️ Reiniciando serviços..."
sudo systemctl start redis
sleep 5
sudo systemctl start bdfut-prod

# 8. Verificar status
log "🔍 Verificando status..."
sleep 10
if sudo systemctl is-active --quiet bdfut-prod; then
    log "✅ Serviço BDFut ativo"
else
    log "❌ Serviço BDFut inativo"
    exit 1
fi

# 9. Verificar conectividade
log "🔗 Verificando conectividade..."
if bdfut test-connection; then
    log "✅ Conectividade verificada"
else
    log "❌ Problema de conectividade"
    exit 1
fi

log "🎉 Recovery concluído com sucesso - $BACKUP_FILE"
```

#### Recovery Parcial

```bash
#!/bin/bash
# scripts/recovery_partial.sh

set -euo pipefail

BACKUP_FILE="$1"
COMPONENT="$2"  # database, config, data, redis
BACKUP_DIR="/opt/backups/bdfut"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "🚀 Iniciando recovery parcial - $COMPONENT de $BACKUP_FILE"

case "$COMPONENT" in
    "database")
        log "📊 Restaurando banco de dados..."
        supabase db reset
        supabase db push < "$BACKUP_DIR/${BACKUP_FILE}.sql"
        ;;
    "config")
        log "⚙️ Restaurando configurações..."
        tar -xzf "$BACKUP_DIR/${BACKUP_FILE}_config.tar.gz"
        ;;
    "data")
        log "💾 Restaurando dados..."
        tar -xzf "$BACKUP_DIR/${BACKUP_FILE}_data.tar.gz"
        ;;
    "redis")
        log "🔴 Restaurando Redis..."
        sudo systemctl stop redis
        cp "$BACKUP_DIR/${BACKUP_FILE}_redis.rdb" /var/lib/redis/dump.rdb
        sudo systemctl start redis
        ;;
    *)
        log "❌ Componente inválido: $COMPONENT"
        exit 1
        ;;
esac

log "✅ Recovery parcial concluído"
```

### Recovery de Dados Específicos

#### Recovery de Tabela Específica

```bash
#!/bin/bash
# scripts/recovery_table.sh

set -euo pipefail

BACKUP_FILE="$1"
TABLE_NAME="$2"
BACKUP_DIR="/opt/backups/bdfut"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "🚀 Iniciando recovery de tabela - $TABLE_NAME de $BACKUP_FILE"

# Extrair dados da tabela do backup
if pg_restore --data-only --table="$TABLE_NAME" "$BACKUP_DIR/${BACKUP_FILE}.sql" > "/tmp/${TABLE_NAME}_data.sql"; then
    log "✅ Dados da tabela extraídos"
    
    # Restaurar dados
    if supabase db push < "/tmp/${TABLE_NAME}_data.sql"; then
        log "✅ Tabela $TABLE_NAME restaurada"
    else
        log "❌ Falha na restauração da tabela"
        exit 1
    fi
else
    log "❌ Falha na extração dos dados"
    exit 1
fi

log "🎉 Recovery de tabela concluído"
```

### Recovery de Arquivos

#### Recovery de Configurações

```bash
#!/bin/bash
# scripts/recovery_config.sh

set -euo pipefail

BACKUP_FILE="$1"
BACKUP_DIR="/opt/backups/bdfut"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "🚀 Iniciando recovery de configurações - $BACKUP_FILE"

# Backup atual
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
cp -r config/ config.backup.$(date +%Y%m%d_%H%M%S)

# Restaurar configurações
if tar -xzf "$BACKUP_DIR/${BACKUP_FILE}_config.tar.gz"; then
    log "✅ Configurações restauradas"
    
    # Verificar configurações
    if bdfut show-config; then
        log "✅ Configurações validadas"
    else
        log "❌ Configurações inválidas"
        exit 1
    fi
else
    log "❌ Falha na restauração de configurações"
    exit 1
fi

log "🎉 Recovery de configurações concluído"
```

---

## Testes de Recovery

### Teste de Integridade

#### Script de Verificação

```bash
#!/bin/bash
# scripts/verify_backups.sh

set -euo pipefail

BACKUP_DIR="/opt/backups/bdfut"
LOG_FILE="/var/log/bdfut_backup_verify.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🔍 Iniciando verificação de backups"

# Verificar backups SQL
for backup in "$BACKUP_DIR"/*.sql; do
    if [ -f "$backup" ]; then
        if gzip -t "$backup" 2>/dev/null; then
            log "✅ Backup SQL válido: $(basename "$backup")"
        else
            log "❌ Backup SQL inválido: $(basename "$backup")"
        fi
    fi
done

# Verificar backups TAR
for backup in "$BACKUP_DIR"/*.tar.gz; do
    if [ -f "$backup" ]; then
        if tar -tzf "$backup" >/dev/null 2>&1; then
            log "✅ Backup TAR válido: $(basename "$backup")"
        else
            log "❌ Backup TAR inválido: $(basename "$backup")"
        fi
    fi
done

# Verificar backups Redis
for backup in "$BACKUP_DIR"/*.rdb; do
    if [ -f "$backup" ]; then
        if file "$backup" | grep -q "Redis"; then
            log "✅ Backup Redis válido: $(basename "$backup")"
        else
            log "❌ Backup Redis inválido: $(basename "$backup")"
        fi
    fi
done

log "🎉 Verificação de backups concluída"
```

### Teste de Recovery

#### Script de Teste

```bash
#!/bin/bash
# scripts/test_recovery.sh

set -euo pipefail

BACKUP_FILE="$1"
TEST_ENV="/opt/bdfut_test"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "🧪 Iniciando teste de recovery - $BACKUP_FILE"

# Criar ambiente de teste
mkdir -p "$TEST_ENV"
cd "$TEST_ENV"

# Copiar backup
cp "/opt/backups/bdfut/${BACKUP_FILE}.sql" .
cp "/opt/backups/bdfut/${BACKUP_FILE}_config.tar.gz" .
cp "/opt/backups/bdfut/${BACKUP_FILE}_data.tar.gz" .

# Restaurar configurações
tar -xzf "${BACKUP_FILE}_config.tar.gz"

# Configurar ambiente de teste
export BDFUT_ENV=test
export SUPABASE_URL="https://test-project.supabase.co"
export SUPABASE_KEY="test_key"

# Testar conectividade
if bdfut test-connection; then
    log "✅ Teste de conectividade passou"
else
    log "❌ Teste de conectividade falhou"
    exit 1
fi

# Testar funcionalidades básicas
if bdfut sync-base; then
    log "✅ Teste de sincronização passou"
else
    log "❌ Teste de sincronização falhou"
    exit 1
fi

# Limpar ambiente de teste
cd /
rm -rf "$TEST_ENV"

log "🎉 Teste de recovery concluído com sucesso"
```

---

## Monitoramento de Backups

### Métricas de Backup

#### Script de Monitoramento

```bash
#!/bin/bash
# scripts/monitor_backups.sh

set -euo pipefail

BACKUP_DIR="/opt/backups/bdfut"
LOG_FILE="/var/log/bdfut_backup_monitor.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "📊 Iniciando monitoramento de backups"

# Verificar último backup completo
LAST_COMPLETE=$(find "$BACKUP_DIR" -name "bdfut_backup_*.sql" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2)
if [ -n "$LAST_COMPLETE" ]; then
    LAST_COMPLETE_DATE=$(stat -c %Y "$LAST_COMPLETE")
    DAYS_SINCE_COMPLETE=$(( ( $(date +%s) - LAST_COMPLETE_DATE ) / 86400 ))
    
    if [ $DAYS_SINCE_COMPLETE -gt 7 ]; then
        log "⚠️ Último backup completo há $DAYS_SINCE_COMPLETE dias"
    else
        log "✅ Último backup completo há $DAYS_SINCE_COMPLETE dias"
    fi
else
    log "❌ Nenhum backup completo encontrado"
fi

# Verificar último backup incremental
LAST_INCREMENTAL=$(find "$BACKUP_DIR/incremental" -name "bdfut_incremental_*.tar.gz" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2)
if [ -n "$LAST_INCREMENTAL" ]; then
    LAST_INCREMENTAL_DATE=$(stat -c %Y "$LAST_INCREMENTAL")
    DAYS_SINCE_INCREMENTAL=$(( ( $(date +%s) - LAST_INCREMENTAL_DATE ) / 86400 ))
    
    if [ $DAYS_SINCE_INCREMENTAL -gt 1 ]; then
        log "⚠️ Último backup incremental há $DAYS_SINCE_INCREMENTAL dias"
    else
        log "✅ Último backup incremental há $DAYS_SINCE_INCREMENTAL dias"
    fi
else
    log "❌ Nenhum backup incremental encontrado"
fi

# Verificar espaço em disco
DISK_USAGE=$(df "$BACKUP_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    log "⚠️ Uso de disco alto: ${DISK_USAGE}%"
else
    log "✅ Uso de disco: ${DISK_USAGE}%"
fi

# Verificar tamanho dos backups
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "📦 Tamanho total dos backups: $TOTAL_SIZE"

log "🎉 Monitoramento de backups concluído"
```

### Alertas de Backup

#### Configuração de Alertas

```bash
#!/bin/bash
# scripts/backup_alerts.sh

set -euo pipefail

BACKUP_DIR="/opt/backups/bdfut"
ALERT_EMAIL="alerts@bdfut.com"

# Verificar último backup completo
LAST_COMPLETE=$(find "$BACKUP_DIR" -name "bdfut_backup_*.sql" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2)
if [ -n "$LAST_COMPLETE" ]; then
    LAST_COMPLETE_DATE=$(stat -c %Y "$LAST_COMPLETE")
    DAYS_SINCE_COMPLETE=$(( ( $(date +%s) - LAST_COMPLETE_DATE ) / 86400 ))
    
    if [ $DAYS_SINCE_COMPLETE -gt 7 ]; then
        echo "ALERTA: Último backup completo há $DAYS_SINCE_COMPLETE dias" | mail -s "Alerta de Backup BDFut" "$ALERT_EMAIL"
    fi
fi

# Verificar último backup incremental
LAST_INCREMENTAL=$(find "$BACKUP_DIR/incremental" -name "bdfut_incremental_*.tar.gz" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2)
if [ -n "$LAST_INCREMENTAL" ]; then
    LAST_INCREMENTAL_DATE=$(stat -c %Y "$LAST_INCREMENTAL")
    DAYS_SINCE_INCREMENTAL=$(( ( $(date +%s) - LAST_INCREMENTAL_DATE ) / 86400 ))
    
    if [ $DAYS_SINCE_INCREMENTAL -gt 1 ]; then
        echo "ALERTA: Último backup incremental há $DAYS_SINCE_INCREMENTAL dias" | mail -s "Alerta de Backup BDFut" "$ALERT_EMAIL"
    fi
fi

# Verificar espaço em disco
DISK_USAGE=$(df "$BACKUP_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "ALERTA: Uso de disco crítico: ${DISK_USAGE}%" | mail -s "Alerta de Espaço em Disco BDFut" "$ALERT_EMAIL"
fi
```

---

## Troubleshooting

### Problemas Comuns

#### Backup Falha

**Sintoma:**
```
❌ Falha no backup do banco
```

**Soluções:**
```bash
# Verificar conectividade com banco
supabase db ping

# Verificar permissões
ls -la /opt/backups/bdfut/

# Verificar espaço em disco
df -h

# Executar backup manual
supabase db dump > backup_manual.sql
```

#### Recovery Falha

**Sintoma:**
```
❌ Falha na restauração do banco
```

**Soluções:**
```bash
# Verificar integridade do backup
gzip -t backup.sql

# Verificar conectividade
supabase db ping

# Executar recovery parcial
./scripts/recovery_partial.sh backup_20250113 database
```

#### Espaço em Disco

**Sintoma:**
```
⚠️ Uso de disco alto: 85%
```

**Soluções:**
```bash
# Limpar backups antigos
find /opt/backups/bdfut -name "bdfut_backup_*" -mtime +28 -delete

# Limpar logs antigos
find logs/ -name "*.log" -mtime +30 -delete

# Limpar dados temporários
rm -rf data/temp/*
```

### Logs de Backup

#### Verificar Logs

```bash
# Verificar logs de backup
tail -f /var/log/bdfut_backup.log

# Verificar logs de recovery
tail -f /var/log/bdfut_recovery.log

# Verificar logs de monitoramento
tail -f /var/log/bdfut_backup_monitor.log
```

#### Debug de Backup

```bash
# Executar backup com debug
bash -x scripts/backup.sh

# Verificar variáveis de ambiente
env | grep BDFUT

# Verificar permissões
ls -la scripts/
```

---

**Última atualização**: 2025-01-13  
**Versão**: 2.0  
**Responsável**: Technical Writer
