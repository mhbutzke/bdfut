create table if not exists public.stages (
    id bigint primary key generated always as identity,
    sportmonks_id integer unique not null,
    sport_id integer,
    country_id integer,
    league_id integer,
    season_id integer,
    type_id integer,
    name text,
    short_code text,
    sort_order integer,
    finished boolean default false,
    is_current boolean default false,
    starting_at timestamptz,
    ending_at timestamptz,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);
