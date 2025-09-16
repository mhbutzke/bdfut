# ============================================
# BDFut Structured Logging Module
# ============================================
"""
Módulo de logging estruturado para o sistema BDFut.
Implementa logging JSON com contexto, correlação e integração com observabilidade.
"""

import json
import logging
import logging.handlers
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Union
from contextvars import ContextVar
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
import os

# Context variables para correlação
request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
session_id: ContextVar[Optional[str]] = ContextVar('session_id', default=None)
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)

class LogLevel(Enum):
    """Níveis de log padronizados."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(Enum):
    """Categorias de log para organização."""
    SYSTEM = "system"
    API = "api"
    ETL = "etl"
    DATABASE = "database"
    CACHE = "cache"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    AUDIT = "audit"

@dataclass
class LogContext:
    """Contexto de log estruturado."""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    service: str = "bdfut"
    version: str = "2.0.0"
    environment: str = "development"
    hostname: str = ""
    pid: int = 0
    
    def __post_init__(self):
        if not self.hostname:
            self.hostname = os.uname().nodename
        if not self.pid:
            self.pid = os.getpid()

@dataclass
class LogEvent:
    """Evento de log estruturado."""
    timestamp: str
    level: str
    message: str
    category: str
    context: LogContext
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, Any]] = None
    business: Optional[Dict[str, Any]] = None

class StructuredFormatter(logging.Formatter):
    """Formatter para logs estruturados em JSON."""
    
    def __init__(self, include_context: bool = True):
        super().__init__()
        self.include_context = include_context
        self.default_context = LogContext()
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata o log record em JSON estruturado."""
        # Extrai contexto das variáveis de contexto
        context_data = LogContext(
            request_id=request_id.get(),
            user_id=user_id.get(),
            session_id=session_id.get(),
            correlation_id=correlation_id.get(),
            service=self.default_context.service,
            version=self.default_context.version,
            environment=self.default_context.environment,
            hostname=self.default_context.hostname,
            pid=self.default_context.pid
        )
        
        # Prepara dados do evento
        event_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "category": getattr(record, 'category', LogCategory.SYSTEM.value),
            "context": asdict(context_data),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Adiciona dados estruturados se disponíveis
        if hasattr(record, 'data') and record.data:
            event_data["data"] = record.data
        
        # Adiciona informações de erro se disponíveis
        if record.exc_info:
            event_data["error"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Adiciona métricas de performance se disponíveis
        if hasattr(record, 'performance') and record.performance:
            event_data["performance"] = record.performance
        
        # Adiciona dados de negócio se disponíveis
        if hasattr(record, 'business') and record.business:
            event_data["business"] = record.business
        
        # Adiciona campos extras do record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info', 'category', 'data', 'performance', 
                          'business']:
                event_data[key] = value
        
        return json.dumps(event_data, ensure_ascii=False, default=str)

class BDFutLogger:
    """Logger principal do sistema BDFut."""
    
    def __init__(self, name: str = "bdfut"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Configura o logger com handlers e formatters."""
        # Remove handlers existentes
        self.logger.handlers.clear()
        
        # Configura nível
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para console (desenvolvimento)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = StructuredFormatter()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Handler para arquivo (produção)
        file_handler = logging.handlers.RotatingFileHandler(
            'logs/bdfut.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = StructuredFormatter()
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Handler para erros críticos
        error_handler = logging.handlers.RotatingFileHandler(
            'logs/bdfut-error.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = StructuredFormatter()
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)
        
        # Previne propagação para root logger
        self.logger.propagate = False
    
    def _log(self, level: LogLevel, message: str, category: LogCategory = LogCategory.SYSTEM,
             data: Optional[Dict[str, Any]] = None, performance: Optional[Dict[str, Any]] = None,
             business: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """Método interno de logging."""
        extra = {
            'category': category.value,
            'data': data,
            'performance': performance,
            'business': business
        }
        
        log_method = getattr(self.logger, level.value.lower())
        log_method(message, extra=extra, exc_info=exc_info)
    
    def debug(self, message: str, category: LogCategory = LogCategory.SYSTEM,
              data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log de debug."""
        self._log(LogLevel.DEBUG, message, category, data, **kwargs)
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM,
             data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log de informação."""
        self._log(LogLevel.INFO, message, category, data, **kwargs)
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM,
                data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log de aviso."""
        self._log(LogLevel.WARNING, message, category, data, **kwargs)
    
    def error(self, message: str, category: LogCategory = LogCategory.SYSTEM,
              data: Optional[Dict[str, Any]] = None, exc_info: bool = False, **kwargs):
        """Log de erro."""
        self._log(LogLevel.ERROR, message, category, data, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, category: LogCategory = LogCategory.SYSTEM,
                 data: Optional[Dict[str, Any]] = None, exc_info: bool = False, **kwargs):
        """Log crítico."""
        self._log(LogLevel.CRITICAL, message, category, data, exc_info=exc_info, **kwargs)

# ============================================
# DECORATORS E CONTEXT MANAGERS
# ============================================

def log_function_call(category: LogCategory = LogCategory.SYSTEM, 
                     include_args: bool = True, include_result: bool = True):
    """Decorator para logar chamadas de função."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = f"{func.__module__}.{func.__name__}"
            
            # Log de entrada
            logger.info(f"Chamando função {func_name}", 
                       category=category,
                       data={
                           "function": func_name,
                           "args": args if include_args else None,
                           "kwargs": kwargs if include_args else None
                       })
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log de saída
                logger.info(f"Função {func_name} executada com sucesso",
                           category=category,
                           performance={"duration_ms": duration * 1000},
                           data={
                               "function": func_name,
                               "result": result if include_result else None
                           })
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Log de erro
                logger.error(f"Erro na função {func_name}: {str(e)}",
                           category=category,
                           performance={"duration_ms": duration * 1000},
                           data={"function": func_name},
                           exc_info=True)
                raise
        
        return wrapper
    return decorator

class LogContext:
    """Context manager para logging com contexto."""
    
    def __init__(self, request_id: Optional[str] = None, 
                 user_id: Optional[str] = None,
                 session_id: Optional[str] = None,
                 correlation_id: Optional[str] = None):
        self.request_id = request_id or str(uuid.uuid4())
        self.user_id = user_id
        self.session_id = session_id
        self.correlation_id = correlation_id or str(uuid.uuid4())
        
        # Tokens para restaurar contexto
        self._request_token = None
        self._user_token = None
        self._session_token = None
        self._correlation_token = None
    
    def __enter__(self):
        # Define contexto
        self._request_token = request_id.set(self.request_id)
        self._user_token = user_id.set(self.user_id)
        self._session_token = session_id.set(self.session_id)
        self._correlation_token = correlation_id.set(self.correlation_id)
        
        logger.info("Contexto de log iniciado",
                   category=LogCategory.SYSTEM,
                   data={
                       "request_id": self.request_id,
                       "user_id": self.user_id,
                       "session_id": self.session_id,
                       "correlation_id": self.correlation_id
                   })
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restaura contexto anterior
        if self._request_token:
            request_id.reset(self._request_token)
        if self._user_token:
            user_id.reset(self._user_token)
        if self._session_token:
            session_id.reset(self._session_token)
        if self._correlation_token:
            correlation_id.reset(self._correlation_token)
        
        if exc_type:
            logger.error("Contexto de log finalizado com erro",
                        category=LogCategory.SYSTEM,
                        data={
                            "request_id": self.request_id,
                            "error_type": exc_type.__name__,
                            "error_message": str(exc_val)
                        },
                        exc_info=True)
        else:
            logger.info("Contexto de log finalizado com sucesso",
                       category=LogCategory.SYSTEM,
                       data={"request_id": self.request_id})

# ============================================
# LOGGERS ESPECIALIZADOS
# ============================================

class APILogger:
    """Logger especializado para APIs."""
    
    def __init__(self):
        self.logger = BDFutLogger("bdfut.api")
    
    def request_start(self, method: str, path: str, headers: Dict[str, str] = None,
                     query_params: Dict[str, Any] = None, body: Any = None):
        """Log de início de requisição."""
        self.logger.info("Requisição iniciada",
                        category=LogCategory.API,
                        data={
                            "method": method,
                            "path": path,
                            "headers": headers,
                            "query_params": query_params,
                            "body": body
                        })
    
    def request_end(self, method: str, path: str, status_code: int, 
                   response_time: float, response_size: int = None):
        """Log de fim de requisição."""
        self.logger.info("Requisição finalizada",
                        category=LogCategory.API,
                        performance={
                            "response_time_ms": response_time * 1000,
                            "response_size_bytes": response_size
                        },
                        data={
                            "method": method,
                            "path": path,
                            "status_code": status_code
                        })
    
    def request_error(self, method: str, path: str, error: Exception, 
                     response_time: float = None):
        """Log de erro em requisição."""
        self.logger.error("Erro em requisição",
                         category=LogCategory.API,
                         performance={"response_time_ms": response_time * 1000} if response_time else None,
                         data={
                             "method": method,
                             "path": path,
                             "error_type": type(error).__name__
                         },
                         exc_info=True)

class ETLLogger:
    """Logger especializado para ETL."""
    
    def __init__(self):
        self.logger = BDFutLogger("bdfut.etl")
    
    def job_start(self, job_name: str, job_type: str, parameters: Dict[str, Any] = None):
        """Log de início de job ETL."""
        self.logger.info("Job ETL iniciado",
                        category=LogCategory.ETL,
                        data={
                            "job_name": job_name,
                            "job_type": job_type,
                            "parameters": parameters
                        })
    
    def job_progress(self, job_name: str, progress: float, 
                    processed: int, total: int, message: str = None):
        """Log de progresso do job ETL."""
        self.logger.info("Progresso do job ETL",
                        category=LogCategory.ETL,
                        data={
                            "job_name": job_name,
                            "progress_percent": progress,
                            "processed": processed,
                            "total": total,
                            "message": message
                        })
    
    def job_end(self, job_name: str, status: str, duration: float,
               records_processed: int = None, records_failed: int = None):
        """Log de fim de job ETL."""
        self.logger.info("Job ETL finalizado",
                        category=LogCategory.ETL,
                        performance={"duration_ms": duration * 1000},
                        data={
                            "job_name": job_name,
                            "status": status,
                            "records_processed": records_processed,
                            "records_failed": records_failed
                        })
    
    def job_error(self, job_name: str, error: Exception, duration: float = None):
        """Log de erro em job ETL."""
        self.logger.error("Erro em job ETL",
                         category=LogCategory.ETL,
                         performance={"duration_ms": duration * 1000} if duration else None,
                         data={
                             "job_name": job_name,
                             "error_type": type(error).__name__
                         },
                         exc_info=True)

class DatabaseLogger:
    """Logger especializado para banco de dados."""
    
    def __init__(self):
        self.logger = BDFutLogger("bdfut.database")
    
    def query_start(self, query_type: str, table: str = None, 
                   query: str = None, parameters: Dict[str, Any] = None):
        """Log de início de consulta."""
        self.logger.debug("Consulta iniciada",
                         category=LogCategory.DATABASE,
                         data={
                             "query_type": query_type,
                             "table": table,
                             "query": query,
                             "parameters": parameters
                         })
    
    def query_end(self, query_type: str, duration: float, rows_affected: int = None,
                 table: str = None):
        """Log de fim de consulta."""
        self.logger.debug("Consulta finalizada",
                         category=LogCategory.DATABASE,
                         performance={"duration_ms": duration * 1000},
                         data={
                             "query_type": query_type,
                             "rows_affected": rows_affected,
                             "table": table
                         })
    
    def query_error(self, query_type: str, error: Exception, duration: float = None,
                   table: str = None):
        """Log de erro em consulta."""
        self.logger.error("Erro em consulta",
                         category=LogCategory.DATABASE,
                         performance={"duration_ms": duration * 1000} if duration else None,
                         data={
                             "query_type": query_type,
                             "table": table,
                             "error_type": type(error).__name__
                         },
                         exc_info=True)

class SecurityLogger:
    """Logger especializado para segurança."""
    
    def __init__(self):
        self.logger = BDFutLogger("bdfut.security")
    
    def auth_success(self, user_id: str, method: str, ip_address: str = None):
        """Log de autenticação bem-sucedida."""
        self.logger.info("Autenticação bem-sucedida",
                        category=LogCategory.SECURITY,
                        data={
                            "user_id": user_id,
                            "method": method,
                            "ip_address": ip_address
                        })
    
    def auth_failure(self, user_id: str, method: str, reason: str, 
                    ip_address: str = None):
        """Log de falha de autenticação."""
        self.logger.warning("Falha de autenticação",
                           category=LogCategory.SECURITY,
                           data={
                               "user_id": user_id,
                               "method": method,
                               "reason": reason,
                               "ip_address": ip_address
                           })
    
    def access_denied(self, user_id: str, resource: str, action: str, 
                     ip_address: str = None):
        """Log de acesso negado."""
        self.logger.warning("Acesso negado",
                           category=LogCategory.SECURITY,
                           data={
                               "user_id": user_id,
                               "resource": resource,
                               "action": action,
                               "ip_address": ip_address
                           })
    
    def security_event(self, event_type: str, severity: str, details: Dict[str, Any],
                      ip_address: str = None):
        """Log de evento de segurança."""
        level = LogLevel.WARNING if severity == "medium" else LogLevel.ERROR if severity == "high" else LogLevel.INFO
        
        self.logger._log(level, "Evento de segurança",
                        LogCategory.SECURITY,
                        data={
                            "event_type": event_type,
                            "severity": severity,
                            "details": details,
                            "ip_address": ip_address
                        })

# ============================================
# INSTÂNCIAS GLOBAIS
# ============================================

# Logger principal
logger = BDFutLogger()

# Loggers especializados
api_logger = APILogger()
etl_logger = ETLLogger()
db_logger = DatabaseLogger()
security_logger = SecurityLogger()

# ============================================
# CONFIGURAÇÃO DE AMBIENTE
# ============================================

def configure_logging(environment: str = "development", log_level: str = "INFO"):
    """Configura o sistema de logging baseado no ambiente."""
    
    # Cria diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Configura nível de log
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.logger.setLevel(level)
    
    # Configuração específica por ambiente
    if environment == "production":
        # Em produção, remove handler de console
        logger.logger.handlers = [h for h in logger.logger.handlers 
                                 if not isinstance(h, logging.StreamHandler)]
        
        # Adiciona handler para syslog se disponível
        try:
            syslog_handler = logging.handlers.SysLogHandler()
            syslog_handler.setLevel(logging.INFO)
            syslog_formatter = StructuredFormatter()
            syslog_handler.setFormatter(syslog_formatter)
            logger.logger.addHandler(syslog_handler)
        except Exception:
            pass  # Syslog não disponível
    
    logger.info("Sistema de logging configurado",
                category=LogCategory.SYSTEM,
                data={
                    "environment": environment,
                    "log_level": log_level
                })
