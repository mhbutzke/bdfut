-- Migração para criar schema completo do Sportmonks no Supabase
-- Execute este script no SQL Editor do Supabase

-- Criar schema se não existir
CREATE SCHEMA IF NOT EXISTS sportmonks;

-- Configurar search_path para incluir o schema sportmonks
ALTER DATABASE postgres SET search_path TO public, sportmonks;

-- ============================================
-- TABELAS DE REFERÊNCIA BASE
-- ============================================

-- Tabela de países
CREATE TABLE IF NOT EXISTS sportmonks.countries (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    official_name VARCHAR(255),
    fifa_name VARCHAR(255),
    iso2 VARCHAR(2),
    iso3 VARCHAR(3),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    borders TEXT,
    image_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de continentes
CREATE TABLE IF NOT EXISTS sportmonks.continents (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de estados (states)
CREATE TABLE IF NOT EXISTS sportmonks.states (
    id INTEGER PRIMARY KEY,
    state VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    short_name VARCHAR(10),
    developer_name VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de tipos (types)
CREATE TABLE IF NOT EXISTS sportmonks.types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50),
    developer_name VARCHAR(100),
    model_type VARCHAR(50),
    stat_group VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELAS DE COMPETIÇÕES
-- ============================================

-- Tabela de ligas
CREATE TABLE IF NOT EXISTS sportmonks.leagues (
    id BIGINT PRIMARY KEY,
    sport_id BIGINT,
    country_id BIGINT REFERENCES sportmonks.countries(id),
    name VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT true,
    short_code VARCHAR(10),
    image_path TEXT,
    type VARCHAR(50),
    sub_type VARCHAR(50),
    last_played_at TIMESTAMPTZ,
    category INTEGER,
    has_jerseys BOOLEAN DEFAULT false,
    has_standings BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de temporadas
CREATE TABLE IF NOT EXISTS sportmonks.seasons (
    id BIGINT PRIMARY KEY,
    sport_id BIGINT,
    league_id BIGINT REFERENCES sportmonks.leagues(id),
    name VARCHAR(255) NOT NULL,
    finished BOOLEAN DEFAULT false,
    pending BOOLEAN DEFAULT false,
    is_current BOOLEAN DEFAULT false,
    starting_at DATE,
    ending_at DATE,
    standings_recalculated_at TIMESTAMPTZ,
    games_in_current_week BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de stages
CREATE TABLE IF NOT EXISTS sportmonks.stages (
    id BIGINT PRIMARY KEY,
    sport_id BIGINT,
    league_id BIGINT REFERENCES sportmonks.leagues(id),
    season_id BIGINT REFERENCES sportmonks.seasons(id),
    type_id INTEGER REFERENCES sportmonks.types(id),
    name VARCHAR(255) NOT NULL,
    sort_order INTEGER,
    finished BOOLEAN DEFAULT false,
    is_current BOOLEAN DEFAULT false,
    starting_at DATE,
    ending_at DATE,
    games_in_current_week BOOLEAN DEFAULT false,
    tie_break_rule VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de rounds
CREATE TABLE IF NOT EXISTS sportmonks.rounds (
    id BIGINT PRIMARY KEY,
    sport_id BIGINT,
    league_id BIGINT REFERENCES sportmonks.leagues(id),
    season_id BIGINT REFERENCES sportmonks.seasons(id),
    stage_id BIGINT REFERENCES sportmonks.stages(id),
    name VARCHAR(255) NOT NULL,
    finished BOOLEAN DEFAULT false,
    is_current BOOLEAN DEFAULT false,
    starting_at DATE,
    ending_at DATE,
    games_in_current_week BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELAS DE LOCAIS E PESSOAS
-- ============================================

-- Tabela de estádios
CREATE TABLE IF NOT EXISTS sportmonks.venues (
    id BIGINT PRIMARY KEY,
    country_id BIGINT REFERENCES sportmonks.countries(id),
    city_id BIGINT,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(500),
    zipcode VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    capacity INTEGER,
    image_path TEXT,
    city_name VARCHAR(255),
    surface VARCHAR(50),
    national_team BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de times
CREATE TABLE IF NOT EXISTS sportmonks.teams (
    id BIGINT PRIMARY KEY,
    sport_id BIGINT,
    country_id BIGINT REFERENCES sportmonks.countries(id),
    venue_id BIGINT REFERENCES sportmonks.venues(id),
    name VARCHAR(255) NOT NULL,
    short_code VARCHAR(10),
    twitter VARCHAR(255),
    founded INTEGER,
    logo_path TEXT,
    is_national_team BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de técnicos
CREATE TABLE IF NOT EXISTS sportmonks.coaches (
    id BIGINT PRIMARY KEY,
    player_id BIGINT,
    sport_id BIGINT,
    country_id BIGINT REFERENCES sportmonks.countries(id),
    nationality_id BIGINT REFERENCES sportmonks.countries(id),
    city_id BIGINT,
    common_name VARCHAR(255),
    firstname VARCHAR(255),
    lastname VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    image_path TEXT,
    height INTEGER,
    weight INTEGER,
    date_of_birth DATE,
    gender VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de jogadores
CREATE TABLE IF NOT EXISTS sportmonks.players (
    id BIGINT PRIMARY KEY,
    sport_id BIGINT,
    country_id BIGINT REFERENCES sportmonks.countries(id),
    nationality_id BIGINT REFERENCES sportmonks.countries(id),
    city_id BIGINT,
    position_id INTEGER,
    common_name VARCHAR(255),
    firstname VARCHAR(255),
    lastname VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    image_path TEXT,
    height INTEGER,
    weight INTEGER,
    date_of_birth DATE,
    gender VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de árbitros
CREATE TABLE IF NOT EXISTS sportmonks.referees (
    id BIGINT PRIMARY KEY,
    sport_id BIGINT,
    country_id BIGINT REFERENCES sportmonks.countries(id),
    city_id BIGINT,
    common_name VARCHAR(255),
    firstname VARCHAR(255),
    lastname VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    image_path TEXT,
    height INTEGER,
    weight INTEGER,
    date_of_birth DATE,
    gender VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELAS DE PARTIDAS
-- ============================================

-- Tabela de partidas (fixtures)
CREATE TABLE IF NOT EXISTS sportmonks.fixtures (
    id BIGINT PRIMARY KEY,
    sport_id BIGINT,
    league_id BIGINT REFERENCES sportmonks.leagues(id),
    season_id BIGINT REFERENCES sportmonks.seasons(id),
    stage_id BIGINT,
    group_id BIGINT,
    aggregate_id BIGINT,
    round_id BIGINT,
    state_id INTEGER REFERENCES sportmonks.states(id),
    venue_id BIGINT REFERENCES sportmonks.venues(id),
    name VARCHAR(500),
    starting_at TIMESTAMPTZ,
    result_info VARCHAR(100),
    leg VARCHAR(20),
    details VARCHAR(500),
    length INTEGER,
    placeholder BOOLEAN DEFAULT false,
    has_odds BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de participantes das partidas
CREATE TABLE IF NOT EXISTS sportmonks.fixture_participants (
    id BIGSERIAL PRIMARY KEY,
    fixture_id BIGINT REFERENCES sportmonks.fixtures(id) ON DELETE CASCADE,
    team_id BIGINT REFERENCES sportmonks.teams(id),
    position VARCHAR(20), -- home ou away
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(fixture_id, team_id)
);

-- Tabela de scores das partidas
CREATE TABLE IF NOT EXISTS sportmonks.fixture_scores (
    id BIGSERIAL PRIMARY KEY,
    fixture_id BIGINT REFERENCES sportmonks.fixtures(id) ON DELETE CASCADE,
    team_id BIGINT REFERENCES sportmonks.teams(id),
    score_type VARCHAR(50), -- total, 1st_half, 2nd_half, extra_time, penalty
    score INTEGER,
    description VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de eventos das partidas
CREATE TABLE IF NOT EXISTS sportmonks.fixture_events (
    id BIGINT PRIMARY KEY,
    fixture_id BIGINT REFERENCES sportmonks.fixtures(id) ON DELETE CASCADE,
    period_id INTEGER,
    participant_id BIGINT REFERENCES sportmonks.teams(id),
    type_id INTEGER REFERENCES sportmonks.types(id),
    player_id BIGINT REFERENCES sportmonks.players(id),
    related_player_id BIGINT REFERENCES sportmonks.players(id),
    player_name VARCHAR(255),
    related_player_name VARCHAR(255),
    result VARCHAR(50),
    info VARCHAR(500),
    addition VARCHAR(500),
    minute INTEGER,
    extra_minute INTEGER,
    injured BOOLEAN DEFAULT false,
    on_bench BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de estatísticas das partidas
CREATE TABLE IF NOT EXISTS sportmonks.fixture_statistics (
    id BIGSERIAL PRIMARY KEY,
    fixture_id BIGINT REFERENCES sportmonks.fixtures(id) ON DELETE CASCADE,
    team_id BIGINT REFERENCES sportmonks.teams(id),
    type_id INTEGER REFERENCES sportmonks.types(id),
    player_id BIGINT REFERENCES sportmonks.players(id),
    position_id INTEGER,
    location VARCHAR(20), -- home ou away
    data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de escalações
CREATE TABLE IF NOT EXISTS sportmonks.fixture_lineups (
    id BIGSERIAL PRIMARY KEY,
    fixture_id BIGINT REFERENCES sportmonks.fixtures(id) ON DELETE CASCADE,
    team_id BIGINT REFERENCES sportmonks.teams(id),
    player_id BIGINT REFERENCES sportmonks.players(id),
    type VARCHAR(20), -- lineup ou bench
    position_id INTEGER,
    position_name VARCHAR(50),
    formation_position VARCHAR(10),
    player_name VARCHAR(255),
    jersey_number INTEGER,
    captain BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELAS DE CLASSIFICAÇÕES E TRANSFERÊNCIAS
-- ============================================

-- Tabela de classificações
CREATE TABLE IF NOT EXISTS sportmonks.standings (
    id BIGSERIAL PRIMARY KEY,
    participant_id BIGINT REFERENCES sportmonks.teams(id),
    sport_id BIGINT,
    league_id BIGINT REFERENCES sportmonks.leagues(id),
    season_id BIGINT REFERENCES sportmonks.seasons(id),
    stage_id BIGINT,
    group_id BIGINT,
    round_id BIGINT,
    standing_rule_id INTEGER,
    position INTEGER,
    result VARCHAR(100),
    points INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de detalhes das classificações
CREATE TABLE IF NOT EXISTS sportmonks.standing_details (
    id BIGSERIAL PRIMARY KEY,
    standing_id BIGINT REFERENCES sportmonks.standings(id) ON DELETE CASCADE,
    type_id INTEGER REFERENCES sportmonks.types(id),
    value INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de transferências
CREATE TABLE IF NOT EXISTS sportmonks.transfers (
    id BIGINT PRIMARY KEY,
    sport_id BIGINT,
    player_id BIGINT REFERENCES sportmonks.players(id),
    from_team_id BIGINT REFERENCES sportmonks.teams(id),
    to_team_id BIGINT REFERENCES sportmonks.teams(id),
    position_id INTEGER,
    transfer_date DATE,
    amount DECIMAL(15, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================

CREATE INDEX IF NOT EXISTS idx_leagues_country ON sportmonks.leagues(country_id);
CREATE INDEX IF NOT EXISTS idx_seasons_league ON sportmonks.seasons(league_id);
CREATE INDEX IF NOT EXISTS idx_seasons_current ON sportmonks.seasons(is_current) WHERE is_current = true;
CREATE INDEX IF NOT EXISTS idx_teams_country ON sportmonks.teams(country_id);
CREATE INDEX IF NOT EXISTS idx_teams_venue ON sportmonks.teams(venue_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_league ON sportmonks.fixtures(league_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_season ON sportmonks.fixtures(season_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_venue ON sportmonks.fixtures(venue_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_state ON sportmonks.fixtures(state_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_starting_at ON sportmonks.fixtures(starting_at);
CREATE INDEX IF NOT EXISTS idx_fixture_participants_fixture ON sportmonks.fixture_participants(fixture_id);
CREATE INDEX IF NOT EXISTS idx_fixture_participants_team ON sportmonks.fixture_participants(team_id);
CREATE INDEX IF NOT EXISTS idx_fixture_events_fixture ON sportmonks.fixture_events(fixture_id);
CREATE INDEX IF NOT EXISTS idx_fixture_events_player ON sportmonks.fixture_events(player_id);
CREATE INDEX IF NOT EXISTS idx_fixture_events_type ON sportmonks.fixture_events(type_id);
CREATE INDEX IF NOT EXISTS idx_fixture_statistics_fixture ON sportmonks.fixture_statistics(fixture_id);
CREATE INDEX IF NOT EXISTS idx_fixture_statistics_team ON sportmonks.fixture_statistics(team_id);
CREATE INDEX IF NOT EXISTS idx_fixture_lineups_fixture ON sportmonks.fixture_lineups(fixture_id);
CREATE INDEX IF NOT EXISTS idx_fixture_lineups_team ON sportmonks.fixture_lineups(team_id);
CREATE INDEX IF NOT EXISTS idx_fixture_lineups_player ON sportmonks.fixture_lineups(player_id);
CREATE INDEX IF NOT EXISTS idx_standings_season ON sportmonks.standings(season_id);
CREATE INDEX IF NOT EXISTS idx_standings_participant ON sportmonks.standings(participant_id);
CREATE INDEX IF NOT EXISTS idx_transfers_player ON sportmonks.transfers(player_id);
CREATE INDEX IF NOT EXISTS idx_transfers_date ON sportmonks.transfers(transfer_date);

-- ============================================
-- FUNÇÕES E TRIGGERS
-- ============================================

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION sportmonks.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Criar triggers para todas as tabelas
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN 
        SELECT table_name 
        FROM information_schema.columns 
        WHERE table_schema = 'sportmonks' 
        AND column_name = 'updated_at'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS update_%I_updated_at ON sportmonks.%I', t, t);
        EXECUTE format('CREATE TRIGGER update_%I_updated_at BEFORE UPDATE ON sportmonks.%I FOR EACH ROW EXECUTE FUNCTION sportmonks.update_updated_at_column()', t, t);
    END LOOP;
END;
$$;

-- ============================================
-- COMENTÁRIOS NAS TABELAS
-- ============================================

COMMENT ON SCHEMA sportmonks IS 'Schema para dados da Sportmonks API';
COMMENT ON TABLE sportmonks.countries IS 'Países disponíveis na API';
COMMENT ON TABLE sportmonks.leagues IS 'Ligas de futebol';
COMMENT ON TABLE sportmonks.seasons IS 'Temporadas das ligas';
COMMENT ON TABLE sportmonks.teams IS 'Times de futebol';
COMMENT ON TABLE sportmonks.venues IS 'Estádios e locais de jogos';
COMMENT ON TABLE sportmonks.players IS 'Jogadores de futebol';
COMMENT ON TABLE sportmonks.coaches IS 'Técnicos e comissão técnica';
COMMENT ON TABLE sportmonks.referees IS 'Árbitros';
COMMENT ON TABLE sportmonks.fixtures IS 'Partidas de futebol';
COMMENT ON TABLE sportmonks.fixture_events IS 'Eventos das partidas (gols, cartões, substituições)';
COMMENT ON TABLE sportmonks.fixture_statistics IS 'Estatísticas detalhadas das partidas';
COMMENT ON TABLE sportmonks.fixture_lineups IS 'Escalações das partidas';
COMMENT ON TABLE sportmonks.standings IS 'Classificações das ligas';
COMMENT ON TABLE sportmonks.transfers IS 'Transferências de jogadores';
COMMENT ON TABLE sportmonks.states IS 'Estados/Status das partidas';
COMMENT ON TABLE sportmonks.types IS 'Tipos de eventos, estatísticas, etc.';

-- ============================================
-- GRANT PERMISSIONS
-- ============================================

-- Dar permissões para as roles do Supabase
GRANT USAGE ON SCHEMA sportmonks TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA sportmonks TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA sportmonks TO anon, authenticated, service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA sportmonks TO anon, authenticated, service_role;
