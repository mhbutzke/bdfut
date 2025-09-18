-- Criar tabela match_participants para dados dos participantes (times)
CREATE TABLE IF NOT EXISTS match_participants (
    id BIGINT PRIMARY KEY,
    sport_id INTEGER NOT NULL,
    country_id INTEGER,
    venue_id INTEGER,
    gender VARCHAR(10),
    name VARCHAR(255) NOT NULL,
    short_code VARCHAR(10),
    image_path TEXT,
    founded INTEGER,
    type VARCHAR(50),
    placeholder BOOLEAN DEFAULT FALSE,
    last_played_at TIMESTAMP WITH TIME ZONE,
    meta JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_match_participants_sport_id ON match_participants(sport_id);
CREATE INDEX IF NOT EXISTS idx_match_participants_country_id ON match_participants(country_id);
CREATE INDEX IF NOT EXISTS idx_match_participants_name ON match_participants(name);
CREATE INDEX IF NOT EXISTS idx_match_participants_type ON match_participants(type);

-- Comentários
COMMENT ON TABLE match_participants IS 'Tabela para armazenar dados dos participantes (times) de cada partida';
COMMENT ON COLUMN match_participants.id IS 'ID único do participante (ID da Sportmonks)';
COMMENT ON COLUMN match_participants.sport_id IS 'ID do esporte';
COMMENT ON COLUMN match_participants.country_id IS 'ID do país';
COMMENT ON COLUMN match_participants.venue_id IS 'ID do estádio';
COMMENT ON COLUMN match_participants.name IS 'Nome do time';
COMMENT ON COLUMN match_participants.short_code IS 'Código abreviado do time';
COMMENT ON COLUMN match_participants.founded IS 'Ano de fundação';
COMMENT ON COLUMN match_participants.type IS 'Tipo do participante (team, etc.)';
