"""
Testes adicionais para melhorar cobertura dos módulos core
=========================================================

Testes para métodos e cenários não cobertos pelos testes existentes,
focando em atingir a meta de 60% de cobertura.
"""
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
from bdfut.core.etl_process import ETLProcess
from bdfut.config.config import Config


class TestSportmonksClientAdditional:
    """Testes adicionais para SportmonksClient"""
    
    def test_get_countries_success(self, mock_config):
        """Testa obtenção de países com sucesso"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            # Mock da resposta
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'x-ratelimit-remaining': '2999'}
            mock_response.json.return_value = {
                'data': [
                    {'id': 1, 'name': 'Brazil', 'fifa_name': 'BRA'},
                    {'id': 2, 'name': 'Argentina', 'fifa_name': 'ARG'}
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            client = SportmonksClient(enable_cache=False)
            countries = client.get_countries()
            
            assert len(countries) == 2
            assert countries[0]['name'] == 'Brazil'
            assert countries[1]['name'] == 'Argentina'
    
    def test_get_states_success(self, mock_config):
        """Testa obtenção de estados com sucesso"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            # Mock da resposta
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'x-ratelimit-remaining': '2999'}
            mock_response.json.return_value = {
                'data': [
                    {'id': 1, 'state': 'scheduled', 'name': 'Scheduled'},
                    {'id': 5, 'state': 'finished', 'name': 'Finished'}
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            client = SportmonksClient(enable_cache=False)
            states = client.get_states()
            
            assert len(states) == 2
            assert states[0]['state'] == 'scheduled'
            assert states[1]['state'] == 'finished'
    
    def test_get_types_success(self, mock_config):
        """Testa obtenção de tipos com sucesso"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            # Mock da resposta
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'x-ratelimit-remaining': '2999'}
            mock_response.json.return_value = {
                'data': [
                    {'id': 1, 'name': 'Goal', 'code': 'goal'},
                    {'id': 2, 'name': 'Yellow Card', 'code': 'yellowcard'}
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            client = SportmonksClient(enable_cache=False)
            types = client.get_types()
            
            assert len(types) == 2
            assert types[0]['name'] == 'Goal'
            assert types[1]['name'] == 'Yellow Card'
    
    def test_get_league_by_id_success(self, mock_config):
        """Testa obtenção de liga por ID com sucesso"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            # Mock da resposta
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'x-ratelimit-remaining': '2999'}
            mock_response.json.return_value = {
                'data': {
                    'id': 8,
                    'name': 'Premier League',
                    'country_id': 1,
                    'seasons': [
                        {'id': 25583, 'name': '2025/2026'}
                    ]
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            client = SportmonksClient(enable_cache=False)
            league = client.get_league_by_id(8, include='seasons')
            
            assert league['id'] == 8
            assert league['name'] == 'Premier League'
            assert len(league['seasons']) == 1
    
    def test_get_teams_by_season_success(self, mock_config):
        """Testa obtenção de times por temporada com sucesso"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            # Mock da resposta
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'x-ratelimit-remaining': '2999'}
            mock_response.json.return_value = {
                'data': [
                    {
                        'id': 1,
                        'name': 'Manchester City',
                        'venue': {'id': 1, 'name': 'Etihad Stadium'}
                    }
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            client = SportmonksClient(enable_cache=False)
            teams = client.get_teams_by_season(25583, include='venue')
            
            assert len(teams) == 1
            assert teams[0]['name'] == 'Manchester City'
            assert teams[0]['venue']['name'] == 'Etihad Stadium'
    
    def test_get_fixture_by_id_success(self, mock_config):
        """Testa obtenção de partida por ID com sucesso"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            # Mock da resposta
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'x-ratelimit-remaining': '2999'}
            mock_response.json.return_value = {
                'data': {
                    'id': 1,
                    'name': 'Manchester City vs Liverpool',
                    'venue': {'id': 1, 'name': 'Etihad Stadium'},
                    'participants': [
                        {'id': 1, 'meta': {'location': 'home'}},
                        {'id': 2, 'meta': {'location': 'away'}}
                    ],
                    'events': [
                        {'id': 1, 'minute': 15, 'type_id': 1}
                    ]
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            client = SportmonksClient(enable_cache=False)
            fixture = client.get_fixture_by_id(1, include='venue,participants,events')
            
            assert fixture['id'] == 1
            assert fixture['name'] == 'Manchester City vs Liverpool'
            assert len(fixture['participants']) == 2
            assert len(fixture['events']) == 1
    
    def test_request_error_handling(self, mock_config):
        """Testa tratamento de erro em requisições"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            # Mock de erro de conexão
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            client = SportmonksClient(enable_cache=False)
            
            with pytest.raises(Exception):
                client.get_countries()


class TestSupabaseClientAdditional:
    """Testes adicionais para SupabaseClient"""
    
    def test_init_with_config_validation(self, mock_config):
        """Testa inicialização com validação de config"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            assert client.client == mock_client
            # Verificar que create_client foi chamado (sem verificar argumentos específicos)
            mock_create.assert_called_once()
    
    def test_upsert_with_empty_data(self, mock_config):
        """Testa upsert com dados vazios"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            # Testar com lista vazia
            result = client.upsert_countries([])
            assert result is True
            
            # Verificar que upsert foi chamado com lista vazia
            mock_table.upsert.assert_called_once_with([], on_conflict='id')
    
    def test_upsert_leagues_with_all_fields(self, mock_config):
        """Testa upsert de ligas com todos os campos"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            leagues_data = [
                {
                    'id': 8,
                    'sport_id': 1,
                    'country_id': 1,
                    'name': 'Premier League',
                    'active': True,
                    'short_code': 'EPL',
                    'image_path': '/leagues/premier.png',
                    'type': 'league',
                    'sub_type': 'first_tier',
                    'last_played_at': '2025-01-15T10:00:00Z',
                    'category': 1,
                    'has_jerseys': True,
                    'has_standings': True
                }
            ]
            
            result = client.upsert_leagues(leagues_data)
            
            assert result is True
            mock_table.upsert.assert_called_once()
            
            # Verificar dados processados
            call_args = mock_table.upsert.call_args[0][0]
            assert len(call_args) == 1
            assert call_args[0]['name'] == 'Premier League'
            assert call_args[0]['active'] is True
    
    def test_data_cleaning_and_validation(self, mock_config):
        """Testa limpeza e validação de dados"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            # Dados com valores None e campos ausentes
            dirty_data = [
                {
                    'id': 1,
                    'name': None,  # Valor None
                    'active': 'true',  # String ao invés de bool
                    # 'country_id' ausente
                }
            ]
            
            result = client.upsert_leagues(dirty_data)
            
            assert result is True
            # Verificar que dados foram limpos
            call_args = mock_table.upsert.call_args[0][0]
            assert call_args[0]['name'] is None
            assert 'country_id' in call_args[0]  # Campo adicionado como None


class TestETLProcessAdditional:
    """Testes adicionais para ETLProcess"""
    
    def test_init_with_config(self, mock_config):
        """Testa inicialização com configuração"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase, \
             patch('bdfut.core.etl_process.ETLMetadataManager') as mock_metadata:
            
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_metadata_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            mock_metadata.return_value = mock_metadata_instance
            
            etl = ETLProcess()
            
            assert etl.sportmonks == mock_sportmonks_instance
            assert etl.supabase == mock_supabase_instance
            assert etl.metadata_manager == mock_metadata_instance
            assert hasattr(etl, 'main_leagues')
    
    def test_sync_leagues_with_multiple_leagues(self, mock_config):
        """Testa sincronização de múltiplas ligas"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dos dados retornados para múltiplas ligas
            league_data = [
                {
                    'id': 8,
                    'name': 'Premier League',
                    'seasons': [{'id': 25583, 'league_id': 8, 'name': '2025/2026'}]
                },
                {
                    'id': 564,
                    'name': 'La Liga',
                    'seasons': [{'id': 25584, 'league_id': 564, 'name': '2025/2026'}]
                }
            ]
            
            mock_sportmonks_instance.get_league_by_id.side_effect = league_data
            mock_supabase_instance.upsert_leagues.return_value = True
            mock_supabase_instance.upsert_seasons.return_value = True
            
            etl = ETLProcess()
            etl.sync_leagues([8, 564])  # Lista de IDs de ligas
            
            # Verificar que ambas as ligas foram processadas
            assert mock_sportmonks_instance.get_league_by_id.call_count == 2
            # O método sync_leagues processa todas as ligas de uma vez
            assert mock_supabase_instance.upsert_leagues.call_count >= 1
            assert mock_supabase_instance.upsert_seasons.call_count >= 1
    
    def test_sync_teams_error_handling(self, mock_config):
        """Testa tratamento de erro na sincronização de times"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock de erro na API
            mock_sportmonks_instance.get_teams_by_season.side_effect = Exception("API Error")
            
            etl = ETLProcess()
            result = etl.sync_teams_by_season(25583)
            
            assert result is False
    
    def test_sync_fixtures_with_details(self, mock_config):
        """Testa sincronização de partidas com detalhes completos"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dos dados retornados com detalhes completos
            mock_fixtures = [
                {
                    'id': 1,
                    'name': 'Manchester City vs Liverpool',
                    'starting_at': '2025-01-15T15:00:00Z',
                    'venue': {'id': 1, 'name': 'Etihad Stadium', 'capacity': 55017},
                    'referees': [{'id': 1, 'name': 'Mike Dean'}],
                    'participants': [
                        {'id': 1, 'meta': {'location': 'home'}},
                        {'id': 2, 'meta': {'location': 'away'}}
                    ],
                    'events': [
                        {'id': 1, 'minute': 15, 'type_id': 1, 'player_name': 'Haaland'}
                    ]
                }
            ]
            mock_sportmonks_instance.get_fixtures_by_date_range.return_value = mock_fixtures
            
            # Mock dos upserts
            mock_supabase_instance.upsert_venues.return_value = True
            mock_supabase_instance.upsert_referees.return_value = True
            mock_supabase_instance.upsert_fixtures.return_value = True
            mock_supabase_instance.upsert_fixture_participants.return_value = True
            mock_supabase_instance.upsert_fixture_events.return_value = True
            
            etl = ETLProcess()
            result = etl.sync_fixtures_by_date_range('2025-01-15', '2025-01-15', include_details=True)
            
            assert result is True
            
            # Verificar que todos os upserts foram chamados
            mock_supabase_instance.upsert_venues.assert_called_once()
            mock_supabase_instance.upsert_referees.assert_called_once()
            mock_supabase_instance.upsert_fixtures.assert_called_once()
            mock_supabase_instance.upsert_fixture_participants.assert_called_once()
            mock_supabase_instance.upsert_fixture_events.assert_called_once()


class TestConfigValidation:
    """Testes para validação de configuração"""
    
    def test_config_validation_missing_keys(self):
        """Testa validação de configuração com chaves ausentes"""
        with patch('bdfut.config.config.Config.SPORTMONKS_API_KEY', None):
            with pytest.raises(ValueError, match="SPORTMONKS_API_KEY"):
                Config.validate()
    
    def test_config_validation_success(self, mock_config):
        """Testa validação de configuração com sucesso"""
        # Não deve levantar exceção
        Config.validate()


class TestErrorScenarios:
    """Testes para cenários de erro"""
    
    def test_network_timeout_handling(self, mock_config):
        """Testa tratamento de timeout de rede"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
            
            client = SportmonksClient(enable_cache=False)
            
            with pytest.raises(Exception):
                client.get_countries()
    
    def test_invalid_json_response(self, mock_config):
        """Testa tratamento de resposta JSON inválida"""
        with patch('bdfut.core.sportmonks_client.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'x-ratelimit-remaining': '2999'}
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            client = SportmonksClient(enable_cache=False)
            
            # O cliente usa retry, então esperamos RetryError
            from tenacity import RetryError
            with pytest.raises(RetryError):
                client.get_countries()
    
    def test_database_connection_error(self, mock_config):
        """Testa tratamento de erro de conexão com banco"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_create.side_effect = Exception("Database connection failed")
            
            with pytest.raises(Exception):
                SupabaseClient()


class TestPerformanceScenarios:
    """Testes para cenários de performance"""
    
    def test_large_dataset_processing(self, mock_config):
        """Testa processamento de grandes datasets"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            # Simular dataset grande (1000 registros)
            large_dataset = [
                {'id': i, 'name': f'Country {i}', 'fifa_name': f'C{i:03d}'}
                for i in range(1000)
            ]
            
            result = client.upsert_countries(large_dataset)
            
            assert result is True
            mock_table.upsert.assert_called_once()
            
            # Verificar que todos os registros foram processados
            call_args = mock_table.upsert.call_args[0][0]
            assert len(call_args) == 1000
