"""
Testes de Performance para BDFut
===============================

Testes para validar performance, throughput e escalabilidade
do sistema ETL e componentes críticos.

QA-004: Testes de Performance
"""
import pytest
import time
import psutil
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch, MagicMock
import json
import logging
from datetime import datetime, timedelta
import statistics
import sys
import os

from bdfut.core.etl_process import ETLProcess
from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
from bdfut.core.redis_cache import RedisCache
from bdfut.config.config import Config


class TestAPIPerformance:
    """Testes de performance da API Sportmonks"""
    
    def test_single_api_request_performance(self, mock_config):
        """Testa performance de uma única requisição à API"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            print("⚡ Performance: Requisição única à API")
            
            # Mock resposta da API
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'x-ratelimit-remaining': '2999'}
            mock_response.json.return_value = {
                'data': [{'id': 1, 'name': 'Brazil', 'fifa_name': 'BRA'}]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            client = SportmonksClient(enable_cache=False)
            
            # Medir tempo de resposta
            start_time = time.time()
            result = client.get_countries()
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Verificações de performance
            assert result is not None
            assert response_time < 2.0  # Deve responder em menos de 2 segundos
            assert mock_get.call_count == 1
            
            print(f"✅ Tempo de resposta: {response_time:.3f}s")
    
    def test_api_batch_performance(self, mock_config):
        """Testa performance de múltiplas requisições em lote"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            print("⚡ Performance: Lote de requisições à API")
            
            # Mock múltiplas respostas
            responses = []
            for i in range(10):
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.headers = {'x-ratelimit-remaining': str(2990 - i)}
                mock_response.json.return_value = {
                    'data': [{'id': i + 1, 'name': f'Country {i + 1}'}]
                }
                mock_response.raise_for_status.return_value = None
                responses.append(mock_response)
            
            mock_get.side_effect = responses
            
            client = SportmonksClient(enable_cache=False)
            
            # Medir performance do lote
            start_time = time.time()
            results = []
            
            for i in range(10):
                result = client.get_countries()
                results.append(result)
                time.sleep(0.1)  # Simular rate limiting
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_response_time = total_time / 10
            
            # Verificações
            assert len(results) == 10
            assert total_time < 15.0  # 10 requisições em menos de 15s
            assert avg_response_time < 1.5  # Média < 1.5s por requisição
            
            print(f"✅ Lote de 10 requisições: {total_time:.3f}s total, {avg_response_time:.3f}s média")
    
    def test_api_rate_limiting_performance(self, mock_config):
        """Testa performance com rate limiting ativo"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            print("⚡ Performance: Rate limiting")
            
            # Mock respostas com rate limiting
            def mock_rate_limited_response(*args, **kwargs):
                # Simular delay de rate limiting
                time.sleep(0.5)  # 500ms delay por requisição
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.headers = {'x-ratelimit-remaining': '1'}
                mock_response.json.return_value = {
                    'data': [{'id': 1, 'name': 'Test'}]
                }
                mock_response.raise_for_status.return_value = None
                return mock_response
            
            mock_get.side_effect = mock_rate_limited_response
            
            client = SportmonksClient(enable_cache=False)
            
            # Testar rate limiting
            start_time = time.time()
            
            # Fazer 3 requisições rapidamente
            for i in range(3):
                client.get_countries()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verificar que rate limiting foi aplicado
            assert total_time > 1.0  # Deve ter delay devido ao rate limiting
            assert mock_get.call_count == 3
            
            print(f"✅ Rate limiting ativo: {total_time:.3f}s para 3 requisições")


class TestCachePerformance:
    """Testes de performance do sistema de cache"""
    
    def test_cache_hit_performance(self, mock_config):
        """Testa performance de cache hit"""
        with patch('bdfut.core.redis_cache.redis.Redis') as mock_redis_class:
            print("⚡ Performance: Cache hit")
            
            # Mock Redis com comportamento de cache miss/hit
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            
            # Primeira chamada: cache miss (None), segunda: cache hit (dados)
            call_count = 0
            def mock_get(key):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return None  # Cache miss
                else:
                    return json.dumps([{'id': 1, 'name': 'Brazil'}])  # Cache hit
            
            mock_redis.get.side_effect = mock_get
            mock_redis.set.return_value = True
            
            cache = RedisCache(enable_fallback=False)
            
            # Primeira chamada (cache miss) - deve retornar None e fazer set
            start_time = time.time()
            result1 = cache.get('countries')
            first_call_time = time.time() - start_time
            
            # Segunda chamada (cache hit) - deve retornar dados do cache
            start_time = time.time()
            result2 = cache.get('countries')
            second_call_time = time.time() - start_time
            
            # Verificações
            assert result1 is None  # Primeira chamada é cache miss
            assert result2 is not None  # Segunda chamada é cache hit
            assert second_call_time < first_call_time  # Cache hit deve ser mais rápido
            assert second_call_time < 0.1  # Cache hit em menos de 100ms
            
            print(f"✅ Cache miss: {first_call_time:.3f}s, Cache hit: {second_call_time:.3f}s")
    
    def test_cache_throughput(self, mock_config):
        """Testa throughput do cache com múltiplas operações"""
        with patch('redis.Redis') as mock_redis_class:
            print("⚡ Performance: Throughput do cache")
            
            # Mock Redis
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.get.return_value = json.dumps([{'id': 1, 'name': 'Test'}])
            mock_redis.set.return_value = True
            
            cache = RedisCache(enable_fallback=False)
            
            # Testar throughput
            start_time = time.time()
            
            # 100 operações de leitura
            for i in range(100):
                cache.get(f'key_{i}')
            
            end_time = time.time()
            total_time = end_time - start_time
            operations_per_second = 100 / total_time
            
            # Verificações
            assert total_time < 5.0  # 100 operações em menos de 5s
            assert operations_per_second > 20  # Pelo menos 20 ops/s
            
            print(f"✅ Throughput: {operations_per_second:.1f} operações/segundo")
    
    def test_cache_memory_usage(self, mock_config):
        """Testa uso de memória do cache local"""
        print("⚡ Performance: Uso de memória do cache")
        
        # Monitorar memória inicial
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        cache = RedisCache(enable_fallback=True)
        
        # Adicionar dados ao cache local
        large_data = [{'id': i, 'data': f'large_data_string_{i}' * 100} for i in range(1000)]
        
        start_time = time.time()
        for i, data in enumerate(large_data):
            cache.set(f'large_key_{i}', data, ttl=3600)
        end_time = time.time()
        
        # Monitorar memória após cache
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Verificações
        assert memory_increase < 100  # Não deve usar mais de 100MB
        assert end_time - start_time < 10.0  # Operação em menos de 10s
        
        print(f"✅ Memória: +{memory_increase:.1f}MB para 1000 itens")


class TestDatabasePerformance:
    """Testes de performance do banco de dados"""
    
    def test_single_upsert_performance(self, mock_config):
        """Testa performance de um único upsert"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            print("⚡ Performance: Upsert único")
            
            # Mock Supabase
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_table.upsert.return_value = Mock()
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            # Dados de teste
            test_countries = [
                {'id': 1, 'name': 'Brazil', 'fifa_name': 'BRA'},
                {'id': 2, 'name': 'Argentina', 'fifa_name': 'ARG'}
            ]
            
            # Medir performance
            start_time = time.time()
            result = client.upsert_countries(test_countries)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Verificações
            assert result is True
            assert response_time < 1.0  # Upsert em menos de 1 segundo
            
            print(f"✅ Upsert único: {response_time:.3f}s")
    
    def test_bulk_upsert_performance(self, mock_config):
        """Testa performance de upsert em lote"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            print("⚡ Performance: Upsert em lote")
            
            # Mock Supabase
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_table.upsert.return_value = Mock()
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            # Dados grandes para teste
            large_countries = [
                {
                    'id': i,
                    'name': f'Country {i}',
                    'fifa_name': f'C{i:03d}',
                    'iso2': f'C{i}',
                    'iso3': f'C{i:02d}'
                }
                for i in range(1, 1001)  # 1000 países
            ]
            
            # Medir performance
            start_time = time.time()
            result = client.upsert_countries(large_countries)
            end_time = time.time()
            
            response_time = end_time - start_time
            records_per_second = 1000 / response_time
            
            # Verificações
            assert result is True
            assert response_time < 5.0  # 1000 registros em menos de 5s
            assert records_per_second > 200  # Pelo menos 200 registros/s
            
            print(f"✅ Upsert em lote: {response_time:.3f}s ({records_per_second:.0f} reg/s)")
    
    def test_concurrent_upserts_performance(self, mock_config):
        """Testa performance de upserts concorrentes"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            print("⚡ Performance: Upserts concorrentes")
            
            # Mock Supabase
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_table.upsert.return_value = Mock()
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            def upsert_batch(batch_id):
                """Função para upsert de um lote"""
                countries = [
                    {'id': i, 'name': f'Country {i}'}
                    for i in range(batch_id * 100, (batch_id + 1) * 100)
                ]
                return client.upsert_countries(countries)
            
            # Executar 5 upserts concorrentes
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(upsert_batch, i) for i in range(5)]
                results = [future.result() for future in as_completed(futures)]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verificações
            assert all(results)  # Todos os upserts devem ter sucesso
            assert total_time < 10.0  # 5 upserts concorrentes em menos de 10s
            
            print(f"✅ Upserts concorrentes: {total_time:.3f}s para 5 lotes")


class TestETLPerformance:
    """Testes de performance do processo ETL completo"""
    
    def test_sync_base_data_performance(self, mock_config):
        """Testa performance da sincronização de dados base"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            print("⚡ Performance: Sincronização dados base")
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dados
            mock_sportmonks_instance.get_countries.return_value = [
                {'id': 1, 'name': 'Brazil'}, {'id': 2, 'name': 'Argentina'}
            ]
            mock_sportmonks_instance.get_states.return_value = [
                {'id': 1, 'state': 'scheduled'}, {'id': 5, 'state': 'finished'}
            ]
            mock_sportmonks_instance.get_types.return_value = [
                {'id': 1, 'name': 'Goal'}, {'id': 2, 'name': 'Yellow Card'}
            ]
            
            mock_supabase_instance.upsert_countries.return_value = True
            mock_supabase_instance.upsert_states.return_value = True
            mock_supabase_instance.upsert_types.return_value = True
            
            # Mock job context
            mock_job_context = Mock()
            mock_job_context.__enter__ = Mock(return_value=mock_job_context)
            mock_job_context.__exit__ = Mock(return_value=None)
            
            etl = ETLProcess()
            
            # Medir performance
            start_time = time.time()
            
            with patch('bdfut.core.etl_process.ETLJobContext', return_value=mock_job_context):
                etl.sync_base_data()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verificações
            assert total_time < 5.0  # Sincronização completa em menos de 5s
            
            # Verificar que todos os métodos foram chamados
            mock_sportmonks_instance.get_countries.assert_called_once()
            mock_sportmonks_instance.get_states.assert_called_once()
            mock_sportmonks_instance.get_types.assert_called_once()
            
            mock_supabase_instance.upsert_countries.assert_called_once()
            mock_supabase_instance.upsert_states.assert_called_once()
            mock_supabase_instance.upsert_types.assert_called_once()
            
            print(f"✅ Sincronização dados base: {total_time:.3f}s")
    
    def test_sync_leagues_performance(self, mock_config):
        """Testa performance da sincronização de ligas"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            print("⚡ Performance: Sincronização de ligas")
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dados de ligas
            mock_leagues_data = {
                'id': 8,
                'name': 'Premier League',
                'country_id': 42,
                'seasons': [
                    {'id': 25583, 'league_id': 8, 'name': '2025', 'is_current': True}
                ]
            }
            mock_sportmonks_instance.get_league_by_id.return_value = mock_leagues_data
            
            mock_supabase_instance.upsert_leagues.return_value = True
            mock_supabase_instance.upsert_seasons.return_value = True
            
            etl = ETLProcess()
            
            # Medir performance
            start_time = time.time()
            etl.sync_leagues([8])  # Premier League
            end_time = time.time()
            
            total_time = end_time - start_time
            
            # Verificações
            assert total_time < 3.0  # Sincronização de liga em menos de 3s
            mock_sportmonks_instance.get_league_by_id.assert_called_once()
            mock_supabase_instance.upsert_leagues.assert_called_once()
            mock_supabase_instance.upsert_seasons.assert_called_once()
            
            print(f"✅ Sincronização de liga: {total_time:.3f}s")
    
    def test_full_etl_workflow_performance(self, mock_config):
        """Testa performance do workflow ETL completo"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            print("⚡ Performance: Workflow ETL completo")
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dados base
            mock_sportmonks_instance.get_countries.return_value = [
                {'id': 1, 'name': 'Brazil'}, {'id': 2, 'name': 'Argentina'}
            ]
            mock_sportmonks_instance.get_states.return_value = [
                {'id': 1, 'state': 'scheduled'}, {'id': 5, 'state': 'finished'}
            ]
            mock_sportmonks_instance.get_types.return_value = [
                {'id': 1, 'name': 'Goal'}, {'id': 2, 'name': 'Yellow Card'}
            ]
            
            # Mock dados de ligas
            mock_leagues_data = {
                'id': 8,
                'name': 'Premier League',
                'country_id': 42,
                'seasons': [
                    {'id': 25583, 'league_id': 8, 'name': '2025', 'is_current': True}
                ]
            }
            mock_sportmonks_instance.get_league_by_id.return_value = mock_leagues_data
            
            # Mock todos os upserts
            mock_supabase_instance.upsert_countries.return_value = True
            mock_supabase_instance.upsert_states.return_value = True
            mock_supabase_instance.upsert_types.return_value = True
            mock_supabase_instance.upsert_leagues.return_value = True
            mock_supabase_instance.upsert_seasons.return_value = True
            
            # Mock job context
            mock_job_context = Mock()
            mock_job_context.__enter__ = Mock(return_value=mock_job_context)
            mock_job_context.__exit__ = Mock(return_value=None)
            
            etl = ETLProcess()
            
            # Medir performance do workflow completo
            start_time = time.time()
            
            with patch('bdfut.core.etl_process.ETLJobContext', return_value=mock_job_context):
                # 1. Sincronizar dados base
                etl.sync_base_data()
                
                # 2. Sincronizar ligas principais
                etl.sync_leagues([8])  # Premier League
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verificações
            assert total_time < 10.0  # Workflow completo em menos de 10s
            
            # Verificar que todos os passos foram executados
            assert mock_sportmonks_instance.get_countries.call_count == 1
            assert mock_sportmonks_instance.get_states.call_count == 1
            assert mock_sportmonks_instance.get_types.call_count == 1
            assert mock_sportmonks_instance.get_league_by_id.call_count == 1
            
            print(f"✅ Workflow ETL completo: {total_time:.3f}s")


class TestScalabilityPerformance:
    """Testes de escalabilidade e carga"""
    
    def test_concurrent_users_performance(self, mock_config):
        """Testa performance com usuários concorrentes"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            print("⚡ Performance: Usuários concorrentes")
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dados
            mock_sportmonks_instance.get_countries.return_value = [
                {'id': 1, 'name': 'Brazil'}
            ]
            mock_supabase_instance.upsert_countries.return_value = True
            
            # Mock job context
            mock_job_context = Mock()
            mock_job_context.__enter__ = Mock(return_value=mock_job_context)
            mock_job_context.__exit__ = Mock(return_value=None)
            
            def simulate_user_workflow():
                """Simula workflow de um usuário"""
                etl = ETLProcess()
                with patch('bdfut.core.etl_process.ETLJobContext', return_value=mock_job_context):
                    etl.sync_base_data()
                return True
            
            # Simular 10 usuários concorrentes
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(simulate_user_workflow) for _ in range(10)]
                results = [future.result() for future in as_completed(futures)]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verificações
            assert all(results)  # Todos os usuários devem completar com sucesso
            assert total_time < 15.0  # 10 usuários em menos de 15s
            
            print(f"✅ 10 usuários concorrentes: {total_time:.3f}s")
    
    def test_memory_usage_under_load(self, mock_config):
        """Testa uso de memória sob carga"""
        print("⚡ Performance: Uso de memória sob carga")
        
        # Monitorar memória inicial
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simular carga de processamento
        def memory_intensive_task():
            """Tarefa que usa memória"""
            data = []
            for i in range(10000):
                data.append({
                    'id': i,
                    'name': f'Item {i}',
                    'data': f'Large data string {i}' * 100
                })
            return len(data)
        
        # Executar múltiplas tarefas concorrentes
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(memory_intensive_task) for _ in range(5)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Monitorar memória após carga
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Verificações
        assert all(result == 10000 for result in results)
        assert total_time < 10.0  # Processamento em menos de 10s
        assert memory_increase < 200  # Não deve usar mais de 200MB
        
        print(f"✅ Memória sob carga: +{memory_increase:.1f}MB em {total_time:.3f}s")
    
    def test_system_resource_usage(self, mock_config):
        """Testa uso de recursos do sistema"""
        print("⚡ Performance: Recursos do sistema")
        
        # Monitorar recursos iniciais
        initial_cpu = psutil.cpu_percent(interval=1)
        initial_memory = psutil.virtual_memory().percent
        
        # Simular processamento intensivo
        def cpu_intensive_task():
            """Tarefa que usa CPU"""
            result = 0
            for i in range(1000000):
                result += i * i
            return result
        
        # Executar tarefas concorrentes
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(cpu_intensive_task) for _ in range(4)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Monitorar recursos após processamento
        final_cpu = psutil.cpu_percent(interval=1)
        final_memory = psutil.virtual_memory().percent
        
        cpu_increase = final_cpu - initial_cpu
        memory_increase = final_memory - initial_memory
        
        # Verificações
        assert all(result > 0 for result in results)
        assert total_time < 20.0  # Processamento em menos de 20s
        assert cpu_increase < 50  # Não deve aumentar CPU em mais de 50%
        assert memory_increase < 20  # Não deve aumentar memória em mais de 20%
        
        print(f"✅ CPU: +{cpu_increase:.1f}%, Memória: +{memory_increase:.1f}% em {total_time:.3f}s")


class TestPerformanceBenchmarks:
    """Benchmarks de performance para estabelecer métricas de referência"""
    
    def test_api_response_time_benchmark(self, mock_config):
        """Estabelece benchmark de tempo de resposta da API"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            print("📊 Benchmark: Tempo de resposta da API")
            
            # Mock resposta rápida
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'x-ratelimit-remaining': '2999'}
            mock_response.json.return_value = {'data': [{'id': 1, 'name': 'Test'}]}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            client = SportmonksClient(enable_cache=False)
            
            # Medir múltiplas requisições para estatísticas
            response_times = []
            for i in range(10):
                start_time = time.time()
                client.get_countries()
                end_time = time.time()
                response_times.append(end_time - start_time)
            
            # Calcular estatísticas
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            std_deviation = statistics.stdev(response_times)
            
            # Benchmarks estabelecidos
            assert avg_response_time < 1.0  # Média < 1s
            assert min_response_time < 0.5  # Melhor caso < 0.5s
            assert max_response_time < 2.0  # Pior caso < 2s
            assert std_deviation < 0.5  # Baixa variabilidade
            
            print(f"✅ Benchmark API: {avg_response_time:.3f}s média, {min_response_time:.3f}s-{max_response_time:.3f}s range")
    
    def test_database_throughput_benchmark(self, mock_config):
        """Estabelece benchmark de throughput do banco"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            print("📊 Benchmark: Throughput do banco")
            
            # Mock Supabase
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_table.upsert.return_value = Mock()
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            # Testar diferentes tamanhos de lote
            batch_sizes = [10, 50, 100, 500, 1000]
            throughputs = []
            
            for batch_size in batch_sizes:
                test_data = [
                    {'id': i, 'name': f'Country {i}'}
                    for i in range(batch_size)
                ]
                
                start_time = time.time()
                client.upsert_countries(test_data)
                end_time = time.time()
                
                duration = end_time - start_time
                throughput = batch_size / duration
                throughputs.append(throughput)
            
            # Benchmarks estabelecidos
            assert throughputs[0] > 100  # 10 registros: >100 reg/s
            assert throughputs[1] > 200  # 50 registros: >200 reg/s
            assert throughputs[2] > 300  # 100 registros: >300 reg/s
            assert throughputs[3] > 400  # 500 registros: >400 reg/s
            assert throughputs[4] > 500  # 1000 registros: >500 reg/s
            
            print(f"✅ Benchmark DB: {throughputs[4]:.0f} reg/s para 1000 registros")
    
    def test_cache_efficiency_benchmark(self, mock_config):
        """Estabelece benchmark de eficiência do cache"""
        with patch('redis.Redis') as mock_redis_class:
            print("📊 Benchmark: Eficiência do cache")
            
            # Mock Redis
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.get.return_value = json.dumps([{'id': 1, 'name': 'Test'}])
            mock_redis.set.return_value = True
            
            cache = RedisCache(enable_fallback=False)
            
            # Testar hit rate
            total_requests = 100
            cache_hits = 0
            
            for i in range(total_requests):
                if i < 50:  # Primeira metade: cache miss
                    cache.set(f'key_{i}', {'data': f'value_{i}'})
                else:  # Segunda metade: cache hit
                    result = cache.get(f'key_{i-50}')
                    if result:
                        cache_hits += 1
            
            hit_rate = (cache_hits / 50) * 100  # Hit rate dos últimos 50 requests
            
            # Benchmarks estabelecidos
            assert hit_rate > 90  # Hit rate > 90%
            assert cache.redis_hits > 0  # Deve ter hits no Redis
            
            print(f"✅ Benchmark Cache: {hit_rate:.1f}% hit rate")
    
    def test_etl_pipeline_benchmark(self, mock_config):
        """Estabelece benchmark do pipeline ETL completo"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            print("📊 Benchmark: Pipeline ETL completo")
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dados completos
            mock_sportmonks_instance.get_countries.return_value = [
                {'id': i, 'name': f'Country {i}'} for i in range(1, 101)
            ]
            mock_sportmonks_instance.get_states.return_value = [
                {'id': i, 'state': f'state_{i}'} for i in range(1, 11)
            ]
            mock_sportmonks_instance.get_types.return_value = [
                {'id': i, 'name': f'type_{i}'} for i in range(1, 21)
            ]
            
            # Mock ligas
            mock_leagues_data = {
                'id': 8,
                'name': 'Premier League',
                'seasons': [
                    {'id': 25583, 'league_id': 8, 'name': '2025', 'is_current': True}
                ]
            }
            mock_sportmonks_instance.get_league_by_id.return_value = mock_leagues_data
            
            # Mock todos os upserts
            mock_supabase_instance.upsert_countries.return_value = True
            mock_supabase_instance.upsert_states.return_value = True
            mock_supabase_instance.upsert_types.return_value = True
            mock_supabase_instance.upsert_leagues.return_value = True
            mock_supabase_instance.upsert_seasons.return_value = True
            
            # Mock job context
            mock_job_context = Mock()
            mock_job_context.__enter__ = Mock(return_value=mock_job_context)
            mock_job_context.__exit__ = Mock(return_value=None)
            
            etl = ETLProcess()
            
            # Medir pipeline completo
            start_time = time.time()
            
            with patch('bdfut.core.etl_process.ETLJobContext', return_value=mock_job_context):
                # Pipeline completo: base data + leagues
                etl.sync_base_data()
                etl.sync_leagues([8])
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Calcular métricas
            total_records = 100 + 10 + 20 + 1 + 1  # countries + states + types + league + season
            records_per_second = total_records / total_time
            
            # Benchmarks estabelecidos
            assert total_time < 8.0  # Pipeline completo em menos de 8s
            assert records_per_second > 15  # Pelo menos 15 registros/s
            
            print(f"✅ Benchmark ETL: {total_time:.3f}s para {total_records} registros ({records_per_second:.1f} reg/s)")
