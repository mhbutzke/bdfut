# ============================================
# BDFut APM (Application Performance Monitoring) Module
# ============================================
"""
Módulo de APM para monitoramento de performance da aplicação BDFut.
Integra métricas de performance, profiling e análise de código.
"""

import time
import psutil
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import functools
import asyncio
from collections import defaultdict, deque
import statistics
import gc
import sys
import tracemalloc

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

class PerformanceMetric(Enum):
    """Tipos de métricas de performance."""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    GC_PRESSURE = "gc_pressure"
    THREAD_COUNT = "thread_count"
    CONNECTION_POOL = "connection_pool"

@dataclass
class PerformanceSnapshot:
    """Snapshot de performance em um momento específico."""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    thread_count: int
    gc_collections: Dict[str, int]
    active_connections: int
    response_time_p95: float
    throughput_rps: float
    error_rate: float

@dataclass
class PerformanceAlert:
    """Alerta de performance."""
    metric: PerformanceMetric
    threshold: float
    current_value: float
    severity: str
    message: str
    timestamp: float

class PerformanceProfiler:
    """Profiler de performance da aplicação."""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.response_times = deque(maxlen=window_size)
        self.error_counts = deque(maxlen=window_size)
        self.request_counts = deque(maxlen=window_size)
        self.performance_snapshots = deque(maxlen=window_size)
        
        # Métricas Prometheus
        if PROMETHEUS_AVAILABLE:
            self.response_time_histogram = Histogram(
                'bdfut_apm_response_time_seconds',
                'Response time distribution',
                ['endpoint', 'method'],
                buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
            )
            
            self.throughput_counter = Counter(
                'bdfut_apm_requests_total',
                'Total requests',
                ['endpoint', 'method', 'status']
            )
            
            self.error_rate_gauge = Gauge(
                'bdfut_apm_error_rate',
                'Error rate percentage',
                ['endpoint']
            )
            
            self.cpu_usage_gauge = Gauge(
                'bdfut_apm_cpu_usage_percent',
                'CPU usage percentage'
            )
            
            self.memory_usage_gauge = Gauge(
                'bdfut_apm_memory_usage_mb',
                'Memory usage in MB'
            )
            
            self.gc_pressure_gauge = Gauge(
                'bdfut_apm_gc_pressure',
                'GC pressure metric'
            )
        
        # Configuração de alertas
        self.alert_thresholds = {
            PerformanceMetric.RESPONSE_TIME: 2.0,  # 2 segundos
            PerformanceMetric.ERROR_RATE: 5.0,    # 5%
            PerformanceMetric.CPU_USAGE: 80.0,     # 80%
            PerformanceMetric.MEMORY_USAGE: 85.0,  # 85%
            PerformanceMetric.GC_PRESSURE: 10.0,   # 10 GCs por minuto
            PerformanceMetric.THREAD_COUNT: 100    # 100 threads
        }
        
        # Estado do profiler
        self.is_monitoring = False
        self.monitor_thread = None
        self.start_time = time.time()
        
        # Estatísticas de GC
        self.gc_stats = {
            'collections_0': 0,
            'collections_1': 0,
            'collections_2': 0
        }
    
    def start_monitoring(self, interval: float = 5.0):
        """Inicia monitoramento contínuo de performance."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Para o monitoramento de performance."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self, interval: float):
        """Loop principal de monitoramento."""
        while self.is_monitoring:
            try:
                snapshot = self._take_performance_snapshot()
                self.performance_snapshots.append(snapshot)
                
                # Atualiza métricas Prometheus
                if PROMETHEUS_AVAILABLE:
                    self._update_prometheus_metrics(snapshot)
                
                # Verifica alertas
                self._check_performance_alerts(snapshot)
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Erro no monitoramento de performance: {e}")
                time.sleep(interval)
    
    def _take_performance_snapshot(self) -> PerformanceSnapshot:
        """Captura snapshot de performance atual."""
        # CPU e memória
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_mb = memory.used / (1024 * 1024)
        
        # Threads
        thread_count = threading.active_count()
        
        # GC
        gc_stats = gc.get_stats()
        gc_collections = {
            'collections_0': gc_stats[0]['collections'],
            'collections_1': gc_stats[1]['collections'],
            'collections_2': gc_stats[2]['collections']
        }
        
        # Conexões ativas (simulado)
        active_connections = len(psutil.net_connections())
        
        # Métricas de resposta
        response_time_p95 = self._calculate_p95_response_time()
        throughput_rps = self._calculate_throughput()
        error_rate = self._calculate_error_rate()
        
        return PerformanceSnapshot(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            memory_percent=memory.percent,
            thread_count=thread_count,
            gc_collections=gc_collections,
            active_connections=active_connections,
            response_time_p95=response_time_p95,
            throughput_rps=throughput_rps,
            error_rate=error_rate
        )
    
    def _calculate_p95_response_time(self) -> float:
        """Calcula P95 do tempo de resposta."""
        if not self.response_times:
            return 0.0
        
        sorted_times = sorted(self.response_times)
        index = int(0.95 * len(sorted_times))
        return sorted_times[index] if index < len(sorted_times) else sorted_times[-1]
    
    def _calculate_throughput(self) -> float:
        """Calcula throughput em requisições por segundo."""
        if len(self.request_counts) < 2:
            return 0.0
        
        # Calcula diferença entre primeiro e último
        total_requests = sum(self.request_counts)
        time_window = len(self.request_counts) * 5.0  # 5 segundos por snapshot
        return total_requests / time_window if time_window > 0 else 0.0
    
    def _calculate_error_rate(self) -> float:
        """Calcula taxa de erro."""
        if not self.error_counts or not self.request_counts:
            return 0.0
        
        total_errors = sum(self.error_counts)
        total_requests = sum(self.request_counts)
        
        return (total_errors / total_requests * 100) if total_requests > 0 else 0.0
    
    def _update_prometheus_metrics(self, snapshot: PerformanceSnapshot):
        """Atualiza métricas Prometheus."""
        if not PROMETHEUS_AVAILABLE:
            return
        
        self.cpu_usage_gauge.set(snapshot.cpu_percent)
        self.memory_usage_gauge.set(snapshot.memory_mb)
        
        # GC pressure
        gc_pressure = sum(snapshot.gc_collections.values())
        self.gc_pressure_gauge.set(gc_pressure)
    
    def _check_performance_alerts(self, snapshot: PerformanceSnapshot):
        """Verifica alertas de performance."""
        alerts = []
        
        # CPU
        if snapshot.cpu_percent > self.alert_thresholds[PerformanceMetric.CPU_USAGE]:
            alerts.append(PerformanceAlert(
                metric=PerformanceMetric.CPU_USAGE,
                threshold=self.alert_thresholds[PerformanceMetric.CPU_USAGE],
                current_value=snapshot.cpu_percent,
                severity="warning",
                message=f"CPU usage high: {snapshot.cpu_percent:.1f}%",
                timestamp=snapshot.timestamp
            ))
        
        # Memória
        if snapshot.memory_percent > self.alert_thresholds[PerformanceMetric.MEMORY_USAGE]:
            alerts.append(PerformanceAlert(
                metric=PerformanceMetric.MEMORY_USAGE,
                threshold=self.alert_thresholds[PerformanceMetric.MEMORY_USAGE],
                current_value=snapshot.memory_percent,
                severity="warning",
                message=f"Memory usage high: {snapshot.memory_percent:.1f}%",
                timestamp=snapshot.timestamp
            ))
        
        # Tempo de resposta
        if snapshot.response_time_p95 > self.alert_thresholds[PerformanceMetric.RESPONSE_TIME]:
            alerts.append(PerformanceAlert(
                metric=PerformanceMetric.RESPONSE_TIME,
                threshold=self.alert_thresholds[PerformanceMetric.RESPONSE_TIME],
                current_value=snapshot.response_time_p95,
                severity="warning",
                message=f"Response time high: {snapshot.response_time_p95:.2f}s",
                timestamp=snapshot.timestamp
            ))
        
        # Taxa de erro
        if snapshot.error_rate > self.alert_thresholds[PerformanceMetric.ERROR_RATE]:
            alerts.append(PerformanceAlert(
                metric=PerformanceMetric.ERROR_RATE,
                threshold=self.alert_thresholds[PerformanceMetric.ERROR_RATE],
                current_value=snapshot.error_rate,
                severity="critical",
                message=f"Error rate high: {snapshot.error_rate:.1f}%",
                timestamp=snapshot.timestamp
            ))
        
        # Processa alertas
        for alert in alerts:
            self._handle_performance_alert(alert)
    
    def _handle_performance_alert(self, alert: PerformanceAlert):
        """Processa alerta de performance."""
        # Aqui você pode integrar com sistemas de alerta
        print(f"🚨 Performance Alert: {alert.message}")
        
        # Log estruturado
        from .logging import logger
        logger.warning("Performance alert triggered",
                      category=LogCategory.PERFORMANCE,
                      data=asdict(alert))
    
    def record_request(self, endpoint: str, method: str, response_time: float, 
                      status_code: int):
        """Registra requisição para análise de performance."""
        self.response_times.append(response_time)
        self.request_counts.append(1)
        
        if status_code >= 400:
            self.error_counts.append(1)
        else:
            self.error_counts.append(0)
        
        # Atualiza métricas Prometheus
        if PROMETHEUS_AVAILABLE:
            self.response_time_histogram.labels(
                endpoint=endpoint, method=method
            ).observe(response_time)
            
            self.throughput_counter.labels(
                endpoint=endpoint, method=method, status=str(status_code)
            ).inc()
            
            self.error_rate_gauge.labels(endpoint=endpoint).set(
                self._calculate_error_rate()
            )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance."""
        if not self.performance_snapshots:
            return {}
        
        latest = self.performance_snapshots[-1]
        
        return {
            "current": asdict(latest),
            "averages": {
                "cpu_percent": statistics.mean([s.cpu_percent for s in self.performance_snapshots]),
                "memory_mb": statistics.mean([s.memory_mb for s in self.performance_snapshots]),
                "response_time_p95": statistics.mean([s.response_time_p95 for s in self.performance_snapshots]),
                "throughput_rps": statistics.mean([s.throughput_rps for s in self.performance_snapshots]),
                "error_rate": statistics.mean([s.error_rate for s in self.performance_snapshots])
            },
            "uptime_seconds": time.time() - self.start_time,
            "total_requests": sum(self.request_counts),
            "total_errors": sum(self.error_counts)
        }

# ============================================
# DECORATORS DE PERFORMANCE
# ============================================

def profile_performance(endpoint: str = None, method: str = None):
    """Decorator para profiling de performance."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                status_code = 200
                return result
                
            except Exception as e:
                status_code = 500
                raise
                
            finally:
                response_time = time.time() - start_time
                
                # Registra métricas
                profiler.record_request(
                    endpoint=endpoint or func.__name__,
                    method=method or "FUNCTION",
                    response_time=response_time,
                    status_code=status_code
                )
        
        return wrapper
    return decorator

def profile_async_performance(endpoint: str = None, method: str = None):
    """Decorator para profiling de performance assíncrono."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                status_code = 200
                return result
                
            except Exception as e:
                status_code = 500
                raise
                
            finally:
                response_time = time.time() - start_time
                
                # Registra métricas
                profiler.record_request(
                    endpoint=endpoint or func.__name__,
                    method=method or "ASYNC_FUNCTION",
                    response_time=response_time,
                    status_code=status_code
                )
        
        return wrapper
    return decorator

# ============================================
# MEMORY PROFILING
# ============================================

class MemoryProfiler:
    """Profiler de memória."""
    
    def __init__(self):
        self.snapshots = []
        self.tracemalloc_enabled = False
    
    def start_tracing(self):
        """Inicia tracing de memória."""
        if not self.tracemalloc_enabled:
            tracemalloc.start()
            self.tracemalloc_enabled = True
    
    def stop_tracing(self):
        """Para tracing de memória."""
        if self.tracemalloc_enabled:
            tracemalloc.stop()
            self.tracemalloc_enabled = False
    
    def take_snapshot(self, label: str = None):
        """Captura snapshot de memória."""
        if not self.tracemalloc_enabled:
            return None
        
        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append({
            'timestamp': time.time(),
            'label': label,
            'snapshot': snapshot
        })
        
        return snapshot
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de memória."""
        if not self.snapshots:
            return {}
        
        latest = self.snapshots[-1]['snapshot']
        
        # Top 10 maiores blocos de memória
        top_stats = latest.statistics('lineno')
        top_10 = top_stats[:10]
        
        return {
            "total_size_mb": sum(stat.size for stat in top_stats) / (1024 * 1024),
            "top_10_allocations": [
                {
                    "filename": stat.traceback.format()[0],
                    "size_mb": stat.size / (1024 * 1024),
                    "count": stat.count
                }
                for stat in top_10
            ],
            "snapshots_count": len(self.snapshots)
        }

# ============================================
# CODE PROFILING
# ============================================

class CodeProfiler:
    """Profiler de código."""
    
    def __init__(self):
        self.function_stats = defaultdict(lambda: {
            'call_count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0
        })
    
    def profile_function(self, func_name: str = None):
        """Decorator para profiling de função."""
        def decorator(func):
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time
                    
                    stats = self.function_stats[name]
                    stats['call_count'] += 1
                    stats['total_time'] += execution_time
                    stats['min_time'] = min(stats['min_time'], execution_time)
                    stats['max_time'] = max(stats['max_time'], execution_time)
            
            return wrapper
        return decorator
    
    def get_function_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de funções."""
        result = {}
        
        for func_name, stats in self.function_stats.items():
            if stats['call_count'] > 0:
                result[func_name] = {
                    'call_count': stats['call_count'],
                    'total_time': stats['total_time'],
                    'average_time': stats['total_time'] / stats['call_count'],
                    'min_time': stats['min_time'],
                    'max_time': stats['max_time']
                }
        
        return result

# ============================================
# INSTÂNCIAS GLOBAIS
# ============================================

# Profiler principal
profiler = PerformanceProfiler()

# Profilers especializados
memory_profiler = MemoryProfiler()
code_profiler = CodeProfiler()

# ============================================
# CONFIGURAÇÃO DE AMBIENTE
# ============================================

def configure_apm(environment: str = "development", 
                  enable_monitoring: bool = True,
                  monitoring_interval: float = 5.0):
    """Configura o sistema de APM baseado no ambiente."""
    
    if not enable_monitoring:
        print("APM desabilitado")
        return
    
    try:
        # Configura profiler
        profiler.start_monitoring(monitoring_interval)
        
        # Configura memory profiling em desenvolvimento
        if environment == "development":
            memory_profiler.start_tracing()
        
        print(f"APM configurado para ambiente {environment}")
        
    except Exception as e:
        print(f"Erro ao configurar APM: {e}")

# ============================================
# UTILITÁRIOS
# ============================================

def get_performance_metrics() -> Dict[str, Any]:
    """Retorna métricas de performance atuais."""
    return profiler.get_performance_summary()

def get_memory_metrics() -> Dict[str, Any]:
    """Retorna métricas de memória."""
    return memory_profiler.get_memory_stats()

def get_code_metrics() -> Dict[str, Any]:
    """Retorna métricas de código."""
    return code_profiler.get_function_stats()

def force_gc():
    """Força coleta de lixo."""
    collected = gc.collect()
    return collected
