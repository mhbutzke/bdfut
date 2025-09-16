-- Adicionar colunas necessárias para a tabela seasons baseada na Sportmonks API
-- Manter colunas existentes e adicionar novas

-- Adicionar coluna sportmonks_id se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'seasons' AND column_name = 'sportmonks_id') THEN
        ALTER TABLE public.seasons ADD COLUMN sportmonks_id integer;
    END IF;
END $$;

-- Adicionar coluna sport_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'seasons' AND column_name = 'sport_id') THEN
        ALTER TABLE public.seasons ADD COLUMN sport_id integer;
    END IF;
END $$;

-- Adicionar coluna country_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'seasons' AND column_name = 'country_id') THEN
        ALTER TABLE public.seasons ADD COLUMN country_id integer;
    END IF;
END $$;

-- Adicionar coluna starting_at
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'seasons' AND column_name = 'starting_at') THEN
        ALTER TABLE public.seasons ADD COLUMN starting_at timestamptz;
    END IF;
END $$;

-- Adicionar coluna ending_at
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'seasons' AND column_name = 'ending_at') THEN
        ALTER TABLE public.seasons ADD COLUMN ending_at timestamptz;
    END IF;
END $$;

-- Adicionar coluna finished
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'seasons' AND column_name = 'finished') THEN
        ALTER TABLE public.seasons ADD COLUMN finished boolean default false;
    END IF;
END $$;

-- Adicionar coluna pending
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'seasons' AND column_name = 'pending') THEN
        ALTER TABLE public.seasons ADD COLUMN pending boolean default false;
    END IF;
END $$;

-- Adicionar coluna is_current (já existe, mas vamos garantir que seja boolean)
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'seasons' AND column_name = 'is_current') THEN
        -- Coluna já existe, não fazer nada
        NULL;
    ELSE
        ALTER TABLE public.seasons ADD COLUMN is_current boolean default false;
    END IF;
END $$;

-- Adicionar coluna current_round_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'seasons' AND column_name = 'current_round_id') THEN
        ALTER TABLE public.seasons ADD COLUMN current_round_id integer;
    END IF;
END $$;

-- Adicionar coluna current_stage_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'seasons' AND column_name = 'current_stage_id') THEN
        ALTER TABLE public.seasons ADD COLUMN current_stage_id integer;
    END IF;
END $$;

-- Adicionar coluna winner_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'seasons' AND column_name = 'winner_id') THEN
        ALTER TABLE public.seasons ADD COLUMN winner_id integer;
    END IF;
END $$;

-- Adicionar constraint unique para sportmonks_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE table_name = 'seasons' AND constraint_name = 'seasons_sportmonks_id_key') THEN
        ALTER TABLE public.seasons ADD CONSTRAINT seasons_sportmonks_id_key UNIQUE (sportmonks_id);
    END IF;
END $$;

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_seasons_league_id ON public.seasons(league_id);
CREATE INDEX IF NOT EXISTS idx_seasons_sportmonks_id ON public.seasons(sportmonks_id);
CREATE INDEX IF NOT EXISTS idx_seasons_starting_at ON public.seasons(starting_at);
CREATE INDEX IF NOT EXISTS idx_seasons_ending_at ON public.seasons(ending_at);
CREATE INDEX IF NOT EXISTS idx_seasons_is_current ON public.seasons(is_current);
CREATE INDEX IF NOT EXISTS idx_seasons_finished ON public.seasons(finished);
