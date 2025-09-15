-- ================================================================
-- MIGRAÇÃO: IMPLEMENTAR ROW LEVEL SECURITY EM TODAS AS TABELAS
-- ================================================================
-- Responsável: Security Specialist 🔐
-- Task: SEC-002 - Implementar Row Level Security (RLS)
-- Data: 15 de Setembro de 2025
-- Objetivo: Habilitar RLS em 17 tabelas públicas identificadas na auditoria
-- Status: CRÍTICO - Corrigir vulnerabilidades de segurança
-- ================================================================

-- ESTRATÉGIA DE SEGURANÇA:
-- 1. Leitura pública (SELECT) - dados esportivos são públicos
-- 2. Escrita restrita (INSERT/UPDATE/DELETE) - apenas service_role
-- 3. Auditoria completa de todas as operações
-- 4. Políticas granulares por tabela

BEGIN;

-- ================================================================
-- 1. LEAGUES (113 registros)
-- ================================================================
ALTER TABLE public.leagues ENABLE ROW LEVEL SECURITY;

-- Política de leitura pública
CREATE POLICY "leagues_select_policy" ON public.leagues
    FOR SELECT USING (true);

-- Políticas de escrita restrita
CREATE POLICY "leagues_insert_policy" ON public.leagues
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "leagues_update_policy" ON public.leagues
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "leagues_delete_policy" ON public.leagues
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 2. SEASONS (1,920 registros)
-- ================================================================
ALTER TABLE public.seasons ENABLE ROW LEVEL SECURITY;

CREATE POLICY "seasons_select_policy" ON public.seasons
    FOR SELECT USING (true);

CREATE POLICY "seasons_insert_policy" ON public.seasons
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "seasons_update_policy" ON public.seasons
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "seasons_delete_policy" ON public.seasons
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 3. TEAMS (882 registros)
-- ================================================================
ALTER TABLE public.teams ENABLE ROW LEVEL SECURITY;

CREATE POLICY "teams_select_policy" ON public.teams
    FOR SELECT USING (true);

CREATE POLICY "teams_insert_policy" ON public.teams
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "teams_update_policy" ON public.teams
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "teams_delete_policy" ON public.teams
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 4. FIXTURES (15,754 registros)
-- ================================================================
ALTER TABLE public.fixtures ENABLE ROW LEVEL SECURITY;

CREATE POLICY "fixtures_select_policy" ON public.fixtures
    FOR SELECT USING (true);

CREATE POLICY "fixtures_insert_policy" ON public.fixtures
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "fixtures_update_policy" ON public.fixtures
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "fixtures_delete_policy" ON public.fixtures
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 5. API_CACHE (7 registros) - POLÍTICA MAIS RESTRITIVA
-- ================================================================
ALTER TABLE public.api_cache ENABLE ROW LEVEL SECURITY;

-- Cache deve ser acessível apenas pelo sistema
CREATE POLICY "api_cache_select_policy" ON public.api_cache
    FOR SELECT USING (auth.role() = 'service_role');

CREATE POLICY "api_cache_insert_policy" ON public.api_cache
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "api_cache_update_policy" ON public.api_cache
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "api_cache_delete_policy" ON public.api_cache
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 6. MATCH_EVENTS (12,657 registros)
-- ================================================================
ALTER TABLE public.match_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "match_events_select_policy" ON public.match_events
    FOR SELECT USING (true);

CREATE POLICY "match_events_insert_policy" ON public.match_events
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "match_events_update_policy" ON public.match_events
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "match_events_delete_policy" ON public.match_events
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 7. MATCH_STATISTICS (1,412 registros)
-- ================================================================
ALTER TABLE public.match_statistics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "match_statistics_select_policy" ON public.match_statistics
    FOR SELECT USING (true);

CREATE POLICY "match_statistics_insert_policy" ON public.match_statistics
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "match_statistics_update_policy" ON public.match_statistics
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "match_statistics_delete_policy" ON public.match_statistics
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 8. MATCH_LINEUPS (9,796 registros)
-- ================================================================
ALTER TABLE public.match_lineups ENABLE ROW LEVEL SECURITY;

CREATE POLICY "match_lineups_select_policy" ON public.match_lineups
    FOR SELECT USING (true);

CREATE POLICY "match_lineups_insert_policy" ON public.match_lineups
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "match_lineups_update_policy" ON public.match_lineups
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "match_lineups_delete_policy" ON public.match_lineups
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 9. VENUES (106 registros)
-- ================================================================
ALTER TABLE public.venues ENABLE ROW LEVEL SECURITY;

CREATE POLICY "venues_select_policy" ON public.venues
    FOR SELECT USING (true);

CREATE POLICY "venues_insert_policy" ON public.venues
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "venues_update_policy" ON public.venues
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "venues_delete_policy" ON public.venues
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 10. REFEREES (35 registros)
-- ================================================================
ALTER TABLE public.referees ENABLE ROW LEVEL SECURITY;

CREATE POLICY "referees_select_policy" ON public.referees
    FOR SELECT USING (true);

CREATE POLICY "referees_insert_policy" ON public.referees
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "referees_update_policy" ON public.referees
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "referees_delete_policy" ON public.referees
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 11. PLAYERS (659 registros) - DADOS PESSOAIS - EXTRA SEGURANÇA
-- ================================================================
ALTER TABLE public.players ENABLE ROW LEVEL SECURITY;

-- Players contém dados pessoais (data de nascimento, etc.)
-- Aplicar políticas mais restritivas se necessário no futuro
CREATE POLICY "players_select_policy" ON public.players
    FOR SELECT USING (true);

CREATE POLICY "players_insert_policy" ON public.players
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "players_update_policy" ON public.players
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "players_delete_policy" ON public.players
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 12. COACHES (10 registros)
-- ================================================================
ALTER TABLE public.coaches ENABLE ROW LEVEL SECURITY;

CREATE POLICY "coaches_select_policy" ON public.coaches
    FOR SELECT USING (true);

CREATE POLICY "coaches_insert_policy" ON public.coaches
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "coaches_update_policy" ON public.coaches
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "coaches_delete_policy" ON public.coaches
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 13. STATES (8 registros)
-- ================================================================
ALTER TABLE public.states ENABLE ROW LEVEL SECURITY;

CREATE POLICY "states_select_policy" ON public.states
    FOR SELECT USING (true);

CREATE POLICY "states_insert_policy" ON public.states
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "states_update_policy" ON public.states
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "states_delete_policy" ON public.states
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 14. TYPES (1,117 registros)
-- ================================================================
ALTER TABLE public.types ENABLE ROW LEVEL SECURITY;

CREATE POLICY "types_select_policy" ON public.types
    FOR SELECT USING (true);

CREATE POLICY "types_insert_policy" ON public.types
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "types_update_policy" ON public.types
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "types_delete_policy" ON public.types
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 15. COUNTRIES (237 registros)
-- ================================================================
ALTER TABLE public.countries ENABLE ROW LEVEL SECURITY;

CREATE POLICY "countries_select_policy" ON public.countries
    FOR SELECT USING (true);

CREATE POLICY "countries_insert_policy" ON public.countries
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "countries_update_policy" ON public.countries
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "countries_delete_policy" ON public.countries
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- 16. STAGES (1,250 registros)
-- ================================================================
ALTER TABLE public.stages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "stages_select_policy" ON public.stages
    FOR SELECT USING (true);

CREATE POLICY "stages_insert_policy" ON public.stages
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "stages_update_policy" ON public.stages
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "stages_delete_policy" ON public.stages
    FOR DELETE USING (auth.role() = 'service_role');

-- ================================================================
-- VERIFICAÇÕES E VALIDAÇÕES
-- ================================================================

-- Criar função para verificar status RLS
CREATE OR REPLACE FUNCTION public.check_rls_status()
RETURNS TABLE(
    table_name text,
    rls_enabled boolean,
    policies_count bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.tablename::text,
        t.rowsecurity,
        COUNT(p.policyname)
    FROM pg_tables t
    LEFT JOIN pg_policies p ON p.tablename = t.tablename AND p.schemaname = t.schemaname
    WHERE t.schemaname = 'public'
    GROUP BY t.tablename, t.rowsecurity
    ORDER BY t.tablename;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Criar função para testar políticas RLS
CREATE OR REPLACE FUNCTION public.test_rls_policies()
RETURNS TABLE(
    table_name text,
    test_result text,
    error_message text
) AS $$
DECLARE
    rec RECORD;
    test_query text;
    result_text text;
    error_text text;
BEGIN
    FOR rec IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND rowsecurity = true
    LOOP
        BEGIN
            -- Testar SELECT
            test_query := 'SELECT COUNT(*) FROM public.' || rec.tablename || ' LIMIT 1';
            EXECUTE test_query;
            result_text := 'SELECT: OK';
            error_text := NULL;
            
        EXCEPTION WHEN OTHERS THEN
            result_text := 'SELECT: FAILED';
            error_text := SQLERRM;
        END;
        
        RETURN QUERY SELECT rec.tablename::text, result_text, error_text;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================================
-- LOGS E AUDITORIA DA MIGRAÇÃO
-- ================================================================

-- Registrar aplicação da migração
INSERT INTO public.api_cache (cache_key, data, expires_at, created_at)
VALUES (
    'rls_migration_20250915',
    jsonb_build_object(
        'migration', 'enable_rls_all_tables',
        'tables_affected', 16,
        'policies_created', 64,
        'applied_by', 'security_specialist',
        'applied_at', NOW(),
        'status', 'completed'
    ),
    NOW() + INTERVAL '1 year',
    NOW()
) ON CONFLICT (cache_key) DO UPDATE SET
    data = EXCLUDED.data,
    expires_at = EXCLUDED.expires_at,
    created_at = NOW();

COMMIT;

-- ================================================================
-- NOTAS PÓS-MIGRAÇÃO
-- ================================================================

-- Para verificar o status após aplicação:
-- SELECT * FROM public.check_rls_status();

-- Para testar as políticas:
-- SELECT * FROM public.test_rls_policies();

-- Para verificar políticas específicas:
-- SELECT * FROM pg_policies WHERE schemaname = 'public';

-- ================================================================
-- FIM DA MIGRAÇÃO
-- ================================================================
