-- ================================================================
-- MIGRAÇÃO: IMPLEMENTAR MONITORAMENTO DE SEGURANÇA
-- ================================================================
-- Responsável: Security Specialist 🔐
-- Task: SEC-006 - Configurar Monitoramento de Segurança
-- Data: 15 de Setembro de 2025
-- Objetivo: Implementar monitoramento proativo de segurança
-- Status: CRÍTICO - Detecção de ameaças e resposta a incidentes
-- ================================================================

-- ESTRATÉGIA DE MONITORAMENTO DE SEGURANÇA:
-- 1. Sistema de alertas de segurança
-- 2. Detecção de anomalias
-- 3. Dashboard de segurança
-- 4. Procedimentos de resposta a incidentes
-- 5. Testes de alertas
-- 6. Integração com compliance (SEC-005), auditoria (SEC-003) e criptografia (SEC-004)

BEGIN;

-- ================================================================
-- 1. CRIAR SCHEMA PARA MONITORAMENTO DE SEGURANÇA
-- ================================================================

-- Criar schema dedicado para monitoramento de segurança
CREATE SCHEMA IF NOT EXISTS security_monitoring;

-- Comentário no schema
COMMENT ON SCHEMA security_monitoring IS 'Schema dedicado para monitoramento proativo de segurança';

-- ================================================================
-- 2. SISTEMA DE ALERTAS DE SEGURANÇA
-- ================================================================

-- Tabela para configuração de alertas
CREATE TABLE security_monitoring.security_alerts_config (
    id SERIAL PRIMARY KEY,
    alert_name VARCHAR NOT NULL UNIQUE,
    alert_type VARCHAR NOT NULL, -- threshold, anomaly, pattern, compliance
    severity_level VARCHAR NOT NULL, -- low, medium, high, critical
    description TEXT NOT NULL,
    query_template TEXT NOT NULL, -- Template SQL para detecção
    threshold_value NUMERIC, -- Valor limite para alertas de threshold
    threshold_operator VARCHAR, -- >, <, =, >=, <=, !=
    check_interval_minutes INTEGER DEFAULT 5, -- Intervalo de verificação
    is_active BOOLEAN DEFAULT true,
    notification_channels TEXT[], -- email, slack, webhook, etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_severity_level CHECK (severity_level IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT chk_alert_type CHECK (alert_type IN ('threshold', 'anomaly', 'pattern', 'compliance')),
    CONSTRAINT chk_threshold_operator CHECK (threshold_operator IN ('>', '<', '=', '>=', '<=', '!='))
);

COMMENT ON TABLE security_monitoring.security_alerts_config IS 'Configuração de alertas de segurança';

-- Índices para performance
CREATE INDEX idx_security_alerts_config_type ON security_monitoring.security_alerts_config (alert_type);
CREATE INDEX idx_security_alerts_config_severity ON security_monitoring.security_alerts_config (severity_level);
CREATE INDEX idx_security_alerts_config_active ON security_monitoring.security_alerts_config (is_active);

-- Tabela para histórico de alertas
CREATE TABLE security_monitoring.security_alerts_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_config_id INTEGER REFERENCES security_monitoring.security_alerts_config(id),
    alert_name VARCHAR NOT NULL,
    alert_type VARCHAR NOT NULL,
    severity_level VARCHAR NOT NULL,
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    status VARCHAR NOT NULL DEFAULT 'active', -- active, resolved, acknowledged, false_positive
    alert_data JSONB, -- Dados específicos do alerta
    affected_resources TEXT[], -- Recursos afetados
    impact_assessment TEXT, -- Avaliação de impacto
    remediation_steps TEXT[], -- Passos de remediação
    assigned_to VARCHAR, -- Responsável pela resolução
    resolution_notes TEXT, -- Notas de resolução
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_alert_status CHECK (status IN ('active', 'resolved', 'acknowledged', 'false_positive'))
);

COMMENT ON TABLE security_monitoring.security_alerts_history IS 'Histórico de alertas de segurança';

-- Índices para performance
CREATE INDEX idx_security_alerts_history_config ON security_monitoring.security_alerts_history (alert_config_id);
CREATE INDEX idx_security_alerts_history_name ON security_monitoring.security_alerts_history (alert_name);
CREATE INDEX idx_security_alerts_history_status ON security_monitoring.security_alerts_history (status);
CREATE INDEX idx_security_alerts_history_triggered ON security_monitoring.security_alerts_history (triggered_at);
CREATE INDEX idx_security_alerts_history_severity ON security_monitoring.security_alerts_history (severity_level);

-- ================================================================
-- 3. DETECÇÃO DE ANOMALIAS
-- ================================================================

-- Tabela para baseline de comportamento normal
CREATE TABLE security_monitoring.behavior_baseline (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR NOT NULL,
    resource_type VARCHAR NOT NULL, -- user, ip, endpoint, table, etc.
    resource_id VARCHAR NOT NULL,
    time_window VARCHAR NOT NULL, -- hourly, daily, weekly
    baseline_value NUMERIC NOT NULL,
    standard_deviation NUMERIC NOT NULL,
    sample_size INTEGER NOT NULL,
    confidence_level NUMERIC NOT NULL, -- 0.95, 0.99, etc.
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_time_window CHECK (time_window IN ('hourly', 'daily', 'weekly', 'monthly')),
    CONSTRAINT chk_confidence_level CHECK (confidence_level > 0 AND confidence_level < 1)
);

COMMENT ON TABLE security_monitoring.behavior_baseline IS 'Baseline de comportamento normal para detecção de anomalias';

-- Índices para performance
CREATE INDEX idx_behavior_baseline_metric ON security_monitoring.behavior_baseline (metric_name);
CREATE INDEX idx_behavior_baseline_resource ON security_monitoring.behavior_baseline (resource_type, resource_id);
CREATE INDEX idx_behavior_baseline_time ON security_monitoring.behavior_baseline (time_window);

-- Tabela para métricas de segurança em tempo real
CREATE TABLE security_monitoring.security_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR NOT NULL,
    metric_type VARCHAR NOT NULL, -- counter, gauge, histogram, summary
    resource_type VARCHAR NOT NULL,
    resource_id VARCHAR NOT NULL,
    metric_value NUMERIC NOT NULL,
    metric_labels JSONB, -- Labels adicionais
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_metric_type CHECK (metric_type IN ('counter', 'gauge', 'histogram', 'summary'))
);

COMMENT ON TABLE security_monitoring.security_metrics IS 'Métricas de segurança em tempo real';

-- Índices para performance
CREATE INDEX idx_security_metrics_name ON security_monitoring.security_metrics (metric_name);
CREATE INDEX idx_security_metrics_resource ON security_monitoring.security_metrics (resource_type, resource_id);
CREATE INDEX idx_security_metrics_timestamp ON security_monitoring.security_metrics (timestamp);

-- ================================================================
-- 4. DASHBOARD DE SEGURANÇA
-- ================================================================

-- Tabela para configuração de dashboards
CREATE TABLE security_monitoring.security_dashboards (
    id SERIAL PRIMARY KEY,
    dashboard_name VARCHAR NOT NULL UNIQUE,
    dashboard_type VARCHAR NOT NULL, -- overview, compliance, incidents, metrics
    description TEXT,
    layout_config JSONB NOT NULL, -- Configuração do layout
    refresh_interval_seconds INTEGER DEFAULT 30,
    is_public BOOLEAN DEFAULT false,
    created_by VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_dashboard_type CHECK (dashboard_type IN ('overview', 'compliance', 'incidents', 'metrics'))
);

COMMENT ON TABLE security_monitoring.security_dashboards IS 'Configuração de dashboards de segurança';

-- Tabela para widgets do dashboard
CREATE TABLE security_monitoring.dashboard_widgets (
    id SERIAL PRIMARY KEY,
    dashboard_id INTEGER REFERENCES security_monitoring.security_dashboards(id),
    widget_name VARCHAR NOT NULL,
    widget_type VARCHAR NOT NULL, -- chart, table, metric, alert
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    config JSONB NOT NULL, -- Configuração específica do widget
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_widget_type CHECK (widget_type IN ('chart', 'table', 'metric', 'alert'))
);

COMMENT ON TABLE security_monitoring.dashboard_widgets IS 'Widgets dos dashboards de segurança';

-- ================================================================
-- 5. PROCEDIMENTOS DE RESPOSTA A INCIDENTES
-- ================================================================

-- Tabela para procedimentos de resposta
CREATE TABLE security_monitoring.incident_response_procedures (
    id SERIAL PRIMARY KEY,
    procedure_name VARCHAR NOT NULL UNIQUE,
    incident_type VARCHAR NOT NULL, -- data_breach, unauthorized_access, ddos, malware, etc.
    severity_level VARCHAR NOT NULL,
    description TEXT NOT NULL,
    response_steps JSONB NOT NULL, -- Passos estruturados de resposta
    escalation_matrix JSONB NOT NULL, -- Matriz de escalação
    communication_template TEXT, -- Template de comunicação
    recovery_procedures JSONB, -- Procedimentos de recuperação
    lessons_learned TEXT, -- Lições aprendidas
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_incident_type CHECK (incident_type IN ('data_breach', 'unauthorized_access', 'ddos', 'malware', 'insider_threat', 'phishing', 'system_compromise')),
    CONSTRAINT chk_procedure_severity CHECK (severity_level IN ('low', 'medium', 'high', 'critical'))
);

COMMENT ON TABLE security_monitoring.incident_response_procedures IS 'Procedimentos de resposta a incidentes de segurança';

-- Tabela para registro de incidentes
CREATE TABLE security_monitoring.security_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id VARCHAR NOT NULL UNIQUE, -- ID legível do incidente
    incident_type VARCHAR NOT NULL,
    severity_level VARCHAR NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'open', -- open, investigating, contained, resolved, closed
    title VARCHAR NOT NULL,
    description TEXT NOT NULL,
    affected_systems TEXT[],
    affected_users INTEGER,
    data_compromised BOOLEAN DEFAULT false,
    data_types TEXT[], -- Tipos de dados comprometidos
    initial_detection TIMESTAMPTZ NOT NULL,
    containment_time TIMESTAMPTZ,
    resolution_time TIMESTAMPTZ,
    root_cause TEXT,
    impact_assessment TEXT,
    remediation_steps TEXT[],
    lessons_learned TEXT,
    assigned_to VARCHAR,
    incident_commander VARCHAR,
    communication_log JSONB, -- Log de comunicações
    evidence_collection JSONB, -- Coleta de evidências
    regulatory_notification BOOLEAN DEFAULT false,
    customer_notification BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_incident_status CHECK (status IN ('open', 'investigating', 'contained', 'resolved', 'closed'))
);

COMMENT ON TABLE security_monitoring.security_incidents IS 'Registro de incidentes de segurança';

-- Índices para performance
CREATE INDEX idx_security_incidents_type ON security_monitoring.security_incidents (incident_type);
CREATE INDEX idx_security_incidents_severity ON security_monitoring.security_incidents (severity_level);
CREATE INDEX idx_security_incidents_status ON security_monitoring.security_incidents (status);
CREATE INDEX idx_security_incidents_detection ON security_monitoring.security_incidents (initial_detection);

-- ================================================================
-- 6. FUNÇÕES DE MONITORAMENTO
-- ================================================================

-- Função para criar alertas padrão de segurança
CREATE OR REPLACE FUNCTION security_monitoring.create_default_security_alerts()
RETURNS INTEGER AS $$
DECLARE
    v_alerts_count INTEGER := 0;
BEGIN
    -- Alertas de threshold
    INSERT INTO security_monitoring.security_alerts_config (
        alert_name, alert_type, severity_level, description, query_template,
        threshold_value, threshold_operator, check_interval_minutes, notification_channels
    ) VALUES
    -- Alertas de conexões
    ('high_database_connections', 'threshold', 'high', 'Alto número de conexões simultâneas',
     'SELECT COUNT(*) FROM pg_stat_activity WHERE state = ''active''', 80, '>', 5, ARRAY['email', 'slack']),
    
    -- Alertas de tentativas de login
    ('failed_login_attempts', 'threshold', 'medium', 'Muitas tentativas de login falhadas',
     'SELECT COUNT(*) FROM auth.audit_log_entries WHERE action = ''login'' AND created_at > NOW() - INTERVAL ''1 hour''', 10, '>', 5, ARRAY['email']),
    
    -- Alertas de acesso não autorizado
    ('unauthorized_access_attempts', 'threshold', 'critical', 'Tentativas de acesso não autorizado',
     'SELECT COUNT(*) FROM audit.activity_log WHERE action_type = ''SELECT'' AND user_email IS NULL AND event_time > NOW() - INTERVAL ''1 hour''', 5, '>', 1, ARRAY['email', 'slack', 'webhook']),
    
    -- Alertas de modificação de dados
    ('suspicious_data_modifications', 'threshold', 'high', 'Modificações suspeitas de dados',
     'SELECT COUNT(*) FROM audit.activity_log WHERE action_type IN (''UPDATE'', ''DELETE'') AND event_time > NOW() - INTERVAL ''1 hour''', 50, '>', 5, ARRAY['email', 'slack']),
    
    -- Alertas de compliance
    ('low_compliance_score', 'threshold', 'critical', 'Score de compliance LGPD baixo',
     'SELECT lgpd.calculate_compliance_score()', 70, '<', 60, ARRAY['email', 'slack']),
    
    -- Alertas de criptografia
    ('unencrypted_personal_data', 'pattern', 'critical', 'Dados pessoais não criptografados detectados',
     'SELECT COUNT(*) FROM lgpd.personal_data_mapping WHERE is_encrypted = false', 0, '>', 60, ARRAY['email', 'slack']);
    
    GET DIAGNOSTICS v_alerts_count = ROW_COUNT;
    
    RETURN v_alerts_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION security_monitoring.create_default_security_alerts IS 'Cria alertas padrão de segurança';

-- Função para verificar alertas ativos
CREATE OR REPLACE FUNCTION security_monitoring.check_security_alerts()
RETURNS INTEGER AS $$
DECLARE
    v_alert_config RECORD;
    v_alert_count INTEGER := 0;
    v_query_result INTEGER;
    v_alert_id UUID;
BEGIN
    -- Iterar sobre alertas ativos
    FOR v_alert_config IN 
        SELECT * FROM security_monitoring.security_alerts_config WHERE is_active = true
    LOOP
        -- Executar query de detecção
        BEGIN
            EXECUTE v_alert_config.query_template INTO v_query_result;
            
            -- Verificar se alerta deve ser disparado
            IF v_alert_config.alert_type = 'threshold' THEN
                IF (v_alert_config.threshold_operator = '>' AND v_query_result > v_alert_config.threshold_value) OR
                   (v_alert_config.threshold_operator = '<' AND v_query_result < v_alert_config.threshold_value) OR
                   (v_alert_config.threshold_operator = '=' AND v_query_result = v_alert_config.threshold_value) OR
                   (v_alert_config.threshold_operator = '>=' AND v_query_result >= v_alert_config.threshold_value) OR
                   (v_alert_config.threshold_operator = '<=' AND v_query_result <= v_alert_config.threshold_value) OR
                   (v_alert_config.threshold_operator = '!=' AND v_query_result != v_alert_config.threshold_value) THEN
                    
                    -- Criar alerta
                    INSERT INTO security_monitoring.security_alerts_history (
                        alert_config_id, alert_name, alert_type, severity_level,
                        alert_data, affected_resources
                    ) VALUES (
                        v_alert_config.id, v_alert_config.alert_name, v_alert_config.alert_type,
                        v_alert_config.severity_level,
                        jsonb_build_object('threshold_value', v_alert_config.threshold_value, 'actual_value', v_query_result),
                        ARRAY['system']
                    ) RETURNING id INTO v_alert_id;
                    
                    v_alert_count := v_alert_count + 1;
                END IF;
            END IF;
            
        EXCEPTION WHEN OTHERS THEN
            -- Log erro mas continue
            RAISE WARNING 'Erro ao verificar alerta %: %', v_alert_config.alert_name, SQLERRM;
        END;
    END LOOP;
    
    RETURN v_alert_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION security_monitoring.check_security_alerts IS 'Verifica alertas de segurança ativos';

-- Função para calcular métricas de segurança
CREATE OR REPLACE FUNCTION security_monitoring.calculate_security_metrics()
RETURNS INTEGER AS $$
DECLARE
    v_metrics_count INTEGER := 0;
    v_current_time TIMESTAMPTZ := NOW();
BEGIN
    -- Métricas de conexões
    INSERT INTO security_monitoring.security_metrics (
        metric_name, metric_type, resource_type, resource_id, metric_value
    ) VALUES
    ('active_connections', 'gauge', 'database', 'postgres', 
     (SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active')),
    
    ('total_connections', 'gauge', 'database', 'postgres',
     (SELECT COUNT(*) FROM pg_stat_activity)),
    
    -- Métricas de autenticação
    ('login_attempts_last_hour', 'counter', 'auth', 'system',
     (SELECT COUNT(*) FROM auth.audit_log_entries WHERE action = 'login' AND created_at > NOW() - INTERVAL '1 hour')),
    
    ('failed_logins_last_hour', 'counter', 'auth', 'system',
     (SELECT COUNT(*) FROM auth.audit_log_entries WHERE action = 'login' AND created_at > NOW() - INTERVAL '1 hour' AND metadata->>'error' IS NOT NULL)),
    
    -- Métricas de auditoria
    ('audit_events_last_hour', 'counter', 'audit', 'system',
     (SELECT COUNT(*) FROM audit.activity_log WHERE event_time > NOW() - INTERVAL '1 hour')),
    
    -- Métricas de compliance
    ('compliance_score', 'gauge', 'compliance', 'lgpd',
     (SELECT lgpd.calculate_compliance_score())),
    
    -- Métricas de dados pessoais
    ('personal_data_fields', 'gauge', 'compliance', 'lgpd',
     (SELECT COUNT(*) FROM lgpd.personal_data_mapping)),
    
    ('encrypted_personal_data_fields', 'gauge', 'compliance', 'lgpd',
     (SELECT COUNT(*) FROM lgpd.personal_data_mapping WHERE is_encrypted = true));
    
    GET DIAGNOSTICS v_metrics_count = ROW_COUNT;
    
    RETURN v_metrics_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION security_monitoring.calculate_security_metrics IS 'Calcula métricas de segurança em tempo real';

-- Função para criar dashboard padrão
CREATE OR REPLACE FUNCTION security_monitoring.create_default_dashboard()
RETURNS INTEGER AS $$
DECLARE
    v_dashboard_id INTEGER;
    v_widgets_count INTEGER := 0;
BEGIN
    -- Criar dashboard principal
    INSERT INTO security_monitoring.security_dashboards (
        dashboard_name, dashboard_type, description, layout_config, created_by
    ) VALUES (
        'Security Overview', 'overview', 'Dashboard principal de segurança',
        '{"title": "Security Overview", "refresh_interval": 30, "theme": "dark"}',
        'security_specialist'
    ) RETURNING id INTO v_dashboard_id;
    
    -- Criar widgets do dashboard
    INSERT INTO security_monitoring.dashboard_widgets (
        dashboard_id, widget_name, widget_type, position_x, position_y, width, height, config
    ) VALUES
    -- Widget de métricas de conexão
    (v_dashboard_id, 'Database Connections', 'metric', 0, 0, 3, 2,
     '{"title": "Active Connections", "query": "SELECT COUNT(*) FROM pg_stat_activity WHERE state = ''active''", "format": "number"}'),
    
    -- Widget de alertas ativos
    (v_dashboard_id, 'Active Alerts', 'alert', 3, 0, 3, 2,
     '{"title": "Active Security Alerts", "severity_filter": ["high", "critical"], "limit": 10}'),
    
    -- Widget de compliance score
    (v_dashboard_id, 'Compliance Score', 'metric', 6, 0, 3, 2,
     '{"title": "LGPD Compliance Score", "query": "SELECT lgpd.calculate_compliance_score()", "format": "percentage"}'),
    
    -- Widget de gráfico de tentativas de login
    (v_dashboard_id, 'Login Attempts', 'chart', 0, 2, 6, 4,
     '{"title": "Login Attempts (Last 24h)", "type": "line", "query": "SELECT DATE_TRUNC(''hour'', created_at) as hour, COUNT(*) as attempts FROM auth.audit_log_entries WHERE action = ''login'' AND created_at > NOW() - INTERVAL ''24 hours'' GROUP BY hour ORDER BY hour"}'),
    
    -- Widget de tabela de incidentes recentes
    (v_dashboard_id, 'Recent Incidents', 'table', 6, 2, 3, 4,
     '{"title": "Recent Security Incidents", "query": "SELECT incident_id, incident_type, severity_level, status, initial_detection FROM security_monitoring.security_incidents ORDER BY initial_detection DESC LIMIT 5"}');
    
    GET DIAGNOSTICS v_widgets_count = ROW_COUNT;
    
    RETURN v_widgets_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION security_monitoring.create_default_dashboard IS 'Cria dashboard padrão de segurança';

-- ================================================================
-- 7. VIEWS PARA RELATÓRIOS
-- ================================================================

-- View para resumo de alertas
CREATE OR REPLACE VIEW security_monitoring.alerts_summary AS
SELECT 
    alert_name,
    alert_type,
    severity_level,
    COUNT(*) as total_alerts,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_alerts,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_alerts,
    MAX(triggered_at) as last_triggered,
    AVG(EXTRACT(EPOCH FROM (resolved_at - triggered_at))/3600) as avg_resolution_hours
FROM security_monitoring.security_alerts_history
GROUP BY alert_name, alert_type, severity_level
ORDER BY severity_level DESC, total_alerts DESC;

COMMENT ON VIEW security_monitoring.alerts_summary IS 'Resumo de alertas de segurança';

-- View para métricas de segurança
CREATE OR REPLACE VIEW security_monitoring.security_metrics_summary AS
SELECT 
    metric_name,
    metric_type,
    resource_type,
    AVG(metric_value) as avg_value,
    MAX(metric_value) as max_value,
    MIN(metric_value) as min_value,
    COUNT(*) as sample_count,
    MAX(timestamp) as last_updated
FROM security_monitoring.security_metrics
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY metric_name, metric_type, resource_type
ORDER BY metric_name;

COMMENT ON VIEW security_monitoring.security_metrics_summary IS 'Resumo de métricas de segurança';

-- View para status de incidentes
CREATE OR REPLACE VIEW security_monitoring.incidents_summary AS
SELECT 
    incident_type,
    severity_level,
    COUNT(*) as total_incidents,
    COUNT(CASE WHEN status = 'open' THEN 1 END) as open_incidents,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_incidents,
    AVG(EXTRACT(EPOCH FROM (resolution_time - initial_detection))/3600) as avg_resolution_hours,
    COUNT(CASE WHEN data_compromised = true THEN 1 END) as incidents_with_data_compromise
FROM security_monitoring.security_incidents
GROUP BY incident_type, severity_level
ORDER BY severity_level DESC, total_incidents DESC;

COMMENT ON VIEW security_monitoring.incidents_summary IS 'Resumo de incidentes de segurança';

-- ================================================================
-- 8. TRIGGERS PARA AUDITORIA
-- ================================================================

-- Função de trigger para auditoria de monitoramento
CREATE OR REPLACE FUNCTION security_monitoring.audit_monitoring_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_operation TEXT;
    v_table_name TEXT;
BEGIN
    -- Determinar operação
    v_operation := TG_OP;
    v_table_name := TG_TABLE_NAME;
    
    -- Registrar atividade de monitoramento na auditoria
    PERFORM audit.log_activity(
        v_operation,
        'security_monitoring',
        v_table_name,
        'security_monitoring.' || v_table_name,
        NULL,
        CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END,
        'INFO',
        ARRAY['monitoring', 'security', v_table_name]
    );
    
    -- Retornar registro apropriado
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION security_monitoring.audit_monitoring_trigger IS 'Trigger para auditoria de operações de monitoramento';

-- Aplicar triggers nas tabelas de monitoramento
CREATE TRIGGER audit_security_alerts_config
    AFTER INSERT OR UPDATE OR DELETE ON security_monitoring.security_alerts_config
    FOR EACH ROW EXECUTE FUNCTION security_monitoring.audit_monitoring_trigger();

CREATE TRIGGER audit_security_alerts_history
    AFTER INSERT OR UPDATE OR DELETE ON security_monitoring.security_alerts_history
    FOR EACH ROW EXECUTE FUNCTION security_monitoring.audit_monitoring_trigger();

CREATE TRIGGER audit_security_incidents
    AFTER INSERT OR UPDATE OR DELETE ON security_monitoring.security_incidents
    FOR EACH ROW EXECUTE FUNCTION security_monitoring.audit_monitoring_trigger();

CREATE TRIGGER audit_security_metrics
    AFTER INSERT OR UPDATE OR DELETE ON security_monitoring.security_metrics
    FOR EACH ROW EXECUTE FUNCTION security_monitoring.audit_monitoring_trigger();

-- ================================================================
-- 9. CONFIGURAR PERMISSÕES DE SEGURANÇA
-- ================================================================

-- Revogar acesso público ao schema de monitoramento
REVOKE ALL ON SCHEMA security_monitoring FROM PUBLIC;

-- Conceder acesso apenas a roles específicos
GRANT USAGE ON SCHEMA security_monitoring TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA security_monitoring TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA security_monitoring TO postgres;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA security_monitoring TO postgres;

-- ================================================================
-- 10. HABILITAR RLS NO SCHEMA DE MONITORAMENTO
-- ================================================================

-- Habilitar RLS nas tabelas de monitoramento
ALTER TABLE security_monitoring.security_alerts_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_monitoring.security_alerts_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_monitoring.security_incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_monitoring.security_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_monitoring.behavior_baseline ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_monitoring.security_dashboards ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_monitoring.dashboard_widgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_monitoring.incident_response_procedures ENABLE ROW LEVEL SECURITY;

-- Políticas para tabelas de monitoramento
CREATE POLICY "security_monitoring_alerts_config_select" ON security_monitoring.security_alerts_config
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "security_monitoring_alerts_history_select" ON security_monitoring.security_alerts_history
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "security_monitoring_incidents_select" ON security_monitoring.security_incidents
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "security_monitoring_metrics_select" ON security_monitoring.security_metrics
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

-- ================================================================
-- 11. INICIALIZAR SISTEMA DE MONITORAMENTO
-- ================================================================

-- Criar alertas padrão de segurança
SELECT security_monitoring.create_default_security_alerts();

-- Criar dashboard padrão
SELECT security_monitoring.create_default_dashboard();

-- Calcular métricas iniciais
SELECT security_monitoring.calculate_security_metrics();

-- ================================================================
-- 12. REGISTRAR APLICAÇÃO DA MIGRAÇÃO
-- ================================================================

-- Registrar na tabela de cache que o monitoramento foi implementado
INSERT INTO public.api_cache (cache_key, data, expires_at, created_at)
VALUES (
    'security_monitoring_20250915',
    jsonb_build_object(
        'migration', 'implement_security_monitoring',
        'components_installed', jsonb_build_array(
            'security_monitoring_schema',
            'security_alerts_config_table',
            'security_alerts_history_table',
            'behavior_baseline_table',
            'security_metrics_table',
            'security_dashboards_table',
            'dashboard_widgets_table',
            'incident_response_procedures_table',
            'security_incidents_table',
            'monitoring_functions',
            'monitoring_views',
            'audit_triggers',
            'rls_policies'
        ),
        'tables_created', 8,
        'functions_created', 4,
        'views_created', 3,
        'triggers_created', 4,
        'applied_by', 'security_specialist',
        'applied_at', NOW(),
        'status', 'completed',
        'security_monitoring', 'implemented'
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

-- Para verificar alertas ativos:
-- SELECT * FROM security_monitoring.alerts_summary;

-- Para verificar métricas de segurança:
-- SELECT * FROM security_monitoring.security_metrics_summary;

-- Para verificar incidentes:
-- SELECT * FROM security_monitoring.incidents_summary;

-- Para verificar alertas de segurança:
-- SELECT security_monitoring.check_security_alerts();

-- Para calcular métricas:
-- SELECT security_monitoring.calculate_security_metrics();

-- Para verificar dashboards:
-- SELECT * FROM security_monitoring.security_dashboards;

-- ================================================================
-- FIM DA MIGRAÇÃO
-- ================================================================
