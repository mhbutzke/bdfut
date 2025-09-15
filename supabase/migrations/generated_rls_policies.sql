-- ================================================================
-- SCRIPT DE APLICAÇÃO RLS - GERADO AUTOMATICAMENTE
-- ================================================================
-- Responsável: Security Specialist 🔐
-- Task: SEC-002 - Implementar Row Level Security (RLS)
-- Gerado em: 1757951937.381166

BEGIN;


-- ================================================================
-- TABELA: LEAGUES
-- ================================================================
-- enable_rls: enable_rls_leagues
ALTER TABLE public.leagues ENABLE ROW LEVEL SECURITY;

-- select_policy: leagues_select_policy
CREATE POLICY "leagues_select_policy" ON public.leagues
                    FOR SELECT USING (true);

-- insert_policy: leagues_insert_policy
CREATE POLICY "leagues_insert_policy" ON public.leagues
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: leagues_update_policy
CREATE POLICY "leagues_update_policy" ON public.leagues
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: leagues_delete_policy
CREATE POLICY "leagues_delete_policy" ON public.leagues
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: SEASONS
-- ================================================================
-- enable_rls: enable_rls_seasons
ALTER TABLE public.seasons ENABLE ROW LEVEL SECURITY;

-- select_policy: seasons_select_policy
CREATE POLICY "seasons_select_policy" ON public.seasons
                    FOR SELECT USING (true);

-- insert_policy: seasons_insert_policy
CREATE POLICY "seasons_insert_policy" ON public.seasons
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: seasons_update_policy
CREATE POLICY "seasons_update_policy" ON public.seasons
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: seasons_delete_policy
CREATE POLICY "seasons_delete_policy" ON public.seasons
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: TEAMS
-- ================================================================
-- enable_rls: enable_rls_teams
ALTER TABLE public.teams ENABLE ROW LEVEL SECURITY;

-- select_policy: teams_select_policy
CREATE POLICY "teams_select_policy" ON public.teams
                    FOR SELECT USING (true);

-- insert_policy: teams_insert_policy
CREATE POLICY "teams_insert_policy" ON public.teams
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: teams_update_policy
CREATE POLICY "teams_update_policy" ON public.teams
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: teams_delete_policy
CREATE POLICY "teams_delete_policy" ON public.teams
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: FIXTURES
-- ================================================================
-- enable_rls: enable_rls_fixtures
ALTER TABLE public.fixtures ENABLE ROW LEVEL SECURITY;

-- select_policy: fixtures_select_policy
CREATE POLICY "fixtures_select_policy" ON public.fixtures
                    FOR SELECT USING (true);

-- insert_policy: fixtures_insert_policy
CREATE POLICY "fixtures_insert_policy" ON public.fixtures
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: fixtures_update_policy
CREATE POLICY "fixtures_update_policy" ON public.fixtures
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: fixtures_delete_policy
CREATE POLICY "fixtures_delete_policy" ON public.fixtures
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: MATCH_EVENTS
-- ================================================================
-- enable_rls: enable_rls_match_events
ALTER TABLE public.match_events ENABLE ROW LEVEL SECURITY;

-- select_policy: match_events_select_policy
CREATE POLICY "match_events_select_policy" ON public.match_events
                    FOR SELECT USING (true);

-- insert_policy: match_events_insert_policy
CREATE POLICY "match_events_insert_policy" ON public.match_events
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: match_events_update_policy
CREATE POLICY "match_events_update_policy" ON public.match_events
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: match_events_delete_policy
CREATE POLICY "match_events_delete_policy" ON public.match_events
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: MATCH_STATISTICS
-- ================================================================
-- enable_rls: enable_rls_match_statistics
ALTER TABLE public.match_statistics ENABLE ROW LEVEL SECURITY;

-- select_policy: match_statistics_select_policy
CREATE POLICY "match_statistics_select_policy" ON public.match_statistics
                    FOR SELECT USING (true);

-- insert_policy: match_statistics_insert_policy
CREATE POLICY "match_statistics_insert_policy" ON public.match_statistics
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: match_statistics_update_policy
CREATE POLICY "match_statistics_update_policy" ON public.match_statistics
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: match_statistics_delete_policy
CREATE POLICY "match_statistics_delete_policy" ON public.match_statistics
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: MATCH_LINEUPS
-- ================================================================
-- enable_rls: enable_rls_match_lineups
ALTER TABLE public.match_lineups ENABLE ROW LEVEL SECURITY;

-- select_policy: match_lineups_select_policy
CREATE POLICY "match_lineups_select_policy" ON public.match_lineups
                    FOR SELECT USING (true);

-- insert_policy: match_lineups_insert_policy
CREATE POLICY "match_lineups_insert_policy" ON public.match_lineups
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: match_lineups_update_policy
CREATE POLICY "match_lineups_update_policy" ON public.match_lineups
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: match_lineups_delete_policy
CREATE POLICY "match_lineups_delete_policy" ON public.match_lineups
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: VENUES
-- ================================================================
-- enable_rls: enable_rls_venues
ALTER TABLE public.venues ENABLE ROW LEVEL SECURITY;

-- select_policy: venues_select_policy
CREATE POLICY "venues_select_policy" ON public.venues
                    FOR SELECT USING (true);

-- insert_policy: venues_insert_policy
CREATE POLICY "venues_insert_policy" ON public.venues
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: venues_update_policy
CREATE POLICY "venues_update_policy" ON public.venues
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: venues_delete_policy
CREATE POLICY "venues_delete_policy" ON public.venues
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: REFEREES
-- ================================================================
-- enable_rls: enable_rls_referees
ALTER TABLE public.referees ENABLE ROW LEVEL SECURITY;

-- select_policy: referees_select_policy
CREATE POLICY "referees_select_policy" ON public.referees
                    FOR SELECT USING (true);

-- insert_policy: referees_insert_policy
CREATE POLICY "referees_insert_policy" ON public.referees
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: referees_update_policy
CREATE POLICY "referees_update_policy" ON public.referees
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: referees_delete_policy
CREATE POLICY "referees_delete_policy" ON public.referees
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: PLAYERS
-- ================================================================
-- enable_rls: enable_rls_players
ALTER TABLE public.players ENABLE ROW LEVEL SECURITY;

-- select_policy: players_select_policy
CREATE POLICY "players_select_policy" ON public.players
                    FOR SELECT USING (true);

-- insert_policy: players_insert_policy
CREATE POLICY "players_insert_policy" ON public.players
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: players_update_policy
CREATE POLICY "players_update_policy" ON public.players
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: players_delete_policy
CREATE POLICY "players_delete_policy" ON public.players
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: COACHES
-- ================================================================
-- enable_rls: enable_rls_coaches
ALTER TABLE public.coaches ENABLE ROW LEVEL SECURITY;

-- select_policy: coaches_select_policy
CREATE POLICY "coaches_select_policy" ON public.coaches
                    FOR SELECT USING (true);

-- insert_policy: coaches_insert_policy
CREATE POLICY "coaches_insert_policy" ON public.coaches
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: coaches_update_policy
CREATE POLICY "coaches_update_policy" ON public.coaches
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: coaches_delete_policy
CREATE POLICY "coaches_delete_policy" ON public.coaches
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: STATES
-- ================================================================
-- enable_rls: enable_rls_states
ALTER TABLE public.states ENABLE ROW LEVEL SECURITY;

-- select_policy: states_select_policy
CREATE POLICY "states_select_policy" ON public.states
                    FOR SELECT USING (true);

-- insert_policy: states_insert_policy
CREATE POLICY "states_insert_policy" ON public.states
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: states_update_policy
CREATE POLICY "states_update_policy" ON public.states
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: states_delete_policy
CREATE POLICY "states_delete_policy" ON public.states
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: TYPES
-- ================================================================
-- enable_rls: enable_rls_types
ALTER TABLE public.types ENABLE ROW LEVEL SECURITY;

-- select_policy: types_select_policy
CREATE POLICY "types_select_policy" ON public.types
                    FOR SELECT USING (true);

-- insert_policy: types_insert_policy
CREATE POLICY "types_insert_policy" ON public.types
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: types_update_policy
CREATE POLICY "types_update_policy" ON public.types
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: types_delete_policy
CREATE POLICY "types_delete_policy" ON public.types
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: COUNTRIES
-- ================================================================
-- enable_rls: enable_rls_countries
ALTER TABLE public.countries ENABLE ROW LEVEL SECURITY;

-- select_policy: countries_select_policy
CREATE POLICY "countries_select_policy" ON public.countries
                    FOR SELECT USING (true);

-- insert_policy: countries_insert_policy
CREATE POLICY "countries_insert_policy" ON public.countries
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: countries_update_policy
CREATE POLICY "countries_update_policy" ON public.countries
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: countries_delete_policy
CREATE POLICY "countries_delete_policy" ON public.countries
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: STAGES
-- ================================================================
-- enable_rls: enable_rls_stages
ALTER TABLE public.stages ENABLE ROW LEVEL SECURITY;

-- select_policy: stages_select_policy
CREATE POLICY "stages_select_policy" ON public.stages
                    FOR SELECT USING (true);

-- insert_policy: stages_insert_policy
CREATE POLICY "stages_insert_policy" ON public.stages
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: stages_update_policy
CREATE POLICY "stages_update_policy" ON public.stages
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: stages_delete_policy
CREATE POLICY "stages_delete_policy" ON public.stages
                        FOR DELETE USING (auth.role() = 'service_role');


-- ================================================================
-- TABELA: API_CACHE
-- ================================================================
-- enable_rls: enable_rls_api_cache
ALTER TABLE public.api_cache ENABLE ROW LEVEL SECURITY;

-- select_policy: api_cache_select_policy
CREATE POLICY "api_cache_select_policy" ON public.api_cache
                        FOR SELECT USING (auth.role() = 'service_role');

-- insert_policy: api_cache_insert_policy
CREATE POLICY "api_cache_insert_policy" ON public.api_cache
                        FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- update_policy: api_cache_update_policy
CREATE POLICY "api_cache_update_policy" ON public.api_cache
                        FOR UPDATE USING (auth.role() = 'service_role');

-- delete_policy: api_cache_delete_policy
CREATE POLICY "api_cache_delete_policy" ON public.api_cache
                        FOR DELETE USING (auth.role() = 'service_role');


-- Verificar aplicação
SELECT 
    tablename,
    rowsecurity as rls_enabled,
    (SELECT COUNT(*) FROM pg_policies p WHERE p.tablename = t.tablename AND p.schemaname = 'public') as policies_count
FROM pg_tables t
WHERE schemaname = 'public'
ORDER BY tablename;

COMMIT;

-- ================================================================
-- FIM DO SCRIPT
-- ================================================================
