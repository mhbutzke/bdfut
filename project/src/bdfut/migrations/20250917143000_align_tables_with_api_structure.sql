-- Migration para alinhar tabelas com estrutura da API Sportmonks
-- Data: 2025-09-17 14:30:00

-- =====================================================
-- TABELA MATCH_EVENTS - Alinhar com API
-- =====================================================

-- Adicionar colunas que faltam da API
ALTER TABLE match_events 
ADD COLUMN IF NOT EXISTS section VARCHAR(50),
ADD COLUMN IF NOT EXISTS sub_type_id INTEGER,
ADD COLUMN IF NOT EXISTS info TEXT,
ADD COLUMN IF NOT EXISTS rescinded BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS coach_id INTEGER,
ADD COLUMN IF NOT EXISTS participant_id INTEGER,
ADD COLUMN IF NOT EXISTS related_player_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS sort_order INTEGER,
ADD COLUMN IF NOT EXISTS addition TEXT,
ADD COLUMN IF NOT EXISTS detailed_period_id INTEGER;

-- Renomear colunas para alinhar com API
-- team_id -> participant_id (manter ambos por compatibilidade)
-- Adicionar índices para performance
CREATE INDEX IF NOT EXISTS idx_match_events_section ON match_events(section);
CREATE INDEX IF NOT EXISTS idx_match_events_type_id ON match_events(type_id);
CREATE INDEX IF NOT EXISTS idx_match_events_participant_id ON match_events(participant_id);
CREATE INDEX IF NOT EXISTS idx_match_events_player_id ON match_events(player_id);

-- =====================================================
-- TABELA MATCH_LINEUPS - Alinhar com API
-- =====================================================

-- Adicionar colunas que faltam da API
ALTER TABLE match_lineups 
ADD COLUMN IF NOT EXISTS formation_field VARCHAR(50),
ADD COLUMN IF NOT EXISTS sport_id INTEGER,
ADD COLUMN IF NOT EXISTS type_id INTEGER;

-- Adicionar índices para performance
CREATE INDEX IF NOT EXISTS idx_match_lineups_type_id ON match_lineups(type_id);
CREATE INDEX IF NOT EXISTS idx_match_lineups_sport_id ON match_lineups(sport_id);
CREATE INDEX IF NOT EXISTS idx_match_lineups_formation_field ON match_lineups(formation_field);

-- =====================================================
-- TABELA MATCH_STATISTICS - Reorganizar completamente
-- =====================================================

-- A API retorna statistics em formato diferente
-- Cada estatística é um registro separado com type_id e data
-- Vamos manter a estrutura atual mas adicionar campos da API

ALTER TABLE match_statistics 
ADD COLUMN IF NOT EXISTS data JSONB,
ADD COLUMN IF NOT EXISTS participant_id INTEGER,
ADD COLUMN IF NOT EXISTS type_id INTEGER,
ADD COLUMN IF NOT EXISTS location VARCHAR(50);

-- Adicionar índices para performance
CREATE INDEX IF NOT EXISTS idx_match_statistics_type_id ON match_statistics(type_id);
CREATE INDEX IF NOT EXISTS idx_match_statistics_participant_id ON match_statistics(participant_id);
CREATE INDEX IF NOT EXISTS idx_match_statistics_location ON match_statistics(location);
CREATE INDEX IF NOT EXISTS idx_match_statistics_data ON match_statistics USING GIN(data);

-- =====================================================
-- COMENTÁRIOS E DOCUMENTAÇÃO
-- =====================================================

COMMENT ON TABLE match_events IS 'Eventos detalhados das partidas - alinhado com API Sportmonks';
COMMENT ON TABLE match_lineups IS 'Escalações das partidas - alinhado com API Sportmonks';
COMMENT ON TABLE match_statistics IS 'Estatísticas das partidas - alinhado com API Sportmonks';

COMMENT ON COLUMN match_events.section IS 'Seção do evento (event, substitution, etc.)';
COMMENT ON COLUMN match_events.info IS 'Informação adicional do evento';
COMMENT ON COLUMN match_events.addition IS 'Detalhes adicionais (ex: 1st Yellowcard)';
COMMENT ON COLUMN match_events.participant_id IS 'ID do participante (time) - campo da API';
COMMENT ON COLUMN match_events.detailed_period_id IS 'ID detalhado do período';

COMMENT ON COLUMN match_lineups.formation_field IS 'Campo de formação da API';
COMMENT ON COLUMN match_lineups.type_id IS 'Tipo do lineup (11=starting, 12=substitute)';
COMMENT ON COLUMN match_lineups.sport_id IS 'ID do esporte';

COMMENT ON COLUMN match_statistics.data IS 'Dados da estatística em formato JSON';
COMMENT ON COLUMN match_statistics.type_id IS 'Tipo da estatística (41=shots_total, 42=shots_on_target, etc.)';
COMMENT ON COLUMN match_statistics.participant_id IS 'ID do participante (time)';
COMMENT ON COLUMN match_statistics.location IS 'Localização (home/away)';
