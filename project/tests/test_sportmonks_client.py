"""
Testes unitários para SportmonksClient
=====================================

Testes abrangentes para o cliente da API Sportmonks com foco em:
- Rate limiting
- Cache
- Tratamento de erros
- Validação de dados
"""
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

from bdfut.core.sportmonks_client import SportmonksClient


class TestSportmonksClient:
    """Testes para SportmonksClient"""
    
    def test_init_with_cache_enabled(self, mock_config):
        """Testa inicialização com cache ativado"""
        with patch('bdfut.core.sportmonks_client.create_client') as mock_create:
            client = SportmonksClient(enable_cache=True, cache_ttl_hours=2)
            
            assert client.enable_cache is True
            assert client.cache_ttl_hours == 2
            assert client.cache_hits == 0
            assert client.cache_misses == 0
            mock_create.assert_called_once()
    
    def test_init_with_cache_disabled(self, mock_config):
        """Testa inicialização com cache desativado"""
        client = SportmonksClient(enable_cache=False)
        
        assert client.enable_cache is False
        assert client.cache_hits == 0
        assert client.cache_misses == 0
    
    def test_generate_cache_key(self, mock_config):
        """Testa geração de chave de cache"""
        client = SportmonksClient(enable_cache=False)
        
        params1 = {'season_id': 25583, 'per_page': 100, 'api_token': 'secret'}
        params2 = {'season_id': 25583, 'per_page': 100, 'api_token': 'different_secret'}
        params3 = {'season_id': 25584, 'per_page': 100, 'api_token': 'secret'}
        
        key1 = client._generate_cache_key('/fixtures', params1)
        key2 = client._generate_cache_key('/fixtures', params2)
        key3 = client._generate_cache_key('/fixtures', params3)
        
        # Chaves 1 e 2 devem ser iguais (api_token ignorado)
        assert key1 == key2
        # Chave 3 deve ser diferente (season_id diferente)
        assert key1 != key3
        # Chaves devem ter 32 caracteres (MD5)
        assert len(key1) == 32
    
    @patch('bdfut.core.sportmonks_client.requests.get')
    def test_make_request_success(self, mock_get, mock_config):
        """Testa requisição bem-sucedida"""
        # Mock da resposta
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'x-ratelimit-limit': '3000',
            'x-ratelimit-remaining': '2999'
        }
        mock_response.json.return_value = {'data': [{'id': 1, 'name': 'Test'}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = SportmonksClient(enable_cache=False)
        result = client._make_request('/test', {'param': 'value'})
        
        assert result == {'data': [{'id': 1, 'name': 'Test'}]}
        # requests_made é incrementado em request_timestamps.append()
        assert len(client.request_timestamps) == 1
        # Verificar se a requisição foi feita
        mock_get.assert_called_once()
    
    @patch('bdfut.core.sportmonks_client.requests.get')
    def test_make_request_rate_limit_429(self, mock_get, mock_config):
        """Testa tratamento de erro 429 (Rate Limit)"""
        # Mock da resposta 429
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response
        
        client = SportmonksClient(enable_cache=False)
        
        with pytest.raises(Exception, match="Rate limit exceeded"):
            client._make_request('/test', {'param': 'value'})
    
    @patch('bdfut.core.sportmonks_client.requests.get')
    def test_make_request_with_cache_hit(self, mock_get, mock_config):
        """Testa requisição com cache hit"""
        # Mock do Supabase
        mock_supabase = Mock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value.data = [
            {'data': {'cached': 'data'}}
        ]
        
        with patch('bdfut.core.sportmonks_client.create_client', return_value=mock_supabase):
            client = SportmonksClient(enable_cache=True)
            
            # Primeira chamada deve buscar no cache
            result = client._make_request('/test', {'param': 'value'})
            
            assert result == {'cached': 'data'}
            assert client.cache_hits == 1
            assert client.cache_misses == 0
            # Não deve fazer requisição HTTP
            mock_get.assert_not_called()
    
    @patch('bdfut.core.sportmonks_client.requests.get')
    def test_make_request_with_cache_miss(self, mock_get, mock_config):
        """Testa requisição com cache miss"""
        # Mock da resposta HTTP
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'x-ratelimit-remaining': '2999'}
        mock_response.json.return_value = {'data': [{'id': 1}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock do Supabase (cache miss)
        mock_supabase = Mock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value.data = []
        mock_supabase.table.return_value.upsert.return_value.execute.return_value = None
        
        with patch('bdfut.core.sportmonks_client.create_client', return_value=mock_supabase):
            client = SportmonksClient(enable_cache=True)
            
            result = client._make_request('/test', {'param': 'value'})
            
            assert result == {'data': [{'id': 1}]}
            assert client.cache_hits == 0
            assert client.cache_misses == 1
            # Deve fazer requisição HTTP
            mock_get.assert_called_once()
            # Deve salvar no cache
            mock_supabase.table.return_value.upsert.assert_called_once()
    
    def test_get_cache_stats_disabled(self, mock_config):
        """Testa estatísticas de cache quando desabilitado"""
        client = SportmonksClient(enable_cache=False)
        stats = client.get_cache_stats()
        
        assert stats == {"cache_enabled": False}
    
    def test_get_cache_stats_enabled(self, mock_config):
        """Testa estatísticas de cache quando habilitado"""
        # Mock do Supabase
        mock_supabase = Mock()
        mock_supabase.table.return_value.select.return_value.execute.return_value.count = 10
        mock_supabase.table.return_value.select.return_value.lt.return_value.execute.return_value.count = 2
        
        with patch('bdfut.core.sportmonks_client.create_client', return_value=mock_supabase):
            client = SportmonksClient(enable_cache=True)
            client.cache_hits = 5
            client.cache_misses = 3
            
            stats = client.get_cache_stats()
            
            assert stats["cache_enabled"] is True
            assert stats["cache_hits"] == 5
            assert stats["cache_misses"] == 3
            assert stats["hit_rate"] == 5/8
            assert stats["total_entries"] == 10
            assert stats["expired_entries"] == 2
    
    @patch('bdfut.core.sportmonks_client.requests.get')
    def test_get_fixtures_by_date_range(self, mock_get, mock_config):
        """Testa obtenção de fixtures por intervalo de datas"""
        # Mock da resposta
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'x-ratelimit-remaining': '2999'}
        mock_response.json.return_value = {
            'data': [{'id': 1, 'name': 'Fixture 1'}],
            'pagination': {'has_more': False}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = SportmonksClient(enable_cache=False)
        fixtures = client.get_fixtures_by_date_range('2025-01-15', '2025-01-15')
        
        assert len(fixtures) == 1
        assert fixtures[0]['id'] == 1
        assert fixtures[0]['name'] == 'Fixture 1'
    
    @patch('bdfut.core.sportmonks_client.requests.get')
    def test_get_paginated_data_multiple_pages(self, mock_get, mock_config):
        """Testa obtenção de dados paginados com múltiplas páginas"""
        # Mock das respostas para múltiplas páginas
        responses = [
            Mock(status_code=200, headers={'x-ratelimit-remaining': '2999'}, 
                 json=lambda: {'data': [{'id': 1}], 'pagination': {'has_more': True}}),
            Mock(status_code=200, headers={'x-ratelimit-remaining': '2998'}, 
                 json=lambda: {'data': [{'id': 2}], 'pagination': {'has_more': False}})
        ]
        
        for response in responses:
            response.raise_for_status.return_value = None
        
        mock_get.side_effect = responses
        
        client = SportmonksClient(enable_cache=False)
        data = client.get_paginated_data('/test')
        
        assert len(data) == 2
        assert data[0]['id'] == 1
        assert data[1]['id'] == 2
        assert mock_get.call_count == 2
    
    def test_check_rate_limit_no_limit(self, mock_config):
        """Testa verificação de rate limit quando não há limite"""
        client = SportmonksClient(enable_cache=False)
        client.rate_limit = 3000
        client.request_timestamps = []
        
        # Não deve levantar exceção
        client._check_rate_limit()
    
    def test_check_rate_limit_with_limit(self, mock_config):
        """Testa verificação de rate limit quando há limite"""
        client = SportmonksClient(enable_cache=False)
        client.rate_limit = 2
        
        # Simular muitas requisições
        now = datetime.now()
        client.request_timestamps = [
            now - timedelta(minutes=30),
            now - timedelta(minutes=20),
            now - timedelta(minutes=10)
        ]
        
        with patch('time.sleep') as mock_sleep:
            client._check_rate_limit()
            # Deve ter chamado sleep
            mock_sleep.assert_called_once()
    
    def test_update_rate_limit_from_headers(self, mock_config):
        """Testa atualização de rate limit dos headers"""
        client = SportmonksClient(enable_cache=False)
        
        headers = {
            'x-ratelimit-limit': '3000',
            'x-ratelimit-remaining': '2500',
            'x-ratelimit-reset': '1640995200'  # Timestamp futuro
        }
        
        client._update_rate_limit_from_headers(headers)
        
        assert client.rate_limit_remaining == 2500
        assert client.rate_limit_reset is not None
    
    def test_save_to_cache_error_handling(self, mock_config):
        """Testa tratamento de erro ao salvar no cache"""
        # Mock do Supabase com erro
        mock_supabase = Mock()
        mock_supabase.table.return_value.upsert.return_value.execute.side_effect = Exception("Database error")
        
        with patch('bdfut.core.sportmonks_client.create_client', return_value=mock_supabase):
            client = SportmonksClient(enable_cache=True)
            
            # Não deve levantar exceção
            client._save_to_cache('/test', {'param': 'value'}, {'data': 'test'})
    
    def test_get_from_cache_error_handling(self, mock_config):
        """Testa tratamento de erro ao buscar no cache"""
        # Mock do Supabase com erro
        mock_supabase = Mock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.side_effect = Exception("Database error")
        
        with patch('bdfut.core.sportmonks_client.create_client', return_value=mock_supabase):
            client = SportmonksClient(enable_cache=True)
            
            result = client._get_from_cache('/test', {'param': 'value'})
            
            assert result is None
            assert client.cache_misses == 1


class TestSportmonksClientIntegration:
    """Testes de integração para SportmonksClient"""
    
    @patch('bdfut.core.sportmonks_client.requests.get')
    def test_full_workflow_with_cache(self, mock_get, mock_config):
        """Testa workflow completo com cache"""
        # Mock da resposta
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'x-ratelimit-remaining': '2999'}
        mock_response.json.return_value = {'data': [{'id': 1}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock do Supabase
        mock_supabase = Mock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value.data = []
        mock_supabase.table.return_value.upsert.return_value.execute.return_value = None
        
        with patch('bdfut.core.sportmonks_client.create_client', return_value=mock_supabase):
            client = SportmonksClient(enable_cache=True, cache_ttl_hours=1)
            
            # Primeira requisição (cache miss)
            result1 = client.get_fixtures_by_date_range('2025-01-15', '2025-01-15')
            
            # Segunda requisição (cache hit)
            result2 = client.get_fixtures_by_date_range('2025-01-15', '2025-01-15')
            
            # Verificar resultados
            assert result1 == result2
            assert client.cache_hits == 1
            assert client.cache_misses == 1
            
            # Verificar estatísticas
            stats = client.get_cache_stats()
            assert stats["cache_enabled"] is True
            assert stats["hit_rate"] == 0.5
