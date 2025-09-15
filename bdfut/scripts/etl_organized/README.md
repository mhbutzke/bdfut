# Scripts ETL Organizados - Estrutura Hierárquica

Esta é a nova estrutura hierárquica dos scripts ETL, organizados por funcionalidade e ordem de execução.

## 📁 Estrutura de Diretórios

### 01_setup/ - Configuração e Criação de Tabelas
Scripts para configuração inicial do banco de dados e criação de estruturas.

### 02_base_data/ - Dados Base do Sistema
Scripts para popular dados fundamentais (countries, states, types).

### 03_leagues_seasons/ - Ligas e Temporadas
Scripts para coletar e popular dados de ligas e temporadas.

### 04_fixtures_events/ - Partidas e Eventos
Scripts para coletar partidas, eventos, times e dados relacionados.

### 05_quality_checks/ - Controle de Qualidade
Scripts para auditoria, validação e relatórios de qualidade dos dados.

## 🔄 Ordem de Execução Recomendada

1. **Setup (01_setup/)**: Executar primeiro para criar estruturas
2. **Base Data (02_base_data/)**: Popular dados fundamentais
3. **Leagues/Seasons (03_leagues_seasons/)**: Configurar ligas e temporadas
4. **Fixtures/Events (04_fixtures_events/)**: Coletar dados de partidas
5. **Quality Checks (05_quality_checks/)**: Validar e auditar dados

## 📋 Dependências

- Scripts em cada diretório devem ser executados em ordem numérica
- Diretórios devem ser executados na ordem hierárquica (01 → 02 → 03 → 04 → 05)
- Alguns scripts podem ter dependências específicas documentadas em seus cabeçalhos

## 🏷️ Padrão de Nomenclatura

```
{categoria}_{sequencia}_{funcionalidade}.py

Exemplos:
- 01_setup_01_create_tables.py
- 02_base_data_01_populate_countries.py
- 03_leagues_seasons_01_main_leagues.py
```

## 📊 Scripts Migrados

### 01_setup/ (Configuração)
- `01_setup_01_create_tables_postgres.py` (ex: 11_criar_tabelas_postgres_direto.py)
- `01_setup_02_create_tables_supabase.py` (ex: 09_criar_tabelas_com_service_role.py)
- `01_setup_03_create_complete_structure.py` (ex: 07_criar_tabelas_e_coletar.py)

### 02_base_data/ (Dados Base)
- `02_base_data_01_populate_countries.py` (ex: 23_enriquecer_countries_completo.py)
- `02_base_data_02_populate_types.py` (ex: 20_enriquecer_types_completo.py)
- `02_base_data_03_populate_states.py` (ex: 53_enriquecer_tabelas_completas.py)

### 03_leagues_seasons/ (Ligas e Temporadas)
- `03_leagues_seasons_01_main_leagues.py` (ex: 01_popular_leagues_seasons_v2.py)
- `03_leagues_seasons_02_teams_venues.py` (ex: 02_coletar_teams_primeiro.py)
- `03_leagues_seasons_03_referees.py` (ex: 04_popular_venues_referees.py)

### 04_fixtures_events/ (Partidas e Eventos)
- `04_fixtures_events_01_collect_by_season.py` (ex: 58_coletar_fixtures_ultimas_3_seasons.py)
- `04_fixtures_events_02_collect_main_leagues.py` (ex: 59_coletar_fixtures_ligas_principais.py)
- `04_fixtures_events_03_collect_by_date.py` (ex: 61_coletar_fixtures_por_data.py)
- `04_fixtures_events_04_enrich_events.py` (ex: 03_enriquecer_fixtures_com_events.py)

### 05_quality_checks/ (Controle de Qualidade)
- `05_quality_checks_01_final_audit.py` (ex: 05_auditoria_final.py)
- `05_quality_checks_02_final_report.py` (ex: 57_relatorio_final_enriquecimento.py)
- `05_quality_checks_03_api_test.py` (ex: 60_teste_api_sportmonks.py)

## 🔧 Scripts de Desenvolvimento (Arquivados)

Scripts experimentais e versões antigas foram movidos para `archive/`:
- Versões duplicadas ou obsoletas
- Scripts de teste específicos
- Implementações experimentais

## ⚠️ Importante

- **NÃO execute** scripts diretamente da pasta `etl/` antiga
- **USE SEMPRE** a estrutura `etl_organized/`
- Verifique dependências antes da execução
- Execute testes de qualidade após cada etapa
