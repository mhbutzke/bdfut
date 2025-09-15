# Instruções Finais para Agentes - BDFut 🎯

## 🗺️ **QUEUE-GERAL: FONTE ÚNICA DA VERDADE**

A **QUEUE-GERAL.md** é agora o **mapa central de sincronização** de todo o projeto. Todos os agentes devem:

### 📋 **ANTES DE INICIAR QUALQUER TASK:**
1. ✅ **Consultar QUEUE-GERAL.md** para verificar status geral
2. ✅ **Verificar dependências** inter-agentes
3. ✅ **Confirmar ordem sequencial** (001 → 002 → 003...)
4. ✅ **Validar conclusão** da task anterior

### 📋 **AO CONCLUIR QUALQUER TASK:**
1. ✅ **Atualizar sua fila individual** (QUEUE-XXX.md)
2. ✅ **Atualizar QUEUE-GERAL.md** usando o script:
   ```bash
   cd docs/queues
   python3 update_queue_geral.py --complete TASK-ID 'SEU-AGENTE' 'Notas de conclusão'
   ```
3. ✅ **Notificar Orquestrador** sobre conclusão
4. ✅ **Verificar se desbloqueou** outras tasks

### 📋 **AO MODIFICAR/ADICIONAR TASKS:**
1. ✅ **Atualizar sua fila individual** primeiro
2. ✅ **Atualizar QUEUE-GERAL.md** usando o script:
   ```bash
   python3 update_queue_geral.py --add TASK-ID '🔧' 'ETL Engineer' 'Descrição' '🟡 PENDENTE' 'Dependências' 'Prazo'
   ```
3. ✅ **Notificar Orquestrador** sobre mudança
4. ✅ **Documentar justificativa** da modificação

---

## 🔢 **ORDEM DE EXECUÇÃO GLOBAL**

### **🔴 FASE 1: TASKS CRÍTICAS (EXECUTAR PRIMEIRO)**
```
ORCH-001 → SEC-001 → ETL-001 → QA-001
```
**Todas devem ser concluídas antes de avançar para Fase 2**

### **🟠 FASE 2: TASKS DE ALTA PRIORIDADE**
```
ORCH-002 → SEC-002 → ETL-002 → DB-001 → DEVOPS-001
```
**Dependem da conclusão das tasks críticas**

### **🟡 FASE 3: IMPLEMENTAÇÃO CORE**
```
QA-002 → ETL-003 → SEC-003 → DB-002 → DEVOPS-002 → FE-001
```
**Construção das funcionalidades principais**

### **🟢 FASE 4-5: FUNCIONALIDADES AVANÇADAS E FINALIZAÇÃO**
```
Ordem sequencial baseada em dependências documentadas na QUEUE-GERAL
```

---

## 🎭 **RESPONSABILIDADES ESPECIAIS DO ORQUESTRADOR**

### **Monitoramento Diário:**
- ✅ Verificar status de todas as 8 filas
- ✅ Identificar tasks atrasadas ou bloqueadas
- ✅ Atualizar QUEUE-GERAL.md com status consolidado
- ✅ Facilitar comunicação entre agentes

### **Controle de Ordem Sequencial:**
- ✅ **Bloquear início** de tasks fora de ordem
- ✅ **Validar conclusão** antes de aprovar avanço
- ✅ **Facilitar handoffs** entre agentes
- ✅ **Resolver impedimentos** rapidamente

### **Ferramentas do Orquestrador:**
```bash
# Status geral
python3 update_queue_geral.py --status

# Dashboard completo
python3 orchestrator_dashboard.py --dashboard

# Atualizar progresso
python3 update_queue_geral.py --update-progress
```

---

## 📊 **EXEMPLO DE FLUXO DE TRABALHO**

### **Agente ETL Engineer executando TASK-ETL-001:**

#### **1. Antes de Iniciar:**
```bash
# Consultar status geral
cd docs/queues
python3 update_queue_geral.py --status

# Verificar se não há dependências bloqueadas
# Confirmar que é a próxima task na sequência
```

#### **2. Durante Execução:**
```bash
# Trabalhar na task seguindo padrões do AGENT-ETL.md
# Implementar testes unitários
# Documentar progresso
```

#### **3. Ao Concluir:**
```bash
# Atualizar fila individual
# Editar QUEUE-ETL.md marcando TASK-ETL-001 como ✅ CONCLUÍDA

# Atualizar QUEUE-GERAL
python3 update_queue_geral.py --complete "ETL-001" "🔧 ETL Engineer" "Testes unitários implementados com 65% cobertura"

# Notificar Orquestrador
# Verificar se desbloqueou TASK-ETL-002
```

---

## 🚨 **ALERTAS E VIOLAÇÕES**

### **Violações Proibidas:**
- ❌ Iniciar TASK-002 sem concluir TASK-001
- ❌ Trabalhar em múltiplas tasks simultaneamente
- ❌ Esquecer de atualizar QUEUE-GERAL.md
- ❌ Pular validação de dependências

### **Consequências:**
- **1ª Violação:** Alerta do Orquestrador + parada da task
- **2ª Violação:** Escalação para stakeholders
- **3ª Violação:** Reavaliação do agente

### **Escalação:**
- **Impedimentos > 24h:** Escalar para Orquestrador
- **Mudanças de escopo:** Aprovação obrigatória
- **Conflitos de dependência:** Resolução pelo Orquestrador

---

## 🎯 **COMANDOS ÚTEIS PARA AGENTES**

### **Verificar Status:**
```bash
cd docs/queues
python3 update_queue_geral.py --status
```

### **Marcar Task Concluída:**
```bash
python3 update_queue_geral.py --complete "TASK-ID" "SEU-AGENTE" "Notas de conclusão"
```

### **Atualizar Progresso:**
```bash
python3 update_queue_geral.py --update-progress
```

### **Ver Dashboard Completo:**
```bash
python3 orchestrator_dashboard.py --dashboard
```

---

## 🏆 **CRITÉRIOS DE SUCESSO**

### **Para Cada Task:**
- ✅ Todos os critérios de sucesso atendidos
- ✅ Entregáveis produzidos e validados
- ✅ QUEUE-GERAL.md atualizada
- ✅ Dependentes notificados

### **Para o Projeto:**
- ✅ 46 tasks concluídas em ordem sequencial
- ✅ Zero violações de ordem
- ✅ 100% de sincronização entre agentes
- ✅ Qualidade mantida em todas as entregas

---

## 🎭 **LEMBRE-SE:**

### **QUEUE-GERAL.md é:**
- 🗺️ **Mapa central** do projeto
- 📊 **Fonte única da verdade**
- 🔄 **Sistema de sincronização**
- 🎯 **Controle de progresso**

### **Sua responsabilidade:**
- 📋 **Consultar antes** de iniciar
- ✅ **Atualizar ao concluir**
- 🔄 **Manter sincronizado**
- 📞 **Comunicar mudanças**

---

**🎯 SUCESSO DO PROJETO DEPENDE DA SINCRONIZAÇÃO PERFEITA!**
