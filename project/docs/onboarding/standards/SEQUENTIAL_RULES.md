# Regras de Ordem Sequencial - OBRIGATÓRIO 🔢

## ⚠️ **REGRA FUNDAMENTAL DO PROJETO**

### **🔢 ORDEM SEQUENCIAL OBRIGATÓRIA:**
- **Tasks devem ser executadas em ordem numérica: 001 → 002 → 003 → 004...**
- **PROIBIDO iniciar task sem concluir a anterior**
- **VALIDAÇÃO obrigatória antes de avançar**
- **SEM EXCEÇÕES ou paralelismo dentro do agente**

---

## 🚫 **VIOLAÇÕES PROIBIDAS**

### **❌ NUNCA FAÇA:**
- Iniciar TASK-002 sem concluir TASK-001
- Trabalhar em múltiplas tasks simultaneamente
- Pular tasks na sequência
- Marcar task como concluída sem validação
- Esquecer de atualizar QUEUE-GERAL.md

### **⚠️ CONSEQUÊNCIAS:**
- **1ª Violação:** Alerta do Orquestrador + parada da task
- **2ª Violação:** Escalação para stakeholders
- **3ª Violação:** Reavaliação do agente

---

## ✅ **PROCESSO DE VALIDAÇÃO**

### **Antes de Iniciar Nova Task:**
1. ✅ Verificar se task anterior está 100% concluída
2. ✅ Validar todos os critérios de sucesso atendidos
3. ✅ Confirmar entregáveis produzidos
4. ✅ Atualizar status na fila individual
5. ✅ Atualizar QUEUE-GERAL.md
6. ✅ Notificar conclusão

### **Critérios de Conclusão:**
- [ ] Todos os critérios de sucesso ✅ marcados
- [ ] Todos os entregáveis produzidos
- [ ] Testes passando (quando aplicável)
- [ ] Documentação atualizada
- [ ] Status atualizado para "✅ CONCLUÍDA"
- [ ] QUEUE-GERAL.md atualizada

---

## 🎯 **EXEMPLOS DE ORDEM CORRETA**

### **🔧 ETL Engineer:**
```
✅ TASK-ETL-001: Testes Unitários (CONCLUÍDA)
   ↓
🔄 TASK-ETL-002: Reorganizar Scripts (PODE INICIAR)
   ↓
⏸️ TASK-ETL-003: Metadados ETL (BLOQUEADA até ETL-002)
```

### **🎨 Frontend Developer:**
```
✅ TASK-FE-001: Framework (CONCLUÍDA)
   ↓
🔄 TASK-FE-002: Componentes (PODE INICIAR)
   ↓
⏸️ TASK-FE-003: Rotas (BLOQUEADA até FE-002)
```

---

## 📊 **DEPENDÊNCIAS INTER-AGENTES**

### **🤝 Algumas tasks dependem de outros agentes:**
- **FE-001** depende de **DEVOPS-001** ✅
- **QA-007** depende de **SEC-005** ✅
- **DOCS-001** depende de **ETL-003** ✅ e **DB-003** ✅

### **📋 Como verificar:**
1. Consultar **QUEUE-GERAL.md**
2. Verificar coluna "Dependências"
3. Confirmar se dependências estão ✅ CONCLUÍDAS

---

## 🎯 **RESPONSABILIDADES**

### **🎭 Orquestrador:**
- **Monitorar** compliance diariamente
- **Bloquear** violações da regra
- **Facilitar** resolução de impedimentos
- **Reportar** status de ordem sequencial

### **👤 Cada Agente:**
- **Seguir** rigorosamente a ordem sequencial
- **Validar** conclusão antes de avançar
- **Reportar** impedimentos imediatamente
- **Nunca** pular ou trabalhar em paralelo

### **📊 Stakeholders:**
- **Respeitar** necessidade de ordem sequencial
- **Não pressionar** por paralelismo
- **Apoiar** resolução de impedimentos

---

## 📈 **BENEFÍCIOS DA ORDEM SEQUENCIAL**

### **✅ Qualidade:**
- Cada task constrói sobre base sólida
- Menor risco de regressão
- Validação contínua

### **✅ Dependências:**
- Dependências claras e respeitadas
- Menor risco de conflitos
- Handoffs mais limpos

### **✅ Rastreabilidade:**
- Progresso linear e mensurável
- Fácil identificação de impedimentos
- Responsabilidades claras

---

## 🚨 **ALERTAS IMPORTANTES**

### **🔴 CRÍTICO:**
- **QUEUE-GERAL.md** é fonte única da verdade
- **Ordem sequencial** não é sugestão, é OBRIGATÓRIA
- **Violações** são registradas e monitoradas

### **📞 COMUNICAÇÃO:**
- **Impedimentos** devem ser reportados em 24h
- **Mudanças** precisam de aprovação
- **Dúvidas** devem ser esclarecidas antes de agir

---

## 🎯 **PRÓXIMO PASSO**

### **Agora que você entende as regras:**
1. **Localizar** sua fila específica
2. **Identificar** sua próxima task
3. **Verificar** dependências
4. **Iniciar** seguindo ordem sequencial

---

**🔢 Ordem sequencial é FUNDAMENTAL para o sucesso do projeto! Siga rigorosamente! 🎯**
