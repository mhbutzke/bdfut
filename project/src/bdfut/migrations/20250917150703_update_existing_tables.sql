-- Atualizar tabela match_events com novos campos importantes
ALTER TABLE match_events 
ADD COLUMN IF NOT EXISTS period_id INTEGER,
ADD COLUMN IF NOT EXISTS participant_id INTEGER,
ADD COLUMN IF NOT EXISTS section VARCHAR(50),
ADD COLUMN IF NOT EXISTS result VARCHAR(100),
ADD COLUMN IF NOT EXISTS info TEXT,
ADD COLUMN IF NOT EXISTS addition TEXT,
ADD COLUMN IF NOT EXISTS injured BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS on_bench BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS coach_id INTEGER,
ADD COLUMN IF NOT EXISTS sub_type_id INTEGER,
ADD COLUMN IF NOT EXISTS detailed_period_id INTEGER,
ADD COLUMN IF NOT EXISTS rescinded BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS sort_order INTEGER;

-- Criar índices para novos campos
CREATE INDEX IF NOT EXISTS idx_match_events_period_id ON match_events(period_id);
CREATE INDEX IF NOT EXISTS idx_match_events_participant_id ON match_events(participant_id);
CREATE INDEX IF NOT EXISTS idx_match_events_section ON match_events(section);
CREATE INDEX IF NOT EXISTS idx_match_events_result ON match_events(result);

-- Atualizar tabela match_lineups com novos campos importantes
ALTER TABLE match_lineups 
ADD COLUMN IF NOT EXISTS sport_id INTEGER,
ADD COLUMN IF NOT EXISTS position_id INTEGER,
ADD COLUMN IF NOT EXISTS formation_field VARCHAR(50),
ADD COLUMN IF NOT EXISTS formation_position VARCHAR(50);

-- Criar índices para novos campos
CREATE INDEX IF NOT EXISTS idx_match_lineups_sport_id ON match_lineups(sport_id);
CREATE INDEX IF NOT EXISTS idx_match_lineups_position_id ON match_lineups(position_id);
CREATE INDEX IF NOT EXISTS idx_match_lineups_formation_field ON match_lineups(formation_field);

-- Atualizar tabela match_statistics com novos campos importantes
ALTER TABLE match_statistics 
ADD COLUMN IF NOT EXISTS location VARCHAR(100);

-- Criar índice para novo campo
CREATE INDEX IF NOT EXISTS idx_match_statistics_location ON match_statistics(location);

-- Comentários para novos campos
COMMENT ON COLUMN match_events.period_id IS 'ID do período da partida';
COMMENT ON COLUMN match_events.participant_id IS 'ID do participante (time)';
COMMENT ON COLUMN match_events.section IS 'Seção do evento (home/away)';
COMMENT ON COLUMN match_events.result IS 'Resultado do evento';
COMMENT ON COLUMN match_events.info IS 'Informações adicionais do evento';
COMMENT ON COLUMN match_events.addition IS 'Informações de adição';
COMMENT ON COLUMN match_events.injured IS 'Se o jogador estava lesionado';
COMMENT ON COLUMN match_events.on_bench IS 'Se o jogador estava no banco';
COMMENT ON COLUMN match_events.coach_id IS 'ID do técnico';
COMMENT ON COLUMN match_events.sub_type_id IS 'ID do subtipo do evento';
COMMENT ON COLUMN match_events.detailed_period_id IS 'ID detalhado do período';
COMMENT ON COLUMN match_events.rescinded IS 'Se o evento foi revogado';
COMMENT ON COLUMN match_events.sort_order IS 'Ordem de classificação';

COMMENT ON COLUMN match_lineups.sport_id IS 'ID do esporte';
COMMENT ON COLUMN match_lineups.position_id IS 'ID da posição do jogador';
COMMENT ON COLUMN match_lineups.formation_field IS 'Campo da formação';
COMMENT ON COLUMN match_lineups.formation_position IS 'Posição na formação';

COMMENT ON COLUMN match_statistics.location IS 'Localização da estatística';
