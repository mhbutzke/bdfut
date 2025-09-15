# Changelog da API - BDFut 📝

## Visão Geral

Este documento registra todas as mudanças na API do sistema BDFut, incluindo novos endpoints, modificações, depreciações e correções.

## Formato do Changelog

- **[Adicionado]** para novas funcionalidades
- **[Modificado]** para mudanças em funcionalidades existentes
- **[Depreciado]** para funcionalidades que serão removidas
- **[Removido]** para funcionalidades removidas
- **[Corrigido]** para correções de bugs
- **[Segurança]** para correções de segurança

---

## [2.0.0] - 2025-01-13

### [Adicionado]

#### Sportmonks Client
- **Novo método**: `get_cache_stats()` - Retorna estatísticas do cache
- **Novo método**: `get_paginated_data()` - Busca dados paginados de qualquer endpoint
- **Novo método**: `get_coaches_by_team()` - Busca técnicos de um time
- **Novo método**: `get_standings_by_season()` - Busca classificação de temporada
- **Novo parâmetro**: `include` em todos os métodos GET para campos relacionados
- **Nova funcionalidade**: Rate limiting inteligente com janela deslizante
- **Nova funcionalidade**: Cache Redis com fallback automático
- **Nova funcionalidade**: Retry automático com backoff exponencial

#### Supabase Client
- **Novo método**: `upsert_fixture_participants()` - Upsert de participantes de partida
- **Novo método**: `upsert_fixture_events()` - Upsert de eventos de partida
- **Novo método**: `upsert_states()` - Upsert de estados
- **Novo método**: `upsert_types()` - Upsert de tipos
- **Nova funcionalidade**: Suporte a schemas múltiplos
- **Nova funcionalidade**: Validação automática de dados

#### ETL Process
- **Novo método**: `sync_base_data()` - Sincronização de dados base
- **Novo método**: `sync_recent_fixtures()` - Sincronização de partidas recentes
- **Novo método**: `sync_fixture_details()` - Sincronização de detalhes de partida
- **Novo método**: `incremental_sync()` - Sincronização incremental
- **Novo parâmetro**: `include_details` em `sync_fixtures_by_date_range()`
- **Nova funcionalidade**: Sistema de checkpoints
- **Nova funcionalidade**: Logging estruturado

#### ETL Metadata
- **Nova classe**: `ETLMetadataManager` - Gerenciamento de metadados
- **Novo método**: `create_job()` - Criação de jobs ETL
- **Novo método**: `complete_job()` - Finalização de jobs
- **Novo método**: `create_checkpoint()` - Criação de checkpoints
- **Novo método**: `log_job_event()` - Log de eventos de job
- **Novo método**: `get_job_stats()` - Estatísticas de jobs
- **Novo método**: `get_recent_jobs()` - Jobs recentes
- **Novo método**: `get_job_logs()` - Logs de job específico

#### Redis Cache
- **Nova classe**: `RedisCache` - Sistema de cache inteligente
- **Novo método**: `get()` - Busca valor no cache
- **Novo método**: `set()` - Armazena valor no cache
- **Novo método**: `delete()` - Remove valor do cache
- **Novo método**: `invalidate_pattern()` - Invalidação por padrão
- **Novo método**: `get_stats()` - Estatísticas do cache
- **Novo método**: `get_comprehensive_stats()` - Estatísticas detalhadas
- **Nova funcionalidade**: Fallback automático para cache em memória
- **Nova funcionalidade**: TTL configurável

#### Configuration
- **Nova classe**: `Config` - Configuração centralizada
- **Novo método**: `validate()` - Validação de configurações
- **Novo método**: `get_sportmonks_config()` - Configuração Sportmonks
- **Novo método**: `get_supabase_config()` - Configuração Supabase
- **Novo método**: `get_rate_limit_config()` - Configuração rate limiting
- **Nova funcionalidade**: Suporte a múltiplos ambientes
- **Nova funcionalidade**: Validação automática de secrets

#### CLI Commands
- **Novo comando**: `show-config` - Exibe configuração atual
- **Novo comando**: `test-connection` - Testa conectividade
- **Novo comando**: `sync-base` - Sincronização de dados base
- **Novo comando**: `sync-leagues` - Sincronização de ligas
- **Novo comando**: `full-sync` - Sincronização completa
- **Novo comando**: `incremental` - Sincronização incremental
- **Nova funcionalidade**: Validação de parâmetros
- **Nova funcionalidade**: Tratamento de erros

### [Modificado]

#### Sportmonks Client
- **Modificado**: `__init__()` - Agora aceita parâmetros de cache
- **Modificado**: Todos os métodos GET - Agora suportam parâmetro `include`
- **Modificado**: Rate limiting - Implementado controle inteligente
- **Modificado**: Tratamento de erros - Melhorado com retry automático

#### Supabase Client
- **Modificado**: `__init__()` - Validação automática de configuração
- **Modificado**: Todos os métodos upsert - Melhor validação de dados
- **Modificado**: Tratamento de erros - Logging mais detalhado

#### ETL Process
- **Modificado**: `sync_leagues()` - Agora aceita lista de IDs de ligas
- **Modificado**: `sync_fixtures_by_date_range()` - Suporte a detalhes opcionais
- **Modificado**: Tratamento de erros - Melhor recuperação de falhas

### [Corrigido]

#### Sportmonks Client
- **Corrigido**: Rate limiting não funcionava corretamente
- **Corrigido**: Cache não era invalidado adequadamente
- **Corrigido**: Retry não respeitava backoff exponencial
- **Corrigido**: Tratamento de erros HTTP inadequado

#### Supabase Client
- **Corrigido**: Upsert não funcionava com dados nulos
- **Corrigido**: Validação de dados insuficiente
- **Corrigido**: Tratamento de relacionamentos inadequado

#### ETL Process
- **Corrigido**: Sincronização não respeitava dependências
- **Corrigido**: Checkpoints não eram salvos corretamente
- **Corrigido**: Logging não incluía contexto suficiente

### [Segurança]

#### Configuration
- **Segurança**: Validação obrigatória de secrets
- **Segurança**: Mascaramento de API keys em logs
- **Segurança**: Suporte a variáveis de ambiente seguras

---

## [1.0.0] - 2024-12-01

### [Adicionado]

#### Versão Inicial
- **Sportmonks Client**: Cliente básico para API Sportmonks
- **Supabase Client**: Cliente básico para Supabase
- **ETL Process**: Processo básico de ETL
- **Scripts**: Scripts básicos de sincronização

### [Modificado]

#### N/A
- Primeira versão do sistema

### [Corrigido]

#### N/A
- Primeira versão do sistema

---

## Roadmap de Mudanças Futuras

### [2.1.0] - Planejado para 2025-02-01

#### [Adicionado]
- **Dashboard Web**: Interface web para monitoramento
- **API REST**: Exposição de dados via API REST
- **Webhooks**: Sistema de notificações
- **Batch Operations**: Operações em lote otimizadas
- **Data Validation**: Validação avançada de dados

#### [Modificado]
- **Cache**: Implementação de cache distribuído
- **Rate Limiting**: Rate limiting adaptativo
- **Error Handling**: Tratamento de erros mais robusto

### [2.2.0] - Planejado para 2025-03-01

#### [Adicionado]
- **Machine Learning**: Análise preditiva de dados
- **Real-time Sync**: Sincronização em tempo real
- **Advanced Analytics**: Dashboards avançados
- **Data Export**: Exportação de dados em múltiplos formatos

#### [Depreciado]
- **Legacy Scripts**: Scripts antigos serão depreciados
- **Old CLI Commands**: Comandos CLI antigos serão removidos

### [3.0.0] - Planejado para 2025-06-01

#### [Adicionado]
- **Microservices**: Arquitetura de microserviços
- **GraphQL API**: API GraphQL completa
- **Advanced Caching**: Cache inteligente com ML
- **Multi-tenant**: Suporte a múltiplos tenants

#### [Removido]
- **Legacy APIs**: APIs antigas serão removidas
- **Deprecated Methods**: Métodos depreciados serão removidos

---

## Guia de Migração

### Migração de 1.0.0 para 2.0.0

#### Breaking Changes

1. **Sportmonks Client**
   ```python
   # Antes (1.0.0)
   client = SportmonksClient()
   
   # Depois (2.0.0)
   client = SportmonksClient(enable_cache=True, use_redis=True)
   ```

2. **Supabase Client**
   ```python
   # Antes (1.0.0)
   client = SupabaseClient()
   
   # Depois (2.0.0) - Validação automática
   client = SupabaseClient()  # Validação automática
   ```

3. **ETL Process**
   ```python
   # Antes (1.0.0)
   etl = ETLProcess()
   etl.sync_leagues()
   
   # Depois (2.0.0)
   etl = ETLProcess()
   etl.sync_leagues([648, 651])  # IDs específicos
   ```

#### Novas Funcionalidades

1. **Sistema de Cache**
   ```python
   # Novo em 2.0.0
   from bdfut.core.redis_cache import RedisCache
   cache = RedisCache()
   cache.set('key', 'value', ttl=3600)
   ```

2. **Metadados ETL**
   ```python
   # Novo em 2.0.0
   from bdfut.core.etl_metadata import ETLMetadataManager
   metadata = ETLMetadataManager()
   job_id = metadata.create_job('sync_leagues', 'etl', 'script.py')
   ```

3. **Configuração Centralizada**
   ```python
   # Novo em 2.0.0
   from bdfut.config.config import Config
   Config.validate()  # Validação automática
   ```

### Migração de 2.0.0 para 2.1.0 (Futuro)

#### Preparação

1. **Atualizar Dependências**
   ```bash
   pip install -U bdfut
   ```

2. **Migrar Configurações**
   ```bash
   # Novas variáveis de ambiente
   DASHBOARD_ENABLED=true
   API_REST_ENABLED=true
   ```

3. **Atualizar Código**
   ```python
   # Novos imports
   from bdfut.web.dashboard import Dashboard
   from bdfut.api.rest import RESTAPI
   ```

---

## Compatibilidade

### Versões Suportadas

| Versão | Status | Suporte Até |
|--------|--------|-------------|
| 2.0.x  | Atual  | 2025-12-31  |
| 1.0.x  | Depreciada | 2025-06-30 |

### Python Versions

| Versão | Status |
|--------|--------|
| 3.8+   | Suportada |
| 3.7    | Depreciada |
| < 3.7  | Não suportada |

### Dependências

| Pacote | Versão Mínima | Versão Recomendada |
|--------|---------------|-------------------|
| requests | 2.25.0 | 2.31.0 |
| supabase | 1.0.0 | 2.0.0 |
| redis | 3.5.0 | 4.5.0 |
| tenacity | 8.0.0 | 8.2.0 |

---

## Reportar Problemas

### Como Reportar

1. **GitHub Issues**: [Criar issue](https://github.com/bdfut/bdfut/issues)
2. **Email**: support@bdfut.com
3. **Discord**: [Servidor da comunidade](https://discord.gg/bdfut)

### Informações Necessárias

- Versão do BDFut
- Versão do Python
- Sistema operacional
- Logs de erro
- Código de exemplo
- Passos para reproduzir

### Template de Bug Report

```markdown
## Descrição
Descrição clara do problema

## Versões
- BDFut: 2.0.0
- Python: 3.9.0
- OS: Ubuntu 20.04

## Passos para Reproduzir
1. Execute o comando...
2. Observe o erro...

## Comportamento Esperado
O que deveria acontecer

## Comportamento Atual
O que está acontecendo

## Logs
```
[Logs de erro aqui]
```

## Código de Exemplo
```python
[Código que reproduz o problema]
```
```

---

**Última atualização**: 2025-01-13  
**Versão**: 2.0  
**Responsável**: Technical Writer
