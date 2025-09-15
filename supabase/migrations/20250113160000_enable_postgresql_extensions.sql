-- Migração: Habilitar Extensões PostgreSQL
-- TASK-DB-006: Habilitar Extensões PostgreSQL
-- Data: 2025-01-13
-- Agente: Database Specialist 🗄️

-- Habilitando extensões úteis para funcionalidades avançadas

-- 1. EXTENSÕES JÁ HABILITADAS (verificação)
-- pgcrypto: Funções criptográficas
-- uuid-ossp: Geração de UUIDs
-- pg_stat_statements: Estatísticas de queries

-- 2. HABILITAR EXTENSÕES PARA BUSCA DE TEXTO

-- pg_trgm: Busca por similaridade usando trigramas
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- unaccent: Remover acentos para busca
CREATE EXTENSION IF NOT EXISTS unaccent;

-- fuzzystrmatch: Busca fuzzy e distância entre strings
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;

-- 3. HABILITAR EXTENSÕES PARA ÍNDICES AVANÇADOS

-- btree_gin: Suporte a tipos comuns em índices GIN
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- btree_gist: Suporte a tipos comuns em índices GiST
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- 4. HABILITAR EXTENSÕES PARA MANIPULAÇÃO DE DADOS

-- tablefunc: Funções para manipular tabelas (crosstab, etc.)
CREATE EXTENSION IF NOT EXISTS tablefunc;

-- 5. CRIAR FUNÇÕES PERSONALIZADAS USANDO AS EXTENSÕES

-- Função para busca de nomes sem acento e case-insensitive
CREATE OR REPLACE FUNCTION search_player_name(search_term text)
RETURNS TABLE(
    player_id integer,
    player_name varchar,
    similarity_score real
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.sportmonks_id as player_id,
        p.name as player_name,
        similarity(unaccent(lower(p.name)), unaccent(lower(search_term))) as similarity_score
    FROM players p
    WHERE similarity(unaccent(lower(p.name)), unaccent(lower(search_term))) > 0.3
    ORDER BY similarity_score DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- Função para busca de times sem acento e case-insensitive
CREATE OR REPLACE FUNCTION search_team_name(search_term text)
RETURNS TABLE(
    team_id integer,
    team_name varchar,
    similarity_score real
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.sportmonks_id as team_id,
        t.name as team_name,
        similarity(unaccent(lower(t.name)), unaccent(lower(search_term))) as similarity_score
    FROM teams t
    WHERE similarity(unaccent(lower(t.name)), unaccent(lower(search_term))) > 0.3
    ORDER BY similarity_score DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- Função para busca de ligas sem acento e case-insensitive
CREATE OR REPLACE FUNCTION search_league_name(search_term text)
RETURNS TABLE(
    league_id integer,
    league_name varchar,
    country varchar,
    similarity_score real
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.sportmonks_id as league_id,
        l.name as league_name,
        l.country,
        similarity(unaccent(lower(l.name)), unaccent(lower(search_term))) as similarity_score
    FROM leagues l
    WHERE similarity(unaccent(lower(l.name)), unaccent(lower(search_term))) > 0.3
    ORDER BY similarity_score DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- 6. FUNÇÃO PARA GERAÇÃO DE UUIDs CUSTOMIZADOS

-- Função para gerar UUID v4 com prefixo
CREATE OR REPLACE FUNCTION generate_prefixed_uuid(prefix text)
RETURNS text AS $$
BEGIN
    RETURN prefix || '_' || replace(uuid_generate_v4()::text, '-', '');
END;
$$ LANGUAGE plpgsql;

-- 7. FUNÇÕES CRIPTOGRÁFICAS PERSONALIZADAS

-- Função para hash seguro de senhas (usando bcrypt-like)
CREATE OR REPLACE FUNCTION hash_password(password text, salt text DEFAULT NULL)
RETURNS text AS $$
BEGIN
    IF salt IS NULL THEN
        salt := gen_salt('bf', 8);
    END IF;
    RETURN crypt(password, salt);
END;
$$ LANGUAGE plpgsql;

-- Função para verificar senha
CREATE OR REPLACE FUNCTION verify_password(password text, hash text)
RETURNS boolean AS $$
BEGIN
    RETURN hash = crypt(password, hash);
END;
$$ LANGUAGE plpgsql;

-- 8. FUNÇÃO PARA ESTATÍSTICAS AVANÇADAS

-- Função para obter estatísticas de performance de queries
CREATE OR REPLACE FUNCTION get_query_stats(limit_count integer DEFAULT 10)
RETURNS TABLE(
    query text,
    calls bigint,
    total_time double precision,
    mean_time double precision,
    rows bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pss.query,
        pss.calls,
        pss.total_exec_time as total_time,
        pss.mean_exec_time as mean_time,
        pss.rows
    FROM pg_stat_statements pss
    WHERE pss.query NOT LIKE '%pg_stat_statements%'
    ORDER BY pss.total_exec_time DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- 9. FUNÇÃO PARA ANÁLISE DE DISTÂNCIA ENTRE STRINGS

-- Função para encontrar nomes similares usando Levenshtein
CREATE OR REPLACE FUNCTION find_similar_names(
    table_name text, 
    column_name text, 
    search_term text, 
    max_distance integer DEFAULT 3
)
RETURNS TABLE(
    name text,
    distance integer
) AS $$
BEGIN
    RETURN QUERY EXECUTE format('
        SELECT %I as name, levenshtein(%I, %L) as distance
        FROM %I
        WHERE levenshtein(%I, %L) <= %L
        ORDER BY distance
        LIMIT 20',
        column_name, column_name, search_term,
        table_name,
        column_name, search_term, max_distance
    );
END;
$$ LANGUAGE plpgsql;

-- 10. CRIAR ÍNDICES ESPECIALIZADOS USANDO AS EXTENSÕES

-- Índices GIN para busca de texto em nomes
CREATE INDEX CONCURRENTLY idx_players_name_gin_trgm 
ON players USING gin (name gin_trgm_ops);

CREATE INDEX CONCURRENTLY idx_teams_name_gin_trgm 
ON teams USING gin (name gin_trgm_ops);

CREATE INDEX CONCURRENTLY idx_leagues_name_gin_trgm 
ON leagues USING gin (name gin_trgm_ops);

-- Índices para busca sem acento
CREATE INDEX CONCURRENTLY idx_players_name_unaccent 
ON players USING gin (unaccent(lower(name)) gin_trgm_ops);

CREATE INDEX CONCURRENTLY idx_teams_name_unaccent 
ON teams USING gin (unaccent(lower(name)) gin_trgm_ops);

CREATE INDEX CONCURRENTLY idx_leagues_name_unaccent 
ON leagues USING gin (unaccent(lower(name)) gin_trgm_ops);

-- 11. FUNÇÃO PARA CROSSTAB DE ESTATÍSTICAS

-- Função para criar tabela cruzada de estatísticas por time e temporada
CREATE OR REPLACE FUNCTION team_stats_crosstab(season_filter integer DEFAULT NULL)
RETURNS TABLE(
    team_name varchar,
    total_games bigint,
    wins bigint,
    draws bigint,
    losses bigint,
    goals_scored bigint,
    goals_conceded bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.name as team_name,
        COUNT(*) as total_games,
        COUNT(CASE WHEN 
            (f.home_team_id = t.sportmonks_id AND f.home_score > f.away_score) OR
            (f.away_team_id = t.sportmonks_id AND f.away_score > f.home_score)
        THEN 1 END) as wins,
        COUNT(CASE WHEN f.home_score = f.away_score THEN 1 END) as draws,
        COUNT(CASE WHEN 
            (f.home_team_id = t.sportmonks_id AND f.home_score < f.away_score) OR
            (f.away_team_id = t.sportmonks_id AND f.away_score < f.home_score)
        THEN 1 END) as losses,
        SUM(CASE 
            WHEN f.home_team_id = t.sportmonks_id THEN f.home_score
            WHEN f.away_team_id = t.sportmonks_id THEN f.away_score
            ELSE 0
        END) as goals_scored,
        SUM(CASE 
            WHEN f.home_team_id = t.sportmonks_id THEN f.away_score
            WHEN f.away_team_id = t.sportmonks_id THEN f.home_score
            ELSE 0
        END) as goals_conceded
    FROM teams t
    JOIN fixtures f ON (f.home_team_id = t.sportmonks_id OR f.away_team_id = t.sportmonks_id)
    WHERE (season_filter IS NULL OR f.season_id = season_filter)
    AND f.home_score IS NOT NULL AND f.away_score IS NOT NULL
    GROUP BY t.sportmonks_id, t.name
    ORDER BY wins DESC, goals_scored DESC;
END;
$$ LANGUAGE plpgsql;

-- 12. FUNÇÃO PARA VALIDAÇÃO DE DADOS

-- Função para validar integridade dos dados usando criptografia
CREATE OR REPLACE FUNCTION validate_data_integrity()
RETURNS TABLE(
    table_name text,
    record_count bigint,
    checksum text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'fixtures'::text,
        COUNT(*)::bigint,
        md5(string_agg(sportmonks_id::text, ',' ORDER BY sportmonks_id))
    FROM fixtures
    
    UNION ALL
    
    SELECT 
        'teams'::text,
        COUNT(*)::bigint,
        md5(string_agg(sportmonks_id::text, ',' ORDER BY sportmonks_id))
    FROM teams
    
    UNION ALL
    
    SELECT 
        'players'::text,
        COUNT(*)::bigint,
        md5(string_agg(sportmonks_id::text, ',' ORDER BY sportmonks_id))
    FROM players
    
    UNION ALL
    
    SELECT 
        'leagues'::text,
        COUNT(*)::bigint,
        md5(string_agg(sportmonks_id::text, ',' ORDER BY sportmonks_id))
    FROM leagues;
END;
$$ LANGUAGE plpgsql;

-- Comentários para documentação
COMMENT ON EXTENSION pg_trgm IS 'Busca por similaridade usando trigramas para nomes de jogadores, times e ligas';
COMMENT ON EXTENSION unaccent IS 'Remoção de acentos para busca normalizada em nomes';
COMMENT ON EXTENSION fuzzystrmatch IS 'Busca fuzzy e cálculo de distância entre strings';
COMMENT ON EXTENSION btree_gin IS 'Suporte a índices GIN para tipos comuns de dados';
COMMENT ON EXTENSION btree_gist IS 'Suporte a índices GiST para tipos comuns de dados';
COMMENT ON EXTENSION tablefunc IS 'Funções para manipulação de tabelas e crosstab';

COMMENT ON FUNCTION search_player_name(text) IS 'Busca jogadores por nome com similaridade e sem acento';
COMMENT ON FUNCTION search_team_name(text) IS 'Busca times por nome com similaridade e sem acento';
COMMENT ON FUNCTION search_league_name(text) IS 'Busca ligas por nome com similaridade e sem acento';
COMMENT ON FUNCTION generate_prefixed_uuid(text) IS 'Gera UUID v4 com prefixo personalizado';
COMMENT ON FUNCTION hash_password(text, text) IS 'Gera hash seguro de senha usando bcrypt';
COMMENT ON FUNCTION verify_password(text, text) IS 'Verifica senha contra hash bcrypt';
COMMENT ON FUNCTION get_query_stats(integer) IS 'Obtém estatísticas de performance das queries mais lentas';
COMMENT ON FUNCTION find_similar_names(text, text, text, integer) IS 'Encontra nomes similares usando distância Levenshtein';
COMMENT ON FUNCTION team_stats_crosstab(integer) IS 'Cria tabela cruzada de estatísticas por time';
COMMENT ON FUNCTION validate_data_integrity() IS 'Valida integridade dos dados principais usando checksums';
