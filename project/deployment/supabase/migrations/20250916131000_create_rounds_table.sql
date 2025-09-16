-- Migração: Criar tabela rounds
-- Data: 2025-09-16
-- Objetivo: Implementar sistema de rounds (TASK-ETL-024)

-- Criar tabela rounds (verificar se já existe)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'rounds') THEN
        CREATE TABLE rounds (
            id BIGSERIAL PRIMARY KEY,
            sportmonks_id INTEGER UNIQUE NOT NULL,
            sport_id INTEGER,
            league_id BIGINT,
            season_id BIGINT,
            stage_id BIGINT,
            name TEXT,
            finished BOOLEAN DEFAULT FALSE,
            is_current BOOLEAN DEFAULT FALSE,
            starting_at DATE,
            ending_at DATE,
            games_in_current_week BOOLEAN DEFAULT FALSE,
            details JSONB, -- dados adicionais da API
            
            -- Metadados
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Constraints
            CONSTRAINT chk_round_dates CHECK (starting_at IS NULL OR ending_at IS NULL OR starting_at <= ending_at),
            CONSTRAINT chk_sport_id CHECK (sport_id IS NULL OR sport_id > 0),
            CONSTRAINT chk_league_id CHECK (league_id IS NULL OR league_id > 0),
            CONSTRAINT chk_season_id CHECK (season_id IS NULL OR season_id > 0),
            CONSTRAINT chk_stage_id CHECK (stage_id IS NULL OR stage_id > 0)
        );
        
        -- Índices para performance
        CREATE INDEX idx_rounds_sportmonks_id ON rounds(sportmonks_id);
        CREATE INDEX idx_rounds_league_id ON rounds(league_id);
        CREATE INDEX idx_rounds_season_id ON rounds(season_id);
        CREATE INDEX idx_rounds_stage_id ON rounds(stage_id);
        CREATE INDEX idx_rounds_starting_at ON rounds(starting_at);
        CREATE INDEX idx_rounds_ending_at ON rounds(ending_at);
        CREATE INDEX idx_rounds_finished ON rounds(finished);
        CREATE INDEX idx_rounds_is_current ON rounds(is_current);
        CREATE INDEX idx_rounds_created_at ON rounds(created_at);
        
        -- Trigger para updated_at
        CREATE OR REPLACE FUNCTION update_rounds_updated_at()
        RETURNS TRIGGER AS $trigger$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $trigger$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_rounds_updated_at
            BEFORE UPDATE ON rounds
            FOR EACH ROW
            EXECUTE FUNCTION update_rounds_updated_at();
        
        -- Comentários para documentação
        COMMENT ON TABLE rounds IS 'Tabela de rodadas/rounds dos campeonatos';
        COMMENT ON COLUMN rounds.sportmonks_id IS 'ID único da rodada na API Sportmonks';
        COMMENT ON COLUMN rounds.sport_id IS 'ID do esporte (1=futebol)';
        COMMENT ON COLUMN rounds.league_id IS 'Referência à liga/campeonato';
        COMMENT ON COLUMN rounds.season_id IS 'Referência à temporada';
        COMMENT ON COLUMN rounds.stage_id IS 'Referência ao estágio/fase';
        COMMENT ON COLUMN rounds.name IS 'Nome/número da rodada';
        COMMENT ON COLUMN rounds.finished IS 'Se a rodada foi finalizada';
        COMMENT ON COLUMN rounds.is_current IS 'Se é a rodada atual';
        COMMENT ON COLUMN rounds.starting_at IS 'Data de início da rodada';
        COMMENT ON COLUMN rounds.ending_at IS 'Data de fim da rodada';
        COMMENT ON COLUMN rounds.games_in_current_week IS 'Se há jogos na semana atual';
        COMMENT ON COLUMN rounds.details IS 'Dados JSON adicionais da API Sportmonks';
        
        RAISE NOTICE 'Tabela rounds criada com sucesso';
    ELSE
        RAISE NOTICE 'Tabela rounds já existe, pulando criação';
    END IF;
END $$;
