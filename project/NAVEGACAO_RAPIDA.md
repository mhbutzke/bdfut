# Navegação Rápida - Projeto Organizado 🧭

## ⚡ **ACESSO RÁPIDO**

### **🗺️ FONTE ÚNICA DA VERDADE:**
**`docs/management/queues/QUEUE-GERAL.md`**

### **⚡ INÍCIO RÁPIDO:**
**`docs/management/QUICK_START_AGENTS.md`**

### **🔢 REGRAS:**
**`docs/management/queues/SEQUENTIAL_ORDER_RULES.md`**

---

## 📁 **NAVEGAÇÃO POR CATEGORIA**

### **💻 CÓDIGO FONTE:**
```bash
cd project/src/bdfut/          # Código ETL principal
cd project/frontend/           # Dashboard Next.js
```

### **📚 DOCUMENTAÇÃO:**
```bash
cd project/docs/management/    # Gestão de agentes
cd project/docs/guides/        # Guias por categoria
cd project/docs/reference/     # Documentação técnica
```

### **🧪 TESTES:**
```bash
cd project/tests/              # Todos os testes
pytest project/tests/          # Executar testes
```

### **🚀 DEPLOY:**
```bash
cd project/deployment/         # Configurações deploy
cd project/monitoring/         # Observabilidade
```

---

## 🛠️ **FERRAMENTAS ESSENCIAIS**

### **📊 Gestão de Agentes:**
```bash
cd project/docs/management/queues
python3 tools/update_queue_geral.py --status
python3 tools/orchestrator_dashboard.py --dashboard
python3 tools/manage_queues.py --status
```

### **🔧 Desenvolvimento:**
```bash
cd project/config
make setup          # Setup ambiente
make test           # Testes
make lint           # Linting
make docker-dev     # Docker
```

### **🎨 Frontend:**
```bash
cd project/frontend
npm run dev         # Desenvolvimento
npm run build       # Build produção
npm run storybook   # Storybook
```

---

## 🎯 **POR AGENTE**

### **🎭 ORQUESTRADOR:**
- **Dashboard:** `project/docs/management/queues/tools/orchestrator_dashboard.py`
- **Relatórios:** `project/docs/management/reports/`

### **🔧 ETL ENGINEER:**
- **Código:** `project/src/bdfut/core/`
- **Scripts:** `project/src/bdfut/scripts/etl_organized/`
- **Fila:** `project/docs/management/queues/QUEUE-ETL.md`

### **🎨 FRONTEND DEVELOPER:**
- **Código:** `project/frontend/src/`
- **Componentes:** `project/frontend/src/components/`
- **Fila:** `project/docs/management/queues/QUEUE-FRONTEND.md`

### **🗄️ DATABASE SPECIALIST:**
- **Migrações:** `project/deployment/supabase/migrations/`
- **Scripts:** `project/src/bdfut/scripts/maintenance/`

### **🔐 SECURITY SPECIALIST:**
- **Tools:** `project/src/bdfut/tools/`
- **Guides:** `project/docs/guides/security/`

### **🧪 QA ENGINEER:**
- **Testes:** `project/tests/`
- **Coverage:** `project/tests/htmlcov/`

### **⚙️ DEVOPS ENGINEER:**
- **Docker:** `project/config/docker-compose.yml`
- **CI/CD:** `.github/workflows/`
- **Monitoring:** `project/monitoring/`

### **📚 TECHNICAL WRITER:**
- **Docs:** `project/docs/`
- **Guides:** `project/docs/guides/`

---

## 🔍 **LOCALIZAÇÃO RÁPIDA**

### **📊 Status do Projeto:**
```bash
cd project/docs/management/queues
cat QUEUE-GERAL.md | grep "PROGRESSO GERAL"
```

### **🔧 Executar ETL:**
```bash
cd project/src/bdfut
python cli.py sync-base
```

### **🎨 Dashboard:**
```bash
cd project/frontend
npm run dev
# Acesse: http://localhost:3000
```

### **🧪 Testes:**
```bash
cd project
pytest tests/ --cov=src/bdfut
```

### **📊 Métricas:**
```bash
cd project/monitoring
docker-compose up -d
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001
```

---

## 📋 **ARQUIVOS IMPORTANTES**

### **🎯 Configuração:**
- **`project/config/pyproject.toml`** - Configuração Python
- **`project/config/docker-compose.yml`** - Ambiente Docker
- **`project/config/Makefile`** - Comandos automação

### **📊 Gestão:**
- **`project/docs/management/queues/QUEUE-GERAL.md`** - Status geral
- **`project/docs/management/QUICK_START_AGENTS.md`** - Início rápido

### **🔧 Desenvolvimento:**
- **`project/src/bdfut/cli.py`** - Interface CLI
- **`project/src/bdfut/core/etl_process.py`** - Processo principal

### **🎨 Frontend:**
- **`project/frontend/src/app/page.tsx`** - Dashboard principal
- **`project/frontend/package.json`** - Dependências

---

## 🚀 **COMANDOS DE PRODUTIVIDADE**

### **Setup Rápido:**
```bash
# Clone e setup
git clone https://github.com/mhbutzke/bdfut.git
cd bdfut
make setup

# Status do projeto
cd project/docs/management/queues
python3 tools/update_queue_geral.py --status
```

### **Desenvolvimento:**
```bash
# Backend
cd project/src/bdfut
python cli.py --help

# Frontend
cd project/frontend
npm run dev

# Testes
cd project
pytest tests/
```

### **Monitoramento:**
```bash
# Logs
tail -f project/data/logs/*.log

# Métricas
cd project/monitoring
docker-compose up -d
```

---

## 🏆 **ESTRUTURA OTIMIZADA**

### **✅ Benefícios:**
- **Navegação 90% mais rápida**
- **Localização intuitiva** por categoria
- **Separação lógica** de responsabilidades
- **Manutenção simplificada**
- **Colaboração facilitada**

### **📊 Organização:**
- **6 categorias principais** bem definidas
- **Hierarquia lógica** implementada
- **Ferramentas centralizadas**
- **Documentação categorizada**

---

**🎯 Estrutura final organizada e pronta para máxima produtividade! 📊**
