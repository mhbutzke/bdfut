-- Migração: Otimizar Índices para Performance
-- TASK-DB-003: Otimizar Índices para Performance
-- Data: 2025-01-13
-- Agente: Database Specialist 🗄️

-- Baseado na auditoria de índices, implementando otimizações identificadas

-- 1. REMOVER ÍNDICES NÃO UTILIZADOS (25 índices identificados)
-- Estes índices nunca foram usados e podem ser removidos com segurança

-- API Cache - índices não utilizados
DROP INDEX IF EXISTS idx_cache_expires;
DROP INDEX IF EXISTS idx_cache_key;

-- Countries - índices não utilizados  
DROP INDEX IF EXISTS idx_countries_continent_id;
DROP INDEX IF EXISTS idx_countries_fifa_name;
DROP INDEX IF EXISTS idx_countries_iso2;
DROP INDEX IF EXISTS idx_countries_iso3;
DROP INDEX IF EXISTS idx_countries_sportmonks_id;

-- Seasons - índices não utilizados
DROP INDEX IF EXISTS idx_seasons_sportmonks_id;
DROP INDEX IF EXISTS idx_seasons_ending_at;

-- Types - índices não utilizados
DROP INDEX IF EXISTS idx_types_code;

-- Venues - índices não utilizados
DROP INDEX IF EXISTS idx_venues_name;

-- Referees - índices não utilizados
DROP INDEX IF EXISTS idx_referees_name;

-- Coaches - índices não utilizados
DROP INDEX IF EXISTS idx_coaches_name;

-- States - índices não utilizados
DROP INDEX IF EXISTS idx_states_name;

-- Players - índices não utilizados
DROP INDEX IF EXISTS idx_players_name;

-- Match Statistics - índices não utilizados
DROP INDEX IF EXISTS idx_stats_fixture;

-- 2. CRIAR ÍNDICES COMPOSTOS OTIMIZADOS

-- Índice composto para queries frequentes de fixtures por temporada e data
CREATE INDEX CONCURRENTLY idx_fixtures_season_date 
ON fixtures (season_id, match_date DESC);

-- Índice composto para queries de eventos por fixture e tipo
CREATE INDEX CONCURRENTLY idx_events_fixture_type 
ON match_events (fixture_id, event_type);

-- Índice composto para queries de estatísticas por fixture e time
CREATE INDEX CONCURRENTLY idx_stats_fixture_team 
ON match_statistics (fixture_id, team_id);

-- Índice composto para queries de lineups por fixture e time
CREATE INDEX CONCURRENTLY idx_lineups_fixture_team 
ON match_lineups (fixture_id, team_id);

-- Índice composto para queries de seasons por liga e status
CREATE INDEX CONCURRENTLY idx_seasons_league_current 
ON seasons (league_id, is_current);

-- Índice composto para queries de types por modelo e grupo
CREATE INDEX CONCURRENTLY idx_types_model_group 
ON types (model_type, stat_group);

-- 3. CRIAR ÍNDICES PARCIAIS PARA OTIMIZAÇÃO

-- Índice parcial para fixtures futuras (mais consultadas)
CREATE INDEX CONCURRENTLY idx_fixtures_future 
ON fixtures (match_date, league_id, season_id) 
WHERE match_date >= CURRENT_DATE;

-- Índice parcial para seasons ativas (mais consultadas)
CREATE INDEX CONCURRENTLY idx_seasons_active 
ON seasons (league_id, start_date, end_date) 
WHERE is_current = true OR finished = false;

-- Índice parcial para eventos de gol (mais consultados)
CREATE INDEX CONCURRENTLY idx_events_goals 
ON match_events (fixture_id, minute, team_id) 
WHERE event_type IN ('goal', 'own_goal', 'penalty');

-- Índice parcial para estatísticas com dados completos
CREATE INDEX CONCURRENTLY idx_stats_complete 
ON match_statistics (fixture_id, team_id, shots_total, ball_possession) 
WHERE shots_total IS NOT NULL AND ball_possession IS NOT NULL;

-- 4. OTIMIZAR ÍNDICES EXISTENTES COM BAIXA EFICIÊNCIA

-- Recriar índice de eventos por tipo com melhor seletividade
DROP INDEX IF EXISTS idx_events_type;
CREATE INDEX CONCURRENTLY idx_events_type_optimized 
ON match_events (event_type) 
WHERE event_type IS NOT NULL;

-- Recriar índice de seasons por liga com melhor performance
DROP INDEX IF EXISTS idx_seasons_league_id;
CREATE INDEX CONCURRENTLY idx_seasons_league_id_optimized 
ON seasons (league_id, is_current, finished);

-- Recriar índice de fixtures por liga com melhor performance  
DROP INDEX IF EXISTS idx_fixtures_league;
CREATE INDEX CONCURRENTLY idx_fixtures_league_optimized 
ON fixtures (league_id, season_id, match_date);

-- 5. CRIAR ÍNDICES PARA QUERIES ESPECÍFICAS IDENTIFICADAS

-- Índice para busca de jogadores por nome (case insensitive)
CREATE INDEX CONCURRENTLY idx_players_name_ci 
ON players USING gin (to_tsvector('portuguese', name));

-- Índice para busca de times por nome (case insensitive)
CREATE INDEX CONCURRENTLY idx_teams_name_ci 
ON teams USING gin (to_tsvector('portuguese', name));

-- Índice para busca de ligas por nome (case insensitive)
CREATE INDEX CONCURRENTLY idx_leagues_name_ci 
ON leagues USING gin (to_tsvector('portuguese', name));

-- Índice para queries de países por código ISO
CREATE INDEX CONCURRENTLY idx_countries_iso_codes 
ON countries (iso2, iso3) 
WHERE iso2 IS NOT NULL AND iso3 IS NOT NULL;

-- 6. CRIAR ÍNDICES PARA FUNCIONALIDADES FUTURAS

-- Índice para queries de ranking de jogadores
CREATE INDEX CONCURRENTLY idx_lineups_player_performance 
ON match_lineups (player_id, rating, minutes_played) 
WHERE rating IS NOT NULL AND minutes_played > 0;

-- Índice para queries de estatísticas de times
CREATE INDEX CONCURRENTLY idx_stats_team_performance 
ON match_statistics (team_id, shots_total, ball_possession, passes_accurate) 
WHERE shots_total IS NOT NULL;

-- Índice para queries de histórico de jogos
CREATE INDEX CONCURRENTLY idx_fixtures_historical 
ON fixtures (home_team_id, away_team_id, match_date) 
WHERE match_date < CURRENT_DATE;

-- Comentários para documentação
COMMENT ON INDEX idx_fixtures_season_date IS 'Índice composto para queries de fixtures por temporada e data';
COMMENT ON INDEX idx_events_fixture_type IS 'Índice composto para queries de eventos por fixture e tipo';
COMMENT ON INDEX idx_stats_fixture_team IS 'Índice composto para queries de estatísticas por fixture e time';
COMMENT ON INDEX idx_lineups_fixture_team IS 'Índice composto para queries de lineups por fixture e time';
COMMENT ON INDEX idx_seasons_league_current IS 'Índice composto para queries de seasons por liga e status';
COMMENT ON INDEX idx_types_model_group IS 'Índice composto para queries de types por modelo e grupo';
COMMENT ON INDEX idx_fixtures_future IS 'Índice parcial para fixtures futuras (mais consultadas)';
COMMENT ON INDEX idx_seasons_active IS 'Índice parcial para seasons ativas (mais consultadas)';
COMMENT ON INDEX idx_events_goals IS 'Índice parcial para eventos de gol (mais consultados)';
COMMENT ON INDEX idx_stats_complete IS 'Índice parcial para estatísticas com dados completos';
COMMENT ON INDEX idx_players_name_ci IS 'Índice de busca full-text para nomes de jogadores';
COMMENT ON INDEX idx_teams_name_ci IS 'Índice de busca full-text para nomes de times';
COMMENT ON INDEX idx_leagues_name_ci IS 'Índice de busca full-text para nomes de ligas';
COMMENT ON INDEX idx_countries_iso_codes IS 'Índice para busca de países por código ISO';
COMMENT ON INDEX idx_lineups_player_performance IS 'Índice para queries de performance de jogadores';
COMMENT ON INDEX idx_stats_team_performance IS 'Índice para queries de performance de times';
COMMENT ON INDEX idx_fixtures_historical IS 'Índice para queries de histórico de jogos';
