# Navegação no Projeto BDFut 🧭

## 🗺️ **MAPA COMPLETO DO PROJETO**

### **📊 ESTRUTURA PRINCIPAL:**
```
project/
├── src/                   💻 CÓDIGO FONTE
│   ├── bdfut/             🔧 Sistema ETL Python
│   └── frontend/          🎨 Dashboard Next.js
├── docs/                  📚 DOCUMENTAÇÃO
│   ├── management/        🎭 Gestão de agentes
│   ├── onboarding/        🎯 Esta pasta (VOCÊ ESTÁ AQUI)
│   └── guides/            📖 Guias técnicos
├── tests/                 🧪 Testes (222 testes)
├── deployment/            🚀 Deploy e migrações
├── monitoring/            📊 Observabilidade
├── data/                  📁 Dados e logs
└── config/                ⚙️ Configurações
```

---

## 🎯 **NAVEGAÇÃO POR AGENTE**

### **🔧 ETL ENGINEER:**
```bash
# Seu código principal:
cd project/src/bdfut/core/

# Seus scripts organizados:
cd project/src/bdfut/scripts/etl_organized/

# Suas ferramentas:
cd project/src/bdfut/tools/

# Sua fila de tasks:
cat project/docs/management/queues/QUEUE-ETL.md

# Status geral:
cd project/docs/management/queues
python3 tools/update_queue_geral.py --status
```

### **🎨 FRONTEND DEVELOPER:**
```bash
# Seu código principal:
cd project/frontend/src/

# Seus componentes:
cd project/frontend/src/components/

# Seus hooks:
cd project/frontend/src/hooks/

# Desenvolvimento:
cd project/frontend
npm run dev

# Sua fila:
cat project/docs/management/queues/QUEUE-FRONTEND.md
```

### **🗄️ DATABASE SPECIALIST:**
```bash
# Suas migrações:
cd project/deployment/supabase/migrations/

# Scripts de manutenção:
cd project/src/bdfut/scripts/maintenance/

# Sua fila:
cat project/docs/management/queues/QUEUE-DATABASE.md
```

### **🔐 SECURITY SPECIALIST:**
```bash
# Suas ferramentas:
cd project/src/bdfut/tools/

# Seus guias:
cd project/docs/guides/security/

# Sua fila:
cat project/docs/management/queues/QUEUE-SECURITY.md
```

### **🧪 QA ENGINEER:**
```bash
# Seus testes:
cd project/tests/

# Executar testes:
pytest project/tests/

# Coverage:
pytest --cov=project/src/bdfut

# Sua fila:
cat project/docs/management/queues/QUEUE-QA.md
```

### **⚙️ DEVOPS ENGINEER:**
```bash
# CI/CD:
cd .github/workflows/

# Configurações:
cd project/config/

# Monitoramento:
cd project/monitoring/

# Sua fila:
cat project/docs/management/queues/QUEUE-DEVOPS.md
```

### **📚 TECHNICAL WRITER:**
```bash
# Toda documentação:
cd project/docs/

# Guias categorizados:
cd project/docs/guides/

# Sua fila:
cat project/docs/management/queues/QUEUE-DOCS.md
```

---

## 🔍 **ARQUIVOS MAIS IMPORTANTES**

### **🗺️ FONTE ÚNICA DA VERDADE:**
**`project/docs/management/queues/QUEUE-GERAL.md`**
- Status de todas as 59+ tasks
- Progresso geral do projeto
- Tasks disponíveis para execução

### **🔢 REGRAS OBRIGATÓRIAS:**
**`project/docs/management/queues/SEQUENTIAL_ORDER_RULES.md`**
- Ordem sequencial obrigatória
- Consequências de violações
- Processo de validação

### **📋 SUA FILA ESPECÍFICA:**
**`project/docs/management/queues/QUEUE-[SEU-CODIGO].md`**
- Suas tasks específicas
- Ordem de execução
- Critérios de sucesso

### **👤 SEU PERFIL:**
**`project/docs/management/agents/AGENT-[SEU-CODIGO].md`**
- Suas responsabilidades
- Padrões de trabalho
- Métricas de sucesso

---

## 🛠️ **FERRAMENTAS ESSENCIAIS**

### **📊 Gestão de Status:**
```bash
cd project/docs/management/queues

# Ver status geral
python3 tools/update_queue_geral.py --status

# Ver sua fila específica
python3 tools/manage_queues.py --agent [SEU-CODIGO]

# Marcar task concluída
python3 tools/update_queue_geral.py --complete "TASK-ID" "SEU-AGENTE" "Notas"
```

### **🔧 Desenvolvimento:**
```bash
cd project/config

# Setup ambiente
make setup

# Executar testes
make test

# Linting
make lint

# Docker
make docker-dev
```

---

## 📊 **COMANDOS POR ESPECIALIZAÇÃO**

### **🔧 ETL:**
```bash
cd project/src/bdfut
python cli.py --help
python cli.py sync-base
```

### **🎨 Frontend:**
```bash
cd project/frontend
npm run dev
npm run build
npm run storybook
```

### **🧪 QA:**
```bash
cd project
pytest tests/
pytest --cov=src/bdfut
```

### **🚀 Deploy:**
```bash
cd project/deployment/supabase
supabase db push
```

---

## 🎯 **NAVEGAÇÃO RÁPIDA**

### **📋 Precisa de:**
- **Status geral?** → `QUEUE-GERAL.md`
- **Suas tasks?** → `QUEUE-[SEU-CODIGO].md`
- **Como fazer?** → `onboarding/templates/`
- **Exemplos?** → `onboarding/examples/`
- **Padrões?** → `onboarding/standards/`
- **Dúvidas?** → `onboarding/guides/`

### **🔧 Precisa executar:**
- **Ver status** → `update_queue_geral.py --status`
- **Sua fila** → `manage_queues.py --agent [CODIGO]`
- **Concluir task** → `update_queue_geral.py --complete`

---

## 🏆 **VOCÊ SABE NAVEGAR!**

### **✅ Agora você pode:**
- **Localizar** qualquer arquivo do projeto
- **Executar** comandos essenciais
- **Seguir** padrões estabelecidos
- **Trabalhar** com máxima eficiência

### **🎯 Próximo passo:**
**Ler `standards/SEQUENTIAL_RULES.md` para entender as regras fundamentais!**

---

**🧭 Navegação no projeto BDFut dominada! Você está pronto para trabalhar! 🚀**
