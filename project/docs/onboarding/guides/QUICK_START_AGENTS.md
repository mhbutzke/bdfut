# Quick Start para Agentes - BDFut ⚡

## 🚀 **INÍCIO RÁPIDO EM 5 MINUTOS**

### **📋 PASSO 1: Leia os 3 Arquivos Obrigatórios (3 minutos)**
1. **`docs/queues/QUEUE-GERAL.md`** - Mapa central do projeto
2. **`docs/queues/SEQUENTIAL_ORDER_RULES.md`** - Regras de ordem
3. **`docs/queues/AGENT_INSTRUCTIONS_FINAL.md`** - Como trabalhar

### **📋 PASSO 2: Conheça Seu Perfil (2 minutos)**
1. **`docs/agents/AGENT-SEU-CODIGO.md`** - Seu perfil específico
2. **`docs/queues/QUEUE-SEU-CODIGO.md`** - Suas tasks

---

## 🎯 **REGRA ÚNICA QUE VOCÊ PRECISA SABER**

### **🔢 ORDEM SEQUENCIAL OBRIGATÓRIA:**
- **Sempre execute: 001 → 002 → 003 → 004...**
- **NUNCA pule a ordem**
- **NUNCA inicie task sem concluir anterior**
- **SEMPRE atualize QUEUE-GERAL.md ao concluir**

---

## ⚡ **COMANDOS ESSENCIAIS**

### **Antes de Trabalhar:**
```bash
cd docs/queues
python3 update_queue_geral.py --status
```

### **Ao Concluir Task:**
```bash
python3 update_queue_geral.py --complete "TASK-ID" "SEU-AGENTE" "Notas"
```

### **Ver Sua Fila:**
```bash
python3 manage_queues.py --agent SEU-CODIGO
```

---

## 🎭 **AGENTES E SEUS CÓDIGOS**

| Agente | Código | Primeira Task |
|--------|--------|---------------|
| 🎭 Orquestrador | ORCH | ORCH-001 |
| 🔐 Security | SECURITY | SEC-001 |
| 🔧 ETL Engineer | ETL | ETL-001 |
| 🧪 QA Engineer | QA | QA-001 |
| 🗄️ Database | DATABASE | DB-001 |
| ⚙️ DevOps | DEVOPS | DEVOPS-001 |
| 🎨 Frontend | FRONTEND | FE-001 |
| 📚 Technical Writer | DOCS | DOCS-001 |

---

## 🔴 **TASKS CRÍTICAS IMEDIATAS**

### **Executar HOJE (em paralelo):**
1. **ORCH-001** (🎭 Orquestrador): Coordenar melhorias
2. **SEC-001** (🔐 Security): Auditoria vulnerabilidades
3. **ETL-001** (🔧 ETL): Implementar testes unitários
4. **QA-001** (🧪 QA): Implementar testes unitários

---

## 📞 **SUPORTE**

### **Dúvidas sobre:**
- **Ordem de execução:** Ver SEQUENTIAL_ORDER_RULES.md
- **Como atualizar:** Ver AGENT_INSTRUCTIONS_FINAL.md
- **Status geral:** Executar `python3 update_queue_geral.py --status`
- **Impedimentos:** Escalar para 🎭 Orquestrador

---

**🎯 VOCÊ ESTÁ PRONTO PARA COMEÇAR! Boa sorte! 🚀**
