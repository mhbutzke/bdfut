-- Migração: Criar Materialized Views para Agregados
-- TASK-DB-004: Criar Materialized Views para Agregados
-- Data: 2025-01-13
-- Agente: Database Specialist 🗄️

-- Baseado na auditoria de índices, criando views para queries agregadas frequentes

-- 1. MATERIALIZED VIEW: Estatísticas de Jogadores por Temporada
CREATE MATERIALIZED VIEW player_season_stats AS
SELECT 
    ml.player_id,
    p.name as player_name,
    p.position_name,
    ml.team_id,
    t.name as team_name,
    f.season_id,
    s.name as season_name,
    f.league_id,
    l.name as league_name,
    COUNT(*) as games_played,
    SUM(ml.minutes_played) as total_minutes,
    AVG(ml.minutes_played) as avg_minutes_per_game,
    AVG(ml.rating) as avg_rating,
    MAX(ml.rating) as best_rating,
    MIN(ml.rating) as worst_rating,
    COUNT(CASE WHEN ml.captain = true THEN 1 END) as captain_games,
    COUNT(CASE WHEN ml.minutes_played >= 90 THEN 1 END) as full_games,
    COUNT(CASE WHEN ml.minutes_played >= 60 AND ml.minutes_played < 90 THEN 1 END) as partial_games,
    COUNT(CASE WHEN ml.minutes_played < 60 THEN 1 END) as short_games,
    COUNT(CASE WHEN ml.minutes_played = 0 THEN 1 END) as unused_games,
    SUM(CASE WHEN ml.minutes_played > 0 THEN 1 ELSE 0 END) as games_with_minutes,
    ROUND(
        (SUM(CASE WHEN ml.minutes_played > 0 THEN 1 ELSE 0 END)::numeric / COUNT(*)) * 100, 
        2
    ) as participation_percentage,
    MAX(f.match_date) as last_game_date,
    MIN(f.match_date) as first_game_date
FROM match_lineups ml
JOIN players p ON ml.player_id = p.sportmonks_id
JOIN teams t ON ml.team_id = t.sportmonks_id
JOIN fixtures f ON ml.fixture_id = f.sportmonks_id
JOIN seasons s ON f.season_id = s.sportmonks_id
JOIN leagues l ON f.league_id = l.sportmonks_id
WHERE ml.minutes_played IS NOT NULL
GROUP BY 
    ml.player_id, p.name, p.position_name, ml.team_id, t.name, 
    f.season_id, s.name, f.league_id, l.name;

-- 2. MATERIALIZED VIEW: Estatísticas de Times por Temporada
CREATE MATERIALIZED VIEW team_season_stats AS
SELECT 
    f.league_id,
    l.name as league_name,
    f.season_id,
    s.name as season_name,
    f.home_team_id as team_id,
    t.name as team_name,
    COUNT(*) as total_games,
    COUNT(CASE WHEN f.home_score > f.away_score THEN 1 END) as wins,
    COUNT(CASE WHEN f.home_score = f.away_score THEN 1 END) as draws,
    COUNT(CASE WHEN f.home_score < f.away_score THEN 1 END) as losses,
    SUM(f.home_score) as goals_scored,
    SUM(f.away_score) as goals_conceded,
    SUM(f.home_score) - SUM(f.away_score) as goal_difference,
    ROUND(
        (COUNT(CASE WHEN f.home_score > f.away_score THEN 1 END) * 3 + 
         COUNT(CASE WHEN f.home_score = f.away_score THEN 1 END))::numeric / COUNT(*), 
        2
    ) as points_per_game,
    COUNT(CASE WHEN f.home_score > f.away_score THEN 1 END) * 3 + 
    COUNT(CASE WHEN f.home_score = f.away_score THEN 1 END) as total_points,
    ROUND(AVG(f.home_score), 2) as avg_goals_scored,
    ROUND(AVG(f.away_score), 2) as avg_goals_conceded,
    COUNT(CASE WHEN f.home_score = 0 THEN 1 END) as clean_sheets,
    COUNT(CASE WHEN f.away_score = 0 THEN 1 END) as clean_sheets_conceded,
    MAX(f.match_date) as last_game_date,
    MIN(f.match_date) as first_game_date
FROM fixtures f
JOIN teams t ON f.home_team_id = t.sportmonks_id
JOIN leagues l ON f.league_id = l.sportmonks_id
JOIN seasons s ON f.season_id = s.sportmonks_id
WHERE f.home_score IS NOT NULL AND f.away_score IS NOT NULL
GROUP BY 
    f.league_id, l.name, f.season_id, s.name, f.home_team_id, t.name

UNION ALL

SELECT 
    f.league_id,
    l.name as league_name,
    f.season_id,
    s.name as season_name,
    f.away_team_id as team_id,
    t.name as team_name,
    COUNT(*) as total_games,
    COUNT(CASE WHEN f.away_score > f.home_score THEN 1 END) as wins,
    COUNT(CASE WHEN f.away_score = f.home_score THEN 1 END) as draws,
    COUNT(CASE WHEN f.away_score < f.home_score THEN 1 END) as losses,
    SUM(f.away_score) as goals_scored,
    SUM(f.home_score) as goals_conceded,
    SUM(f.away_score) - SUM(f.home_score) as goal_difference,
    ROUND(
        (COUNT(CASE WHEN f.away_score > f.home_score THEN 1 END) * 3 + 
         COUNT(CASE WHEN f.away_score = f.home_score THEN 1 END))::numeric / COUNT(*), 
        2
    ) as points_per_game,
    COUNT(CASE WHEN f.away_score > f.home_score THEN 1 END) * 3 + 
    COUNT(CASE WHEN f.away_score = f.home_score THEN 1 END) as total_points,
    ROUND(AVG(f.away_score), 2) as avg_goals_scored,
    ROUND(AVG(f.home_score), 2) as avg_goals_conceded,
    COUNT(CASE WHEN f.away_score = 0 THEN 1 END) as clean_sheets,
    COUNT(CASE WHEN f.home_score = 0 THEN 1 END) as clean_sheets_conceded,
    MAX(f.match_date) as last_game_date,
    MIN(f.match_date) as first_game_date
FROM fixtures f
JOIN teams t ON f.away_team_id = t.sportmonks_id
JOIN leagues l ON f.league_id = l.sportmonks_id
JOIN seasons s ON f.season_id = s.sportmonks_id
WHERE f.home_score IS NOT NULL AND f.away_score IS NOT NULL
GROUP BY 
    f.league_id, l.name, f.season_id, s.name, f.away_team_id, t.name;

-- 3. MATERIALIZED VIEW: Timeline Expandida de Fixtures
CREATE MATERIALIZED VIEW fixture_timeline_expanded AS
SELECT 
    f.id,
    f.sportmonks_id,
    f.league_id,
    l.name as league_name,
    f.season_id,
    s.name as season_name,
    f.home_team_id,
    ht.name as home_team_name,
    f.away_team_id,
    at.name as away_team_name,
    f.match_date,
    f.status,
    f.home_score,
    f.away_score,
    f.venue,
    f.referee,
    -- Estatísticas agregadas
    COALESCE(home_stats.shots_total, 0) as home_shots_total,
    COALESCE(home_stats.shots_on_target, 0) as home_shots_on_target,
    COALESCE(home_stats.ball_possession, 0) as home_possession,
    COALESCE(home_stats.passes_total, 0) as home_passes_total,
    COALESCE(home_stats.passes_accurate, 0) as home_passes_accurate,
    COALESCE(home_stats.yellow_cards, 0) as home_yellow_cards,
    COALESCE(home_stats.red_cards, 0) as home_red_cards,
    COALESCE(away_stats.shots_total, 0) as away_shots_total,
    COALESCE(away_stats.shots_on_target, 0) as away_shots_on_target,
    COALESCE(away_stats.ball_possession, 0) as away_possession,
    COALESCE(away_stats.passes_total, 0) as away_passes_total,
    COALESCE(away_stats.passes_accurate, 0) as away_passes_accurate,
    COALESCE(away_stats.yellow_cards, 0) as away_yellow_cards,
    COALESCE(away_stats.red_cards, 0) as away_red_cards,
    -- Contagem de eventos
    COALESCE(event_counts.total_events, 0) as total_events,
    COALESCE(event_counts.goals, 0) as total_goals,
    COALESCE(event_counts.yellow_cards, 0) as total_yellow_cards,
    COALESCE(event_counts.red_cards, 0) as total_red_cards,
    COALESCE(event_counts.substitutions, 0) as total_substitutions,
    -- Contagem de lineups
    COALESCE(lineup_counts.home_players, 0) as home_players_count,
    COALESCE(lineup_counts.away_players, 0) as away_players_count,
    f.created_at,
    f.updated_at
FROM fixtures f
JOIN leagues l ON f.league_id = l.sportmonks_id
JOIN seasons s ON f.season_id = s.sportmonks_id
JOIN teams ht ON f.home_team_id = ht.sportmonks_id
JOIN teams at ON f.away_team_id = at.sportmonks_id
LEFT JOIN (
    SELECT 
        fixture_id,
        SUM(CASE WHEN team_id = fixtures.home_team_id THEN shots_total ELSE 0 END) as shots_total,
        SUM(CASE WHEN team_id = fixtures.home_team_id THEN shots_on_target ELSE 0 END) as shots_on_target,
        SUM(CASE WHEN team_id = fixtures.home_team_id THEN ball_possession ELSE 0 END) as ball_possession,
        SUM(CASE WHEN team_id = fixtures.home_team_id THEN passes_total ELSE 0 END) as passes_total,
        SUM(CASE WHEN team_id = fixtures.home_team_id THEN passes_accurate ELSE 0 END) as passes_accurate,
        SUM(CASE WHEN team_id = fixtures.home_team_id THEN yellow_cards ELSE 0 END) as yellow_cards,
        SUM(CASE WHEN team_id = fixtures.home_team_id THEN red_cards ELSE 0 END) as red_cards
    FROM match_statistics ms
    JOIN fixtures ON ms.fixture_id = fixtures.sportmonks_id
    GROUP BY fixture_id
) home_stats ON f.sportmonks_id = home_stats.fixture_id
LEFT JOIN (
    SELECT 
        fixture_id,
        SUM(CASE WHEN team_id = fixtures.away_team_id THEN shots_total ELSE 0 END) as shots_total,
        SUM(CASE WHEN team_id = fixtures.away_team_id THEN shots_on_target ELSE 0 END) as shots_on_target,
        SUM(CASE WHEN team_id = fixtures.away_team_id THEN ball_possession ELSE 0 END) as ball_possession,
        SUM(CASE WHEN team_id = fixtures.away_team_id THEN passes_total ELSE 0 END) as passes_total,
        SUM(CASE WHEN team_id = fixtures.away_team_id THEN passes_accurate ELSE 0 END) as passes_accurate,
        SUM(CASE WHEN team_id = fixtures.away_team_id THEN yellow_cards ELSE 0 END) as yellow_cards,
        SUM(CASE WHEN team_id = fixtures.away_team_id THEN red_cards ELSE 0 END) as red_cards
    FROM match_statistics ms
    JOIN fixtures ON ms.fixture_id = fixtures.sportmonks_id
    GROUP BY fixture_id
) away_stats ON f.sportmonks_id = away_stats.fixture_id
LEFT JOIN (
    SELECT 
        fixture_id,
        COUNT(*) as total_events,
        COUNT(CASE WHEN event_type = 'goal' THEN 1 END) as goals,
        COUNT(CASE WHEN event_type = 'yellow_card' THEN 1 END) as yellow_cards,
        COUNT(CASE WHEN event_type = 'red_card' THEN 1 END) as red_cards,
        COUNT(CASE WHEN event_type = 'substitution' THEN 1 END) as substitutions
    FROM match_events
    GROUP BY fixture_id
) event_counts ON f.sportmonks_id = event_counts.fixture_id
LEFT JOIN (
    SELECT 
        fixture_id,
        COUNT(CASE WHEN team_id = fixtures.home_team_id THEN 1 END) as home_players,
        COUNT(CASE WHEN team_id = fixtures.away_team_id THEN 1 END) as away_players
    FROM match_lineups ml
    JOIN fixtures ON ml.fixture_id = fixtures.sportmonks_id
    GROUP BY fixture_id
) lineup_counts ON f.sportmonks_id = lineup_counts.fixture_id;

-- 4. MATERIALIZED VIEW: Estatísticas de Ligas por Temporada
CREATE MATERIALIZED VIEW league_season_summary AS
SELECT 
    l.id as league_id,
    l.sportmonks_id as league_sportmonks_id,
    l.name as league_name,
    l.country as league_country,
    s.id as season_id,
    s.sportmonks_id as season_sportmonks_id,
    s.name as season_name,
    s.start_date,
    s.end_date,
    s.is_current,
    s.finished,
    COUNT(DISTINCT f.id) as total_fixtures,
    COUNT(DISTINCT CASE WHEN f.home_score IS NOT NULL AND f.away_score IS NOT NULL THEN f.id END) as completed_fixtures,
    COUNT(DISTINCT CASE WHEN f.home_score IS NULL OR f.away_score IS NULL THEN f.id END) as pending_fixtures,
    COUNT(DISTINCT f.home_team_id) as total_teams,
    SUM(f.home_score + f.away_score) as total_goals,
    ROUND(AVG(f.home_score + f.away_score), 2) as avg_goals_per_game,
    COUNT(CASE WHEN f.home_score > f.away_score THEN 1 END) as home_wins,
    COUNT(CASE WHEN f.home_score = f.away_score THEN 1 END) as draws,
    COUNT(CASE WHEN f.home_score < f.away_score THEN 1 END) as away_wins,
    ROUND(
        (COUNT(CASE WHEN f.home_score = f.away_score THEN 1 END)::numeric / 
         COUNT(CASE WHEN f.home_score IS NOT NULL AND f.away_score IS NOT NULL THEN 1 END)) * 100, 
        2
    ) as draw_percentage,
    MAX(f.match_date) as last_fixture_date,
    MIN(f.match_date) as first_fixture_date,
    COUNT(DISTINCT me.id) as total_events,
    COUNT(DISTINCT CASE WHEN me.event_type = 'goal' THEN me.id END) as total_goals_events,
    COUNT(DISTINCT ml.id) as total_lineups
FROM leagues l
JOIN seasons s ON l.sportmonks_id = s.league_id
LEFT JOIN fixtures f ON s.sportmonks_id = f.season_id
LEFT JOIN match_events me ON f.sportmonks_id = me.fixture_id
LEFT JOIN match_lineups ml ON f.sportmonks_id = ml.fixture_id
GROUP BY 
    l.id, l.sportmonks_id, l.name, l.country,
    s.id, s.sportmonks_id, s.name, s.start_date, s.end_date, s.is_current, s.finished;

-- 5. CRIAR ÍNDICES PARA AS MATERIALIZED VIEWS

-- Índices para player_season_stats
CREATE INDEX idx_player_season_stats_player_season 
ON player_season_stats (player_id, season_id);

CREATE INDEX idx_player_season_stats_team_season 
ON player_season_stats (team_id, season_id);

CREATE INDEX idx_player_season_stats_league_season 
ON player_season_stats (league_id, season_id);

CREATE INDEX idx_player_season_stats_rating 
ON player_season_stats (avg_rating DESC);

-- Índices para team_season_stats
CREATE INDEX idx_team_season_stats_team_season 
ON team_season_stats (team_id, season_id);

CREATE INDEX idx_team_season_stats_league_season 
ON team_season_stats (league_id, season_id);

CREATE INDEX idx_team_season_stats_points 
ON team_season_stats (total_points DESC);

CREATE INDEX idx_team_season_stats_goals 
ON team_season_stats (goals_scored DESC);

-- Índices para fixture_timeline_expanded
CREATE INDEX idx_fixture_timeline_date 
ON fixture_timeline_expanded (match_date DESC);

CREATE INDEX idx_fixture_timeline_league_season 
ON fixture_timeline_expanded (league_id, season_id);

CREATE INDEX idx_fixture_timeline_teams 
ON fixture_timeline_expanded (home_team_id, away_team_id);

CREATE INDEX idx_fixture_timeline_status 
ON fixture_timeline_expanded (status);

-- Índices para league_season_summary
CREATE INDEX idx_league_season_summary_league 
ON league_season_summary (league_id);

CREATE INDEX idx_league_season_summary_season 
ON league_season_summary (season_id);

CREATE INDEX idx_league_season_summary_current 
ON league_season_summary (is_current);

CREATE INDEX idx_league_season_summary_finished 
ON league_season_summary (finished);

-- 6. FUNÇÃO PARA REFRESH AUTOMÁTICO DAS VIEWS

CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    -- Refresh das views em ordem de dependência
    REFRESH MATERIALIZED VIEW CONCURRENTLY player_season_stats;
    REFRESH MATERIALIZED VIEW CONCURRENTLY team_season_stats;
    REFRESH MATERIALIZED VIEW CONCURRENTLY fixture_timeline_expanded;
    REFRESH MATERIALIZED VIEW CONCURRENTLY league_season_summary;
    
    -- Log da operação
    INSERT INTO api_cache (cache_key, data, expires_at) 
    VALUES (
        'materialized_views_refresh_' || to_char(now(), 'YYYY-MM-DD_HH24:MI:SS'),
        jsonb_build_object(
            'timestamp', now(),
            'views_refreshed', ARRAY['player_season_stats', 'team_season_stats', 'fixture_timeline_expanded', 'league_season_summary']
        ),
        now() + INTERVAL '1 day'
    );
END;
$$ LANGUAGE plpgsql;

-- Comentários para documentação
COMMENT ON MATERIALIZED VIEW player_season_stats IS 'Estatísticas agregadas de jogadores por temporada';
COMMENT ON MATERIALIZED VIEW team_season_stats IS 'Estatísticas agregadas de times por temporada';
COMMENT ON MATERIALIZED VIEW fixture_timeline_expanded IS 'Timeline expandida de fixtures com estatísticas agregadas';
COMMENT ON MATERIALIZED VIEW league_season_summary IS 'Resumo de ligas por temporada';
COMMENT ON FUNCTION refresh_materialized_views() IS 'Função para refresh automático de todas as materialized views';
