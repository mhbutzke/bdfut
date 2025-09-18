# 🗺️ Índice de Navegação - Projeto BDFut

## 🚀 Acesso Rápido

### **📋 Para Agente ETL:**
```bash
# Task Master
task-master next                     # Próxima task
task-master show 1                   # Detalhes Task 1
task-master list                     # Todas as tasks

# Documentação ETL
docs_organized/etl/AGENT-ETL.md      # Guia principal
docs_organized/etl/ETL_AGENT_GUIDELINES.md  # Diretrizes
```

### **🔧 Para Desenvolvimento:**
```bash
# Scripts ETL
cd src/bdfut/scripts/etl_organized/
python3 04_fixtures_events/[script].py

# Ferramentas
python src/bdfut/tools/database_validator.py
```

### **🗃️ Para Database:**
```bash
# Migrations
psql $SUPABASE_DB_URL -f docs_organized/database/migrations/001_enhance_fixtures_table.sql

# Backup
./docs_organized/database/migrations/backup_fixtures.sh
```

## 📁 Estrutura de Arquivos

### **🎯 Essenciais (Uso Diário):**
- `README.md` - Visão geral do projeto
- `.taskmaster/tasks/tasks.json` - Tasks organizadas
- `src/bdfut/core/sportmonks_client.py` - Cliente API
- `config/requirements.txt` - Dependências

### **📚 Documentação (Por Área):**
- `docs_organized/core/` - PRDs e análises principais
- `docs_organized/etl/` - Guias específicos do ETL
- `docs_organized/database/` - Migrations e scripts DB

### **🔧 Scripts (Por Categoria):**
- `src/bdfut/scripts/etl_organized/01_setup/` - Configuração
- `src/bdfut/scripts/etl_organized/04_fixtures_events/` - **FOCO**
- `src/bdfut/tools/` - Ferramentas auxiliares

### **📦 Arquivados (Referência):**
- `archive/api_samples/` - Samples de teste da API
- `docs_organized/archive/` - Documentação histórica

## 🎯 Fluxo de Trabalho

### **1. Início de Sessão:**
```bash
cd /Users/mhbutzke/Documents/BDFut/bdfut/project
task-master next
```

### **2. Implementação:**
```bash
task-master show [id]              # Ver detalhes
task-master set-status --id=[id] --status=in-progress
# [Implementar a task]
task-master set-status --id=[id] --status=done
```

### **3. Validação:**
```bash
python src/bdfut/tools/database_validator.py
```

## 📊 Status Atual

### **🏷️ Task Master:**
- **Tag ativo**: `etl-agent`
- **Tasks**: 6 principais + 3 subtasks
- **Próxima**: Task 1.1 (Mapear colunas faltantes)

### **🗃️ Base de Dados:**
- **fixtures**: 67,085 registros (tabela central)
- **Colunas faltantes**: name, result_info, placares
- **Migration pronta**: 001_enhance_fixtures_table.sql

### **📁 Projeto:**
- **294 arquivos** Python organizados
- **56 arquivos** Markdown focados
- **43 arquivos** JSON arquivados
- **Estrutura limpa** e navegável

## 🔍 Busca Rápida

### **Por Função:**
- **ETL**: `src/bdfut/` e `docs_organized/etl/`
- **Database**: `docs_organized/database/`
- **Config**: `config/` e `.env`
- **Tasks**: `.taskmaster/`

### **Por Tipo de Arquivo:**
- **Scripts Python**: `find src/ -name "*.py"`
- **Migrations SQL**: `docs_organized/database/migrations/`
- **Documentação**: `docs_organized/`
- **Configurações**: `config/`

---

**🎯 Navegação otimizada para máxima eficiência no projeto BDFut!**
