# ============================================
# BDFut Monitoring Guide
# ============================================
"""
Guia completo de monitoramento do sistema BDFut.
Cobre métricas, alertas, dashboards e health checks.
"""

## 📊 **Visão Geral**

O sistema de monitoramento do BDFut é baseado em:
- **Prometheus**: Coleta e armazenamento de métricas
- **Grafana**: Visualização e dashboards
- **Alertmanager**: Gerenciamento de alertas
- **Health Checks**: Verificações de saúde dos componentes

## 🏗️ **Arquitetura de Monitoramento**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   BDFut App     │───▶│   Prometheus    │───▶│     Grafana     │
│   (Métricas)    │    │   (Coleta)      │    │  (Dashboards)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │  Alertmanager   │              │
         │              │   (Alertas)     │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Health Checks  │    │   Notificações  │    │   Logs & Traces │
│   (Saúde)       │    │  (Email/Slack)  │    │   (Debugging)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📈 **Métricas Implementadas**

### **Métricas de Aplicação**
- `bdfut_api_requests_total`: Total de requisições da API
- `bdfut_api_request_duration_seconds`: Duração das requisições
- `bdfut_etl_jobs_total`: Total de jobs ETL executados
- `bdfut_etl_job_duration_seconds`: Duração dos jobs ETL
- `bdfut_data_sync_total`: Total de sincronizações de dados

### **Métricas de Sistema**
- `bdfut_system_cpu_usage_percent`: Uso de CPU
- `bdfut_system_memory_usage_bytes`: Uso de memória
- `bdfut_system_disk_usage_bytes`: Uso de disco
- `bdfut_system_load_average`: Load average do sistema

### **Métricas de Banco de Dados**
- `bdfut_database_connections`: Conexões ativas
- `bdfut_database_query_duration_seconds`: Duração das consultas
- `bdfut_database_table_size_bytes`: Tamanho das tabelas

### **Métricas de Cache**
- `bdfut_cache_hit_ratio`: Taxa de acerto do cache
- `bdfut_cache_memory_usage_bytes`: Uso de memória do cache
- `bdfut_cache_operations_total`: Operações no cache

### **Métricas de Filas**
- `bdfut_queue_size`: Tamanho das filas
- `bdfut_queue_processing_rate`: Taxa de processamento

## 🚨 **Sistema de Alertas**

### **Alertas Críticos**
- **HighCPUUsage**: CPU > 80% por 5 minutos
- **HighMemoryUsage**: Memória > 4GB por 5 minutos
- **HighAPIErrorRate**: Taxa de erro 5xx > 10%
- **ETLJobFailure**: Jobs ETL falhando
- **ServiceDown**: Serviços fora do ar

### **Alertas de Warning**
- **HighDiskUsage**: Disco > 10GB por 10 minutos
- **HighAPIResponseTime**: P95 > 2s por 5 minutos
- **ETLJobSlow**: P95 > 5 minutos por 5 minutos
- **DatabaseConnectionHigh**: Conexões > 20 por 5 minutos

### **Alertas Informativos**
- **DatabaseTableSizeLarge**: Tabelas > 5GB
- **CacheHitRatioLow**: Taxa de acerto < 80%
- **QueueSizeHigh**: Filas > 1000 itens

## 📊 **Dashboards Disponíveis**

### **1. BDFut Overview**
- **CPU Usage**: Uso de CPU em tempo real
- **Memory Usage**: Uso de memória em tempo real
- **API Request Rate**: Taxa de requisições da API
- **API Response Time**: Tempo de resposta (P50/P95)
- **ETL Jobs Rate**: Taxa de execução dos jobs ETL
- **Cache Hit Ratio**: Taxa de acerto do cache

### **2. BDFut System Metrics**
- **CPU Usage**: Uso detalhado de CPU
- **Memory Usage**: Uso detalhado de memória
- **Disk Usage**: Uso de disco por mount point
- **Load Average**: Load average (1m/5m/15m)
- **Database Connections**: Conexões ativas com o banco
- **Database Query Duration**: Duração das consultas (P50/P95)

## 🏥 **Health Checks**

### **Verificações Básicas**
- **System Resources**: CPU, memória, disco, load average
- **Python Environment**: Versão e módulos críticos
- **Disk Space**: Espaço livre disponível
- **Memory Usage**: Uso de memória
- **CPU Usage**: Uso de CPU

### **Verificações Externas**
- **Supabase**: Conexão e tempo de resposta
- **Redis**: Conexão e informações do servidor
- **Sportmonks API**: Disponibilidade da API externa

### **Status de Saúde**
- **HEALTHY**: Componente funcionando normalmente
- **DEGRADED**: Componente com performance reduzida
- **UNHEALTHY**: Componente com problemas críticos
- **UNKNOWN**: Status não pode ser determinado

## 🚀 **Como Usar**

### **1. Iniciando o Monitoramento**

```bash
# Subir stack completo de monitoramento
make dev-monitoring

# Ou usando Docker Compose diretamente
docker-compose up -d prometheus grafana
```

### **2. Acessando os Serviços**

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Métricas da App**: http://localhost:8000/metrics

### **3. Verificando Health Status**

```bash
# Via CLI
make health

# Via API (quando implementada)
curl http://localhost:8000/health
```

### **4. Visualizando Métricas**

```bash
# Métricas em formato Prometheus
curl http://localhost:8000/metrics

# Status de saúde
curl http://localhost:8000/health
```

## 🔧 **Configuração**

### **Prometheus**
- **Arquivo**: `monitoring/prometheus.yml`
- **Porta**: 9090
- **Retenção**: 15 dias
- **Intervalo de coleta**: 15s

### **Grafana**
- **Arquivo**: `monitoring/grafana/datasources/prometheus.yml`
- **Porta**: 3000
- **Usuário padrão**: admin/admin
- **Dashboards**: Provisionamento automático

### **Alertmanager**
- **Arquivo**: `monitoring/alertmanager.yml`
- **Notificações**: Email e Slack
- **Grupos**: Por severidade (critical/warning/info)

## 📝 **Adicionando Novas Métricas**

### **1. Definindo Métricas**

```python
from prometheus_client import Counter, Histogram, Gauge

# Contador
my_counter = Counter('my_requests_total', 'Total requests', ['method'])

# Histograma
my_histogram = Histogram('my_request_duration_seconds', 'Request duration')

# Gauge
my_gauge = Gauge('my_active_connections', 'Active connections')
```

### **2. Registrando Métricas**

```python
# Incrementar contador
my_counter.labels(method='GET').inc()

# Observar histograma
with my_histogram.time():
    # código a ser medido
    pass

# Definir gauge
my_gauge.set(42)
```

### **3. Adicionando Health Check**

```python
def my_health_check():
    try:
        # verificação
        return HealthCheckResult(
            status=HealthStatus.HEALTHY,
            message="Componente OK"
        )
    except Exception as e:
        return HealthCheckResult(
            status=HealthStatus.UNHEALTHY,
            message=f"Erro: {e}"
        )

# Registrar
health_checker.register_check("my_component", my_health_check)
```

## 🚨 **Troubleshooting**

### **Problemas Comuns**

1. **Prometheus não coleta métricas**
   - Verificar se a app está expondo métricas em `/metrics`
   - Verificar configuração de targets no `prometheus.yml`

2. **Grafana não mostra dados**
   - Verificar datasource do Prometheus
   - Verificar se há métricas sendo coletadas

3. **Alertas não funcionam**
   - Verificar configuração do Alertmanager
   - Verificar regras de alerta no Prometheus

4. **Health checks falhando**
   - Verificar logs da aplicação
   - Verificar conectividade com serviços externos

### **Comandos Úteis**

```bash
# Verificar status dos containers
docker-compose ps

# Ver logs do Prometheus
docker-compose logs prometheus

# Ver logs do Grafana
docker-compose logs grafana

# Testar conectividade
curl http://localhost:9090/api/v1/targets
curl http://localhost:3000/api/health
```

## 📚 **Recursos Adicionais**

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Prometheus Client Python](https://github.com/prometheus/client_python)

## 🔄 **Próximos Passos**

1. **Observabilidade Completa** (DEVOPS-006)
   - Implementar tracing distribuído
   - Adicionar logs estruturados
   - Integrar com sistemas de APM

2. **Métricas Avançadas**
   - Métricas de negócio
   - SLIs/SLOs
   - Métricas de custo

3. **Alertas Inteligentes**
   - Machine learning para detecção de anomalias
   - Alertas baseados em contexto
   - Redução de ruído

---

**📞 Suporte**: Para dúvidas sobre monitoramento, consulte a equipe de DevOps ou abra uma issue no repositório.
