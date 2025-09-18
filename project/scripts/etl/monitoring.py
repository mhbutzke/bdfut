#!/usr/bin/env python3
"""
Sistema de Monitoramento e Logs para ETL Sportmonks
==================================================

Este módulo implementa monitoramento avançado, logging estruturado e
métricas de performance para o sistema ETL.

Autor: ETL Engineer
Data: 17 de Janeiro de 2025
Task: 2.4 - Implementar Monitoramento e Logs
"""

import os
import json
import uuid
import time
import logging
import psycopg2
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)

@dataclass
class ETLExecution:
    """Dados de uma execução ETL"""
    execution_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str = 'RUNNING'
    total_fixtures: int = 0
    processed_fixtures: int = 0
    successful_fixtures: int = 0
    failed_fixtures: int = 0
    total_chunks: int = 0
    processed_chunks: int = 0
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    config: Optional[Dict] = None

@dataclass
class ETLHealthStatus:
    """Status de saúde do sistema ETL"""
    total_executions: int
    running_executions: int
    completed_executions: int
    failed_executions: int
    avg_duration_seconds: Optional[float]
    avg_success_rate: Optional[float]
    last_execution_at: Optional[datetime]
    total_logs_24h: int
    error_logs_24h: int

class ETLMonitor:
    """Monitor principal do sistema ETL"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
        self._lock = threading.Lock()
    
    def connect(self):
        """Conecta ao banco de dados"""
        try:
            self.connection = psycopg2.connect(self.connection_string)
            logger.info("Conectado ao banco de dados para monitoramento")
        except psycopg2.Error as e:
            logger.error(f"Erro ao conectar ao banco: {e}")
            raise
    
    def disconnect(self):
        """Desconecta do banco de dados"""
        if self.connection:
            self.connection.close()
            logger.info("Desconectado do banco de dados")
    
    def start_execution(self, execution_id: str = None, config: Dict = None) -> str:
        """
        Inicia uma nova execução ETL
        
        Args:
            execution_id: ID da execução (opcional, será gerado se não fornecido)
            config: Configuração da execução
        
        Returns:
            ID da execução
        """
        if execution_id is None:
            execution_id = f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT start_etl_execution(%s, %s)",
                (execution_id, json.dumps(config) if config else None)
            )
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Execução ETL iniciada: {execution_id}")
            return execution_id
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao iniciar execução ETL: {e}")
            raise
    
    def finish_execution(self, execution_id: str, status: str, 
                        total_fixtures: int = 0, processed_fixtures: int = 0,
                        successful_fixtures: int = 0, failed_fixtures: int = 0,
                        total_chunks: int = 0, processed_chunks: int = 0,
                        error_message: str = None):
        """
        Finaliza uma execução ETL
        
        Args:
            execution_id: ID da execução
            status: Status final ('COMPLETED', 'FAILED', 'CANCELLED')
            total_fixtures: Total de fixtures encontradas
            processed_fixtures: Fixtures processadas
            successful_fixtures: Fixtures processadas com sucesso
            failed_fixtures: Fixtures que falharam
            total_chunks: Total de chunks encontrados
            processed_chunks: Chunks processados
            error_message: Mensagem de erro (se houver)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT finish_etl_execution(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (execution_id, status, total_fixtures, processed_fixtures,
                 successful_fixtures, failed_fixtures, total_chunks, 
                 processed_chunks, error_message)
            )
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Execução ETL finalizada: {execution_id} - Status: {status}")
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao finalizar execução ETL: {e}")
            raise
    
    def log_event(self, level: str, component: str, message: str,
                  details: Dict = None, execution_id: str = None,
                  chunk_id: str = None, fixture_id: int = None,
                  duration_ms: int = None):
        """
        Registra um evento no log estruturado
        
        Args:
            level: Nível do log ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
            component: Componente que gerou o evento
            message: Mensagem do evento
            details: Detalhes adicionais (JSON)
            execution_id: ID da execução
            chunk_id: ID do chunk
            fixture_id: ID da fixture
            duration_ms: Duração em milissegundos
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT log_etl_event(%s, %s, %s, %s, %s, %s, %s, %s)",
                (level, component, message, 
                 json.dumps(details) if details else None,
                 execution_id, chunk_id, fixture_id, duration_ms)
            )
            self.connection.commit()
            cursor.close()
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao registrar evento: {e}")
            # Não levanta exceção para não interromper o processamento
    
    def record_metric(self, execution_id: str, metric_name: str, 
                     metric_value: float, metric_unit: str = None,
                     tags: Dict = None):
        """
        Registra uma métrica de performance
        
        Args:
            execution_id: ID da execução
            metric_name: Nome da métrica
            metric_value: Valor da métrica
            metric_unit: Unidade da métrica
            tags: Tags adicionais
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT record_etl_metric(%s, %s, %s, %s, %s)",
                (execution_id, metric_name, metric_value, metric_unit,
                 json.dumps(tags) if tags else None)
            )
            self.connection.commit()
            cursor.close()
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao registrar métrica: {e}")
    
    def get_execution_summary(self, execution_id: str) -> Optional[ETLExecution]:
        """Obtém resumo de uma execução ETL"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM get_etl_execution_summary(%s)", (execution_id,))
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return ETLExecution(
                    execution_id=row[0],
                    status=row[1],
                    started_at=row[2],
                    finished_at=row[3],
                    duration_seconds=row[4],
                    total_fixtures=row[5],
                    processed_fixtures=row[6],
                    successful_fixtures=row[7],
                    failed_fixtures=row[8],
                    total_chunks=row[11],
                    processed_chunks=row[12],
                    error_message=row[14]
                )
            return None
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao obter resumo da execução: {e}")
            return None
    
    def get_health_status(self) -> ETLHealthStatus:
        """Obtém status de saúde do sistema ETL"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM get_etl_health_status()")
            row = cursor.fetchone()
            cursor.close()
            
            return ETLHealthStatus(
                total_executions=row[0],
                running_executions=row[1],
                completed_executions=row[2],
                failed_executions=row[3],
                avg_duration_seconds=row[4],
                avg_success_rate=row[5],
                last_execution_at=row[6],
                total_logs_24h=row[7],
                error_logs_24h=row[8]
            )
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao obter status de saúde: {e}")
            return ETLHealthStatus(0, 0, 0, 0, None, None, None, 0, 0)

class ETLLogger:
    """Logger estruturado para ETL"""
    
    def __init__(self, monitor: ETLMonitor, execution_id: str = None):
        self.monitor = monitor
        self.execution_id = execution_id
        self._lock = threading.Lock()
    
    def debug(self, component: str, message: str, **kwargs):
        """Log de debug"""
        self._log('DEBUG', component, message, **kwargs)
    
    def info(self, component: str, message: str, **kwargs):
        """Log de informação"""
        self._log('INFO', component, message, **kwargs)
    
    def warning(self, component: str, message: str, **kwargs):
        """Log de aviso"""
        self._log('WARNING', component, message, **kwargs)
    
    def error(self, component: str, message: str, **kwargs):
        """Log de erro"""
        self._log('ERROR', component, message, **kwargs)
    
    def critical(self, component: str, message: str, **kwargs):
        """Log crítico"""
        self._log('CRITICAL', component, message, **kwargs)
    
    def _log(self, level: str, component: str, message: str, **kwargs):
        """Método interno de logging"""
        with self._lock:
            self.monitor.log_event(
                level=level,
                component=component,
                message=message,
                details=kwargs if kwargs else None,
                execution_id=self.execution_id,
                chunk_id=kwargs.get('chunk_id'),
                fixture_id=kwargs.get('fixture_id'),
                duration_ms=kwargs.get('duration_ms')
            )

class PerformanceTracker:
    """Rastreador de performance para componentes ETL"""
    
    def __init__(self, monitor: ETLMonitor, execution_id: str):
        self.monitor = monitor
        self.execution_id = execution_id
        self._metrics = {}
    
    @contextmanager
    def track_operation(self, operation_name: str, tags: Dict = None):
        """Context manager para rastrear operações"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_metric(
                f"{operation_name}_duration",
                duration,
                "seconds",
                tags
            )
    
    def record_metric(self, metric_name: str, value: float, 
                     unit: str = None, tags: Dict = None):
        """Registra métrica de performance"""
        self.monitor.record_metric(
            self.execution_id, metric_name, value, unit, tags
        )
    
    def increment_counter(self, counter_name: str, value: int = 1, tags: Dict = None):
        """Incrementa contador"""
        if counter_name not in self._metrics:
            self._metrics[counter_name] = 0
        self._metrics[counter_name] += value
        
        self.record_metric(f"{counter_name}_total", self._metrics[counter_name], "count", tags)
    
    def set_gauge(self, gauge_name: str, value: float, tags: Dict = None):
        """Define valor de gauge"""
        self._metrics[gauge_name] = value
        self.record_metric(f"{gauge_name}_current", value, "gauge", tags)

class ETLAlertManager:
    """Gerenciador de alertas para ETL"""
    
    def __init__(self, monitor: ETLMonitor):
        self.monitor = monitor
        self.alert_thresholds = {
            'error_rate': 0.05,  # 5% de taxa de erro
            'duration_minutes': 60,  # 60 minutos de duração
            'success_rate': 0.90,  # 90% de taxa de sucesso
            'consecutive_failures': 3  # 3 falhas consecutivas
        }
    
    def check_execution_alerts(self, execution_id: str) -> List[str]:
        """
        Verifica alertas para uma execução específica
        
        Returns:
            Lista de alertas encontrados
        """
        alerts = []
        
        try:
            summary = self.monitor.get_execution_summary(execution_id)
            if not summary:
                return alerts
            
            # Verifica taxa de sucesso
            if summary.processed_fixtures > 0:
                success_rate = summary.successful_fixtures / summary.processed_fixtures
                if success_rate < self.alert_thresholds['success_rate']:
                    alerts.append(f"Taxa de sucesso baixa: {success_rate:.2%}")
            
            # Verifica duração
            if summary.duration_seconds:
                duration_minutes = summary.duration_seconds / 60
                if duration_minutes > self.alert_thresholds['duration_minutes']:
                    alerts.append(f"Execução muito longa: {duration_minutes:.1f} minutos")
            
            # Verifica status de falha
            if summary.status == 'FAILED':
                alerts.append(f"Execução falhou: {summary.error_message}")
            
        except Exception as e:
            alerts.append(f"Erro ao verificar alertas: {e}")
        
        return alerts
    
    def check_system_alerts(self) -> List[str]:
        """
        Verifica alertas do sistema geral
        
        Returns:
            Lista de alertas encontrados
        """
        alerts = []
        
        try:
            health = self.monitor.get_health_status()
            
            # Verifica execuções em execução há muito tempo
            if health.running_executions > 0:
                alerts.append(f"{health.running_executions} execuções ainda em execução")
            
            # Verifica taxa de erro geral
            if health.total_executions > 0:
                failure_rate = health.failed_executions / health.total_executions
                if failure_rate > self.alert_thresholds['error_rate']:
                    alerts.append(f"Taxa de falha alta: {failure_rate:.2%}")
            
            # Verifica logs de erro recentes
            if health.error_logs_24h > 10:  # Mais de 10 erros nas últimas 24h
                alerts.append(f"Muitos erros nas últimas 24h: {health.error_logs_24h}")
            
        except Exception as e:
            alerts.append(f"Erro ao verificar alertas do sistema: {e}")
        
        return alerts

def create_monitoring_setup(connection_string: str) -> tuple:
    """
    Cria setup completo de monitoramento
    
    Returns:
        Tupla com (monitor, logger, tracker, alert_manager)
    """
    monitor = ETLMonitor(connection_string)
    monitor.connect()
    
    execution_id = monitor.start_execution()
    
    logger = ETLLogger(monitor, execution_id)
    tracker = PerformanceTracker(monitor, execution_id)
    alert_manager = ETLAlertManager(monitor)
    
    return monitor, logger, tracker, alert_manager
