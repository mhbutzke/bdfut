"""
Testes unitários para SupabaseClient
===================================

Testes abrangentes para o cliente Supabase com foco em:
- Operações de upsert
- Validação de dados
- Tratamento de erros
- Integridade referencial
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from bdfut.core.supabase_client import SupabaseClient


class TestSupabaseClient:
    """Testes para SupabaseClient"""
    
    def test_init_success(self, mock_config):
        """Testa inicialização bem-sucedida"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            assert client.client == mock_client
            mock_create.assert_called_once()
    
    def test_upsert_countries_success(self, mock_config):
        """Testa upsert de países com sucesso"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            countries_data = [
                {
                    'id': 1,
                    'name': 'Brazil',
                    'official_name': 'Federative Republic of Brazil',
                    'fifa_name': 'BRA',
                    'iso2': 'BR',
                    'iso3': 'BRA',
                    'latitude': -14.235,
                    'longitude': -51.9253,
                    'borders': ['ARG', 'BOL', 'COL'],
                    'image_path': '/flags/brazil.png'
                }
            ]
            
            result = client.upsert_countries(countries_data)
            
            assert result is True
            mock_table.upsert.assert_called_once()
    
    def test_upsert_countries_with_schema_fallback(self, mock_config):
        """Testa upsert de países com fallback de schema"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            
            # Primeira chamada falha, segunda sucede
            mock_table.upsert.side_effect = [Exception("Schema not found"), None]
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            countries_data = [{'id': 1, 'name': 'Brazil'}]
            result = client.upsert_countries(countries_data)
            
            assert result is True
            assert mock_table.upsert.call_count == 2
    
    def test_upsert_countries_error_handling(self, mock_config):
        """Testa tratamento de erro no upsert de países"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_table.upsert.side_effect = Exception("Database error")
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            countries_data = [{'id': 1, 'name': 'Brazil'}]
            result = client.upsert_countries(countries_data)
            
            assert result is False
    
    def test_upsert_leagues_success(self, mock_config):
        """Testa upsert de ligas com sucesso"""
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
    
    def test_upsert_seasons_success(self, mock_config):
        """Testa upsert de temporadas com sucesso"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            seasons_data = [
                {
                    'id': 25583,
                    'sport_id': 1,
                    'league_id': 8,
                    'name': '2025/2026',
                    'finished': False,
                    'pending': False,
                    'is_current': True,
                    'starting_at': '2025-08-15T00:00:00Z',
                    'ending_at': '2026-05-31T23:59:59Z',
                    'standings_recalculated_at': '2025-01-15T10:00:00Z',
                    'games_in_current_week': True
                }
            ]
            
            result = client.upsert_seasons(seasons_data)
            
            assert result is True
            mock_table.upsert.assert_called_once()
    
    def test_upsert_teams_success(self, mock_config):
        """Testa upsert de times com sucesso"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            teams_data = [
                {
                    'id': 1,
                    'sport_id': 1,
                    'country_id': 1,
                    'venue_id': 1,
                    'name': 'Manchester City',
                    'short_code': 'MCI',
                    'twitter': '@ManCity',
                    'founded': 1880,
                    'logo_path': '/teams/mancity.png',
                    'is_national_team': False
                }
            ]
            
            result = client.upsert_teams(teams_data)
            
            assert result is True
            mock_table.upsert.assert_called_once()
    
    def test_upsert_venues_success(self, mock_config):
        """Testa upsert de estádios com sucesso"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            venues_data = [
                {
                    'id': 1,
                    'country_id': 1,
                    'city_id': 1,
                    'name': 'Etihad Stadium',
                    'address': 'SportCity, Manchester M11 3FF',
                    'zipcode': 'M11 3FF',
                    'latitude': 53.4831,
                    'longitude': -2.2004,
                    'capacity': 55017,
                    'image_path': '/venues/etihad.png',
                    'city_name': 'Manchester',
                    'surface': 'grass',
                    'national_team': False
                }
            ]
            
            result = client.upsert_venues(venues_data)
            
            assert result is True
            mock_table.upsert.assert_called_once()
    
    def test_upsert_referees_success(self, mock_config):
        """Testa upsert de árbitros com sucesso"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            referees_data = [
                {
                    'id': 1,
                    'sport_id': 1,
                    'country_id': 1,
                    'city_id': 1,
                    'common_name': 'Mike Dean',
                    'firstname': 'Mike',
                    'lastname': 'Dean',
                    'name': 'Mike Dean',
                    'display_name': 'M. Dean',
                    'image_path': '/referees/dean.png',
                    'height': 180,
                    'weight': 75,
                    'date_of_birth': '1968-06-02',
                    'gender': 'male'
                }
            ]
            
            result = client.upsert_referees(referees_data)
            
            assert result is True
            mock_table.upsert.assert_called_once()
    
    def test_upsert_fixtures_success(self, mock_config):
        """Testa upsert de partidas com sucesso"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            fixtures_data = [
                {
                    'id': 1,
                    'sport_id': 1,
                    'league_id': 8,
                    'season_id': 25583,
                    'stage_id': 1,
                    'group_id': None,
                    'aggregate_id': None,
                    'round_id': 1,
                    'state_id': 5,
                    'venue_id': 1,
                    'name': 'Manchester City vs Liverpool',
                    'starting_at': '2025-01-15T15:00:00Z',
                    'result_info': 'Game ended in draw.',
                    'leg': '1/1',
                    'details': None,
                    'length': 90,
                    'placeholder': False,
                    'has_odds': True
                }
            ]
            
            result = client.upsert_fixtures(fixtures_data)
            
            assert result is True
            mock_table.upsert.assert_called_once()
    
    def test_upsert_fixture_participants_success(self, mock_config):
        """Testa upsert de participantes de partida com sucesso"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_delete = Mock()
            mock_insert = Mock()
            
            mock_table.delete.return_value.eq.return_value.execute.return_value = mock_delete
            mock_table.insert.return_value.execute.return_value = mock_insert
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            participants_data = [
                {
                    'id': 1,
                    'meta': {'location': 'home'}
                },
                {
                    'id': 2,
                    'meta': {'location': 'away'}
                }
            ]
            
            result = client.upsert_fixture_participants(123, participants_data)
            
            assert result is True
            mock_table.delete.assert_called_once()
            mock_table.insert.assert_called_once()
    
    def test_upsert_fixture_events_success(self, mock_config):
        """Testa upsert de eventos de partida com sucesso"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            events_data = [
                {
                    'id': 1,
                    'period_id': 1,
                    'participant_id': 1,
                    'type_id': 1,
                    'player_id': 1,
                    'related_player_id': None,
                    'player_name': 'Erling Haaland',
                    'related_player_name': None,
                    'result': '1-0',
                    'info': 'Goal',
                    'addition': None,
                    'minute': 15,
                    'extra_minute': None,
                    'injured': False,
                    'on_bench': False
                }
            ]
            
            result = client.upsert_fixture_events(123, events_data)
            
            assert result is True
            mock_table.upsert.assert_called_once()
    
    def test_upsert_states_success(self, mock_config):
        """Testa upsert de estados com sucesso"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            states_data = [
                {
                    'id': 5,
                    'state': 'finished',
                    'name': 'Finished',
                    'short_name': 'FT',
                    'developer_name': 'finished'
                }
            ]
            
            result = client.upsert_states(states_data)
            
            assert result is True
            mock_table.upsert.assert_called_once()
    
    def test_upsert_types_success(self, mock_config):
        """Testa upsert de tipos com sucesso"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            types_data = [
                {
                    'id': 1,
                    'name': 'Goal',
                    'code': 'goal',
                    'developer_name': 'goal',
                    'model_type': 'event',
                    'stat_group': 'goals'
                }
            ]
            
            result = client.upsert_types(types_data)
            
            assert result is True
            mock_table.upsert.assert_called_once()
    
    def test_data_validation_missing_fields(self, mock_config):
        """Testa validação de dados com campos ausentes"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            # Dados com campos ausentes
            incomplete_data = [
                {
                    'id': 1,
                    # 'name' ausente
                    'active': True
                }
            ]
            
            result = client.upsert_leagues(incomplete_data)
            
            assert result is True
            # Verificar se campos ausentes foram tratados
            call_args = mock_table.upsert.call_args[0][0]
            assert call_args[0]['name'] is None
    
    def test_data_validation_type_conversion(self, mock_config):
        """Testa conversão de tipos de dados"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            # Dados com tipos incorretos
            data_with_wrong_types = [
                {
                    'id': '1',  # String ao invés de int
                    'active': 'true',  # String ao invés de bool
                    'has_jerseys': 1,  # Int ao invés de bool
                    'borders': ['ARG', 'BOL']  # Lista que será convertida para string
                }
            ]
            
            result = client.upsert_countries(data_with_wrong_types)
            
            assert result is True
            # Verificar se tipos foram convertidos corretamente
            call_args = mock_table.upsert.call_args[0][0]
            assert call_args[0]['id'] == '1'  # Mantém como string
            assert call_args[0]['borders'] == "['ARG', 'BOL']"  # Convertido para string


class TestSupabaseClientErrorHandling:
    """Testes de tratamento de erro para SupabaseClient"""
    
    def test_all_upsert_methods_error_handling(self, mock_config):
        """Testa tratamento de erro em todos os métodos upsert"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_table.upsert.side_effect = Exception("Database connection failed")
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            test_data = [{'id': 1, 'name': 'Test'}]
            
            # Testar todos os métodos upsert
            methods_to_test = [
                ('upsert_countries', test_data),
                ('upsert_leagues', test_data),
                ('upsert_seasons', test_data),
                ('upsert_teams', test_data),
                ('upsert_venues', test_data),
                ('upsert_referees', test_data),
                ('upsert_fixtures', test_data),
                ('upsert_states', test_data),
                ('upsert_types', test_data)
            ]
            
            for method_name, data in methods_to_test:
                method = getattr(client, method_name)
                result = method(data)
                assert result is False, f"{method_name} should return False on error"
    
    def test_fixture_participants_error_handling(self, mock_config):
        """Testa tratamento de erro no upsert de participantes"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_table.delete.side_effect = Exception("Delete failed")
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            participants_data = [{'id': 1, 'meta': {'location': 'home'}}]
            result = client.upsert_fixture_participants(123, participants_data)
            
            assert result is False
    
    def test_fixture_events_error_handling(self, mock_config):
        """Testa tratamento de erro no upsert de eventos"""
        with patch('bdfut.core.supabase_client.create_client') as mock_create:
            mock_client = Mock()
            mock_table = Mock()
            mock_table.upsert.side_effect = Exception("Upsert failed")
            mock_client.table.return_value = mock_table
            mock_create.return_value = mock_client
            
            client = SupabaseClient()
            
            events_data = [{'id': 1, 'minute': 15}]
            result = client.upsert_fixture_events(123, events_data)
            
            assert result is False
