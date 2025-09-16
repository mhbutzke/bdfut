-- ================================================================
-- MIGRAÇÃO: IMPLEMENTAR SISTEMA COMPLETO DE AUDITORIA
-- ================================================================
-- Responsável: Security Specialist 🔐
-- Task: SEC-003 - Implementar Logs de Auditoria
-- Data: 15 de Setembro de 2025
-- Objetivo: Implementar sistema completo de auditoria para rastreabilidade
-- Status: CRÍTICO - Implementar auditoria após RLS
-- ================================================================

-- ESTRATÉGIA DE AUDITORIA:
-- 1. Habilitar pgaudit para auditoria avançada
-- 2. Configurar auditoria por categorias (READ, WRITE, DDL, ROLE)
-- 3. Criar tabela personalizada para logs de auditoria
-- 4. Implementar triggers para auditoria customizada
-- 5. Configurar retenção e limpeza automática de logs
-- 6. Monitoramento de atividades suspeitas

BEGIN;

-- ================================================================
-- 1. HABILITAR EXTENSÃO PGAUDIT
-- ================================================================

-- Habilitar pgaudit para auditoria avançada
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- Verificar se pgaudit foi habilitado
SELECT extname, extversion FROM pg_extension WHERE extname = 'pgaudit';

-- ================================================================
-- 2. CONFIGURAR AUDITORIA GLOBAL
-- ================================================================

-- Configurar auditoria para role postgres (global)
-- Auditar: WRITE (INSERT, UPDATE, DELETE), DDL (CREATE, ALTER, DROP), ROLE (user management)
ALTER ROLE postgres SET pgaudit.log TO 'write, ddl, role';

-- Configurar auditoria para roles da API (service_role, authenticator)
ALTER ROLE authenticator SET pgaudit.log TO 'write, ddl';
-- ALTER ROLE service_role SET pgaudit.log TO 'write, ddl, role'; -- Se existir

-- Configurar nível de log (info para capturar mais detalhes)
ALTER ROLE postgres SET pgaudit.log_level TO 'info';

-- ================================================================
-- 3. CRIAR SCHEMA DE AUDITORIA CUSTOMIZADA
-- ================================================================

-- Criar schema dedicado para auditoria
CREATE SCHEMA IF NOT EXISTS audit;

-- Comentário no schema
COMMENT ON SCHEMA audit IS 'Schema dedicado para sistema de auditoria e logs de segurança';

-- ================================================================
-- 4. TABELA DE LOGS DE AUDITORIA CUSTOMIZADA
-- ================================================================

-- Tabela principal de auditoria
CREATE TABLE audit.activity_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Informações da sessão
    session_id TEXT,
    user_id TEXT,
    user_role TEXT,
    client_ip INET,
    user_agent TEXT,
    
    -- Informações da operação
    operation_type VARCHAR(20) NOT NULL, -- SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, etc.
    table_schema VARCHAR(63),
    table_name VARCHAR(63),
    object_name TEXT, -- nome completo do objeto afetado
    
    -- Detalhes da query
    statement_text TEXT,
    statement_id BIGINT,
    
    -- Dados da operação
    old_values JSONB, -- valores antes da mudança
    new_values JSONB, -- valores após a mudança
    changed_fields TEXT[], -- campos que foram alterados
    
    -- Contexto adicional
    application_name TEXT,
    database_name TEXT,
    
    -- Metadados de segurança
    severity VARCHAR(20) DEFAULT 'INFO', -- INFO, WARNING, CRITICAL
    tags TEXT[], -- tags para categorização
    
    -- Índices para performance
    CONSTRAINT chk_operation_type CHECK (
        operation_type IN ('SELECT', 'INSERT', 'UPDATE', 'DELETE', 
                          'CREATE', 'ALTER', 'DROP', 'GRANT', 'REVOKE',
                          'TRUNCATE', 'COPY', 'LOGIN', 'LOGOUT')
    ),
    CONSTRAINT chk_severity CHECK (
        severity IN ('INFO', 'WARNING', 'CRITICAL')
    )
);

-- Comentários na tabela
COMMENT ON TABLE audit.activity_log IS 'Log detalhado de todas as atividades auditadas no sistema';
COMMENT ON COLUMN audit.activity_log.operation_type IS 'Tipo de operação executada';
COMMENT ON COLUMN audit.activity_log.old_values IS 'Valores antes da alteração (UPDATE/DELETE)';
COMMENT ON COLUMN audit.activity_log.new_values IS 'Valores após a alteração (INSERT/UPDATE)';
COMMENT ON COLUMN audit.activity_log.severity IS 'Nível de criticidade da operação';

-- ================================================================
-- 5. ÍNDICES PARA PERFORMANCE
-- ================================================================

-- Índice principal por timestamp (particionamento futuro)
CREATE INDEX idx_activity_log_timestamp ON audit.activity_log (timestamp DESC);

-- Índice por usuário e role
CREATE INDEX idx_activity_log_user ON audit.activity_log (user_id, user_role);

-- Índice por operação e tabela
CREATE INDEX idx_activity_log_operation ON audit.activity_log (operation_type, table_schema, table_name);

-- Índice por IP para detectar atividades suspeitas
CREATE INDEX idx_activity_log_ip ON audit.activity_log (client_ip);

-- Índice por severidade para alertas
CREATE INDEX idx_activity_log_severity ON audit.activity_log (severity, timestamp DESC);

-- Índice composto para queries frequentes
CREATE INDEX idx_activity_log_composite ON audit.activity_log (timestamp DESC, user_id, operation_type);

-- ================================================================
-- 6. TABELA DE SESSÕES AUDITADAS
-- ================================================================

CREATE TABLE audit.user_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    user_id TEXT,
    user_role TEXT,
    
    -- Informações de conexão
    login_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    logout_time TIMESTAMPTZ,
    client_ip INET,
    user_agent TEXT,
    
    -- Estatísticas da sessão
    queries_executed INTEGER DEFAULT 0,
    tables_accessed TEXT[],
    operations_performed TEXT[],
    
    -- Status da sessão
    session_status VARCHAR(20) DEFAULT 'ACTIVE',
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT chk_session_status CHECK (
        session_status IN ('ACTIVE', 'ENDED', 'TERMINATED')
    )
);

COMMENT ON TABLE audit.user_sessions IS 'Rastreamento de sessões de usuários para auditoria';

-- Índices para sessões
CREATE INDEX idx_user_sessions_user ON audit.user_sessions (user_id, login_time DESC);
CREATE INDEX idx_user_sessions_ip ON audit.user_sessions (client_ip);
CREATE INDEX idx_user_sessions_status ON audit.user_sessions (session_status, last_activity);

-- ================================================================
-- 7. TABELA DE ALERTAS DE SEGURANÇA
-- ================================================================

CREATE TABLE audit.security_alerts (
    id BIGSERIAL PRIMARY KEY,
    alert_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Tipo de alerta
    alert_type VARCHAR(50) NOT NULL,
    alert_level VARCHAR(20) NOT NULL DEFAULT 'WARNING',
    
    -- Contexto do alerta
    user_id TEXT,
    client_ip INET,
    description TEXT NOT NULL,
    details JSONB,
    
    -- Ações tomadas
    action_taken TEXT,
    resolved_at TIMESTAMPTZ,
    resolved_by TEXT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'OPEN',
    
    CONSTRAINT chk_alert_level CHECK (
        alert_level IN ('INFO', 'WARNING', 'CRITICAL', 'EMERGENCY')
    ),
    CONSTRAINT chk_alert_status CHECK (
        status IN ('OPEN', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE')
    )
);

COMMENT ON TABLE audit.security_alerts IS 'Alertas de segurança gerados automaticamente';

-- Índices para alertas
CREATE INDEX idx_security_alerts_level ON audit.security_alerts (alert_level, alert_time DESC);
CREATE INDEX idx_security_alerts_status ON audit.security_alerts (status, alert_time DESC);
CREATE INDEX idx_security_alerts_type ON audit.security_alerts (alert_type);

-- ================================================================
-- 8. FUNÇÕES DE AUDITORIA CUSTOMIZADA
-- ================================================================

-- Função para registrar atividade personalizada
CREATE OR REPLACE FUNCTION audit.log_activity(
    p_operation_type TEXT,
    p_table_schema TEXT DEFAULT NULL,
    p_table_name TEXT DEFAULT NULL,
    p_object_name TEXT DEFAULT NULL,
    p_statement_text TEXT DEFAULT NULL,
    p_old_values JSONB DEFAULT NULL,
    p_new_values JSONB DEFAULT NULL,
    p_severity TEXT DEFAULT 'INFO',
    p_tags TEXT[] DEFAULT NULL
) RETURNS BIGINT AS $$
DECLARE
    v_activity_id BIGINT;
    v_session_id TEXT;
    v_user_id TEXT;
    v_user_role TEXT;
    v_client_ip INET;
    v_user_agent TEXT;
    v_app_name TEXT;
    v_db_name TEXT;
BEGIN
    -- Capturar informações da sessão atual
    v_session_id := COALESCE(current_setting('audit.session_id', true), 'system');
    v_user_id := COALESCE(current_setting('audit.user_id', true), current_user);
    v_user_role := current_user;
    v_client_ip := COALESCE(current_setting('audit.client_ip', true)::INET, '127.0.0.1'::INET);
    v_user_agent := current_setting('audit.user_agent', true);
    v_app_name := current_setting('application_name', true);
    v_db_name := current_database();
    
    -- Inserir log de atividade
    INSERT INTO audit.activity_log (
        session_id, user_id, user_role, client_ip, user_agent,
        operation_type, table_schema, table_name, object_name,
        statement_text, old_values, new_values, 
        application_name, database_name, severity, tags
    ) VALUES (
        v_session_id, v_user_id, v_user_role, v_client_ip, v_user_agent,
        p_operation_type, p_table_schema, p_table_name, p_object_name,
        p_statement_text, p_old_values, p_new_values,
        v_app_name, v_db_name, p_severity, p_tags
    ) RETURNING id INTO v_activity_id;
    
    RETURN v_activity_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION audit.log_activity IS 'Função para registrar atividades customizadas no log de auditoria';

-- ================================================================
-- 9. FUNÇÃO PARA CRIAR ALERTAS DE SEGURANÇA
-- ================================================================

CREATE OR REPLACE FUNCTION audit.create_security_alert(
    p_alert_type TEXT,
    p_alert_level TEXT,
    p_description TEXT,
    p_user_id TEXT DEFAULT NULL,
    p_client_ip INET DEFAULT NULL,
    p_details JSONB DEFAULT NULL
) RETURNS BIGINT AS $$
DECLARE
    v_alert_id BIGINT;
BEGIN
    INSERT INTO audit.security_alerts (
        alert_type, alert_level, description, user_id, client_ip, details
    ) VALUES (
        p_alert_type, p_alert_level, p_description, p_user_id, p_client_ip, p_details
    ) RETURNING id INTO v_alert_id;
    
    -- Log da criação do alerta
    PERFORM audit.log_activity(
        'CREATE', 'audit', 'security_alerts', 'alert_' || v_alert_id,
        'Security alert created: ' || p_alert_type,
        NULL, jsonb_build_object('alert_id', v_alert_id, 'level', p_alert_level),
        'WARNING', ARRAY['security', 'alert']
    );
    
    RETURN v_alert_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION audit.create_security_alert IS 'Função para criar alertas de segurança automatizados';

-- ================================================================
-- 10. TRIGGERS PARA AUDITORIA AUTOMÁTICA
-- ================================================================

-- Função de trigger genérica para auditoria
CREATE OR REPLACE FUNCTION audit.audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    v_old_values JSONB;
    v_new_values JSONB;
    v_changed_fields TEXT[];
    v_operation TEXT;
BEGIN
    -- Determinar tipo de operação
    v_operation := TG_OP;
    
    -- Capturar valores antigos e novos
    IF TG_OP = 'DELETE' THEN
        v_old_values := to_jsonb(OLD);
        v_new_values := NULL;
    ELSIF TG_OP = 'INSERT' THEN
        v_old_values := NULL;
        v_new_values := to_jsonb(NEW);
    ELSIF TG_OP = 'UPDATE' THEN
        v_old_values := to_jsonb(OLD);
        v_new_values := to_jsonb(NEW);
        
        -- Identificar campos alterados
        SELECT array_agg(key) INTO v_changed_fields
        FROM jsonb_each(v_old_values) o
        JOIN jsonb_each(v_new_values) n ON o.key = n.key
        WHERE o.value IS DISTINCT FROM n.value;
    END IF;
    
    -- Registrar atividade
    PERFORM audit.log_activity(
        v_operation,
        TG_TABLE_SCHEMA,
        TG_TABLE_NAME,
        TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
        NULL, -- statement será capturado pelo pgaudit
        v_old_values,
        v_new_values,
        'INFO',
        ARRAY['auto-audit', TG_TABLE_NAME]
    );
    
    -- Retornar registro apropriado
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION audit.audit_trigger_function IS 'Função de trigger genérica para auditoria automática de tabelas';

-- ================================================================
-- 11. APLICAR TRIGGERS NAS TABELAS PRINCIPAIS
-- ================================================================

-- Trigger para tabela de usuários (se existir tabela auth.users)
-- CREATE TRIGGER audit_auth_users
--     AFTER INSERT OR UPDATE OR DELETE ON auth.users
--     FOR EACH ROW EXECUTE FUNCTION audit.audit_trigger_function();

-- Triggers para tabelas principais do sistema (dados esportivos geralmente não precisam de auditoria detalhada)
-- Mas vamos auditar mudanças estruturais importantes

-- Exemplo: auditar mudanças na tabela de ligas (se for crítica)
CREATE TRIGGER audit_leagues
    AFTER INSERT OR UPDATE OR DELETE ON public.leagues
    FOR EACH ROW EXECUTE FUNCTION audit.audit_trigger_function();

-- ================================================================
-- 12. FUNÇÕES DE CONSULTA E RELATÓRIOS
-- ================================================================

-- Função para buscar atividades por usuário
CREATE OR REPLACE FUNCTION audit.get_user_activity(
    p_user_id TEXT,
    p_start_date TIMESTAMPTZ DEFAULT NOW() - INTERVAL '30 days',
    p_end_date TIMESTAMPTZ DEFAULT NOW()
) RETURNS TABLE (
    timestamp TIMESTAMPTZ,
    operation_type VARCHAR(20),
    table_name VARCHAR(63),
    object_name TEXT,
    severity VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        al.timestamp,
        al.operation_type,
        al.table_name,
        al.object_name,
        al.severity
    FROM audit.activity_log al
    WHERE al.user_id = p_user_id
      AND al.timestamp BETWEEN p_start_date AND p_end_date
    ORDER BY al.timestamp DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para detectar atividades suspeitas
CREATE OR REPLACE FUNCTION audit.detect_suspicious_activity()
RETURNS TABLE (
    alert_type TEXT,
    user_id TEXT,
    client_ip INET,
    activity_count BIGINT,
    last_activity TIMESTAMPTZ
) AS $$
BEGIN
    -- Detectar múltiplos logins falhados
    RETURN QUERY
    SELECT 
        'MULTIPLE_FAILED_LOGINS'::TEXT,
        al.user_id,
        al.client_ip,
        COUNT(*) as activity_count,
        MAX(al.timestamp) as last_activity
    FROM audit.activity_log al
    WHERE al.operation_type = 'LOGIN'
      AND al.severity = 'WARNING'
      AND al.timestamp > NOW() - INTERVAL '1 hour'
    GROUP BY al.user_id, al.client_ip
    HAVING COUNT(*) > 5;
    
    -- Detectar atividade fora do horário
    RETURN QUERY
    SELECT 
        'OFF_HOURS_ACTIVITY'::TEXT,
        al.user_id,
        al.client_ip,
        COUNT(*) as activity_count,
        MAX(al.timestamp) as last_activity
    FROM audit.activity_log al
    WHERE al.timestamp > NOW() - INTERVAL '24 hours'
      AND (EXTRACT(hour FROM al.timestamp) < 6 OR EXTRACT(hour FROM al.timestamp) > 22)
      AND al.operation_type IN ('DELETE', 'DROP', 'ALTER')
    GROUP BY al.user_id, al.client_ip
    HAVING COUNT(*) > 3;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================================
-- 13. CONFIGURAR LIMPEZA AUTOMÁTICA DE LOGS
-- ================================================================

-- Função para limpeza automática de logs antigos
CREATE OR REPLACE FUNCTION audit.cleanup_old_logs(
    p_retention_days INTEGER DEFAULT 90
) RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    -- Deletar logs antigos
    DELETE FROM audit.activity_log 
    WHERE timestamp < NOW() - (p_retention_days || ' days')::INTERVAL;
    
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    
    -- Log da limpeza
    PERFORM audit.log_activity(
        'DELETE', 'audit', 'activity_log', 'cleanup_operation',
        'Automated cleanup of old audit logs',
        NULL, 
        jsonb_build_object('deleted_count', v_deleted_count, 'retention_days', p_retention_days),
        'INFO',
        ARRAY['maintenance', 'cleanup']
    );
    
    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================================
-- 14. VIEWS PARA RELATÓRIOS
-- ================================================================

-- View para atividades recentes
CREATE VIEW audit.recent_activity AS
SELECT 
    timestamp,
    user_id,
    user_role,
    operation_type,
    table_schema,
    table_name,
    object_name,
    severity,
    client_ip
FROM audit.activity_log
WHERE timestamp > NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;

COMMENT ON VIEW audit.recent_activity IS 'View das atividades dos últimos 7 dias';

-- View para estatísticas de auditoria
CREATE VIEW audit.audit_statistics AS
SELECT 
    DATE(timestamp) as audit_date,
    operation_type,
    COUNT(*) as operation_count,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT client_ip) as unique_ips
FROM audit.activity_log
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY DATE(timestamp), operation_type
ORDER BY audit_date DESC, operation_count DESC;

COMMENT ON VIEW audit.audit_statistics IS 'Estatísticas diárias de auditoria dos últimos 30 dias';

-- ================================================================
-- 15. CONFIGURAR PERMISSÕES DE SEGURANÇA
-- ================================================================

-- Revogar acesso público ao schema de auditoria
REVOKE ALL ON SCHEMA audit FROM PUBLIC;

-- Conceder acesso apenas a roles específicos
GRANT USAGE ON SCHEMA audit TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA audit TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA audit TO postgres;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA audit TO postgres;

-- Permitir que service_role possa inserir logs (para aplicações)
-- GRANT INSERT ON audit.activity_log TO service_role;
-- GRANT EXECUTE ON FUNCTION audit.log_activity TO service_role;

-- ================================================================
-- 16. HABILITAR RLS NO SCHEMA DE AUDITORIA
-- ================================================================

-- Habilitar RLS nas tabelas de auditoria
ALTER TABLE audit.activity_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit.user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit.security_alerts ENABLE ROW LEVEL SECURITY;

-- Políticas para activity_log
CREATE POLICY "audit_activity_log_select" ON audit.activity_log
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "audit_activity_log_insert" ON audit.activity_log
    FOR INSERT WITH CHECK (auth.role() = 'service_role' OR current_user = 'postgres');

-- Políticas similares para outras tabelas
CREATE POLICY "audit_user_sessions_select" ON audit.user_sessions
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "audit_security_alerts_select" ON audit.security_alerts
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

-- ================================================================
-- 17. REGISTRAR APLICAÇÃO DA MIGRAÇÃO
-- ================================================================

-- Registrar na tabela de cache que a auditoria foi implementada
INSERT INTO public.api_cache (cache_key, data, expires_at, created_at)
VALUES (
    'audit_system_20250915',
    jsonb_build_object(
        'migration', 'implement_audit_logging',
        'components_installed', jsonb_build_array(
            'pgaudit_extension',
            'audit_schema',
            'activity_log_table',
            'user_sessions_table',
            'security_alerts_table',
            'audit_functions',
            'audit_triggers',
            'audit_views',
            'rls_policies'
        ),
        'tables_created', 3,
        'functions_created', 5,
        'triggers_created', 1,
        'views_created', 2,
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

-- Para verificar se pgaudit está funcionando:
-- SELECT * FROM pg_extension WHERE extname = 'pgaudit';

-- Para verificar configurações de auditoria:
-- SELECT rolname, rolconfig FROM pg_roles WHERE rolconfig IS NOT NULL;

-- Para testar o sistema de auditoria:
-- SELECT audit.log_activity('TEST', 'public', 'test_table', 'test_operation');

-- Para ver logs recentes:
-- SELECT * FROM audit.recent_activity LIMIT 10;

-- Para detectar atividades suspeitas:
-- SELECT * FROM audit.detect_suspicious_activity();

-- ================================================================
-- FIM DA MIGRAÇÃO
-- ================================================================
