-- Migration: 001_enhance_fixtures_table.sql
-- Description: Adiciona colunas essenciais da API Sportmonks à tabela fixtures
-- Date: 2025-01-18
-- Author: Database Optimization Team

-- =====================================================
-- BACKUP SAFETY CHECK
-- =====================================================
-- IMPORTANTE: Execute backup completo antes de aplicar!
-- pg_dump -h [host] -U [user] -d [database] -t fixtures > fixtures_backup_$(date +%Y%m%d_%H%M%S).sql

-- =====================================================
-- PHASE 1: ADD ESSENTIAL COLUMNS FROM API
-- =====================================================

BEGIN;

-- Adicionar colunas principais faltantes da API Sportmonks
ALTER TABLE fixtures 
ADD COLUMN IF NOT EXISTS name VARCHAR(255),
ADD COLUMN IF NOT EXISTS result_info TEXT,
ADD COLUMN IF NOT EXISTS leg VARCHAR(10) DEFAULT '1/1',
ADD COLUMN IF NOT EXISTS details TEXT,
ADD COLUMN IF NOT EXISTS last_processed_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS home_score INTEGER,
ADD COLUMN IF NOT EXISTS away_score INTEGER;

-- Adicionar comentários para documentação
COMMENT ON COLUMN fixtures.name IS 'Nome da partida (ex: "Celtic vs Rangers")';
COMMENT ON COLUMN fixtures.result_info IS 'Informação do resultado (ex: "Celtic won after full-time")';
COMMENT ON COLUMN fixtures.leg IS 'Informação da perna do jogo (ex: "1/1")';
COMMENT ON COLUMN fixtures.details IS 'Detalhes adicionais da partida em JSON';
COMMENT ON COLUMN fixtures.last_processed_at IS 'Timestamp do último processamento pela API';
COMMENT ON COLUMN fixtures.home_score IS 'Placar final do time da casa';
COMMENT ON COLUMN fixtures.away_score IS 'Placar final do time visitante';

-- =====================================================
-- PHASE 2: ADD CALCULATED COLUMNS FOR PERFORMANCE
-- =====================================================

-- Adicionar colunas calculadas para otimização de consultas
ALTER TABLE fixtures 
ADD COLUMN IF NOT EXISTS total_goals INTEGER GENERATED ALWAYS AS (COALESCE(home_score, 0) + COALESCE(away_score, 0)) STORED,
ADD COLUMN IF NOT EXISTS goal_difference INTEGER GENERATED ALWAYS AS (COALESCE(home_score, 0) - COALESCE(away_score, 0)) STORED,
ADD COLUMN IF NOT EXISTS match_result VARCHAR(10);

-- Adicionar comentários para colunas calculadas
COMMENT ON COLUMN fixtures.total_goals IS 'Total de gols na partida (calculado automaticamente)';
COMMENT ON COLUMN fixtures.goal_difference IS 'Diferença de gols (casa - visitante)';
COMMENT ON COLUMN fixtures.match_result IS 'Resultado: home_win, away_win, draw, ou NULL se não finalizado';

-- =====================================================
-- PHASE 3: ADD ETL METADATA COLUMNS
-- =====================================================

-- Adicionar colunas para controle ETL
ALTER TABLE fixtures 
ADD COLUMN IF NOT EXISTS etl_processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS etl_version VARCHAR(20),
ADD COLUMN IF NOT EXISTS data_quality_score DECIMAL(3,2) CHECK (data_quality_score >= 0.00 AND data_quality_score <= 1.00);

-- Adicionar comentários para metadados ETL
COMMENT ON COLUMN fixtures.etl_processed_at IS 'Timestamp do último processamento ETL';
COMMENT ON COLUMN fixtures.etl_version IS 'Versão do processo ETL que processou o registro';
COMMENT ON COLUMN fixtures.data_quality_score IS 'Score de qualidade dos dados (0.00 a 1.00)';

-- =====================================================
-- PHASE 4: CREATE PERFORMANCE INDEXES
-- =====================================================

-- Índices para consultas por nome da partida
CREATE INDEX IF NOT EXISTS idx_fixtures_name ON fixtures(name) WHERE name IS NOT NULL;

-- Índices compostos para consultas frequentes
CREATE INDEX IF NOT EXISTS idx_fixtures_league_season_date ON fixtures(league_id, season_id, starting_at) WHERE starting_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_fixtures_date_state ON fixtures(starting_at, state_id) WHERE starting_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_fixtures_teams ON fixtures(home_team_id, away_team_id) WHERE home_team_id IS NOT NULL AND away_team_id IS NOT NULL;

-- Índices para campos de resultado
CREATE INDEX IF NOT EXISTS idx_fixtures_match_result ON fixtures(match_result) WHERE match_result IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_fixtures_total_goals ON fixtures(total_goals) WHERE total_goals IS NOT NULL;

-- Índices para flags de dados disponíveis (melhorar os existentes)
CREATE INDEX IF NOT EXISTS idx_fixtures_data_flags ON fixtures(has_events, has_lineups, has_statistics) 
WHERE has_events = true OR has_lineups = true OR has_statistics = true;

-- =====================================================
-- PHASE 5: UPDATE MATCH_RESULT FOR EXISTING DATA
-- =====================================================

-- Função para calcular resultado da partida
CREATE OR REPLACE FUNCTION calculate_match_result(home_score INTEGER, away_score INTEGER, state_id INTEGER)
RETURNS VARCHAR(10) AS $$
BEGIN
    -- Só calcular resultado para partidas finalizadas (state_id = 5)
    IF state_id != 5 OR home_score IS NULL OR away_score IS NULL THEN
        RETURN NULL;
    END IF;
    
    IF home_score > away_score THEN
        RETURN 'home_win';
    ELSIF away_score > home_score THEN
        RETURN 'away_win';
    ELSE
        RETURN 'draw';
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Atualizar match_result para dados existentes
UPDATE fixtures 
SET match_result = calculate_match_result(home_score, away_score, state_id)
WHERE match_result IS NULL 
  AND home_score IS NOT NULL 
  AND away_score IS NOT NULL 
  AND state_id = 5;

-- =====================================================
-- PHASE 6: CREATE TRIGGER FOR AUTO-UPDATE MATCH_RESULT
-- =====================================================

-- Função trigger para atualizar match_result automaticamente
CREATE OR REPLACE FUNCTION update_match_result_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.match_result := calculate_match_result(NEW.home_score, NEW.away_score, NEW.state_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Criar trigger para atualização automática
DROP TRIGGER IF EXISTS trigger_update_match_result ON fixtures;
CREATE TRIGGER trigger_update_match_result
    BEFORE INSERT OR UPDATE OF home_score, away_score, state_id ON fixtures
    FOR EACH ROW
    EXECUTE FUNCTION update_match_result_trigger();

-- =====================================================
-- PHASE 7: UPDATE STATISTICS
-- =====================================================

-- Atualizar estatísticas das tabelas
ANALYZE fixtures;

COMMIT;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Verificar se as colunas foram adicionadas corretamente
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'fixtures' 
  AND table_schema = 'public'
  AND column_name IN ('name', 'result_info', 'leg', 'home_score', 'away_score', 'total_goals', 'match_result')
ORDER BY ordinal_position;

-- Verificar índices criados
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'fixtures' 
  AND schemaname = 'public'
  AND indexname LIKE 'idx_fixtures_%'
ORDER BY indexname;

-- Verificar alguns registros atualizados
SELECT 
    fixture_id,
    name,
    home_score,
    away_score,
    total_goals,
    goal_difference,
    match_result,
    etl_processed_at
FROM fixtures 
WHERE home_score IS NOT NULL 
  AND away_score IS NOT NULL
LIMIT 5;

-- =====================================================
-- ROLLBACK SCRIPT (Para emergências)
-- =====================================================
/*
-- CUIDADO: Este script remove as colunas adicionadas!
-- Só execute em caso de emergência e com backup!

BEGIN;

-- Remover trigger e função
DROP TRIGGER IF EXISTS trigger_update_match_result ON fixtures;
DROP FUNCTION IF EXISTS update_match_result_trigger();
DROP FUNCTION IF EXISTS calculate_match_result(INTEGER, INTEGER, INTEGER);

-- Remover índices
DROP INDEX IF EXISTS idx_fixtures_name;
DROP INDEX IF EXISTS idx_fixtures_league_season_date;
DROP INDEX IF EXISTS idx_fixtures_date_state;
DROP INDEX IF EXISTS idx_fixtures_teams;
DROP INDEX IF EXISTS idx_fixtures_match_result;
DROP INDEX IF EXISTS idx_fixtures_total_goals;
DROP INDEX IF EXISTS idx_fixtures_data_flags;

-- Remover colunas (CUIDADO: PERDA DE DADOS!)
ALTER TABLE fixtures 
DROP COLUMN IF EXISTS name,
DROP COLUMN IF EXISTS result_info,
DROP COLUMN IF EXISTS leg,
DROP COLUMN IF EXISTS details,
DROP COLUMN IF EXISTS last_processed_at,
DROP COLUMN IF EXISTS home_score,
DROP COLUMN IF EXISTS away_score,
DROP COLUMN IF EXISTS total_goals,
DROP COLUMN IF EXISTS goal_difference,
DROP COLUMN IF EXISTS match_result,
DROP COLUMN IF EXISTS etl_processed_at,
DROP COLUMN IF EXISTS etl_version,
DROP COLUMN IF EXISTS data_quality_score;

COMMIT;
*/
