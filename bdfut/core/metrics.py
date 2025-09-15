# ============================================
# BDFut Metrics Module
# ============================================
"""
Módulo de métricas para o sistema BDFut.
Implementa métricas customizadas para Prometheus.
"""

import time
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, Summary, Info, start_http_server

# ============================================
# MÉTRICAS DE APLICAÇÃO
# ============================================

# Contadores
REQUEST_COUNT = Counter(
    'bdfut_api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code']
)

ETL_JOBS_TOTAL = Counter(
    'bdfut_etl_jobs_total',
    'Total number of ETL jobs',
    ['job_name', 'status']
)

DATABASE_QUERIES_TOTAL = Counter(
    'bdfut_database_queries_total',
    'Total number of database queries',
    ['query_type', 'table', 'status']
)

CACHE_OPERATIONS_TOTAL = Counter(
    'bdfut_cache_operations_total',
    'Total number of cache operations',
    ['operation', 'hit']
)

# Histogramas
REQUEST_DURATION = Histogram(
    'bdfut_api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

ETL_JOB_DURATION = Histogram(
    'bdfut_etl_job_duration_seconds',
    'ETL job duration in seconds',
    ['job_name'],
    buckets=[60, 300, 600, 1800, 3600, 7200]
)

DATABASE_QUERY_DURATION = Histogram(
    'bdfut_database_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type', 'table'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

# Gauges
ACTIVE_CONNECTIONS = Gauge(
    'bdfut_active_connections',
    'Number of active connections'
)

CACHE_SIZE = Gauge(
    'bdfut_cache_size_bytes',
    'Cache size in bytes'
)

QUEUE_SIZE = Gauge(
    'bdfut_queue_size',
    'Queue size',
    ['queue_name']
)

# Summaries
DATA_PROCESSED = Summary(
    'bdfut_data_processed_bytes',
    'Amount of data processed in bytes',
    ['data_type']
)

# Info
APPLICATION_INFO = Info(
    'bdfut_application_info',
    'Application information'
)

# ============================================
# MÉTRICAS DE SISTEMA
# ============================================

# CPU e Memória
CPU_USAGE = Gauge(
    'bdfut_cpu_usage_percent',
    'CPU usage percentage'
)

MEMORY_USAGE = Gauge(
    'bdfut_memory_usage_bytes',
    'Memory usage in bytes'
)

THREAD_COUNT = Gauge(
    'bdfut_thread_count',
    'Number of threads'
)

# ============================================
# MÉTRICAS DE NEGÓCIO
# ============================================

# Times processados
TEAMS_PROCESSED = Counter(
    'bdfut_teams_processed_total',
    'Total teams processed'
)

PLAYERS_PROCESSED = Counter(
    'bdfut_players_processed_total',
    'Total players processed'
)

MATCHES_PROCESSED = Counter(
    'bdfut_matches_processed_total',
    'Total matches processed'
)

# Dados atualizados
DATA_LAST_UPDATED = Gauge(
    'bdfut_data_last_updated_timestamp',
    'Timestamp of last data update',
    ['data_type']
)

# ============================================
# FUNÇÕES DE CONVENIÊNCIA
# ============================================

def record_request(method: str, endpoint: str, status_code: int, duration: float):
    """Registra uma requisição HTTP."""
    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status_code=str(status_code)
    ).inc()
    
    REQUEST_DURATION.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)

def record_etl_job(job_name: str, status: str, duration: float):
    """Registra um job ETL."""
    ETL_JOBS_TOTAL.labels(
        job_name=job_name,
        status=status
    ).inc()
    
    ETL_JOB_DURATION.labels(
        job_name=job_name
    ).observe(duration)

def record_database_query(query_type: str, table: str, status: str, duration: float):
    """Registra uma consulta ao banco."""
    DATABASE_QUERIES_TOTAL.labels(
        query_type=query_type,
        table=table,
        status=status
    ).inc()
    
    DATABASE_QUERY_DURATION.labels(
        query_type=query_type,
        table=table
    ).observe(duration)

def record_cache_operation(operation: str, hit: bool):
    """Registra uma operação de cache."""
    CACHE_OPERATIONS_TOTAL.labels(
        operation=operation,
        hit=str(hit)
    ).inc()

def update_active_connections(count: int):
    """Atualiza número de conexões ativas."""
    ACTIVE_CONNECTIONS.set(count)

def update_cache_size(size_bytes: int):
    """Atualiza tamanho do cache."""
    CACHE_SIZE.set(size_bytes)

def update_queue_size(queue_name: str, size: int):
    """Atualiza tamanho da fila."""
    QUEUE_SIZE.labels(queue_name=queue_name).set(size)

def record_data_processed(data_type: str, size_bytes: int):
    """Registra dados processados."""
    DATA_PROCESSED.labels(data_type=data_type).observe(size_bytes)

def update_teams_processed(count: int):
    """Atualiza times processados."""
    TEAMS_PROCESSED.inc(count)

def update_players_processed(count: int):
    """Atualiza jogadores processados."""
    PLAYERS_PROCESSED.inc(count)

def update_matches_processed(count: int):
    """Atualiza partidas processadas."""
    MATCHES_PROCESSED.inc(count)

def update_data_last_updated(data_type: str, timestamp: float):
    """Atualiza timestamp da última atualização."""
    DATA_LAST_UPDATED.labels(data_type=data_type).set(timestamp)

# ============================================
# CONFIGURAÇÃO
# ============================================

def setup_metrics(port: int = 8000):
    """Configura métricas e inicia servidor HTTP."""
    # Define informações da aplicação
    APPLICATION_INFO.info({
        'version': '2.0.0',
        'environment': 'development',
        'service': 'bdfut'
    })
    
    # Inicia servidor HTTP para métricas
    start_http_server(port)
    print(f"Metrics server started on port {port}")

def get_metrics_summary() -> Dict[str, Any]:
    """Retorna resumo das métricas."""
    return {
        "application_info": {
            "version": "2.0.0",
            "environment": "development",
            "service": "bdfut"
        },
        "metrics_available": [
            "bdfut_api_requests_total",
            "bdfut_api_request_duration_seconds",
            "bdfut_etl_jobs_total",
            "bdfut_etl_job_duration_seconds",
            "bdfut_database_queries_total",
            "bdfut_database_query_duration_seconds",
            "bdfut_cache_operations_total",
            "bdfut_active_connections",
            "bdfut_cache_size_bytes",
            "bdfut_queue_size",
            "bdfut_data_processed_bytes",
            "bdfut_cpu_usage_percent",
            "bdfut_memory_usage_bytes",
            "bdfut_thread_count",
            "bdfut_teams_processed_total",
            "bdfut_players_processed_total",
            "bdfut_matches_processed_total",
            "bdfut_data_last_updated_timestamp"
        ]
    }