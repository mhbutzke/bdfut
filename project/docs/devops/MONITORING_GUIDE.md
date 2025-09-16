# ============================================
# BDFut Monitoring Guide
# ============================================
"""
Guia completo de monitoramento do sistema BDFut.
Cobre Prometheus, Grafana, alertas e health checks.
"""

## 🔍 **Visão Geral**

O sistema de monitoramento do BDFut é composto por:

1. **📊 Prometheus**: Coleta e armazena métricas
2. **📈 Grafana**: Visualização e dashboards
3. **🚨 Alertmanager**: Gerenciamento de alertas
4. **🏥 Health Checks**: Verificações de saúde
5. **📋 Métricas Customizadas**: Métricas específicas da aplicação

## 🏗️ **Arquitetura de Monitoramento**

```
┌─────────────────────────────────────────────────────────────────┐
│                        BDFut Application                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Metrics   │  │ Health      │  │   Logs      │  │ Traces  │ │
│  │   (Port     │  │ Checks      │  │             │  │         │ │
│  │    8000)    │  │ (Port 8001) │  │             │  │         │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ Prometheus  │  │   Grafana   │  │Alertmanager │  │ Node    │ │
│  │  (Port      │  │  (Port      │  │  (Port      │  │Exporter │ │
│  │   9090)     │  │   3000)     │  │   9093)     │  │ (9100)  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 **1. Prometheus**

### **Configuração**
- **Arquivo**: `monitoring/prometheus.yml`
- **Porta**: 9090
- **Intervalo de scraping**: 15s
- **Avaliação de regras**: 15s

### **Targets Configurados**
```yaml
scrape_configs:
  - job_name: 'prometheus'      # Auto-monitoramento
  - job_name: 'bdfut-app'       # Aplicação principal
  - job_name: 'bdfut-worker'    # Worker de background
  - job_name: 'node-exporter'   # Métricas de sistema
  - job_name: 'postgres-exporter' # Métricas do banco
  - job_name: 'redis-exporter'  # Métricas do cache
  - job_name: 'grafana'         # Métricas do Grafana
  - job_name: 'jaeger'          # Métricas do Jaeger
  - job_name: 'alertmanager'    # Métricas do Alertmanager
```

### **Acesso**
- **URL**: http://localhost:9090
- **Query**: `bdfut_api_requests_total`
- **Targets**: http://localhost:9090/targets

## 📈 **2. Grafana**

### **Configuração**
- **Porta**: 3000
- **Usuário padrão**: admin/admin
- **Datasource**: Prometheus (http://prometheus:9090)

### **Dashboards Disponíveis**

#### **BDFut Overview Dashboard**
- **UID**: `bdfut-overview`
- **Métricas**:
  - Taxa de requisições da API
  - Tempo de resposta P95
  - Taxa de erro da API
  - Uso de CPU do sistema

#### **BDFut System Metrics Dashboard**
- **UID**: `bdfut-system`
- **Métricas**:
  - Uso de CPU
  - Uso de memória
  - Uso de disco
  - Load average

### **Acesso**
- **URL**: http://localhost:3000
- **Login**: admin/admin
- **Dashboards**: http://localhost:3000/dashboards

## 🚨 **3. Alertmanager**

### **Configuração**
- **Arquivo**: `monitoring/alertmanager.yml`
- **Porta**: 9093
- **Roteamento**: Por severidade e serviço

### **Alertas Configurados**

#### **Alertas de Sistema**
- **HighCPUUsage**: CPU > 80% por 5min
- **HighMemoryUsage**: Memória > 85% por 5min
- **HighDiskUsage**: Disco > 90% por 5min
- **HighLoadAverage**: Load > 5 por 5min

#### **Alertas de Aplicação**
- **HighAPIResponseTime**: P95 > 2s por 5min
- **HighAPIErrorRate**: Erro > 5% por 2min
- **LowAPIRequestRate**: < 0.1 req/s por 10min

#### **Alertas de Banco de Dados**
- **HighDatabaseConnections**: > 80 conexões por 5min
- **HighDatabaseQueryTime**: > 1000ms por 5min

#### **Alertas de Cache**
- **HighRedisMemoryUsage**: > 80% por 5min
- **HighRedisConnections**: > 100 conexões por 5min

#### **Alertas de ETL**
- **ETLJobFailed**: Job falhou
- **ETLJobDurationHigh**: > 1 hora

#### **Alertas de Serviços**
- **ServiceDown**: Serviço indisponível por 1min
- **PrometheusDown**: Prometheus indisponível
- **GrafanaDown**: Grafana indisponível

#### **Alertas de Segurança**
- **HighFailedLoginAttempts**: > 10 tentativas/min por 2min
- **SuspiciousActivity**: Eventos de alta severidade

#### **Alertas de Performance**
- **HighGCPressure**: > 10 GCs/min por 5min
- **HighThreadCount**: > 100 threads por 5min

### **Receivers Configurados**
- **critical-receiver**: admin@bdfut.com + webhook
- **system-receiver**: ops@bdfut.com + webhook
- **api-receiver**: api-team@bdfut.com + webhook
- **database-receiver**: dba@bdfut.com + webhook
- **cache-receiver**: cache-team@bdfut.com + webhook
- **etl-receiver**: etl-team@bdfut.com + webhook
- **security-receiver**: security@bdfut.com + webhook + PagerDuty

### **Acesso**
- **URL**: http://localhost:9093
- **Alertas**: http://localhost:9093/#/alerts
- **Silences**: http://localhost:9093/#/silences

## 🏥 **4. Health Checks**

### **Configuração**
- **Arquivo**: `bdfut/core/health.py`
- **Endpoint**: `/health`
- **Verificações**: Assíncronas e síncronas

### **Verificações Implementadas**

#### **Verificações Assíncronas**
- **Database**: Conexão e query simples
- **Redis**: Ping e conectividade
- **External API**: Acessibilidade da API SportMonks

#### **Verificações Síncronas**
- **System Resources**: CPU, memória, disco
- **Application Status**: Uptime, threads, conexões

### **Status Possíveis**
- **HEALTHY**: Tudo funcionando normalmente
- **DEGRADED**: Problemas menores detectados
- **UNHEALTHY**: Problemas críticos
- **UNKNOWN**: Não foi possível verificar

### **Exemplo de Resposta**
```json
{
  "status": "healthy",
  "timestamp": 1642248000.0,
  "uptime_seconds": 3600.0,
  "version": "2.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful",
      "response_time_ms": 15.5,
      "details": {"query_result": 1}
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection successful",
      "response_time_ms": 2.1,
      "details": {"ping_result": true}
    },
    "system_resources": {
      "status": "healthy",
      "message": "System resources normal",
      "response_time_ms": 5.0,
      "details": {
        "cpu_percent": 45.2,
        "memory_percent": 67.8,
        "disk_percent": 23.1
      }
    }
  }
}
```

## 📋 **5. Métricas Customizadas**

### **Métricas de Aplicação**
- **bdfut_api_requests_total**: Total de requisições HTTP
- **bdfut_api_request_duration_seconds**: Duração das requisições
- **bdfut_etl_jobs_total**: Total de jobs ETL
- **bdfut_etl_job_duration_seconds**: Duração dos jobs ETL
- **bdfut_database_queries_total**: Total de consultas ao banco
- **bdfut_database_query_duration_seconds**: Duração das consultas
- **bdfut_cache_operations_total**: Total de operações de cache

### **Métricas de Sistema**
- **bdfut_cpu_usage_percent**: Uso de CPU
- **bdfut_memory_usage_bytes**: Uso de memória
- **bdfut_thread_count**: Número de threads

### **Métricas de Negócio**
- **bdfut_teams_processed_total**: Times processados
- **bdfut_players_processed_total**: Jogadores processados
- **bdfut_matches_processed_total**: Partidas processadas
- **bdfut_data_last_updated_timestamp**: Timestamp da última atualização

### **Acesso às Métricas**
- **URL**: http://localhost:8000/metrics
- **Formato**: Prometheus exposition format

## 🚀 **Como Usar**

### **1. Iniciar Monitoramento**

```bash
# Via Docker Compose
docker-compose up -d prometheus grafana alertmanager

# Via Makefile
make monitoring-start
```

### **2. Verificar Status**

```bash
# Health check da aplicação
curl http://localhost:8001/health

# Métricas da aplicação
curl http://localhost:8000/metrics

# Status do Prometheus
curl http://localhost:9090/-/healthy

# Status do Grafana
curl http://localhost:3000/api/health
```

### **3. Acessar Dashboards**

```bash
# Abrir Grafana
open http://localhost:3000

# Abrir Prometheus
open http://localhost:9090

# Abrir Alertmanager
open http://localhost:9093
```

### **4. Configurar Alertas**

```bash
# Testar alerta
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning"
    },
    "annotations": {
      "summary": "Test alert",
      "description": "This is a test alert"
    }
  }]'
```

## 🔧 **Configuração Avançada**

### **Ambiente de Produção**

```yaml
# prometheus.yml
global:
  scrape_interval: 30s
  evaluation_interval: 30s
  external_labels:
    cluster: 'bdfut-production'
    environment: 'production'

# alertmanager.yml
global:
  smtp_smarthost: 'smtp.company.com:587'
  smtp_from: 'alerts@company.com'
  smtp_auth_username: 'alerts@company.com'
  smtp_auth_password: 'secure_password'
```

### **Alertas Personalizados**

```yaml
# Adicionar em basic_alerts.yml
- alert: CustomAlert
  expr: custom_metric > threshold
  for: 5m
  labels:
    severity: warning
    service: custom
  annotations:
    summary: "Custom alert triggered"
    description: "Custom metric exceeded threshold"
```

### **Dashboards Personalizados**

```json
{
  "title": "Custom Dashboard",
  "panels": [
    {
      "title": "Custom Metric",
      "targets": [
        {
          "expr": "custom_metric",
          "legendFormat": "Custom Metric"
        }
      ]
    }
  ]
}
```

## 📚 **Comandos Úteis**

### **Prometheus**
```bash
# Verificar configuração
promtool check config prometheus.yml

# Testar regras
promtool check rules rules/*.yml

# Backup de dados
tar -czf prometheus-backup.tar.gz /var/lib/prometheus/
```

### **Grafana**
```bash
# Backup de dashboards
curl -H "Authorization: Bearer $GRAFANA_TOKEN" \
  http://localhost:3000/api/dashboards/db/bdfut-overview

# Restaurar dashboard
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GRAFANA_TOKEN" \
  -d @dashboard.json \
  http://localhost:3000/api/dashboards/db
```

### **Alertmanager**
```bash
# Testar configuração
amtool check-config alertmanager.yml

# Listar alertas
amtool alert query

# Silenciar alerta
amtool silence add alertname=TestAlert
```

## 🚨 **Troubleshooting**

### **Problemas Comuns**

1. **Prometheus não coleta métricas**
   - Verificar se o target está UP em http://localhost:9090/targets
   - Verificar conectividade de rede
   - Verificar configuração de scraping

2. **Grafana não mostra dados**
   - Verificar datasource Prometheus
   - Verificar queries das métricas
   - Verificar time range do dashboard

3. **Alertas não são enviados**
   - Verificar configuração do Alertmanager
   - Verificar conectividade SMTP
   - Verificar regras de roteamento

4. **Health checks falham**
   - Verificar dependências (asyncpg, redis, httpx)
   - Verificar conectividade com serviços externos
   - Verificar configuração de timeout

### **Logs Úteis**

```bash
# Logs do Prometheus
docker logs prometheus

# Logs do Grafana
docker logs grafana

# Logs do Alertmanager
docker logs alertmanager

# Logs da aplicação
docker logs bdfut-app
```

### **Métricas de Debug**

```bash
# Verificar métricas disponíveis
curl http://localhost:8000/metrics | grep bdfut

# Verificar targets do Prometheus
curl http://localhost:9090/api/v1/targets

# Verificar regras ativas
curl http://localhost:9090/api/v1/rules
```

## 📈 **Próximos Passos**

1. **Monitoramento Avançado**
   - Métricas de negócio específicas
   - Dashboards executivos
   - Alertas inteligentes com ML

2. **Integração com Ferramentas Externas**
   - Datadog, New Relic, AppDynamics
   - PagerDuty para alertas críticos
   - Slack/Teams para notificações

3. **Observabilidade Completa**
   - Logging estruturado
   - Tracing distribuído
   - APM (Application Performance Monitoring)

---

**📞 Suporte**: Para dúvidas sobre monitoramento, consulte a equipe de DevOps ou abra uma issue no repositório.
