-- =====================================================
-- MIGRAÇÃO: Adicionar colunas faltantes para API Sportmonks
-- Data: 2025-01-13
-- Objetivo: Acomodar todos os dados da API Sportmonks
-- =====================================================

-- 1. FIXTURES - Adicionar colunas faltantes
ALTER TABLE public.fixtures 
ADD COLUMN IF NOT EXISTS name VARCHAR(255),
ADD COLUMN IF NOT EXISTS starting_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS result_info VARCHAR(100),
ADD COLUMN IF NOT EXISTS leg VARCHAR(50),
ADD COLUMN IF NOT EXISTS details TEXT,
ADD COLUMN IF NOT EXISTS length INTEGER,
ADD COLUMN IF NOT EXISTS placeholder BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_odds BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_players BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_lineups BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_statistics BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_events BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS tie_breaker_rule VARCHAR(255);

-- 2. MATCH_EVENTS - Adicionar colunas faltantes
ALTER TABLE public.match_events 
ADD COLUMN IF NOT EXISTS var BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS var_reason VARCHAR(255),
ADD COLUMN IF NOT EXISTS coordinates JSONB,
ADD COLUMN IF NOT EXISTS assist_id BIGINT,
ADD COLUMN IF NOT EXISTS assist_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS injured BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS on_bench BOOLEAN DEFAULT FALSE;

-- 3. MATCH_STATISTICS - Adicionar colunas faltantes
ALTER TABLE public.match_statistics 
ADD COLUMN IF NOT EXISTS goals INTEGER,
ADD COLUMN IF NOT EXISTS goals_conceded INTEGER,
ADD COLUMN IF NOT EXISTS shots_off_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_saved INTEGER,
ADD COLUMN IF NOT EXISTS shots_woodwork INTEGER,
ADD COLUMN IF NOT EXISTS shots_blocked INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_total INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_total INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_on_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_on_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_off_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_off_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_saved INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_saved INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_woodwork INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_woodwork INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_blocked INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_blocked INTEGER;

-- 4. MATCH_LINEUPS - Adicionar colunas faltantes
ALTER TABLE public.match_lineups 
ADD COLUMN IF NOT EXISTS formation VARCHAR(50),
ADD COLUMN IF NOT EXISTS formation_position VARCHAR(50),
ADD COLUMN IF NOT EXISTS formation_number INTEGER,
ADD COLUMN IF NOT EXISTS formation_row INTEGER,
ADD COLUMN IF NOT EXISTS formation_position_x NUMERIC,
ADD COLUMN IF NOT EXISTS formation_position_y NUMERIC,
ADD COLUMN IF NOT EXISTS substitute BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS substitute_in INTEGER,
ADD COLUMN IF NOT EXISTS substitute_out INTEGER,
ADD COLUMN IF NOT EXISTS substitute_minute INTEGER,
ADD COLUMN IF NOT EXISTS substitute_extra_minute INTEGER,
ADD COLUMN IF NOT EXISTS substitute_reason VARCHAR(100),
ADD COLUMN IF NOT EXISTS substitute_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS substitute_player_id BIGINT,
ADD COLUMN IF NOT EXISTS substitute_player_name VARCHAR(255);

-- 5. PLAYERS - Adicionar colunas faltantes
ALTER TABLE public.players 
ADD COLUMN IF NOT EXISTS common_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS firstname VARCHAR(255),
ADD COLUMN IF NOT EXISTS lastname VARCHAR(255),
ADD COLUMN IF NOT EXISTS nationality VARCHAR(100),
ADD COLUMN IF NOT EXISTS position_id INTEGER,
ADD COLUMN IF NOT EXISTS position_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS date_of_birth DATE,
ADD COLUMN IF NOT EXISTS height INTEGER,
ADD COLUMN IF NOT EXISTS weight INTEGER,
ADD COLUMN IF NOT EXISTS image_path TEXT;

-- 6. TEAMS - Adicionar colunas faltantes
ALTER TABLE public.teams 
ADD COLUMN IF NOT EXISTS short_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS logo_url TEXT,
ADD COLUMN IF NOT EXISTS founded INTEGER,
ADD COLUMN IF NOT EXISTS venue_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS venue_id INTEGER,
ADD COLUMN IF NOT EXISTS country_id INTEGER,
ADD COLUMN IF NOT EXISTS national_team BOOLEAN DEFAULT FALSE;

-- 7. LEAGUES - Adicionar colunas faltantes
ALTER TABLE public.leagues 
ADD COLUMN IF NOT EXISTS country VARCHAR(100),
ADD COLUMN IF NOT EXISTS logo_url TEXT,
ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS type VARCHAR(50),
ADD COLUMN IF NOT EXISTS sub_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS is_cup BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_friendly BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_international BOOLEAN DEFAULT FALSE;

-- =====================================================
-- ÍNDICES PARA NOVAS COLUNAS
-- =====================================================

-- Índices para fixtures
CREATE INDEX IF NOT EXISTS idx_fixtures_starting_at ON public.fixtures (starting_at);
CREATE INDEX IF NOT EXISTS idx_fixtures_result_info ON public.fixtures (result_info);
CREATE INDEX IF NOT EXISTS idx_fixtures_leg ON public.fixtures (leg);

-- Índices para match_events
CREATE INDEX IF NOT EXISTS idx_match_events_var ON public.match_events (var);
CREATE INDEX IF NOT EXISTS idx_match_events_assist_id ON public.match_events (assist_id);
CREATE INDEX IF NOT EXISTS idx_match_events_coordinates ON public.match_events USING GIN (coordinates);

-- Índices para match_statistics
CREATE INDEX IF NOT EXISTS idx_match_statistics_goals ON public.match_statistics (goals);
CREATE INDEX IF NOT EXISTS idx_match_statistics_goals_conceded ON public.match_statistics (goals_conceded);

-- Índices para match_lineups
CREATE INDEX IF NOT EXISTS idx_match_lineups_formation ON public.match_lineups (formation);
CREATE INDEX IF NOT EXISTS idx_match_lineups_substitute ON public.match_lineups (substitute);
CREATE INDEX IF NOT EXISTS idx_match_lineups_substitute_minute ON public.match_lineups (substitute_minute);

-- Índices para players
CREATE INDEX IF NOT EXISTS idx_players_nationality ON public.players (nationality);
CREATE INDEX IF NOT EXISTS idx_players_position_id ON public.players (position_id);

-- Índices para teams
CREATE INDEX IF NOT EXISTS idx_teams_country_id ON public.teams (country_id);
CREATE INDEX IF NOT EXISTS idx_teams_venue_id ON public.teams (venue_id);

-- Índices para leagues
CREATE INDEX IF NOT EXISTS idx_leagues_type ON public.leagues (type);
CREATE INDEX IF NOT EXISTS idx_leagues_is_cup ON public.leagues (is_cup);

-- =====================================================
-- COMENTÁRIOS PARA DOCUMENTAÇÃO
-- =====================================================

COMMENT ON COLUMN public.fixtures.name IS 'Nome da partida';
COMMENT ON COLUMN public.fixtures.starting_at IS 'Data e hora de início da partida';
COMMENT ON COLUMN public.fixtures.result_info IS 'Informações sobre o resultado';
COMMENT ON COLUMN public.fixtures.leg IS 'Perna da partida (ida/volta)';
COMMENT ON COLUMN public.fixtures.details IS 'Detalhes adicionais da partida';
COMMENT ON COLUMN public.fixtures.length IS 'Duração da partida em minutos';
COMMENT ON COLUMN public.fixtures.placeholder IS 'Indica se é uma partida placeholder';
COMMENT ON COLUMN public.fixtures.has_odds IS 'Indica se tem odds disponíveis';
COMMENT ON COLUMN public.fixtures.has_players IS 'Indica se tem dados de jogadores';
COMMENT ON COLUMN public.fixtures.has_lineups IS 'Indica se tem escalações';
COMMENT ON COLUMN public.fixtures.has_statistics IS 'Indica se tem estatísticas';
COMMENT ON COLUMN public.fixtures.has_events IS 'Indica se tem eventos';
COMMENT ON COLUMN public.fixtures.is_deleted IS 'Indica se a partida foi deletada';
COMMENT ON COLUMN public.fixtures.tie_breaker_rule IS 'Regra de desempate';

COMMENT ON COLUMN public.match_events.var IS 'Indica se foi revisado pelo VAR';
COMMENT ON COLUMN public.match_events.var_reason IS 'Motivo da revisão do VAR';
COMMENT ON COLUMN public.match_events.coordinates IS 'Coordenadas do evento no campo';
COMMENT ON COLUMN public.match_events.assist_id IS 'ID do jogador que deu assistência';
COMMENT ON COLUMN public.match_events.assist_name IS 'Nome do jogador que deu assistência';
COMMENT ON COLUMN public.match_events.injured IS 'Indica se o jogador estava lesionado';
COMMENT ON COLUMN public.match_events.on_bench IS 'Indica se o jogador estava no banco';

COMMENT ON COLUMN public.match_statistics.goals IS 'Número de gols marcados';
COMMENT ON COLUMN public.match_statistics.goals_conceded IS 'Número de gols sofridos';
COMMENT ON COLUMN public.match_statistics.shots_off_target IS 'Chutes para fora do gol';
COMMENT ON COLUMN public.match_statistics.shots_saved IS 'Chutes defendidos';
COMMENT ON COLUMN public.match_statistics.shots_woodwork IS 'Chutes na trave';
COMMENT ON COLUMN public.match_statistics.shots_blocked IS 'Chutes bloqueados';

COMMENT ON COLUMN public.match_lineups.formation IS 'Formação tática do time';
COMMENT ON COLUMN public.match_lineups.formation_position IS 'Posição na formação';
COMMENT ON COLUMN public.match_lineups.formation_number INTEGER;
COMMENT ON COLUMN public.match_lineups.formation_row INTEGER;
COMMENT ON COLUMN public.match_lineups.formation_position_x NUMERIC;
COMMENT ON COLUMN public.match_lineups.formation_position_y NUMERIC;
COMMENT ON COLUMN public.match_lineups.substitute BOOLEAN DEFAULT FALSE;
COMMENT ON COLUMN public.match_lineups.substitute_in INTEGER;
COMMENT ON COLUMN public.match_lineups.substitute_out INTEGER;
COMMENT ON COLUMN public.match_lineups.substitute_minute INTEGER;
COMMENT ON COLUMN public.match_lineups.substitute_extra_minute INTEGER;
COMMENT ON COLUMN public.match_lineups.substitute_reason VARCHAR(100);
COMMENT ON COLUMN public.match_lineups.substitute_type VARCHAR(50);
COMMENT ON COLUMN public.match_lineups.substitute_player_id BIGINT;
COMMENT ON COLUMN public.match_lineups.substitute_player_name VARCHAR(255);
