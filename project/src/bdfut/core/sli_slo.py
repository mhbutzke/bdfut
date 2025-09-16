# ============================================
# BDFut SLI/SLO Module
# ============================================
"""
Módulo de SLIs (Service Level Indicators) e SLOs (Service Level Objectives)
para o sistema BDFut. Define métricas de qualidade de serviço e objetivos.
"""

import time
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import statistics
import threading
from datetime import datetime, timedelta

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

class SLIType(Enum):
    """Tipos de SLI."""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    DATA_FRESHNESS = "data_freshness"
    DATA_COMPLETENESS = "data_completeness"

class SLOStatus(Enum):
    """Status do SLO."""
    HEALTHY = "healthy"
    WARNING = "warning"
    BREACHED = "breached"
    UNKNOWN = "unknown"

@dataclass
class SLI:
    """Service Level Indicator."""
    name: str
    description: str
    sli_type: SLIType
    measurement_window: int  # em segundos
    success_criteria: str
    prometheus_query: Optional[str] = None

@dataclass
class SLO:
    """Service Level Objective."""
    name: str
    description: str
    sli: SLI
    target_percentage: float  # 0-100
    warning_threshold: float  # 0-100
    measurement_window: int  # em segundos
    burn_rate_threshold: float = 1.0  # taxa de queima

@dataclass
class SLIMeasurement:
    """Medição de SLI."""
    sli_name: str
    timestamp: float
    value: float
    success_count: int
    total_count: int
    window_start: float
    window_end: float

@dataclass
class SLOStatus:
    """Status atual do SLO."""
    slo_name: str
    current_percentage: float
    target_percentage: float
    status: SLOStatus
    measurement_window: int
    burn_rate: float
    last_updated: float
    breach_duration: float = 0.0

class SLICalculator:
    """Calculadora de SLIs."""
    
    def __init__(self):
        self.measurements = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.Lock()
    
    def record_measurement(self, sli_name: str, success: bool, value: float = None):
        """Registra uma medição de SLI."""
        with self.lock:
            measurement = {
                'timestamp': time.time(),
                'success': success,
                'value': value
            }
            self.measurements[sli_name].append(measurement)
    
    def calculate_sli(self, sli: SLI) -> SLIMeasurement:
        """Calcula valor atual do SLI."""
        with self.lock:
            measurements = self.measurements[sli.name]
            
            if not measurements:
                return SLIMeasurement(
                    sli_name=sli.name,
                    timestamp=time.time(),
                    value=0.0,
                    success_count=0,
                    total_count=0,
                    window_start=time.time(),
                    window_end=time.time()
                )
            
            # Filtra medições dentro da janela
            window_start = time.time() - sli.measurement_window
            window_measurements = [
                m for m in measurements 
                if m['timestamp'] >= window_start
            ]
            
            if not window_measurements:
                return SLIMeasurement(
                    sli_name=sli.name,
                    timestamp=time.time(),
                    value=0.0,
                    success_count=0,
                    total_count=0,
                    window_start=window_start,
                    window_end=time.time()
                )
            
            # Calcula SLI baseado no tipo
            if sli.sli_type == SLIType.AVAILABILITY:
                success_count = sum(1 for m in window_measurements if m['success'])
                total_count = len(window_measurements)
                value = (success_count / total_count * 100) if total_count > 0 else 0.0
                
            elif sli.sli_type == SLIType.LATENCY:
                values = [m['value'] for m in window_measurements if m['value'] is not None]
                if values:
                    value = statistics.median(values)  # P50
                else:
                    value = 0.0
                success_count = len(values)
                total_count = len(window_measurements)
                
            elif sli.sli_type == SLIType.THROUGHPUT:
                # Requisições por segundo
                time_span = window_measurements[-1]['timestamp'] - window_measurements[0]['timestamp']
                value = len(window_measurements) / time_span if time_span > 0 else 0.0
                success_count = len(window_measurements)
                total_count = len(window_measurements)
                
            elif sli.sli_type == SLIType.ERROR_RATE:
                error_count = sum(1 for m in window_measurements if not m['success'])
                total_count = len(window_measurements)
                value = (error_count / total_count * 100) if total_count > 0 else 0.0
                success_count = total_count - error_count
                
            else:
                value = 0.0
                success_count = 0
                total_count = 0
            
            return SLIMeasurement(
                sli_name=sli.name,
                timestamp=time.time(),
                value=value,
                success_count=success_count,
                total_count=total_count,
                window_start=window_start,
                window_end=time.time()
            )

class SLOManager:
    """Gerenciador de SLOs."""
    
    def __init__(self):
        self.slos: Dict[str, SLO] = {}
        self.sli_calculator = SLICalculator()
        self.slo_statuses: Dict[str, SLOStatus] = {}
        self.breach_start_times: Dict[str, float] = {}
        
        # Métricas Prometheus
        if PROMETHEUS_AVAILABLE:
            self.slo_status_gauge = Gauge(
                'bdfut_slo_status_percentage',
                'SLO status percentage',
                ['slo_name']
            )
            
            self.slo_breach_duration_gauge = Gauge(
                'bdfut_slo_breach_duration_seconds',
                'SLO breach duration in seconds',
                ['slo_name']
            )
        
        # Define SLIs padrão
        self._define_default_slis()
        self._define_default_slos()
    
    def _define_default_slis(self):
        """Define SLIs padrão do sistema."""
        self.slis = {
            'api_availability': SLI(
                name='api_availability',
                description='Disponibilidade da API',
                sli_type=SLIType.AVAILABILITY,
                measurement_window=300,  # 5 minutos
                success_criteria='HTTP 2xx responses',
                prometheus_query='rate(bdfut_api_requests_total{status_code=~"2.."}[5m]) / rate(bdfut_api_requests_total[5m]) * 100'
            ),
            
            'api_latency_p95': SLI(
                name='api_latency_p95',
                description='Latência P95 da API',
                sli_type=SLIType.LATENCY,
                measurement_window=300,  # 5 minutos
                success_criteria='P95 response time < 2s',
                prometheus_query='histogram_quantile(0.95, rate(bdfut_api_request_duration_seconds_bucket[5m]))'
            ),
            
            'api_throughput': SLI(
                name='api_throughput',
                description='Throughput da API',
                sli_type=SLIType.THROUGHPUT,
                measurement_window=300,  # 5 minutos
                success_criteria='Requests per second',
                prometheus_query='rate(bdfut_api_requests_total[5m])'
            ),
            
            'api_error_rate': SLI(
                name='api_error_rate',
                description='Taxa de erro da API',
                sli_type=SLIType.ERROR_RATE,
                measurement_window=300,  # 5 minutos
                success_criteria='Error rate < 1%',
                prometheus_query='rate(bdfut_api_requests_total{status_code=~"5.."}[5m]) / rate(bdfut_api_requests_total[5m]) * 100'
            ),
            
            'etl_job_success_rate': SLI(
                name='etl_job_success_rate',
                description='Taxa de sucesso dos jobs ETL',
                sli_type=SLIType.AVAILABILITY,
                measurement_window=3600,  # 1 hora
                success_criteria='ETL jobs completed successfully',
                prometheus_query='rate(bdfut_etl_jobs_total{status="success"}[1h]) / rate(bdfut_etl_jobs_total[1h]) * 100'
            ),
            
            'data_freshness': SLI(
                name='data_freshness',
                description='Frescor dos dados',
                sli_type=SLIType.DATA_FRESHNESS,
                measurement_window=3600,  # 1 hora
                success_criteria='Data updated within 1 hour',
                prometheus_query='time() - max(bdfut_data_last_updated_timestamp)'
            ),
            
            'database_availability': SLI(
                name='database_availability',
                description='Disponibilidade do banco de dados',
                sli_type=SLIType.AVAILABILITY,
                measurement_window=300,  # 5 minutos
                success_criteria='Database queries successful',
                prometheus_query='rate(bdfut_database_queries_total{status="success"}[5m]) / rate(bdfut_database_queries_total[5m]) * 100'
            )
        }
    
    def _define_default_slos(self):
        """Define SLOs padrão do sistema."""
        # API Availability SLO
        self.add_slo(SLO(
            name='api_availability_slo',
            description='API deve estar disponível 99.9% do tempo',
            sli=self.slis['api_availability'],
            target_percentage=99.9,
            warning_threshold=99.5,
            measurement_window=86400,  # 24 horas
            burn_rate_threshold=2.0
        ))
        
        # API Latency SLO
        self.add_slo(SLO(
            name='api_latency_slo',
            description='95% das requisições devem responder em menos de 2 segundos',
            sli=self.slis['api_latency_p95'],
            target_percentage=95.0,
            warning_threshold=90.0,
            measurement_window=86400,  # 24 horas
            burn_rate_threshold=2.0
        ))
        
        # API Error Rate SLO
        self.add_slo(SLO(
            name='api_error_rate_slo',
            description='Taxa de erro deve ser menor que 0.1%',
            sli=self.slis['api_error_rate'],
            target_percentage=99.9,  # 0.1% de erro = 99.9% de sucesso
            warning_threshold=99.5,
            measurement_window=86400,  # 24 horas
            burn_rate_threshold=2.0
        ))
        
        # ETL Job Success SLO
        self.add_slo(SLO(
            name='etl_job_success_slo',
            description='Jobs ETL devem ter 99% de taxa de sucesso',
            sli=self.slis['etl_job_success_rate'],
            target_percentage=99.0,
            warning_threshold=95.0,
            measurement_window=86400,  # 24 horas
            burn_rate_threshold=2.0
        ))
        
        # Data Freshness SLO
        self.add_slo(SLO(
            name='data_freshness_slo',
            description='Dados devem estar atualizados em menos de 1 hora',
            sli=self.slis['data_freshness'],
            target_percentage=95.0,  # 95% dos dados frescos
            warning_threshold=90.0,
            measurement_window=86400,  # 24 horas
            burn_rate_threshold=2.0
        ))
        
        # Database Availability SLO
        self.add_slo(SLO(
            name='database_availability_slo',
            description='Banco de dados deve estar disponível 99.95% do tempo',
            sli=self.slis['database_availability'],
            target_percentage=99.95,
            warning_threshold=99.9,
            measurement_window=86400,  # 24 horas
            burn_rate_threshold=2.0
        ))
    
    def add_slo(self, slo: SLO):
        """Adiciona um SLO."""
        self.slos[slo.name] = slo
        self.slo_statuses[slo.name] = SLOStatus(
            slo_name=slo.name,
            current_percentage=0.0,
            target_percentage=slo.target_percentage,
            status=SLOStatus.UNKNOWN,
            measurement_window=slo.measurement_window,
            burn_rate=0.0,
            last_updated=time.time()
        )
    
    def record_api_request(self, success: bool, response_time: float = None):
        """Registra requisição da API."""
        self.sli_calculator.record_measurement('api_availability', success, response_time)
        if response_time is not None:
            self.sli_calculator.record_measurement('api_latency_p95', success, response_time)
        self.sli_calculator.record_measurement('api_throughput', success)
        self.sli_calculator.record_measurement('api_error_rate', success)
    
    def record_etl_job(self, success: bool):
        """Registra job ETL."""
        self.sli_calculator.record_measurement('etl_job_success_rate', success)
    
    def record_database_query(self, success: bool):
        """Registra consulta ao banco."""
        self.sli_calculator.record_measurement('database_availability', success)
    
    def record_data_update(self, timestamp: float):
        """Registra atualização de dados."""
        freshness = time.time() - timestamp
        self.sli_calculator.record_measurement('data_freshness', freshness < 3600, freshness)
    
    def evaluate_slos(self) -> Dict[str, SLOStatus]:
        """Avalia todos os SLOs."""
        for slo_name, slo in self.slos.items():
            self._evaluate_slo(slo)
        
        return self.slo_statuses.copy()
    
    def _evaluate_slo(self, slo: SLO):
        """Avalia um SLO específico."""
        # Calcula SLI
        sli_measurement = self.sli_calculator.calculate_sli(slo.sli)
        
        # Determina status baseado no tipo de SLI
        if slo.sli.sli_type in [SLIType.AVAILABILITY, SLIType.ERROR_RATE]:
            # Para disponibilidade e taxa de erro, valor já é percentual
            current_percentage = sli_measurement.value
        else:
            # Para latência e throughput, precisa converter
            if slo.sli.sli_type == SLIType.LATENCY:
                # Latência: sucesso se < threshold
                threshold = 2.0  # 2 segundos
                success_rate = (sli_measurement.success_count / sli_measurement.total_count * 100) if sli_measurement.total_count > 0 else 0.0
                current_percentage = success_rate
            else:
                current_percentage = sli_measurement.value
        
        # Calcula burn rate (taxa de queima do SLO)
        burn_rate = self._calculate_burn_rate(slo, current_percentage)
        
        # Determina status
        if current_percentage >= slo.target_percentage:
            status = SLOStatus.HEALTHY
            if slo_name in self.breach_start_times:
                del self.breach_start_times[slo_name]
        elif current_percentage >= slo.warning_threshold:
            status = SLOStatus.WARNING
            if slo_name in self.breach_start_times:
                del self.breach_start_times[slo_name]
        else:
            status = SLOStatus.BREACHED
            if slo_name not in self.breach_start_times:
                self.breach_start_times[slo_name] = time.time()
        
        # Calcula duração da violação
        breach_duration = 0.0
        if slo_name in self.breach_start_times:
            breach_duration = time.time() - self.breach_start_times[slo_name]
        
        # Atualiza status
        self.slo_statuses[slo_name] = SLOStatus(
            slo_name=slo_name,
            current_percentage=current_percentage,
            target_percentage=slo.target_percentage,
            status=status,
            measurement_window=slo.measurement_window,
            burn_rate=burn_rate,
            last_updated=time.time(),
            breach_duration=breach_duration
        )
        
        # Atualiza métricas Prometheus
        if PROMETHEUS_AVAILABLE:
            self.slo_status_gauge.labels(slo_name=slo_name).set(current_percentage)
            self.slo_breach_duration_gauge.labels(slo_name=slo_name).set(breach_duration)
    
    def _calculate_burn_rate(self, slo: SLO, current_percentage: float) -> float:
        """Calcula taxa de queima do SLO."""
        # Burn rate = (target - current) / target
        if slo.target_percentage > 0:
            return (slo.target_percentage - current_percentage) / slo.target_percentage
        return 0.0
    
    def get_slo_status(self, slo_name: str) -> Optional[SLOStatus]:
        """Retorna status de um SLO específico."""
        return self.slo_statuses.get(slo_name)
    
    def get_all_slo_statuses(self) -> Dict[str, SLOStatus]:
        """Retorna status de todos os SLOs."""
        return self.slo_statuses.copy()
    
    def get_breached_slos(self) -> List[SLOStatus]:
        """Retorna SLOs violados."""
        return [
            status for status in self.slo_statuses.values()
            if status.status == SLOStatus.BREACHED
        ]
    
    def get_warning_slos(self) -> List[SLOStatus]:
        """Retorna SLOs em warning."""
        return [
            status for status in self.slo_statuses.values()
            if status.status == SLOStatus.WARNING
        ]
    
    def generate_slo_report(self) -> Dict[str, Any]:
        """Gera relatório de SLOs."""
        self.evaluate_slos()
        
        total_slos = len(self.slos)
        healthy_slos = len([s for s in self.slo_statuses.values() if s.status == SLOStatus.HEALTHY])
        warning_slos = len([s for s in self.slo_statuses.values() if s.status == SLOStatus.WARNING])
        breached_slos = len([s for s in self.slo_statuses.values() if s.status == SLOStatus.BREACHED])
        
        return {
            "summary": {
                "total_slos": total_slos,
                "healthy": healthy_slos,
                "warning": warning_slos,
                "breached": breached_slos,
                "health_percentage": (healthy_slos / total_slos * 100) if total_slos > 0 else 0.0
            },
            "slo_details": {
                name: asdict(status) for name, status in self.slo_statuses.items()
            },
            "breached_slos": [asdict(s) for s in self.get_breached_slos()],
            "warning_slos": [asdict(s) for s in self.get_warning_slos()],
            "generated_at": datetime.utcnow().isoformat()
        }

# ============================================
# DECORATORS PARA SLI/SLO
# ============================================

def track_sli(sli_name: str):
    """Decorator para rastrear SLI."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                response_time = time.time() - start_time
                slo_manager.sli_calculator.record_measurement(sli_name, success, response_time)
        
        return wrapper
    return decorator

def track_slo(slo_name: str):
    """Decorator para rastrear SLO."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                response_time = time.time() - start_time
                
                # Registra para SLIs relacionados
                if 'api' in slo_name.lower():
                    slo_manager.record_api_request(success, response_time)
                elif 'etl' in slo_name.lower():
                    slo_manager.record_etl_job(success)
                elif 'database' in slo_name.lower():
                    slo_manager.record_database_query(success)
        
        return wrapper
    return decorator

# ============================================
# INSTÂNCIA GLOBAL
# ============================================

# Gerenciador de SLOs
slo_manager = SLOManager()

# ============================================
# CONFIGURAÇÃO DE AMBIENTE
# ============================================

def configure_sli_slo(environment: str = "development"):
    """Configura SLIs/SLOs baseado no ambiente."""
    
    # Ajusta thresholds baseado no ambiente
    if environment == "production":
        # Em produção, thresholds mais rigorosos
        for slo_name, slo in slo_manager.slos.items():
            if 'availability' in slo_name:
                slo.target_percentage = 99.95
                slo.warning_threshold = 99.9
            elif 'latency' in slo_name:
                slo.target_percentage = 98.0  # 98% das requisições < 2s
                slo.warning_threshold = 95.0
            elif 'error_rate' in slo_name:
                slo.target_percentage = 99.95  # 0.05% de erro
                slo.warning_threshold = 99.9
    
    print(f"SLIs/SLOs configurados para ambiente {environment}")

# ============================================
# UTILITÁRIOS
# ============================================

def get_slo_dashboard_data() -> Dict[str, Any]:
    """Retorna dados para dashboard de SLOs."""
    return slo_manager.generate_slo_report()

def get_slo_alerts() -> List[Dict[str, Any]]:
    """Retorna alertas de SLO."""
    breached_slos = slo_manager.get_breached_slos()
    warning_slos = slo_manager.get_warning_slos()
    
    alerts = []
    
    for slo in breached_slos:
        alerts.append({
            "severity": "critical",
            "slo_name": slo.slo_name,
            "message": f"SLO {slo.slo_name} violado: {slo.current_percentage:.2f}% (target: {slo.target_percentage:.2f}%)",
            "breach_duration": slo.breach_duration,
            "burn_rate": slo.burn_rate
        })
    
    for slo in warning_slos:
        alerts.append({
            "severity": "warning",
            "slo_name": slo.slo_name,
            "message": f"SLO {slo.slo_name} em warning: {slo.current_percentage:.2f}% (target: {slo.target_percentage:.2f}%)",
            "breach_duration": 0.0,
            "burn_rate": slo.burn_rate
        })
    
    return alerts
