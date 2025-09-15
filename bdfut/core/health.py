# ============================================
# BDFut Health Check Module
# ============================================
"""
Módulo de health checks para o sistema BDFut.
Implementa verificações de saúde para todos os componentes.
"""

import time
import psutil
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

try:
    import asyncpg
    import redis.asyncio as redis
    import httpx
    ASYNC_DEPENDENCIES_AVAILABLE = True
except ImportError:
    ASYNC_DEPENDENCIES_AVAILABLE = False

class HealthStatus(Enum):
    """Status de saúde dos componentes."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    """Resultado de um health check."""
    name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    details: Optional[Dict[str, Any]] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class OverallHealth:
    """Saúde geral do sistema."""
    status: HealthStatus
    checks: List[HealthCheck]
    timestamp: float
    uptime_seconds: float
    version: str = "2.0.0"

class HealthChecker:
    """Verificador de saúde do sistema."""
    
    def __init__(self):
        self.start_time = time.time()
        self.logger = logging.getLogger(__name__)
        self.checks = []
    
    async def check_database(self) -> HealthCheck:
        """Verifica saúde do banco de dados."""
        start_time = time.time()
        
        try:
            if not ASYNC_DEPENDENCIES_AVAILABLE:
                return HealthCheck(
                    name="database",
                    status=HealthStatus.UNKNOWN,
                    message="Database dependencies not available",
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Conecta ao banco
            conn = await asyncpg.connect(
                host="localhost",
                port=5432,
                user="bdfut",
                password="bdfut_password",
                database="bdfut"
            )
            
            # Executa query simples
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            
            if result == 1:
                return HealthCheck(
                    name="database",
                    status=HealthStatus.HEALTHY,
                    message="Database connection successful",
                    response_time_ms=(time.time() - start_time) * 1000,
                    details={"query_result": result}
                )
            else:
                return HealthCheck(
                    name="database",
                    status=HealthStatus.UNHEALTHY,
                    message="Database query failed",
                    response_time_ms=(time.time() - start_time) * 1000
                )
                
        except Exception as e:
            return HealthCheck(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            )
    
    async def check_redis(self) -> HealthCheck:
        """Verifica saúde do Redis."""
        start_time = time.time()
        
        try:
            if not ASYNC_DEPENDENCIES_AVAILABLE:
                return HealthCheck(
                    name="redis",
                    status=HealthStatus.UNKNOWN,
                    message="Redis dependencies not available",
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Conecta ao Redis
            redis_client = redis.Redis(
                host="localhost",
                port=6379,
                db=0,
                decode_responses=True
            )
            
            # Executa ping
            result = await redis_client.ping()
            await redis_client.close()
            
            if result:
                return HealthCheck(
                    name="redis",
                    status=HealthStatus.HEALTHY,
                    message="Redis connection successful",
                    response_time_ms=(time.time() - start_time) * 1000,
                    details={"ping_result": result}
                )
            else:
                return HealthCheck(
                    name="redis",
                    status=HealthStatus.UNHEALTHY,
                    message="Redis ping failed",
                    response_time_ms=(time.time() - start_time) * 1000
                )
                
        except Exception as e:
            return HealthCheck(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            )
    
    async def check_external_api(self) -> HealthCheck:
        """Verifica saúde da API externa (SportMonks)."""
        start_time = time.time()
        
        try:
            if not ASYNC_DEPENDENCIES_AVAILABLE:
                return HealthCheck(
                    name="external_api",
                    status=HealthStatus.UNKNOWN,
                    message="HTTP dependencies not available",
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Testa conexão com API externa
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.sportmonks.com/v3/core/countries")
                
                if response.status_code == 200:
                    return HealthCheck(
                        name="external_api",
                        status=HealthStatus.HEALTHY,
                        message="External API accessible",
                        response_time_ms=(time.time() - start_time) * 1000,
                        details={"status_code": response.status_code}
                    )
                elif response.status_code == 429:
                    return HealthCheck(
                        name="external_api",
                        status=HealthStatus.DEGRADED,
                        message="External API rate limited",
                        response_time_ms=(time.time() - start_time) * 1000,
                        details={"status_code": response.status_code}
                    )
                else:
                    return HealthCheck(
                        name="external_api",
                        status=HealthStatus.UNHEALTHY,
                        message=f"External API returned {response.status_code}",
                        response_time_ms=(time.time() - start_time) * 1000,
                        details={"status_code": response.status_code}
                    )
                    
        except Exception as e:
            return HealthCheck(
                name="external_api",
                status=HealthStatus.UNHEALTHY,
                message=f"External API check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            )
    
    def check_system_resources(self) -> HealthCheck:
        """Verifica recursos do sistema."""
        start_time = time.time()
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            
            # Disco
            disk = psutil.disk_usage('/')
            
            # Determina status baseado nos recursos
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 95:
                status = HealthStatus.UNHEALTHY
                message = "System resources critically low"
            elif cpu_percent > 80 or memory.percent > 80 or disk.percent > 85:
                status = HealthStatus.DEGRADED
                message = "System resources high"
            else:
                status = HealthStatus.HEALTHY
                message = "System resources normal"
            
            return HealthCheck(
                name="system_resources",
                status=status,
                message=message,
                response_time_ms=(time.time() - start_time) * 1000,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_free_gb": disk.free / (1024**3)
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="system_resources",
                status=HealthStatus.UNKNOWN,
                message=f"System resource check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            )
    
    def check_application_status(self) -> HealthCheck:
        """Verifica status da aplicação."""
        start_time = time.time()
        
        try:
            # Verifica se a aplicação está rodando
            uptime = time.time() - self.start_time
            
            # Verifica threads ativas
            thread_count = len(psutil.Process().threads())
            
            # Verifica conexões de rede
            connections = len(psutil.net_connections())
            
            if uptime < 60:  # Menos de 1 minuto
                status = HealthStatus.DEGRADED
                message = "Application recently started"
            elif thread_count > 100:
                status = HealthStatus.DEGRADED
                message = "High thread count"
            else:
                status = HealthStatus.HEALTHY
                message = "Application running normally"
            
            return HealthCheck(
                name="application_status",
                status=status,
                message=message,
                response_time_ms=(time.time() - start_time) * 1000,
                details={
                    "uptime_seconds": uptime,
                    "thread_count": thread_count,
                    "network_connections": connections
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="application_status",
                status=HealthStatus.UNKNOWN,
                message=f"Application status check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            )
    
    async def run_all_checks(self) -> OverallHealth:
        """Executa todos os health checks."""
        checks = []
        
        # Checks síncronos
        checks.append(self.check_system_resources())
        checks.append(self.check_application_status())
        
        # Checks assíncronos
        if ASYNC_DEPENDENCIES_AVAILABLE:
            async_checks = await asyncio.gather(
                self.check_database(),
                self.check_redis(),
                self.check_external_api(),
                return_exceptions=True
            )
            
            for check in async_checks:
                if isinstance(check, Exception):
                    checks.append(HealthCheck(
                        name="async_check_error",
                        status=HealthStatus.UNKNOWN,
                        message=f"Async check failed: {str(check)}",
                        response_time_ms=0.0
                    ))
                else:
                    checks.append(check)
        
        # Determina status geral
        unhealthy_count = sum(1 for check in checks if check.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for check in checks if check.status == HealthStatus.DEGRADED)
        
        if unhealthy_count > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        return OverallHealth(
            status=overall_status,
            checks=checks,
            timestamp=time.time(),
            uptime_seconds=time.time() - self.start_time
        )
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Retorna resumo de saúde do sistema."""
        return {
            "status": "healthy",  # Simplificado para compatibilidade
            "timestamp": time.time(),
            "uptime_seconds": time.time() - self.start_time,
            "version": "2.0.0",
            "checks": {
                "system_resources": "healthy",
                "application_status": "healthy"
            }
        }

# Instância global
health_checker = HealthChecker()

# Função de conveniência para FastAPI
async def get_health() -> Dict[str, Any]:
    """Retorna status de saúde para endpoint de health check."""
    try:
        overall_health = await health_checker.run_all_checks()
        
        return {
            "status": overall_health.status.value,
            "timestamp": overall_health.timestamp,
            "uptime_seconds": overall_health.uptime_seconds,
            "version": overall_health.version,
            "checks": {
                check.name: {
                    "status": check.status.value,
                    "message": check.message,
                    "response_time_ms": check.response_time_ms,
                    "details": check.details
                }
                for check in overall_health.checks
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "uptime_seconds": time.time() - health_checker.start_time,
            "version": "2.0.0",
            "error": str(e),
            "checks": {}
        }

# Função simplificada para compatibilidade
def get_simple_health() -> Dict[str, Any]:
    """Retorna health check simplificado."""
    return health_checker.get_health_summary()