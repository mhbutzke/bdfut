# Dependências dos Scripts ETL

Este arquivo documenta as dependências entre os scripts ETL organizados.

## 🔄 Ordem de Execução Obrigatória

### 1. Setup (01_setup/) - PRIMEIRO
```
01_setup_01_create_tables_postgres.py
├── Cria estrutura básica no PostgreSQL
├── Dependências: Nenhuma
└── Requerido por: Todos os outros scripts

01_setup_02_create_tables_supabase.py  
├── Cria estrutura no Supabase
├── Dependências: Nenhuma
└── Requerido por: Todos os scripts de coleta

01_setup_03_create_complete_structure.py
├── Cria estrutura completa e inicia coleta
├── Dependências: 01_setup_01 OU 01_setup_02
└── Requerido por: Scripts de coleta
```

### 2. Base Data (02_base_data/) - SEGUNDO
```
02_base_data_01_populate_countries.py
├── Popula tabela countries
├── Dependências: 01_setup/
└── Requerido por: Todos os scripts que usam country_id

02_base_data_02_populate_types.py
├── Popula tabela types (event types, etc.)
├── Dependências: 01_setup/
└── Requerido por: Scripts de eventos

02_base_data_03_populate_states.py
├── Popula tabela states (fixture states)
├── Dependências: 01_setup/
└── Requerido por: Scripts de fixtures
```

### 3. Leagues/Seasons (03_leagues_seasons/) - TERCEIRO
```
03_leagues_seasons_01_main_leagues.py
├── Popula ligas principais e temporadas
├── Dependências: 02_base_data/
└── Requerido por: Scripts de fixtures e teams

03_leagues_seasons_02_teams_venues.py
├── Coleta teams e venues das temporadas
├── Dependências: 03_leagues_seasons_01
└── Requerido por: Scripts de fixtures

03_leagues_seasons_03_referees.py
├── Coleta árbitros das temporadas
├── Dependências: 03_leagues_seasons_01
└── Requerido por: Scripts de fixtures completos
```

### 4. Fixtures/Events (04_fixtures_events/) - QUARTO
```
04_fixtures_events_01_collect_by_season.py
├── Coleta fixtures por temporada
├── Dependências: 03_leagues_seasons/
└── Pode executar independente dos outros fixtures

04_fixtures_events_02_collect_main_leagues.py
├── Coleta fixtures das ligas principais
├── Dependências: 03_leagues_seasons/
└── Script principal de fixtures (RECOMENDADO)

04_fixtures_events_03_collect_by_date.py
├── Coleta fixtures por intervalo de datas
├── Dependências: 03_leagues_seasons/
└── Para atualizações incrementais

04_fixtures_events_04_enrich_events.py
├── Enriquece fixtures com eventos detalhados
├── Dependências: Qualquer script 04_fixtures_events_0[1-3]
└── Execução opcional para dados completos
```

### 5. Quality Checks (05_quality_checks/) - ÚLTIMO
```
05_quality_checks_01_final_audit.py
├── Auditoria completa dos dados
├── Dependências: Todos os scripts anteriores
└── Executar após qualquer coleta

05_quality_checks_02_final_report.py
├── Relatório final de enriquecimento
├── Dependências: Todos os scripts anteriores
└── Relatório completo do processo

05_quality_checks_03_api_test.py
├── Teste da API Sportmonks
├── Dependências: Nenhuma
└── Pode executar independente para diagnóstico
```

## ⚡ Execução Rápida (Mínimo Viável)

Para uma execução mínima e funcional:

```bash
# 1. Setup mínimo
python3 01_setup/01_setup_02_create_tables_supabase.py

# 2. Dados base essenciais
python3 02_base_data/02_base_data_01_populate_countries.py
python3 02_base_data/02_base_data_02_populate_types.py
python3 02_base_data/02_base_data_03_populate_states.py

# 3. Ligas principais
python3 03_leagues_seasons/03_leagues_seasons_01_main_leagues.py

# 4. Fixtures principais
python3 04_fixtures_events/04_fixtures_events_02_collect_main_leagues.py

# 5. Verificação
python3 05_quality_checks/05_quality_checks_01_final_audit.py
```

## 🔧 Execução Completa (Dados Completos)

Para coleta completa de todos os dados:

```bash
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

## 🚨 Importante

1. **Ordem obrigatória**: Sempre executar na ordem hierárquica (01 → 02 → 03 → 04 → 05)
2. **Verificar dependências**: Cada script verifica suas dependências no início
3. **Logs detalhados**: Todos os scripts geram logs para monitoramento
4. **Rate limiting**: Scripts de coleta respeitam limites da API
5. **Idempotência**: Scripts podem ser re-executados com segurança

## 📊 Tempo Estimado de Execução

| Categoria | Tempo Estimado | Observações |
|-----------|----------------|-------------|
| 01_setup/ | 5-10 minutos | Criação de estruturas |
| 02_base_data/ | 15-30 minutos | Depende da API |
| 03_leagues_seasons/ | 30-60 minutos | Muitas requisições |
| 04_fixtures_events/ | 2-6 horas | Volume alto de dados |
| 05_quality_checks/ | 10-20 minutos | Análise dos dados |
| **TOTAL** | **3-8 horas** | Execução completa |
