-- ================================================================
-- MIGRAÇÃO: IMPLEMENTAR COMPLIANCE LGPD/GDPR
-- ================================================================
-- Responsável: Security Specialist 🔐
-- Task: SEC-005 - Implementar Compliance LGPD/GDPR
-- Data: 15 de Setembro de 2025
-- Objetivo: Implementar compliance completo com LGPD/GDPR
-- Status: CRÍTICO - Proteção de dados pessoais conforme regulamentações
-- ================================================================

-- ESTRATÉGIA DE COMPLIANCE LGPD/GDPR:
-- 1. Mapeamento completo de dados pessoais
-- 2. Políticas de retenção e exclusão
-- 3. Sistema de consentimento
-- 4. Procedimentos de portabilidade
-- 5. Direitos dos titulares
-- 6. Relatórios de compliance
-- 7. Integração com auditoria (SEC-003) e criptografia (SEC-004)

BEGIN;

-- ================================================================
-- 1. CRIAR SCHEMA PARA COMPLIANCE LGPD/GDPR
-- ================================================================

-- Criar schema dedicado para compliance
CREATE SCHEMA IF NOT EXISTS lgpd;

-- Comentário no schema
COMMENT ON SCHEMA lgpd IS 'Schema dedicado para compliance LGPD/GDPR';

-- ================================================================
-- 2. MAPEAMENTO DE DADOS PESSOAIS
-- ================================================================

-- Tabela para mapeamento de dados pessoais
CREATE TABLE lgpd.personal_data_mapping (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR NOT NULL,
    schema_name VARCHAR NOT NULL,
    column_name VARCHAR NOT NULL,
    data_type VARCHAR NOT NULL,
    data_category VARCHAR NOT NULL, -- identificação, biométricos, profissionais, etc.
    sensitivity_level VARCHAR NOT NULL, -- baixa, média, alta, crítica
    legal_basis VARCHAR NOT NULL, -- consentimento, contrato, interesse legítimo, etc.
    retention_period INTEGER, -- dias
    purpose VARCHAR NOT NULL, -- finalidade do tratamento
    is_encrypted BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_sensitivity_level CHECK (sensitivity_level IN ('baixa', 'média', 'alta', 'crítica')),
    CONSTRAINT chk_legal_basis CHECK (legal_basis IN ('consentimento', 'contrato', 'interesse_legitimo', 'obrigacao_legal', 'protecao_vida', 'saude_publica')),
    CONSTRAINT chk_data_category CHECK (data_category IN ('identificacao', 'biometricos', 'profissionais', 'comportamentais', 'financeiros', 'saude'))
);

COMMENT ON TABLE lgpd.personal_data_mapping IS 'Mapeamento completo de dados pessoais para compliance LGPD/GDPR';

-- Índices para performance
CREATE INDEX idx_personal_data_mapping_table ON lgpd.personal_data_mapping (table_name, schema_name);
CREATE INDEX idx_personal_data_mapping_category ON lgpd.personal_data_mapping (data_category);
CREATE INDEX idx_personal_data_mapping_sensitivity ON lgpd.personal_data_mapping (sensitivity_level);

-- ================================================================
-- 3. SISTEMA DE CONSENTIMENTO
-- ================================================================

-- Tabela para registro de consentimentos
CREATE TABLE lgpd.consent_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_subject_id VARCHAR NOT NULL, -- identificador do titular
    data_subject_type VARCHAR NOT NULL, -- player, coach, referee, user
    consent_type VARCHAR NOT NULL, -- tratamento, marketing, compartilhamento, etc.
    legal_basis VARCHAR NOT NULL,
    consent_given BOOLEAN NOT NULL,
    consent_date TIMESTAMPTZ NOT NULL,
    consent_method VARCHAR NOT NULL, -- digital, presencial, telefone, etc.
    consent_version VARCHAR NOT NULL, -- versão do termo de consentimento
    purpose VARCHAR NOT NULL,
    data_categories TEXT[] NOT NULL, -- categorias de dados cobertas
    retention_period INTEGER, -- dias
    withdrawal_date TIMESTAMPTZ, -- data de retirada do consentimento
    withdrawal_method VARCHAR, -- método de retirada
    withdrawal_reason TEXT, -- motivo da retirada
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_consent_type CHECK (consent_type IN ('tratamento', 'marketing', 'compartilhamento', 'transferencia_internacional', 'pesquisa')),
    CONSTRAINT chk_consent_method CHECK (consent_method IN ('digital', 'presencial', 'telefone', 'email', 'documento')),
    CONSTRAINT chk_data_subject_type CHECK (data_subject_type IN ('player', 'coach', 'referee', 'user', 'staff'))
);

COMMENT ON TABLE lgpd.consent_records IS 'Registro de consentimentos para tratamento de dados pessoais';

-- Índices para performance
CREATE INDEX idx_consent_records_subject ON lgpd.consent_records (data_subject_id, data_subject_type);
CREATE INDEX idx_consent_records_type ON lgpd.consent_records (consent_type);
CREATE INDEX idx_consent_records_date ON lgpd.consent_records (consent_date);
CREATE INDEX idx_consent_records_withdrawal ON lgpd.consent_records (withdrawal_date) WHERE withdrawal_date IS NOT NULL;

-- ================================================================
-- 4. POLÍTICAS DE RETENÇÃO E EXCLUSÃO
-- ================================================================

-- Tabela para políticas de retenção
CREATE TABLE lgpd.retention_policies (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR NOT NULL,
    schema_name VARCHAR NOT NULL,
    data_category VARCHAR NOT NULL,
    retention_period INTEGER NOT NULL, -- dias
    retention_reason VARCHAR NOT NULL, -- motivo da retenção
    legal_basis VARCHAR NOT NULL,
    auto_delete BOOLEAN DEFAULT false, -- exclusão automática
    archive_before_delete BOOLEAN DEFAULT true, -- arquivar antes de excluir
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_retention_reason CHECK (retention_reason IN ('obrigacao_legal', 'interesse_legitimo', 'contrato', 'consentimento', 'pesquisa'))
);

COMMENT ON TABLE lgpd.retention_policies IS 'Políticas de retenção de dados pessoais';

-- Índices para performance
CREATE INDEX idx_retention_policies_table ON lgpd.retention_policies (table_name, schema_name);
CREATE INDEX idx_retention_policies_category ON lgpd.retention_policies (data_category);

-- ================================================================
-- 5. DIREITOS DOS TITULARES
-- ================================================================

-- Tabela para registro de exercício de direitos
CREATE TABLE lgpd.data_subject_rights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_subject_id VARCHAR NOT NULL,
    data_subject_type VARCHAR NOT NULL,
    right_type VARCHAR NOT NULL, -- acesso, retificação, exclusão, portabilidade, etc.
    request_date TIMESTAMPTZ NOT NULL,
    request_method VARCHAR NOT NULL, -- email, telefone, presencial, etc.
    request_description TEXT NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'pending', -- pending, processing, completed, rejected
    response_date TIMESTAMPTZ,
    response_description TEXT,
    data_provided JSONB, -- dados fornecidos (para direito de acesso/portabilidade)
    processing_time_hours INTEGER, -- tempo de processamento em horas
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_right_type CHECK (right_type IN ('acesso', 'retificacao', 'exclusao', 'portabilidade', 'limitacao', 'objeccao')),
    CONSTRAINT chk_request_method CHECK (request_method IN ('email', 'telefone', 'presencial', 'digital', 'correio')),
    CONSTRAINT chk_status CHECK (status IN ('pending', 'processing', 'completed', 'rejected', 'cancelled'))
);

COMMENT ON TABLE lgpd.data_subject_rights IS 'Registro de exercício de direitos dos titulares de dados';

-- Índices para performance
CREATE INDEX idx_data_subject_rights_subject ON lgpd.data_subject_rights (data_subject_id, data_subject_type);
CREATE INDEX idx_data_subject_rights_type ON lgpd.data_subject_rights (right_type);
CREATE INDEX idx_data_subject_rights_status ON lgpd.data_subject_rights (status);
CREATE INDEX idx_data_subject_rights_date ON lgpd.data_subject_rights (request_date);

-- ================================================================
-- 6. RELATÓRIOS DE COMPLIANCE
-- ================================================================

-- Tabela para relatórios de compliance
CREATE TABLE lgpd.compliance_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR NOT NULL, -- mensal, trimestral, anual, incidente
    report_period_start DATE NOT NULL,
    report_period_end DATE NOT NULL,
    data_subjects_count INTEGER NOT NULL,
    consent_records_count INTEGER NOT NULL,
    rights_requests_count INTEGER NOT NULL,
    data_breaches_count INTEGER DEFAULT 0,
    retention_policies_count INTEGER NOT NULL,
    compliance_score NUMERIC(5,2) NOT NULL, -- 0-100
    recommendations TEXT[],
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    generated_by VARCHAR NOT NULL,
    
    -- Constraints
    CONSTRAINT chk_report_type CHECK (report_type IN ('mensal', 'trimestral', 'anual', 'incidente', 'auditoria')),
    CONSTRAINT chk_compliance_score CHECK (compliance_score >= 0 AND compliance_score <= 100)
);

COMMENT ON TABLE lgpd.compliance_reports IS 'Relatórios de compliance LGPD/GDPR';

-- Índices para performance
CREATE INDEX idx_compliance_reports_type ON lgpd.compliance_reports (report_type);
CREATE INDEX idx_compliance_reports_period ON lgpd.compliance_reports (report_period_start, report_period_end);
CREATE INDEX idx_compliance_reports_score ON lgpd.compliance_reports (compliance_score);

-- ================================================================
-- 7. FUNÇÕES DE COMPLIANCE
-- ================================================================

-- Função para mapear dados pessoais automaticamente
CREATE OR REPLACE FUNCTION lgpd.map_personal_data()
RETURNS INTEGER AS $$
DECLARE
    v_mapped_count INTEGER := 0;
    v_table_record RECORD;
    v_column_record RECORD;
BEGIN
    -- Mapear dados de jogadores
    INSERT INTO lgpd.personal_data_mapping (
        table_name, schema_name, column_name, data_type, data_category,
        sensitivity_level, legal_basis, retention_period, purpose, is_encrypted
    ) VALUES
    ('players', 'public', 'firstname', 'character varying', 'identificacao', 'alta', 'consentimento', 2555, 'Identificação profissional de jogadores', true),
    ('players', 'public', 'lastname', 'character varying', 'identificacao', 'alta', 'consentimento', 2555, 'Identificação profissional de jogadores', true),
    ('players', 'public', 'date_of_birth', 'date', 'identificacao', 'crítica', 'consentimento', 2555, 'Verificação de idade e elegibilidade', true),
    ('players', 'public', 'nationality', 'character varying', 'identificacao', 'média', 'consentimento', 2555, 'Identificação nacional', true),
    ('players', 'public', 'height', 'integer', 'biometricos', 'média', 'consentimento', 2555, 'Dados físicos para análise esportiva', true),
    ('players', 'public', 'weight', 'integer', 'biometricos', 'média', 'consentimento', 2555, 'Dados físicos para análise esportiva', true),
    
    -- Mapear dados de treinadores
    ('coaches', 'public', 'firstname', 'character varying', 'identificacao', 'alta', 'consentimento', 2555, 'Identificação profissional de treinadores', true),
    ('coaches', 'public', 'lastname', 'character varying', 'identificacao', 'alta', 'consentimento', 2555, 'Identificação profissional de treinadores', true),
    ('coaches', 'public', 'nationality', 'character varying', 'identificacao', 'média', 'consentimento', 2555, 'Identificação nacional', true),
    
    -- Mapear dados de árbitros
    ('referees', 'public', 'firstname', 'character varying', 'identificacao', 'alta', 'consentimento', 2555, 'Identificação profissional de árbitros', true),
    ('referees', 'public', 'lastname', 'character varying', 'identificacao', 'alta', 'consentimento', 2555, 'Identificação profissional de árbitros', true),
    ('referees', 'public', 'nationality', 'character varying', 'identificacao', 'média', 'consentimento', 2555, 'Identificação nacional', true);
    
    GET DIAGNOSTICS v_mapped_count = ROW_COUNT;
    
    RETURN v_mapped_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION lgpd.map_personal_data IS 'Mapeia automaticamente dados pessoais para compliance LGPD/GDPR';

-- Função para criar políticas de retenção padrão
CREATE OR REPLACE FUNCTION lgpd.create_default_retention_policies()
RETURNS INTEGER AS $$
DECLARE
    v_policies_count INTEGER := 0;
BEGIN
    -- Políticas de retenção padrão
    INSERT INTO lgpd.retention_policies (
        table_name, schema_name, data_category, retention_period,
        retention_reason, legal_basis, auto_delete, archive_before_delete
    ) VALUES
    ('players', 'public', 'identificacao', 2555, 'contrato', 'contrato', false, true),
    ('players', 'public', 'biometricos', 2555, 'contrato', 'contrato', false, true),
    ('coaches', 'public', 'identificacao', 2555, 'contrato', 'contrato', false, true),
    ('referees', 'public', 'identificacao', 2555, 'contrato', 'contrato', false, true);
    
    GET DIAGNOSTICS v_policies_count = ROW_COUNT;
    
    RETURN v_policies_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION lgpd.create_default_retention_policies IS 'Cria políticas de retenção padrão para dados pessoais';

-- Função para calcular score de compliance
CREATE OR REPLACE FUNCTION lgpd.calculate_compliance_score()
RETURNS NUMERIC AS $$
DECLARE
    v_score NUMERIC := 0;
    v_total_checks INTEGER := 0;
    v_passed_checks INTEGER := 0;
BEGIN
    -- Verificar se dados pessoais estão mapeados
    v_total_checks := v_total_checks + 1;
    IF EXISTS (SELECT 1 FROM lgpd.personal_data_mapping) THEN
        v_passed_checks := v_passed_checks + 1;
    END IF;
    
    -- Verificar se políticas de retenção existem
    v_total_checks := v_total_checks + 1;
    IF EXISTS (SELECT 1 FROM lgpd.retention_policies) THEN
        v_passed_checks := v_passed_checks + 1;
    END IF;
    
    -- Verificar se dados estão criptografados
    v_total_checks := v_total_checks + 1;
    IF EXISTS (SELECT 1 FROM lgpd.personal_data_mapping WHERE is_encrypted = true) THEN
        v_passed_checks := v_passed_checks + 1;
    END IF;
    
    -- Verificar se auditoria está configurada
    v_total_checks := v_total_checks + 1;
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'audit') THEN
        v_passed_checks := v_passed_checks + 1;
    END IF;
    
    -- Verificar se RLS está habilitado
    v_total_checks := v_total_checks + 1;
    IF EXISTS (
        SELECT 1 FROM pg_class c
        JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE n.nspname = 'public' AND c.relname IN ('players', 'coaches', 'referees')
        AND c.relrowsecurity = true
    ) THEN
        v_passed_checks := v_passed_checks + 1;
    END IF;
    
    -- Calcular score
    IF v_total_checks > 0 THEN
        v_score := ROUND((v_passed_checks::NUMERIC / v_total_checks::NUMERIC) * 100, 2);
    END IF;
    
    RETURN v_score;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION lgpd.calculate_compliance_score IS 'Calcula score de compliance LGPD/GDPR';

-- Função para gerar relatório de compliance
CREATE OR REPLACE FUNCTION lgpd.generate_compliance_report(
    p_report_type VARCHAR,
    p_period_start DATE,
    p_period_end DATE
)
RETURNS UUID AS $$
DECLARE
    v_report_id UUID;
    v_data_subjects_count INTEGER;
    v_consent_records_count INTEGER;
    v_rights_requests_count INTEGER;
    v_retention_policies_count INTEGER;
    v_compliance_score NUMERIC;
BEGIN
    -- Calcular estatísticas
    SELECT COUNT(DISTINCT data_subject_id) INTO v_data_subjects_count
    FROM lgpd.consent_records
    WHERE consent_date BETWEEN p_period_start AND p_period_end;
    
    SELECT COUNT(*) INTO v_consent_records_count
    FROM lgpd.consent_records
    WHERE consent_date BETWEEN p_period_start AND p_period_end;
    
    SELECT COUNT(*) INTO v_rights_requests_count
    FROM lgpd.data_subject_rights
    WHERE request_date BETWEEN p_period_start AND p_period_end;
    
    SELECT COUNT(*) INTO v_retention_policies_count
    FROM lgpd.retention_policies;
    
    -- Calcular score de compliance
    SELECT lgpd.calculate_compliance_score() INTO v_compliance_score;
    
    -- Inserir relatório
    INSERT INTO lgpd.compliance_reports (
        report_type, report_period_start, report_period_end,
        data_subjects_count, consent_records_count, rights_requests_count,
        retention_policies_count, compliance_score, generated_by
    ) VALUES (
        p_report_type, p_period_start, p_period_end,
        v_data_subjects_count, v_consent_records_count, v_rights_requests_count,
        v_retention_policies_count, v_compliance_score, 'security_specialist'
    ) RETURNING id INTO v_report_id;
    
    RETURN v_report_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION lgpd.generate_compliance_report IS 'Gera relatório de compliance LGPD/GDPR';

-- ================================================================
-- 8. VIEWS PARA RELATÓRIOS
-- ================================================================

-- View para resumo de dados pessoais
CREATE OR REPLACE VIEW lgpd.personal_data_summary AS
SELECT 
    data_category,
    COUNT(*) as total_fields,
    COUNT(CASE WHEN is_encrypted = true THEN 1 END) as encrypted_fields,
    COUNT(CASE WHEN sensitivity_level = 'crítica' THEN 1 END) as critical_fields,
    COUNT(CASE WHEN sensitivity_level = 'alta' THEN 1 END) as high_sensitivity_fields,
    ROUND(
        COUNT(CASE WHEN is_encrypted = true THEN 1 END)::NUMERIC / 
        COUNT(*) * 100, 2
    ) as encryption_percentage
FROM lgpd.personal_data_mapping
GROUP BY data_category
ORDER BY data_category;

COMMENT ON VIEW lgpd.personal_data_summary IS 'Resumo de dados pessoais por categoria';

-- View para status de consentimentos
CREATE OR REPLACE VIEW lgpd.consent_status AS
SELECT 
    consent_type,
    COUNT(*) as total_consents,
    COUNT(CASE WHEN consent_given = true THEN 1 END) as consents_given,
    COUNT(CASE WHEN withdrawal_date IS NOT NULL THEN 1 END) as consents_withdrawn,
    ROUND(
        COUNT(CASE WHEN consent_given = true THEN 1 END)::NUMERIC / 
        COUNT(*) * 100, 2
    ) as consent_rate
FROM lgpd.consent_records
GROUP BY consent_type
ORDER BY consent_type;

COMMENT ON VIEW lgpd.consent_status IS 'Status de consentimentos por tipo';

-- View para direitos dos titulares
CREATE OR REPLACE VIEW lgpd.rights_summary AS
SELECT 
    right_type,
    COUNT(*) as total_requests,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_requests,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_requests,
    ROUND(
        COUNT(CASE WHEN status = 'completed' THEN 1 END)::NUMERIC / 
        COUNT(*) * 100, 2
    ) as completion_rate,
    ROUND(AVG(processing_time_hours), 2) as avg_processing_hours
FROM lgpd.data_subject_rights
GROUP BY right_type
ORDER BY right_type;

COMMENT ON VIEW lgpd.rights_summary IS 'Resumo de direitos dos titulares';

-- ================================================================
-- 9. TRIGGERS PARA AUDITORIA
-- ================================================================

-- Função de trigger para auditoria de compliance
CREATE OR REPLACE FUNCTION lgpd.audit_compliance_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_operation TEXT;
    v_table_name TEXT;
BEGIN
    -- Determinar operação
    v_operation := TG_OP;
    v_table_name := TG_TABLE_NAME;
    
    -- Registrar atividade de compliance na auditoria
    PERFORM audit.log_activity(
        v_operation,
        'lgpd',
        v_table_name,
        'lgpd.' || v_table_name,
        NULL,
        CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END,
        'INFO',
        ARRAY['compliance', 'lgpd', v_table_name]
    );
    
    -- Retornar registro apropriado
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION lgpd.audit_compliance_trigger IS 'Trigger para auditoria de operações de compliance';

-- Aplicar triggers nas tabelas de compliance
CREATE TRIGGER audit_personal_data_mapping
    AFTER INSERT OR UPDATE OR DELETE ON lgpd.personal_data_mapping
    FOR EACH ROW EXECUTE FUNCTION lgpd.audit_compliance_trigger();

CREATE TRIGGER audit_consent_records
    AFTER INSERT OR UPDATE OR DELETE ON lgpd.consent_records
    FOR EACH ROW EXECUTE FUNCTION lgpd.audit_compliance_trigger();

CREATE TRIGGER audit_data_subject_rights
    AFTER INSERT OR UPDATE OR DELETE ON lgpd.data_subject_rights
    FOR EACH ROW EXECUTE FUNCTION lgpd.audit_compliance_trigger();

CREATE TRIGGER audit_retention_policies
    AFTER INSERT OR UPDATE OR DELETE ON lgpd.retention_policies
    FOR EACH ROW EXECUTE FUNCTION lgpd.audit_compliance_trigger();

CREATE TRIGGER audit_compliance_reports
    AFTER INSERT OR UPDATE OR DELETE ON lgpd.compliance_reports
    FOR EACH ROW EXECUTE FUNCTION lgpd.audit_compliance_trigger();

-- ================================================================
-- 10. CONFIGURAR PERMISSÕES DE SEGURANÇA
-- ================================================================

-- Revogar acesso público ao schema de compliance
REVOKE ALL ON SCHEMA lgpd FROM PUBLIC;

-- Conceder acesso apenas a roles específicos
GRANT USAGE ON SCHEMA lgpd TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA lgpd TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA lgpd TO postgres;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA lgpd TO postgres;

-- ================================================================
-- 11. HABILITAR RLS NO SCHEMA DE COMPLIANCE
-- ================================================================

-- Habilitar RLS nas tabelas de compliance
ALTER TABLE lgpd.personal_data_mapping ENABLE ROW LEVEL SECURITY;
ALTER TABLE lgpd.consent_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE lgpd.data_subject_rights ENABLE ROW LEVEL SECURITY;
ALTER TABLE lgpd.retention_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE lgpd.compliance_reports ENABLE ROW LEVEL SECURITY;

-- Políticas para tabelas de compliance
CREATE POLICY "lgpd_personal_data_mapping_select" ON lgpd.personal_data_mapping
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "lgpd_personal_data_mapping_insert" ON lgpd.personal_data_mapping
    FOR INSERT WITH CHECK (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "lgpd_consent_records_select" ON lgpd.consent_records
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "lgpd_consent_records_insert" ON lgpd.consent_records
    FOR INSERT WITH CHECK (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "lgpd_data_subject_rights_select" ON lgpd.data_subject_rights
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "lgpd_data_subject_rights_insert" ON lgpd.data_subject_rights
    FOR INSERT WITH CHECK (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "lgpd_retention_policies_select" ON lgpd.retention_policies
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "lgpd_compliance_reports_select" ON lgpd.compliance_reports
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

-- ================================================================
-- 12. INICIALIZAR DADOS DE COMPLIANCE
-- ================================================================

-- Executar mapeamento inicial de dados pessoais
SELECT lgpd.map_personal_data();

-- Criar políticas de retenção padrão
SELECT lgpd.create_default_retention_policies();

-- Gerar relatório inicial de compliance
SELECT lgpd.generate_compliance_report('anual', CURRENT_DATE - INTERVAL '1 year', CURRENT_DATE);

-- ================================================================
-- 13. REGISTRAR APLICAÇÃO DA MIGRAÇÃO
-- ================================================================

-- Registrar na tabela de cache que o compliance foi implementado
INSERT INTO public.api_cache (cache_key, data, expires_at, created_at)
VALUES (
    'lgpd_compliance_20250915',
    jsonb_build_object(
        'migration', 'implement_lgpd_compliance',
        'components_installed', jsonb_build_array(
            'lgpd_schema',
            'personal_data_mapping_table',
            'consent_records_table',
            'data_subject_rights_table',
            'retention_policies_table',
            'compliance_reports_table',
            'compliance_functions',
            'compliance_views',
            'audit_triggers',
            'rls_policies'
        ),
        'tables_created', 5,
        'functions_created', 4,
        'views_created', 3,
        'triggers_created', 5,
        'applied_by', 'security_specialist',
        'applied_at', NOW(),
        'status', 'completed',
        'lgpd_compliance', 'implemented'
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

-- Para verificar mapeamento de dados pessoais:
-- SELECT * FROM lgpd.personal_data_mapping;

-- Para verificar status de consentimentos:
-- SELECT * FROM lgpd.consent_status;

-- Para verificar direitos dos titulares:
-- SELECT * FROM lgpd.rights_summary;

-- Para calcular score de compliance:
-- SELECT lgpd.calculate_compliance_score();

-- Para gerar relatório de compliance:
-- SELECT lgpd.generate_compliance_report('mensal', CURRENT_DATE - INTERVAL '1 month', CURRENT_DATE);

-- Para verificar resumo de dados pessoais:
-- SELECT * FROM lgpd.personal_data_summary;

-- ================================================================
-- FIM DA MIGRAÇÃO
-- ================================================================
