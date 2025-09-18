-- Migration: Limpeza da tabela fixtures
-- Data: 2025-09-17
-- Objetivo: Remover campos duplicados e desnecessários da tabela fixtures

-- 1. Remover campos duplicados/desnecessários
ALTER TABLE fixtures DROP COLUMN IF EXISTS venue;  -- Substituído por venue_name
ALTER TABLE fixtures DROP COLUMN IF EXISTS referee;  -- Substituído por referee_name
ALTER TABLE fixtures DROP COLUMN IF EXISTS name;  -- Não usado
ALTER TABLE fixtures DROP COLUMN IF EXISTS result_info;  -- Não usado
ALTER TABLE fixtures DROP COLUMN IF EXISTS leg;  -- Não usado
ALTER TABLE fixtures DROP COLUMN IF EXISTS details;  -- Não usado
ALTER TABLE fixtures DROP COLUMN IF EXISTS tie_breaker_rule;  -- Não usado

-- 2. Adicionar campos que estão faltando baseados na API
ALTER TABLE fixtures ADD COLUMN IF NOT EXISTS sport_id INTEGER;
ALTER TABLE fixtures ADD COLUMN IF NOT EXISTS group_id INTEGER;
ALTER TABLE fixtures ADD COLUMN IF NOT EXISTS aggregate_id INTEGER;
ALTER TABLE fixtures ADD COLUMN IF NOT EXISTS has_premium_odds BOOLEAN DEFAULT FALSE;
ALTER TABLE fixtures ADD COLUMN IF NOT EXISTS starting_at_timestamp INTEGER;

-- 3. Renomear match_date para starting_at se necessário (verificar se são diferentes)
-- ALTER TABLE fixtures RENAME COLUMN match_date TO starting_at;

-- 4. Adicionar comentários para documentar a estrutura
COMMENT ON TABLE fixtures IS 'Tabela de fixtures com dados enriquecidos da API Sportmonks';
COMMENT ON COLUMN fixtures.sportmonks_id IS 'ID da fixture na API Sportmonks';
COMMENT ON COLUMN fixtures.league_id IS 'ID da liga';
COMMENT ON COLUMN fixtures.league_name IS 'Nome da liga';
COMMENT ON COLUMN fixtures.season_id IS 'ID da temporada';
COMMENT ON COLUMN fixtures.season_name IS 'Nome da temporada';
COMMENT ON COLUMN fixtures.venue_id IS 'ID do estádio';
COMMENT ON COLUMN fixtures.venue_name IS 'Nome do estádio';
COMMENT ON COLUMN fixtures.state_id IS 'ID do estado da partida';
COMMENT ON COLUMN fixtures.state_name IS 'Nome do estado da partida';
COMMENT ON COLUMN fixtures.round_id IS 'ID da rodada';
COMMENT ON COLUMN fixtures.round_name IS 'Nome da rodada';
COMMENT ON COLUMN fixtures.stage_id IS 'ID da fase';
COMMENT ON COLUMN fixtures.stage_name IS 'Nome da fase';
COMMENT ON COLUMN fixtures.home_team_id IS 'ID do time da casa';
COMMENT ON COLUMN fixtures.home_team_name IS 'Nome do time da casa';
COMMENT ON COLUMN fixtures.away_team_id IS 'ID do time visitante';
COMMENT ON COLUMN fixtures.away_team_name IS 'Nome do time visitante';
COMMENT ON COLUMN fixtures.referee_id IS 'ID do árbitro principal';
COMMENT ON COLUMN fixtures.referee_name IS 'Nome do árbitro principal';
