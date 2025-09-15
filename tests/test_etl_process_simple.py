"""
Testes unitários simplificados para ETLProcess
==============================================

Testes focados nos métodos que realmente existem no ETLProcess
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from bdfut.core.etl_process import ETLProcess


class TestETLProcessSimple:
    """Testes simplificados para ETLProcess"""
    
    def test_init_success(self, mock_config):
        """Testa inicialização bem-sucedida"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            etl = ETLProcess()
            
            assert etl.sportmonks == mock_sportmonks_instance
            assert etl.supabase == mock_supabase_instance
            mock_sportmonks.assert_called_once()
            mock_supabase.assert_called_once()
    
    def test_sync_base_data_success(self, mock_config):
        """Testa sincronização de dados base com sucesso"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dos dados retornados
            mock_sportmonks_instance.get_countries.return_value = [
                {'id': 1, 'name': 'Brazil', 'fifa_name': 'BRA'}
            ]
            mock_sportmonks_instance.get_states.return_value = [
                {'id': 5, 'state': 'finished', 'name': 'Finished'}
            ]
            mock_sportmonks_instance.get_types.return_value = [
                {'id': 1, 'name': 'Goal', 'code': 'goal'}
            ]
            
            # Mock dos upserts
            mock_supabase_instance.upsert_countries.return_value = True
            mock_supabase_instance.upsert_states.return_value = True
            mock_supabase_instance.upsert_types.return_value = True
            
            etl = ETLProcess()
            etl.sync_base_data()  # Método não retorna valor
            
            mock_sportmonks_instance.get_countries.assert_called_once()
            mock_sportmonks_instance.get_states.assert_called_once()
            mock_sportmonks_instance.get_types.assert_called_once()
            mock_supabase_instance.upsert_countries.assert_called_once()
            mock_supabase_instance.upsert_states.assert_called_once()
            mock_supabase_instance.upsert_types.assert_called_once()
    
    def test_sync_leagues_success(self, mock_config):
        """Testa sincronização de ligas com sucesso"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dos dados retornados
            mock_league = {
                'id': 8,
                'name': 'Premier League',
                'seasons': [
                    {'id': 25583, 'league_id': 8, 'name': '2025/2026'}
                ]
            }
            mock_sportmonks_instance.get_league_by_id.return_value = mock_league
            
            # Mock dos upserts
            mock_supabase_instance.upsert_leagues.return_value = True
            mock_supabase_instance.upsert_seasons.return_value = True
            
            etl = ETLProcess()
            etl.sync_leagues([8])  # Lista de IDs de ligas
            
            mock_sportmonks_instance.get_league_by_id.assert_called_once_with(8, include='seasons')
            mock_supabase_instance.upsert_leagues.assert_called_once()
            mock_supabase_instance.upsert_seasons.assert_called_once()
    
    def test_sync_teams_by_season_success(self, mock_config):
        """Testa sincronização de times por temporada com sucesso"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dos dados retornados
            mock_teams = [
                {
                    'id': 1,
                    'name': 'Manchester City',
                    'venue': {'id': 1, 'name': 'Etihad Stadium', 'capacity': 55017}
                }
            ]
            mock_sportmonks_instance.get_teams_by_season.return_value = mock_teams
            
            # Mock dos upserts
            mock_supabase_instance.upsert_venues.return_value = True
            mock_supabase_instance.upsert_teams.return_value = True
            
            etl = ETLProcess()
            result = etl.sync_teams_by_season(25583)
            
            assert result is True
            mock_sportmonks_instance.get_teams_by_season.assert_called_once_with(25583, include='venue')
            mock_supabase_instance.upsert_venues.assert_called_once()
            mock_supabase_instance.upsert_teams.assert_called_once()
    
    def test_sync_fixtures_by_date_range_success(self, mock_config):
        """Testa sincronização de partidas por intervalo de datas com sucesso"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dos dados retornados
            mock_fixture = {
                'id': 1,
                'name': 'Manchester City vs Liverpool',
                'starting_at': '2025-01-15T15:00:00Z',
                'venue': {'id': 1, 'name': 'Etihad Stadium'},
                'participants': [
                    {'id': 1, 'meta': {'location': 'home'}},
                    {'id': 2, 'meta': {'location': 'away'}}
                ],
                'events': [
                    {'id': 1, 'minute': 15, 'type_id': 1}
                ]
            }
            mock_sportmonks_instance.get_fixtures_by_date_range.return_value = [mock_fixture]
            
            # Mock dos upserts
            mock_supabase_instance.upsert_venues.return_value = True
            mock_supabase_instance.upsert_fixtures.return_value = True
            mock_supabase_instance.upsert_fixture_participants.return_value = True
            mock_supabase_instance.upsert_fixture_events.return_value = True
            
            etl = ETLProcess()
            result = etl.sync_fixtures_by_date_range('2025-01-15', '2025-01-15', include_details=True)
            
            assert result is True
            mock_sportmonks_instance.get_fixtures_by_date_range.assert_called_once()
            mock_supabase_instance.upsert_venues.assert_called_once()
            mock_supabase_instance.upsert_fixtures.assert_called_once()
            mock_supabase_instance.upsert_fixture_participants.assert_called_once()
            mock_supabase_instance.upsert_fixture_events.assert_called_once()
    
    def test_sync_recent_fixtures_success(self, mock_config):
        """Testa sincronização de partidas recentes com sucesso"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase, \
             patch('bdfut.core.etl_process.datetime') as mock_datetime:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock da data atual
            mock_now = datetime(2025, 1, 15, 10, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.strftime = datetime.strftime
            
            # Mock do método sync_fixtures_by_date_range
            with patch.object(ETLProcess, 'sync_fixtures_by_date_range', return_value=True) as mock_sync:
                etl = ETLProcess()
                result = etl.sync_recent_fixtures(days_back=7, days_forward=7)
                
                assert result is True
                mock_sync.assert_called_once()
    
    def test_sync_fixture_details_success(self, mock_config):
        """Testa sincronização de detalhes de partida específica com sucesso"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dos dados retornados
            mock_fixture = {
                'id': 1,
                'name': 'Manchester City vs Liverpool',
                'venue': {'id': 1, 'name': 'Etihad Stadium'},
                'referees': [{'id': 1, 'name': 'Mike Dean'}],
                'participants': [
                    {'id': 1, 'meta': {'location': 'home'}},
                    {'id': 2, 'meta': {'location': 'away'}}
                ],
                'events': [
                    {'id': 1, 'minute': 15, 'type_id': 1}
                ]
            }
            mock_sportmonks_instance.get_fixture_by_id.return_value = mock_fixture
            
            # Mock dos upserts
            mock_supabase_instance.upsert_venues.return_value = True
            mock_supabase_instance.upsert_referees.return_value = True
            mock_supabase_instance.upsert_fixtures.return_value = True
            mock_supabase_instance.upsert_fixture_participants.return_value = True
            mock_supabase_instance.upsert_fixture_events.return_value = True
            
            etl = ETLProcess()
            result = etl.sync_fixture_details(1)
            
            assert result is True
            mock_sportmonks_instance.get_fixture_by_id.assert_called_once()
            mock_supabase_instance.upsert_venues.assert_called_once()
            mock_supabase_instance.upsert_referees.assert_called_once()
            mock_supabase_instance.upsert_fixtures.assert_called_once()
            mock_supabase_instance.upsert_fixture_participants.assert_called_once()
            mock_supabase_instance.upsert_fixture_events.assert_called_once()
    
    def test_full_sync_success(self, mock_config):
        """Testa sincronização completa com sucesso"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dos métodos de sincronização
            with patch.object(ETLProcess, 'sync_base_data') as mock_sync_base, \
                 patch.object(ETLProcess, 'sync_leagues') as mock_sync_leagues, \
                 patch.object(ETLProcess, 'sync_recent_fixtures') as mock_sync_recent:
                
                etl = ETLProcess()
                etl.full_sync()
                
                mock_sync_base.assert_called_once()
                mock_sync_leagues.assert_called_once()
                mock_sync_recent.assert_called_once_with(days_back=30, days_forward=30)
    
    def test_incremental_sync_success(self, mock_config):
        """Testa sincronização incremental com sucesso"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock do método sync_recent_fixtures
            with patch.object(ETLProcess, 'sync_recent_fixtures', return_value=True) as mock_sync_recent:
                etl = ETLProcess()
                etl.incremental_sync()
                
                mock_sync_recent.assert_called_once_with(days_back=2, days_forward=14)
    
    def test_error_handling_in_sync_methods(self, mock_config):
        """Testa tratamento de erro nos métodos de sincronização"""
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
    
    def test_data_validation_in_sync_methods(self, mock_config):
        """Testa validação de dados nos métodos de sincronização"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock de dados vazios (mas como lista, não None)
            mock_sportmonks_instance.get_countries.return_value = []
            mock_sportmonks_instance.get_states.return_value = []
            mock_sportmonks_instance.get_types.return_value = []
            
            # Mock dos upserts
            mock_supabase_instance.upsert_countries.return_value = True
            mock_supabase_instance.upsert_states.return_value = True
            mock_supabase_instance.upsert_types.return_value = True
            
            etl = ETLProcess()
            etl.sync_base_data()
            
            # Verificar que os métodos get foram chamados
            mock_sportmonks_instance.get_countries.assert_called_once()
            mock_sportmonks_instance.get_states.assert_called_once()
            mock_sportmonks_instance.get_types.assert_called_once()
            
            # Com listas vazias, upserts não devem ser chamados
            mock_supabase_instance.upsert_countries.assert_not_called()
            mock_supabase_instance.upsert_states.assert_not_called()
            mock_supabase_instance.upsert_types.assert_not_called()


class TestETLProcessLogging:
    """Testes de logging para ETLProcess"""
    
    def test_logging_during_execution(self, mock_config):
        """Testa logging durante execução"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase, \
             patch('bdfut.core.etl_process.logger') as mock_logger:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock dos dados com lista real para evitar erro de len()
            mock_countries = [{'id': 1, 'name': 'Brazil'}]
            mock_states = [{'id': 1, 'name': 'Active'}]
            mock_types = [{'id': 1, 'name': 'Goal'}]
            
            mock_sportmonks_instance.get_countries.return_value = mock_countries
            mock_sportmonks_instance.get_states.return_value = mock_states
            mock_sportmonks_instance.get_types.return_value = mock_types
            mock_supabase_instance.upsert_countries.return_value = True
            mock_supabase_instance.upsert_states.return_value = True
            mock_supabase_instance.upsert_types.return_value = True
            
            etl = ETLProcess()
            etl.sync_base_data()
            
            # Verificar se logs foram chamados
            assert mock_logger.info.called
            # Não testar debug pois pode não existir
    
    def test_error_logging(self, mock_config):
        """Testa logging de erros"""
        with patch('bdfut.core.etl_process.SportmonksClient') as mock_sportmonks, \
             patch('bdfut.core.etl_process.SupabaseClient') as mock_supabase, \
             patch('bdfut.core.etl_process.logger') as mock_logger:
            
            # Mock dos clientes
            mock_sportmonks_instance = Mock()
            mock_supabase_instance = Mock()
            mock_sportmonks.return_value = mock_sportmonks_instance
            mock_supabase.return_value = mock_supabase_instance
            
            # Mock de erro
            mock_sportmonks_instance.get_teams_by_season.side_effect = Exception("API Error")
            
            etl = ETLProcess()
            etl.sync_teams_by_season(25583)
            
            # Verificar se erro foi logado
            mock_logger.error.assert_called()
