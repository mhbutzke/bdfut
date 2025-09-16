# ============================================
# BDFut Distributed Tracing Module
# ============================================
"""
Módulo de tracing distribuído para o sistema BDFut.
Implementa OpenTelemetry com Jaeger para rastreamento de requisições.
"""

import time
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from contextvars import ContextVar
from enum import Enum
import functools
import asyncio

try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    print("OpenTelemetry não disponível. Instale com: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger-thrift")

# Context variables para tracing
current_span: ContextVar[Optional[Any]] = ContextVar('current_span', default=None)
trace_id: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
span_id: ContextVar[Optional[str]] = ContextVar('span_id', default=None)

class TraceStatus(Enum):
    """Status de spans de trace."""
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

@dataclass
class TraceContext:
    """Contexto de trace distribuído."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    baggage: Dict[str, str] = None
    
    def __post_init__(self):
        if self.baggage is None:
            self.baggage = {}

class BDFutTracer:
    """Tracer principal do sistema BDFut."""
    
    def __init__(self, service_name: str = "bdfut", jaeger_endpoint: str = None):
        self.service_name = service_name
        self.jaeger_endpoint = jaeger_endpoint or "http://localhost:14268/api/traces"
        self.tracer = None
        self._setup_tracing()
    
    def _setup_tracing(self):
        """Configura o sistema de tracing."""
        if not OPENTELEMETRY_AVAILABLE:
            print("OpenTelemetry não disponível. Tracing desabilitado.")
            return
        
        try:
            # Configura resource
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "2.0.0",
                "service.namespace": "bdfut",
                "deployment.environment": "development"
            })
            
            # Configura tracer provider
            trace.set_tracer_provider(TracerProvider(resource=resource))
            
            # Configura Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
                collector_endpoint=self.jaeger_endpoint
            )
            
            # Configura span processor
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            
            # Obtém tracer
            self.tracer = trace.get_tracer(self.service_name)
            
            # Instrumenta bibliotecas
            self._instrument_libraries()
            
            print(f"Tracing configurado para {self.service_name}")
            
        except Exception as e:
            print(f"Erro ao configurar tracing: {e}")
            self.tracer = None
    
    def _instrument_libraries(self):
        """Instrumenta bibliotecas para tracing automático."""
        try:
            # Instrumenta requests
            RequestsInstrumentor().instrument()
            
            # Instrumenta psycopg2
            Psycopg2Instrumentor().instrument()
            
            # Instrumenta Redis
            RedisInstrumentor().instrument()
            
            # Instrumenta SQLAlchemy
            SQLAlchemyInstrumentor().instrument()
            
            print("Bibliotecas instrumentadas para tracing")
            
        except Exception as e:
            print(f"Erro ao instrumentar bibliotecas: {e}")
    
    def start_span(self, name: str, parent: Optional[Any] = None, 
                   attributes: Dict[str, Any] = None) -> Any:
        """Inicia um novo span."""
        if not self.tracer:
            return None
        
        try:
            span = self.tracer.start_span(name, parent=parent)
            
            # Adiciona atributos se fornecidos
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            # Define contexto
            current_span.set(span)
            trace_id.set(span.get_span_context().trace_id)
            span_id.set(span.get_span_context().span_id)
            
            return span
            
        except Exception as e:
            print(f"Erro ao iniciar span: {e}")
            return None
    
    def end_span(self, span: Any, status: TraceStatus = TraceStatus.OK, 
                 error: Exception = None, attributes: Dict[str, Any] = None):
        """Finaliza um span."""
        if not span:
            return
        
        try:
            # Adiciona atributos finais
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            # Define status
            if status == TraceStatus.OK:
                span.set_status(Status(StatusCode.OK))
            else:
                span.set_status(Status(StatusCode.ERROR, str(error) if error else status.value))
            
            # Adiciona informações de erro se disponível
            if error:
                span.record_exception(error)
                span.set_attribute("error.type", type(error).__name__)
                span.set_attribute("error.message", str(error))
            
            # Finaliza span
            span.end()
            
            # Limpa contexto
            current_span.set(None)
            
        except Exception as e:
            print(f"Erro ao finalizar span: {e}")
    
    def add_event(self, span: Any, name: str, attributes: Dict[str, Any] = None):
        """Adiciona evento ao span."""
        if not span:
            return
        
        try:
            span.add_event(name, attributes or {})
        except Exception as e:
            print(f"Erro ao adicionar evento: {e}")
    
    def add_attribute(self, span: Any, key: str, value: Any):
        """Adiciona atributo ao span."""
        if not span:
            return
        
        try:
            span.set_attribute(key, value)
        except Exception as e:
            print(f"Erro ao adicionar atributo: {e}")

# ============================================
# DECORATORS E CONTEXT MANAGERS
# ============================================

def trace_function(name: Optional[str] = None, 
                  attributes: Optional[Dict[str, Any]] = None,
                  include_args: bool = True,
                  include_result: bool = True):
    """Decorator para tracing de funções."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            # Inicia span
            span = tracer.start_span(span_name, attributes=attributes)
            
            try:
                # Adiciona informações da função
                if include_args:
                    span.set_attribute("function.args", str(args))
                    span.set_attribute("function.kwargs", str(kwargs))
                
                # Executa função
                result = func(*args, **kwargs)
                
                # Adiciona resultado se solicitado
                if include_result:
                    span.set_attribute("function.result", str(result))
                
                # Finaliza span com sucesso
                tracer.end_span(span, TraceStatus.OK)
                
                return result
                
            except Exception as e:
                # Finaliza span com erro
                tracer.end_span(span, TraceStatus.ERROR, error=e)
                raise
        
        return wrapper
    return decorator

def trace_async_function(name: Optional[str] = None,
                         attributes: Optional[Dict[str, Any]] = None,
                         include_args: bool = True,
                         include_result: bool = True):
    """Decorator para tracing de funções assíncronas."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            # Inicia span
            span = tracer.start_span(span_name, attributes=attributes)
            
            try:
                # Adiciona informações da função
                if include_args:
                    span.set_attribute("function.args", str(args))
                    span.set_attribute("function.kwargs", str(kwargs))
                
                # Executa função assíncrona
                result = await func(*args, **kwargs)
                
                # Adiciona resultado se solicitado
                if include_result:
                    span.set_attribute("function.result", str(result))
                
                # Finaliza span com sucesso
                tracer.end_span(span, TraceStatus.OK)
                
                return result
                
            except Exception as e:
                # Finaliza span com erro
                tracer.end_span(span, TraceStatus.ERROR, error=e)
                raise
        
        return wrapper
    return decorator

class TraceContext:
    """Context manager para tracing com contexto."""
    
    def __init__(self, name: str, attributes: Optional[Dict[str, Any]] = None,
                 parent: Optional[Any] = None):
        self.name = name
        self.attributes = attributes or {}
        self.parent = parent
        self.span = None
    
    def __enter__(self):
        self.span = tracer.start_span(self.name, parent=self.parent, 
                                     attributes=self.attributes)
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            if exc_type:
                tracer.end_span(self.span, TraceStatus.ERROR, error=exc_val)
            else:
                tracer.end_span(self.span, TraceStatus.OK)

# ============================================
# TRACERS ESPECIALIZADOS
# ============================================

class APITracer:
    """Tracer especializado para APIs."""
    
    def __init__(self):
        self.tracer = BDFutTracer("bdfut-api")
    
    def trace_request(self, method: str, path: str, headers: Dict[str, str] = None,
                     query_params: Dict[str, Any] = None, body: Any = None):
        """Inicia trace de requisição HTTP."""
        span_name = f"{method} {path}"
        attributes = {
            "http.method": method,
            "http.url": path,
            "http.route": path,
            "http.user_agent": headers.get("User-Agent") if headers else None,
            "http.request.query_params": str(query_params) if query_params else None,
            "http.request.body": str(body) if body else None
        }
        
        return self.tracer.start_span(span_name, attributes=attributes)
    
    def trace_response(self, span: Any, status_code: int, response_time: float,
                      response_size: int = None, response_body: Any = None):
        """Finaliza trace de resposta HTTP."""
        if not span:
            return
        
        attributes = {
            "http.status_code": status_code,
            "http.response_time_ms": response_time * 1000,
            "http.response_size_bytes": response_size,
            "http.response.body": str(response_body) if response_body else None
        }
        
        status = TraceStatus.OK if 200 <= status_code < 400 else TraceStatus.ERROR
        self.tracer.end_span(span, status, attributes=attributes)

class ETLTracer:
    """Tracer especializado para ETL."""
    
    def __init__(self):
        self.tracer = BDFutTracer("bdfut-etl")
    
    def trace_job(self, job_name: str, job_type: str, 
                  parameters: Dict[str, Any] = None):
        """Inicia trace de job ETL."""
        span_name = f"ETL Job: {job_name}"
        attributes = {
            "etl.job_name": job_name,
            "etl.job_type": job_type,
            "etl.parameters": str(parameters) if parameters else None
        }
        
        return self.tracer.start_span(span_name, attributes=attributes)
    
    def trace_data_processing(self, span: Any, operation: str, 
                             records_processed: int, records_failed: int = 0):
        """Adiciona evento de processamento de dados."""
        if not span:
            return
        
        attributes = {
            "etl.operation": operation,
            "etl.records_processed": records_processed,
            "etl.records_failed": records_failed
        }
        
        self.tracer.add_event(span, "data_processing", attributes)
    
    def trace_external_api_call(self, span: Any, api_name: str, endpoint: str,
                               response_time: float, status_code: int = None):
        """Adiciona evento de chamada de API externa."""
        if not span:
            return
        
        attributes = {
            "external.api_name": api_name,
            "external.endpoint": endpoint,
            "external.response_time_ms": response_time * 1000,
            "external.status_code": status_code
        }
        
        self.tracer.add_event(span, "external_api_call", attributes)

class DatabaseTracer:
    """Tracer especializado para banco de dados."""
    
    def __init__(self):
        self.tracer = BDFutTracer("bdfut-database")
    
    def trace_query(self, query_type: str, table: str = None, 
                   query: str = None, parameters: Dict[str, Any] = None):
        """Inicia trace de consulta ao banco."""
        span_name = f"DB Query: {query_type}"
        attributes = {
            "db.operation": query_type,
            "db.table": table,
            "db.query": query,
            "db.parameters": str(parameters) if parameters else None
        }
        
        return self.tracer.start_span(span_name, attributes=attributes)
    
    def trace_query_result(self, span: Any, rows_affected: int = None,
                          execution_time: float = None):
        """Finaliza trace de consulta com resultado."""
        if not span:
            return
        
        attributes = {
            "db.rows_affected": rows_affected,
            "db.execution_time_ms": execution_time * 1000 if execution_time else None
        }
        
        self.tracer.end_span(span, TraceStatus.OK, attributes=attributes)

class CacheTracer:
    """Tracer especializado para cache."""
    
    def __init__(self):
        self.tracer = BDFutTracer("bdfut-cache")
    
    def trace_cache_operation(self, operation: str, key: str, 
                             cache_type: str = "redis"):
        """Inicia trace de operação de cache."""
        span_name = f"Cache {operation}: {key}"
        attributes = {
            "cache.operation": operation,
            "cache.key": key,
            "cache.type": cache_type
        }
        
        return self.tracer.start_span(span_name, attributes=attributes)
    
    def trace_cache_result(self, span: Any, hit: bool, response_time: float = None):
        """Finaliza trace de cache com resultado."""
        if not span:
            return
        
        attributes = {
            "cache.hit": hit,
            "cache.response_time_ms": response_time * 1000 if response_time else None
        }
        
        self.tracer.end_span(span, TraceStatus.OK, attributes=attributes)

# ============================================
# INTEGRAÇÃO COM LOGGING
# ============================================

def inject_trace_context_to_logs():
    """Injeta contexto de trace nos logs."""
    from .logging import logger
    
    def log_with_trace(level: str, message: str, **kwargs):
        """Log com contexto de trace."""
        trace_ctx = current_span.get()
        if trace_ctx:
            kwargs.setdefault('data', {})
            kwargs['data']['trace_id'] = trace_id.get()
            kwargs['data']['span_id'] = span_id.get()
        
        getattr(logger, level)(message, **kwargs)
    
    return log_with_trace

# ============================================
# INSTÂNCIAS GLOBAIS
# ============================================

# Tracer principal
tracer = BDFutTracer()

# Tracers especializados
api_tracer = APITracer()
etl_tracer = ETLTracer()
db_tracer = DatabaseTracer()
cache_tracer = CacheTracer()

# ============================================
# CONFIGURAÇÃO DE AMBIENTE
# ============================================

def configure_tracing(environment: str = "development", 
                     jaeger_endpoint: str = None,
                     enable_tracing: bool = True):
    """Configura o sistema de tracing baseado no ambiente."""
    
    if not enable_tracing or not OPENTELEMETRY_AVAILABLE:
        print("Tracing desabilitado")
        return
    
    try:
        # Configura endpoint do Jaeger
        if not jaeger_endpoint:
            if environment == "production":
                jaeger_endpoint = "http://jaeger-collector:14268/api/traces"
            else:
                jaeger_endpoint = "http://localhost:14268/api/traces"
        
        # Reconfigura tracer
        global tracer
        tracer = BDFutTracer("bdfut", jaeger_endpoint)
        
        print(f"Tracing configurado para ambiente {environment}")
        
    except Exception as e:
        print(f"Erro ao configurar tracing: {e}")

# ============================================
# UTILITÁRIOS
# ============================================

def get_current_trace_id() -> Optional[str]:
    """Retorna o ID do trace atual."""
    return trace_id.get()

def get_current_span_id() -> Optional[str]:
    """Retorna o ID do span atual."""
    return span_id.get()

def get_trace_context() -> Optional[TraceContext]:
    """Retorna o contexto de trace atual."""
    current_trace_id = trace_id.get()
    current_span_id = span_id.get()
    
    if current_trace_id and current_span_id:
        return TraceContext(
            trace_id=current_trace_id,
            span_id=current_span_id
        )
    
    return None

def create_trace_link(jaeger_ui_url: str = "http://localhost:16686") -> Optional[str]:
    """Cria link para visualização do trace no Jaeger UI."""
    current_trace_id = trace_id.get()
    
    if current_trace_id:
        return f"{jaeger_ui_url}/trace/{current_trace_id}"
    
    return None
