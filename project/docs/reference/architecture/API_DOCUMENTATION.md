# Documentação da API - BDFut 📚

## Visão Geral

Este documento detalha as APIs internas do sistema BDFut, incluindo endpoints dos clientes Sportmonks e Supabase, métodos de ETL, e interfaces de configuração.

## Índice

1. [Sportmonks Client API](#sportmonks-client-api)
2. [Supabase Client API](#supabase-client-api)
3. [ETL Process API](#etl-process-api)
4. [ETL Metadata API](#etl-metadata-api)
5. [Redis Cache API](#redis-cache-api)
6. [Configuration API](#configuration-api)
7. [CLI Commands](#cli-commands)
8. [Exemplos de Uso](#exemplos-de-uso)

---

## Sportmonks Client API

### Classe: `SportmonksClient`

Cliente para interação com a API Sportmonks com rate limiting inteligente e cache.

#### Construtor

```python
SportmonksClient(
    enable_cache: bool = True,
    cache_ttl_hours: int = 24,
    use_redis: bool = True,
    redis_url: Optional[str] = None
)
```

**Parâmetros:**
- `enable_cache`: Habilita sistema de cache
- `cache_ttl_hours`: TTL do cache em horas
- `use_redis`: Usa Redis como cache principal
- `redis_url`: URL do Redis (opcional)

#### Métodos de Dados Base

##### `get_countries(include: Optional[str] = None) -> List[Dict]`

Busca países da API Sportmonks.

**Parâmetros:**
- `include`: Campos relacionados para incluir (opcional)

**Retorno:**
- `List[Dict]`: Lista de países

**Exemplo:**
```python
client = SportmonksClient()
countries = client.get_countries()
```

##### `get_states() -> List[Dict]`

Busca estados/províncias da API Sportmonks.

**Retorno:**
- `List[Dict]`: Lista de estados

##### `get_types() -> List[Dict]`

Busca tipos de competição da API Sportmonks.

**Retorno:**
- `List[Dict]`: Lista de tipos

#### Métodos de Ligas e Temporadas

##### `get_leagues(include: Optional[str] = None) -> List[Dict]`

Busca ligas da API Sportmonks.

**Parâmetros:**
- `include`: Campos relacionados (ex: 'seasons')

**Retorno:**
- `List[Dict]`: Lista de ligas

**Exemplo:**
```python
leagues = client.get_leagues(include='seasons')
```

##### `get_league_by_id(league_id: int, include: Optional[str] = None) -> Dict`

Busca liga específica por ID.

**Parâmetros:**
- `league_id`: ID da liga
- `include`: Campos relacionados

**Retorno:**
- `Dict`: Dados da liga

##### `get_seasons(include: Optional[str] = None) -> List[Dict]`

Busca temporadas da API Sportmonks.

**Parâmetros:**
- `include`: Campos relacionados

**Retorno:**
- `List[Dict]`: Lista de temporadas

##### `get_season_by_id(season_id: int, include: Optional[str] = None) -> Dict`

Busca temporada específica por ID.

**Parâmetros:**
- `season_id`: ID da temporada
- `include`: Campos relacionados

**Retorno:**
- `Dict`: Dados da temporada

#### Métodos de Times e Jogadores

##### `get_teams_by_season(season_id: int, include: Optional[str] = None) -> List[Dict]`

Busca times de uma temporada específica.

**Parâmetros:**
- `season_id`: ID da temporada
- `include`: Campos relacionados (ex: 'venue')

**Retorno:**
- `List[Dict]`: Lista de times

**Exemplo:**
```python
teams = client.get_teams_by_season(season_id=12345, include='venue')
```

##### `get_players_by_team(team_id: int, include: Optional[str] = None) -> List[Dict]`

Busca jogadores de um time específico.

**Parâmetros:**
- `team_id`: ID do time
- `include`: Campos relacionados

**Retorno:**
- `List[Dict]`: Lista de jogadores

##### `get_player_by_id(player_id: int, include: Optional[str] = None) -> Dict`

Busca jogador específico por ID.

**Parâmetros:**
- `player_id`: ID do jogador
- `include`: Campos relacionados

**Retorno:**
- `Dict`: Dados do jogador

##### `get_coaches_by_team(team_id: int, include: Optional[str] = None) -> List[Dict]`

Busca técnicos de um time específico.

**Parâmetros:**
- `team_id`: ID do time
- `include`: Campos relacionados

**Retorno:**
- `List[Dict]`: Lista de técnicos

#### Métodos de Partidas

##### `get_fixtures_by_date_range(start_date: str, end_date: str, include: Optional[str] = None) -> List[Dict]`

Busca partidas em um intervalo de datas.

**Parâmetros:**
- `start_date`: Data inicial (YYYY-MM-DD)
- `end_date`: Data final (YYYY-MM-DD)
- `include`: Campos relacionados (ex: 'participants;venue;events')

**Retorno:**
- `List[Dict]`: Lista de partidas

**Exemplo:**
```python
fixtures = client.get_fixtures_by_date_range(
    start_date='2024-01-01',
    end_date='2024-01-31',
    include='participants;venue;events'
)
```

##### `get_fixture_by_id(fixture_id: int, include: Optional[str] = None) -> Dict`

Busca partida específica por ID.

**Parâmetros:**
- `fixture_id`: ID da partida
- `include`: Campos relacionados

**Retorno:**
- `Dict`: Dados da partida

#### Métodos de Locais e Árbitros

##### `get_venues(include: Optional[str] = None) -> List[Dict]`

Busca estádios/venues da API Sportmonks.

**Parâmetros:**
- `include`: Campos relacionados

**Retorno:**
- `List[Dict]`: Lista de venues

##### `get_referees(include: Optional[str] = None) -> List[Dict]`

Busca árbitros da API Sportmonks.

**Parâmetros:**
- `include`: Campos relacionados

**Retorno:**
- `List[Dict]`: Lista de árbitros

#### Métodos de Classificação

##### `get_standings_by_season(season_id: int, include: Optional[str] = None) -> List[Dict]`

Busca classificação de uma temporada específica.

**Parâmetros:**
- `season_id`: ID da temporada
- `include`: Campos relacionados

**Retorno:**
- `List[Dict]`: Lista de classificações

#### Métodos de Cache e Estatísticas

##### `get_cache_stats() -> Dict`

Retorna estatísticas do cache.

**Retorno:**
- `Dict`: Estatísticas de cache (hits, misses, etc.)

##### `get_paginated_data(endpoint: str, params: Optional[Dict] = None, page: int = 1, per_page: int = 25) -> Dict`

Busca dados paginados de qualquer endpoint.

**Parâmetros:**
- `endpoint`: Endpoint da API
- `params`: Parâmetros da requisição
- `page`: Página atual
- `per_page`: Itens por página

**Retorno:**
- `Dict`: Dados paginados

---

## Supabase Client API

### Classe: `SupabaseClient`

Cliente para interação com o banco de dados Supabase.

#### Construtor

```python
SupabaseClient()
```

#### Métodos de Upsert

##### `upsert_countries(countries: List[Dict]) -> bool`

Insere ou atualiza países no banco de dados.

**Parâmetros:**
- `countries`: Lista de dados de países

**Retorno:**
- `bool`: True se sucesso, False se erro

**Exemplo:**
```python
client = SupabaseClient()
countries_data = [
    {
        'id': 1,
        'name': 'Brazil',
        'iso2': 'BR',
        'iso3': 'BRA'
    }
]
success = client.upsert_countries(countries_data)
```

##### `upsert_leagues(leagues: List[Dict]) -> bool`

Insere ou atualiza ligas no banco de dados.

**Parâmetros:**
- `leagues`: Lista de dados de ligas

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `upsert_seasons(seasons: List[Dict]) -> bool`

Insere ou atualiza temporadas no banco de dados.

**Parâmetros:**
- `seasons`: Lista de dados de temporadas

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `upsert_teams(teams: List[Dict]) -> bool`

Insere ou atualiza times no banco de dados.

**Parâmetros:**
- `teams`: Lista de dados de times

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `upsert_venues(venues: List[Dict]) -> bool`

Insere ou atualiza venues no banco de dados.

**Parâmetros:**
- `venues`: Lista de dados de venues

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `upsert_referees(referees: List[Dict]) -> bool`

Insere ou atualiza árbitros no banco de dados.

**Parâmetros:**
- `referees`: Lista de dados de árbitros

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `upsert_fixtures(fixtures: List[Dict]) -> bool`

Insere ou atualiza partidas no banco de dados.

**Parâmetros:**
- `fixtures`: Lista de dados de partidas

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `upsert_fixture_participants(fixture_id: int, participants: List[Dict]) -> bool`

Insere ou atualiza participantes de uma partida.

**Parâmetros:**
- `fixture_id`: ID da partida
- `participants`: Lista de participantes

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `upsert_fixture_events(fixture_id: int, events: List[Dict]) -> bool`

Insere ou atualiza eventos de uma partida.

**Parâmetros:**
- `fixture_id`: ID da partida
- `events`: Lista de eventos

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `upsert_states(states: List[Dict]) -> bool`

Insere ou atualiza estados no banco de dados.

**Parâmetros:**
- `states`: Lista de dados de estados

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `upsert_types(types: List[Dict]) -> bool`

Insere ou atualiza tipos no banco de dados.

**Parâmetros:**
- `types`: Lista de dados de tipos

**Retorno:**
- `bool`: True se sucesso, False se erro

---

## ETL Process API

### Classe: `ETLProcess`

Coordena o processo de ETL dos dados.

#### Construtor

```python
ETLProcess()
```

#### Métodos de Sincronização

##### `sync_base_data()`

Sincroniza dados base (countries, states, types).

**Exemplo:**
```python
etl = ETLProcess()
etl.sync_base_data()
```

##### `sync_leagues(league_ids: Optional[List[int]] = None)`

Sincroniza ligas e suas temporadas.

**Parâmetros:**
- `league_ids`: Lista de IDs de ligas (opcional, usa ligas principais se None)

**Exemplo:**
```python
etl.sync_leagues([648, 651])  # Brasileirão e Premier League
```

##### `sync_teams_by_season(season_id: int)`

Sincroniza times de uma temporada específica.

**Parâmetros:**
- `season_id`: ID da temporada

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `sync_fixtures_by_date_range(start_date: str, end_date: str, include_details: bool = False)`

Sincroniza partidas em um intervalo de datas.

**Parâmetros:**
- `start_date`: Data inicial (YYYY-MM-DD)
- `end_date`: Data final (YYYY-MM-DD)
- `include_details`: Se deve incluir detalhes completos

**Retorno:**
- `bool`: True se sucesso, False se erro

**Exemplo:**
```python
etl.sync_fixtures_by_date_range(
    start_date='2024-01-01',
    end_date='2024-01-31',
    include_details=True
)
```

##### `sync_recent_fixtures(days_back: int = 7, days_forward: int = 7)`

Sincroniza partidas recentes e próximas.

**Parâmetros:**
- `days_back`: Dias para trás
- `days_forward`: Dias para frente

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `sync_fixture_details(fixture_id: int)`

Sincroniza detalhes completos de uma partida específica.

**Parâmetros:**
- `fixture_id`: ID da partida

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `full_sync()`

Executa sincronização completa dos dados principais.

**Exemplo:**
```python
etl.full_sync()
```

##### `incremental_sync()`

Executa sincronização incremental (apenas atualizações).

**Exemplo:**
```python
etl.incremental_sync()
```

---

## ETL Metadata API

### Classe: `ETLMetadataManager`

Gerenciador de metadados do ETL.

#### Construtor

```python
ETLMetadataManager()
```

#### Métodos de Jobs

##### `create_job(job_name: str, job_type: str, script_path: str) -> str`

Cria um novo job ETL.

**Parâmetros:**
- `job_name`: Nome do job
- `job_type`: Tipo do job
- `script_path`: Caminho do script

**Retorno:**
- `str`: ID do job criado

##### `complete_job(job_id: str, status: str, metrics: Dict) -> bool`

Finaliza um job ETL.

**Parâmetros:**
- `job_id`: ID do job
- `status`: Status final (SUCCESS, FAILED, etc.)
- `metrics`: Métricas finais

**Retorno:**
- `bool`: True se sucesso, False se erro

#### Métodos de Checkpoints

##### `create_checkpoint(job_id: str, checkpoint_name: str, data: Dict, progress_percentage: float) -> bool`

Cria um checkpoint de progresso.

**Parâmetros:**
- `job_id`: ID do job
- `checkpoint_name`: Nome do checkpoint
- `data`: Dados do checkpoint
- `progress_percentage`: Percentual de progresso

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `get_checkpoint(job_id: str, checkpoint_name: str) -> Optional[Dict]`

Recupera um checkpoint.

**Parâmetros:**
- `job_id`: ID do job
- `checkpoint_name`: Nome do checkpoint

**Retorno:**
- `Optional[Dict]`: Dados do checkpoint ou None

#### Métodos de Logging

##### `log_job_event(job_id: str, level: str, message: str, data: Optional[Dict] = None) -> bool`

Registra um evento de job.

**Parâmetros:**
- `job_id`: ID do job
- `level`: Nível do log (INFO, WARNING, ERROR)
- `message`: Mensagem do log
- `data`: Dados adicionais (opcional)

**Retorno:**
- `bool`: True se sucesso, False se erro

#### Métodos de Estatísticas

##### `get_job_stats() -> Dict[str, Any]`

Retorna estatísticas gerais dos jobs.

**Retorno:**
- `Dict[str, Any]`: Estatísticas dos jobs

##### `get_recent_jobs(limit: int = 10, job_type: Optional[str] = None) -> List[Dict]`

Retorna jobs recentes.

**Parâmetros:**
- `limit`: Limite de jobs
- `job_type`: Tipo de job (opcional)

**Retorno:**
- `List[Dict]`: Lista de jobs recentes

##### `get_job_logs(job_id: str, level: Optional[str] = None, limit: int = 100) -> List[Dict]`

Retorna logs de um job específico.

**Parâmetros:**
- `job_id`: ID do job
- `level`: Nível do log (opcional)
- `limit`: Limite de logs

**Retorno:**
- `List[Dict]`: Lista de logs

---

## Redis Cache API

### Classe: `RedisCache`

Sistema de cache inteligente com Redis.

#### Construtor

```python
RedisCache(
    redis_url: Optional[str] = None,
    ttl_hours: int = 24,
    enable_fallback: bool = True
)
```

**Parâmetros:**
- `redis_url`: URL do Redis (opcional)
- `ttl_hours`: TTL padrão em horas
- `enable_fallback`: Habilita cache de fallback

#### Métodos de Cache

##### `get(key: str) -> Optional[Any]`

Busca valor no cache.

**Parâmetros:**
- `key`: Chave do cache

**Retorno:**
- `Optional[Any]`: Valor do cache ou None

##### `set(key: str, value: Any, ttl: Optional[int] = None) -> bool`

Armazena valor no cache.

**Parâmetros:**
- `key`: Chave do cache
- `value`: Valor a armazenar
- `ttl`: TTL em segundos (opcional)

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `delete(key: str) -> bool`

Remove valor do cache.

**Parâmetros:**
- `key`: Chave do cache

**Retorno:**
- `bool`: True se sucesso, False se erro

##### `invalidate_pattern(pattern: str) -> int`

Invalida cache por padrão.

**Parâmetros:**
- `pattern`: Padrão de chaves

**Retorno:**
- `int`: Número de chaves invalidadas

#### Métodos de Estatísticas

##### `get_stats() -> Dict[str, Any]`

Retorna estatísticas do cache.

**Retorno:**
- `Dict[str, Any]`: Estatísticas do cache

##### `get_comprehensive_stats() -> Dict[str, Any]`

Retorna estatísticas detalhadas do cache.

**Retorno:**
- `Dict[str, Any]`: Estatísticas detalhadas

---

## Configuration API

### Classe: `Config`

Gerenciador de configuração centralizada.

#### Métodos Estáticos

##### `validate() -> None`

Valida configurações obrigatórias.

**Exceções:**
- `ValueError`: Se configuração obrigatória estiver ausente

##### `get_sportmonks_config() -> Dict[str, str]`

Retorna configuração do Sportmonks.

**Retorno:**
- `Dict[str, str]`: Configuração do Sportmonks

##### `get_supabase_config() -> Dict[str, str]`

Retorna configuração do Supabase.

**Retorno:**
- `Dict[str, str]`: Configuração do Supabase

##### `get_rate_limit_config() -> Dict[str, int]`

Retorna configuração de rate limiting.

**Retorno:**
- `Dict[str, int]`: Configuração de rate limiting

---

## CLI Commands

### Comandos Principais

#### `show-config`

Exibe configuração atual do sistema.

```bash
bdfut show-config
```

#### `test-connection`

Testa conectividade com APIs externas.

```bash
bdfut test-connection
```

#### `sync-base`

Sincroniza dados base (countries, states, types).

```bash
bdfut sync-base
```

#### `sync-leagues`

Sincroniza ligas específicas.

```bash
bdfut sync-leagues -l 648 -l 651
```

**Opções:**
- `-l, --league-ids`: IDs das ligas (múltiplos permitidos)

#### `full-sync`

Executa sincronização completa.

```bash
bdfut full-sync
```

#### `incremental`

Executa sincronização incremental.

```bash
bdfut incremental
```

---

## Exemplos de Uso

### Exemplo 1: Sincronização Básica

```python
from bdfut.core.etl_process import ETLProcess

# Criar instância do ETL
etl = ETLProcess()

# Sincronizar dados base
etl.sync_base_data()

# Sincronizar ligas principais
etl.sync_leagues()

# Sincronizar partidas recentes
etl.sync_recent_fixtures(days_back=7, days_forward=7)
```

### Exemplo 2: Sincronização Específica

```python
from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient

# Criar clientes
sm_client = SportmonksClient()
sb_client = SupabaseClient()

# Buscar dados específicos
fixtures = sm_client.get_fixtures_by_date_range(
    start_date='2024-01-01',
    end_date='2024-01-31',
    include='participants;venue;events'
)

# Salvar no banco
success = sb_client.upsert_fixtures(fixtures)
```

### Exemplo 3: Uso com Cache

```python
from bdfut.core.redis_cache import RedisCache

# Criar cache
cache = RedisCache(ttl_hours=12)

# Armazenar dados
cache.set('leagues:648', league_data, ttl=3600)

# Recuperar dados
cached_data = cache.get('leagues:648')

# Estatísticas
stats = cache.get_stats()
print(f"Cache hits: {stats['hits']}")
```

### Exemplo 4: Monitoramento de Jobs

```python
from bdfut.core.etl_metadata import ETLMetadataManager

# Criar gerenciador de metadados
metadata = ETLMetadataManager()

# Criar job
job_id = metadata.create_job('sync_leagues', 'etl', 'script.py')

# Log de progresso
metadata.log_job_event(job_id, 'INFO', 'Iniciando sincronização')

# Checkpoint
metadata.create_checkpoint(job_id, 'leagues_synced', {'count': 10}, 50.0)

# Finalizar job
metadata.complete_job(job_id, 'SUCCESS', {'total_records': 100})
```

### Exemplo 5: Tratamento de Erros

```python
from bdfut.core.etl_process import ETLProcess
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

etl = ETLProcess()

try:
    # Tentar sincronização
    success = etl.sync_fixtures_by_date_range('2024-01-01', '2024-01-31')
    
    if success:
        print("Sincronização concluída com sucesso")
    else:
        print("Sincronização falhou")
        
except Exception as e:
    logging.error(f"Erro durante sincronização: {str(e)}")
```

---

## Códigos de Erro

### Sportmonks API

- **429**: Rate limit excedido
- **401**: API key inválida
- **404**: Recurso não encontrado
- **500**: Erro interno do servidor

### Supabase

- **401**: Token de autenticação inválido
- **403**: Permissão negada
- **404**: Tabela não encontrada
- **409**: Conflito de dados

### Sistema Interno

- **CONFIG_ERROR**: Erro de configuração
- **CACHE_ERROR**: Erro de cache
- **VALIDATION_ERROR**: Erro de validação
- **NETWORK_ERROR**: Erro de rede

---

## Limitações e Considerações

### Rate Limiting

- Sportmonks: 3000 requests/hora
- Supabase: Limites baseados no plano
- Redis: Sem limites específicos

### Tamanho de Dados

- Requests individuais: Máximo 25 itens por página
- Batch operations: Máximo 1000 registros por lote
- Cache: Limitado pela memória disponível

### Timeouts

- API Sportmonks: 30 segundos
- Supabase: 60 segundos
- Redis: 5 segundos

---

**Última atualização**: 2025-01-13  
**Versão**: 2.0  
**Responsável**: Technical Writer
