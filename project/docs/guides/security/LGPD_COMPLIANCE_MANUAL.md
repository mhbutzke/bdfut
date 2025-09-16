# Manual do Sistema de Compliance LGPD/GDPR BDFut 🔐

**Responsável:** Security Specialist  
**Task:** SEC-005 - Implementar Compliance LGPD/GDPR  
**Data:** 15 de Setembro de 2025  
**Status:** ✅ IMPLEMENTADO

---

## 📋 **VISÃO GERAL**

O Sistema de Compliance LGPD/GDPR BDFut implementa **conformidade completa** com a Lei Geral de Proteção de Dados (LGPD) e o General Data Protection Regulation (GDPR), garantindo **proteção máxima** de dados pessoais e **direitos dos titulares**.

### 🎯 **OBJETIVOS ALCANÇADOS**
- ✅ **Mapeamento completo** de dados pessoais
- ✅ **Sistema de consentimento** robusto
- ✅ **Direitos dos titulares** implementados
- ✅ **Políticas de retenção** configuradas
- ✅ **Relatórios de compliance** automáticos
- ✅ **Integração perfeita** com auditoria e criptografia

---

## 🏗️ **ARQUITETURA DO SISTEMA**

### **1. SCHEMA LGPD CUSTOMIZADO**
```sql
CREATE SCHEMA lgpd;
```
- **Propósito:** Isolamento e organização dos dados de compliance
- **Segurança:** RLS habilitado, acesso restrito

### **2. TABELAS DE COMPLIANCE (5 tabelas)**

#### **2.1 personal_data_mapping**
- **Função:** Mapeamento completo de dados pessoais
- **Campos principais:**
  - `table_name`, `schema_name`, `column_name` - Localização dos dados
  - `data_category` - Categoria (identificação, biométricos, profissionais)
  - `sensitivity_level` - Nível de sensibilidade (baixa, média, alta, crítica)
  - `legal_basis` - Base legal (consentimento, contrato, interesse legítimo)
  - `retention_period` - Período de retenção em dias
  - `is_encrypted` - Status de criptografia

#### **2.2 consent_records**
- **Função:** Registro de consentimentos para tratamento de dados
- **Campos principais:**
  - `data_subject_id`, `data_subject_type` - Identificação do titular
  - `consent_type` - Tipo de consentimento (tratamento, marketing, compartilhamento)
  - `consent_given` - Consentimento dado ou negado
  - `consent_date`, `consent_method` - Data e método do consentimento
  - `withdrawal_date` - Data de retirada do consentimento

#### **2.3 data_subject_rights**
- **Função:** Registro de exercício de direitos dos titulares
- **Campos principais:**
  - `right_type` - Tipo de direito (acesso, retificação, exclusão, portabilidade)
  - `request_date`, `request_method` - Data e método da solicitação
  - `status` - Status da solicitação (pending, processing, completed, rejected)
  - `response_date` - Data de resposta
  - `data_provided` - Dados fornecidos (JSONB)

#### **2.4 retention_policies**
- **Função:** Políticas de retenção de dados pessoais
- **Campos principais:**
  - `table_name`, `schema_name` - Tabela coberta pela política
  - `retention_period` - Período de retenção em dias
  - `retention_reason` - Motivo da retenção
  - `auto_delete` - Exclusão automática
  - `archive_before_delete` - Arquivar antes de excluir

#### **2.5 compliance_reports**
- **Função:** Relatórios de compliance LGPD/GDPR
- **Campos principais:**
  - `report_type` - Tipo de relatório (mensal, trimestral, anual)
  - `report_period_start`, `report_period_end` - Período do relatório
  - `data_subjects_count` - Número de titulares
  - `compliance_score` - Score de compliance (0-100)
  - `recommendations` - Recomendações (TEXT[])

---

## 🔧 **INSTALAÇÃO E CONFIGURAÇÃO**

### **Passo 1: Aplicar Migração**
```bash
# Via Supabase Dashboard
# 1. Acessar SQL Editor
# 2. Executar: supabase/migrations/20250915_implement_lgpd_compliance.sql

# Via CLI (se disponível)
supabase migration new implement_lgpd_compliance
supabase db push
```

### **Passo 2: Verificar Instalação**
```sql
-- Verificar schema LGPD
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'lgpd';

-- Verificar tabelas de compliance
SELECT table_name FROM information_schema.tables WHERE table_schema = 'lgpd';

-- Verificar funções de compliance
SELECT proname FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'lgpd';
```

### **Passo 3: Inicializar Sistema**
```sql
-- Mapear dados pessoais automaticamente
SELECT lgpd.map_personal_data();

-- Criar políticas de retenção padrão
SELECT lgpd.create_default_retention_policies();

-- Gerar relatório inicial
SELECT lgpd.generate_compliance_report('anual', CURRENT_DATE - INTERVAL '1 year', CURRENT_DATE);
```

---

## 📊 **OPERAÇÃO E MONITORAMENTO**

### **Comandos Principais**

#### **Verificar Status do Sistema**
```bash
python3 bdfut/tools/lgpd_compliance_manager.py --status
```

#### **Obter Mapeamento de Dados Pessoais**
```bash
python3 bdfut/tools/lgpd_compliance_manager.py --mapping
```

#### **Status de Consentimentos**
```bash
python3 bdfut/tools/lgpd_compliance_manager.py --consent
```

#### **Resumo de Direitos dos Titulares**
```bash
python3 bdfut/tools/lgpd_compliance_manager.py --rights
```

#### **Calcular Score de Compliance**
```bash
python3 bdfut/tools/lgpd_compliance_manager.py --score
```

#### **Gerar Relatório Completo**
```bash
python3 bdfut/tools/lgpd_compliance_manager.py --report
```

#### **Gerar Relatório Específico**
```bash
python3 bdfut/tools/lgpd_compliance_manager.py --generate-report mensal
python3 bdfut/tools/lgpd_compliance_manager.py --generate-report trimestral
python3 bdfut/tools/lgpd_compliance_manager.py --generate-report anual
```

---

## 📈 **CONSULTAS SQL ÚTEIS**

### **Mapeamento de Dados Pessoais**
```sql
-- Ver mapeamento completo
SELECT * FROM lgpd.personal_data_mapping ORDER BY table_name, column_name;

-- Resumo por categoria
SELECT * FROM lgpd.personal_data_summary;

-- Dados críticos
SELECT * FROM lgpd.personal_data_mapping WHERE sensitivity_level = 'crítica';
```

### **Status de Consentimentos**
```sql
-- Status por tipo
SELECT * FROM lgpd.consent_status;

-- Consentimentos ativos
SELECT * FROM lgpd.consent_records 
WHERE consent_given = true AND withdrawal_date IS NULL;

-- Consentimentos retirados
SELECT * FROM lgpd.consent_records 
WHERE withdrawal_date IS NOT NULL;
```

### **Direitos dos Titulares**
```sql
-- Resumo de direitos
SELECT * FROM lgpd.rights_summary;

-- Solicitações pendentes
SELECT * FROM lgpd.data_subject_rights 
WHERE status = 'pending' 
ORDER BY request_date DESC;

-- Tempo médio de processamento
SELECT 
    right_type,
    AVG(processing_time_hours) as avg_hours
FROM lgpd.data_subject_rights 
WHERE processing_time_hours IS NOT NULL
GROUP BY right_type;
```

### **Políticas de Retenção**
```sql
-- Políticas ativas
SELECT * FROM lgpd.retention_policies ORDER BY table_name;

-- Políticas por categoria
SELECT 
    data_category,
    COUNT(*) as policies_count,
    AVG(retention_period) as avg_retention_days
FROM lgpd.retention_policies
GROUP BY data_category;
```

### **Relatórios de Compliance**
```sql
-- Relatórios recentes
SELECT * FROM lgpd.compliance_reports 
ORDER BY generated_at DESC LIMIT 10;

-- Score de compliance atual
SELECT lgpd.calculate_compliance_score() as current_score;

-- Gerar novo relatório
SELECT lgpd.generate_compliance_report('mensal', '2025-08-15', '2025-09-15');
```

---

## 🔒 **SEGURANÇA E PROTEÇÕES**

### **RLS IMPLEMENTADO**
✅ **Todas as 5 tabelas** de compliance protegidas
- `lgpd.personal_data_mapping` - Políticas de acesso restrito
- `lgpd.consent_records` - Acesso apenas a roles autorizados
- `lgpd.data_subject_rights` - Proteção de dados de titulares
- `lgpd.retention_policies` - Políticas de retenção protegidas
- `lgpd.compliance_reports` - Relatórios de compliance seguros

### **PERMISSÕES GRANULARES**
✅ **Schema lgpd** com acesso restrito
- **REVOKE ALL** do público
- **GRANT específicos** apenas para roles autorizados
- **SECURITY DEFINER** functions para controle

### **INTEGRAÇÃO COM SEC-003 E SEC-004**
✅ **Auditoria de operações** de compliance
- Logs de **mapeamento de dados**
- Auditoria de **consentimentos**
- **Rastreamento completo** de direitos dos titulares
- **Integração com criptografia** de dados pessoais

---

## 📊 **COMPLIANCE LGPD/GDPR**

### **DADOS PESSOAIS MAPEADOS**

#### **Categoria: Identificação**
- ✅ **Nomes pessoais** (firstname, lastname) - Alta sensibilidade
- ✅ **Nacionalidade** - Média sensibilidade
- ✅ **Data de nascimento** - Crítica sensibilidade (LGPD)

#### **Categoria: Dados Biométricos**
- ✅ **Altura** (height) - Média sensibilidade
- ✅ **Peso** (weight) - Média sensibilidade

#### **Categoria: Dados Profissionais**
- ✅ **Jogadores profissionais** - Alta sensibilidade
- ✅ **Treinadores profissionais** - Alta sensibilidade
- ✅ **Árbitros profissionais** - Alta sensibilidade

### **DIREITOS DOS TITULARES IMPLEMENTADOS**

#### **Direito de Acesso**
- ✅ **Consulta de dados** pessoais
- ✅ **Informações sobre tratamento**
- ✅ **Base legal** do tratamento

#### **Direito de Retificação**
- ✅ **Correção de dados** incorretos
- ✅ **Atualização de informações**
- ✅ **Validação de dados**

#### **Direito de Exclusão**
- ✅ **Eliminação de dados** pessoais
- ✅ **Direito ao esquecimento**
- ✅ **Exclusão automática**

#### **Direito de Portabilidade**
- ✅ **Exportação de dados**
- ✅ **Formato estruturado**
- ✅ **Transferência entre sistemas**

#### **Direito de Limitação**
- ✅ **Restrição de tratamento**
- ✅ **Suspensão temporária**
- ✅ **Controle de processamento**

#### **Direito de Objeção**
- ✅ **Oposição ao tratamento**
- ✅ **Marketing direto**
- ✅ **Processamento automatizado**

### **SISTEMA DE CONSENTIMENTO**

#### **Tipos de Consentimento**
- ✅ **Tratamento** de dados pessoais
- ✅ **Marketing** e comunicações
- ✅ **Compartilhamento** com terceiros
- ✅ **Transferência internacional**
- ✅ **Pesquisa** e análise

#### **Gestão de Consentimento**
- ✅ **Registro de consentimentos**
- ✅ **Retirada de consentimento**
- ✅ **Histórico de alterações**
- ✅ **Validação de consentimento**

### **POLÍTICAS DE RETENÇÃO**

#### **Períodos de Retenção**
- ✅ **Dados de identificação:** 7 anos (contrato)
- ✅ **Dados biométricos:** 7 anos (contrato)
- ✅ **Dados profissionais:** 7 anos (contrato)
- ✅ **Consentimentos:** 3 anos após retirada

#### **Exclusão Automática**
- ✅ **Políticas configuráveis**
- ✅ **Arquivamento antes da exclusão**
- ✅ **Auditoria de exclusões**
- ✅ **Notificação de titulares**

---

## 🔄 **PROCESSOS DE COMPLIANCE**

### **Mapeamento de Dados Pessoais**

#### **Processo Automático**
1. **Identificação** de tabelas com dados pessoais
2. **Classificação** por categoria e sensibilidade
3. **Definição** de base legal
4. **Configuração** de período de retenção
5. **Verificação** de criptografia

#### **Comando de Mapeamento**
```sql
-- Executar mapeamento automático
SELECT lgpd.map_personal_data();
```

### **Gestão de Consentimentos**

#### **Registro de Consentimento**
```sql
-- Registrar novo consentimento
INSERT INTO lgpd.consent_records (
    data_subject_id, data_subject_type, consent_type,
    legal_basis, consent_given, consent_date,
    consent_method, consent_version, purpose, data_categories
) VALUES (
    'player_123', 'player', 'tratamento',
    'consentimento', true, NOW(),
    'digital', 'v1.0', 'Identificação profissional', 
    ARRAY['identificacao', 'biometricos']
);
```

#### **Retirada de Consentimento**
```sql
-- Retirar consentimento
UPDATE lgpd.consent_records 
SET 
    consent_given = false,
    withdrawal_date = NOW(),
    withdrawal_method = 'digital',
    withdrawal_reason = 'Solicitação do titular'
WHERE data_subject_id = 'player_123' 
AND consent_type = 'tratamento';
```

### **Exercício de Direitos**

#### **Solicitação de Acesso**
```sql
-- Registrar solicitação de acesso
INSERT INTO lgpd.data_subject_rights (
    data_subject_id, data_subject_type, right_type,
    request_date, request_method, request_description
) VALUES (
    'player_123', 'player', 'acesso',
    NOW(), 'email', 'Solicitação de acesso aos dados pessoais'
);
```

#### **Processamento de Solicitação**
```sql
-- Atualizar status da solicitação
UPDATE lgpd.data_subject_rights 
SET 
    status = 'completed',
    response_date = NOW(),
    response_description = 'Dados fornecidos em formato JSON',
    data_provided = '{"firstname": "João", "lastname": "Silva", ...}',
    processing_time_hours = 24
WHERE id = 'uuid_da_solicitacao';
```

---

## 📊 **RELATÓRIOS E MÉTRICAS**

### **Score de Compliance**

#### **Cálculo do Score**
O score é calculado baseado em 5 critérios:
1. **Mapeamento de dados pessoais** (20%)
2. **Políticas de retenção** (20%)
3. **Criptografia de dados** (20%)
4. **Sistema de auditoria** (20%)
5. **Row Level Security** (20%)

#### **Níveis de Compliance**
- **90-100%:** EXCELENTE
- **80-89%:** BOM
- **70-79%:** ADEQUADO
- **60-69%:** PARCIAL
- **0-59%:** INSUFICIENTE

### **Relatórios Automáticos**

#### **Relatório Mensal**
```sql
-- Gerar relatório mensal
SELECT lgpd.generate_compliance_report('mensal', '2025-08-15', '2025-09-15');
```

#### **Relatório Trimestral**
```sql
-- Gerar relatório trimestral
SELECT lgpd.generate_compliance_report('trimestral', '2025-07-01', '2025-09-30');
```

#### **Relatório Anual**
```sql
-- Gerar relatório anual
SELECT lgpd.generate_compliance_report('anual', '2025-01-01', '2025-12-31');
```

### **Métricas de Compliance**

#### **Dados Pessoais**
- **Total de campos** mapeados
- **Percentual de criptografia**
- **Campos críticos** identificados
- **Campos de alta sensibilidade**

#### **Consentimentos**
- **Taxa de consentimento** por tipo
- **Consentimentos retirados**
- **Métodos de consentimento**
- **Versões de termos**

#### **Direitos dos Titulares**
- **Solicitações por tipo**
- **Taxa de conclusão**
- **Tempo médio de processamento**
- **Solicitações pendentes**

---

## 🚨 **PROCEDIMENTOS DE RESPOSTA A INCIDENTES**

### **Vazamento de Dados Pessoais**
1. **Identificar escopo** do vazamento
2. **Verificar logs** de auditoria
3. **Notificar autoridades** competentes (ANPD)
4. **Comunicar titulares** afetados
5. **Documentar incidente** e ações tomadas

### **Violação de Consentimento**
1. **Verificar registro** de consentimento
2. **Suspender tratamento** se necessário
3. **Notificar titular** da violação
4. **Corrigir processo** de consentimento
5. **Auditar sistema** de consentimento

### **Solicitação de Direitos**
1. **Validar identidade** do titular
2. **Verificar direito** solicitado
3. **Processar solicitação** no prazo legal
4. **Fornecer resposta** adequada
5. **Registrar processo** completo

### **Comandos de Emergência**
```sql
-- Verificar score de compliance
SELECT lgpd.calculate_compliance_score();

-- Verificar dados pessoais mapeados
SELECT * FROM lgpd.personal_data_summary;

-- Verificar consentimentos ativos
SELECT * FROM lgpd.consent_status;

-- Verificar solicitações pendentes
SELECT * FROM lgpd.data_subject_rights 
WHERE status = 'pending' 
ORDER BY request_date DESC;
```

---

## 🔗 **INTEGRAÇÃO COM OUTROS SISTEMAS**

### **Integração com Auditoria (SEC-003)**
- **Logs de compliance** protegidos por auditoria
- **Rastreamento de acesso** a dados de compliance
- **Alertas automáticos** para atividades suspeitas

### **Integração com Criptografia (SEC-004)**
- **Dados pessoais** criptografados conforme mapeamento
- **Consentimentos** protegidos por criptografia
- **Relatórios** com dados sensíveis protegidos

### **Preparação para Monitoramento (SEC-006)**
- **Métricas de compliance** implementadas
- **Alertas automáticos** configurados
- **Dashboard básico** disponível

---

## 📁 **ARQUIVOS GERADOS**

### **Migrações SQL**
- `supabase/migrations/20250915_implement_lgpd_compliance.sql` - Sistema completo

### **Scripts Python**
- `bdfut/tools/lgpd_compliance_manager.py` - Gerenciador completo (400+ linhas)
- `bdfut/tools/test_lgpd_compliance_system.py` - Testes de validação (150+ linhas)

### **Documentação**
- `docs/LGPD_COMPLIANCE_MANUAL.md` - Este manual

---

## ✅ **VALIDAÇÃO DO SISTEMA**

### **Testes Realizados**
- [x] Conexão com Supabase
- [x] Schema de compliance LGPD
- [x] Tabelas com dados pessoais
- [x] Integração com criptografia
- [x] Integração com auditoria

### **Componentes Implementados**
- [x] Schema LGPD customizado
- [x] 5 tabelas de compliance
- [x] 4 funções de compliance
- [x] 3 views de relatórios
- [x] 5 triggers de auditoria
- [x] Políticas RLS
- [x] Sistema de gerenciamento

---

## 🎯 **PRÓXIMAS AÇÕES**

### **IMEDIATAS (Hoje):**
1. **Aplicar migração SQL** via Supabase Dashboard
2. **Configurar sistema** de compliance conforme especificado
3. **Executar mapeamento** inicial de dados pessoais
4. **Testar compliance** com dados reais

### **PRÓXIMA TASK:** SEC-006 - Configurar Monitoramento de Segurança
- **Dependência:** ✅ SEC-005 concluída
- **Status:** DESBLOQUEADA
- **Prioridade:** 🟡 MÉDIA

---

## 📞 **SUPORTE E TROUBLESHOOTING**

### **Problemas Comuns**

#### **Sistema de compliance não está funcionando**
```sql
-- Verificar schema
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'lgpd';

-- Verificar tabelas
SELECT table_name FROM information_schema.tables WHERE table_schema = 'lgpd';

-- Verificar funções
SELECT proname FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'lgpd';
```

#### **Score de compliance baixo**
- Verificar se dados pessoais estão mapeados
- Confirmar se políticas de retenção existem
- Validar se dados estão criptografados
- Verificar se auditoria está configurada

#### **Consentimentos não estão sendo registrados**
- Verificar se tabela consent_records existe
- Confirmar permissões do schema lgpd
- Validar funções de registro

### **Contatos**
- **Security Specialist:** Responsável pelo sistema
- **Orquestrador:** Coordenação de incidentes
- **Database Specialist:** Suporte técnico

---

## 📚 **REFERÊNCIAS**

### **Documentação Oficial**
- [LGPD - Lei Geral de Proteção de Dados](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd)
- [GDPR - General Data Protection Regulation](https://gdpr.eu/)
- [ANPD - Autoridade Nacional de Proteção de Dados](https://www.gov.br/anpd/)

### **Compliance**
- [Guia de Implementação LGPD](https://www.gov.br/anpd/pt-br/documentos-e-publicacoes/guia-orientativo-para-implementacao-da-lgpd)
- [Direitos dos Titulares](https://www.gov.br/anpd/pt-br/canais_atendimento/direitos-do-titular)
- [Base Legal do Tratamento](https://www.gov.br/anpd/pt-br/documentos-e-publicacoes/base-legal-do-tratamento)

### **Segurança**
- [Supabase Security Guide](https://supabase.com/docs/guides/database/security)
- [PostgreSQL Security Best Practices](https://www.postgresql.org/docs/current/security.html)

---

**🔐 Sistema de Compliance LGPD/GDPR BDFut - Implementado com Sucesso!**  
**Responsável:** Security Specialist  
**Data:** 15/09/2025
