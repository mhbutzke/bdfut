-- Migration: Adicionar colunas faltantes para ETL
-- Data: 17 de Janeiro de 2025
-- Agente: ETL Engineer
-- Task: 1.2 - Criar Migration para Fixtures
-- Objetivo: Adicionar colunas essenciais da API Sportmonks para otimizar operações ETL

-- =====================================================
-- COLUNAS ESSENCIAIS PARA ETL (ALTA PRIORIDADE)
-- =====================================================

-- Nome da partida (ex: "West Ham United vs Tottenham Hotspur")
ALTER TABLE fixtures ADD COLUMN name VARCHAR(255);

-- Informação do resultado da partida
ALTER TABLE fixtures ADD COLUMN result_info TEXT;

-- Placar do time da casa
ALTER TABLE fixtures ADD COLUMN home_score INTEGER;

-- Placar do time visitante  
ALTER TABLE fixtures ADD COLUMN away_score INTEGER;

-- Perna da partida (ex: "1/1", "2/2")
ALTER TABLE fixtures ADD COLUMN leg VARCHAR(50);

-- =====================================================
-- COLUNAS DE CONTROLE ETL (MÉDIA PRIORIDADE)
-- =====================================================

-- Timestamp do último processamento ETL
ALTER TABLE fixtures ADD COLUMN last_processed_at TIMESTAMP;

-- Versão do ETL que processou este registro
ALTER TABLE fixtures ADD COLUMN etl_version VARCHAR(20) DEFAULT 'v1.0';

-- ID do esporte (1 = futebol)
ALTER TABLE fixtures ADD COLUMN sport_id INTEGER DEFAULT 1;

-- Dados adicionais da API Sportmonks
ALTER TABLE fixtures ADD COLUMN details JSONB;

-- =====================================================
-- COLUNAS CALCULADAS PARA PERFORMANCE
-- =====================================================

-- Total de gols da partida (home_score + away_score)
ALTER TABLE fixtures ADD COLUMN total_goals INTEGER GENERATED ALWAYS AS (COALESCE(home_score, 0) + COALESCE(away_score, 0)) STORED;

-- Resultado da partida (H=Home, A=Away, D=Draw)
ALTER TABLE fixtures ADD COLUMN match_result VARCHAR(1) GENERATED ALWAYS AS (
    CASE 
        WHEN home_score IS NULL OR away_score IS NULL THEN NULL
        WHEN home_score > away_score THEN 'H'
        WHEN away_score > home_score THEN 'A'
        ELSE 'D'
    END
) STORED;

-- =====================================================
-- COLUNAS DE METADADOS ETL
-- =====================================================

-- Timestamp de quando foi processado pelo ETL
ALTER TABLE fixtures ADD COLUMN etl_processed_at TIMESTAMP;

-- Score de qualidade dos dados (0-100)
ALTER TABLE fixtures ADD COLUMN data_quality_score INTEGER DEFAULT 100 CHECK (data_quality_score >= 0 AND data_quality_score <= 100);

-- =====================================================
-- COMENTÁRIOS PARA DOCUMENTAÇÃO
-- =====================================================

COMMENT ON COLUMN fixtures.name IS 'Nome da partida (ex: "Team A vs Team B")';
COMMENT ON COLUMN fixtures.result_info IS 'Informação do resultado da partida';
COMMENT ON COLUMN fixtures.home_score IS 'Placar do time da casa';
COMMENT ON COLUMN fixtures.away_score IS 'Placar do time visitante';
COMMENT ON COLUMN fixtures.leg IS 'Perna da partida (ex: "1/1", "2/2")';
COMMENT ON COLUMN fixtures.last_processed_at IS 'Timestamp do último processamento ETL';
COMMENT ON COLUMN fixtures.etl_version IS 'Versão do ETL que processou este registro';
COMMENT ON COLUMN fixtures.sport_id IS 'ID do esporte (1 = futebol)';
COMMENT ON COLUMN fixtures.details IS 'Dados adicionais da API Sportmonks';
COMMENT ON COLUMN fixtures.total_goals IS 'Total de gols da partida (calculado automaticamente)';
COMMENT ON COLUMN fixtures.match_result IS 'Resultado da partida: H=Home, A=Away, D=Draw';
COMMENT ON COLUMN fixtures.etl_processed_at IS 'Timestamp de quando foi processado pelo ETL';
COMMENT ON COLUMN fixtures.data_quality_score IS 'Score de qualidade dos dados (0-100)';

-- =====================================================
-- ÍNDICES PARA PERFORMANCE ETL
-- =====================================================

-- Índice para consultas por data de processamento
CREATE INDEX idx_fixtures_last_processed_at ON fixtures(last_processed_at);

-- Índice para consultas por versão ETL
CREATE INDEX idx_fixtures_etl_version ON fixtures(etl_version);

-- Índice para consultas por qualidade de dados
CREATE INDEX idx_fixtures_data_quality ON fixtures(data_quality_score);

-- Índice composto para consultas ETL frequentes
CREATE INDEX idx_fixtures_etl_composite ON fixtures(etl_version, last_processed_at, data_quality_score);

-- =====================================================
-- TRIGGER PARA ATUALIZAÇÃO AUTOMÁTICA
-- =====================================================

-- Função para atualizar timestamp de processamento
CREATE OR REPLACE FUNCTION update_fixture_etl_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_processed_at = CURRENT_TIMESTAMP;
    NEW.etl_processed_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar automaticamente os timestamps
CREATE TRIGGER trigger_update_fixture_etl_timestamp
    BEFORE UPDATE ON fixtures
    FOR EACH ROW
    EXECUTE FUNCTION update_fixture_etl_timestamp();

-- =====================================================
-- VALIDAÇÕES E CONSTRAINTS
-- =====================================================

-- Constraint para placares válidos
ALTER TABLE fixtures ADD CONSTRAINT check_valid_scores 
    CHECK (
        (home_score IS NULL OR home_score >= 0) AND 
        (away_score IS NULL OR away_score >= 0)
    );

-- Constraint para leg válido
ALTER TABLE fixtures ADD CONSTRAINT check_valid_leg 
    CHECK (leg IS NULL OR leg ~ '^[0-9]+/[0-9]+$');

-- =====================================================
-- LOG DE MIGRATION
-- =====================================================

-- Inserir log da migration
INSERT INTO api_cache (cache_key, data, expires_at) 
VALUES (
    'migration_003_fixtures_etl_columns',
    jsonb_build_object(
        'migration_id', '003',
        'description', 'Add ETL columns to fixtures table',
        'executed_at', CURRENT_TIMESTAMP,
        'columns_added', jsonb_build_array(
            'name', 'result_info', 'home_score', 'away_score', 'leg',
            'last_processed_at', 'etl_version', 'sport_id', 'details',
            'total_goals', 'match_result', 'etl_processed_at', 'data_quality_score'
        ),
        'indexes_created', jsonb_build_array(
            'idx_fixtures_last_processed_at', 'idx_fixtures_etl_version',
            'idx_fixtures_data_quality', 'idx_fixtures_etl_composite'
        ),
        'triggers_created', jsonb_build_array(
            'trigger_update_fixture_etl_timestamp'
        )
    ),
    CURRENT_TIMESTAMP + INTERVAL '1 year'
);

-- =====================================================
-- VERIFICAÇÃO FINAL
-- =====================================================

-- Verificar se todas as colunas foram adicionadas
DO $$
DECLARE
    missing_columns TEXT[] := ARRAY[]::TEXT[];
    col_name TEXT;
    required_columns TEXT[] := ARRAY[
        'name', 'result_info', 'home_score', 'away_score', 'leg',
        'last_processed_at', 'etl_version', 'sport_id', 'details',
        'total_goals', 'match_result', 'etl_processed_at', 'data_quality_score'
    ];
BEGIN
    FOREACH col_name IN ARRAY required_columns
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'fixtures' 
            AND column_name = col_name
            AND table_schema = 'public'
        ) THEN
            missing_columns := array_append(missing_columns, col_name);
        END IF;
    END LOOP;
    
    IF array_length(missing_columns, 1) > 0 THEN
        RAISE EXCEPTION 'Migration failed: Missing columns: %', array_to_string(missing_columns, ', ');
    ELSE
        RAISE NOTICE 'Migration 003 completed successfully: All columns added to fixtures table';
    END IF;
END $$;
