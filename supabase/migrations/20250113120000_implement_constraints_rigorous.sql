-- Migração: Implementar Constraints Rigorosas
-- TASK-DB-002: Implementar Constraints e FKs Rigorosas
-- Data: 2025-01-13
-- Agente: Database Specialist 🗄️

-- 1. Constraints de validação para fixtures
ALTER TABLE fixtures 
ADD CONSTRAINT chk_fixtures_scores_positive 
CHECK (home_score IS NULL OR home_score >= 0),
ADD CONSTRAINT chk_fixtures_away_score_positive 
CHECK (away_score IS NULL OR away_score >= 0),
ADD CONSTRAINT chk_fixtures_match_date_not_future 
CHECK (match_date IS NULL OR match_date <= CURRENT_TIMESTAMP + INTERVAL '1 year'),
ADD CONSTRAINT chk_fixtures_teams_different 
CHECK (home_team_id IS NULL OR away_team_id IS NULL OR home_team_id != away_team_id);

-- 2. Constraints de validação para seasons
ALTER TABLE seasons 
ADD CONSTRAINT chk_seasons_dates_valid 
CHECK (start_date IS NULL OR end_date IS NULL OR start_date <= end_date),
ADD CONSTRAINT chk_seasons_dates_not_future 
CHECK (start_date IS NULL OR start_date <= CURRENT_DATE + INTERVAL '2 years'),
ADD CONSTRAINT chk_seasons_current_unique 
CHECK (NOT is_current OR NOT EXISTS (
    SELECT 1 FROM seasons s2 
    WHERE s2.league_id = seasons.league_id 
    AND s2.is_current = true 
    AND s2.id != seasons.id
));

-- 3. Constraints de validação para teams
ALTER TABLE teams 
ADD CONSTRAINT chk_teams_founded_valid 
CHECK (founded IS NULL OR founded >= 1800 OR founded <= EXTRACT(YEAR FROM CURRENT_DATE) + 1),
ADD CONSTRAINT chk_teams_name_not_empty 
CHECK (name IS NOT NULL AND LENGTH(TRIM(name)) > 0);

-- 4. Constraints de validação para leagues
ALTER TABLE leagues 
ADD CONSTRAINT chk_leagues_name_not_empty 
CHECK (name IS NOT NULL AND LENGTH(TRIM(name)) > 0),
ADD CONSTRAINT chk_leagues_country_valid 
CHECK (country IS NULL OR LENGTH(TRIM(country)) >= 2);

-- 5. Constraints de validação para match_events
ALTER TABLE match_events 
ADD CONSTRAINT chk_events_minute_valid 
CHECK (minute IS NULL OR minute >= 0 OR minute <= 120),
ADD CONSTRAINT chk_events_extra_minute_valid 
CHECK (extra_minute IS NULL OR extra_minute >= 0 OR extra_minute <= 30),
ADD CONSTRAINT chk_events_player_name_not_empty 
CHECK (player_name IS NULL OR LENGTH(TRIM(player_name)) > 0);

-- 6. Constraints de validação para match_statistics
ALTER TABLE match_statistics 
ADD CONSTRAINT chk_stats_shots_valid 
CHECK (shots_total IS NULL OR shots_total >= 0),
ADD CONSTRAINT chk_stats_shots_on_target_valid 
CHECK (shots_on_target IS NULL OR shots_on_target >= 0 OR shots_on_target <= shots_total),
ADD CONSTRAINT chk_stats_possession_valid 
CHECK (ball_possession IS NULL OR ball_possession >= 0 OR ball_possession <= 100),
ADD CONSTRAINT chk_stats_cards_valid 
CHECK (yellow_cards IS NULL OR yellow_cards >= 0),
ADD CONSTRAINT chk_stats_cards_valid2 
CHECK (red_cards IS NULL OR red_cards >= 0);

-- 7. Constraints de validação para match_lineups
ALTER TABLE match_lineups 
ADD CONSTRAINT chk_lineups_jersey_number_valid 
CHECK (jersey_number IS NULL OR jersey_number >= 1 OR jersey_number <= 99),
ADD CONSTRAINT chk_lineups_minutes_valid 
CHECK (minutes_played IS NULL OR minutes_played >= 0 OR minutes_played <= 120),
ADD CONSTRAINT chk_lineups_rating_valid 
CHECK (rating IS NULL OR rating >= 0 OR rating <= 10);

-- 8. Constraints de validação para players
ALTER TABLE players 
ADD CONSTRAINT chk_players_name_not_empty 
CHECK (name IS NOT NULL AND LENGTH(TRIM(name)) > 0),
ADD CONSTRAINT chk_players_height_valid 
CHECK (height IS NULL OR height >= 100 OR height <= 250),
ADD CONSTRAINT chk_players_weight_valid 
CHECK (weight IS NULL OR weight >= 30 OR weight <= 200),
ADD CONSTRAINT chk_players_birth_date_valid 
CHECK (date_of_birth IS NULL OR date_of_birth >= '1900-01-01' OR date_of_birth <= CURRENT_DATE);

-- 9. Constraints de validação para countries
ALTER TABLE countries 
ADD CONSTRAINT chk_countries_name_not_empty 
CHECK (name IS NOT NULL AND LENGTH(TRIM(name)) > 0),
ADD CONSTRAINT chk_countries_iso2_valid 
CHECK (iso2 IS NULL OR LENGTH(iso2) = 2),
ADD CONSTRAINT chk_countries_iso3_valid 
CHECK (iso3 IS NULL OR LENGTH(iso3) = 3),
ADD CONSTRAINT chk_countries_coordinates_valid 
CHECK (
    (latitude IS NULL AND longitude IS NULL) OR 
    (latitude IS NOT NULL AND longitude IS NOT NULL AND 
     latitude >= -90 AND latitude <= 90 AND 
     longitude >= -180 AND longitude <= 180)
);

-- 10. Constraints de validação para venues
ALTER TABLE venues 
ADD CONSTRAINT chk_venues_name_not_empty 
CHECK (name IS NOT NULL AND LENGTH(TRIM(name)) > 0),
ADD CONSTRAINT chk_venues_capacity_valid 
CHECK (capacity IS NULL OR capacity >= 0 OR capacity <= 200000);

-- 11. Constraints de validação para types
ALTER TABLE types 
ADD CONSTRAINT chk_types_name_not_empty 
CHECK (name IS NOT NULL AND LENGTH(TRIM(name)) > 0),
ADD CONSTRAINT chk_types_code_valid 
CHECK (code IS NULL OR LENGTH(TRIM(code)) > 0);

-- 12. Constraints de validação para api_cache
ALTER TABLE api_cache 
ADD CONSTRAINT chk_cache_key_not_empty 
CHECK (cache_key IS NOT NULL AND LENGTH(TRIM(cache_key)) > 0),
ADD CONSTRAINT chk_cache_expires_future 
CHECK (expires_at IS NULL OR expires_at > created_at);

-- Comentários para documentação
COMMENT ON CONSTRAINT chk_fixtures_scores_positive ON fixtures IS 'Scores devem ser não-negativos';
COMMENT ON CONSTRAINT chk_fixtures_teams_different ON fixtures IS 'Times devem ser diferentes';
COMMENT ON CONSTRAINT chk_seasons_dates_valid ON seasons IS 'Data de início deve ser anterior à data de fim';
COMMENT ON CONSTRAINT chk_seasons_current_unique ON seasons IS 'Apenas uma temporada atual por liga';
COMMENT ON CONSTRAINT chk_teams_name_not_empty ON teams IS 'Nome do time não pode ser vazio';
COMMENT ON CONSTRAINT chk_leagues_name_not_empty ON leagues IS 'Nome da liga não pode ser vazio';
COMMENT ON CONSTRAINT chk_events_minute_valid ON match_events IS 'Minuto deve estar entre 0 e 120';
COMMENT ON CONSTRAINT chk_stats_possession_valid ON match_statistics IS 'Posse de bola deve estar entre 0 e 100%';
COMMENT ON CONSTRAINT chk_players_height_valid ON players IS 'Altura deve estar entre 100 e 250 cm';
COMMENT ON CONSTRAINT chk_countries_coordinates_valid ON countries IS 'Coordenadas devem ser válidas';
COMMENT ON CONSTRAINT chk_venues_capacity_valid ON venues IS 'Capacidade deve estar entre 0 e 200.000';
COMMENT ON CONSTRAINT chk_cache_expires_future ON api_cache IS 'Expiração deve ser no futuro';
