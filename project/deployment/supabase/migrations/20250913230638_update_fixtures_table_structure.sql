-- Adicionar colunas necessárias para a tabela fixtures baseada na Sportmonks API
-- Manter colunas existentes e adicionar novas

-- Adicionar coluna sport_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'sport_id') THEN
        ALTER TABLE public.fixtures ADD COLUMN sport_id integer;
    END IF;
END $$;

-- Adicionar coluna country_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'country_id') THEN
        ALTER TABLE public.fixtures ADD COLUMN country_id integer;
    END IF;
END $$;

-- Adicionar coluna round_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'round_id') THEN
        ALTER TABLE public.fixtures ADD COLUMN round_id integer;
    END IF;
END $$;

-- Adicionar coluna stage_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'stage_id') THEN
        ALTER TABLE public.fixtures ADD COLUMN stage_id integer;
    END IF;
END $$;

-- Adicionar coluna group_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'group_id') THEN
        ALTER TABLE public.fixtures ADD COLUMN group_id integer;
    END IF;
END $$;

-- Adicionar coluna aggregate_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'aggregate_id') THEN
        ALTER TABLE public.fixtures ADD COLUMN aggregate_id integer;
    END IF;
END $$;

-- Adicionar coluna starting_at (se não existir)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'starting_at') THEN
        ALTER TABLE public.fixtures ADD COLUMN starting_at timestamptz;
    END IF;
END $$;

-- Adicionar coluna result_info
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'result_info') THEN
        ALTER TABLE public.fixtures ADD COLUMN result_info jsonb;
    END IF;
END $$;

-- Adicionar coluna leg
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'leg') THEN
        ALTER TABLE public.fixtures ADD COLUMN leg text;
    END IF;
END $$;

-- Adicionar coluna details
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'details') THEN
        ALTER TABLE public.fixtures ADD COLUMN details text;
    END IF;
END $$;

-- Adicionar coluna length
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'length') THEN
        ALTER TABLE public.fixtures ADD COLUMN length integer;
    END IF;
END $$;

-- Adicionar coluna placeholder
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'placeholder') THEN
        ALTER TABLE public.fixtures ADD COLUMN placeholder boolean default false;
    END IF;
END $$;

-- Adicionar coluna has_odds
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'has_odds') THEN
        ALTER TABLE public.fixtures ADD COLUMN has_odds boolean default false;
    END IF;
END $$;

-- Adicionar coluna has_xg
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'has_xg') THEN
        ALTER TABLE public.fixtures ADD COLUMN has_xg boolean default false;
    END IF;
END $$;

-- Adicionar coluna has_lineups
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'has_lineups') THEN
        ALTER TABLE public.fixtures ADD COLUMN has_lineups boolean default false;
    END IF;
END $$;

-- Adicionar coluna has_player_stats
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'has_player_stats') THEN
        ALTER TABLE public.fixtures ADD COLUMN has_player_stats boolean default false;
    END IF;
END $$;

-- Adicionar coluna has_events
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'has_events') THEN
        ALTER TABLE public.fixtures ADD COLUMN has_events boolean default false;
    END IF;
END $$;

-- Adicionar coluna has_statistics
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'has_statistics') THEN
        ALTER TABLE public.fixtures ADD COLUMN has_statistics boolean default false;
    END IF;
END $$;

-- Adicionar coluna has_tv_stations
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'has_tv_stations') THEN
        ALTER TABLE public.fixtures ADD COLUMN has_tv_stations boolean default false;
    END IF;
END $$;

-- Adicionar coluna has_commentaries
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'has_commentaries') THEN
        ALTER TABLE public.fixtures ADD COLUMN has_commentaries boolean default false;
    END IF;
END $$;

-- Adicionar coluna has_highlights
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'has_highlights') THEN
        ALTER TABLE public.fixtures ADD COLUMN has_highlights boolean default false;
    END IF;
END $$;

-- Adicionar coluna has_venue
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'has_venue') THEN
        ALTER TABLE public.fixtures ADD COLUMN has_venue boolean default false;
    END IF;
END $$;

-- Adicionar coluna has_referee
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'has_referee') THEN
        ALTER TABLE public.fixtures ADD COLUMN has_referee boolean default false;
    END IF;
END $$;

-- Adicionar coluna deleted
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'deleted') THEN
        ALTER TABLE public.fixtures ADD COLUMN deleted boolean default false;
    END IF;
END $$;

-- Adicionar coluna is_placeholder
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fixtures' AND column_name = 'is_placeholder') THEN
        ALTER TABLE public.fixtures ADD COLUMN is_placeholder boolean default false;
    END IF;
END $$;

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_fixtures_sportmonks_id ON public.fixtures(sportmonks_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_league_id ON public.fixtures(league_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_season_id ON public.fixtures(season_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_home_team_id ON public.fixtures(home_team_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_away_team_id ON public.fixtures(away_team_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_match_date ON public.fixtures(match_date);
CREATE INDEX IF NOT EXISTS idx_fixtures_starting_at ON public.fixtures(starting_at);
CREATE INDEX IF NOT EXISTS idx_fixtures_status ON public.fixtures(status);
CREATE INDEX IF NOT EXISTS idx_fixtures_country_id ON public.fixtures(country_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_round_id ON public.fixtures(round_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_stage_id ON public.fixtures(stage_id);
