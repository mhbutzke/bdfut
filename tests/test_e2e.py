"""
Testes End-to-End (E2E) para BDFut
==================================

Testes que simulam cenários completos de uso do sistema,
validando workflows inteiros de ponta a ponta.

QA-003: Implementar Testes E2E
"""
import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import logging

from bdfut.core.etl_process import ETLProcess
from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
from bdfut.core.etl_metadata import ETLMetadataManager, ETLJobContext
from bdfut.config.config import Config


class TestE2ECompleteWorkflows:
    """Testes E2E para workflows completos do sistema"""
    
    def test_complete_new_project_setup_workflow(self, mock_config):
        """Testa workflow completo de setup de um novo projeto"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase, \
             patch('bdfut.core.etl_process.ETLMetadataManager') as mock_metadata:
            
            # Simular cenário: Novo projeto iniciando do zero
            print("🚀 E2E: Setup completo de novo projeto")
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_metadata_instance = Mock()
            
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            mock_metadata.return_value = mock_metadata_instance
            
            # Mock dados base completos
            mock_countries = [
                {'id': 1, 'name': 'Brazil', 'fifa_name': 'BRA'},
                {'id': 2, 'name': 'Argentina', 'fifa_name': 'ARG'},
                {'id': 3, 'name': 'England', 'fifa_name': 'ENG'}
            ]
            mock_states = [
                {'id': 1, 'state': 'scheduled', 'name': 'Scheduled'},
                {'id': 5, 'state': 'finished', 'name': 'Finished'},
                {'id': 14, 'state': 'cancelled', 'name': 'Cancelled'}
            ]
            mock_types = [
                {'id': 1, 'name': 'Goal', 'code': 'goal'},
                {'id': 2, 'name': 'Yellow Card', 'code': 'yellowcard'},
                {'id': 3, 'name': 'Red Card', 'code': 'redcard'}
            ]
            
            mock_sportmonks_instance.get_countries.return_value = mock_countries
            mock_sportmonks_instance.get_states.return_value = mock_states
            mock_sportmonks_instance.get_types.return_value = mock_types
            
            # Mock dos upserts
            mock_supabase_instance.upsert_countries.return_value = True
            mock_supabase_instance.upsert_states.return_value = True
            mock_supabase_instance.upsert_types.return_value = True
            
            # Mock do job context
            mock_job_context = Mock()
            mock_job_context.__enter__ = Mock(return_value=mock_job_context)
            mock_job_context.__exit__ = Mock(return_value=None)
            
            with patch('bdfut.core.etl_process.ETLJobContext', return_value=mock_job_context):
                # WORKFLOW COMPLETO: Setup de novo projeto
                etl = ETLProcess()
                
                # Passo 1: Sincronizar dados base
                etl.sync_base_data()
                
                # Verificar que todo o workflow base foi executado
                mock_sportmonks_instance.get_countries.assert_called_once()
                mock_sportmonks_instance.get_states.assert_called_once()
                mock_sportmonks_instance.get_types.assert_called_once()
                
                mock_supabase_instance.upsert_countries.assert_called_once_with(mock_countries)
                mock_supabase_instance.upsert_states.assert_called_once_with(mock_states)
                mock_supabase_instance.upsert_types.assert_called_once_with(mock_types)
                
                # Verificar metadata tracking
                assert mock_job_context.log.call_count >= 6
                assert mock_job_context.checkpoint.call_count == 3
                assert mock_job_context.increment_api_requests.call_count == 3
                assert mock_job_context.increment_records.call_count == 3
                
                print("✅ Workflow de setup completo executado com sucesso")
    
    def test_complete_league_synchronization_workflow(self, mock_config):
        """Testa workflow completo de sincronização de uma liga"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            print("🏆 E2E: Sincronização completa de liga (Brasil Serie A)")
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # CENÁRIO: Sincronizar Brasil Serie A completa
            brasil_serie_a_id = 648
            season_2025_id = 25583
            
            # Mock dados da liga
            mock_league_data = {
                'id': brasil_serie_a_id,
                'name': 'Brasil - Serie A',
                'country_id': 1,
                'seasons': [
                    {
                        'id': season_2025_id,
                        'league_id': brasil_serie_a_id,
                        'name': '2025',
                        'is_current': True
                    }
                ]
            }
            mock_sportmonks_instance.get_league_by_id.return_value = mock_league_data
            
            # Mock times da Serie A
            mock_teams = [
                {'id': 1, 'name': 'Palmeiras', 'venue': {'id': 1, 'name': 'Allianz Parque'}},
                {'id': 2, 'name': 'Flamengo', 'venue': {'id': 2, 'name': 'Maracanã'}},
                {'id': 3, 'name': 'São Paulo', 'venue': {'id': 3, 'name': 'Morumbi'}},
                {'id': 4, 'name': 'Corinthians', 'venue': {'id': 4, 'name': 'Neo Química Arena'}}
            ]
            mock_sportmonks_instance.get_teams_by_season.return_value = mock_teams
            
            # Mock fixtures da Serie A
            mock_fixtures = [
                {
                    'id': 1,
                    'name': 'Palmeiras vs Flamengo',
                    'starting_at': '2025-01-15T20:00:00Z',
                    'venue': {'id': 1, 'name': 'Allianz Parque'},
                    'participants': [
                        {'id': 1, 'meta': {'location': 'home'}},
                        {'id': 2, 'meta': {'location': 'away'}}
                    ],
                    'events': [
                        {'id': 1, 'minute': 23, 'type_id': 1, 'player_name': 'Dudu'},
                        {'id': 2, 'minute': 78, 'type_id': 1, 'player_name': 'Gabigol'}
                    ]
                },
                {
                    'id': 2,
                    'name': 'São Paulo vs Corinthians',
                    'starting_at': '2025-01-16T18:00:00Z',
                    'venue': {'id': 3, 'name': 'Morumbi'},
                    'participants': [
                        {'id': 3, 'meta': {'location': 'home'}},
                        {'id': 4, 'meta': {'location': 'away'}}
                    ],
                    'events': [
                        {'id': 3, 'minute': 45, 'type_id': 2, 'player_name': 'Calleri'},
                        {'id': 4, 'minute': 67, 'type_id': 1, 'player_name': 'Yuri Alberto'}
                    ]
                }
            ]
            mock_sportmonks_instance.get_fixtures_by_date_range.return_value = mock_fixtures
            
            # Mock todos os upserts
            mock_supabase_instance.upsert_leagues.return_value = True
            mock_supabase_instance.upsert_seasons.return_value = True
            mock_supabase_instance.upsert_venues.return_value = True
            mock_supabase_instance.upsert_teams.return_value = True
            mock_supabase_instance.upsert_fixtures.return_value = True
            mock_supabase_instance.upsert_fixture_participants.return_value = True
            mock_supabase_instance.upsert_fixture_events.return_value = True
            
            # WORKFLOW COMPLETO: Sincronização de liga
            etl = ETLProcess()
            
            # Passo 1: Sincronizar liga e temporadas
            etl.sync_leagues([brasil_serie_a_id])
            
            # Passo 2: Sincronizar times da temporada
            result_teams = etl.sync_teams_by_season(season_2025_id)
            assert result_teams is True
            
            # Passo 3: Sincronizar fixtures com eventos
            result_fixtures = etl.sync_fixtures_by_date_range('2025-01-15', '2025-01-16', include_details=True)
            assert result_fixtures is True
            
            # VALIDAÇÕES DO WORKFLOW COMPLETO
            
            # Verificar sincronização de liga
            mock_sportmonks_instance.get_league_by_id.assert_called_with(brasil_serie_a_id, include='seasons')
            mock_supabase_instance.upsert_leagues.assert_called()
            mock_supabase_instance.upsert_seasons.assert_called()
            
            # Verificar sincronização de times
            mock_sportmonks_instance.get_teams_by_season.assert_called_with(season_2025_id, include='venue')
            mock_supabase_instance.upsert_venues.assert_called()
            mock_supabase_instance.upsert_teams.assert_called()
            
            # Verificar sincronização de fixtures
            mock_sportmonks_instance.get_fixtures_by_date_range.assert_called()
            mock_supabase_instance.upsert_fixtures.assert_called()
            mock_supabase_instance.upsert_fixture_participants.assert_called()
            mock_supabase_instance.upsert_fixture_events.assert_called()
            
            # Validar dados processados
            fixtures_call = mock_supabase_instance.upsert_fixtures.call_args[0][0]
            assert len(fixtures_call) == 2
            assert fixtures_call[0]['name'] == 'Palmeiras vs Flamengo'
            assert fixtures_call[1]['name'] == 'São Paulo vs Corinthians'
            
            events_calls = mock_supabase_instance.upsert_fixture_events.call_args_list
            assert len(events_calls) == 2  # 2 fixtures
            
            print("✅ Workflow de sincronização de liga completo executado")
    
    def test_complete_daily_update_workflow(self, mock_config):
        """Testa workflow completo de atualização diária"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase, \
             patch('bdfut.core.etl_process.datetime') as mock_datetime:
            
            print("📅 E2E: Workflow de atualização diária")
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock data atual (15 de janeiro de 2025)
            mock_now = datetime(2025, 1, 15, 10, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.strftime = datetime.strftime
            
            # Mock fixtures do dia (ontem, hoje, amanhã)
            mock_recent_fixtures = [
                {
                    'id': 100,
                    'name': 'Manchester City vs Liverpool',
                    'starting_at': '2025-01-14T20:00:00Z',  # Ontem
                    'venue': {'id': 10, 'name': 'Etihad Stadium'},
                    'participants': [
                        {'id': 10, 'meta': {'location': 'home'}},
                        {'id': 11, 'meta': {'location': 'away'}}
                    ],
                    'events': [
                        {'id': 100, 'minute': 25, 'type_id': 1, 'player_name': 'Haaland'},
                        {'id': 101, 'minute': 58, 'type_id': 1, 'player_name': 'Salah'}
                    ]
                },
                {
                    'id': 101,
                    'name': 'Arsenal vs Chelsea',
                    'starting_at': '2025-01-15T19:30:00Z',  # Hoje
                    'venue': {'id': 11, 'name': 'Emirates Stadium'},
                    'participants': [
                        {'id': 12, 'meta': {'location': 'home'}},
                        {'id': 13, 'meta': {'location': 'away'}}
                    ],
                    'events': []  # Jogo ainda não começou
                },
                {
                    'id': 102,
                    'name': 'Real Madrid vs Barcelona',
                    'starting_at': '2025-01-16T21:00:00Z',  # Amanhã
                    'venue': {'id': 12, 'name': 'Santiago Bernabéu'},
                    'participants': [
                        {'id': 14, 'meta': {'location': 'home'}},
                        {'id': 15, 'meta': {'location': 'away'}}
                    ],
                    'events': []  # Jogo futuro
                }
            ]
            mock_sportmonks_instance.get_fixtures_by_date_range.return_value = mock_recent_fixtures
            
            # Mock todos os upserts
            mock_supabase_instance.upsert_venues.return_value = True
            mock_supabase_instance.upsert_fixtures.return_value = True
            mock_supabase_instance.upsert_fixture_participants.return_value = True
            mock_supabase_instance.upsert_fixture_events.return_value = True
            
            # WORKFLOW: Atualização diária automática
            etl = ETLProcess()
            
            # Simular execução de sync_recent_fixtures (usado em atualizações diárias)
            with patch.object(etl, 'sync_fixtures_by_date_range', wraps=etl.sync_fixtures_by_date_range) as mock_sync:
                result = etl.sync_recent_fixtures(days_back=2, days_forward=7)
                
                assert result is True
                mock_sync.assert_called_once()
                
                # Verificar que chamou com as datas corretas
                call_args = mock_sync.call_args[0]
                start_date = call_args[0]
                end_date = call_args[1]
                
                # Deve cobrir de 13/01 (2 dias atrás) até 22/01 (7 dias à frente)
                assert start_date == '2025-01-13'
                assert end_date == '2025-01-22'
            
            # Verificar processamento dos dados
            mock_supabase_instance.upsert_fixtures.assert_called()
            fixtures_call = mock_supabase_instance.upsert_fixtures.call_args[0][0]
            assert len(fixtures_call) == 3
            
            # Verificar que processou fixtures de diferentes estados
            fixture_names = [f['name'] for f in fixtures_call]
            assert 'Manchester City vs Liverpool' in fixture_names  # Jogo finalizado
            assert 'Arsenal vs Chelsea' in fixture_names  # Jogo em andamento
            assert 'Real Madrid vs Barcelona' in fixture_names  # Jogo futuro
            
            print("✅ Workflow de atualização diária completo")
    
    def test_complete_error_recovery_workflow(self, mock_config):
        """Testa workflow completo com recuperação de erros"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            print("🔧 E2E: Workflow com recuperação de erros")
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # CENÁRIO: Falha temporária na API, depois recuperação
            
            # Primeira tentativa: API falha
            mock_sportmonks_instance.get_countries.side_effect = [
                Exception("API temporarily unavailable"),  # Primeira falha
                [{'id': 1, 'name': 'Brazil', 'fifa_name': 'BRA'}]  # Segunda tentativa funciona
            ]
            
            # Mock dados para outras chamadas
            mock_sportmonks_instance.get_states.return_value = [
                {'id': 1, 'state': 'scheduled', 'name': 'Scheduled'}
            ]
            mock_sportmonks_instance.get_types.return_value = [
                {'id': 1, 'name': 'Goal', 'code': 'goal'}
            ]
            
            # Mock upserts funcionando
            mock_supabase_instance.upsert_countries.return_value = True
            mock_supabase_instance.upsert_states.return_value = True
            mock_supabase_instance.upsert_types.return_value = True
            
            # Mock job context
            mock_job_context = Mock()
            mock_job_context.__enter__ = Mock(return_value=mock_job_context)
            mock_job_context.__exit__ = Mock(return_value=None)
            
            etl = ETLProcess()
            
            # Primeira tentativa: deve falhar
            with patch('bdfut.core.etl_process.ETLJobContext', return_value=mock_job_context):
                with pytest.raises(Exception, match="API temporarily unavailable"):
                    etl.sync_base_data()
            
            # Segunda tentativa: deve funcionar
            with patch('bdfut.core.etl_process.ETLJobContext', return_value=mock_job_context):
                etl.sync_base_data()  # Agora deve funcionar
            
            # Verificar que a segunda tentativa funcionou
            assert mock_sportmonks_instance.get_countries.call_count == 2
            mock_supabase_instance.upsert_countries.assert_called_once()
            # States e types são chamados 2 vezes (primeira tentativa + segunda tentativa)
            assert mock_supabase_instance.upsert_states.call_count == 2
            assert mock_supabase_instance.upsert_types.call_count == 2
            
            print("✅ Workflow de recuperação de erros testado")


class TestE2EPerformanceScenarios:
    """Testes E2E para cenários de performance"""
    
    def test_large_dataset_processing_workflow(self, mock_config):
        """Testa workflow com grandes volumes de dados"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            
            print("📊 E2E: Processamento de grande volume de dados")
            
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            # Simular dataset grande (1000 países)
            large_countries_dataset = [
                {
                    'id': i,
                    'name': f'Country {i}',
                    'fifa_name': f'C{i:03d}',
                    'iso2': f'C{i}',
                    'iso3': f'C{i:02d}'
                }
                for i in range(1, 1001)
            ]
            
            supabase_client = SupabaseClient()
            
            # Medir performance
            start_time = time.time()
            result = supabase_client.upsert_countries(large_countries_dataset)
            end_time = time.time()
            
            # Verificações
            assert result is True
            processing_time = end_time - start_time
            
            # Deve processar em tempo razoável (menos de 2 segundos para mock)
            assert processing_time < 2.0
            
            # Verificar que todos os dados foram processados
            call_args = mock_table.upsert.call_args[0][0]
            assert len(call_args) == 1000
            
            # Verificar integridade dos dados
            assert call_args[0]['name'] == 'Country 1'
            assert call_args[999]['name'] == 'Country 1000'
            
            print(f"✅ Processou 1000 registros em {processing_time:.2f}s")
    
    def test_concurrent_operations_workflow(self, mock_config):
        """Testa workflow com operações concorrentes simuladas"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            
            print("⚡ E2E: Operações concorrentes simuladas")
            
            # Mock múltiplas respostas para simular concorrência
            responses = []
            for i in range(5):
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.headers = {'x-ratelimit-remaining': str(2995 - i)}
                mock_response.json.return_value = {
                    'data': [{'id': i + 1, 'name': f'Data {i + 1}'}]
                }
                mock_response.raise_for_status.return_value = None
                responses.append(mock_response)
            
            mock_get.side_effect = responses
            
            client = SportmonksClient(enable_cache=False)
            
            # Simular múltiplas operações em sequência rápida
            results = []
            start_time = time.time()
            
            for i in range(5):
                result = client.get_countries()
                results.append(result)
                # Simular processamento mínimo entre requisições
                time.sleep(0.01)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verificações
            assert len(results) == 5
            assert mock_get.call_count == 5
            
            # Deve completar rapidamente
            assert total_time < 1.0
            
            # Verificar rate limiting foi respeitado
            assert len(client.request_timestamps) == 5
            
            print(f"✅ 5 operações concorrentes em {total_time:.2f}s")


class TestE2ERealWorldScenarios:
    """Testes E2E para cenários do mundo real"""
    
    def test_premier_league_matchday_workflow(self, mock_config):
        """Testa workflow completo de um dia de jogos da Premier League"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            print("🏴󠁧󠁢󠁥󠁮󠁧󠁿 E2E: Dia de jogos da Premier League")
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # CENÁRIO: Sábado de Premier League com 5 jogos
            premier_league_fixtures = [
                {
                    'id': 1001,
                    'name': 'Manchester City vs Arsenal',
                    'starting_at': '2025-01-15T12:30:00Z',
                    'venue': {'id': 101, 'name': 'Etihad Stadium', 'capacity': 55017},
                    'referees': [{'id': 201, 'name': 'Michael Oliver'}],
                    'participants': [
                        {'id': 301, 'meta': {'location': 'home'}},
                        {'id': 302, 'meta': {'location': 'away'}}
                    ],
                    'events': [
                        {'id': 1001, 'minute': 15, 'type_id': 1, 'player_name': 'Haaland', 'result': '1-0'},
                        {'id': 1002, 'minute': 33, 'type_id': 1, 'player_name': 'Saka', 'result': '1-1'},
                        {'id': 1003, 'minute': 67, 'type_id': 1, 'player_name': 'De Bruyne', 'result': '2-1'}
                    ]
                },
                {
                    'id': 1002,
                    'name': 'Liverpool vs Chelsea',
                    'starting_at': '2025-01-15T15:00:00Z',
                    'venue': {'id': 102, 'name': 'Anfield', 'capacity': 54074},
                    'referees': [{'id': 202, 'name': 'Anthony Taylor'}],
                    'participants': [
                        {'id': 303, 'meta': {'location': 'home'}},
                        {'id': 304, 'meta': {'location': 'away'}}
                    ],
                    'events': [
                        {'id': 1004, 'minute': 23, 'type_id': 1, 'player_name': 'Salah', 'result': '1-0'},
                        {'id': 1005, 'minute': 45, 'type_id': 2, 'player_name': 'Sterling'},
                        {'id': 1006, 'minute': 78, 'type_id': 1, 'player_name': 'Jackson', 'result': '1-1'}
                    ]
                },
                {
                    'id': 1003,
                    'name': 'Tottenham vs Newcastle',
                    'starting_at': '2025-01-15T17:30:00Z',
                    'venue': {'id': 103, 'name': 'Tottenham Hotspur Stadium', 'capacity': 62850},
                    'referees': [{'id': 203, 'name': 'Simon Hooper'}],
                    'participants': [
                        {'id': 305, 'meta': {'location': 'home'}},
                        {'id': 306, 'meta': {'location': 'away'}}
                    ],
                    'events': [
                        {'id': 1007, 'minute': 12, 'type_id': 1, 'player_name': 'Son', 'result': '1-0'},
                        {'id': 1008, 'minute': 56, 'type_id': 1, 'player_name': 'Isak', 'result': '1-1'},
                        {'id': 1009, 'minute': 89, 'type_id': 1, 'player_name': 'Kane', 'result': '2-1'}
                    ]
                }
            ]
            
            mock_sportmonks_instance.get_fixtures_by_date_range.return_value = premier_league_fixtures
            
            # Mock todos os upserts
            mock_supabase_instance.upsert_venues.return_value = True
            mock_supabase_instance.upsert_referees.return_value = True
            mock_supabase_instance.upsert_fixtures.return_value = True
            mock_supabase_instance.upsert_fixture_participants.return_value = True
            mock_supabase_instance.upsert_fixture_events.return_value = True
            
            # WORKFLOW: Processamento de dia de jogos
            etl = ETLProcess()
            result = etl.sync_fixtures_by_date_range('2025-01-15', '2025-01-15', include_details=True)
            
            assert result is True
            
            # VALIDAÇÕES ESPECÍFICAS DO CENÁRIO
            
            # Verificar processamento de venues
            venues_call = mock_supabase_instance.upsert_venues.call_args[0][0]
            assert len(venues_call) == 3
            venue_names = [v['name'] for v in venues_call]
            assert 'Etihad Stadium' in venue_names
            assert 'Anfield' in venue_names
            assert 'Tottenham Hotspur Stadium' in venue_names
            
            # Verificar processamento de árbitros
            referees_call = mock_supabase_instance.upsert_referees.call_args[0][0]
            assert len(referees_call) == 3
            referee_names = [r['name'] for r in referees_call]
            assert 'Michael Oliver' in referee_names
            assert 'Anthony Taylor' in referee_names
            assert 'Simon Hooper' in referee_names
            
            # Verificar processamento de fixtures
            fixtures_call = mock_supabase_instance.upsert_fixtures.call_args[0][0]
            assert len(fixtures_call) == 3
            
            # Verificar eventos processados
            events_calls = mock_supabase_instance.upsert_fixture_events.call_args_list
            assert len(events_calls) == 3  # 3 fixtures
            
            # Contar total de eventos
            total_events = 0
            for call in events_calls:
                events_data = call[0][1]  # segundo argumento (events)
                total_events += len(events_data)
            
            assert total_events == 9  # 3 + 3 + 3 eventos
            
            print("✅ Dia completo de Premier League processado (3 jogos, 9 eventos)")
    
    def test_copa_libertadores_final_workflow(self, mock_config):
        """Testa workflow de final da Copa Libertadores"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            print("🏆 E2E: Final da Copa Libertadores")
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # CENÁRIO: Final da Libertadores - Palmeiras vs Flamengo
            libertadores_final = [
                {
                    'id': 2001,
                    'name': 'Palmeiras vs Flamengo - Final Copa Libertadores',
                    'starting_at': '2025-01-15T21:30:00Z',
                    'venue': {'id': 501, 'name': 'Estadio Centenario', 'capacity': 60235},
                    'referees': [
                        {'id': 401, 'name': 'Raphael Claus'},
                        {'id': 402, 'name': 'Bruno Boschilia'}  # VAR
                    ],
                    'participants': [
                        {'id': 701, 'meta': {'location': 'home'}},  # Palmeiras
                        {'id': 702, 'meta': {'location': 'away'}}   # Flamengo
                    ],
                    'events': [
                        # Primeiro tempo
                        {'id': 2001, 'minute': 12, 'type_id': 1, 'player_name': 'Dudu', 'result': '1-0'},
                        {'id': 2002, 'minute': 23, 'type_id': 2, 'player_name': 'Gerson'},
                        {'id': 2003, 'minute': 34, 'type_id': 1, 'player_name': 'Gabigol', 'result': '1-1'},
                        {'id': 2004, 'minute': 45, 'extra_minute': 2, 'type_id': 2, 'player_name': 'Zé Rafael'},
                        
                        # Segundo tempo
                        {'id': 2005, 'minute': 58, 'type_id': 1, 'player_name': 'Rony', 'result': '2-1'},
                        {'id': 2006, 'minute': 67, 'type_id': 3, 'player_name': 'David Luiz'},  # Cartão vermelho
                        {'id': 2007, 'minute': 78, 'type_id': 1, 'player_name': 'Endrick', 'result': '3-1'},
                        {'id': 2008, 'minute': 89, 'type_id': 1, 'player_name': 'Bruno Henrique', 'result': '3-2'},
                        {'id': 2009, 'minute': 90, 'extra_minute': 4, 'type_id': 1, 'player_name': 'Scarpa', 'result': '4-2'}
                    ]
                }
            ]
            
            mock_sportmonks_instance.get_fixtures_by_date_range.return_value = libertadores_final
            
            # Mock todos os upserts
            mock_supabase_instance.upsert_venues.return_value = True
            mock_supabase_instance.upsert_referees.return_value = True
            mock_supabase_instance.upsert_fixtures.return_value = True
            mock_supabase_instance.upsert_fixture_participants.return_value = True
            mock_supabase_instance.upsert_fixture_events.return_value = True
            
            # WORKFLOW: Processamento da final
            etl = ETLProcess()
            result = etl.sync_fixtures_by_date_range('2025-01-15', '2025-01-15', include_details=True)
            
            assert result is True
            
            # VALIDAÇÕES ESPECÍFICAS DA FINAL
            
            # Verificar venue especial
            venues_call = mock_supabase_instance.upsert_venues.call_args[0][0]
            assert len(venues_call) == 1
            assert venues_call[0]['name'] == 'Estadio Centenario'
            assert venues_call[0]['capacity'] == 60235
            
            # Verificar múltiplos árbitros (principal + VAR)
            referees_call = mock_supabase_instance.upsert_referees.call_args[0][0]
            assert len(referees_call) == 2
            referee_names = [r['name'] for r in referees_call]
            assert 'Raphael Claus' in referee_names
            assert 'Bruno Boschilia' in referee_names
            
            # Verificar fixture da final
            fixtures_call = mock_supabase_instance.upsert_fixtures.call_args[0][0]
            assert len(fixtures_call) == 1
            final_fixture = fixtures_call[0]
            assert 'Final Copa Libertadores' in final_fixture['name']
            
            # Verificar eventos detalhados
            events_call = mock_supabase_instance.upsert_fixture_events.call_args[0][1]
            assert len(events_call) == 9
            
            # Verificar tipos de eventos
            event_types = [e['type_id'] for e in events_call]
            assert 1 in event_types  # Gols
            assert 2 in event_types  # Cartões amarelos
            assert 3 in event_types  # Cartão vermelho
            
            # Verificar gols (6 gols no total na final)
            goals = [e for e in events_call if e['type_id'] == 1]
            assert len(goals) == 6
            
            # Verificar resultado final
            last_goal = goals[-1]
            assert last_goal['result'] == '4-2'
            assert last_goal['player_name'] == 'Scarpa'
            
            print("✅ Final da Libertadores processada (9 eventos, 6 gols, cartão vermelho)")


class TestE2EDataValidation:
    """Testes E2E para validação de dados"""
    
    def test_data_integrity_workflow(self, mock_config):
        """Testa workflow completo com validação de integridade de dados"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            print("🔍 E2E: Validação de integridade de dados")
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # CENÁRIO: Dados com possíveis inconsistências
            mock_fixture_with_validation = [
                {
                    'id': 3001,
                    'name': 'Barcelona vs Real Madrid',
                    'starting_at': '2025-01-15T20:00:00Z',
                    'venue': {
                        'id': 801,
                        'name': 'Camp Nou',
                        'capacity': 99354,
                        'city_name': 'Barcelona',
                        'country_id': 2  # Espanha
                    },
                    'referees': [
                        {
                            'id': 601,
                            'name': 'Mateu Lahoz',
                            'country_id': 2,  # Deve ser consistente
                            'date_of_birth': '1977-03-12'
                        }
                    ],
                    'participants': [
                        {
                            'id': 801,  # Barcelona
                            'meta': {'location': 'home'},
                            'name': 'FC Barcelona',
                            'country_id': 2  # Consistente com venue
                        },
                        {
                            'id': 802,  # Real Madrid
                            'meta': {'location': 'away'},
                            'name': 'Real Madrid CF',
                            'country_id': 2  # Também da Espanha
                        }
                    ],
                    'events': [
                        {
                            'id': 3001,
                            'minute': 25,
                            'type_id': 1,
                            'player_name': 'Pedri',
                            'participant_id': 801,  # Barcelona
                            'result': '1-0'
                        },
                        {
                            'id': 3002,
                            'minute': 67,
                            'type_id': 1,
                            'player_name': 'Vinícius Jr.',
                            'participant_id': 802,  # Real Madrid
                            'result': '1-1'
                        },
                        {
                            'id': 3003,
                            'minute': 89,
                            'type_id': 1,
                            'player_name': 'Lewandowski',
                            'participant_id': 801,  # Barcelona
                            'result': '2-1'
                        }
                    ]
                }
            ]
            
            mock_sportmonks_instance.get_fixtures_by_date_range.return_value = mock_fixture_with_validation
            
            # Mock upserts com validação
            def validate_and_upsert_venues(venues):
                # Validar dados de venue
                for venue in venues:
                    assert 'id' in venue
                    assert 'name' in venue
                    assert venue['capacity'] > 0
                    assert venue['country_id'] is not None
                return True
            
            def validate_and_upsert_referees(referees):
                # Validar dados de árbitros
                for referee in referees:
                    assert 'id' in referee
                    assert 'name' in referee
                    assert 'country_id' in referee
                    # Validar formato de data de nascimento
                    if 'date_of_birth' in referee:
                        assert len(referee['date_of_birth']) == 10  # YYYY-MM-DD
                return True
            
            def validate_and_upsert_events(fixture_id, events):
                # Validar eventos
                for event in events:
                    assert 'id' in event
                    assert 'minute' in event
                    assert event['minute'] > 0 and event['minute'] <= 90
                    assert 'type_id' in event
                    assert 'participant_id' in event
                    
                    # Validar gols têm resultado
                    if event['type_id'] == 1:  # Gol
                        assert 'result' in event
                        assert 'player_name' in event
                return True
            
            mock_supabase_instance.upsert_venues.side_effect = validate_and_upsert_venues
            mock_supabase_instance.upsert_referees.side_effect = validate_and_upsert_referees
            mock_supabase_instance.upsert_fixtures.return_value = True
            mock_supabase_instance.upsert_fixture_participants.return_value = True
            mock_supabase_instance.upsert_fixture_events.side_effect = validate_and_upsert_events
            
            # WORKFLOW: Processamento com validação
            etl = ETLProcess()
            result = etl.sync_fixtures_by_date_range('2025-01-15', '2025-01-15', include_details=True)
            
            assert result is True
            
            # VALIDAÇÕES ESPECÍFICAS DE INTEGRIDADE
            
            # Verificar que todas as validações passaram
            mock_supabase_instance.upsert_venues.assert_called_once()
            mock_supabase_instance.upsert_referees.assert_called_once()
            mock_supabase_instance.upsert_fixtures.assert_called_once()
            mock_supabase_instance.upsert_fixture_participants.assert_called_once()
            mock_supabase_instance.upsert_fixture_events.assert_called_once()
            
            # Verificar dados específicos
            venues_call = mock_supabase_instance.upsert_venues.call_args[0][0]
            venue = venues_call[0]
            assert venue['name'] == 'Camp Nou'
            assert venue['capacity'] == 99354
            assert venue['country_id'] == 2
            
            referees_call = mock_supabase_instance.upsert_referees.call_args[0][0]
            referee = referees_call[0]
            assert referee['name'] == 'Mateu Lahoz'
            assert referee['country_id'] == 2
            assert referee['date_of_birth'] == '1977-03-12'
            
            events_call = mock_supabase_instance.upsert_fixture_events.call_args[0][1]
            assert len(events_call) == 3
            
            # Verificar consistência dos gols
            goals = [e for e in events_call if e['type_id'] == 1]
            assert len(goals) == 3
            assert goals[0]['result'] == '1-0'
            assert goals[1]['result'] == '1-1'
            assert goals[2]['result'] == '2-1'  # Resultado final
            
            print("✅ Validação de integridade completa (El Clasico processado)")
    
    def test_configuration_validation_workflow(self, mock_config):
        """Testa workflow de validação de configuração completa"""
        print("⚙️ E2E: Validação completa de configuração")
        
        # Testar todas as configurações necessárias
        required_configs = [
            'SPORTMONKS_API_KEY',
            'SUPABASE_URL',
            'SUPABASE_KEY',
            'MAIN_LEAGUES',
            'RATE_LIMIT_PER_HOUR'
        ]
        
        for config_name in required_configs:
            assert hasattr(Config, config_name), f"Configuração {config_name} não encontrada"
            config_value = getattr(Config, config_name)
            assert config_value is not None, f"Configuração {config_name} está vazia"
        
        # Testar validação específica
        Config.validate()  # Não deve levantar exceção
        
        # Testar ligas principais
        assert len(Config.MAIN_LEAGUES) > 0
        assert isinstance(Config.MAIN_LEAGUES, list)
        assert all(isinstance(league_id, int) for league_id in Config.MAIN_LEAGUES)
        
        # Testar rate limit
        assert Config.RATE_LIMIT_PER_HOUR > 0
        assert isinstance(Config.RATE_LIMIT_PER_HOUR, int)
        
        # Testar método auxiliar
        leagues_str = Config.get_main_leagues_str()
        assert isinstance(leagues_str, str)
        assert len(leagues_str) > 0
        assert ',' in leagues_str  # Deve ter vírgulas separando IDs
        
        print("✅ Configuração validada completamente")
