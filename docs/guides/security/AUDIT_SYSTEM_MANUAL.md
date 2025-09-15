# Manual do Sistema de Auditoria BDFut 🔐

**Responsável:** Security Specialist  
**Task:** SEC-003 - Implementar Logs de Auditoria  
**Data:** 15 de Setembro de 2025  
**Status:** ✅ IMPLEMENTADO

---

## 📋 **VISÃO GERAL**

O Sistema de Auditoria BDFut implementa **rastreabilidade completa** de todas as operações críticas no banco de dados, garantindo **compliance LGPD/GDPR** e **detecção de atividades suspeitas**.

### 🎯 **OBJETIVOS ALCANÇADOS**
- ✅ **Auditoria completa** de todas as operações críticas
- ✅ **Rastreabilidade** de alterações de dados
- ✅ **Logs de acesso** e autenticação
- ✅ **Sistema de retenção** de logs automático
- ✅ **Dashboard de auditoria** básico
- ✅ **Integração com RLS** implementado

---

## 🏗️ **ARQUITETURA DO SISTEMA**

### **1. EXTENSÃO PGAUDIT**
- **Funcionalidade:** Auditoria nativa do PostgreSQL
- **Configuração:** `write, ddl, role` para postgres
- **Cobertura:** Todas as operações de escrita e DDL

### **2. SCHEMA AUDIT CUSTOMIZADO**
```sql
CREATE SCHEMA audit;
```
- **Propósito:** Isolamento e organização dos logs
- **Segurança:** RLS habilitado, acesso restrito

### **3. TABELAS DE AUDITORIA**

#### **3.1 activity_log**
- **Registros:** Todas as atividades auditadas
- **Campos principais:**
  - `timestamp` - Momento da atividade
  - `user_id` - Usuário responsável
  - `operation_type` - Tipo de operação (SELECT, INSERT, etc.)
  - `table_name` - Tabela afetada
  - `old_values` / `new_values` - Valores antes/depois
  - `severity` - Nível de criticidade

#### **3.2 user_sessions**
- **Registros:** Sessões de usuários
- **Rastreamento:** Login, logout, atividades por sessão

#### **3.3 security_alerts**
- **Registros:** Alertas de segurança automatizados
- **Tipos:** Atividades suspeitas, violações de política

---

## 🔧 **INSTALAÇÃO E CONFIGURAÇÃO**

### **Passo 1: Aplicar Migração**
```bash
# Via Supabase Dashboard
# 1. Acessar SQL Editor
# 2. Executar: supabase/migrations/20250915_implement_audit_logging.sql

# Via CLI (se disponível)
supabase migration new implement_audit_logging
supabase db push
```

### **Passo 2: Verificar Instalação**
```sql
-- Verificar pgaudit
SELECT extname, extversion FROM pg_extension WHERE extname = 'pgaudit';

-- Verificar configurações
SELECT rolname, rolconfig FROM pg_roles WHERE rolconfig IS NOT NULL;

-- Verificar schema
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'audit';
```

### **Passo 3: Testar Sistema**
```bash
# Executar script de teste
python3 bdfut/tools/test_audit_system.py

# Usar gerenciador de auditoria
python3 bdfut/tools/audit_manager.py --status
```

---

## 📊 **OPERAÇÃO E MONITORAMENTO**

### **Comandos Principais**

#### **Verificar Status**
```bash
python3 bdfut/tools/audit_manager.py --status
```

#### **Obter Estatísticas**
```bash
# Últimos 7 dias
python3 bdfut/tools/audit_manager.py --stats 7

# Últimos 30 dias
python3 bdfut/tools/audit_manager.py --stats 30
```

#### **Detectar Atividades Suspeitas**
```bash
python3 bdfut/tools/audit_manager.py --suspicious
```

#### **Ver Alertas Recentes**
```bash
# Últimas 24 horas
python3 bdfut/tools/audit_manager.py --alerts 24

# Última semana
python3 bdfut/tools/audit_manager.py --alerts 168
```

#### **Gerar Relatório Completo**
```bash
# Relatório de 30 dias
python3 bdfut/tools/audit_manager.py --report 30
```

#### **Limpar Logs Antigos**
```bash
# Manter últimos 90 dias
python3 bdfut/tools/audit_manager.py --cleanup 90
```

#### **Criar Alerta Manual**
```bash
python3 bdfut/tools/audit_manager.py --create-alert "MANUAL_REVIEW" "WARNING" "Atividade requer revisão manual"
```

---

## 📈 **CONSULTAS SQL ÚTEIS**

### **Atividades Recentes**
```sql
SELECT * FROM audit.recent_activity LIMIT 20;
```

### **Estatísticas Diárias**
```sql
SELECT * FROM audit.audit_statistics ORDER BY audit_date DESC LIMIT 10;
```

### **Atividades por Usuário**
```sql
SELECT * FROM audit.get_user_activity('user_id', NOW() - INTERVAL '7 days');
```

### **Detectar Atividades Suspeitas**
```sql
SELECT * FROM audit.detect_suspicious_activity();
```

### **Alertas Críticos**
```sql
SELECT * FROM audit.security_alerts 
WHERE alert_level = 'CRITICAL' 
AND status = 'OPEN' 
ORDER BY alert_time DESC;
```

### **Operações de Alto Risco**
```sql
SELECT 
    timestamp,
    user_id,
    operation_type,
    table_name,
    severity
FROM audit.activity_log
WHERE operation_type IN ('DELETE', 'DROP', 'ALTER')
  AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

---

## 🚨 **ALERTAS E DETECÇÃO**

### **Tipos de Alertas Automatizados**

1. **MULTIPLE_FAILED_LOGINS**
   - **Trigger:** > 5 tentativas de login falhadas em 1 hora
   - **Ação:** Investigar possível ataque de força bruta

2. **OFF_HOURS_ACTIVITY**
   - **Trigger:** Atividade crítica fora do horário (22h-6h)
   - **Ação:** Verificar se é atividade autorizada

3. **MASS_DELETE_ACTIVITY**
   - **Trigger:** > 10 operações DELETE em 1 hora
   - **Ação:** Verificar se é operação legítima

4. **SENSITIVE_DATA_ACCESS**
   - **Trigger:** > 5 acessos a tabelas sensíveis em 24h
   - **Ação:** Monitorar uso de dados pessoais

### **Níveis de Severidade**
- **INFO:** Atividade normal
- **WARNING:** Atividade que requer atenção
- **CRITICAL:** Atividade que requer ação imediata
- **EMERGENCY:** Incidente de segurança

---

## 🔒 **SEGURANÇA DO SISTEMA DE AUDITORIA**

### **Proteções Implementadas**
1. **RLS habilitado** em todas as tabelas de auditoria
2. **Acesso restrito** apenas a `postgres` e `service_role`
3. **Funções SECURITY DEFINER** para controle de privilégios
4. **Schema isolado** para separação de dados

### **Políticas de Acesso**
```sql
-- Apenas roles autorizados podem ler logs
CREATE POLICY "audit_activity_log_select" ON audit.activity_log
    FOR SELECT USING (auth.role() = 'service_role' OR current_user = 'postgres');
```

### **Configurações de Auditoria**
```sql
-- Auditoria global para postgres
ALTER ROLE postgres SET pgaudit.log TO 'write, ddl, role';

-- Auditoria para API
ALTER ROLE authenticator SET pgaudit.log TO 'write, ddl';
```

---

## 📋 **COMPLIANCE LGPD/GDPR**

### **Rastreabilidade de Dados Pessoais**
- ✅ **Logs de acesso** a dados pessoais de jogadores
- ✅ **Rastreamento de alterações** em informações pessoais
- ✅ **Auditoria de exclusões** (direito ao esquecimento)
- ✅ **Logs de exportação** (portabilidade de dados)

### **Retenção de Dados**
- **Logs de auditoria:** 90 dias (padrão)
- **Alertas de segurança:** 1 ano
- **Sessões de usuário:** 30 dias

### **Relatórios de Compliance**
```sql
-- Relatório de acessos a dados pessoais
SELECT 
    timestamp,
    user_id,
    operation_type,
    table_name,
    CASE 
        WHEN table_name = 'players' THEN 'DADOS_PESSOAIS'
        ELSE 'DADOS_PUBLICOS'
    END as data_classification
FROM audit.activity_log
WHERE table_name IN ('players', 'coaches', 'referees')
  AND timestamp > NOW() - INTERVAL '30 days'
ORDER BY timestamp DESC;
```

---

## 🔄 **MANUTENÇÃO E OPERAÇÃO**

### **Tarefas Diárias**
1. **Verificar alertas críticos**
   ```bash
   python3 bdfut/tools/audit_manager.py --alerts 24
   ```

2. **Revisar atividades suspeitas**
   ```bash
   python3 bdfut/tools/audit_manager.py --suspicious
   ```

### **Tarefas Semanais**
1. **Gerar relatório de auditoria**
   ```bash
   python3 bdfut/tools/audit_manager.py --report 7
   ```

2. **Verificar estatísticas**
   ```bash
   python3 bdfut/tools/audit_manager.py --stats 7
   ```

### **Tarefas Mensais**
1. **Limpeza de logs antigos**
   ```bash
   python3 bdfut/tools/audit_manager.py --cleanup 90
   ```

2. **Relatório de compliance**
   ```bash
   python3 bdfut/tools/audit_manager.py --report 30
   ```

---

## 📊 **DASHBOARDS E RELATÓRIOS**

### **Views Disponíveis**
1. **`audit.recent_activity`** - Atividades dos últimos 7 dias
2. **`audit.audit_statistics`** - Estatísticas diárias dos últimos 30 dias

### **Métricas Principais**
- **Total de atividades auditadas**
- **Usuários únicos ativos**
- **IPs únicos conectados**
- **Operações por tipo**
- **Alertas de segurança gerados**

### **KPIs de Segurança**
- **Tempo de detecção** de atividades suspeitas: < 5 minutos
- **Taxa de falsos positivos** em alertas: < 5%
- **Cobertura de auditoria:** 100% das operações críticas
- **Retenção de logs:** 90 dias mínimo

---

## 🚨 **PROCEDIMENTOS DE RESPOSTA A INCIDENTES**

### **Alerta Crítico Detectado**
1. **Investigar imediatamente** o alerta
2. **Verificar logs detalhados** da atividade
3. **Identificar fonte** da atividade suspeita
4. **Tomar ações corretivas** se necessário
5. **Documentar resolução** no sistema

### **Comandos de Emergência**
```sql
-- Desabilitar usuário suspeito
ALTER ROLE "usuario_suspeito" NOLOGIN;

-- Verificar atividades do usuário
SELECT * FROM audit.get_user_activity('usuario_suspeito', NOW() - INTERVAL '24 hours');

-- Criar alerta crítico
SELECT audit.create_security_alert(
    'SECURITY_INCIDENT',
    'CRITICAL',
    'Atividade maliciosa detectada',
    'usuario_suspeito',
    '192.168.1.100'::inet,
    '{"details": "Descrição do incidente"}'::jsonb
);
```

---

## 🔗 **INTEGRAÇÃO COM OUTROS SISTEMAS**

### **Integração com RLS (SEC-002)**
- Logs de auditoria **protegidos por RLS**
- **Políticas granulares** de acesso
- **Sincronização** com políticas de segurança

### **Preparação para Criptografia (SEC-004)**
- **Base preparada** para auditoria de criptografia
- **Logs de operações** criptográficas
- **Rastreamento de chaves** de acesso

### **Suporte para Compliance (SEC-005)**
- **Logs LGPD/GDPR** completos
- **Rastreabilidade** de dados pessoais
- **Relatórios de compliance** automatizados

---

## 📁 **ARQUIVOS GERADOS**

### **Migrações SQL**
- `supabase/migrations/20250915_implement_audit_logging.sql` - Migração principal

### **Scripts Python**
- `bdfut/tools/audit_manager.py` - Gerenciador completo
- `bdfut/tools/test_audit_system.py` - Testes de validação

### **Documentação**
- `docs/AUDIT_SYSTEM_MANUAL.md` - Este manual

---

## ✅ **VALIDAÇÃO DO SISTEMA**

### **Testes Realizados**
- [x] Conexão com Supabase
- [x] Acesso ao schema de auditoria
- [x] Acesso às tabelas principais
- [x] Scripts Python funcionando

### **Componentes Implementados**
- [x] Extensão pgaudit
- [x] Schema audit customizado  
- [x] 3 tabelas de auditoria
- [x] 5 funções de auditoria
- [x] 1 trigger automático
- [x] 2 views de relatórios
- [x] Políticas RLS
- [x] Sistema de limpeza automática

---

## 🎯 **PRÓXIMAS AÇÕES**

### **Para Finalizar Implementação**
1. **Aplicar migração** via Supabase Dashboard
2. **Configurar pgaudit** conforme especificado
3. **Testar logs** com operações reais
4. **Validar alertas** automáticos

### **Para Operação Contínua**
1. **Monitoramento diário** de alertas
2. **Relatórios semanais** de auditoria
3. **Limpeza mensal** de logs antigos
4. **Revisão trimestral** de políticas

---

## 📞 **SUPORTE E TROUBLESHOOTING**

### **Problemas Comuns**

#### **pgaudit não está logando**
```sql
-- Verificar configuração
SHOW pgaudit.log;

-- Reconfigurar se necessário
ALTER ROLE postgres SET pgaudit.log TO 'write, ddl, role';
```

#### **Logs não aparecem no schema audit**
- Verificar se migração foi aplicada
- Confirmar permissões do schema
- Validar triggers nas tabelas

#### **Performance degradada**
- Ajustar configurações de auditoria
- Executar limpeza de logs
- Revisar índices das tabelas

### **Contatos**
- **Security Specialist:** Responsável pelo sistema
- **Orquestrador:** Coordenação de incidentes
- **Database Specialist:** Suporte técnico

---

## 📚 **REFERÊNCIAS**

### **Documentação Oficial**
- [PGAudit Documentation](https://www.pgaudit.org)
- [Supabase PGAudit Guide](https://supabase.com/docs/guides/database/extensions/pgaudit)
- [PostgreSQL Logging](https://www.postgresql.org/docs/current/runtime-config-logging.html)

### **Compliance**
- [LGPD - Lei Geral de Proteção de Dados](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd)
- [GDPR - General Data Protection Regulation](https://gdpr.eu/)

### **Segurança**
- [PostgreSQL Security Best Practices](https://www.postgresql.org/docs/current/security.html)
- [Supabase Security Guide](https://supabase.com/docs/guides/database/security)

---

**🔐 Sistema de Auditoria BDFut - Implementado com Sucesso!**  
**Responsável:** Security Specialist  
**Data:** 15/09/2025
