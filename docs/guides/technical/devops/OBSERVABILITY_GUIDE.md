# ============================================
# BDFut Observability Guide
# ============================================
"""
Guia completo de observabilidade do sistema BDFut.
Cobre logging estruturado, tracing distribuído, APM e SLIs/SLOs.
"""

## 🔍 **Visão Geral**

O sistema de observabilidade do BDFut é composto por quatro pilares principais:

1. **📝 Logging Estruturado**: Logs JSON com contexto e correlação
2. **🔗 Tracing Distribuído**: Rastreamento de requisições com OpenTelemetry
3. **📊 APM**: Monitoramento de performance da aplicação
4. **🎯 SLIs/SLOs**: Indicadores e objetivos de qualidade de serviço

## 🏗️ **Arquitetura de Observabilidade**

```
┌─────────────────────────────────────────────────────────────────┐
│                        BDFut Application                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Logging   │  │   Tracing   │  │     APM     │  │ SLI/SLO │ │
│  │ Estruturado │  │ Distribuído │  │             │  │         │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Observability Stack                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Grafana   │  │   Jaeger    │  │ Prometheus  │  │  Logs   │ │
│  │ Dashboards  │  │   Traces    │  │  Metrics    │  │ Storage │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📝 **1. Logging Estruturado**

### **Características**
- **Formato JSON**: Logs estruturados para fácil parsing
- **Contexto de Correlação**: Request ID, User ID, Session ID
- **Categorização**: Logs organizados por categoria (API, ETL, Database, etc.)
- **Performance Metrics**: Duração de operações incluída nos logs
- **Error Tracking**: Stack traces e contexto de erro

### **Categorias de Log**
```python
class LogCategory(Enum):
    SYSTEM = "system"
    API = "api"
    ETL = "etl"
    DATABASE = "database"
    CACHE = "cache"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    AUDIT = "audit"
```

### **Exemplo de Log Estruturado**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Requisição finalizada",
  "category": "api",
  "context": {
    "request_id": "req_123456",
    "user_id": "user_789",
    "session_id": "sess_abc123",
    "correlation_id": "corr_def456",
    "service": "bdfut",
    "version": "2.0.0",
    "environment": "development",
    "hostname": "bdfut-server-01",
    "pid": 1234
  },
  "data": {
    "method": "GET",
    "path": "/api/v1/teams",
    "status_code": 200
  },
  "performance": {
    "response_time_ms": 150.5
  }
}
```

### **Uso Básico**
```python
from bdfut.core.logging import logger, LogContext, LogCategory

# Log simples
logger.info("Sistema iniciado", category=LogCategory.SYSTEM)

# Log com contexto
with LogContext(request_id="req_123", user_id="user_456"):
    logger.info("Operação executada", 
                category=LogCategory.API,
                data={"operation": "get_teams"})

# Log de performance
logger.info("Job ETL concluído",
            category=LogCategory.ETL,
            performance={"duration_ms": 5000},
            data={"records_processed": 1000})
```

### **Loggers Especializados**
```python
from bdfut.core.logging import api_logger, etl_logger, db_logger, security_logger

# API Logger
api_logger.request_start("GET", "/api/v1/teams")
api_logger.request_end("GET", "/api/v1/teams", 200, 0.15)

# ETL Logger
etl_logger.job_start("sync_teams", "daily_sync")
etl_logger.job_progress("sync_teams", 50.0, 500, 1000)
etl_logger.job_end("sync_teams", "success", 300.0)

# Database Logger
db_logger.query_start("SELECT", "teams", "SELECT * FROM teams")
db_logger.query_end("SELECT", 0.05, 100, "teams")

# Security Logger
security_logger.auth_success("user_123", "jwt", "192.168.1.1")
security_logger.access_denied("user_456", "/admin", "read", "192.168.1.2")
```

## 🔗 **2. Tracing Distribuído**

### **Características**
- **OpenTelemetry**: Padrão aberto para observabilidade
- **Jaeger Integration**: Visualização de traces
- **Auto-instrumentation**: Bibliotecas instrumentadas automaticamente
- **Context Propagation**: Contexto de trace propagado entre serviços
- **Performance Analysis**: Análise de latência e bottlenecks

### **Configuração**
```python
from bdfut.core.tracing import configure_tracing

# Configuração básica
configure_tracing(
    environment="development",
    jaeger_endpoint="http://localhost:14268/api/traces",
    enable_tracing=True
)
```

### **Uso Básico**
```python
from bdfut.core.tracing import trace_function, TraceContext, api_tracer

# Decorator para funções
@trace_function("process_team_data")
def process_team_data(team_id: str):
    # código da função
    pass

# Context manager
with TraceContext("etl_job", {"job_type": "daily_sync"}):
    # código do job
    pass

# Tracer especializado para API
span = api_tracer.trace_request("GET", "/api/v1/teams")
api_tracer.trace_response(span, 200, 0.15)
```

### **Tracers Especializados**
```python
from bdfut.core.tracing import api_tracer, etl_tracer, db_tracer, cache_tracer

# API Tracer
span = api_tracer.trace_request("GET", "/api/v1/teams")
api_tracer.trace_response(span, 200, 0.15)

# ETL Tracer
span = etl_tracer.trace_job("sync_teams", "daily_sync")
etl_tracer.trace_data_processing(span, "transform", 1000, 0)
etl_tracer.trace_external_api_call(span, "sportmonks", "/teams", 0.5, 200)

# Database Tracer
span = db_tracer.trace_query("SELECT", "teams")
db_tracer.trace_query_result(span, 100, 0.05)

# Cache Tracer
span = cache_tracer.trace_cache_operation("GET", "team:123")
cache_tracer.trace_cache_result(span, True, 0.01)
```

## 📊 **3. APM (Application Performance Monitoring)**

### **Características**
- **Performance Metrics**: CPU, memória, GC, threads
- **Request Tracking**: Tempo de resposta, throughput, taxa de erro
- **Memory Profiling**: Análise de uso de memória
- **Code Profiling**: Profiling de funções e métodos
- **Alertas Automáticos**: Alertas baseados em thresholds

### **Configuração**
```python
from bdfut.core.apm import configure_apm

# Configuração básica
configure_apm(
    environment="development",
    enable_monitoring=True,
    monitoring_interval=5.0
)
```

### **Uso Básico**
```python
from bdfut.core.apm import profile_performance, get_performance_metrics

# Decorator para performance
@profile_performance(endpoint="get_teams", method="GET")
def get_teams():
    # código da função
    pass

# Métricas de performance
metrics = get_performance_metrics()
print(f"CPU: {metrics['current']['cpu_percent']}%")
print(f"Memory: {metrics['current']['memory_mb']}MB")
```

### **Memory Profiling**
```python
from bdfut.core.apm import memory_profiler

# Iniciar tracing de memória
memory_profiler.start_tracing()

# Capturar snapshot
snapshot = memory_profiler.take_snapshot("after_data_load")

# Obter estatísticas
stats = memory_profiler.get_memory_stats()
print(f"Total memory: {stats['total_size_mb']}MB")
```

### **Code Profiling**
```python
from bdfut.core.apm import code_profiler

# Decorator para profiling de código
@code_profiler.profile_function("process_teams")
def process_teams(teams):
    # código da função
    pass

# Estatísticas de funções
stats = code_profiler.get_function_stats()
for func_name, func_stats in stats.items():
    print(f"{func_name}: {func_stats['average_time']}ms avg")
```

## 🎯 **4. SLIs/SLOs**

### **SLIs (Service Level Indicators)**
- **API Availability**: Disponibilidade da API
- **API Latency**: Latência P95 da API
- **API Throughput**: Requisições por segundo
- **API Error Rate**: Taxa de erro da API
- **ETL Job Success Rate**: Taxa de sucesso dos jobs ETL
- **Data Freshness**: Frescor dos dados
- **Database Availability**: Disponibilidade do banco

### **SLOs (Service Level Objectives)**
- **API Availability**: 99.9% de disponibilidade
- **API Latency**: 95% das requisições < 2s
- **API Error Rate**: < 0.1% de taxa de erro
- **ETL Job Success**: 99% de taxa de sucesso
- **Data Freshness**: 95% dos dados atualizados em < 1h
- **Database Availability**: 99.95% de disponibilidade

### **Uso Básico**
```python
from bdfut.core.sli_slo import slo_manager, track_slo

# Decorator para SLO
@track_slo("api_availability_slo")
def handle_api_request():
    # código da função
    pass

# Registro manual
slo_manager.record_api_request(success=True, response_time=0.15)
slo_manager.record_etl_job(success=True)
slo_manager.record_database_query(success=True)

# Avaliação de SLOs
slo_statuses = slo_manager.evaluate_slos()
for slo_name, status in slo_statuses.items():
    print(f"{slo_name}: {status.current_percentage}%")
```

### **Relatório de SLOs**
```python
from bdfut.core.sli_slo import get_slo_dashboard_data

# Dados para dashboard
dashboard_data = get_slo_dashboard_data()
print(f"Total SLOs: {dashboard_data['summary']['total_slos']}")
print(f"Healthy: {dashboard_data['summary']['healthy']}")
print(f"Breached: {dashboard_data['summary']['breached']}")
```

## 📊 **Dashboards Disponíveis**

### **1. BDFut Overview**
- Métricas básicas do sistema
- Performance da API
- Status dos jobs ETL
- Uso de cache

### **2. BDFut System Metrics**
- CPU, memória, disco
- Load average
- Conexões de banco
- Duração de consultas

### **3. BDFut Observability Dashboard**
- SLIs/SLOs em tempo real
- Métricas de APM
- Duração de violações de SLO
- Performance geral

### **4. BDFut SLI/SLO Dashboard**
- Status de todos os SLOs
- Tendências de disponibilidade
- Tendências de latência
- Duração de violações

## 🚀 **Como Usar**

### **1. Configuração Inicial**

```python
# Configurar logging
from bdfut.core.logging import configure_logging
configure_logging(environment="development", log_level="INFO")

# Configurar tracing
from bdfut.core.tracing import configure_tracing
configure_tracing(environment="development")

# Configurar APM
from bdfut.core.apm import configure_apm
configure_apm(environment="development")

# Configurar SLIs/SLOs
from bdfut.core.sli_slo import configure_sli_slo
configure_sli_slo(environment="development")
```

### **2. Integração com FastAPI**

```python
from fastapi import FastAPI
from bdfut.core.logging import api_logger
from bdfut.core.tracing import api_tracer
from bdfut.core.apm import profile_performance

app = FastAPI()

@app.middleware("http")
async def observability_middleware(request, call_next):
    # Iniciar trace
    span = api_tracer.trace_request(
        request.method, 
        str(request.url.path),
        dict(request.headers)
    )
    
    # Log de início
    api_logger.request_start(
        request.method,
        str(request.url.path),
        dict(request.headers)
    )
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Log de sucesso
        response_time = time.time() - start_time
        api_logger.request_end(
            request.method,
            str(request.url.path),
            response.status_code,
            response_time
        )
        
        # Finalizar trace
        api_tracer.trace_response(span, response.status_code, response_time)
        
        return response
        
    except Exception as e:
        # Log de erro
        response_time = time.time() - start_time
        api_logger.request_error(
            request.method,
            str(request.url.path),
            e,
            response_time
        )
        
        # Finalizar trace com erro
        api_tracer.trace_response(span, 500, response_time)
        
        raise
```

### **3. Integração com ETL**

```python
from bdfut.core.logging import etl_logger
from bdfut.core.tracing import etl_tracer
from bdfut.core.apm import profile_performance
from bdfut.core.sli_slo import slo_manager

@profile_performance(endpoint="etl_job", method="ETL")
def run_etl_job(job_name: str, job_type: str):
    # Iniciar trace
    span = etl_tracer.trace_job(job_name, job_type)
    
    # Log de início
    etl_logger.job_start(job_name, job_type)
    
    start_time = time.time()
    success = False
    
    try:
        # Executar job
        # ... código do job ...
        
        success = True
        
        # Log de sucesso
        duration = time.time() - start_time
        etl_logger.job_end(job_name, "success", duration, 1000, 0)
        
        # Registrar SLO
        slo_manager.record_etl_job(success)
        
        return result
        
    except Exception as e:
        # Log de erro
        duration = time.time() - start_time
        etl_logger.job_error(job_name, e, duration)
        
        # Registrar SLO
        slo_manager.record_etl_job(success)
        
        raise
```

## 🔧 **Configuração Avançada**

### **Ambiente de Produção**
```python
# Logging em produção
configure_logging(
    environment="production",
    log_level="WARNING"
)

# Tracing em produção
configure_tracing(
    environment="production",
    jaeger_endpoint="http://jaeger-collector:14268/api/traces"
)

# APM em produção
configure_apm(
    environment="production",
    enable_monitoring=True,
    monitoring_interval=10.0
)

# SLIs/SLOs em produção
configure_sli_slo(environment="production")
```

### **Filtros e Samplers**
```python
# Sampling de traces
from opentelemetry.sdk.trace.sampling import TraceIdRatioBasedSampler

# 10% de sampling em produção
sampler = TraceIdRatioBasedSampler(0.1)
trace.set_tracer_provider(TracerProvider(sampler=sampler))

# Filtros de log
class LogFilter(logging.Filter):
    def filter(self, record):
        # Filtrar logs de debug em produção
        return record.levelno >= logging.INFO
```

## 📈 **Métricas e Alertas**

### **Métricas Prometheus**
- `bdfut_slo_status_percentage`: Status dos SLOs
- `bdfut_slo_breach_duration_seconds`: Duração de violações
- `bdfut_apm_cpu_usage_percent`: Uso de CPU
- `bdfut_apm_memory_usage_mb`: Uso de memória
- `bdfut_apm_gc_pressure`: Pressão do GC

### **Alertas Configurados**
- SLO violado por mais de 5 minutos
- CPU usage > 80% por 5 minutos
- Memory usage > 85% por 5 minutos
- GC pressure > 10 por minuto
- Error rate > 1% por 2 minutos

## 🚨 **Troubleshooting**

### **Problemas Comuns**

1. **Logs não aparecem**
   - Verificar configuração de nível de log
   - Verificar permissões de escrita no diretório logs/

2. **Traces não aparecem no Jaeger**
   - Verificar se Jaeger está rodando
   - Verificar endpoint de configuração
   - Verificar sampling rate

3. **Métricas de APM não atualizam**
   - Verificar se monitoramento está ativo
   - Verificar interval de coleta
   - Verificar Prometheus config

4. **SLOs sempre em estado UNKNOWN**
   - Verificar se medições estão sendo registradas
   - Verificar janela de medição
   - Verificar thresholds configurados

### **Comandos Úteis**

```bash
# Verificar logs
tail -f logs/bdfut.log
tail -f logs/bdfut-error.log

# Verificar métricas
curl http://localhost:8000/metrics

# Verificar health
curl http://localhost:8000/health

# Verificar SLOs
curl http://localhost:8000/slo-status
```

## 📚 **Recursos Adicionais**

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [SLI/SLO Best Practices](https://sre.google/sre-book/service-level-objectives/)

## 🔄 **Próximos Passos**

1. **Observabilidade Avançada**
   - Machine learning para detecção de anomalias
   - Correlação automática entre logs, traces e métricas
   - Alertas inteligentes baseados em contexto

2. **Integração com Ferramentas Externas**
   - Datadog, New Relic, AppDynamics
   - PagerDuty para alertas
   - Slack/Teams para notificações

3. **Observabilidade de Negócio**
   - Métricas de negócio
   - SLIs baseados em KPIs
   - Dashboards executivos

---

**📞 Suporte**: Para dúvidas sobre observabilidade, consulte a equipe de DevOps ou abra uma issue no repositório.
