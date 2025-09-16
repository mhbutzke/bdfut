"""
Configuração de testes para BDFut
================================

Configurações compartilhadas e fixtures para os testes.
"""
import pytest
import os
import tempfile
from unittest.mock import Mock
from bdfut.config.settings import Config, Environment, set_config

@pytest.fixture
def temp_dir():
    """Cria um diretório temporário para testes"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def mock_config():
    """Cria uma configuração mock para testes"""
    config = Config(Environment.DEVELOPMENT)
    config.SPORTMONKS_API_KEY = "test_api_key"
    config.SUPABASE_URL = "https://test.supabase.co"
    config.SUPABASE_KEY = "test_supabase_key"
    config.DEBUG = True
    config.VERBOSE_LOGGING = True
    config.SAVE_RAW_DATA = True
    config.RATE_LIMIT_PER_HOUR = 100
    config.BATCH_SIZE = 10
    config.MAX_RETRIES = 1
    config.RETRY_DELAY = 1
    
    # Definir como configuração global
    set_config(config)
    return config

@pytest.fixture
def mock_sportmonks_client():
    """Cria um mock do cliente Sportmonks"""
    client = Mock()
    client.get_states.return_value = [
        {"id": 1, "name": "Test State"},
        {"id": 2, "name": "Another State"}
    ]
    client.get_leagues.return_value = [
        {"id": 648, "name": "Brasil - Serie A"},
        {"id": 651, "name": "Brasil - Serie B"}
    ]
    return client

@pytest.fixture
def mock_supabase_client():
    """Cria um mock do cliente Supabase"""
    client = Mock()
    client.client = Mock()
    client.client.table.return_value.select.return_value.limit.return_value.execute.return_value = Mock()
    return client

@pytest.fixture(autouse=True)
def setup_test_env():
    """Configura o ambiente para testes"""
    # Definir variáveis de ambiente para testes
    os.environ["BDFUT_ENV"] = "development"
    os.environ["SPORTMONKS_API_KEY"] = "test_key"
    os.environ["SUPABASE_URL"] = "https://test.supabase.co"
    os.environ["SUPABASE_KEY"] = "test_key"
    
    yield
    
    # Limpar após os testes
    for key in ["BDFUT_ENV", "SPORTMONKS_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]:
        os.environ.pop(key, None)
