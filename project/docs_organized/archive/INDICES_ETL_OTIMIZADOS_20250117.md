# Relatório de Otimização de Índices para ETL (2025-01-17)

## Objetivo
Otimizar índices da tabela `fixtures` para operações ETL eficientes, incluindo coleta incremental, consultas por chunks e monitoramento de qualidade de dados.

## Status da Task
✅ **CONCLUÍDA** - Task 1.3: Otimizar Índices para ETL

## Índices Criados/Otimizados

### 1. Índices Básicos (Já Existentes)
- `fixtures_pkey` - Chave primária
- `fixtures_sportmonks_id_key` - Chave única Sportmonks ID
- `idx_fixtures_league_id` - Liga
- `idx_fixtures_season_id` - Temporada
- `idx_fixtures_home_team_id` - Time da casa
- `idx_fixtures_away_team_id` - Time visitante
- `idx_fixtures_starting_at` - Data/hora da partida
- `idx_fixtures_state_id` - Estado da partida
- `idx_fixtures_round_id` - Rodada
- `idx_fixtures_stage_id` - Fase
- `idx_fixtures_venue_id` - Local
- `idx_fixtures_referee_id` - Árbitro

### 2. Índices ETL Especializados (Novos)
- `idx_fixtures_etl_composite` - Composto ETL (versão, processamento, qualidade)
- `idx_fixtures_last_processed_at` - Último processamento
- `idx_fixtures_etl_version` - Versão ETL
- `idx_fixtures_data_quality` - Qualidade dos dados
- `idx_fixtures_updated_at_etl` - Atualização para ETL incremental
- `idx_fixtures_incremental_etl` - Composto para processamento incremental

### 3. Índices para Consultas por Chunks (Novos)
- `idx_fixtures_league_season` - Liga + Temporada
- `idx_fixtures_season_date` - Temporada + Data
- `idx_fixtures_league_date` - Liga + Data

### 4. Índices para Flags de Dados (Otimizados)
- `idx_fixtures_has_events` - Tem eventos
- `idx_fixtures_has_lineups` - Tem escalações
- `idx_fixtures_has_statistics` - Tem estatísticas
- `idx_fixtures_has_events_true` - Com eventos (otimizado)
- `idx_fixtures_has_lineups_true` - Com escalações (otimizado)
- `idx_fixtures_has_statistics_true` - Com estatísticas (otimizado)
- `idx_fixtures_complete_data` - Dados completos
- `idx_fixtures_missing_data` - Dados faltantes

### 5. Índices para Qualidade de Dados (Novos)
- `idx_fixtures_low_quality` - Baixa qualidade (< 80)
- `idx_fixtures_unprocessed` - Não processadas
- `idx_fixtures_old_etl_version` - Versão ETL antiga

### 6. Índices para Consultas Específicas
- `idx_fixtures_match_result` - Resultado da partida
- `idx_fixtures_scores` - Placar (home_score, away_score)
- `idx_fixtures_teams` - Composto times (home, away)
- `idx_fixtures_date` - Data da partida

## Benefícios da Otimização

### 1. Performance ETL
- **Coleta Incremental**: Índices otimizados para `last_processed_at` e `updated_at`
- **Consultas por Chunks**: Índices compostos para liga+temporada e temporada+data
- **Processamento em Lote**: Índices especializados para flags de dados

### 2. Monitoramento
- **Qualidade de Dados**: Índices para identificar fixtures com problemas
- **Status de Processamento**: Índices para fixtures não processadas ou com versão antiga
- **Dados Completos**: Índices para identificar fixtures com dados completos

### 3. Consultas Frequentes
- **Por Liga/Temporada**: Otimização para consultas de relatórios
- **Por Data**: Otimização para consultas temporais
- **Por Times**: Otimização para análises de performance

## Estatísticas dos Índices
- **Total de Índices**: 35
- **Índices Básicos**: 12
- **Índices ETL**: 6
- **Índices Chunks**: 3
- **Índices Flags**: 8
- **Índices Qualidade**: 3
- **Índices Específicos**: 3

## Próximos Passos
Com a otimização de índices concluída, o próximo passo é implementar a **Coleta Incremental** (Task 2), que se beneficiará significativamente desses índices otimizados.

## Conclusão
A tabela `fixtures` agora possui índices otimizados para todas as operações ETL essenciais, garantindo performance eficiente para coleta incremental, processamento em chunks e monitoramento de qualidade de dados.
