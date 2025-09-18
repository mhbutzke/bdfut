-- Migration: 002_create_fixtures_views.sql
-- Description: Cria views otimizadas para consultas de fixtures
-- Date: 2025-01-18
-- Author: Database Optimization Team

-- =====================================================
-- VIEW 1: FIXTURES COMPLETAS COM DADOS AGREGADOS
-- =====================================================

CREATE OR REPLACE VIEW v_fixtures_complete AS
SELECT 
    -- Dados básicos da fixture
    f.fixture_id,
    f.name as match_name,
    f.starting_at,
    f.starting_at_timestamp,
    f.match_date,
    f.status,
    f.state_id,
    f.result_info,
    f.leg,
    f.length,
    
    -- Placares e resultados
    f.home_score,
    f.away_score,
    f.total_goals,
    f.goal_difference,
    f.match_result,
    
    -- Dados da liga e temporada
    f.league_id,
    l.name as league_name,
    l.country_name as league_country,
    l.type as league_type,
    
    f.season_id,
    s.name as season_name,
    s.is_current as is_current_season,
    
    -- Dados dos times
    f.home_team_id,
    ht.name as home_team_name,
    ht.short_code as home_team_code,
    ht.image_path as home_team_logo,
    
    f.away_team_id,
    at.name as away_team_name,
    at.short_code as away_team_code,
    at.image_path as away_team_logo,
    
    -- Dados do estádio
    f.venue_id,
    v.name as venue_name,
    v.city as venue_city,
    v.capacity as venue_capacity,
    
    -- Dados do estado da partida
    st.name as state_name,
    st.short_name as state_short,
    
    -- Dados da rodada e fase
    f.round_id,
    r.name as round_name,
    f.stage_id,
    sg.name as stage_name,
    
    -- Dados do árbitro
    f.referee_id,
    f.referee_name,
    
    -- Flags de dados disponíveis
    f.has_odds,
    f.has_premium_odds,
    f.has_players,
    f.has_lineups,
    f.has_statistics,
    f.has_events,
    f.placeholder,
    f.is_deleted,
    
    -- Metadados ETL
    f.etl_processed_at,
    f.etl_version,
    f.data_quality_score,
    f.created_at,
    f.updated_at

FROM fixtures f
LEFT JOIN leagues l ON f.league_id = l.league_id
LEFT JOIN seasons s ON f.season_id = s.season_id
LEFT JOIN teams ht ON f.home_team_id = ht.team_id
LEFT JOIN teams at ON f.away_team_id = at.team_id
LEFT JOIN venues v ON f.venue_id = v.venue_id
LEFT JOIN states st ON f.state_id = st.state_id
LEFT JOIN rounds r ON f.round_id = r.round_id
LEFT JOIN stages sg ON f.stage_id = sg.stage_id;

-- Comentário da view
COMMENT ON VIEW v_fixtures_complete IS 'View completa de fixtures com todos os dados relacionados agregados para consultas otimizadas';

-- =====================================================
-- VIEW 2: FIXTURES RESUMIDAS PARA LISTAGENS
-- =====================================================

CREATE OR REPLACE VIEW v_fixtures_summary AS
SELECT 
    f.fixture_id,
    f.name as match_name,
    f.starting_at,
    f.state_id,
    st.name as state_name,
    
    -- Liga e temporada
    l.name as league_name,
    l.country_name as league_country,
    s.name as season_name,
    
    -- Times
    ht.name as home_team,
    ht.short_code as home_code,
    at.name as away_team,
    at.short_code as away_code,
    
    -- Resultado
    f.home_score,
    f.away_score,
    f.match_result,
    f.total_goals,
    
    -- Flags principais
    f.has_events,
    f.has_lineups,
    f.has_statistics

FROM fixtures f
LEFT JOIN leagues l ON f.league_id = l.league_id
LEFT JOIN seasons s ON f.season_id = s.season_id
LEFT JOIN teams ht ON f.home_team_id = ht.team_id
LEFT JOIN teams at ON f.away_team_id = at.team_id
LEFT JOIN states st ON f.state_id = st.state_id
WHERE f.is_deleted = FALSE;

-- Comentário da view
COMMENT ON VIEW v_fixtures_summary IS 'View resumida de fixtures para listagens e consultas rápidas';

-- =====================================================
-- VIEW 3: ESTATÍSTICAS POR LIGA E TEMPORADA
-- =====================================================

CREATE OR REPLACE VIEW v_league_season_stats AS
SELECT 
    l.league_id,
    l.name as league_name,
    l.country_name as league_country,
    s.season_id,
    s.name as season_name,
    s.is_current as is_current_season,
    
    -- Contadores de partidas
    COUNT(f.fixture_id) as total_matches,
    COUNT(CASE WHEN f.state_id = 5 THEN 1 END) as finished_matches,
    COUNT(CASE WHEN f.state_id != 5 AND f.starting_at > NOW() THEN 1 END) as upcoming_matches,
    COUNT(CASE WHEN f.state_id IN (1, 2, 3) THEN 1 END) as live_matches,
    
    -- Estatísticas de gols
    AVG(CASE WHEN f.total_goals IS NOT NULL THEN f.total_goals END) as avg_goals_per_match,
    MAX(f.total_goals) as max_goals_in_match,
    MIN(CASE WHEN f.total_goals IS NOT NULL THEN f.total_goals END) as min_goals_in_match,
    SUM(CASE WHEN f.total_goals IS NOT NULL THEN f.total_goals END) as total_goals_season,
    
    -- Distribuição de resultados
    COUNT(CASE WHEN f.match_result = 'home_win' THEN 1 END) as home_wins,
    COUNT(CASE WHEN f.match_result = 'away_win' THEN 1 END) as away_wins,
    COUNT(CASE WHEN f.match_result = 'draw' THEN 1 END) as draws,
    
    -- Percentuais
    ROUND(
        COUNT(CASE WHEN f.match_result = 'home_win' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN f.match_result IS NOT NULL THEN 1 END), 0), 2
    ) as home_win_percentage,
    
    -- Qualidade dos dados
    COUNT(CASE WHEN f.has_events = true THEN 1 END) as matches_with_events,
    COUNT(CASE WHEN f.has_lineups = true THEN 1 END) as matches_with_lineups,
    COUNT(CASE WHEN f.has_statistics = true THEN 1 END) as matches_with_statistics,
    
    -- Datas
    MIN(f.starting_at) as season_start_date,
    MAX(f.starting_at) as season_end_date,
    MAX(f.updated_at) as last_updated

FROM leagues l
JOIN seasons s ON l.league_id = s.league_id
LEFT JOIN fixtures f ON s.season_id = f.season_id AND f.is_deleted = FALSE
GROUP BY 
    l.league_id, l.name, l.country_name,
    s.season_id, s.name, s.is_current
HAVING COUNT(f.fixture_id) > 0
ORDER BY l.name, s.season_id DESC;

-- Comentário da view
COMMENT ON VIEW v_league_season_stats IS 'Estatísticas agregadas por liga e temporada para dashboards e relatórios';

-- =====================================================
-- VIEW 4: FIXTURES DO DIA (ÚTIL PARA LIVESCORES)
-- =====================================================

CREATE OR REPLACE VIEW v_fixtures_today AS
SELECT 
    f.fixture_id,
    f.name as match_name,
    f.starting_at,
    f.starting_at_timestamp,
    f.state_id,
    st.name as state_name,
    
    -- Liga
    l.name as league_name,
    l.country_name as league_country,
    
    -- Times
    ht.name as home_team,
    ht.short_code as home_code,
    ht.image_path as home_logo,
    at.name as away_team,
    at.short_code as away_code,
    at.image_path as away_logo,
    
    -- Resultado
    f.home_score,
    f.away_score,
    f.match_result,
    
    -- Estádio
    v.name as venue_name,
    v.city as venue_city

FROM fixtures f
LEFT JOIN leagues l ON f.league_id = l.league_id
LEFT JOIN teams ht ON f.home_team_id = ht.team_id
LEFT JOIN teams at ON f.away_team_id = at.team_id
LEFT JOIN venues v ON f.venue_id = v.venue_id
LEFT JOIN states st ON f.state_id = st.state_id
WHERE 
    f.starting_at::date = CURRENT_DATE
    AND f.is_deleted = FALSE
ORDER BY f.starting_at;

-- Comentário da view
COMMENT ON VIEW v_fixtures_today IS 'Fixtures do dia atual para livescores e aplicações em tempo real';

-- =====================================================
-- VIEW 5: TOP SCORERS POR PARTIDA (USANDO EVENTS)
-- =====================================================

CREATE OR REPLACE VIEW v_top_scoring_matches AS
SELECT 
    f.fixture_id,
    f.name as match_name,
    f.starting_at,
    l.name as league_name,
    f.total_goals,
    f.home_score,
    f.away_score,
    ht.name as home_team,
    at.name as away_team,
    
    -- Ranking por gols
    RANK() OVER (PARTITION BY f.league_id ORDER BY f.total_goals DESC) as goals_rank_in_league,
    RANK() OVER (ORDER BY f.total_goals DESC) as goals_rank_overall

FROM fixtures f
LEFT JOIN leagues l ON f.league_id = l.league_id
LEFT JOIN teams ht ON f.home_team_id = ht.team_id
LEFT JOIN teams at ON f.away_team_id = at.team_id
WHERE 
    f.total_goals IS NOT NULL 
    AND f.total_goals > 0
    AND f.state_id = 5  -- Apenas partidas finalizadas
    AND f.is_deleted = FALSE
ORDER BY f.total_goals DESC, f.starting_at DESC;

-- Comentário da view
COMMENT ON VIEW v_top_scoring_matches IS 'Partidas com mais gols para análises estatísticas e destaques';

-- =====================================================
-- ÍNDICES PARA OTIMIZAÇÃO DAS VIEWS
-- =====================================================

-- Índices para v_fixtures_today (consultas por data)
CREATE INDEX IF NOT EXISTS idx_fixtures_starting_date ON fixtures(starting_at::date) 
WHERE is_deleted = FALSE;

-- Índices para estatísticas por liga/temporada
CREATE INDEX IF NOT EXISTS idx_fixtures_league_season_state ON fixtures(league_id, season_id, state_id) 
WHERE is_deleted = FALSE;

-- Índices para rankings de gols
CREATE INDEX IF NOT EXISTS idx_fixtures_total_goals_desc ON fixtures(total_goals DESC) 
WHERE total_goals IS NOT NULL AND state_id = 5 AND is_deleted = FALSE;

-- =====================================================
-- GRANTS DE SEGURANÇA (AJUSTAR CONFORME NECESSÁRIO)
-- =====================================================

-- Conceder acesso às views para usuários de leitura
-- GRANT SELECT ON v_fixtures_complete TO readonly_user;
-- GRANT SELECT ON v_fixtures_summary TO readonly_user;
-- GRANT SELECT ON v_league_season_stats TO readonly_user;
-- GRANT SELECT ON v_fixtures_today TO readonly_user;
-- GRANT SELECT ON v_top_scoring_matches TO readonly_user;

-- =====================================================
-- QUERIES DE TESTE PARA VALIDAÇÃO
-- =====================================================

-- Testar view completa
-- SELECT * FROM v_fixtures_complete LIMIT 5;

-- Testar view de estatísticas
-- SELECT * FROM v_league_season_stats WHERE is_current_season = true LIMIT 10;

-- Testar fixtures do dia
-- SELECT * FROM v_fixtures_today;

-- Testar top scoring matches
-- SELECT * FROM v_top_scoring_matches LIMIT 20;
