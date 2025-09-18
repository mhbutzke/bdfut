# 📖 Guia Completo do Projeto BDFut Organizado

## 🎯 Objetivo do Projeto

**BDFut** é um sistema ETL que coleta dados da API Sportmonks e armazena no Supabase para criar a mais completa base de dados de futebol do mundo.

## 🏗️ Arquitetura Reorganizada

### **📁 Estrutura Principal**
```
project/
├── 🔧 src/bdfut/                    # CÓDIGO ETL PRINCIPAL
├── 📚 docs_organized/               # DOCUMENTAÇÃO FOCADA
├── ⚙️ config/                       # CONFIGURAÇÕES
├── 🚀 deployment/                   # DEPLOY SUPABASE
├── 🧪 tests/                        # TESTES AUTOMATIZADOS
├── 🎨 frontend/                     # APLICAÇÃO NEXT.JS
├── 📦 archive/                      # ARQUIVOS ARQUIVADOS
├── 🎯 .taskmaster/                  # TASK MASTER
└── 📊 data/                         # DADOS E LOGS
```

## 🔧 Componentes ETL (Foco Principal)

### **Core ETL (`src/bdfut/core/`)**
- `sportmonks_client.py` - Cliente otimizado para API Sportmonks v3
- `supabase_client.py` - Cliente para operações no Supabase
- `etl_process.py` - Orquestrador principal do ETL
- `redis_cache.py` - Sistema de cache inteligente
- `etl_metadata.py` - Controle de jobs ETL
- `data_quality.py` - Validação automática

### **Scripts ETL (`src/bdfut/scripts/etl_organized/`)**
```
├── 01_setup/              # Configuração inicial do sistema
├── 02_base_data/          # Dados fundamentais (countries, types)
├── 03_leagues_seasons/    # Ligas, temporadas, teams, players
├── 04_fixtures_events/    # Fixtures e eventos (FOCO PRINCIPAL)
└── 05_quality_checks/     # Validações e verificações
```

### **Ferramentas (`src/bdfut/tools/`)**
- `database_validator.py` - Validação de integridade automática
- `audit_manager.py` - Auditoria de dados
- `encryption_manager.py` - Segurança de dados

## 📊 Base de Dados (Supabase)

### **Tabelas Principais:**
| Tabela | Registros | Descrição |
|--------|-----------|-----------|
| `fixtures` | 67,085 | **Tabela central** - Partidas de futebol |
| `match_events` | 62,781 | Eventos das partidas (gols, cartões) |
| `match_lineups` | 18,424 | Escalações e formações táticas |
| `teams` | 14,561 | Times de múltiplas ligas |
| `players` | 78,340 | Jogadores com dados completos |
| `leagues` | 113 | Ligas principais mundiais |
| `seasons` | 1,920 | Temporadas históricas |

### **Problema Atual (Task 1.2):**
Tabela `fixtures` faltando colunas essenciais:
- `name` - Nome da partida
- `result_info` - Resultado da partida
- `home_score`, `away_score` - Placares
- Campos de controle ETL

## 🎯 Task Master Integrado

### **Tag Ativo: `etl-agent`**

| ID | Task | Status | Prioridade | Foco |
|----|------|--------|------------|------|
| 1 | **Organizar Schema** | pending | HIGH | Estruturar tabelas |
| 1.1 | Mapear colunas faltantes | pending | HIGH | Análise API |
| 1.2 | Migration fixtures | pending | HIGH | Adicionar colunas |
| 1.3 | Otimizar índices | pending | MEDIUM | Performance |
| 2 | **Coleta Incremental** | pending | HIGH | Otimizar coleta |
| 3 | **Performance ETL** | pending | HIGH | Cache e rate limiting |
| 4 | **Validação de Dados** | pending | MEDIUM | Qualidade |
| 5 | **Enriquecimento** | pending | MEDIUM | Dados completos |
| 6 | **Monitoramento** | pending | LOW | Alertas e métricas |

## 🚀 Como Usar

### **1. Setup Inicial**
```bash
# Navegar para projeto
cd /Users/mhbutzke/Documents/BDFut/bdfut/project

# Configurar ambiente
cp .env.example .env
# Editar .env com credenciais

# Instalar dependências
pip install -r config/requirements.txt
```

### **2. Task Master (Recomendado)**
```bash
# Ver próxima task prioritária
task-master next

# Ver detalhes da Task 1
task-master show 1

# Começar implementação
task-master set-status --id=1.1 --status=in-progress
```

### **3. Execução Manual**
```bash
# Scripts ETL por categoria
cd src/bdfut/scripts/etl_organized/
python3 04_fixtures_events/collect_fixtures.py

# Validação de dados
python src/bdfut/tools/database_validator.py

# Migrations de banco
psql $SUPABASE_DB_URL -f docs_organized/database/migrations/001_enhance_fixtures_table.sql
```

## 📚 Documentação por Área

### **🔧 ETL (Agente Principal)**
- `docs_organized/etl/AGENT-ETL.md` - Guia principal do agente
- `docs_organized/etl/ETL_AGENT_GUIDELINES.md` - Diretrizes específicas

### **🗃️ Database**
- `docs_organized/database/migrations/` - Scripts de migration
- `docs_organized/core/api_database_mapping_analysis.md` - Análise de mapeamento

### **📋 Core**
- `docs_organized/core/prd.md` - Product Requirements Document
- `docs_organized/core/project_improvement_suggestions.md` - Melhorias
- `docs_organized/core/database_organization_prd.md` - PRD específico do banco

## 🔍 Navegação Rápida

### **Por Atividade:**
- **Implementar ETL**: `src/bdfut/` + `docs_organized/etl/`
- **Organizar DB**: `docs_organized/database/migrations/`
- **Ver Tasks**: `.taskmaster/tasks/tasks.json`
- **Configurar**: `config/` + `.env`

### **Por Prioridade:**
1. **ALTA**: Task 1 (Organizar schema) - `task-master show 1`
2. **ALTA**: Task 2 (Coleta incremental) - Após Task 1
3. **ALTA**: Task 3 (Performance) - Após Task 1
4. **MÉDIA**: Tasks 4-5 (Validação e enriquecimento)
5. **BAIXA**: Task 6 (Monitoramento)

## 📊 Métricas e Status

### **Projeto:**
- **294 arquivos** Python organizados
- **56 documentos** Markdown focados  
- **43 arquivos** JSON arquivados
- **34 migrations** SQL disponíveis

### **ETL:**
- **Taxa de sucesso**: 99%+
- **Performance**: 5-8 minutos
- **Cache hit rate**: 70%+
- **Qualidade**: 90%+ score

### **Base de Dados:**
- **25 tabelas** principais
- **200k+ registros** totais
- **Integridade**: Validada
- **Schema**: Precisa organização (Task 1)

## 🎯 Próximas Ações Imediatas

### **1. Agente ETL (Prioridade 1)**
```bash
task-master next
task-master show 1.1
# Implementar mapeamento de colunas
```

### **2. Organização de Schema (Prioridade 2)**
```bash
# Executar migration preparada
psql $SUPABASE_DB_URL -f docs_organized/database/migrations/001_enhance_fixtures_table.sql
```

### **3. Validação (Prioridade 3)**
```bash
# Validar integridade
python src/bdfut/tools/database_validator.py
```

## 🔗 Links Essenciais

- **README Principal**: `README.md`
- **Task Master**: `.taskmaster/tasks/tasks.json`
- **Agente ETL**: `docs_organized/etl/AGENT-ETL.md`
- **Migrations**: `docs_organized/database/migrations/`
- **Navegação**: `docs_organized/NAVIGATION_INDEX.md`

---

## ✅ Projeto Totalmente Organizado!

**BDFut agora tem:**
- 🧹 **Estrutura limpa** - Arquivos organizados por função
- 📚 **Documentação focada** - Apenas o essencial
- 🎯 **Task Master integrado** - Workflow claro
- 🔧 **ETL otimizado** - Scripts preparados
- 🗃️ **Migrations prontas** - Schema organizável
- 📦 **Arquivos arquivados** - Sem poluição

**Próxima ação**: `task-master next` para começar implementação! 🚀
