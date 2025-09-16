# Arquitetura de Componentes - BDFut 🔧

## Visão Detalhada dos Componentes

Este documento detalha a arquitetura interna dos componentes do sistema BDFut, incluindo interações, dependências e responsabilidades.

## Diagrama de Componentes Detalhado

```mermaid
graph TB
    subgraph "CLI Layer"
        CLI[CLI Interface]
        CMD[Commands]
    end
    
    subgraph "Core Layer"
        ETL[ETL Process]
        SM_CLIENT[Sportmonks Client]
        SB_CLIENT[Supabase Client]
        METADATA[ETL Metadata]
        CACHE[Redis Cache]
    end
    
    subgraph "Configuration Layer"
        CONFIG[Config Manager]
        SETTINGS[Settings]
        ENV[Environment]
    end
    
    subgraph "Scripts Layer"
        ETL_SCRIPTS[ETL Scripts]
        SYNC_SCRIPTS[Sync Scripts]
        MAINT_SCRIPTS[Maintenance Scripts]
        TEST_SCRIPTS[Testing Scripts]
        UTIL_SCRIPTS[Utility Scripts]
    end
    
    subgraph "External Services"
        SM_API[Sportmonks API]
        SUPABASE_DB[(Supabase Database)]
        REDIS_DB[(Redis Cache)]
    end
    
    CLI --> CMD
    CMD --> ETL
    ETL --> SM_CLIENT
    ETL --> SB_CLIENT
    ETL --> METADATA
    SM_CLIENT --> CACHE
    SM_CLIENT --> SM_API
    SB_CLIENT --> SUPABASE_DB
    CACHE --> REDIS_DB
    
    ETL --> CONFIG
    SM_CLIENT --> CONFIG
    SB_CLIENT --> CONFIG
    CONFIG --> SETTINGS
    CONFIG --> ENV
    
    ETL --> ETL_SCRIPTS
    ETL --> SYNC_SCRIPTS
    ETL --> MAINT_SCRIPTS
    ETL --> TEST_SCRIPTS
    ETL --> UTIL_SCRIPTS
```

## Detalhamento dos Componentes

### 1. CLI Layer

#### CLI Interface (`cli.py`)
```python
class BDFutCLI:
    """Interface principal de linha de comando"""
    
    def __init__(self):
        self.etl_process = ETLProcess()
        self.config = Config()
    
    def show_config(self):
        """Exibe configuração atual"""
        
    def test_connection(self):
        """Testa conectividade com APIs"""
        
    def sync_base(self):
        """Sincronização de dados base"""
        
    def sync_leagues(self, league_ids):
        """Sincronização de ligas específicas"""
        
    def full_sync(self):
        """Sincronização completa"""
        
    def incremental(self):
        """Sincronização incremental"""
```

**Responsabilidades**:
- Interface de usuário principal
- Validação de parâmetros de entrada
- Coordenação de comandos
- Tratamento de erros de usuário

### 2. Core Layer

#### ETL Process (`etl_process.py`)
```python
class ETLProcess:
    """Coordena o processo de ETL dos dados"""
    
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.metadata_manager = ETLMetadataManager()
    
    def sync_base_data(self):
        """Sincroniza dados base (countries, states, types)"""
        
    def sync_leagues(self, league_ids):
        """Sincroniza ligas e suas temporadas"""
        
    def sync_teams_by_season(self, season_id):
        """Sincroniza times de uma temporada específica"""
        
    def sync_fixtures_by_date_range(self, start_date, end_date):
        """Sincroniza partidas em um intervalo de datas"""
        
    def full_sync(self):
        """Executa sincronização completa"""
        
    def incremental_sync(self):
        """Executa sincronização incremental"""
```

**Responsabilidades**:
- Coordenação de todo o processo ETL
- Orquestração de componentes
- Controle de fluxo de dados
- Gerenciamento de contexto de jobs

#### Sportmonks Client (`sportmonks_client.py`)
```python
class SportmonksClient:
    """Cliente para interação com a API Sportmonks"""
    
    def __init__(self, enable_cache=True, use_redis=True):
        self.cache = RedisCache() if use_redis else None
        self.rate_limiter = RateLimiter()
    
    def get_countries(self):
        """Busca países da API"""
        
    def get_leagues(self):
        """Busca ligas da API"""
        
    def get_fixtures_by_date_range(self, start_date, end_date):
        """Busca partidas por intervalo de datas"""
        
    def _make_request(self, endpoint, params):
        """Faz requisição HTTP com rate limiting"""
```

**Responsabilidades**:
- Interface com API Sportmonks
- Controle de rate limiting
- Cache inteligente
- Retry automático
- Tratamento de erros HTTP

#### Supabase Client (`supabase_client.py`)
```python
class SupabaseClient:
    """Cliente para interação com o banco de dados Supabase"""
    
    def __init__(self):
        self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    def upsert_countries(self, countries):
        """Insere ou atualiza países"""
        
    def upsert_leagues(self, leagues):
        """Insere ou atualiza ligas"""
        
    def upsert_fixtures(self, fixtures):
        """Insere ou atualiza partidas"""
        
    def _prepare_data(self, data, entity_type):
        """Prepara dados para inserção"""
```

**Responsabilidades**:
- Interface com banco Supabase
- Operações CRUD
- Upsert inteligente
- Tratamento de relacionamentos
- Validação de dados

#### ETL Metadata (`etl_metadata.py`)
```python
class ETLMetadataManager:
    """Gerenciador de metadados do ETL"""
    
    def create_job_context(self, job_name, job_type):
        """Cria contexto de job"""
        
    def log_job_event(self, job_id, event_type, message):
        """Registra evento de job"""
        
    def update_job_progress(self, job_id, progress_percentage):
        """Atualiza progresso do job"""
        
    def complete_job(self, job_id, status, metrics):
        """Finaliza job com métricas"""
```

**Responsabilidades**:
- Controle de jobs ETL
- Logging estruturado
- Métricas de performance
- Checkpoints de progresso
- Auditoria de execução

#### Redis Cache (`redis_cache.py`)
```python
class RedisCache:
    """Sistema de cache inteligente"""
    
    def __init__(self, ttl_hours=24):
        self.redis_client = redis.Redis()
        self.ttl = ttl_hours * 3600
    
    def get(self, key):
        """Busca valor no cache"""
        
    def set(self, key, value, ttl=None):
        """Armazena valor no cache"""
        
    def invalidate(self, pattern):
        """Invalida cache por padrão"""
        
    def get_stats(self):
        """Retorna estatísticas do cache"""
```

**Responsabilidades**:
- Cache de dados da API
- TTL configurável
- Invalidação inteligente
- Fallback automático
- Métricas de performance

### 3. Configuration Layer

#### Config Manager (`config.py`)
```python
class Config:
    """Gerenciador de configuração centralizada"""
    
    @classmethod
    def validate(cls):
        """Valida configurações obrigatórias"""
        
    @classmethod
    def get_api_key(cls):
        """Retorna API key do Sportmonks"""
        
    @classmethod
    def get_supabase_config(cls):
        """Retorna configuração do Supabase"""
        
    @classmethod
    def get_rate_limit(cls):
        """Retorna configuração de rate limiting"""
```

**Responsabilidades**:
- Validação de configurações
- Gerenciamento de secrets
- Suporte a múltiplos ambientes
- Configurações centralizadas

### 4. Scripts Layer

#### ETL Scripts (`scripts/etl/`)
- **01_popular_leagues_seasons.py**: Popula ligas e temporadas
- **02_popular_teams.py**: Popula times
- **03_popular_fixtures.py**: Popula partidas
- **04_popular_events.py**: Popula eventos das partidas

#### Sync Scripts (`scripts/sync/`)
- **sync_brasileirao_final.py**: Sincronização específica do Brasileirão
- **sync_premier_league.py**: Sincronização da Premier League
- **incremental_sync.py**: Sincronização incremental

#### Maintenance Scripts (`scripts/maintenance/`)
- **cleanup_old_data.py**: Limpeza de dados antigos
- **optimize_database.py**: Otimização do banco
- **backup_data.py**: Backup de dados

#### Testing Scripts (`scripts/testing/`)
- **test_api_connection.py**: Teste de conectividade
- **test_data_quality.py**: Validação de qualidade
- **performance_test.py**: Testes de performance

#### Utility Scripts (`scripts/utils/`)
- **data_validator.py**: Validador de dados
- **export_data.py**: Exportação de dados
- **import_data.py**: Importação de dados

## Fluxo de Dados Detalhado

### 1. Sincronização de Dados Base

```mermaid
sequenceDiagram
    participant CLI as CLI
    participant ETL as ETL Process
    participant SM as Sportmonks Client
    participant CACHE as Redis Cache
    participant SB as Supabase Client
    participant DB as Database
    
    CLI->>ETL: sync_base_data()
    ETL->>SM: get_states()
    SM->>CACHE: check_cache("states")
    alt Cache Hit
        CACHE-->>SM: return cached data
    else Cache Miss
        SM->>SM: make_api_request()
        SM->>CACHE: store_in_cache()
    end
    SM-->>ETL: return states data
    ETL->>SB: upsert_states(states)
    SB->>DB: INSERT/UPDATE states
    DB-->>SB: confirm operation
    SB-->>ETL: success
    ETL->>ETL: checkpoint("states_completed")
    ETL->>SM: get_types()
    Note over ETL,SM: Repeat for types and countries
    ETL-->>CLI: sync_base_data completed
```

### 2. Sincronização de Ligas

```mermaid
sequenceDiagram
    participant CLI as CLI
    participant ETL as ETL Process
    participant SM as Sportmonks Client
    participant SB as Supabase Client
    participant DB as Database
    
    CLI->>ETL: sync_leagues([648, 651])
    loop For each league_id
        ETL->>SM: get_league_by_id(id, include='seasons')
        SM-->>ETL: league + seasons data
        ETL->>ETL: extract_seasons(league)
    end
    ETL->>SB: upsert_leagues(leagues_data)
    SB->>DB: INSERT/UPDATE leagues
    ETL->>SB: upsert_seasons(seasons_data)
    SB->>DB: INSERT/UPDATE seasons
    ETL-->>CLI: leagues sync completed
```

### 3. Sincronização de Partidas

```mermaid
sequenceDiagram
    participant CLI as CLI
    participant ETL as ETL Process
    participant SM as Sportmonks Client
    participant SB as Supabase Client
    participant DB as Database
    
    CLI->>ETL: sync_fixtures_by_date_range("2024-01-01", "2024-01-31")
    ETL->>SM: get_fixtures_by_date_range(start, end, include='participants;venue')
    SM-->>ETL: fixtures data
    ETL->>ETL: extract_venues(fixtures)
    ETL->>SB: upsert_venues(venues_data)
    ETL->>SB: upsert_fixtures(fixtures_data)
    loop For each fixture
        ETL->>SB: upsert_fixture_participants(fixture_id, participants)
    end
    ETL-->>CLI: fixtures sync completed
```

## Padrões de Interação

### 1. Error Handling
- **Retry Pattern**: Tentativas automáticas com backoff exponencial
- **Circuit Breaker**: Proteção contra falhas em cascata
- **Graceful Degradation**: Fallback para cache quando API falha

### 2. Data Consistency
- **Upsert Operations**: Evita duplicatas e permite atualizações
- **Transaction Boundaries**: Operações atômicas quando possível
- **Validation**: Validação de dados antes do armazenamento

### 3. Performance Optimization
- **Caching Strategy**: Cache inteligente com TTL
- **Batch Processing**: Processamento em lotes
- **Rate Limiting**: Controle de requisições à API
- **Connection Pooling**: Reutilização de conexões

### 4. Monitoring and Observability
- **Structured Logging**: Logs estruturados com contexto
- **Metrics Collection**: Métricas de performance e uso
- **Health Checks**: Verificação de saúde dos componentes
- **Distributed Tracing**: Rastreamento de requisições

## Dependências entre Componentes

### Dependências Diretas
- **ETL Process** → Sportmonks Client, Supabase Client, ETL Metadata
- **Sportmonks Client** → Redis Cache, Config
- **Supabase Client** → Config
- **ETL Metadata** → Supabase Client
- **Redis Cache** → Config

### Dependências Indiretas
- **CLI** → ETL Process → Todos os componentes Core
- **Scripts** → ETL Process → Componentes Core
- **All Components** → Config → Settings/Environment

## Extensibilidade

### Pontos de Extensão
1. **Novos Clientes de API**: Implementar interface comum
2. **Novos Tipos de Dados**: Adicionar métodos no ETL Process
3. **Novos Scripts**: Seguir padrão estabelecido
4. **Novos Comandos CLI**: Adicionar comandos na CLI
5. **Novos Tipos de Cache**: Implementar interface de cache

### Interfaces Padronizadas
- **APIClient**: Interface para clientes de API
- **DataProcessor**: Interface para processadores de dados
- **CacheProvider**: Interface para provedores de cache
- **JobContext**: Interface para contexto de jobs

---

**Última atualização**: 2025-01-13  
**Versão**: 2.0  
**Responsável**: Technical Writer
