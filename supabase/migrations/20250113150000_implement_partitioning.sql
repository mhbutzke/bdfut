-- Migração: Implementar Partitioning por Data
-- TASK-DB-005: Implementar Partitioning por Data
-- Data: 2025-01-13
-- Agente: Database Specialist 🗄️

-- Implementando partitioning na tabela fixtures para otimizar performance com grandes volumes

-- 1. CRIAR NOVA TABELA FIXTURES PARTICIONADA
-- Primeiro, criamos a estrutura particionada

-- Renomear tabela atual para backup
ALTER TABLE fixtures RENAME TO fixtures_backup;

-- Criar nova tabela particionada
CREATE TABLE fixtures (
    id integer NOT NULL DEFAULT nextval('fixtures_id_seq'::regclass),
    sportmonks_id integer NOT NULL,
    league_id integer,
    season_id integer,
    home_team_id integer,
    away_team_id integer,
    match_date timestamp without time zone,
    status character varying,
    home_score integer,
    away_score integer,
    venue character varying,
    referee character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (match_date);

-- 2. CRIAR PARTIÇÕES POR ANO
-- Partições para anos históricos e futuros

-- 2024
CREATE TABLE fixtures_2024 PARTITION OF fixtures
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- 2025
CREATE TABLE fixtures_2025 PARTITION OF fixtures
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- 2026
CREATE TABLE fixtures_2026 PARTITION OF fixtures
FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- 2027 (futuro)
CREATE TABLE fixtures_2027 PARTITION OF fixtures
FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');

-- Partição default para datas fora do range
CREATE TABLE fixtures_default PARTITION OF fixtures DEFAULT;

-- 3. RECRIAR CONSTRAINTS NA TABELA PARTICIONADA
-- Constraints de validação (replicadas da migração anterior)
ALTER TABLE fixtures 
ADD CONSTRAINT chk_fixtures_scores_positive 
CHECK (home_score IS NULL OR home_score >= 0),
ADD CONSTRAINT chk_fixtures_away_score_positive 
CHECK (away_score IS NULL OR away_score >= 0),
ADD CONSTRAINT chk_fixtures_match_date_not_future 
CHECK (match_date IS NULL OR match_date <= CURRENT_TIMESTAMP + INTERVAL '1 year'),
ADD CONSTRAINT chk_fixtures_teams_different 
CHECK (home_team_id IS NULL OR away_team_id IS NULL OR home_team_id != away_team_id);

-- Unique constraint no sportmonks_id (precisa incluir partition key)
ALTER TABLE fixtures 
ADD CONSTRAINT fixtures_sportmonks_id_match_date_key 
UNIQUE (sportmonks_id, match_date);

-- 4. RECRIAR ÍNDICES NAS PARTIÇÕES
-- Índices principais em cada partição

-- Índice na coluna de particionamento
CREATE INDEX idx_fixtures_2024_match_date ON fixtures_2024 (match_date);
CREATE INDEX idx_fixtures_2025_match_date ON fixtures_2025 (match_date);
CREATE INDEX idx_fixtures_2026_match_date ON fixtures_2026 (match_date);
CREATE INDEX idx_fixtures_2027_match_date ON fixtures_2027 (match_date);
CREATE INDEX idx_fixtures_default_match_date ON fixtures_default (match_date);

-- Índices para foreign keys
CREATE INDEX idx_fixtures_2024_season ON fixtures_2024 (season_id);
CREATE INDEX idx_fixtures_2024_league ON fixtures_2024 (league_id);
CREATE INDEX idx_fixtures_2024_teams ON fixtures_2024 (home_team_id, away_team_id);

CREATE INDEX idx_fixtures_2025_season ON fixtures_2025 (season_id);
CREATE INDEX idx_fixtures_2025_league ON fixtures_2025 (league_id);
CREATE INDEX idx_fixtures_2025_teams ON fixtures_2025 (home_team_id, away_team_id);

CREATE INDEX idx_fixtures_2026_season ON fixtures_2026 (season_id);
CREATE INDEX idx_fixtures_2026_league ON fixtures_2026 (league_id);
CREATE INDEX idx_fixtures_2026_teams ON fixtures_2026 (home_team_id, away_team_id);

CREATE INDEX idx_fixtures_2027_season ON fixtures_2027 (season_id);
CREATE INDEX idx_fixtures_2027_league ON fixtures_2027 (league_id);
CREATE INDEX idx_fixtures_2027_teams ON fixtures_2027 (home_team_id, away_team_id);

-- Índices compostos otimizados
CREATE INDEX idx_fixtures_2024_season_date ON fixtures_2024 (season_id, match_date DESC);
CREATE INDEX idx_fixtures_2025_season_date ON fixtures_2025 (season_id, match_date DESC);
CREATE INDEX idx_fixtures_2026_season_date ON fixtures_2026 (season_id, match_date DESC);
CREATE INDEX idx_fixtures_2027_season_date ON fixtures_2027 (season_id, match_date DESC);

-- 5. MIGRAR DADOS DA TABELA ORIGINAL
-- Inserir dados na nova tabela particionada
INSERT INTO fixtures (
    id, sportmonks_id, league_id, season_id, home_team_id, away_team_id,
    match_date, status, home_score, away_score, venue, referee,
    created_at, updated_at
)
SELECT 
    id, sportmonks_id, league_id, season_id, home_team_id, away_team_id,
    match_date, status, home_score, away_score, venue, referee,
    created_at, updated_at
FROM fixtures_backup;

-- 6. RECRIAR FOREIGN KEYS
-- Foreign keys precisam ser recriadas após o partitioning

-- Para teams (home_team_id)
ALTER TABLE fixtures_2024 
ADD CONSTRAINT fixtures_2024_home_team_id_fkey 
FOREIGN KEY (home_team_id) REFERENCES teams(sportmonks_id);

ALTER TABLE fixtures_2025 
ADD CONSTRAINT fixtures_2025_home_team_id_fkey 
FOREIGN KEY (home_team_id) REFERENCES teams(sportmonks_id);

ALTER TABLE fixtures_2026 
ADD CONSTRAINT fixtures_2026_home_team_id_fkey 
FOREIGN KEY (home_team_id) REFERENCES teams(sportmonks_id);

ALTER TABLE fixtures_2027 
ADD CONSTRAINT fixtures_2027_home_team_id_fkey 
FOREIGN KEY (home_team_id) REFERENCES teams(sportmonks_id);

-- Para teams (away_team_id)
ALTER TABLE fixtures_2024 
ADD CONSTRAINT fixtures_2024_away_team_id_fkey 
FOREIGN KEY (away_team_id) REFERENCES teams(sportmonks_id);

ALTER TABLE fixtures_2025 
ADD CONSTRAINT fixtures_2025_away_team_id_fkey 
FOREIGN KEY (away_team_id) REFERENCES teams(sportmonks_id);

ALTER TABLE fixtures_2026 
ADD CONSTRAINT fixtures_2026_away_team_id_fkey 
FOREIGN KEY (away_team_id) REFERENCES teams(sportmonks_id);

ALTER TABLE fixtures_2027 
ADD CONSTRAINT fixtures_2027_away_team_id_fkey 
FOREIGN KEY (away_team_id) REFERENCES teams(sportmonks_id);

-- Para leagues
ALTER TABLE fixtures_2024 
ADD CONSTRAINT fixtures_2024_league_id_fkey 
FOREIGN KEY (league_id) REFERENCES leagues(sportmonks_id);

ALTER TABLE fixtures_2025 
ADD CONSTRAINT fixtures_2025_league_id_fkey 
FOREIGN KEY (league_id) REFERENCES leagues(sportmonks_id);

ALTER TABLE fixtures_2026 
ADD CONSTRAINT fixtures_2026_league_id_fkey 
FOREIGN KEY (league_id) REFERENCES leagues(sportmonks_id);

ALTER TABLE fixtures_2027 
ADD CONSTRAINT fixtures_2027_league_id_fkey 
FOREIGN KEY (league_id) REFERENCES leagues(sportmonks_id);

-- Para seasons
ALTER TABLE fixtures_2024 
ADD CONSTRAINT fixtures_2024_season_id_fkey 
FOREIGN KEY (season_id) REFERENCES seasons(sportmonks_id);

ALTER TABLE fixtures_2025 
ADD CONSTRAINT fixtures_2025_season_id_fkey 
FOREIGN KEY (season_id) REFERENCES seasons(sportmonks_id);

ALTER TABLE fixtures_2026 
ADD CONSTRAINT fixtures_2026_season_id_fkey 
FOREIGN KEY (season_id) REFERENCES seasons(sportmonks_id);

ALTER TABLE fixtures_2027 
ADD CONSTRAINT fixtures_2027_season_id_fkey 
FOREIGN KEY (season_id) REFERENCES seasons(sportmonks_id);

-- 7. ATUALIZAR SEQUENCE
-- Ajustar sequence para próximo valor
SELECT setval('fixtures_id_seq', (SELECT MAX(id) FROM fixtures));

-- 8. FUNÇÃO PARA MANUTENÇÃO AUTOMÁTICA DE PARTIÇÕES
CREATE OR REPLACE FUNCTION create_monthly_partition(target_date date)
RETURNS void AS $$
DECLARE
    partition_name text;
    start_date date;
    end_date date;
BEGIN
    -- Calcular nome da partição e datas
    partition_name := 'fixtures_' || to_char(target_date, 'YYYY_MM');
    start_date := date_trunc('month', target_date)::date;
    end_date := (date_trunc('month', target_date) + interval '1 month')::date;
    
    -- Verificar se partição já existe
    IF NOT EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = partition_name
    ) THEN
        -- Criar nova partição mensal
        EXECUTE format('CREATE TABLE %I PARTITION OF fixtures FOR VALUES FROM (%L) TO (%L)',
                      partition_name, start_date, end_date);
        
        -- Criar índices na nova partição
        EXECUTE format('CREATE INDEX %I ON %I (match_date)', 
                      'idx_' || partition_name || '_match_date', partition_name);
        EXECUTE format('CREATE INDEX %I ON %I (season_id)', 
                      'idx_' || partition_name || '_season', partition_name);
        EXECUTE format('CREATE INDEX %I ON %I (league_id)', 
                      'idx_' || partition_name || '_league', partition_name);
        EXECUTE format('CREATE INDEX %I ON %I (home_team_id, away_team_id)', 
                      'idx_' || partition_name || '_teams', partition_name);
        
        -- Adicionar foreign keys
        EXECUTE format('ALTER TABLE %I ADD CONSTRAINT %I FOREIGN KEY (home_team_id) REFERENCES teams(sportmonks_id)',
                      partition_name, partition_name || '_home_team_id_fkey');
        EXECUTE format('ALTER TABLE %I ADD CONSTRAINT %I FOREIGN KEY (away_team_id) REFERENCES teams(sportmonks_id)',
                      partition_name, partition_name || '_away_team_id_fkey');
        EXECUTE format('ALTER TABLE %I ADD CONSTRAINT %I FOREIGN KEY (league_id) REFERENCES leagues(sportmonks_id)',
                      partition_name, partition_name || '_league_id_fkey');
        EXECUTE format('ALTER TABLE %I ADD CONSTRAINT %I FOREIGN KEY (season_id) REFERENCES seasons(sportmonks_id)',
                      partition_name, partition_name || '_season_id_fkey');
        
        -- Log da operação
        INSERT INTO api_cache (cache_key, data, expires_at) 
        VALUES (
            'partition_created_' || partition_name,
            jsonb_build_object(
                'partition_name', partition_name,
                'start_date', start_date,
                'end_date', end_date,
                'created_at', now()
            ),
            now() + INTERVAL '1 year'
        );
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 9. FUNÇÃO PARA LIMPEZA AUTOMÁTICA DE PARTIÇÕES ANTIGAS
CREATE OR REPLACE FUNCTION drop_old_partitions(retention_months integer DEFAULT 24)
RETURNS void AS $$
DECLARE
    partition_record record;
    cutoff_date date;
BEGIN
    cutoff_date := (current_date - (retention_months || ' months')::interval)::date;
    
    -- Buscar partições antigas
    FOR partition_record IN
        SELECT schemaname, tablename
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename LIKE 'fixtures_20%'
        AND tablename != 'fixtures_default'
        AND substring(tablename from 10 for 4)::integer < extract(year from cutoff_date)
    LOOP
        -- Log antes de remover
        INSERT INTO api_cache (cache_key, data, expires_at) 
        VALUES (
            'partition_dropped_' || partition_record.tablename,
            jsonb_build_object(
                'partition_name', partition_record.tablename,
                'dropped_at', now(),
                'cutoff_date', cutoff_date
            ),
            now() + INTERVAL '1 year'
        );
        
        -- Remover partição
        EXECUTE format('DROP TABLE IF EXISTS %I', partition_record.tablename);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 10. ATUALIZAR TABELAS RELACIONADAS PARA USAR A NOVA ESTRUTURA
-- As tabelas relacionadas (match_events, match_lineups, match_statistics) 
-- continuam funcionando normalmente pois referenciam fixtures.sportmonks_id

-- Comentários para documentação
COMMENT ON TABLE fixtures IS 'Tabela principal de fixtures particionada por data para otimização de performance';
COMMENT ON TABLE fixtures_2024 IS 'Partição de fixtures para o ano 2024';
COMMENT ON TABLE fixtures_2025 IS 'Partição de fixtures para o ano 2025';
COMMENT ON TABLE fixtures_2026 IS 'Partição de fixtures para o ano 2026';
COMMENT ON TABLE fixtures_2027 IS 'Partição de fixtures para o ano 2027';
COMMENT ON TABLE fixtures_default IS 'Partição default para fixtures fora do range definido';
COMMENT ON FUNCTION create_monthly_partition(date) IS 'Função para criar partições mensais automaticamente';
COMMENT ON FUNCTION drop_old_partitions(integer) IS 'Função para remover partições antigas automaticamente';
