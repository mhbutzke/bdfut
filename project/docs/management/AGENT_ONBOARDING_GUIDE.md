# Guia de Onboarding para Agentes - BDFut 🎯

## 📋 **ARQUIVOS OBRIGATÓRIOS PARA TODOS OS AGENTES**

### **1. LEITURA OBRIGATÓRIA (ORDEM DE PRIORIDADE)**

#### **🗺️ PRIMEIRO - Mapa Central:**
- **`docs/queues/QUEUE-GERAL.md`** - **FONTE ÚNICA DA VERDADE**
  - Mapa central com todas as 46 tasks
  - Ordem de execução global
  - Dependências inter-agentes
  - Status de progresso consolidado

#### **🔢 SEGUNDO - Regras Fundamentais:**
- **`docs/queues/SEQUENTIAL_ORDER_RULES.md`** - **REGRAS DE ORDEM SEQUENCIAL**
  - Regra fundamental: 001 → 002 → 003...
  - Proibições e restrições
  - Processo de validação
  - Consequências de violações

#### **📋 TERCEIRO - Instruções de Trabalho:**
- **`docs/queues/AGENT_INSTRUCTIONS_FINAL.md`** - **COMO TRABALHAR**
  - Protocolo de início e conclusão de tasks
  - Comandos para atualizar QUEUE-GERAL
  - Exemplos de fluxo de trabalho
  - Ferramentas disponíveis

---

## 🎭 **ARQUIVOS ESPECÍFICOS POR AGENTE**

### **🎭 ORQUESTRADOR**
#### **Obrigatórios:**
1. **`docs/agents/AGENT-ORCH.md`** - Perfil e responsabilidades
2. **`docs/queues/QUEUE-ORCH.md`** - Sua fila de 9 tasks
3. **`docs/queues/ORCHESTRATOR_INSTRUCTIONS.md`** - Instruções específicas
4. **`docs/queues/orchestrator_dashboard.py`** - Dashboard especializado

#### **Ferramentas:**
```bash
# Dashboard do orquestrador
python3 orchestrator_dashboard.py --dashboard

# Status geral
python3 update_queue_geral.py --status

# Gerenciar filas
python3 manage_queues.py --status
```

---

### **🔐 SECURITY SPECIALIST**
#### **Obrigatórios:**
1. **`docs/agents/AGENT-SECURITY.md`** - Perfil e responsabilidades
2. **`docs/queues/QUEUE-SECURITY.md`** - Sua fila de 6 tasks
3. **`prd.md`** - Seções de compliance e LGPD

#### **Comandos Específicos:**
```bash
# Marcar task concluída
python3 update_queue_geral.py --complete "SEC-001" "🔐 Security" "Auditoria concluída"

# Ver sua fila
python3 manage_queues.py --agent SECURITY
```

---

### **🔧 ETL ENGINEER**
#### **Obrigatórios:**
1. **`docs/agents/AGENT-ETL.md`** - Perfil e responsabilidades
2. **`docs/queues/QUEUE-ETL.md`** - Sua fila de 7 tasks
3. **`bdfut/core/`** - Código core para entender
4. **`docs/api/`** - Documentação da API Sportmonks

#### **Comandos Específicos:**
```bash
# Marcar task concluída
python3 update_queue_geral.py --complete "ETL-001" "🔧 ETL Engineer" "Testes implementados"

# Ver sua fila
python3 manage_queues.py --agent ETL
```

---

### **🧪 QA ENGINEER**
#### **Obrigatórios:**
1. **`docs/agents/AGENT-QA.md`** - Perfil e responsabilidades
2. **`docs/queues/QUEUE-QA.md`** - Sua fila de 7 tasks
3. **`tests/`** - Estrutura de testes atual
4. **`pyproject.toml`** - Configuração do projeto

#### **Comandos Específicos:**
```bash
# Marcar task concluída
python3 update_queue_geral.py --complete "QA-001" "🧪 QA Engineer" "Testes unitários criados"

# Ver sua fila
python3 manage_queues.py --agent QA
```

---

### **🗄️ DATABASE SPECIALIST**
#### **Obrigatórios:**
1. **`docs/agents/AGENT-DATABASE.md`** - Perfil e responsabilidades
2. **`docs/queues/QUEUE-DATABASE.md`** - Sua fila de 6 tasks
3. **`supabase/migrations/`** - Migrações existentes
4. **`bdfut/core/supabase_client.py`** - Cliente Supabase

#### **Comandos Específicos:**
```bash
# Marcar task concluída
python3 update_queue_geral.py --complete "DB-001" "🗄️ Database" "Auditoria de índices concluída"

# Ver sua fila
python3 manage_queues.py --agent DATABASE
```

---

### **⚙️ DEVOPS ENGINEER**
#### **Obrigatórios:**
1. **`docs/agents/AGENT-DEVOPS.md`** - Perfil e responsabilidades
2. **`docs/queues/QUEUE-DEVOPS.md`** - Sua fila de 6 tasks
3. **`Dockerfile`** e **`docker-compose.yml`** - Infraestrutura atual
4. **`Makefile`** - Automação existente

#### **Comandos Específicos:**
```bash
# Marcar task concluída
python3 update_queue_geral.py --complete "DEVOPS-001" "⚙️ DevOps" "GitHub Actions configurado"

# Ver sua fila
python3 manage_queues.py --agent DEVOPS
```

---

### **🎨 FRONTEND DEVELOPER**
#### **Obrigatórios:**
1. **`docs/agents/AGENT-FRONTEND.md`** - Perfil e responsabilidades
2. **`docs/queues/QUEUE-FRONTEND.md`** - Sua fila de 6 tasks
3. **`bdfut/config/`** - Configurações para integração

#### **Comandos Específicos:**
```bash
# Marcar task concluída
python3 update_queue_geral.py --complete "FE-001" "🎨 Frontend" "Framework configurado"

# Ver sua fila
python3 manage_queues.py --agent FRONTEND
```

---

### **📚 TECHNICAL WRITER**
#### **Obrigatórios:**
1. **`docs/agents/AGENT-DOCS.md`** - Perfil e responsabilidades
2. **`docs/queues/QUEUE-DOCS.md`** - Sua fila de 6 tasks
3. **`docs/plan.md`** - Plano geral do projeto
4. **`prd.md`** - Requisitos do produto

#### **Comandos Específicos:**
```bash
# Marcar task concluída
python3 update_queue_geral.py --complete "DOCS-001" "📚 Technical Writer" "Arquitetura documentada"

# Ver sua fila
python3 manage_queues.py --agent DOCS
```

---

## 📚 **ARQUIVOS DE CONTEXTO (OPCIONAL MAS RECOMENDADO)**

### **Para Entender o Projeto:**
- **`prd.md`** - Product Requirements Document completo
- **`docs/plan.md`** - Plano de desenvolvimento atualizado
- **`docs/PROJECT_ANALYSIS.md`** - Análise completa do projeto
- **`README.md`** - Visão geral do projeto

### **Para Entender a Arquitetura:**
- **`bdfut/core/`** - Componentes principais
- **`bdfut/config/`** - Sistema de configuração
- **`supabase/migrations/`** - Schema do banco
- **`pyproject.toml`** - Dependências e configuração

---

## 🎯 **FLUXO DE ONBOARDING RECOMENDADO**

### **Passo 1: Leitura Obrigatória (30 minutos)**
1. **QUEUE-GERAL.md** (10 min) - Entender o mapa geral
2. **SEQUENTIAL_ORDER_RULES.md** (10 min) - Regras de ordem
3. **AGENT_INSTRUCTIONS_FINAL.md** (10 min) - Como trabalhar

### **Passo 2: Perfil Específico (20 minutos)**
1. **Seu AGENT-XXX.md** (10 min) - Seu perfil e responsabilidades
2. **Sua QUEUE-XXX.md** (10 min) - Suas tasks específicas

### **Passo 3: Ferramentas (10 minutos)**
1. Testar comandos de atualização
2. Verificar acesso aos scripts
3. Validar ambiente de trabalho

### **Passo 4: Contexto (Opcional - 30 minutos)**
1. **prd.md** - Entender objetivos do produto
2. **docs/plan.md** - Plano geral
3. Código relevante para sua especialização

---

## 🚀 **COMANDOS ESSENCIAIS PARA TODOS**

### **Antes de Iniciar Trabalho:**
```bash
cd docs/queues
python3 update_queue_geral.py --status
```

### **Ao Concluir Task:**
```bash
python3 update_queue_geral.py --complete "TASK-ID" "SEU-AGENTE" "Notas de conclusão"
```

### **Para Verificar Sua Fila:**
```bash
python3 manage_queues.py --agent SEU-CODIGO
```

### **Dashboard Completo (Orquestrador):**
```bash
python3 orchestrator_dashboard.py --dashboard
```

---

## 📞 **CANAIS DE COMUNICAÇÃO**

### **Principal:**
- **QUEUE-GERAL.md** - Fonte única da verdade
- Atualizar sempre ao concluir tasks

### **Secundários:**
- Suas filas individuais (QUEUE-XXX.md)
- Notificações para Orquestrador
- Escalação para impedimentos

---

## 🏆 **CRITÉRIOS DE SUCESSO DO ONBOARDING**

### **Agente está pronto quando:**
- ✅ Leu e entendeu QUEUE-GERAL.md
- ✅ Conhece suas responsabilidades (AGENT-XXX.md)
- ✅ Sabe usar ferramentas de atualização
- ✅ Entende ordem sequencial obrigatória
- ✅ Pode identificar sua próxima task
- ✅ Sabe como reportar conclusões

---

## 🎯 **RESUMO: ARQUIVOS MÍNIMOS OBRIGATÓRIOS**

### **Para QUALQUER agente (3 arquivos):**
1. **`docs/queues/QUEUE-GERAL.md`** ⭐⭐⭐⭐⭐
2. **`docs/queues/SEQUENTIAL_ORDER_RULES.md`** ⭐⭐⭐⭐⭐
3. **`docs/queues/AGENT_INSTRUCTIONS_FINAL.md`** ⭐⭐⭐⭐⭐

### **Para seu agente específico (+2 arquivos):**
4. **`docs/agents/AGENT-SEU-CODIGO.md`** ⭐⭐⭐⭐⭐
5. **`docs/queues/QUEUE-SEU-CODIGO.md`** ⭐⭐⭐⭐⭐

### **Total mínimo: 5 arquivos para estar 100% operacional!**

---

**🎯 Com estes arquivos, qualquer agente pode começar a trabalhar imediatamente seguindo as regras e ordem estabelecidas!**
