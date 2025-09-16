"""
Módulo para gerenciamento de metadados ETL
=========================================

Gerencia jobs, checkpoints e logs de execução ETL
"""
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from uuid import UUID, uuid4
from supabase import create_client

from ..config.config import Config

logger = logging.getLogger(__name__)


class ETLMetadataManager:
    """Gerenciador de metadados ETL"""
    
    def __init__(self):
        """Inicializa o gerenciador de metadados"""
        try:
            self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            logger.info("✅ ETL Metadata Manager inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar ETL Metadata Manager: {e}")
            self.supabase = None
    
    def start_job(self, 
                  job_name: str,
                  job_type: str,
                  script_path: Optional[str] = None,
                  input_parameters: Optional[Dict] = None,
                  depends_on_jobs: Optional[List[str]] = None,
                  parent_job_id: Optional[str] = None) -> Optional[str]:
        """
        Inicia um novo job ETL
        
        Args:
            job_name: Nome do job
            job_type: Tipo do job (setup, base_data, etc.)
            script_path: Caminho do script
            input_parameters: Parâmetros de entrada
            depends_on_jobs: Lista de IDs de jobs dependentes
            parent_job_id: ID do job pai
            
        Returns:
            UUID do job criado ou None se erro
        """
        if not self.supabase:
            logger.warning("⚠️ Supabase não disponível - job não será rastreado")
            return None
        
        try:
            job_data = {
                'job_name': job_name,
                'job_type': job_type,
                'script_path': script_path,
                'status': 'running',
                'started_at': datetime.now().isoformat(),
                'input_parameters': input_parameters or {},
                'depends_on_jobs': depends_on_jobs or [],
                'parent_job_id': parent_job_id,
                'created_by': 'etl_process',
                'environment': getattr(Config, 'ENVIRONMENT', 'development')
            }
            
            result = self.supabase.table('etl_jobs').insert(job_data).execute()
            
            if result.data:
                job_id = result.data[0]['id']
                logger.info(f"🚀 Job iniciado: {job_name} (ID: {job_id})")
                return job_id
            else:
                logger.error(f"❌ Erro ao criar job: {job_name}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar job {job_name}: {e}")
            return None
    
    def complete_job(self,
                    job_id: str,
                    status: str = 'completed',
                    output_summary: Optional[Dict] = None,
                    error_message: Optional[str] = None,
                    error_details: Optional[Dict] = None,
                    api_requests: int = 0,
                    records_processed: int = 0,
                    records_inserted: int = 0,
                    records_updated: int = 0,
                    records_failed: int = 0) -> bool:
        """
        Finaliza um job ETL
        
        Args:
            job_id: ID do job
            status: Status final (completed, failed, cancelled)
            output_summary: Resumo dos resultados
            error_message: Mensagem de erro
            error_details: Detalhes do erro
            api_requests: Número de requisições à API
            records_processed: Registros processados
            records_inserted: Registros inseridos
            records_updated: Registros atualizados
            records_failed: Registros com erro
            
        Returns:
            True se sucesso, False se erro
        """
        if not self.supabase or not job_id:
            return False
        
        try:
            # Buscar data de início para calcular duração
            job_result = self.supabase.table('etl_jobs').select('started_at').eq('id', job_id).execute()
            
            duration_seconds = None
            if job_result.data:
                started_at = datetime.fromisoformat(job_result.data[0]['started_at'].replace('Z', '+00:00'))
                duration_seconds = int((datetime.now() - started_at.replace(tzinfo=None)).total_seconds())
            
            update_data = {
                'status': status,
                'completed_at': datetime.now().isoformat(),
                'duration_seconds': duration_seconds,
                'output_summary': output_summary or {},
                'error_message': error_message,
                'error_details': error_details or {},
                'api_requests_made': api_requests,
                'records_processed': records_processed,
                'records_inserted': records_inserted,
                'records_updated': records_updated,
                'records_failed': records_failed
            }
            
            result = self.supabase.table('etl_jobs').update(update_data).eq('id', job_id).execute()
            
            if result.data:
                status_emoji = "✅" if status == 'completed' else "❌" if status == 'failed' else "⚠️"
                logger.info(f"{status_emoji} Job finalizado: {job_id} - Status: {status}")
                
                # Desativar checkpoints do job
                self.supabase.table('etl_checkpoints').update({'is_active': False}).eq('job_id', job_id).execute()
                
                return True
            else:
                logger.error(f"❌ Erro ao finalizar job: {job_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao finalizar job {job_id}: {e}")
            return False
    
    def create_checkpoint(self,
                         job_id: str,
                         checkpoint_name: str,
                         checkpoint_data: Dict,
                         checkpoint_type: str = 'iteration',
                         progress_percentage: float = 0.0,
                         items_processed: int = 0,
                         items_total: Optional[int] = None,
                         current_step: Optional[str] = None,
                         next_step: Optional[str] = None,
                         execution_context: Optional[Dict] = None,
                         expires_in_hours: int = 24) -> Optional[str]:
        """
        Cria um checkpoint para retomada
        
        Args:
            job_id: ID do job
            checkpoint_name: Nome do checkpoint
            checkpoint_data: Dados para retomada
            checkpoint_type: Tipo do checkpoint
            progress_percentage: Progresso em %
            items_processed: Items processados
            items_total: Total de items
            current_step: Passo atual
            next_step: Próximo passo
            execution_context: Contexto de execução
            expires_in_hours: Horas até expirar
            
        Returns:
            UUID do checkpoint criado ou None se erro
        """
        if not self.supabase or not job_id:
            return None
        
        try:
            # Desativar checkpoint anterior com mesmo nome
            self.supabase.table('etl_checkpoints').update({'is_active': False}).eq('job_id', job_id).eq('checkpoint_name', checkpoint_name).eq('is_active', True).execute()
            
            checkpoint_data_obj = {
                'job_id': job_id,
                'checkpoint_name': checkpoint_name,
                'checkpoint_type': checkpoint_type,
                'checkpoint_data': checkpoint_data,
                'progress_percentage': progress_percentage,
                'items_processed': items_processed,
                'items_total': items_total,
                'current_step': current_step,
                'next_step': next_step,
                'execution_context': execution_context or {},
                'expires_at': (datetime.now() + timedelta(hours=expires_in_hours)).isoformat(),
                'is_active': True
            }
            
            result = self.supabase.table('etl_checkpoints').insert(checkpoint_data_obj).execute()
            
            if result.data:
                checkpoint_id = result.data[0]['id']
                logger.debug(f"📍 Checkpoint criado: {checkpoint_name} (ID: {checkpoint_id})")
                return checkpoint_id
            else:
                logger.error(f"❌ Erro ao criar checkpoint: {checkpoint_name}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar checkpoint {checkpoint_name}: {e}")
            return None
    
    def get_checkpoint(self, job_id: str, checkpoint_name: str) -> Optional[Dict]:
        """
        Recupera um checkpoint ativo
        
        Args:
            job_id: ID do job
            checkpoint_name: Nome do checkpoint
            
        Returns:
            Dados do checkpoint ou None se não encontrado
        """
        if not self.supabase:
            return None
        
        try:
            result = self.supabase.table('etl_checkpoints').select('*').eq('job_id', job_id).eq('checkpoint_name', checkpoint_name).eq('is_active', True).gte('expires_at', datetime.now().isoformat()).execute()
            
            if result.data:
                checkpoint = result.data[0]
                logger.debug(f"📍 Checkpoint recuperado: {checkpoint_name}")
                return checkpoint
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao recuperar checkpoint {checkpoint_name}: {e}")
            return None
    
    def log_job(self,
                job_id: str,
                level: str,
                message: str,
                details: Optional[Dict] = None,
                component: Optional[str] = None,
                function_name: Optional[str] = None) -> Optional[str]:
        """
        Registra log de execução
        
        Args:
            job_id: ID do job
            level: Nível do log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Mensagem do log
            details: Detalhes estruturados
            component: Componente que gerou o log
            function_name: Função que gerou o log
            
        Returns:
            UUID do log criado ou None se erro
        """
        if not self.supabase or not job_id:
            return None
        
        try:
            log_data = {
                'job_id': job_id,
                'log_level': level.upper(),
                'message': message,
                'details': details or {},
                'component': component,
                'function_name': function_name
            }
            
            result = self.supabase.table('etl_job_logs').insert(log_data).execute()
            
            if result.data:
                return result.data[0]['id']
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao registrar log: {e}")
            return None
    
    def get_job_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas dos jobs ETL
        
        Returns:
            Dicionário com estatísticas
        """
        if not self.supabase:
            return {"error": "Supabase não disponível"}
        
        try:
            result = self.supabase.rpc('get_etl_job_stats').execute()
            
            if result.data:
                return result.data[0]
            else:
                return {"error": "Nenhum dado encontrado"}
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {"error": str(e)}
    
    def get_recent_jobs(self, limit: int = 10, job_type: Optional[str] = None) -> List[Dict]:
        """
        Obtém jobs recentes
        
        Args:
            limit: Número máximo de jobs
            job_type: Filtrar por tipo de job
            
        Returns:
            Lista de jobs
        """
        if not self.supabase:
            return []
        
        try:
            query = self.supabase.table('etl_jobs').select('*').order('created_at', desc=True).limit(limit)
            
            if job_type:
                query = query.eq('job_type', job_type)
            
            result = query.execute()
            
            return result.data if result.data else []
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter jobs recentes: {e}")
            return []
    
    def get_job_logs(self, job_id: str, level: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Obtém logs de um job
        
        Args:
            job_id: ID do job
            level: Filtrar por nível de log
            limit: Número máximo de logs
            
        Returns:
            Lista de logs
        """
        if not self.supabase:
            return []
        
        try:
            query = self.supabase.table('etl_job_logs').select('*').eq('job_id', job_id).order('created_at', desc=True).limit(limit)
            
            if level:
                query = query.eq('log_level', level.upper())
            
            result = query.execute()
            
            return result.data if result.data else []
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter logs do job: {e}")
            return []


class ETLJobContext:
    """Context manager para jobs ETL"""
    
    def __init__(self, 
                 job_name: str,
                 job_type: str,
                 metadata_manager: ETLMetadataManager,
                 script_path: Optional[str] = None,
                 input_parameters: Optional[Dict] = None):
        self.job_name = job_name
        self.job_type = job_type
        self.metadata_manager = metadata_manager
        self.script_path = script_path
        self.input_parameters = input_parameters
        self.job_id = None
        self.api_requests = 0
        self.records_processed = 0
        self.records_inserted = 0
        self.records_updated = 0
        self.records_failed = 0
    
    def __enter__(self):
        """Inicia o job"""
        self.job_id = self.metadata_manager.start_job(
            self.job_name,
            self.job_type,
            self.script_path,
            self.input_parameters
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finaliza o job"""
        if self.job_id:
            if exc_type is None:
                # Sucesso
                self.metadata_manager.complete_job(
                    self.job_id,
                    status='completed',
                    api_requests=self.api_requests,
                    records_processed=self.records_processed,
                    records_inserted=self.records_inserted,
                    records_updated=self.records_updated,
                    records_failed=self.records_failed
                )
            else:
                # Erro
                error_message = str(exc_val) if exc_val else "Erro desconhecido"
                error_details = {
                    'exception_type': exc_type.__name__ if exc_type else None,
                    'exception_message': str(exc_val) if exc_val else None
                }
                
                self.metadata_manager.complete_job(
                    self.job_id,
                    status='failed',
                    error_message=error_message,
                    error_details=error_details,
                    api_requests=self.api_requests,
                    records_processed=self.records_processed,
                    records_inserted=self.records_inserted,
                    records_updated=self.records_updated,
                    records_failed=self.records_failed
                )
    
    def log(self, level: str, message: str, **kwargs):
        """Registra log do job"""
        if self.job_id:
            self.metadata_manager.log_job(self.job_id, level, message, kwargs)
    
    def checkpoint(self, name: str, data: Dict, **kwargs):
        """Cria checkpoint"""
        if self.job_id:
            return self.metadata_manager.create_checkpoint(self.job_id, name, data, **kwargs)
    
    def increment_api_requests(self, count: int = 1):
        """Incrementa contador de requisições à API"""
        self.api_requests += count
    
    def increment_records(self, processed: int = 0, inserted: int = 0, updated: int = 0, failed: int = 0):
        """Incrementa contadores de registros"""
        self.records_processed += processed
        self.records_inserted += inserted
        self.records_updated += updated
        self.records_failed += failed
