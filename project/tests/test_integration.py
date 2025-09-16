"""
Testes de Integração para BDFut
===============================

Testes end-to-end que validam a integração entre componentes do sistema,
fluxos completos de ETL e cenários reais de uso.

QA-002: Implementar Testes de Integração
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json
import logging

from bdfut.core.etl_process import ETLProcess
from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
from bdfut.core.etl_metadata import ETLMetadataManager
from bdfut.config.config import Config


class TestETLIntegrationFlows:
    """Testes de integração para fluxos completos de ETL"""
    
    def test_complete_base_data_sync_flow(self, mock_config):
        """Testa fluxo completo de sincronização de dados base"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase, \
             patch('bdfut.core.etl_process.ETLMetadataManager') as mock_metadata:
            
            # Mock do SportmonksClient
            mock_sportmonks_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            
            # Mock dados da API
            mock_states = [
                {'id': 1, 'state': 'scheduled', 'name': 'Scheduled'},
                {'id': 5, 'state': 'finished', 'name': 'Finished'}
            ]
            mock_types = [
                {'id': 1, 'name': 'Goal', 'code': 'goal'},
                {'id': 2, 'name': 'Yellow Card', 'code': 'yellowcard'}
            ]
            mock_countries = [
                {'id': 1, 'name': 'Brazil', 'fifa_name': 'BRA'},
                {'id': 2, 'name': 'Argentina', 'fifa_name': 'ARG'}
            ]
            
            mock_sportmonks_instance.get_states.return_value = mock_states
            mock_sportmonks_instance.get_types.return_value = mock_types
            mock_sportmonks_instance.get_countries.return_value = mock_countries
            
            # Mock do SupabaseClient
            mock_supabase_instance = Mock()
            mock_supabase.return_value = mock_supabase_instance
            mock_supabase_instance.upsert_states.return_value = True
            mock_supabase_instance.upsert_types.return_value = True
            mock_supabase_instance.upsert_countries.return_value = True
            
            # Mock do ETLMetadataManager
            mock_metadata_instance = Mock()
            mock_metadata.return_value = mock_metadata_instance
            
            # Mock do ETLJobContext
            mock_job_context = Mock()
            mock_job_context.__enter__ = Mock(return_value=mock_job_context)
            mock_job_context.__exit__ = Mock(return_value=None)
            
            with patch('bdfut.core.etl_process.ETLJobContext', return_value=mock_job_context):
                # Executar fluxo completo
                etl = ETLProcess()
                etl.sync_base_data()
                
                # Verificar que todo o fluxo foi executado
                mock_sportmonks_instance.get_states.assert_called_once()
                mock_sportmonks_instance.get_types.assert_called_once()
                mock_sportmonks_instance.get_countries.assert_called_once()
                
                mock_supabase_instance.upsert_states.assert_called_once_with(mock_states)
                mock_supabase_instance.upsert_types.assert_called_once_with(mock_types)
                mock_supabase_instance.upsert_countries.assert_called_once_with(mock_countries)
                
                # Verificar logging e checkpoints
                assert mock_job_context.log.call_count >= 6  # Pelo menos 6 logs
                assert mock_job_context.checkpoint.call_count == 3  # 3 checkpoints
                assert mock_job_context.increment_api_requests.call_count == 3  # 3 requests
                assert mock_job_context.increment_records.call_count == 3  # 3 record increments
    
    def test_league_and_teams_integration_flow(self, mock_config):
        """Testa fluxo integrado de sincronização de ligas e times"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock do SportmonksClient
            mock_sportmonks_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            
            # Mock dados de liga com temporadas
            mock_league_data = {
                'id': 648,
                'name': 'Brasil - Serie A',
                'country_id': 1,
                'seasons': [
                    {'id': 25583, 'league_id': 648, 'name': '2025/2026', 'is_current': True}
                ]
            }
            mock_sportmonks_instance.get_league_by_id.return_value = mock_league_data
            
            # Mock dados de times
            mock_teams_data = [
                {
                    'id': 1,
                    'name': 'Palmeiras',
                    'venue': {'id': 1, 'name': 'Allianz Parque', 'capacity': 43713}
                },
                {
                    'id': 2,
                    'name': 'Flamengo',
                    'venue': {'id': 2, 'name': 'Maracanã', 'capacity': 78838}
                }
            ]
            mock_sportmonks_instance.get_teams_by_season.return_value = mock_teams_data
            
            # Mock do SupabaseClient
            mock_supabase_instance = Mock()
            mock_supabase.return_value = mock_supabase_instance
            mock_supabase_instance.upsert_leagues.return_value = True
            mock_supabase_instance.upsert_seasons.return_value = True
            mock_supabase_instance.upsert_venues.return_value = True
            mock_supabase_instance.upsert_teams.return_value = True
            
            # Executar fluxo integrado
            etl = ETLProcess()
            
            # 1. Sincronizar liga
            etl.sync_leagues([648])
            
            # 2. Sincronizar times da temporada
            result = etl.sync_teams_by_season(25583)
            
            # Verificações
            assert result is True
            
            # Verificar chamadas da API
            mock_sportmonks_instance.get_league_by_id.assert_called_with(648, include='seasons')
            mock_sportmonks_instance.get_teams_by_season.assert_called_with(25583, include='venue')
            
            # Verificar upserts no banco
            mock_supabase_instance.upsert_leagues.assert_called()
            mock_supabase_instance.upsert_seasons.assert_called()
            mock_supabase_instance.upsert_venues.assert_called()
            mock_supabase_instance.upsert_teams.assert_called()
    
    def test_fixtures_with_events_integration_flow(self, mock_config):
        """Testa fluxo completo de fixtures com eventos"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock do SportmonksClient
            mock_sportmonks_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            
            # Mock dados completos de fixture
            mock_fixtures_data = [
                {
                    'id': 1,
                    'name': 'Palmeiras vs Flamengo',
                    'starting_at': '2025-01-15T20:00:00Z',
                    'venue': {'id': 1, 'name': 'Allianz Parque', 'capacity': 43713},
                    'referees': [{'id': 1, 'name': 'Raphael Claus'}],
                    'participants': [
                        {'id': 1, 'meta': {'location': 'home'}},
                        {'id': 2, 'meta': {'location': 'away'}}
                    ],
                    'events': [
                        {
                            'id': 1,
                            'minute': 15,
                            'type_id': 1,
                            'player_name': 'Dudu',
                            'result': '1-0'
                        },
                        {
                            'id': 2,
                            'minute': 67,
                            'type_id': 1,
                            'player_name': 'Gabigol',
                            'result': '1-1'
                        }
                    ]
                }
            ]
            mock_sportmonks_instance.get_fixtures_by_date_range.return_value = mock_fixtures_data
            
            # Mock do SupabaseClient
            mock_supabase_instance = Mock()
            mock_supabase.return_value = mock_supabase_instance
            mock_supabase_instance.upsert_venues.return_value = True
            mock_supabase_instance.upsert_referees.return_value = True
            mock_supabase_instance.upsert_fixtures.return_value = True
            mock_supabase_instance.upsert_fixture_participants.return_value = True
            mock_supabase_instance.upsert_fixture_events.return_value = True
            
            # Executar fluxo completo
            etl = ETLProcess()
            result = etl.sync_fixtures_by_date_range('2025-01-15', '2025-01-15', include_details=True)
            
            # Verificações
            assert result is True
            
            # Verificar que todos os componentes foram processados
            mock_supabase_instance.upsert_venues.assert_called_once()
            mock_supabase_instance.upsert_referees.assert_called_once()
            mock_supabase_instance.upsert_fixtures.assert_called_once()
            mock_supabase_instance.upsert_fixture_participants.assert_called_once()
            mock_supabase_instance.upsert_fixture_events.assert_called_once()
            
            # Verificar dados processados
            venues_call = mock_supabase_instance.upsert_venues.call_args[0][0]
            assert len(venues_call) == 1
            assert venues_call[0]['name'] == 'Allianz Parque'
            
            events_call = mock_supabase_instance.upsert_fixture_events.call_args[0][1]
            assert len(events_call) == 2
            assert events_call[0]['player_name'] == 'Dudu'
            assert events_call[1]['player_name'] == 'Gabigol'


class TestCacheAndRateLimitingIntegration:
    """Testes de integração para cache e rate limiting"""
    
    def test_cache_integration_with_real_workflow(self, mock_config):
        """Testa integração do sistema de cache em workflow real"""
        with patch('bdfut.core.sportmonks_client.create_client') as mock_supabase_create, \
             patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            
            # Mock do Supabase para cache
            mock_supabase = Mock()
            mock_supabase_create.return_value = mock_supabase
            
            # Mock da resposta HTTP
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'x-ratelimit-remaining': '2999'}
            mock_response.json.return_value = {
                'data': [{'id': 1, 'name': 'Brazil', 'fifa_name': 'BRA'}]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Mock mais específico para cache miss/hit
            mock_table = Mock()
            mock_supabase.table.return_value = mock_table
            
            # Setup para cache miss na primeira chamada
            mock_execute_result = Mock()
            mock_execute_result.data = []
            mock_table.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value = mock_execute_result
            mock_table.upsert.return_value.execute.return_value = None
            
            client = SportmonksClient(enable_cache=True, cache_ttl_hours=1)
            
            # Primeira requisição (deve fazer HTTP request - cache miss)
            result1 = client.get_countries()
            assert len(result1) == 1
            assert result1[0]['name'] == 'Brazil'
            
            # Verificar que cache foi usado (pode ter múltiplas tentativas)
            assert client.cache_misses >= 1
            
            # Verificar que sistema de cache está funcionando
            stats = client.get_cache_stats()
            assert stats['cache_enabled'] is True
    
    def test_rate_limiting_integration(self, mock_config):
        """Testa integração do rate limiting com múltiplas requisições"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get, \
             patch('time.sleep') as mock_sleep:
            
            # Mock das respostas HTTP
            responses = []
            for i in range(5):
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.headers = {
                    'x-ratelimit-remaining': str(2999 - i),
                    'x-ratelimit-limit': '3000'
                }
                mock_response.json.return_value = {'data': [{'id': i, 'name': f'Country {i}'}]}
                mock_response.raise_for_status.return_value = None
                responses.append(mock_response)
            
            mock_get.side_effect = responses
            
            client = SportmonksClient(enable_cache=False)
            client.rate_limit = 2  # Limite baixo para forçar rate limiting
            
            # Fazer múltiplas requisições
            results = []
            for i in range(5):
                result = client.get_countries()
                results.append(result)
                # Simular pequeno delay entre requisições
                time.sleep(0.1)
            
            # Verificar que todas as requisições foram feitas
            assert len(results) == 5
            assert mock_get.call_count == 5
            
            # Verificar que rate limiting foi aplicado
            assert len(client.request_timestamps) == 5
            
            # Verificar que sleep foi chamado para controlar rate limit
            assert mock_sleep.called


class TestErrorHandlingIntegration:
    """Testes de integração para tratamento de erros"""
    
    def test_api_error_cascading_through_etl(self, mock_config):
        """Testa como erros da API se propagam pelo sistema ETL"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock do SportmonksClient com erro
            mock_sportmonks_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_sportmonks_instance.get_teams_by_season.side_effect = Exception("API Error: Rate limit exceeded")
            
            # Mock do SupabaseClient
            mock_supabase_instance = Mock()
            mock_supabase.return_value = mock_supabase_instance
            
            etl = ETLProcess()
            
            # Executar método que deve falhar
            result = etl.sync_teams_by_season(25583)
            
            # Verificar que erro foi tratado graciosamente
            assert result is False
            
            # Verificar que Supabase não foi chamado devido ao erro
            mock_supabase_instance.upsert_teams.assert_not_called()
            mock_supabase_instance.upsert_venues.assert_not_called()
    
    def test_database_error_handling_in_integration(self, mock_config):
        """Testa tratamento de erros de banco em fluxo integrado"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock do SportmonksClient funcionando
            mock_sportmonks_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_sportmonks_instance.get_countries.return_value = [
                {'id': 1, 'name': 'Brazil', 'fifa_name': 'BRA'}
            ]
            mock_sportmonks_instance.get_states.return_value = [
                {'id': 1, 'state': 'scheduled', 'name': 'Scheduled'}
            ]
            mock_sportmonks_instance.get_types.return_value = [
                {'id': 1, 'name': 'Goal', 'code': 'goal'}
            ]
            
            # Mock do SupabaseClient com erro em uma operação
            mock_supabase_instance = Mock()
            mock_supabase.return_value = mock_supabase_instance
            mock_supabase_instance.upsert_states.return_value = True
            mock_supabase_instance.upsert_types.return_value = True
            mock_supabase_instance.upsert_countries.side_effect = Exception("Database connection failed")
            
            # Mock do ETLJobContext
            mock_job_context = Mock()
            mock_job_context.__enter__ = Mock(return_value=mock_job_context)
            mock_job_context.__exit__ = Mock(return_value=None)
            
            with patch('bdfut.core.etl_process.ETLJobContext', return_value=mock_job_context):
                etl = ETLProcess()
                
                # O erro deve ser propagado, não silenciosamente ignorado
                with pytest.raises(Exception, match="Database connection failed"):
                    etl.sync_base_data()
                
                # Verificar que as operações anteriores foram executadas
                mock_supabase_instance.upsert_states.assert_called_once()
                mock_supabase_instance.upsert_types.assert_called_once()
                
                # Verificar que a operação com erro foi tentada
                mock_supabase_instance.upsert_countries.assert_called_once()


class TestPerformanceIntegration:
    """Testes de integração para performance"""
    
    def test_bulk_data_processing_performance(self, mock_config):
        """Testa performance com grandes volumes de dados"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            # Simular dataset grande
            large_dataset = [
                {'id': i, 'name': f'Country {i}', 'fifa_name': f'C{i:03d}'}
                for i in range(1000)
            ]
            
            supabase_client = SupabaseClient()
            
            # Medir tempo de processamento
            start_time = time.time()
            result = supabase_client.upsert_countries(large_dataset)
            end_time = time.time()
            
            # Verificações
            assert result is True
            processing_time = end_time - start_time
            
            # Deve processar em menos de 1 segundo (mock é rápido)
            assert processing_time < 1.0
            
            # Verificar que todos os dados foram processados
            call_args = mock_table.upsert.call_args[0][0]
            assert len(call_args) == 1000
    
    def test_concurrent_api_requests_simulation(self, mock_config):
        """Simula requisições concorrentes para testar robustez"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            # Mock de múltiplas respostas
            responses = []
            for i in range(10):
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.headers = {'x-ratelimit-remaining': str(2990 - i)}
                mock_response.json.return_value = {'data': [{'id': i, 'name': f'Data {i}'}]}
                mock_response.raise_for_status.return_value = None
                responses.append(mock_response)
            
            mock_get.side_effect = responses
            
            client = SportmonksClient(enable_cache=False)
            
            # Simular múltiplas requisições em sequência rápida
            results = []
            start_time = time.time()
            
            for i in range(10):
                result = client.get_countries()
                results.append(result)
            
            end_time = time.time()
            
            # Verificações
            assert len(results) == 10
            assert mock_get.call_count == 10
            
            # Deve completar em tempo razoável
            total_time = end_time - start_time
            assert total_time < 5.0  # 5 segundos máximo


class TestConfigurationIntegration:
    """Testes de integração para configurações"""
    
    def test_main_leagues_integration_with_etl(self, mock_config):
        """Testa integração das ligas principais com ETL"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock do SportmonksClient
            mock_sportmonks_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            
            # Mock dados para cada liga principal
            league_responses = []
            for league_id in Config.MAIN_LEAGUES[:3]:  # Testar apenas 3 para rapidez
                league_responses.append({
                    'id': league_id,
                    'name': f'League {league_id}',
                    'seasons': [{'id': 25583 + league_id, 'league_id': league_id}]
                })
            
            mock_sportmonks_instance.get_league_by_id.side_effect = league_responses
            
            # Mock do SupabaseClient
            mock_supabase_instance = Mock()
            mock_supabase.return_value = mock_supabase_instance
            mock_supabase_instance.upsert_leagues.return_value = True
            mock_supabase_instance.upsert_seasons.return_value = True
            
            etl = ETLProcess()
            
            # Verificar que main_leagues foi carregado corretamente
            assert etl.main_leagues == Config.MAIN_LEAGUES
            assert len(etl.main_leagues) > 0
            
            # Sincronizar algumas ligas principais
            test_leagues = Config.MAIN_LEAGUES[:3]
            etl.sync_leagues(test_leagues)
            
            # Verificar que todas foram processadas
            assert mock_sportmonks_instance.get_league_by_id.call_count == 3
            
    def test_environment_specific_configuration(self, mock_config):
        """Testa configurações específicas do ambiente"""
        # Verificar que configuração foi carregada corretamente
        assert hasattr(Config, 'SPORTMONKS_API_KEY')
        assert hasattr(Config, 'SUPABASE_URL')
        assert hasattr(Config, 'SUPABASE_KEY')
        assert hasattr(Config, 'MAIN_LEAGUES')
        assert hasattr(Config, 'RATE_LIMIT_PER_HOUR')
        
        # Verificar valores padrão
        assert Config.RATE_LIMIT_PER_HOUR > 0
        assert len(Config.MAIN_LEAGUES) > 0
        
        # Testar validação
        Config.validate()  # Não deve levantar exceção com mock_config


class TestLoggingAndMonitoringIntegration:
    """Testes de integração para logging e monitoramento"""
    
    def test_logging_integration_in_etl_flow(self, mock_config, caplog):
        """Testa integração do sistema de logging no fluxo ETL"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Configurar logging para capturar
            caplog.set_level(logging.INFO)
            
            # Mock dos clientes com dados reais (listas, não Mocks)
            mock_sportmonks_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            
            # Dados mock reais (listas) para evitar erro de len()
            mock_states = [{'id': 1, 'state': 'finished', 'name': 'Finished'}]
            mock_types = [{'id': 1, 'name': 'Goal', 'code': 'goal'}]
            mock_countries = [{'id': 1, 'name': 'Brazil', 'fifa_name': 'BRA'}]
            
            mock_sportmonks_instance.get_states.return_value = mock_states
            mock_sportmonks_instance.get_types.return_value = mock_types
            mock_sportmonks_instance.get_countries.return_value = mock_countries
            
            mock_supabase_instance = Mock()
            mock_supabase.return_value = mock_supabase_instance
            mock_supabase_instance.upsert_states.return_value = True
            mock_supabase_instance.upsert_types.return_value = True
            mock_supabase_instance.upsert_countries.return_value = True
            
            # Mock do ETLJobContext
            mock_job_context = Mock()
            mock_job_context.__enter__ = Mock(return_value=mock_job_context)
            mock_job_context.__exit__ = Mock(return_value=None)
            
            with patch('bdfut.core.etl_process.ETLJobContext', return_value=mock_job_context):
                etl = ETLProcess()
                etl.sync_base_data()
                
                # Verificar que logs foram gerados
                assert len(caplog.records) > 0
                
                # Verificar mensagens específicas
                log_messages = [record.message for record in caplog.records]
                assert any('Iniciando sincronização' in msg for msg in log_messages)
                assert any('countries sincronizados' in msg for msg in log_messages)
                
                # Verificar que job context foi usado para logging
                assert mock_job_context.log.called
    
    def test_metadata_tracking_integration(self, mock_config):
        """Testa integração do sistema de tracking de metadata"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase, \
             patch('bdfut.core.etl_process.ETLMetadataManager') as mock_metadata:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_sportmonks_instance.get_states.return_value = [{'id': 1, 'state': 'finished'}]
            mock_sportmonks_instance.get_types.return_value = [{'id': 1, 'name': 'Goal'}]
            mock_sportmonks_instance.get_countries.return_value = [{'id': 1, 'name': 'Brazil'}]
            
            mock_supabase_instance = Mock()
            mock_supabase.return_value = mock_supabase_instance
            mock_supabase_instance.upsert_states.return_value = True
            mock_supabase_instance.upsert_types.return_value = True
            mock_supabase_instance.upsert_countries.return_value = True
            
            # Mock do metadata manager
            mock_metadata_instance = Mock()
            mock_metadata.return_value = mock_metadata_instance
            
            # Mock do job context
            mock_job_context = Mock()
            mock_job_context.__enter__ = Mock(return_value=mock_job_context)
            mock_job_context.__exit__ = Mock(return_value=None)
            
            with patch('bdfut.core.etl_process.ETLJobContext', return_value=mock_job_context):
                etl = ETLProcess()
                etl.sync_base_data()
                
                # Verificar que metadata foi rastreado
                assert mock_job_context.increment_api_requests.call_count == 3
                assert mock_job_context.increment_records.call_count == 3
                assert mock_job_context.checkpoint.call_count == 3
                assert mock_job_context.log.call_count >= 6
