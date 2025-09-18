# Relatório de Implementação da Query de Coleta Incremental (2025-01-17)

## Objetivo
Implementar função SQL para identificar fixtures que precisam ser coletadas/atualizadas para coleta incremental otimizada.

## Status da Task
✅ **CONCLUÍDA** - Task 2.1: Implementar Query de Coleta Incremental

## Funções SQL Implementadas

### 1. `get_fixtures_for_incremental_collection()`
**Propósito**: Identifica fixtures que precisam ser coletadas/atualizadas

**Parâmetros**:
- `p_batch_size` (INTEGER, DEFAULT 100): Tamanho do lote de fixtures a retornar
- `p_league_id` (INTEGER, DEFAULT NULL): Filtrar por liga específica
- `p_season_id` (INTEGER, DEFAULT NULL): Filtrar por temporada específica
- `p_hours_back` (INTEGER, DEFAULT 24): Horas para trás para considerar atualizações

**Retorna**:
- `fixture_id`: ID da fixture
- `league_id`: ID da liga
- `season_id`: ID da temporada
- `home_team_id`: ID do time da casa
- `away_team_id`: ID do time visitante
- `starting_at`: Data/hora da partida
- `collection_reason`: Motivo da coleta (NEVER_PROCESSED, UPDATED_RECENTLY, etc.)
- `priority_score`: Score de prioridade (100 = máxima, 30 = baixa)

**Critérios de Priorização**:
1. **NEVER_PROCESSED** (Score: 100): Fixtures nunca processadas (`last_processed_at IS NULL`)
2. **UPDATED_RECENTLY** (Score: 90): Fixtures atualizadas recentemente (`updated_at > last_processed_at`)
3. **INCOMPLETE_DATA** (Score: 70): Fixtures com dados incompletos (sem events/lineups/statistics)
4. **LOW_QUALITY** (Score: 50): Fixtures com baixa qualidade de dados (`data_quality_score < 80`)
5. **OLD_ETL_VERSION** (Score: 30): Fixtures com versão ETL antiga (`etl_version != 'v1.0'`)

### 2. `update_fixture_etl_metadata()`
**Propósito**: Atualiza metadados ETL após processamento de uma fixture

**Parâmetros**:
- `p_fixture_id`: ID da fixture
- `p_etl_version`: Versão do ETL (DEFAULT 'v1.0')
- `p_data_quality_score`: Score de qualidade (DEFAULT 100)
- `p_has_events`: Flag de eventos disponíveis
- `p_has_lineups`: Flag de escalações disponíveis
- `p_has_statistics`: Flag de estatísticas disponíveis

### 3. `get_incremental_collection_stats()`
**Propósito**: Retorna estatísticas para monitoramento da coleta incremental

**Retorna**:
- `total_fixtures`: Total de fixtures na base
- `unprocessed_fixtures`: Fixtures nunca processadas
- `recently_updated_fixtures`: Fixtures atualizadas nas últimas 24h
- `incomplete_data_fixtures`: Fixtures com dados incompletos
- `low_quality_fixtures`: Fixtures com baixa qualidade
- `old_version_fixtures`: Fixtures com versão ETL antiga
- `last_collection_time`: Timestamp da última coleta

## Resultados dos Testes

### Teste 1: Identificação de Fixtures para Coleta
```sql
SELECT * FROM get_fixtures_for_incremental_collection(
    p_batch_size := 5,
    p_hours_back := 24
);
```

**Resultado**: 5 fixtures identificadas como `NEVER_PROCESSED` com prioridade máxima (score: 100)

### Teste 2: Estatísticas Gerais
```sql
SELECT * FROM get_incremental_collection_stats();
```

**Resultado**:
- Total de fixtures: 67,085
- Fixtures não processadas: 67,085 (100%)
- Fixtures com dados incompletos: 67,065
- Última coleta: NULL (nunca executada)

## Benefícios da Implementação

### 1. Performance Otimizada
- Utiliza índices especializados criados na Task 1
- Consultas eficientes com `UNION ALL` e `ORDER BY`
- Filtros otimizados por data e flags

### 2. Priorização Inteligente
- Sistema de scores para priorizar fixtures mais importantes
- Foco em fixtures recentes para dados incompletos
- Evita reprocessamento desnecessário

### 3. Flexibilidade
- Parâmetros configuráveis para diferentes cenários
- Filtros por liga/temporada para processamento em chunks
- Tamanho de lote ajustável

### 4. Monitoramento
- Estatísticas detalhadas para acompanhamento
- Identificação de problemas de qualidade
- Rastreamento de progresso da coleta

## Próximos Passos
Com a query de coleta incremental implementada e testada, o próximo passo é criar o **Script Python de Coleta Incremental** (Task 2.2) que utilizará essas funções SQL para executar a coleta real via API Sportmonks.

## Conclusão
A função de coleta incremental está funcionando perfeitamente, identificando corretamente fixtures que precisam ser processadas com sistema de priorização inteligente. A base está preparada para implementação do script Python de coleta.
