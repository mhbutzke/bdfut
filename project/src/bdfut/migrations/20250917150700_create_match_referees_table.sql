-- Criar tabela match_referees para dados dos árbitros
CREATE TABLE IF NOT EXISTS match_referees (
    id BIGINT PRIMARY KEY,
    fixture_id INTEGER NOT NULL,
    referee_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_match_referees_fixture_id ON match_referees(fixture_id);
CREATE INDEX IF NOT EXISTS idx_match_referees_referee_id ON match_referees(referee_id);
CREATE INDEX IF NOT EXISTS idx_match_referees_type_id ON match_referees(type_id);

-- Comentários
COMMENT ON TABLE match_referees IS 'Tabela para armazenar dados dos árbitros de cada partida';
COMMENT ON COLUMN match_referees.id IS 'ID único do registro (ID da Sportmonks)';
COMMENT ON COLUMN match_referees.fixture_id IS 'ID da partida';
COMMENT ON COLUMN match_referees.referee_id IS 'ID do árbitro';
COMMENT ON COLUMN match_referees.type_id IS 'Tipo do árbitro (6=Principal, 7=Assistente, etc.)';
