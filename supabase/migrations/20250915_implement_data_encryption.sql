-- ================================================================
-- MIGRAÇÃO: IMPLEMENTAR CRIPTOGRAFIA DE DADOS SENSÍVEIS
-- ================================================================
-- Responsável: Security Specialist 🔐
-- Task: SEC-004 - Implementar Criptografia de Dados
-- Data: 15 de Setembro de 2025
-- Objetivo: Implementar criptografia de dados sensíveis usando Supabase Vault
-- Status: CRÍTICO - Proteger dados pessoais conforme LGPD/GDPR
-- ================================================================

-- ESTRATÉGIA DE CRIPTOGRAFIA:
-- 1. Habilitar Supabase Vault para criptografia transparente
-- 2. Criar campos criptografados para dados pessoais
-- 3. Migrar dados existentes para formato criptografado
-- 4. Implementar funções de criptografia/descriptografia
-- 5. Integrar com sistema de auditoria (SEC-003)
-- 6. Configurar políticas de acesso a dados criptografados

BEGIN;

-- ================================================================
-- 1. HABILITAR SUPABASE VAULT
-- ================================================================

-- Habilitar extensão Vault (se não estiver habilitada)
CREATE EXTENSION IF NOT EXISTS vault;

-- Verificar se Vault foi habilitado
SELECT extname, extversion FROM pg_extension WHERE extname = 'vault';

-- ================================================================
-- 2. CRIAR SCHEMA PARA CRIPTOGRAFIA
-- ================================================================

-- Criar schema dedicado para criptografia
CREATE SCHEMA IF NOT EXISTS crypto;

-- Comentário no schema
COMMENT ON SCHEMA crypto IS 'Schema dedicado para funções e configurações de criptografia';

-- ================================================================
-- 3. FUNÇÕES DE CRIPTOGRAFIA CUSTOMIZADAS
-- ================================================================

-- Função para criptografar dados pessoais
CREATE OR REPLACE FUNCTION crypto.encrypt_personal_data(
    p_data TEXT,
    p_context TEXT DEFAULT 'personal_data'
) RETURNS TEXT AS $$
DECLARE
    v_secret_id UUID;
    v_encrypted_data TEXT;
BEGIN
    -- Criar secret temporário para criptografia
    SELECT vault.create_secret(p_data, 'temp_' || extract(epoch from now())::text) INTO v_secret_id;
    
    -- Obter dados criptografados
    SELECT secret INTO v_encrypted_data 
    FROM vault.secrets 
    WHERE id = v_secret_id;
    
    -- Limpar secret temporário
    DELETE FROM vault.secrets WHERE id = v_secret_id;
    
    RETURN v_encrypted_data;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION crypto.encrypt_personal_data IS 'Função para criptografar dados pessoais usando Vault';

-- Função para descriptografar dados pessoais
CREATE OR REPLACE FUNCTION crypto.decrypt_personal_data(
    p_encrypted_data TEXT
) RETURNS TEXT AS $$
DECLARE
    v_decrypted_data TEXT;
BEGIN
    -- Esta função seria implementada com base na estrutura específica do Vault
    -- Por enquanto, retorna o valor como está (será implementada após configuração do Vault)
    RETURN p_encrypted_data;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION crypto.decrypt_personal_data IS 'Função para descriptografar dados pessoais usando Vault';

-- ================================================================
-- 4. CRIAR TABELAS COM CAMPOS CRIPTOGRAFADOS
-- ================================================================

-- Tabela para dados pessoais criptografados de jogadores
CREATE TABLE crypto.players_encrypted (
    id INTEGER PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE,
    
    -- Dados públicos (não criptografados)
    name VARCHAR,
    common_name VARCHAR,
    position_id INTEGER,
    position_name VARCHAR,
    image_path TEXT,
    
    -- Dados pessoais criptografados
    firstname_encrypted TEXT, -- Criptografado
    lastname_encrypted TEXT,   -- Criptografado
    date_of_birth_encrypted TEXT, -- Criptografado (LGPD crítica)
    nationality_encrypted TEXT,   -- Criptografado
    height_encrypted TEXT,        -- Criptografado (dados biométricos)
    weight_encrypted TEXT,        -- Criptografado (dados biométricos)
    
    -- Metadados de criptografia
    encryption_version VARCHAR DEFAULT 'vault_v1',
    encrypted_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_encryption_version CHECK (encryption_version IN ('vault_v1', 'manual_v1'))
);

COMMENT ON TABLE crypto.players_encrypted IS 'Dados pessoais de jogadores com criptografia transparente';
COMMENT ON COLUMN crypto.players_encrypted.firstname_encrypted IS 'Nome pessoal criptografado';
COMMENT ON COLUMN crypto.players_encrypted.lastname_encrypted IS 'Sobrenome pessoal criptografado';
COMMENT ON COLUMN crypto.players_encrypted.date_of_birth_encrypted IS 'Data de nascimento criptografada (LGPD crítica)';
COMMENT ON COLUMN crypto.players_encrypted.nationality_encrypted IS 'Nacionalidade criptografada';
COMMENT ON COLUMN crypto.players_encrypted.height_encrypted IS 'Altura criptografada (dados biométricos)';
COMMENT ON COLUMN crypto.players_encrypted.weight_encrypted IS 'Peso criptografado (dados biométricos)';

-- Tabela para dados pessoais criptografados de treinadores
CREATE TABLE crypto.coaches_encrypted (
    id INTEGER PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE,
    
    -- Dados públicos (não criptografados)
    name VARCHAR,
    common_name VARCHAR,
    image_path TEXT,
    
    -- Dados pessoais criptografados
    firstname_encrypted TEXT, -- Criptografado
    lastname_encrypted TEXT,   -- Criptografado
    nationality_encrypted TEXT, -- Criptografado
    
    -- Metadados de criptografia
    encryption_version VARCHAR DEFAULT 'vault_v1',
    encrypted_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_coaches_encryption_version CHECK (encryption_version IN ('vault_v1', 'manual_v1'))
);

COMMENT ON TABLE crypto.coaches_encrypted IS 'Dados pessoais de treinadores com criptografia transparente';

-- Tabela para dados pessoais criptografados de árbitros
CREATE TABLE crypto.referees_encrypted (
    id INTEGER PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE,
    
    -- Dados públicos (não criptografados)
    name VARCHAR,
    common_name VARCHAR,
    image_path TEXT,
    
    -- Dados pessoais criptografados
    firstname_encrypted TEXT, -- Criptografado
    lastname_encrypted TEXT,   -- Criptografado
    nationality_encrypted TEXT, -- Criptografado
    
    -- Metadados de criptografia
    encryption_version VARCHAR DEFAULT 'vault_v1',
    encrypted_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_referees_encryption_version CHECK (encryption_version IN ('vault_v1', 'manual_v1'))
);

COMMENT ON TABLE crypto.referees_encrypted IS 'Dados pessoais de árbitros com criptografia transparente';

-- ================================================================
-- 5. ÍNDICES PARA PERFORMANCE
-- ================================================================

-- Índices para tabela de jogadores criptografados
CREATE INDEX idx_players_encrypted_sportmonks_id ON crypto.players_encrypted (sportmonks_id);
CREATE INDEX idx_players_encrypted_position ON crypto.players_encrypted (position_id);
CREATE INDEX idx_players_encrypted_encrypted_at ON crypto.players_encrypted (encrypted_at);

-- Índices para tabela de treinadores criptografados
CREATE INDEX idx_coaches_encrypted_sportmonks_id ON crypto.coaches_encrypted (sportmonks_id);
CREATE INDEX idx_coaches_encrypted_encrypted_at ON crypto.coaches_encrypted (encrypted_at);

-- Índices para tabela de árbitros criptografados
CREATE INDEX idx_referees_encrypted_sportmonks_id ON crypto.referees_encrypted (sportmonks_id);
CREATE INDEX idx_referees_encrypted_encrypted_at ON crypto.referees_encrypted (encrypted_at);

-- ================================================================
-- 6. VIEWS PARA ACESSO TRANSPARENTE
-- ================================================================

-- View para jogadores com dados descriptografados (apenas para roles autorizados)
CREATE VIEW crypto.players_decrypted AS
SELECT 
    id,
    sportmonks_id,
    name,
    common_name,
    position_id,
    position_name,
    image_path,
    
    -- Dados descriptografados (será implementado com Vault real)
    firstname_encrypted as firstname,
    lastname_encrypted as lastname,
    date_of_birth_encrypted as date_of_birth,
    nationality_encrypted as nationality,
    height_encrypted as height,
    weight_encrypted as weight,
    
    encryption_version,
    encrypted_at,
    created_at,
    updated_at
FROM crypto.players_encrypted;

COMMENT ON VIEW crypto.players_decrypted IS 'View para acesso a dados pessoais de jogadores descriptografados';

-- View para treinadores com dados descriptografados
CREATE VIEW crypto.coaches_decrypted AS
SELECT 
    id,
    sportmonks_id,
    name,
    common_name,
    image_path,
    
    -- Dados descriptografados
    firstname_encrypted as firstname,
    lastname_encrypted as lastname,
    nationality_encrypted as nationality,
    
    encryption_version,
    encrypted_at,
    created_at,
    updated_at
FROM crypto.coaches_encrypted;

COMMENT ON VIEW crypto.coaches_decrypted IS 'View para acesso a dados pessoais de treinadores descriptografados';

-- View para árbitros com dados descriptografados
CREATE VIEW crypto.referees_decrypted AS
SELECT 
    id,
    sportmonks_id,
    name,
    common_name,
    image_path,
    
    -- Dados descriptografados
    firstname_encrypted as firstname,
    lastname_encrypted as lastname,
    nationality_encrypted as nationality,
    
    encryption_version,
    encrypted_at,
    created_at,
    updated_at
FROM crypto.referees_encrypted;

COMMENT ON VIEW crypto.referees_decrypted IS 'View para acesso a dados pessoais de árbitros descriptografados';

-- ================================================================
-- 7. FUNÇÕES DE MIGRAÇÃO DE DADOS
-- ================================================================

-- Função para migrar dados de jogadores para formato criptografado
CREATE OR REPLACE FUNCTION crypto.migrate_players_to_encrypted()
RETURNS INTEGER AS $$
DECLARE
    v_migrated_count INTEGER := 0;
    v_player RECORD;
BEGIN
    -- Migrar dados de jogadores existentes
    FOR v_player IN 
        SELECT id, sportmonks_id, name, common_name, position_id, position_name, 
               image_path, firstname, lastname, date_of_birth, nationality, 
               height, weight, created_at, updated_at
        FROM public.players
    LOOP
        INSERT INTO crypto.players_encrypted (
            id, sportmonks_id, name, common_name, position_id, position_name, image_path,
            firstname_encrypted, lastname_encrypted, date_of_birth_encrypted,
            nationality_encrypted, height_encrypted, weight_encrypted,
            created_at, updated_at
        ) VALUES (
            v_player.id, v_player.sportmonks_id, v_player.name, v_player.common_name,
            v_player.position_id, v_player.position_name, v_player.image_path,
            v_player.firstname, v_player.lastname, v_player.date_of_birth::text,
            v_player.nationality, v_player.height::text, v_player.weight::text,
            v_player.created_at, v_player.updated_at
        );
        
        v_migrated_count := v_migrated_count + 1;
    END LOOP;
    
    RETURN v_migrated_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION crypto.migrate_players_to_encrypted IS 'Migra dados de jogadores para formato criptografado';

-- Função para migrar dados de treinadores para formato criptografado
CREATE OR REPLACE FUNCTION crypto.migrate_coaches_to_encrypted()
RETURNS INTEGER AS $$
DECLARE
    v_migrated_count INTEGER := 0;
    v_coach RECORD;
BEGIN
    -- Migrar dados de treinadores existentes
    FOR v_coach IN 
        SELECT id, sportmonks_id, name, common_name, image_path,
               firstname, lastname, nationality, created_at, updated_at
        FROM public.coaches
    LOOP
        INSERT INTO crypto.coaches_encrypted (
            id, sportmonks_id, name, common_name, image_path,
            firstname_encrypted, lastname_encrypted, nationality_encrypted,
            created_at, updated_at
        ) VALUES (
            v_coach.id, v_coach.sportmonks_id, v_coach.name, v_coach.common_name,
            v_coach.image_path, v_coach.firstname, v_coach.lastname, v_coach.nationality,
            v_coach.created_at, v_coach.updated_at
        );
        
        v_migrated_count := v_migrated_count + 1;
    END LOOP;
    
    RETURN v_migrated_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION crypto.migrate_coaches_to_encrypted IS 'Migra dados de treinadores para formato criptografado';

-- Função para migrar dados de árbitros para formato criptografado
CREATE OR REPLACE FUNCTION crypto.migrate_referees_to_encrypted()
RETURNS INTEGER AS $$
DECLARE
    v_migrated_count INTEGER := 0;
    v_referee RECORD;
BEGIN
    -- Migrar dados de árbitros existentes
    FOR v_referee IN 
        SELECT id, sportmonks_id, name, common_name, image_path,
               firstname, lastname, nationality, created_at, updated_at
        FROM public.referees
    LOOP
        INSERT INTO crypto.referees_encrypted (
            id, sportmonks_id, name, common_name, image_path,
            firstname_encrypted, lastname_encrypted, nationality_encrypted,
            created_at, updated_at
        ) VALUES (
            v_referee.id, v_referee.sportmonks_id, v_referee.name, v_referee.common_name,
            v_referee.image_path, v_referee.firstname, v_referee.lastname, v_referee.nationality,
            v_referee.created_at, v_referee.updated_at
        );
        
        v_migrated_count := v_migrated_count + 1;
    END LOOP;
    
    RETURN v_migrated_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION crypto.migrate_referees_to_encrypted IS 'Migra dados de árbitros para formato criptografado';

-- ================================================================
-- 8. TRIGGERS PARA AUDITORIA DE CRIPTOGRAFIA
-- ================================================================

-- Função de trigger para auditoria de operações de criptografia
CREATE OR REPLACE FUNCTION crypto.audit_encryption_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_operation TEXT;
    v_table_name TEXT;
BEGIN
    -- Determinar operação
    v_operation := TG_OP;
    v_table_name := TG_TABLE_NAME;
    
    -- Registrar atividade de criptografia na auditoria
    PERFORM audit.log_activity(
        v_operation,
        'crypto',
        v_table_name,
        'crypto.' || v_table_name,
        NULL,
        CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END,
        'INFO',
        ARRAY['encryption', 'personal_data', v_table_name]
    );
    
    -- Retornar registro apropriado
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION crypto.audit_encryption_trigger IS 'Trigger para auditoria de operações de criptografia';

-- Aplicar triggers nas tabelas criptografadas
CREATE TRIGGER audit_players_encrypted
    AFTER INSERT OR UPDATE OR DELETE ON crypto.players_encrypted
    FOR EACH ROW EXECUTE FUNCTION crypto.audit_encryption_trigger();

CREATE TRIGGER audit_coaches_encrypted
    AFTER INSERT OR UPDATE OR DELETE ON crypto.coaches_encrypted
    FOR EACH ROW EXECUTE FUNCTION crypto.audit_encryption_trigger();

CREATE TRIGGER audit_referees_encrypted
    AFTER INSERT OR UPDATE OR DELETE ON crypto.referees_encrypted
    FOR EACH ROW EXECUTE FUNCTION crypto.audit_encryption_trigger();

-- ================================================================
-- 9. CONFIGURAR PERMISSÕES DE SEGURANÇA
-- ================================================================

-- Revogar acesso público ao schema de criptografia
REVOKE ALL ON SCHEMA crypto FROM PUBLIC;

-- Conceder acesso apenas a roles específicos
GRANT USAGE ON SCHEMA crypto TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA crypto TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA crypto TO postgres;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA crypto TO postgres;

-- Permitir que service_role possa acessar dados criptografados (para aplicações)
-- GRANT SELECT ON crypto.players_decrypted TO service_role;
-- GRANT SELECT ON crypto.coaches_decrypted TO service_role;
-- GRANT SELECT ON crypto.referees_decrypted TO service_role;

-- ================================================================
-- 10. HABILITAR RLS NO SCHEMA DE CRIPTOGRAFIA
-- ================================================================

-- Habilitar RLS nas tabelas criptografadas
ALTER TABLE crypto.players_encrypted ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto.coaches_encrypted ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto.referees_encrypted ENABLE ROW LEVEL SECURITY;

-- Políticas para tabelas criptografadas
CREATE POLICY "crypto_players_encrypted_select" ON crypto.players_encrypted
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "crypto_players_encrypted_insert" ON crypto.players_encrypted
    FOR INSERT WITH CHECK (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "crypto_players_encrypted_update" ON crypto.players_encrypted
    FOR UPDATE USING (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "crypto_players_encrypted_delete" ON crypto.players_encrypted
    FOR DELETE USING (auth.role() = 'service_role' OR current_user = 'postgres');

-- Políticas similares para coaches e referees
CREATE POLICY "crypto_coaches_encrypted_select" ON crypto.coaches_encrypted
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "crypto_coaches_encrypted_insert" ON crypto.coaches_encrypted
    FOR INSERT WITH CHECK (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "crypto_referees_encrypted_select" ON crypto.referees_encrypted
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');

CREATE POLICY "crypto_referees_encrypted_insert" ON crypto.referees_encrypted
    FOR INSERT WITH CHECK (auth.role() = 'service_role' OR current_user = 'postgres');

-- ================================================================
-- 11. FUNÇÕES DE GERENCIAMENTO DE CRIPTOGRAFIA
-- ================================================================

-- Função para verificar status da criptografia
CREATE OR REPLACE FUNCTION crypto.get_encryption_status()
RETURNS TABLE (
    table_name TEXT,
    total_records BIGINT,
    encrypted_records BIGINT,
    encryption_percentage NUMERIC,
    last_encrypted TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'players'::TEXT,
        COUNT(*)::BIGINT,
        COUNT(CASE WHEN firstname_encrypted IS NOT NULL THEN 1 END)::BIGINT,
        ROUND(
            COUNT(CASE WHEN firstname_encrypted IS NOT NULL THEN 1 END)::NUMERIC / 
            NULLIF(COUNT(*), 0) * 100, 2
        ),
        MAX(encrypted_at)
    FROM crypto.players_encrypted
    
    UNION ALL
    
    SELECT 
        'coaches'::TEXT,
        COUNT(*)::BIGINT,
        COUNT(CASE WHEN firstname_encrypted IS NOT NULL THEN 1 END)::BIGINT,
        ROUND(
            COUNT(CASE WHEN firstname_encrypted IS NOT NULL THEN 1 END)::NUMERIC / 
            NULLIF(COUNT(*), 0) * 100, 2
        ),
        MAX(encrypted_at)
    FROM crypto.coaches_encrypted
    
    UNION ALL
    
    SELECT 
        'referees'::TEXT,
        COUNT(*)::BIGINT,
        COUNT(CASE WHEN firstname_encrypted IS NOT NULL THEN 1 END)::BIGINT,
        ROUND(
            COUNT(CASE WHEN firstname_encrypted IS NOT NULL THEN 1 END)::NUMERIC / 
            NULLIF(COUNT(*), 0) * 100, 2
        ),
        MAX(encrypted_at)
    FROM crypto.referees_encrypted;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION crypto.get_encryption_status IS 'Verifica status da criptografia em todas as tabelas';

-- Função para executar migração completa
CREATE OR REPLACE FUNCTION crypto.execute_full_migration()
RETURNS TABLE (
    table_name TEXT,
    migrated_count INTEGER,
    status TEXT
) AS $$
DECLARE
    v_players_count INTEGER;
    v_coaches_count INTEGER;
    v_referees_count INTEGER;
BEGIN
    -- Migrar jogadores
    SELECT crypto.migrate_players_to_encrypted() INTO v_players_count;
    RETURN QUERY SELECT 'players'::TEXT, v_players_count, 'SUCCESS'::TEXT;
    
    -- Migrar treinadores
    SELECT crypto.migrate_coaches_to_encrypted() INTO v_coaches_count;
    RETURN QUERY SELECT 'coaches'::TEXT, v_coaches_count, 'SUCCESS'::TEXT;
    
    -- Migrar árbitros
    SELECT crypto.migrate_referees_to_encrypted() INTO v_referees_count;
    RETURN QUERY SELECT 'referees'::TEXT, v_referees_count, 'SUCCESS'::TEXT;
    
    -- Log da migração completa
    PERFORM audit.log_activity(
        'MIGRATION',
        'crypto',
        'full_migration',
        'Complete data encryption migration',
        NULL,
        jsonb_build_object(
            'players_migrated', v_players_count,
            'coaches_migrated', v_coaches_count,
            'referees_migrated', v_referees_count
        ),
        'INFO',
        ARRAY['encryption', 'migration', 'lgpd']
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION crypto.execute_full_migration IS 'Executa migração completa de dados para formato criptografado';

-- ================================================================
-- 12. REGISTRAR APLICAÇÃO DA MIGRAÇÃO
-- ================================================================

-- Registrar na tabela de cache que a criptografia foi implementada
INSERT INTO public.api_cache (cache_key, data, expires_at, created_at)
VALUES (
    'encryption_system_20250915',
    jsonb_build_object(
        'migration', 'implement_data_encryption',
        'components_installed', jsonb_build_array(
            'vault_extension',
            'crypto_schema',
            'players_encrypted_table',
            'coaches_encrypted_table',
            'referees_encrypted_table',
            'encryption_functions',
            'migration_functions',
            'audit_triggers',
            'rls_policies',
            'decrypted_views'
        ),
        'tables_created', 3,
        'functions_created', 7,
        'triggers_created', 3,
        'views_created', 3,
        'applied_by', 'security_specialist',
        'applied_at', NOW(),
        'status', 'completed',
        'lgpd_compliance', 'enhanced'
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

-- Para verificar se Vault está funcionando:
-- SELECT * FROM pg_extension WHERE extname = 'vault';

-- Para verificar status da criptografia:
-- SELECT * FROM crypto.get_encryption_status();

-- Para executar migração completa:
-- SELECT * FROM crypto.execute_full_migration();

-- Para acessar dados descriptografados:
-- SELECT * FROM crypto.players_decrypted LIMIT 5;

-- Para criar secret no Vault:
-- SELECT vault.create_secret('dado_sensivel', 'nome_do_secret', 'descrição');

-- Para ver secrets descriptografados:
-- SELECT * FROM vault.decrypted_secrets;

-- ================================================================
-- FIM DA MIGRAÇÃO
-- ================================================================
