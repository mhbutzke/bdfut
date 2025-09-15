# Scripts do Projeto BDFut

Esta pasta contém todos os scripts organizados por categoria para facilitar a manutenção e desenvolvimento.

## 🚨 **IMPORTANTE - NOVA ESTRUTURA HIERÁRQUICA**

**⚠️ A partir de agora, use APENAS a estrutura `etl_organized/`**

Os scripts foram reorganizados em uma estrutura hierárquica moderna:
- 📁 **`etl_organized/`** - **NOVA ESTRUTURA (USE ESTA)**
- 📁 **`etl/`** - Scripts antigos (arquivados)
- 📁 **`development/`**, **`sync/`**, **`enrichment/`**, **`testing/`** - Estrutura antiga (manter para referência)

## 📁 Nova Estrutura Hierárquica (`etl_organized/`)

### `01_setup/` - Configuração e Criação de Tabelas
Scripts para configuração inicial do banco de dados:
- **01_setup_01_create_tables_postgres.py** - Criar estrutura PostgreSQL
- **01_setup_02_create_tables_supabase.py** - Criar estrutura Supabase
- **01_setup_03_create_complete_structure.py** - Estrutura completa + coleta inicial

### `02_base_data/` - Dados Base do Sistema
Scripts para popular dados fundamentais:
- **02_base_data_01_populate_countries.py** - Popular países
- **02_base_data_02_populate_types.py** - Popular tipos de eventos
- **02_base_data_03_populate_states.py** - Popular estados de partidas

### `03_leagues_seasons/` - Ligas e Temporadas
Scripts para configurar ligas e temporadas:
- **03_leagues_seasons_01_main_leagues.py** - Ligas principais e temporadas
- **03_leagues_seasons_02_teams_venues.py** - Times e estádios
- **03_leagues_seasons_03_referees.py** - Árbitros das temporadas

### `04_fixtures_events/` - Partidas e Eventos
Scripts para coletar dados de partidas:
- **04_fixtures_events_01_collect_by_season.py** - Coleta por temporada
- **04_fixtures_events_02_collect_main_leagues.py** - Ligas principais (RECOMENDADO)
- **04_fixtures_events_03_collect_by_date.py** - Coleta por data
- **04_fixtures_events_04_enrich_events.py** - Enriquecer com eventos

### `05_quality_checks/` - Controle de Qualidade
Scripts para auditoria e validação:
- **05_quality_checks_01_final_audit.py** - Auditoria completa
- **05_quality_checks_02_final_report.py** - Relatório final
- **05_quality_checks_03_api_test.py** - Teste da API

## 🚀 Como Usar a Nova Estrutura

### ⚡ Execução Rápida (Mínimo Viável)
```bash
cd bdfut/scripts/etl_organized/

# 1. Setup mínimo
python3 01_setup/01_setup_02_create_tables_supabase.py

# 2. Dados base essenciais
python3 02_base_data/02_base_data_01_populate_countries.py
python3 02_base_data/02_base_data_02_populate_types.py
python3 02_base_data/02_base_data_03_populate_states.py

# 3. Ligas principais
python3 03_leagues_seasons/03_leagues_seasons_01_main_leagues.py

# 4. Fixtures principais (RECOMENDADO)
python3 04_fixtures_events/04_fixtures_events_02_collect_main_leagues.py

# 5. Verificação
python3 05_quality_checks/05_quality_checks_01_final_audit.py
```

### 🔧 Execução Completa (Dados Completos)
```bash
cd bdfut/scripts/etl_organized/

# 1. Setup completo
python3 01_setup/01_setup_03_create_complete_structure.py

# 2. Todos os dados base
python3 02_base_data/02_base_data_01_populate_countries.py
python3 02_base_data/02_base_data_02_populate_types.py
python3 02_base_data/02_base_data_03_populate_states.py

# 3. Ligas, teams e referees
python3 03_leagues_seasons/03_leagues_seasons_01_main_leagues.py
python3 03_leagues_seasons/03_leagues_seasons_02_teams_venues.py
python3 03_leagues_seasons/03_leagues_seasons_03_referees.py

# 4. Fixtures completos
python3 04_fixtures_events/04_fixtures_events_01_collect_by_season.py
python3 04_fixtures_events/04_fixtures_events_02_collect_main_leagues.py
python3 04_fixtures_events/04_fixtures_events_04_enrich_events.py

# 5. Auditoria completa
python3 05_quality_checks/05_quality_checks_01_final_audit.py
python3 05_quality_checks/05_quality_checks_02_final_report.py
```

### 📋 Verificar Dependências
```bash
# Consultar documentação de dependências
cat bdfut/scripts/etl_organized/DEPENDENCIES.md

# Consultar README da nova estrutura
cat bdfut/scripts/etl_organized/README.md
```

## ⚠️ Importante

- Todos os scripts foram atualizados para funcionar com a nova estrutura de pastas
- Os imports foram corrigidos automaticamente para apontar para o diretório raiz
- Sempre execute os scripts a partir do diretório raiz do projeto
- Verifique as dependências antes de executar scripts específicos

## 📝 Notas de Desenvolvimento

- Scripts numerados (01_, 02_, etc.) representam a ordem de execução durante o desenvolvimento
- Múltiplas versões de scripts (v2, v3, final, etc.) indicam iterações de melhoria
- Scripts de teste devem ser executados antes de scripts de produção
- Sempre faça backup dos dados antes de executar scripts de modificação
