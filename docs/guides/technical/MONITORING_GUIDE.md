# Guia de Monitoramento - BDFut 📊

## Visão Geral

Este guia detalha os procedimentos completos de monitoramento para o sistema BDFut, incluindo métricas, alertas, dashboards e procedimentos de troubleshooting.

## Índice

1. [Estratégia de Monitoramento](#estratégia-de-monitoramento)
2. [Métricas do Sistema](#métricas-do-sistema)
3. [Alertas e Notificações](#alertas-e-notificações)
4. [Dashboards](#dashboards)
5. [Procedimentos de Troubleshooting](#procedimentos-de-troubleshooting)
6. [Manutenção Preventiva](#manutenção-preventiva)

---

## Estratégia de Monitoramento

### Níveis de Monitoramento

#### Nível 1: Infraestrutura
- **CPU**: Uso, temperatura, frequência
- **Memória**: RAM, swap, cache
- **Disco**: Espaço, I/O, latência
- **Rede**: Largura de banda, latência, pacotes perdidos

#### Nível 2: Serviços
- **BDFut**: Status, performance, logs
- **Supabase**: Conectividade, queries, latência
- **Redis**: Memória, conexões, hit rate
- **Sportmonks API**: Rate limit, latência, erros

#### Nível 3: Aplicação
- **ETL Jobs**: Status, duração, sucesso/falha
- **Dados**: Qualidade, consistência, volume
- **Usuários**: Atividade, erros, performance
- **Business Logic**: Regras de negócio, validações

### Ferramentas de Monitoramento

#### Prometheus
- **Função**: Coleta de métricas
- **Configuração**: `/monitoring/prometheus/prometheus.yml`
- **Porta**: 9090
- **Retenção**: 15 dias

#### Grafana
- **Função**: Visualização e dashboards
- **Configuração**: `/monitoring/grafana/`
- **Porta**: 3000
- **Usuário**: admin / admin

#### AlertManager
- **Função**: Gerenciamento de alertas
- **Configuração**: `/monitoring/alertmanager/`
- **Porta**: 9093
- **Integração**: Email, Slack, PagerDuty

---

## Métricas do Sistema

### Métricas de Infraestrutura

#### CPU
```yaml
# /monitoring/prometheus/rules/cpu.yml
groups:
  - name: cpu
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU usage is above 80%"
          description: "CPU usage on {{ $labels.instance }} is {{ $value }}%"
```

#### Memória
```yaml
# /monitoring/prometheus/rules/memory.yml
groups:
  - name: memory
    rules:
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Memory usage is above 85%"
          description: "Memory usage on {{ $labels.instance }} is {{ $value }}%"
```

#### Disco
```yaml
# /monitoring/prometheus/rules/disk.yml
groups:
  - name: disk
    rules:
      - alert: HighDiskUsage
        expr: 100 - (node_filesystem_avail_bytes / node_filesystem_size_bytes * 100) > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk usage is above 90%"
          description: "Disk usage on {{ $labels.instance }} is {{ $value }}%"
```

### Métricas de Aplicação

#### BDFut Service
```python
# bdfut/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Contadores
etl_jobs_total = Counter('bdfut_etl_jobs_total', 'Total ETL jobs', ['status'])
api_requests_total = Counter('bdfut_api_requests_total', 'Total API requests', ['endpoint', 'status'])
cache_hits_total = Counter('bdfut_cache_hits_total', 'Total cache hits', ['type'])

# Histogramas
etl_duration = Histogram('bdfut_etl_duration_seconds', 'ETL job duration', ['job_type'])
api_duration = Histogram('bdfut_api_duration_seconds', 'API request duration', ['endpoint'])

# Gauges
active_connections = Gauge('bdfut_active_connections', 'Active database connections')
queue_size = Gauge('bdfut_queue_size', 'Queue size', ['queue_name'])

def start_metrics_server(port=8000):
    """Inicia servidor de métricas"""
    start_http_server(port)
    print(f"📊 Servidor de métricas iniciado na porta {port}")

def record_etl_job(job_type: str, duration: float, status: str):
    """Registra métricas de job ETL"""
    etl_jobs_total.labels(status=status).inc()
    etl_duration.labels(job_type=job_type).observe(duration)

def record_api_request(endpoint: str, duration: float, status: str):
    """Registra métricas de requisição API"""
    api_requests_total.labels(endpoint=endpoint, status=status).inc()
    api_duration.labels(endpoint=endpoint).observe(duration)

def record_cache_hit(cache_type: str):
    """Registra hit de cache"""
    cache_hits_total.labels(type=cache_type).inc()

def update_active_connections(count: int):
    """Atualiza contador de conexões ativas"""
    active_connections.set(count)

def update_queue_size(queue_name: str, size: int):
    """Atualiza tamanho da fila"""
    queue_size.labels(queue_name=queue_name).set(size)
```

#### Supabase Metrics
```python
# bdfut/core/supabase_metrics.py
import asyncio
from prometheus_client import Gauge, Counter
from bdfut.core.supabase_client import SupabaseClient

# Métricas do Supabase
db_connections = Gauge('bdfut_db_connections', 'Database connections')
db_queries_total = Counter('bdfut_db_queries_total', 'Total database queries', ['operation'])
db_query_duration = Histogram('bdfut_db_query_duration_seconds', 'Database query duration', ['operation'])

class SupabaseMetrics:
    def __init__(self, supabase_client: SupabaseClient):
        self.client = supabase_client
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Inicia monitoramento do Supabase"""
        asyncio.create_task(self._monitor_connections())
        asyncio.create_task(self._monitor_queries())
    
    async def _monitor_connections(self):
        """Monitora conexões do banco"""
        while True:
            try:
                # Obter número de conexões ativas
                result = await self.client.execute_query("""
                    SELECT count(*) as active_connections 
                    FROM pg_stat_activity 
                    WHERE state = 'active'
                """)
                
                if result and len(result) > 0:
                    db_connections.set(result[0]['active_connections'])
                
                await asyncio.sleep(30)  # Verificar a cada 30 segundos
            except Exception as e:
                print(f"Erro ao monitorar conexões: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_queries(self):
        """Monitora queries do banco"""
        while True:
            try:
                # Obter estatísticas de queries
                result = await self.client.execute_query("""
                    SELECT 
                        query_type,
                        count(*) as total_queries,
                        avg(duration) as avg_duration
                    FROM query_logs 
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                    GROUP BY query_type
                """)
                
                for row in result:
                    db_queries_total.labels(operation=row['query_type']).inc(row['total_queries'])
                    db_query_duration.labels(operation=row['query_type']).observe(row['avg_duration'])
                
                await asyncio.sleep(300)  # Verificar a cada 5 minutos
            except Exception as e:
                print(f"Erro ao monitorar queries: {e}")
                await asyncio.sleep(300)
```

#### Redis Metrics
```python
# bdfut/core/redis_metrics.py
import redis
from prometheus_client import Gauge, Counter, Histogram

# Métricas do Redis
redis_memory_usage = Gauge('bdfut_redis_memory_usage_bytes', 'Redis memory usage')
redis_connected_clients = Gauge('bdfut_redis_connected_clients', 'Redis connected clients')
redis_commands_total = Counter('bdfut_redis_commands_total', 'Total Redis commands', ['command'])
redis_command_duration = Histogram('bdfut_redis_command_duration_seconds', 'Redis command duration', ['command'])

class RedisMetrics:
    def __init__(self, redis_client: redis.Redis):
        self.client = redis_client
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Inicia monitoramento do Redis"""
        import threading
        thread = threading.Thread(target=self._monitor_redis)
        thread.daemon = True
        thread.start()
    
    def _monitor_redis(self):
        """Monitora métricas do Redis"""
        while True:
            try:
                # Obter informações do Redis
                info = self.client.info()
                
                # Atualizar métricas
                redis_memory_usage.set(info['used_memory'])
                redis_connected_clients.set(info['connected_clients'])
                
                # Obter estatísticas de comandos
                command_stats = info.get('commandstats', {})
                for command, stats in command_stats.items():
                    redis_commands_total.labels(command=command).inc(stats['calls'])
                    redis_command_duration.labels(command=command).observe(stats['usec'] / 1000000)
                
                time.sleep(30)  # Verificar a cada 30 segundos
            except Exception as e:
                print(f"Erro ao monitorar Redis: {e}")
                time.sleep(60)
```

---

## Alertas e Notificações

### Configuração de Alertas

#### AlertManager
```yaml
# /monitoring/alertmanager/alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@bdfut.com'
  smtp_auth_username: 'alerts@bdfut.com'
  smtp_auth_password: 'password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
    - match:
        severity: warning
      receiver: 'warning-alerts'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://localhost:5001/'

  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@bdfut.com'
        subject: 'CRITICAL: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}

  - name: 'warning-alerts'
    email_configs:
      - to: 'team@bdfut.com'
        subject: 'WARNING: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
```

#### Regras de Alertas
```yaml
# /monitoring/prometheus/rules/bdfut.yml
groups:
  - name: bdfut
    rules:
      # ETL Jobs
      - alert: ETLJobFailed
        expr: increase(bdfut_etl_jobs_total{status="failed"}[5m]) > 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "ETL job failed"
          description: "ETL job {{ $labels.job_type }} failed"

      - alert: ETLJobSlow
        expr: histogram_quantile(0.95, rate(bdfut_etl_duration_seconds_bucket[5m])) > 300
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "ETL job is slow"
          description: "ETL job {{ $labels.job_type }} is taking longer than 5 minutes"

      # API Requests
      - alert: HighAPIErrorRate
        expr: rate(bdfut_api_requests_total{status="error"}[5m]) / rate(bdfut_api_requests_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API error rate"
          description: "API error rate is above 10%"

      # Database
      - alert: HighDatabaseConnections
        expr: bdfut_db_connections > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "Database connections are above 80"

      # Redis
      - alert: RedisMemoryHigh
        expr: bdfut_redis_memory_usage_bytes > 1000000000  # 1GB
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage is high"
          description: "Redis memory usage is above 1GB"

      # Sportmonks API
      - alert: SportmonksAPIRateLimit
        expr: increase(bdfut_api_requests_total{endpoint="sportmonks",status="rate_limit"}[5m]) > 0
        for: 0m
        labels:
          severity: warning
        annotations:
          summary: "Sportmonks API rate limit hit"
          description: "Rate limit exceeded for Sportmonks API"
```

### Integração com Slack

#### Webhook do Slack
```python
# scripts/slack_alerts.py
import requests
import json
from datetime import datetime

class SlackAlerts:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_alert(self, alert_name: str, severity: str, message: str, details: dict = None):
        """Envia alerta para o Slack"""
        color = "danger" if severity == "critical" else "warning"
        
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": f"🚨 {alert_name}",
                    "text": message,
                    "fields": [
                        {
                            "title": "Severity",
                            "value": severity.upper(),
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "short": True
                        }
                    ],
                    "footer": "BDFut Monitoring",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        if details:
            for key, value in details.items():
                payload["attachments"][0]["fields"].append({
                    "title": key,
                    "value": str(value),
                    "short": True
                })
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            print(f"✅ Alerta enviado para Slack: {alert_name}")
        except Exception as e:
            print(f"❌ Erro ao enviar alerta para Slack: {e}")

# Configuração
slack_webhook = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
alerts = SlackAlerts(slack_webhook)

# Exemplo de uso
alerts.send_alert(
    alert_name="ETL Job Failed",
    severity="critical",
    message="ETL job 'sync-leagues' failed after 3 retries",
    details={
        "Job ID": "etl_20250113_001",
        "Error": "Connection timeout",
        "Retries": 3
    }
)
```

---

## Dashboards

### Dashboard Principal

#### Grafana Dashboard
```json
{
  "dashboard": {
    "id": null,
    "title": "BDFut System Overview",
    "tags": ["bdfut", "system"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "System Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"bdfut\"}",
            "legendFormat": "BDFut Service"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {
                  "color": "red",
                  "value": 0
                },
                {
                  "color": "green",
                  "value": 1
                }
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "ETL Jobs",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(bdfut_etl_jobs_total[5m])",
            "legendFormat": "{{status}}"
          }
        ]
      },
      {
        "id": 3,
        "title": "API Requests",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(bdfut_api_requests_total[5m])",
            "legendFormat": "{{endpoint}} - {{status}}"
          }
        ]
      },
      {
        "id": 4,
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "bdfut_db_connections",
            "legendFormat": "Active Connections"
          }
        ]
      },
      {
        "id": 5,
        "title": "Redis Memory",
        "type": "graph",
        "targets": [
          {
            "expr": "bdfut_redis_memory_usage_bytes",
            "legendFormat": "Memory Usage"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

### Dashboard de Performance

#### Métricas de Performance
```json
{
  "dashboard": {
    "title": "BDFut Performance",
    "panels": [
      {
        "title": "ETL Job Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(bdfut_etl_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(bdfut_etl_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(bdfut_api_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(bdfut_cache_hits_total[5m]) / rate(bdfut_api_requests_total[5m]) * 100",
            "legendFormat": "Hit Rate %"
          }
        ]
      }
    ]
  }
}
```

---

## Procedimentos de Troubleshooting

### Problemas Comuns

#### ETL Job Falha

**Sintoma:**
```
❌ ETL job 'sync-leagues' failed after 3 retries
```

**Diagnóstico:**
```bash
# Verificar logs do ETL
tail -f logs/etl.log

# Verificar status do job
bdfut show-etl-status

# Verificar conectividade
bdfut test-connection

# Verificar recursos do sistema
htop
df -h
```

**Soluções:**
```bash
# Reiniciar serviço ETL
sudo systemctl restart bdfut-etl

# Limpar cache
redis-cli FLUSHALL

# Executar job manualmente
bdfut sync-leagues --force

# Verificar configurações
bdfut show-config
```

#### API Rate Limit

**Sintoma:**
```
⚠️ Sportmonks API rate limit hit
```

**Diagnóstico:**
```bash
# Verificar rate limit atual
bdfut show-rate-limit

# Verificar cache
redis-cli INFO memory

# Verificar logs de API
tail -f logs/api.log
```

**Soluções:**
```bash
# Aumentar intervalo entre requisições
export BDFUT_API_DELAY=2

# Limpar cache para reduzir requisições
redis-cli FLUSHDB

# Usar cache local
bdfut sync-leagues --use-cache
```

#### Database Connection Issues

**Sintoma:**
```
❌ Database connection timeout
```

**Diagnóstico:**
```bash
# Verificar conectividade
supabase db ping

# Verificar conexões ativas
psql -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Verificar logs do banco
tail -f logs/database.log
```

**Soluções:**
```bash
# Reiniciar conexões
sudo systemctl restart bdfut-prod

# Verificar configurações
bdfut show-config

# Testar conexão manual
psql $DATABASE_URL -c "SELECT 1;"
```

### Scripts de Diagnóstico

#### Health Check Completo
```bash
#!/bin/bash
# scripts/health_check.sh

set -euo pipefail

echo "🏥 HEALTH CHECK BDFUT - $(date)"
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

#### Performance Check
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

## Manutenção Preventiva

### Tarefas Diárias

#### Limpeza de Logs
```bash
#!/bin/bash
# scripts/daily_maintenance.sh

set -euo pipefail

echo "🧹 MANUTENÇÃO DIÁRIA BDFut - $(date)"
echo "=================================="

# 1. Limpar logs antigos
echo "📝 Limpando logs antigos..."
find logs/ -name "*.log" -mtime +30 -delete
echo "✅ Logs antigos removidos"

# 2. Limpar dados temporários
echo "🗑️ Limpando dados temporários..."
find data/temp/ -name "*.json" -mtime +7 -delete
echo "✅ Dados temporários removidos"

# 3. Otimizar banco de dados
echo "📊 Otimizando banco de dados..."
psql $DATABASE_URL -c "VACUUM ANALYZE;"
echo "✅ Banco otimizado"

# 4. Limpar cache Redis
echo "🔴 Limpando cache Redis..."
redis-cli EVAL "return redis.call('del', unpack(redis.call('keys', 'temp:*')))" 0
echo "✅ Cache Redis limpo"

# 5. Verificar espaço em disco
echo "💾 Verificando espaço em disco..."
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️ Uso de disco alto: ${DISK_USAGE}%"
else
    echo "✅ Uso de disco: ${DISK_USAGE}%"
fi

echo "=================================="
echo "🧹 Manutenção diária concluída"
```

### Tarefas Semanais

#### Backup e Verificação
```bash
#!/bin/bash
# scripts/weekly_maintenance.sh

set -euo pipefail

echo "📦 MANUTENÇÃO SEMANAL BDFut - $(date)"
echo "=================================="

# 1. Executar backup completo
echo "💾 Executando backup completo..."
./scripts/backup.sh
echo "✅ Backup completo executado"

# 2. Verificar integridade dos backups
echo "🔍 Verificando integridade dos backups..."
./scripts/verify_backups.sh
echo "✅ Integridade dos backups verificada"

# 3. Atualizar estatísticas do banco
echo "📊 Atualizando estatísticas do banco..."
psql $DATABASE_URL -c "ANALYZE;"
echo "✅ Estatísticas atualizadas"

# 4. Verificar configurações
echo "⚙️ Verificando configurações..."
bdfut show-config
echo "✅ Configurações verificadas"

# 5. Executar testes de integridade
echo "🧪 Executando testes de integridade..."
bdfut test-data-integrity
echo "✅ Testes de integridade executados"

echo "=================================="
echo "📦 Manutenção semanal concluída"
```

### Tarefas Mensais

#### Análise de Performance
```bash
#!/bin/bash
# scripts/monthly_maintenance.sh

set -euo pipefail

echo "📈 ANÁLISE MENSAL BDFut - $(date)"
echo "=================================="

# 1. Gerar relatório de performance
echo "📊 Gerando relatório de performance..."
bdfut generate-performance-report --period monthly
echo "✅ Relatório de performance gerado"

# 2. Analisar logs de erro
echo "🔍 Analisando logs de erro..."
ERROR_ANALYSIS=$(grep "ERROR" logs/production.log | tail -100 | sort | uniq -c | sort -nr)
echo "$ERROR_ANALYSIS"
echo "✅ Análise de erros concluída"

# 3. Verificar crescimento de dados
echo "📈 Verificando crescimento de dados..."
DATA_GROWTH=$(psql $DATABASE_URL -c "SELECT pg_size_pretty(pg_database_size(current_database()));" -t)
echo "Tamanho do banco: $DATA_GROWTH"

# 4. Verificar performance de queries
echo "⚡ Verificando performance de queries..."
SLOW_QUERIES=$(psql $DATABASE_URL -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;" -t)
echo "Queries mais lentas:"
echo "$SLOW_QUERIES"

# 5. Gerar relatório de uso
echo "📋 Gerando relatório de uso..."
bdfut generate-usage-report --period monthly
echo "✅ Relatório de uso gerado"

echo "=================================="
echo "📈 Análise mensal concluída"
```

---

**Última atualização**: 2025-01-13  
**Versão**: 2.0  
**Responsável**: Technical Writer
