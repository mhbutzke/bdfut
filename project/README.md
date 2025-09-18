# 🏆 BDFut - Sistema ETL para Dados de Futebol

## 🎯 Visão Geral

BDFut é um sistema ETL profissional que coleta dados da API Sportmonks e armazena no Supabase, criando a mais completa e detalhada base de dados de futebol do mundo.

## 📊 Status Atual

### **Base de Dados (Supabase)**
- **67,085 fixtures** coletadas e organizadas
- **62,781 eventos** de partidas (gols, cartões, substituições)
- **18,424 escalações** com formações táticas
- **78,340 jogadores** com dados completos
- **14,561 times** de múltiplas ligas
- **113 ligas** principais mundiais

### **Performance ETL**
- **Taxa de sucesso**: 99%+
- **Tempo de coleta**: 5-8 minutos
- **Cache hit rate**: 70%+
- **Rate limiting**: Otimizado com headers reais

## 🚀 Quick Start

### **1. Configuração do Ambiente**
```bash
# Clone e navegue
git clone [repo-url]
cd project/

# Configure ambiente
cp .env.example .env
# Edite .env com suas credenciais

# Instale dependências
pip install -r config/requirements.txt
```

### **2. Task Master (Recomendado)**
```bash
# Ver próxima task prioritária
task-master next

# Ver todas as tasks
task-master list

# Começar implementação
task-master show 1
```

### **3. Execução Manual de Scripts**
```bash
# Navegar para scripts ETL
cd src/bdfut/scripts/etl_organized/

# Executar por categoria (em ordem)
python3 01_setup/setup_script.py
python3 04_fixtures_events/collect_fixtures.py
python3 05_quality_checks/validate_data.py
```

## 🔧 Componentes Principais

### **ETL Core**
- `SportmonksClient` - Cliente otimizado para API Sportmonks v3
- `SupabaseClient` - Cliente para operações no Supabase
- `ETLMetadataManager` - Controle de jobs ETL
- `DataQualityManager` - Validação automática

### **Scripts Organizados**
```
src/bdfut/scripts/etl_organized/
├── 01_setup/              # Configuração inicial
├── 02_base_data/          # Dados fundamentais
├── 03_leagues_seasons/    # Ligas e temporadas
├── 04_fixtures_events/    # Fixtures (FOCO PRINCIPAL)
└── 05_quality_checks/     # Validações
```

### **Ferramentas**
- `database_validator.py` - Validação de integridade
- Migration scripts - Organização do schema
- Backup scripts - Segurança dos dados

## 📋 Tasks Atuais (Task Master)

### **🔧 Tag: `etl-agent`**

| ID | Task | Status | Prioridade |
|----|------|--------|------------|
| 1 | Organizar Schema das Tabelas | pending | HIGH |
| 2 | Coleta Incremental | pending | HIGH |
| 3 | Performance ETL | pending | HIGH |
| 4 | Validação de Dados | pending | MEDIUM |
| 5 | Enriquecimento Fixtures | pending | MEDIUM |
| 6 | Monitoramento ETL | pending | LOW |

### **🎯 Próxima Ação:**
**Task 1.1** - Mapear colunas faltantes da API Sportmonks

## 🗂️ Estrutura de Arquivos

### **📁 Código Fonte**
```
src/bdfut/
├── core/           # Componentes principais
├── config/         # Configurações
├── scripts/        # Scripts ETL organizados
└── tools/          # Ferramentas auxiliares
```

### **📁 Documentação**
```
docs_organized/
├── core/           # PRDs e análises
├── etl/            # Guias ETL
├── database/       # Migrations e scripts DB
└── archive/        # Documentos históricos
```

### **📁 Configurações**
```
config/
├── docker-compose.yml    # Ambiente Docker
├── requirements.txt      # Dependências Python
├── pyproject.toml        # Configuração Python
└── Dockerfile            # Imagem Docker
```

### **📁 Deploy**
```
deployment/supabase/
├── migrations/           # Migrations oficiais Supabase
└── config.toml          # Configuração Supabase
```

## 🔍 Arquivos Principais

### **ETL Core**
- `src/bdfut/core/sportmonks_client.py` - Cliente API principal
- `src/bdfut/core/supabase_client.py` - Cliente banco de dados
- `src/bdfut/tools/database_validator.py` - Validação automática

### **Configuração**
- `config/requirements.txt` - Dependências Python
- `.env` - Variáveis de ambiente (copie de .env.example)
- `.taskmaster/tasks/tasks.json` - Tasks organizadas

### **Migrations**
- `docs_organized/database/migrations/001_enhance_fixtures_table.sql`
- `docs_organized/database/migrations/002_create_fixtures_views.sql`

## 🎯 Foco Atual: Organização do Schema

### **Problema Identificado:**
A tabela `fixtures` (central do projeto) está faltando colunas essenciais da API Sportmonks:
- `name` - Nome da partida
- `result_info` - Informação do resultado
- `home_score`, `away_score` - Placares
- Campos de controle ETL

### **Solução Preparada:**
- ✅ Migration 001 criada e pronta
- ✅ Scripts de backup preparados
- ✅ Validação automática implementada
- ✅ Task Master organizado

## 🚀 Como Contribuir

### **Para Agente ETL:**
1. Execute `task-master next` para ver próxima task
2. Siga as subtasks em ordem (1.1 → 1.2 → 1.3)
3. Use os scripts preparados em `docs_organized/database/migrations/`
4. Valide resultados com `database_validator.py`

### **Para Desenvolvedores:**
1. Configure ambiente com `.env`
2. Execute `pip install -r config/requirements.txt`
3. Teste conectividade: `python -c "from src.bdfut.core.sportmonks_client import SportmonksClient; SportmonksClient()"`
4. Siga documentação em `docs_organized/`

## 📊 Métricas de Sucesso

- **Taxa de sucesso ETL**: > 95%
- **Tempo de coleta**: < 10 minutos
- **Qualidade dos dados**: > 90%
- **Performance**: Consultas < 100ms
- **Cobertura de testes**: > 60%

## 🔗 Links Importantes

- **Task Master**: `.taskmaster/tasks/tasks.json`
- **Documentação ETL**: `docs_organized/etl/AGENT-ETL.md`
- **Migrations**: `docs_organized/database/migrations/`
- **Scripts ETL**: `src/bdfut/scripts/etl_organized/`

---

## 🎉 Projeto Organizado e Pronto!

**BDFut agora tem:**
- ✅ Estrutura limpa e organizada
- ✅ Task Master integrado
- ✅ Documentação focada
- ✅ Scripts preparados para execução
- ✅ Migrations prontas para aplicação

**Próxima ação**: `task-master next` 🚀
