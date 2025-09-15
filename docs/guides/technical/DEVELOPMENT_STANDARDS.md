# Padrões de Desenvolvimento - BDFut 🛠️

## Visão Geral

Este documento define os padrões, convenções e melhores práticas para desenvolvimento no projeto BDFut, garantindo consistência, qualidade e manutenibilidade do código.

## Índice

1. [Convenções de Código](#convenções-de-código)
2. [Estrutura de Projeto](#estrutura-de-projeto)
3. [Padrões de Nomenclatura](#padrões-de-nomenclatura)
4. [Padrões de Documentação](#padrões-de-documentação)
5. [Padrões de Testes](#padrões-de-testes)
6. [Padrões de Git](#padrões-de-git)
7. [Ferramentas de Desenvolvimento](#ferramentas-de-desenvolvimento)

---

## Convenções de Código

### Python Style Guide

#### PEP 8 Compliance

O projeto segue rigorosamente o PEP 8:

```python
# ✅ CORRETO - Indentação com 4 espaços
def process_data(data):
    result = []
    for item in data:
        if item.is_valid():
            result.append(item.process())
    return result

# ❌ INCORRETO - Indentação com tabs ou 2 espaços
def process_data(data):
  result = []
    for item in data:
        if item.is_valid():
            result.append(item.process())
  return result
```

#### Linha de Comando

```bash
# Usar Black para formatação automática
black bdfut/

# Usar Flake8 para linting
flake8 bdfut/

# Usar MyPy para verificação de tipos
mypy bdfut/
```

### Formatação de Código

#### Imports

```python
# ✅ CORRETO - Imports organizados
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from requests import Session
from supabase import create_client

from .config import Config
from .exceptions import BDFutError

# ❌ INCORRETO - Imports desorganizados
from .config import Config
import os
from requests import Session
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
```

#### Docstrings

```python
def sync_leagues(league_ids: Optional[List[int]] = None) -> bool:
    """
    Sincroniza ligas e suas temporadas.
    
    Args:
        league_ids: Lista de IDs de ligas. Se None, usa ligas principais.
        
    Returns:
        bool: True se sucesso, False se erro.
        
    Raises:
        BDFutError: Se houver erro na sincronização.
        
    Example:
        >>> etl = ETLProcess()
        >>> success = etl.sync_leagues([648, 651])
        >>> print(f"Sincronização: {'Sucesso' if success else 'Falha'}")
    """
    pass
```

#### Type Hints

```python
# ✅ CORRETO - Type hints completos
def process_fixtures(
    fixtures: List[Dict[str, Any]],
    include_details: bool = False
) -> Dict[str, int]:
    """Processa lista de partidas."""
    pass

# ❌ INCORRETO - Sem type hints
def process_fixtures(fixtures, include_details=False):
    """Processa lista de partidas."""
    pass
```

### Tratamento de Erros

#### Exceções Customizadas

```python
# bdfut/exceptions.py
class BDFutError(Exception):
    """Exceção base do BDFut."""
    pass

class APIError(BDFutError):
    """Erro de API externa."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code

class ConfigurationError(BDFutError):
    """Erro de configuração."""
    pass

class ValidationError(BDFutError):
    """Erro de validação de dados."""
    pass
```

#### Tratamento de Erros

```python
# ✅ CORRETO - Tratamento específico
try:
    data = client.get_data()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        logger.warning("Rate limit excedido, aguardando...")
        time.sleep(60)
        return False
    elif e.response.status_code == 401:
        logger.error("API key inválida")
        raise ConfigurationError("API key inválida")
    else:
        logger.error(f"Erro HTTP: {e}")
        raise APIError(f"Erro HTTP: {e}", e.response.status_code)
except requests.exceptions.RequestException as e:
    logger.error(f"Erro de conexão: {e}")
    raise APIError(f"Erro de conexão: {e}")

# ❌ INCORRETO - Tratamento genérico
try:
    data = client.get_data()
except Exception as e:
    logger.error(f"Erro: {e}")
    return False
```

### Logging

#### Configuração de Logging

```python
import logging
from typing import Optional

def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Configura logging do sistema."""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # File handler (se especificado)
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configurar root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=handlers
    )
```

#### Uso de Logging

```python
import logging

logger = logging.getLogger(__name__)

def sync_data():
    """Sincroniza dados."""
    logger.info("Iniciando sincronização de dados")
    
    try:
        # Processar dados
        logger.debug("Processando dados...")
        result = process_data()
        
        logger.info(f"Sincronização concluída: {len(result)} registros")
        return True
        
    except Exception as e:
        logger.error(f"Erro na sincronização: {str(e)}")
        return False
```

---

## Estrutura de Projeto

### Organização de Diretórios

```
bdfut/
├── bdfut/                    # Pacote principal
│   ├── __init__.py
│   ├── core/                 # Módulos principais
│   │   ├── __init__.py
│   │   ├── sportmonks_client.py
│   │   ├── supabase_client.py
│   │   ├── etl_process.py
│   │   ├── etl_metadata.py
│   │   └── redis_cache.py
│   ├── config/               # Configurações
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── settings.py
│   │   ├── environments/
│   │   └── secrets/
│   ├── scripts/              # Scripts organizados
│   │   ├── etl/              # Scripts de ETL
│   │   ├── sync/             # Scripts de sincronização
│   │   ├── maintenance/      # Scripts de manutenção
│   │   ├── testing/          # Scripts de teste
│   │   └── utils/            # Scripts utilitários
│   ├── tools/                # Ferramentas e utilitários
│   ├── notebooks/            # Notebooks Jupyter
│   ├── data/                 # Dados e arquivos JSON
│   ├── logs/                 # Arquivos de log
│   ├── archive/              # Arquivos arquivados
│   └── cli.py                # Interface CLI
├── docs/                     # Documentação
├── tests/                    # Testes automatizados
├── deployment/               # Configurações de deployment
├── pyproject.toml            # Configuração do projeto
├── requirements.txt          # Dependências
├── setup.py                  # Setup do projeto
├── Dockerfile                # Configuração Docker
├── docker-compose.yml        # Compose Docker
├── Makefile                  # Comandos Make
└── README.md                 # Documentação principal
```

### Organização de Módulos

#### Core Modules

```python
# bdfut/core/sportmonks_client.py
class SportmonksClient:
    """Cliente para API Sportmonks."""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = self._create_session()
    
    def _create_session(self) -> Session:
        """Cria sessão HTTP."""
        pass
    
    def get_countries(self) -> List[Dict]:
        """Busca países."""
        pass

# bdfut/core/supabase_client.py
class SupabaseClient:
    """Cliente para Supabase."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = self._create_client()
    
    def _create_client(self) -> Client:
        """Cria cliente Supabase."""
        pass
    
    def upsert_countries(self, countries: List[Dict]) -> bool:
        """Insere ou atualiza países."""
        pass
```

#### Configuration Modules

```python
# bdfut/config/config.py
class Config:
    """Configuração centralizada."""
    
    @classmethod
    def validate(cls) -> None:
        """Valida configurações."""
        pass
    
    @classmethod
    def get_sportmonks_config(cls) -> Dict[str, str]:
        """Retorna configuração Sportmonks."""
        pass

# bdfut/config/settings.py
class Settings:
    """Configurações específicas do ambiente."""
    
    def __init__(self, env: str = "development"):
        self.env = env
        self._load_settings()
    
    def _load_settings(self) -> None:
        """Carrega configurações do ambiente."""
        pass
```

### Organização de Scripts

#### ETL Scripts

```python
# bdfut/scripts/etl/01_popular_leagues_seasons.py
"""
Script para popular ligas e temporadas.
"""

import logging
from bdfut.core.etl_process import ETLProcess

logger = logging.getLogger(__name__)

def main():
    """Função principal do script."""
    logger.info("Iniciando script de popular ligas e temporadas")
    
    try:
        etl = ETLProcess()
        etl.sync_leagues()
        logger.info("Script concluído com sucesso")
    except Exception as e:
        logger.error(f"Erro no script: {str(e)}")
        raise

if __name__ == "__main__":
    main()
```

#### Sync Scripts

```python
# bdfut/scripts/sync/sync_brasileirao_final.py
"""
Script específico para sincronização do Brasileirão.
"""

import logging
from bdfut.core.etl_process import ETLProcess

logger = logging.getLogger(__name__)

def sync_brasileirao():
    """Sincroniza dados do Brasileirão."""
    logger.info("Iniciando sincronização do Brasileirão")
    
    etl = ETLProcess()
    
    # Sincronizar liga específica
    etl.sync_leagues([648])  # Brasileirão
    
    # Sincronizar temporada atual
    # Implementar lógica específica
    
    logger.info("Sincronização do Brasileirão concluída")

if __name__ == "__main__":
    sync_brasileirao()
```

---

## Padrões de Nomenclatura

### Arquivos e Diretórios

#### Convenções

- **Diretórios**: `snake_case` (ex: `etl_scripts`, `data_processing`)
- **Arquivos Python**: `snake_case.py` (ex: `sportmonks_client.py`)
- **Arquivos de Config**: `snake_case.env` (ex: `development.env`)
- **Arquivos de Teste**: `test_snake_case.py` (ex: `test_sportmonks_client.py`)

#### Exemplos

```
# ✅ CORRETO
bdfut/
├── core/
│   ├── sportmonks_client.py
│   ├── supabase_client.py
│   └── etl_process.py
├── scripts/
│   ├── etl/
│   │   ├── 01_popular_leagues_seasons.py
│   │   └── 02_popular_teams.py
│   └── sync/
│       └── sync_brasileirao_final.py
└── tests/
    ├── test_sportmonks_client.py
    └── test_etl_process.py

# ❌ INCORRETO
bdfut/
├── Core/
│   ├── SportmonksClient.py
│   ├── supabaseClient.py
│   └── ETLProcess.py
├── Scripts/
│   ├── ETL/
│   │   ├── 01-Popular-Leagues-Seasons.py
│   │   └── 02-Popular-Teams.py
│   └── Sync/
│       └── SyncBrasileiraoFinal.py
└── Tests/
    ├── TestSportmonksClient.py
    └── test_ETLProcess.py
```

### Classes e Funções

#### Convenções

- **Classes**: `PascalCase` (ex: `SportmonksClient`, `ETLProcess`)
- **Funções**: `snake_case` (ex: `sync_leagues`, `process_data`)
- **Variáveis**: `snake_case` (ex: `league_ids`, `fixture_data`)
- **Constantes**: `UPPER_SNAKE_CASE` (ex: `MAX_RETRIES`, `DEFAULT_BATCH_SIZE`)

#### Exemplos

```python
# ✅ CORRETO
class SportmonksClient:
    """Cliente para API Sportmonks."""
    
    MAX_RETRIES = 3
    DEFAULT_TIMEOUT = 30
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = self._create_session()
    
    def get_countries(self) -> List[Dict]:
        """Busca países."""
        pass
    
    def _create_session(self) -> Session:
        """Cria sessão HTTP."""
        pass

# ❌ INCORRETO
class sportmonksClient:
    """Cliente para API Sportmonks."""
    
    maxRetries = 3
    defaultTimeout = 30
    
    def __init__(self, apiKey: str):
        self.apiKey = apiKey
        self.session = self._createSession()
    
    def getCountries(self) -> List[Dict]:
        """Busca países."""
        pass
    
    def _createSession(self) -> Session:
        """Cria sessão HTTP."""
        pass
```

### Variáveis e Constantes

#### Convenções

- **Variáveis locais**: `snake_case` (ex: `user_data`, `api_response`)
- **Variáveis de instância**: `snake_case` (ex: `self.api_key`, `self.session`)
- **Variáveis privadas**: `_snake_case` (ex: `_internal_data`, `_cache`)
- **Constantes**: `UPPER_SNAKE_CASE` (ex: `MAX_RETRIES`, `DEFAULT_BATCH_SIZE`)

#### Exemplos

```python
# ✅ CORRETO
class ETLProcess:
    """Processo de ETL."""
    
    MAX_RETRIES = 3
    DEFAULT_BATCH_SIZE = 100
    
    def __init__(self):
        self.sportmonks_client = SportmonksClient()
        self.supabase_client = SupabaseClient()
        self._cache = {}
        self._internal_state = "idle"
    
    def sync_leagues(self, league_ids: List[int]) -> bool:
        """Sincroniza ligas."""
        processed_count = 0
        error_count = 0
        
        for league_id in league_ids:
            try:
                league_data = self._fetch_league_data(league_id)
                self._process_league_data(league_data)
                processed_count += 1
            except Exception as e:
                error_count += 1
                logger.error(f"Erro ao processar liga {league_id}: {e}")
        
        return error_count == 0

# ❌ INCORRETO
class ETLProcess:
    """Processo de ETL."""
    
    maxRetries = 3
    defaultBatchSize = 100
    
    def __init__(self):
        self.sportmonksClient = SportmonksClient()
        self.supabaseClient = SupabaseClient()
        self.cache = {}
        self.internalState = "idle"
    
    def syncLeagues(self, leagueIds: List[int]) -> bool:
        """Sincroniza ligas."""
        processedCount = 0
        errorCount = 0
        
        for leagueId in leagueIds:
            try:
                leagueData = self._fetchLeagueData(leagueId)
                self._processLeagueData(leagueData)
                processedCount += 1
            except Exception as e:
                errorCount += 1
                logger.error(f"Erro ao processar liga {leagueId}: {e}")
        
        return errorCount == 0
```

---

## Padrões de Documentação

### Docstrings

#### Formato Padrão

```python
def sync_leagues(
    league_ids: Optional[List[int]] = None,
    include_seasons: bool = True
) -> bool:
    """
    Sincroniza ligas e suas temporadas.
    
    Esta função busca dados de ligas da API Sportmonks e os armazena
    no banco de dados Supabase. Se include_seasons for True, também
    sincroniza as temporadas de cada liga.
    
    Args:
        league_ids: Lista de IDs de ligas para sincronizar. Se None,
                   usa as ligas principais configuradas no sistema.
        include_seasons: Se True, inclui temporadas das ligas.
        
    Returns:
        bool: True se a sincronização foi bem-sucedida, False caso contrário.
        
    Raises:
        APIError: Se houver erro na comunicação com a API Sportmonks.
        DatabaseError: Se houver erro ao salvar dados no Supabase.
        ValidationError: Se os dados recebidos forem inválidos.
        
    Example:
        >>> etl = ETLProcess()
        >>> # Sincronizar ligas específicas
        >>> success = etl.sync_leagues([648, 651])
        >>> print(f"Sincronização: {'Sucesso' if success else 'Falha'}")
        
        >>> # Sincronizar ligas principais sem temporadas
        >>> success = etl.sync_leagues(include_seasons=False)
        
    Note:
        Esta função respeita o rate limiting configurado e pode
        levar vários minutos para completar dependendo do número
        de ligas e temporadas.
    """
    pass
```

#### Classes

```python
class SportmonksClient:
    """
    Cliente para interação com a API Sportmonks.
    
    Este cliente fornece métodos para buscar dados de futebol da API
    Sportmonks, incluindo países, ligas, times, partidas e estatísticas.
    Implementa rate limiting automático e sistema de cache para
    otimizar performance.
    
    Attributes:
        api_key (str): Chave da API Sportmonks.
        base_url (str): URL base da API.
        session (Session): Sessão HTTP para requisições.
        cache (RedisCache): Sistema de cache para otimização.
        
    Example:
        >>> client = SportmonksClient(api_key="sua_chave")
        >>> countries = client.get_countries()
        >>> print(f"Encontrados {len(countries)} países")
        
    Note:
        Requer configuração válida da API key e conectividade
        com a internet para funcionar corretamente.
    """
    
    def __init__(self, api_key: str):
        """
        Inicializa o cliente Sportmonks.
        
        Args:
            api_key: Chave da API Sportmonks.
            
        Raises:
            ConfigurationError: Se a API key for inválida.
        """
        pass
```

### Comentários

#### Comentários de Código

```python
# ✅ CORRETO - Comentários úteis
def process_fixtures(fixtures: List[Dict]) -> List[Dict]:
    """Processa lista de partidas."""
    processed_fixtures = []
    
    for fixture in fixtures:
        # Validar dados obrigatórios antes do processamento
        if not self._validate_fixture(fixture):
            logger.warning(f"Partida {fixture.get('id')} inválida, pulando...")
            continue
        
        # Extrair participantes e salvar separadamente
        participants = fixture.pop('participants', [])
        self._save_participants(fixture['id'], participants)
        
        # Processar dados da partida
        processed_fixture = self._transform_fixture(fixture)
        processed_fixtures.append(processed_fixture)
    
    return processed_fixtures

# ❌ INCORRETO - Comentários óbvios
def process_fixtures(fixtures: List[Dict]) -> List[Dict]:
    """Processa lista de partidas."""
    processed_fixtures = []  # Lista vazia
    
    for fixture in fixtures:  # Para cada partida
        if not self._validate_fixture(fixture):  # Se inválida
            continue  # Pular
        
        processed_fixture = self._transform_fixture(fixture)  # Transformar
        processed_fixtures.append(processed_fixture)  # Adicionar
    
    return processed_fixtures  # Retornar
```

#### Comentários de TODO

```python
# TODO: Implementar cache para reduzir chamadas à API
# TODO: Adicionar validação de dados mais robusta
# TODO: Otimizar processamento em lote
# FIXME: Corrigir bug na validação de datas
# HACK: Solução temporária para problema de encoding
# NOTE: Esta função será refatorada na próxima versão
```

---

## Padrões de Testes

### Estrutura de Testes

```
tests/
├── __init__.py
├── conftest.py              # Configuração do pytest
├── test_core/               # Testes dos módulos core
│   ├── __init__.py
│   ├── test_sportmonks_client.py
│   ├── test_supabase_client.py
│   ├── test_etl_process.py
│   └── test_redis_cache.py
├── test_config/             # Testes de configuração
│   ├── __init__.py
│   └── test_config.py
├── test_scripts/            # Testes de scripts
│   ├── __init__.py
│   └── test_etl_scripts.py
└── fixtures/                # Dados de teste
    ├── sportmonks_responses.json
    └── supabase_data.json
```

### Configuração do Pytest

```python
# tests/conftest.py
import pytest
import os
from unittest.mock import Mock
from bdfut.config.config import Config

@pytest.fixture
def mock_config():
    """Mock de configuração para testes."""
    config = Mock(spec=Config)
    config.SPORTMONKS_API_KEY = "test_key"
    config.SUPABASE_URL = "https://test.supabase.co"
    config.SUPABASE_KEY = "test_key"
    config.RATE_LIMIT_PER_HOUR = 1000
    return config

@pytest.fixture
def mock_sportmonks_response():
    """Mock de resposta da API Sportmonks."""
    return {
        "data": [
            {"id": 1, "name": "Brazil", "iso2": "BR"},
            {"id": 2, "name": "Argentina", "iso2": "AR"}
        ]
    }

@pytest.fixture
def temp_env():
    """Ambiente temporário para testes."""
    old_env = os.environ.copy()
    os.environ.update({
        "BDFUT_ENV": "test",
        "LOG_LEVEL": "DEBUG"
    })
    yield
    os.environ.clear()
    os.environ.update(old_env)
```

### Testes Unitários

```python
# tests/test_core/test_sportmonks_client.py
import pytest
from unittest.mock import Mock, patch
from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.exceptions import APIError

class TestSportmonksClient:
    """Testes para SportmonksClient."""
    
    def test_init_with_valid_config(self, mock_config):
        """Testa inicialização com configuração válida."""
        client = SportmonksClient(mock_config)
        assert client.config == mock_config
        assert client.api_key == "test_key"
    
    def test_get_countries_success(self, mock_config, mock_sportmonks_response):
        """Testa busca de países com sucesso."""
        with patch('requests.Session.get') as mock_get:
            mock_get.return_value.json.return_value = mock_sportmonks_response
            mock_get.return_value.status_code = 200
            
            client = SportmonksClient(mock_config)
            countries = client.get_countries()
            
            assert len(countries) == 2
            assert countries[0]["name"] == "Brazil"
            assert countries[1]["name"] == "Argentina"
    
    def test_get_countries_api_error(self, mock_config):
        """Testa tratamento de erro da API."""
        with patch('requests.Session.get') as mock_get:
            mock_get.return_value.status_code = 401
            mock_get.return_value.raise_for_status.side_effect = Exception("Unauthorized")
            
            client = SportmonksClient(mock_config)
            
            with pytest.raises(APIError):
                client.get_countries()
    
    def test_rate_limiting(self, mock_config):
        """Testa controle de rate limiting."""
        client = SportmonksClient(mock_config)
        
        # Simular muitas requisições
        for _ in range(10):
            client._make_request("/test")
        
        # Verificar se rate limiting foi aplicado
        assert client.requests_made <= client.rate_limit
```

### Testes de Integração

```python
# tests/test_integration/test_etl_process.py
import pytest
from bdfut.core.etl_process import ETLProcess

class TestETLProcessIntegration:
    """Testes de integração para ETLProcess."""
    
    @pytest.mark.integration
    def test_sync_base_data(self, temp_env):
        """Testa sincronização de dados base."""
        etl = ETLProcess()
        success = etl.sync_base_data()
        
        assert success is True
        
        # Verificar se dados foram salvos
        # (implementar verificação no banco)
    
    @pytest.mark.slow
    def test_full_sync(self, temp_env):
        """Testa sincronização completa."""
        etl = ETLProcess()
        success = etl.full_sync()
        
        assert success is True
```

### Testes de Performance

```python
# tests/test_performance/test_cache_performance.py
import pytest
import time
from bdfut.core.redis_cache import RedisCache

class TestCachePerformance:
    """Testes de performance do cache."""
    
    def test_cache_hit_performance(self):
        """Testa performance de cache hit."""
        cache = RedisCache()
        
        # Popular cache
        cache.set("test_key", "test_value")
        
        # Medir tempo de acesso
        start_time = time.time()
        for _ in range(1000):
            cache.get("test_key")
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 1000
        assert avg_time < 0.001  # Menos de 1ms por acesso
    
    def test_cache_miss_performance(self):
        """Testa performance de cache miss."""
        cache = RedisCache()
        
        # Medir tempo de acesso a chave inexistente
        start_time = time.time()
        for _ in range(1000):
            cache.get("nonexistent_key")
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 1000
        assert avg_time < 0.001  # Menos de 1ms por acesso
```

---

## Padrões de Git

### Commits

#### Formato de Commit

```
<tipo>(<escopo>): <descrição>

[corpo opcional]

[rodapé opcional]
```

#### Tipos de Commit

- **feat**: Nova funcionalidade
- **fix**: Correção de bug
- **docs**: Documentação
- **style**: Formatação, sem mudança de código
- **refactor**: Refatoração de código
- **test**: Adição ou correção de testes
- **chore**: Tarefas de manutenção

#### Exemplos

```bash
# ✅ CORRETO
feat(etl): adiciona sincronização incremental
fix(api): corrige rate limiting para ligas
docs(readme): atualiza instruções de instalação
test(core): adiciona testes para SportmonksClient
refactor(cache): otimiza algoritmo de invalidação
chore(deps): atualiza dependências para versão 2.0

# ❌ INCORRETO
adiciona funcionalidade
corrige bug
atualiza documentação
testes
refatoração
```

### Branches

#### Convenções de Naming

- **feature/**: `feature/sync-incremental`
- **bugfix/**: `bugfix/rate-limiting-issue`
- **hotfix/**: `hotfix/critical-api-error`
- **release/**: `release/v2.0.0`
- **chore/**: `chore/update-dependencies`

#### Exemplos

```bash
# ✅ CORRETO
git checkout -b feature/sync-incremental
git checkout -b bugfix/rate-limiting-issue
git checkout -b hotfix/critical-api-error
git checkout -b release/v2.0.0
git checkout -b chore/update-dependencies

# ❌ INCORRETO
git checkout -b new-feature
git checkout -b fix-bug
git checkout -b update-docs
git checkout -b tests
git checkout -b refactor
```

### Pull Requests

#### Template de PR

```markdown
## Descrição
Breve descrição das mudanças implementadas.

## Tipo de Mudança
- [ ] Bug fix (mudança que corrige um problema)
- [ ] Nova funcionalidade (mudança que adiciona funcionalidade)
- [ ] Breaking change (mudança que quebra compatibilidade)
- [ ] Documentação (mudança apenas na documentação)

## Checklist
- [ ] Código segue padrões do projeto
- [ ] Testes foram adicionados/atualizados
- [ ] Documentação foi atualizada
- [ ] Mudanças foram testadas localmente

## Testes
Descreva os testes realizados para validar as mudanças.

## Screenshots (se aplicável)
Adicione screenshots para ajudar a explicar as mudanças.

## Notas Adicionais
Qualquer informação adicional relevante.
```

---

## Ferramentas de Desenvolvimento

### Formatação de Código

#### Black

```bash
# Instalar Black
pip install black

# Formatar código
black bdfut/

# Verificar formatação
black --check bdfut/

# Configuração no pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

#### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.2.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

### Linting

#### Flake8

```bash
# Instalar Flake8
pip install flake8

# Executar linting
flake8 bdfut/

# Configuração no setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    .venv,
    build,
    dist
```

#### MyPy

```bash
# Instalar MyPy
pip install mypy

# Verificar tipos
mypy bdfut/

# Configuração no pyproject.toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Testes

#### Pytest

```bash
# Instalar Pytest
pip install pytest pytest-cov

# Executar testes
pytest

# Executar com cobertura
pytest --cov=bdfut --cov-report=html

# Executar testes específicos
pytest tests/test_core/test_sportmonks_client.py

# Executar com verbose
pytest -v
```

#### Configuração do Pytest

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
```

### Makefile

```makefile
# Makefile
.PHONY: install test lint format clean

install:
	pip install -e .

test:
	pytest

test-cov:
	pytest --cov=bdfut --cov-report=html

lint:
	flake8 bdfut/
	mypy bdfut/

format:
	black bdfut/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

all: format lint test
```

---

**Última atualização**: 2025-01-13  
**Versão**: 2.0  
**Responsável**: Technical Writer
