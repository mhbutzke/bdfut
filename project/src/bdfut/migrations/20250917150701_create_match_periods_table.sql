-- Criar tabela match_periods para dados dos períodos da partida
CREATE TABLE IF NOT EXISTS match_periods (
    id BIGINT PRIMARY KEY,
    fixture_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    started INTEGER,
    ended INTEGER,
    counts_from INTEGER,
    ticking BOOLEAN,
    sort_order INTEGER,
    description TEXT,
    time_added INTEGER,
    period_length INTEGER,
    minutes INTEGER,
    seconds INTEGER,
    has_timer BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_match_periods_fixture_id ON match_periods(fixture_id);
CREATE INDEX IF NOT EXISTS idx_match_periods_type_id ON match_periods(type_id);

-- Comentários
COMMENT ON TABLE match_periods IS 'Tabela para armazenar dados dos períodos de cada partida';
COMMENT ON COLUMN match_periods.id IS 'ID único do registro (ID da Sportmonks)';
COMMENT ON COLUMN match_periods.fixture_id IS 'ID da partida';
COMMENT ON COLUMN match_periods.type_id IS 'Tipo do período (1=1º tempo, 2=2º tempo, etc.)';
COMMENT ON COLUMN match_periods.started IS 'Timestamp de início do período';
COMMENT ON COLUMN match_periods.ended IS 'Timestamp de fim do período';
COMMENT ON COLUMN match_periods.minutes IS 'Minutos do período';
COMMENT ON COLUMN match_periods.seconds IS 'Segundos do período';
