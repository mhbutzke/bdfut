-- Migração para criar tabela de cache da API Sportmonks
-- TASK-ETL-002: Implementar Sistema de Cache API

CREATE TABLE IF NOT EXISTS api_cache (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Identificação da requisição
    endpoint VARCHAR(255) NOT NULL,
    params_hash VARCHAR(64) NOT NULL, -- Hash dos parâmetros para identificação única
    params_json JSONB, -- Parâmetros originais para debug
    
    -- Dados do cache
    response_data JSONB NOT NULL,
    response_size INTEGER, -- Tamanho da resposta em bytes
    
    -- Controle de TTL
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Metadados
    hit_count INTEGER DEFAULT 0, -- Quantas vezes foi acessado
    entity_type VARCHAR(100), -- Tipo de entidade (Fixture, Team, etc.)
    
    -- Índices para performance
    CONSTRAINT api_cache_endpoint_params_unique UNIQUE (endpoint, params_hash)
);

-- Índices para otimizar consultas
CREATE INDEX IF NOT EXISTS idx_api_cache_endpoint ON api_cache(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_cache_expires_at ON api_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_api_cache_entity_type ON api_cache(entity_type);
CREATE INDEX IF NOT EXISTS idx_api_cache_last_accessed ON api_cache(last_accessed_at);

-- Índice composto para limpeza de cache expirado
CREATE INDEX IF NOT EXISTS idx_api_cache_cleanup ON api_cache(expires_at, last_accessed_at);

-- Comentários para documentação
COMMENT ON TABLE api_cache IS 'Cache para respostas da API Sportmonks com TTL configurável';
COMMENT ON COLUMN api_cache.endpoint IS 'Endpoint da API (ex: /fixtures, /teams)';
COMMENT ON COLUMN api_cache.params_hash IS 'Hash MD5 dos parâmetros para identificação única';
COMMENT ON COLUMN api_cache.params_json IS 'Parâmetros originais em JSON para debug';
COMMENT ON COLUMN api_cache.response_data IS 'Dados da resposta da API em JSON';
COMMENT ON COLUMN api_cache.response_size IS 'Tamanho da resposta em bytes para monitoramento';
COMMENT ON COLUMN api_cache.expires_at IS 'Timestamp de expiração do cache';
COMMENT ON COLUMN api_cache.hit_count IS 'Contador de acessos ao cache';
COMMENT ON COLUMN api_cache.entity_type IS 'Tipo de entidade da API (Fixture, Team, Player, etc.)';

-- Função para limpeza automática de cache expirado
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM api_cache 
    WHERE expires_at < NOW() 
    AND last_accessed_at < NOW() - INTERVAL '1 hour';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log da limpeza
    INSERT INTO etl_jobs (job_name, status, message, created_at)
    VALUES ('cache_cleanup', 'completed', 
            'Limpeza de cache: ' || deleted_count || ' registros removidos', 
            NOW())
    ON CONFLICT DO NOTHING;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Função para obter estatísticas do cache
CREATE OR REPLACE FUNCTION get_cache_stats()
RETURNS TABLE (
    total_entries BIGINT,
    expired_entries BIGINT,
    total_hits BIGINT,
    avg_hit_rate NUMERIC,
    total_size_mb NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_entries,
        COUNT(*) FILTER (WHERE expires_at < NOW()) as expired_entries,
        COALESCE(SUM(hit_count), 0) as total_hits,
        CASE 
            WHEN COUNT(*) > 0 THEN ROUND(AVG(hit_count)::NUMERIC, 2)
            ELSE 0
        END as avg_hit_rate,
        ROUND(COALESCE(SUM(response_size), 0) / 1024.0 / 1024.0, 2) as total_size_mb
    FROM api_cache;
END;
$$ LANGUAGE plpgsql;
