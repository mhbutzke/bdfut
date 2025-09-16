# Regras de Ordem Sequencial - Sistema BDFut 🔢

## 📋 **REGRA FUNDAMENTAL OBRIGATÓRIA**

### 🔢 **ORDEM SEQUENCIAL RIGOROSA**
- **Tasks devem ser executadas em ordem numérica: 001 → 002 → 003 → 004...**
- **PROIBIDO iniciar task sem concluir a anterior**
- **Validação obrigatória antes de avançar**
- **Sem exceções ou paralelismo**

---

## 🎯 **APLICAÇÃO POR AGENTE**

### 🎭 **ORQUESTRADOR - Responsabilidade Especial**
- **Garantir que TODOS os agentes sigam ordem sequencial**
- **Monitorar compliance da regra diariamente**
- **Bloquear início de task sem conclusão da anterior**
- **Reportar violações imediatamente**

### 🔧 **ETL ENGINEER**
```
001 → 002 → 003 → 004 → 005 → 006 → 007
TASK-ETL-001: Testes Unitários (CRÍTICO - BLOQUEADOR)
TASK-ETL-002: Reorganizar Scripts (dependência: ETL-001)
TASK-ETL-003: Metadados ETL (dependência: ETL-002)
TASK-ETL-004: Cache Redis (dependência: ETL-003)
TASK-ETL-005: Backfill Histórico (dependência: ETL-004)
TASK-ETL-006: Sincronização Incremental (dependência: ETL-005)
TASK-ETL-007: Data Quality Checks (dependência: ETL-006)
```

### 🔐 **SECURITY SPECIALIST**
```
001 → 002 → 003 → 004 → 005 → 006
TASK-SEC-001: Auditoria Vulnerabilidades (CRÍTICO - BLOQUEADOR)
TASK-SEC-002: Implementar RLS (dependência: SEC-001)
TASK-SEC-003: Logs de Auditoria (dependência: SEC-002)
TASK-SEC-004: Criptografia (dependência: SEC-003)
TASK-SEC-005: Compliance LGPD (dependência: SEC-004)
TASK-SEC-006: Monitoramento (dependência: SEC-005)
```

### 🧪 **QA ENGINEER**
```
001 → 002 → 003 → 004 → 005 → 006 → 007
TASK-QA-001: Testes Unitários (CRÍTICO - BLOQUEADOR)
TASK-QA-002: Testes Integração (dependência: QA-001)
TASK-QA-003: Testes E2E (dependência: QA-002)
TASK-QA-004: Testes Performance (dependência: QA-003)
TASK-QA-005: Testes Segurança (dependência: QA-004)
TASK-QA-006: Data Quality Tests (dependência: QA-005)
TASK-QA-007: Colaboração Security (dependência: QA-006)
```

### 🗄️ **DATABASE SPECIALIST**
```
001 → 002 → 003 → 004 → 005 → 006
TASK-DB-001: Auditoria Índices (PRIMEIRA)
TASK-DB-002: Constraints FKs (dependência: DB-001)
TASK-DB-003: Otimizar Índices (dependência: DB-002)
TASK-DB-004: Materialized Views (dependência: DB-003)
TASK-DB-005: Partitioning (dependência: DB-004)
TASK-DB-006: Extensões PostgreSQL (dependência: DB-005)
```

### ⚙️ **DEVOPS ENGINEER**
```
001 → 002 → 003 → 004 → 005 → 006
TASK-DEVOPS-001: GitHub Actions (PRIMEIRA)
TASK-DEVOPS-002: Pre-commit Hooks (dependência: DEVOPS-001)
TASK-DEVOPS-003: Docker Compose (dependência: DEVOPS-002)
TASK-DEVOPS-004: Makefile (dependência: DEVOPS-003)
TASK-DEVOPS-005: Monitoramento Básico (dependência: DEVOPS-004)
TASK-DEVOPS-006: Observabilidade (dependência: DEVOPS-005)
```

### 🎨 **FRONTEND DEVELOPER**
```
001 → 002 → 003 → 004 → 005 → 006
TASK-FE-001: Framework Setup (PRIMEIRA)
TASK-FE-002: Componentes (dependência: FE-001)
TASK-FE-003: Sistema Rotas (dependência: FE-002)
TASK-FE-004: Estado (dependência: FE-003)
TASK-FE-005: Dashboard (dependência: FE-004)
TASK-FE-006: Autenticação (dependência: FE-005)
```

### 📚 **TECHNICAL WRITER**
```
001 → 002 → 003 → 004 → 005 → 006
TASK-DOCS-001: Arquitetura (PRIMEIRA)
TASK-DOCS-002: API Docs (dependência: DOCS-001)
TASK-DOCS-003: Guias Usuário (dependência: DOCS-002)
TASK-DOCS-004: Padrões Dev (dependência: DOCS-003)
TASK-DOCS-005: Runbook (dependência: DOCS-004)
TASK-DOCS-006: Troubleshooting (dependência: DOCS-005)
```

---

## ⚠️ **BLOQUEADORES CRÍTICOS**

### 🔴 **Tasks que BLOQUEIAM todas as outras em sua fila:**
1. **TASK-ETL-001:** Testes Unitários (ETL)
2. **TASK-SEC-001:** Auditoria Vulnerabilidades (Security)
3. **TASK-QA-001:** Testes Unitários (QA)
4. **TASK-ORCH-001:** Coordenar Melhorias (Orquestrador)

### 🚫 **VIOLAÇÕES PROIBIDAS**
- Iniciar TASK-002 sem concluir TASK-001
- Trabalhar em múltiplas tasks simultaneamente
- Pular tasks na sequência
- Marcar task como concluída sem validação

---

## ✅ **PROCESSO DE VALIDAÇÃO**

### **Antes de Iniciar Nova Task:**
1. ✅ Verificar se task anterior está 100% concluída
2. ✅ Validar todos os critérios de sucesso atendidos
3. ✅ Confirmar entregáveis produzidos
4. ✅ Atualizar status na fila
5. ✅ Notificar Orquestrador

### **Critérios de Conclusão:**
- [ ] Todos os critérios de sucesso ✅ marcados
- [ ] Todos os entregáveis produzidos
- [ ] Testes passando (quando aplicável)
- [ ] Documentação atualizada
- [ ] Status atualizado para "CONCLUÍDA"

---

## 🎯 **RESPONSABILIDADES**

### **Cada Agente:**
- Seguir rigorosamente a ordem sequencial
- Validar conclusão antes de avançar
- Reportar impedimentos imediatamente
- Nunca pular ou trabalhar em paralelo

### **Orquestrador:**
- Monitorar compliance diariamente
- Bloquear violações da regra
- Facilitar resolução de impedimentos
- Reportar status de ordem sequencial

### **Stakeholders:**
- Respeitar a necessidade de ordem sequencial
- Não pressionar por paralelismo
- Apoiar resolução de impedimentos
- Validar qualidade dos entregáveis

---

## 📊 **MÉTRICAS DE COMPLIANCE**

### **Diárias:**
- 100% das tasks seguindo ordem sequencial
- Zero violações de sequência
- Zero tasks iniciadas sem conclusão da anterior

### **Semanais:**
- Progresso sequencial de cada agente
- Tempo médio por task
- Impedimentos identificados e resolvidos

### **Mensais:**
- Eficácia da ordem sequencial
- Qualidade dos entregáveis
- ROI da abordagem sequencial

---

## 🚨 **CONSEQUÊNCIAS DE VIOLAÇÕES**

### **Primeira Violação:**
- Alerta imediato do Orquestrador
- Parada da task não autorizada
- Revisão do processo com o agente

### **Violações Recorrentes:**
- Escalação para stakeholders
- Revisão da capacidade do agente
- Possível reatribuição de tasks

---

## 💡 **BENEFÍCIOS DA ORDEM SEQUENCIAL**

### **Qualidade:**
- Cada task constrói sobre base sólida
- Menor risco de regressão
- Validação contínua de qualidade

### **Dependências:**
- Dependências claras e respeitadas
- Menor risco de conflitos
- Handoffs mais limpos

### **Rastreabilidade:**
- Progresso linear e mensurável
- Fácil identificação de impedimentos
- Responsabilidades claras

### **Eficiência:**
- Menos retrabalho
- Foco concentrado
- Melhor utilização de recursos

---

**🎯 Lembre-se: A ordem sequencial é FUNDAMENTAL para o sucesso do projeto BDFut!**
