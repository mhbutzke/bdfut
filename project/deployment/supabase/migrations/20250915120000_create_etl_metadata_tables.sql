-- Migração para criar tabelas de metadados ETL
-- TASK-ETL-003: Criar Tabelas de Metadados ETL

-- =====================================================
-- Tabela: etl_jobs
-- Objetivo: Controlar execução de jobs ETL
-- =====================================================

CREATE TABLE IF NOT EXISTS etl_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Identificação do Job
    job_name VARCHAR(255) NOT NULL,
    job_type VARCHAR(100) NOT NULL, -- 'setup', 'base_data', 'leagues_seasons', 'fixtures_events', 'quality_checks'
    script_path VARCHAR(500), -- Caminho do script executado
    
    -- Controle de Execução
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER, -- Duração em segundos
    
    -- Dados de Execução
    input_parameters JSONB, -- Parâmetros de entrada
    output_summary JSONB, -- Resumo dos resultados
    error_message TEXT, -- Mensagem de erro se falhou
    error_details JSONB, -- Detalhes técnicos do erro
    
    -- Controle de Recursos
    api_requests_made INTEGER DEFAULT 0, -- Requisições à API
    records_processed INTEGER DEFAULT 0, -- Registros processados
    records_inserted INTEGER DEFAULT 0, -- Registros inseridos
    records_updated INTEGER DEFAULT 0, -- Registros atualizados
    records_failed INTEGER DEFAULT 0, -- Registros com erro
    
    -- Metadados
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100) DEFAULT 'system',
    version VARCHAR(50), -- Versão do script/sistema
    environment VARCHAR(50) DEFAULT 'development', -- 'development', 'staging', 'production'
    
    -- Controle de Dependências
    depends_on_jobs UUID[], -- IDs de jobs que devem completar primeiro
    parent_job_id UUID REFERENCES etl_jobs(id), -- Job pai (para sub-jobs)
    
    -- Índices para performance
    CONSTRAINT etl_jobs_status_check CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    CONSTRAINT etl_jobs_job_type_check CHECK (job_type IN ('setup', 'base_data', 'leagues_seasons', 'fixtures_events', 'quality_checks', 'maintenance'))
);

-- Índices para otimizar consultas
CREATE INDEX IF NOT EXISTS idx_etl_jobs_status ON etl_jobs(status);
CREATE INDEX IF NOT EXISTS idx_etl_jobs_job_type ON etl_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_etl_jobs_job_name ON etl_jobs(job_name);
CREATE INDEX IF NOT EXISTS idx_etl_jobs_created_at ON etl_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_etl_jobs_started_at ON etl_jobs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_etl_jobs_parent_job ON etl_jobs(parent_job_id);

-- Índice composto para consultas de status e tipo
CREATE INDEX IF NOT EXISTS idx_etl_jobs_status_type ON etl_jobs(status, job_type);

-- =====================================================
-- Tabela: etl_checkpoints
-- Objetivo: Permitir retomada de jobs interrompidos
-- =====================================================

CREATE TABLE IF NOT EXISTS etl_checkpoints (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Identificação
    job_id UUID NOT NULL REFERENCES etl_jobs(id) ON DELETE CASCADE,
    checkpoint_name VARCHAR(255) NOT NULL, -- Nome do checkpoint (ex: 'leagues_processed', 'season_2023_done')
    checkpoint_type VARCHAR(100) NOT NULL, -- 'iteration', 'batch', 'milestone', 'recovery'
    
    -- Dados do Checkpoint
    checkpoint_data JSONB NOT NULL, -- Dados necessários para retomar
    progress_percentage DECIMAL(5,2) DEFAULT 0.00, -- Progresso em %
    items_processed INTEGER DEFAULT 0, -- Items processados até aqui
    items_total INTEGER, -- Total de items (se conhecido)
    
    -- Contexto de Execução
    current_step VARCHAR(255), -- Passo atual sendo executado
    next_step VARCHAR(255), -- Próximo passo a executar
    execution_context JSONB, -- Contexto de execução (variáveis, estado)
    
    -- Controle Temporal
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE, -- Quando o checkpoint expira
    is_active BOOLEAN DEFAULT true, -- Se o checkpoint está ativo
    
    -- Metadados
    notes TEXT, -- Observações sobre o checkpoint
    created_by VARCHAR(100) DEFAULT 'system',
    
    -- Constraint para evitar checkpoints duplicados ativos
    CONSTRAINT etl_checkpoints_unique_active UNIQUE (job_id, checkpoint_name, is_active) DEFERRABLE INITIALLY DEFERRED
);

-- Índices para otimizar consultas
CREATE INDEX IF NOT EXISTS idx_etl_checkpoints_job_id ON etl_checkpoints(job_id);
CREATE INDEX IF NOT EXISTS idx_etl_checkpoints_name ON etl_checkpoints(checkpoint_name);
CREATE INDEX IF NOT EXISTS idx_etl_checkpoints_type ON etl_checkpoints(checkpoint_type);
CREATE INDEX IF NOT EXISTS idx_etl_checkpoints_active ON etl_checkpoints(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_etl_checkpoints_expires ON etl_checkpoints(expires_at) WHERE expires_at IS NOT NULL;

-- Índice composto para consultas de job e checkpoint ativo
CREATE INDEX IF NOT EXISTS idx_etl_checkpoints_job_active ON etl_checkpoints(job_id, is_active) WHERE is_active = true;

-- =====================================================
-- Tabela: etl_job_logs
-- Objetivo: Logs detalhados de execução
-- =====================================================

CREATE TABLE IF NOT EXISTS etl_job_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Identificação
    job_id UUID NOT NULL REFERENCES etl_jobs(id) ON DELETE CASCADE,
    log_level VARCHAR(20) NOT NULL DEFAULT 'INFO', -- 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    
    -- Conteúdo do Log
    message TEXT NOT NULL,
    details JSONB, -- Detalhes estruturados do log
    
    -- Contexto
    component VARCHAR(100), -- Componente que gerou o log (ex: 'sportmonks_client', 'supabase_client')
    function_name VARCHAR(100), -- Função que gerou o log
    line_number INTEGER, -- Linha do código (se disponível)
    
    -- Temporal
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraint para nível de log
    CONSTRAINT etl_job_logs_level_check CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
);

-- Índices para otimizar consultas de logs
CREATE INDEX IF NOT EXISTS idx_etl_job_logs_job_id ON etl_job_logs(job_id);
CREATE INDEX IF NOT EXISTS idx_etl_job_logs_level ON etl_job_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_etl_job_logs_created_at ON etl_job_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_etl_job_logs_component ON etl_job_logs(component);

-- Índice composto para consultas por job e nível
CREATE INDEX IF NOT EXISTS idx_etl_job_logs_job_level ON etl_job_logs(job_id, log_level);

-- =====================================================
-- Funções Auxiliares
-- =====================================================

-- Função para iniciar um job ETL
CREATE OR REPLACE FUNCTION start_etl_job(
    p_job_name VARCHAR(255),
    p_job_type VARCHAR(100),
    p_script_path VARCHAR(500) DEFAULT NULL,
    p_input_parameters JSONB DEFAULT NULL,
    p_depends_on_jobs UUID[] DEFAULT NULL,
    p_parent_job_id UUID DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_job_id UUID;
BEGIN
    INSERT INTO etl_jobs (
        job_name, job_type, script_path, status, started_at,
        input_parameters, depends_on_jobs, parent_job_id
    ) VALUES (
        p_job_name, p_job_type, p_script_path, 'running', NOW(),
        p_input_parameters, p_depends_on_jobs, p_parent_job_id
    ) RETURNING id INTO v_job_id;
    
    RETURN v_job_id;
END;
$$ LANGUAGE plpgsql;

-- Função para finalizar um job ETL
CREATE OR REPLACE FUNCTION complete_etl_job(
    p_job_id UUID,
    p_status VARCHAR(50),
    p_output_summary JSONB DEFAULT NULL,
    p_error_message TEXT DEFAULT NULL,
    p_error_details JSONB DEFAULT NULL,
    p_api_requests INTEGER DEFAULT 0,
    p_records_processed INTEGER DEFAULT 0,
    p_records_inserted INTEGER DEFAULT 0,
    p_records_updated INTEGER DEFAULT 0,
    p_records_failed INTEGER DEFAULT 0
) RETURNS BOOLEAN AS $$
DECLARE
    v_started_at TIMESTAMP WITH TIME ZONE;
    v_duration INTEGER;
BEGIN
    -- Buscar data de início
    SELECT started_at INTO v_started_at FROM etl_jobs WHERE id = p_job_id;
    
    -- Calcular duração
    v_duration := EXTRACT(EPOCH FROM (NOW() - v_started_at));
    
    -- Atualizar job
    UPDATE etl_jobs SET
        status = p_status,
        completed_at = NOW(),
        duration_seconds = v_duration,
        output_summary = p_output_summary,
        error_message = p_error_message,
        error_details = p_error_details,
        api_requests_made = p_api_requests,
        records_processed = p_records_processed,
        records_inserted = p_records_inserted,
        records_updated = p_records_updated,
        records_failed = p_records_failed
    WHERE id = p_job_id;
    
    -- Desativar checkpoints do job
    UPDATE etl_checkpoints SET is_active = false WHERE job_id = p_job_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Função para criar checkpoint
CREATE OR REPLACE FUNCTION create_etl_checkpoint(
    p_job_id UUID,
    p_checkpoint_name VARCHAR(255),
    p_checkpoint_type VARCHAR(100),
    p_checkpoint_data JSONB,
    p_progress_percentage DECIMAL DEFAULT 0.00,
    p_items_processed INTEGER DEFAULT 0,
    p_items_total INTEGER DEFAULT NULL,
    p_current_step VARCHAR(255) DEFAULT NULL,
    p_next_step VARCHAR(255) DEFAULT NULL,
    p_execution_context JSONB DEFAULT NULL,
    p_expires_in_hours INTEGER DEFAULT 24
) RETURNS UUID AS $$
DECLARE
    v_checkpoint_id UUID;
BEGIN
    -- Desativar checkpoint anterior com mesmo nome
    UPDATE etl_checkpoints SET is_active = false 
    WHERE job_id = p_job_id AND checkpoint_name = p_checkpoint_name AND is_active = true;
    
    -- Criar novo checkpoint
    INSERT INTO etl_checkpoints (
        job_id, checkpoint_name, checkpoint_type, checkpoint_data,
        progress_percentage, items_processed, items_total,
        current_step, next_step, execution_context,
        expires_at
    ) VALUES (
        p_job_id, p_checkpoint_name, p_checkpoint_type, p_checkpoint_data,
        p_progress_percentage, p_items_processed, p_items_total,
        p_current_step, p_next_step, p_execution_context,
        NOW() + (p_expires_in_hours || ' hours')::INTERVAL
    ) RETURNING id INTO v_checkpoint_id;
    
    RETURN v_checkpoint_id;
END;
$$ LANGUAGE plpgsql;

-- Função para log de job
CREATE OR REPLACE FUNCTION log_etl_job(
    p_job_id UUID,
    p_level VARCHAR(20),
    p_message TEXT,
    p_details JSONB DEFAULT NULL,
    p_component VARCHAR(100) DEFAULT NULL,
    p_function_name VARCHAR(100) DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO etl_job_logs (
        job_id, log_level, message, details, component, function_name
    ) VALUES (
        p_job_id, p_level, p_message, p_details, p_component, p_function_name
    ) RETURNING id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;

-- Função para obter estatísticas de jobs
CREATE OR REPLACE FUNCTION get_etl_job_stats()
RETURNS TABLE (
    total_jobs BIGINT,
    completed_jobs BIGINT,
    failed_jobs BIGINT,
    running_jobs BIGINT,
    avg_duration_minutes NUMERIC,
    total_api_requests BIGINT,
    total_records_processed BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_jobs,
        COUNT(*) FILTER (WHERE status = 'completed') as completed_jobs,
        COUNT(*) FILTER (WHERE status = 'failed') as failed_jobs,
        COUNT(*) FILTER (WHERE status = 'running') as running_jobs,
        ROUND(AVG(duration_seconds) / 60.0, 2) as avg_duration_minutes,
        COALESCE(SUM(api_requests_made), 0) as total_api_requests,
        COALESCE(SUM(records_processed), 0) as total_records_processed
    FROM etl_jobs;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Comentários para Documentação
-- =====================================================

COMMENT ON TABLE etl_jobs IS 'Tabela principal para controle de execução de jobs ETL';
COMMENT ON COLUMN etl_jobs.job_name IS 'Nome único do job ETL';
COMMENT ON COLUMN etl_jobs.job_type IS 'Categoria do job: setup, base_data, leagues_seasons, fixtures_events, quality_checks';
COMMENT ON COLUMN etl_jobs.status IS 'Status atual: pending, running, completed, failed, cancelled';
COMMENT ON COLUMN etl_jobs.depends_on_jobs IS 'Array de UUIDs de jobs que devem completar primeiro';

COMMENT ON TABLE etl_checkpoints IS 'Checkpoints para retomada de jobs ETL interrompidos';
COMMENT ON COLUMN etl_checkpoints.checkpoint_data IS 'Dados JSON necessários para retomar execução';
COMMENT ON COLUMN etl_checkpoints.execution_context IS 'Contexto de execução (variáveis, estado)';

COMMENT ON TABLE etl_job_logs IS 'Logs detalhados de execução dos jobs ETL';
COMMENT ON COLUMN etl_job_logs.log_level IS 'Nível do log: DEBUG, INFO, WARNING, ERROR, CRITICAL';

COMMENT ON FUNCTION start_etl_job IS 'Inicia um novo job ETL e retorna o UUID';
COMMENT ON FUNCTION complete_etl_job IS 'Finaliza um job ETL com status e estatísticas';
COMMENT ON FUNCTION create_etl_checkpoint IS 'Cria um checkpoint para retomada de job';
COMMENT ON FUNCTION log_etl_job IS 'Registra log de execução de job ETL';
COMMENT ON FUNCTION get_etl_job_stats IS 'Retorna estatísticas gerais dos jobs ETL';
