"""
Testes unitários para ETLMetadataManager
=======================================

Testes para o sistema de metadados ETL
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from bdfut.core.etl_metadata import ETLMetadataManager, ETLJobContext


class TestETLMetadataManager:
    """Testes para ETLMetadataManager"""
    
    def test_init_success(self, mock_config):
        """Testa inicialização bem-sucedida"""
        with patch('bdfut.core.etl_metadata.create_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            
            manager = ETLMetadataManager()
            
            assert manager.supabase == mock_client
            mock_create.assert_called_once()
    
    def test_init_failure(self, mock_config):
        """Testa inicialização com falha"""
        with patch('bdfut.core.etl_metadata.create_client') as mock_create:
            mock_create.side_effect = Exception("Connection failed")
            
            manager = ETLMetadataManager()
            
            assert manager.supabase is None
    
    def test_start_job_success(self, mock_config):
        """Testa início de job com sucesso"""
        with patch('bdfut.core.etl_metadata.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_table.insert.return_value.execute.return_value.data = [{'id': 'test-job-id'}]
            mock_create.return_value = mock_client
            
            manager = ETLMetadataManager()
            job_id = manager.start_job(
                job_name="test_job",
                job_type="base_data",
                script_path="test.py",
                input_parameters={"param1": "value1"}
            )
            
            assert job_id == "test-job-id"
            mock_table.insert.assert_called_once()
    
    def test_start_job_no_supabase(self, mock_config):
        """Testa início de job sem Supabase"""
        with patch('bdfut.core.etl_metadata.create_client') as mock_create:
            mock_create.side_effect = Exception("Connection failed")
            
            manager = ETLMetadataManager()
            job_id = manager.start_job("test_job", "base_data")
            
            assert job_id is None
    
    def test_complete_job_success(self, mock_config):
        """Testa finalização de job com sucesso"""
        with patch('bdfut.core.etl_metadata.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            
            # Mock para buscar data de início
            mock_table.select.return_value.eq.return_value.execute.return_value.data = [
                {'started_at': datetime.now().isoformat()}
            ]
            
            # Mock para update
            mock_table.update.return_value.eq.return_value.execute.return_value.data = [{'id': 'test-job-id'}]
            
            mock_create.return_value = mock_client
            
            manager = ETLMetadataManager()
            result = manager.complete_job(
                job_id="test-job-id",
                status="completed",
                api_requests=10,
                records_processed=100
            )
            
            assert result is True
            assert mock_table.update.called
    
    def test_complete_job_no_job_id(self, mock_config):
        """Testa finalização de job sem ID"""
        with patch('bdfut.core.etl_metadata.create_client') as mock_create:
            mock_create.return_value = Mock()
            
            manager = ETLMetadataManager()
            result = manager.complete_job(job_id=None, status="completed")
            
            assert result is False
    
    def test_create_checkpoint_success(self, mock_config):
        """Testa criação de checkpoint com sucesso"""
        with patch('bdfut.core.etl_metadata.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            
            # Mock para desativar checkpoint anterior
            mock_table.update.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = Mock()
            
            # Mock para inserir novo checkpoint
            mock_table.insert.return_value.execute.return_value.data = [{'id': 'checkpoint-id'}]
            
            mock_create.return_value = mock_client
            
            manager = ETLMetadataManager()
            checkpoint_id = manager.create_checkpoint(
                job_id="test-job-id",
                checkpoint_name="test_checkpoint",
                checkpoint_data={"step": 1},
                progress_percentage=50.0
            )
            
            assert checkpoint_id == "checkpoint-id"
            mock_table.insert.assert_called_once()
    
    def test_get_checkpoint_success(self, mock_config):
        """Testa recuperação de checkpoint com sucesso"""
        with patch('bdfut.core.etl_metadata.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            
            checkpoint_data = {
                'id': 'checkpoint-id',
                'checkpoint_name': 'test_checkpoint',
                'checkpoint_data': {'step': 1}
            }
            
            mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value.data = [checkpoint_data]
            
            mock_create.return_value = mock_client
            
            manager = ETLMetadataManager()
            result = manager.get_checkpoint("test-job-id", "test_checkpoint")
            
            assert result == checkpoint_data
    
    def test_get_checkpoint_not_found(self, mock_config):
        """Testa recuperação de checkpoint não encontrado"""
        with patch('bdfut.core.etl_metadata.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            
            mock_table.select.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value.data = []
            
            mock_create.return_value = mock_client
            
            manager = ETLMetadataManager()
            result = manager.get_checkpoint("test-job-id", "test_checkpoint")
            
            assert result is None
    
    def test_log_job_success(self, mock_config):
        """Testa log de job com sucesso"""
        with patch('bdfut.core.etl_metadata.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            
            mock_table.insert.return_value.execute.return_value.data = [{'id': 'log-id'}]
            
            mock_create.return_value = mock_client
            
            manager = ETLMetadataManager()
            log_id = manager.log_job(
                job_id="test-job-id",
                level="INFO",
                message="Test message",
                details={"key": "value"}
            )
            
            assert log_id == "log-id"
            mock_table.insert.assert_called_once()
    
    def test_get_job_stats_success(self, mock_config):
        """Testa obtenção de estatísticas com sucesso"""
        with patch('bdfut.core.etl_metadata.create_client') as mock_create:
            mock_client = Mock()
            mock_client.rpc.return_value.execute.return_value.data = [
                {
                    'total_jobs': 10,
                    'completed_jobs': 8,
                    'failed_jobs': 1,
                    'running_jobs': 1
                }
            ]
            
            mock_create.return_value = mock_client
            
            manager = ETLMetadataManager()
            stats = manager.get_job_stats()
            
            assert stats['total_jobs'] == 10
            assert stats['completed_jobs'] == 8
    
    def test_get_recent_jobs_success(self, mock_config):
        """Testa obtenção de jobs recentes com sucesso"""
        with patch('bdfut.core.etl_metadata.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            
            jobs_data = [
                {'id': 'job1', 'job_name': 'test1', 'status': 'completed'},
                {'id': 'job2', 'job_name': 'test2', 'status': 'running'}
            ]
            
            mock_table.select.return_value.order.return_value.limit.return_value.execute.return_value.data = jobs_data
            
            mock_create.return_value = mock_client
            
            manager = ETLMetadataManager()
            jobs = manager.get_recent_jobs(limit=5)
            
            assert len(jobs) == 2
            assert jobs[0]['job_name'] == 'test1'
    
    def test_get_job_logs_success(self, mock_config):
        """Testa obtenção de logs de job com sucesso"""
        with patch('bdfut.core.etl_metadata.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            
            logs_data = [
                {'id': 'log1', 'message': 'Test log 1', 'log_level': 'INFO'},
                {'id': 'log2', 'message': 'Test log 2', 'log_level': 'ERROR'}
            ]
            
            mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = logs_data
            
            mock_create.return_value = mock_client
            
            manager = ETLMetadataManager()
            logs = manager.get_job_logs("test-job-id")
            
            assert len(logs) == 2
            assert logs[0]['message'] == 'Test log 1'


class TestETLJobContext:
    """Testes para ETLJobContext"""
    
    def test_context_manager_success(self, mock_config):
        """Testa context manager com sucesso"""
        mock_manager = Mock()
        mock_manager.start_job.return_value = "test-job-id"
        mock_manager.complete_job.return_value = True
        
        with ETLJobContext(
            job_name="test_job",
            job_type="base_data",
            metadata_manager=mock_manager
        ) as job:
            assert job.job_id == "test-job-id"
            job.increment_api_requests(5)
            job.increment_records(processed=10, inserted=8)
        
        # Verificar se job foi finalizado com sucesso
        mock_manager.complete_job.assert_called_once()
        call_args = mock_manager.complete_job.call_args
        assert call_args[0][0] == "test-job-id"  # job_id
        assert call_args[1]['status'] == 'completed'
        assert call_args[1]['api_requests'] == 5
        assert call_args[1]['records_processed'] == 10
        assert call_args[1]['records_inserted'] == 8
    
    def test_context_manager_with_exception(self, mock_config):
        """Testa context manager com exceção"""
        mock_manager = Mock()
        mock_manager.start_job.return_value = "test-job-id"
        mock_manager.complete_job.return_value = True
        
        try:
            with ETLJobContext(
                job_name="test_job",
                job_type="base_data",
                metadata_manager=mock_manager
            ) as job:
                job.increment_api_requests(3)
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Verificar se job foi finalizado com erro
        mock_manager.complete_job.assert_called_once()
        call_args = mock_manager.complete_job.call_args
        assert call_args[1]['status'] == 'failed'
        assert call_args[1]['error_message'] == 'Test error'
        assert call_args[1]['api_requests'] == 3
    
    def test_log_method(self, mock_config):
        """Testa método de log"""
        mock_manager = Mock()
        mock_manager.start_job.return_value = "test-job-id"
        mock_manager.log_job.return_value = "log-id"
        
        with ETLJobContext(
            job_name="test_job",
            job_type="base_data",
            metadata_manager=mock_manager
        ) as job:
            job.log("INFO", "Test message", component="test")
        
        mock_manager.log_job.assert_called_once_with(
            "test-job-id", "INFO", "Test message", {"component": "test"}
        )
    
    def test_checkpoint_method(self, mock_config):
        """Testa método de checkpoint"""
        mock_manager = Mock()
        mock_manager.start_job.return_value = "test-job-id"
        mock_manager.create_checkpoint.return_value = "checkpoint-id"
        
        with ETLJobContext(
            job_name="test_job",
            job_type="base_data",
            metadata_manager=mock_manager
        ) as job:
            checkpoint_id = job.checkpoint("test_checkpoint", {"step": 1}, progress_percentage=50.0)
        
        assert checkpoint_id == "checkpoint-id"
        mock_manager.create_checkpoint.assert_called_once_with(
            "test-job-id", "test_checkpoint", {"step": 1}, progress_percentage=50.0
        )
    
    def test_increment_methods(self, mock_config):
        """Testa métodos de incremento"""
        mock_manager = Mock()
        mock_manager.start_job.return_value = "test-job-id"
        
        with ETLJobContext(
            job_name="test_job",
            job_type="base_data",
            metadata_manager=mock_manager
        ) as job:
            # Testar incremento de API requests
            job.increment_api_requests(3)
            job.increment_api_requests()  # default 1
            assert job.api_requests == 4
            
            # Testar incremento de records
            job.increment_records(processed=10, inserted=8, updated=2, failed=1)
            job.increment_records(processed=5)  # outros defaults 0
            
            assert job.records_processed == 15
            assert job.records_inserted == 8
            assert job.records_updated == 2
            assert job.records_failed == 1
