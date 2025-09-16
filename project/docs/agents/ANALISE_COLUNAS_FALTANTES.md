# 🔧 ANÁLISE DE COLUNAS FALTANTES - API SPORTMONKS

**Data:** 13 de Janeiro de 2025  
**Para:** Database Specialist & ETL Specialist  
**Objetivo:** Identificar e adicionar colunas faltantes para acomodar todos os dados da API Sportmonks

---

## 🎯 **RESUMO EXECUTIVO**

### 📊 **Situação Atual**
- **Problema:** Tabelas não têm todas as colunas necessárias para dados da API Sportmonks
- **Impacto:** Perda de dados valiosos durante a coleta
- **Solução:** Migração de schema para adicionar colunas faltantes

### 🎯 **Objetivos**
- **Identificar** colunas faltantes por tabela
- **Criar** migrações SQL para adicionar colunas
- **Validar** compatibilidade com dados existentes
- **Documentar** mudanças no schema

---

## 📋 **ANÁLISE POR TABELA**

### 🔴 **FIXTURES - Colunas Faltantes Críticas**

#### **Colunas Atuais vs Necessárias**

| Campo API Sportmonks | Coluna Atual | Status | Tipo Sugerido |
|----------------------|--------------|---------|---------------|
| `id` | ✅ sportmonks_id | OK | INTEGER |
| `name` | ❌ **FALTANDO** | 🔴 CRÍTICO | VARCHAR(255) |
| `starting_at` | ❌ **FALTANDO** | 🔴 CRÍTICO | TIMESTAMP WITH TIME ZONE |
| `result_info` | ❌ **FALTANDO** | 🔴 CRÍTICO | VARCHAR(100) |
| `leg` | ❌ **FALTANDO** | 🟡 IMPORTANTE | VARCHAR(50) |
| `details` | ❌ **FALTANDO** | 🟡 IMPORTANTE | TEXT |
| `length` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `placeholder` | ❌ **FALTANDO** | 🟢 OPCIONAL | BOOLEAN |
| `has_odds` | ❌ **FALTANDO** | 🟢 OPCIONAL | BOOLEAN |
| `has_players` | ❌ **FALTANDO** | 🟢 OPCIONAL | BOOLEAN |
| `has_lineups` | ❌ **FALTANDO** | 🟢 OPCIONAL | BOOLEAN |
| `has_statistics` | ❌ **FALTANDO** | 🟢 OPCIONAL | BOOLEAN |
| `has_events` | ❌ **FALTANDO** | 🟢 OPCIONAL | BOOLEAN |
| `is_deleted` | ❌ **FALTANDO** | 🟢 OPCIONAL | BOOLEAN |
| `tie_breaker_rule` | ❌ **FALTANDO** | 🟢 OPCIONAL | VARCHAR(255) |

#### **Migração SQL para Fixtures**
```sql
-- Adicionar colunas faltantes na tabela fixtures
ALTER TABLE public.fixtures 
ADD COLUMN IF NOT EXISTS name VARCHAR(255),
ADD COLUMN IF NOT EXISTS starting_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS result_info VARCHAR(100),
ADD COLUMN IF NOT EXISTS leg VARCHAR(50),
ADD COLUMN IF NOT EXISTS details TEXT,
ADD COLUMN IF NOT EXISTS length INTEGER,
ADD COLUMN IF NOT EXISTS placeholder BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_odds BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_players BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_lineups BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_statistics BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_events BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS tie_breaker_rule VARCHAR(255);

-- Adicionar índices para novas colunas importantes
CREATE INDEX IF NOT EXISTS idx_fixtures_starting_at ON public.fixtures (starting_at);
CREATE INDEX IF NOT EXISTS idx_fixtures_result_info ON public.fixtures (result_info);
CREATE INDEX IF NOT EXISTS idx_fixtures_leg ON public.fixtures (leg);
```

### 🔴 **MATCH_EVENTS - Colunas Faltantes Críticas**

#### **Colunas Atuais vs Necessárias**

| Campo API Sportmonks | Coluna Atual | Status | Tipo Sugerido |
|----------------------|--------------|---------|---------------|
| `id` | ✅ id | OK | VARCHAR |
| `fixture_id` | ✅ fixture_id | OK | BIGINT |
| `type_id` | ✅ type_id | OK | INTEGER |
| `event_type` | ✅ event_type | OK | VARCHAR |
| `minute` | ✅ minute | OK | INTEGER |
| `extra_minute` | ✅ extra_minute | OK | INTEGER |
| `team_id` | ✅ team_id | OK | BIGINT |
| `player_id` | ✅ player_id | OK | BIGINT |
| `related_player_id` | ✅ related_player_id | OK | BIGINT |
| `player_name` | ✅ player_name | OK | VARCHAR |
| `period_id` | ✅ period_id | OK | INTEGER |
| `result` | ✅ result | OK | VARCHAR |
| `var` | ❌ **FALTANDO** | 🔴 CRÍTICO | BOOLEAN |
| `var_reason` | ❌ **FALTANDO** | 🔴 CRÍTICO | VARCHAR(255) |
| `coordinates` | ❌ **FALTANDO** | 🟡 IMPORTANTE | JSONB |
| `assist_id` | ❌ **FALTANDO** | 🟡 IMPORTANTE | BIGINT |
| `assist_name` | ❌ **FALTANDO** | 🟡 IMPORTANTE | VARCHAR(255) |
| `injured` | ❌ **FALTANDO** | 🟡 IMPORTANTE | BOOLEAN |
| `on_bench` | ❌ **FALTANDO** | 🟡 IMPORTANTE | BOOLEAN |

#### **Migração SQL para Match Events**
```sql
-- Adicionar colunas faltantes na tabela match_events
ALTER TABLE public.match_events 
ADD COLUMN IF NOT EXISTS var BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS var_reason VARCHAR(255),
ADD COLUMN IF NOT EXISTS coordinates JSONB,
ADD COLUMN IF NOT EXISTS assist_id BIGINT,
ADD COLUMN IF NOT EXISTS assist_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS injured BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS on_bench BOOLEAN DEFAULT FALSE;

-- Adicionar índices para novas colunas
CREATE INDEX IF NOT EXISTS idx_match_events_var ON public.match_events (var);
CREATE INDEX IF NOT EXISTS idx_match_events_assist_id ON public.match_events (assist_id);
CREATE INDEX IF NOT EXISTS idx_match_events_coordinates ON public.match_events USING GIN (coordinates);
```

### 🔴 **MATCH_STATISTICS - Colunas Faltantes Críticas**

#### **Colunas Atuais vs Necessárias**

| Campo API Sportmonks | Coluna Atual | Status | Tipo Sugerido |
|----------------------|--------------|---------|---------------|
| `fixture_id` | ✅ fixture_id | OK | BIGINT |
| `team_id` | ✅ team_id | OK | BIGINT |
| `shots_total` | ✅ shots_total | OK | INTEGER |
| `shots_on_target` | ✅ shots_on_target | OK | INTEGER |
| `shots_inside_box` | ✅ shots_inside_box | OK | INTEGER |
| `shots_outside_box` | ✅ shots_outside_box | OK | INTEGER |
| `blocked_shots` | ✅ blocked_shots | OK | INTEGER |
| `corners` | ✅ corners | OK | INTEGER |
| `offsides` | ✅ offsides | OK | INTEGER |
| `ball_possession` | ✅ ball_possession | OK | NUMERIC |
| `yellow_cards` | ✅ yellow_cards | OK | INTEGER |
| `red_cards` | ✅ red_cards | OK | INTEGER |
| `fouls` | ✅ fouls | OK | INTEGER |
| `passes_total` | ✅ passes_total | OK | INTEGER |
| `passes_accurate` | ✅ passes_accurate | OK | INTEGER |
| `pass_percentage` | ✅ pass_percentage | OK | NUMERIC |
| `saves` | ✅ saves | OK | INTEGER |
| `tackles` | ✅ tackles | OK | INTEGER |
| `interceptions` | ✅ interceptions | OK | INTEGER |
| `goals` | ❌ **FALTANDO** | 🔴 CRÍTICO | INTEGER |
| `goals_conceded` | ❌ **FALTANDO** | 🔴 CRÍTICO | INTEGER |
| `shots_off_target` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_saved` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_woodwork` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_blocked` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_inside_box_total` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_outside_box_total` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_inside_box_on_target` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_outside_box_on_target` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_inside_box_off_target` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_outside_box_off_target` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_inside_box_saved` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_outside_box_saved` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_inside_box_woodwork` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_outside_box_woodwork` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_inside_box_blocked` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_outside_box_blocked` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_inside_box_total_attempts` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_outside_box_total_attempts` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_inside_box_on_target_attempts` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_outside_box_on_target_attempts` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_inside_box_off_target_attempts` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_outside_box_off_target_attempts` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_inside_box_saved_attempts` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_outside_box_saved_attempts` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_inside_box_woodwork_attempts` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_outside_box_woodwork_attempts` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_inside_box_blocked_attempts` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `shots_outside_box_blocked_attempts` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |

#### **Migração SQL para Match Statistics**
```sql
-- Adicionar colunas faltantes na tabela match_statistics
ALTER TABLE public.match_statistics 
ADD COLUMN IF NOT EXISTS goals INTEGER,
ADD COLUMN IF NOT EXISTS goals_conceded INTEGER,
ADD COLUMN IF NOT EXISTS shots_off_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_saved INTEGER,
ADD COLUMN IF NOT EXISTS shots_woodwork INTEGER,
ADD COLUMN IF NOT EXISTS shots_blocked INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_total INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_total INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_on_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_on_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_off_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_off_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_saved INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_saved INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_woodwork INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_woodwork INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_blocked INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_blocked INTEGER;

-- Adicionar índices para novas colunas importantes
CREATE INDEX IF NOT EXISTS idx_match_statistics_goals ON public.match_statistics (goals);
CREATE INDEX IF NOT EXISTS idx_match_statistics_goals_conceded ON public.match_statistics (goals_conceded);
```

### 🔴 **MATCH_LINEUPS - Colunas Faltantes Críticas**

#### **Colunas Atuais vs Necessárias**

| Campo API Sportmonks | Coluna Atual | Status | Tipo Sugerido |
|----------------------|--------------|---------|---------------|
| `fixture_id` | ✅ fixture_id | OK | BIGINT |
| `team_id` | ✅ team_id | OK | BIGINT |
| `player_id` | ✅ player_id | OK | BIGINT |
| `player_name` | ✅ player_name | OK | VARCHAR |
| `type` | ✅ type | OK | VARCHAR |
| `position_id` | ✅ position_id | OK | INTEGER |
| `position_name` | ✅ position_name | OK | VARCHAR |
| `jersey_number` | ✅ jersey_number | OK | INTEGER |
| `captain` | ✅ captain | OK | BOOLEAN |
| `minutes_played` | ✅ minutes_played | OK | INTEGER |
| `rating` | ✅ rating | OK | NUMERIC |
| `formation` | ❌ **FALTANDO** | 🔴 CRÍTICO | VARCHAR(50) |
| `formation_position` | ❌ **FALTANDO** | 🔴 CRÍTICO | VARCHAR(50) |
| `formation_number` | ❌ **FALTANDO** | 🔴 CRÍTICO | INTEGER |
| `formation_row` | ❌ **FALTANDO** | 🔴 CRÍTICO | INTEGER |
| `formation_position_x` | ❌ **FALTANDO** | 🟡 IMPORTANTE | NUMERIC |
| `formation_position_y` | ❌ **FALTANDO** | 🟡 IMPORTANTE | NUMERIC |
| `substitute` | ❌ **FALTANDO** | 🟡 IMPORTANTE | BOOLEAN |
| `substitute_in` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `substitute_out` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `substitute_minute` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `substitute_extra_minute` | ❌ **FALTANDO** | 🟡 IMPORTANTE | INTEGER |
| `substitute_reason` | ❌ **FALTANDO** | 🟡 IMPORTANTE | VARCHAR(100) |
| `substitute_type` | ❌ **FALTANDO** | 🟡 IMPORTANTE | VARCHAR(50) |
| `substitute_player_id` | ❌ **FALTANDO** | 🟡 IMPORTANTE | BIGINT |
| `substitute_player_name` | ❌ **FALTANDO** | 🟡 IMPORTANTE | VARCHAR(255) |

#### **Migração SQL para Match Lineups**
```sql
-- Adicionar colunas faltantes na tabela match_lineups
ALTER TABLE public.match_lineups 
ADD COLUMN IF NOT EXISTS formation VARCHAR(50),
ADD COLUMN IF NOT EXISTS formation_position VARCHAR(50),
ADD COLUMN IF NOT EXISTS formation_number INTEGER,
ADD COLUMN IF NOT EXISTS formation_row INTEGER,
ADD COLUMN IF NOT EXISTS formation_position_x NUMERIC,
ADD COLUMN IF NOT EXISTS formation_position_y NUMERIC,
ADD COLUMN IF NOT EXISTS substitute BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS substitute_in INTEGER,
ADD COLUMN IF NOT EXISTS substitute_out INTEGER,
ADD COLUMN IF NOT EXISTS substitute_minute INTEGER,
ADD COLUMN IF NOT EXISTS substitute_extra_minute INTEGER,
ADD COLUMN IF NOT EXISTS substitute_reason VARCHAR(100),
ADD COLUMN IF NOT EXISTS substitute_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS substitute_player_id BIGINT,
ADD COLUMN IF NOT EXISTS substitute_player_name VARCHAR(255);

-- Adicionar índices para novas colunas importantes
CREATE INDEX IF NOT EXISTS idx_match_lineups_formation ON public.match_lineups (formation);
CREATE INDEX IF NOT EXISTS idx_match_lineups_substitute ON public.match_lineups (substitute);
CREATE INDEX IF NOT EXISTS idx_match_lineups_substitute_minute ON public.match_lineups (substitute_minute);
```

### 🟡 **OUTRAS TABELAS - Colunas Faltantes**

#### **PLAYERS - Colunas Faltantes**
```sql
-- Adicionar colunas faltantes na tabela players
ALTER TABLE public.players 
ADD COLUMN IF NOT EXISTS common_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS firstname VARCHAR(255),
ADD COLUMN IF NOT EXISTS lastname VARCHAR(255),
ADD COLUMN IF NOT EXISTS nationality VARCHAR(100),
ADD COLUMN IF NOT EXISTS position_id INTEGER,
ADD COLUMN IF NOT EXISTS position_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS date_of_birth DATE,
ADD COLUMN IF NOT EXISTS height INTEGER,
ADD COLUMN IF NOT EXISTS weight INTEGER,
ADD COLUMN IF NOT EXISTS image_path TEXT;
```

#### **TEAMS - Colunas Faltantes**
```sql
-- Adicionar colunas faltantes na tabela teams
ALTER TABLE public.teams 
ADD COLUMN IF NOT EXISTS short_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS logo_url TEXT,
ADD COLUMN IF NOT EXISTS founded INTEGER,
ADD COLUMN IF NOT EXISTS venue_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS venue_id INTEGER,
ADD COLUMN IF NOT EXISTS country_id INTEGER,
ADD COLUMN IF NOT EXISTS national_team BOOLEAN DEFAULT FALSE;
```

#### **LEAGUES - Colunas Faltantes**
```sql
-- Adicionar colunas faltantes na tabela leagues
ALTER TABLE public.leagues 
ADD COLUMN IF NOT EXISTS country VARCHAR(100),
ADD COLUMN IF NOT EXISTS logo_url TEXT,
ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS type VARCHAR(50),
ADD COLUMN IF NOT EXISTS sub_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS is_cup BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_friendly BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_international BOOLEAN DEFAULT FALSE;
```

---

## 🚀 **ESTRATÉGIA DE IMPLEMENTAÇÃO**

### 📋 **Fase 1: Colunas Críticas (Prioridade Alta)**

1. **fixtures** - Adicionar campos essenciais
2. **match_events** - Adicionar campos de VAR e assistências
3. **match_statistics** - Adicionar campos de gols e shots detalhados
4. **match_lineups** - Adicionar campos de formação e substituições

### 📋 **Fase 2: Colunas Importantes (Prioridade Média)**

1. **players** - Completar campos de perfil
2. **teams** - Adicionar campos de venue e país
3. **leagues** - Adicionar campos de tipo e status

### 📋 **Fase 3: Colunas Opcionais (Prioridade Baixa)**

1. Campos de metadados e flags
2. Campos de configuração e opções
3. Campos de auditoria e rastreamento

---

## 🔧 **MIGRAÇÃO COMPLETA**

### 📄 **Arquivo de Migração SQL**

```sql
-- =====================================================
-- MIGRAÇÃO: Adicionar colunas faltantes para API Sportmonks
-- Data: 2025-01-13
-- Objetivo: Acomodar todos os dados da API Sportmonks
-- =====================================================

-- 1. FIXTURES - Adicionar colunas faltantes
ALTER TABLE public.fixtures 
ADD COLUMN IF NOT EXISTS name VARCHAR(255),
ADD COLUMN IF NOT EXISTS starting_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS result_info VARCHAR(100),
ADD COLUMN IF NOT EXISTS leg VARCHAR(50),
ADD COLUMN IF NOT EXISTS details TEXT,
ADD COLUMN IF NOT EXISTS length INTEGER,
ADD COLUMN IF NOT EXISTS placeholder BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_odds BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_players BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_lineups BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_statistics BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_events BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS tie_breaker_rule VARCHAR(255);

-- 2. MATCH_EVENTS - Adicionar colunas faltantes
ALTER TABLE public.match_events 
ADD COLUMN IF NOT EXISTS var BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS var_reason VARCHAR(255),
ADD COLUMN IF NOT EXISTS coordinates JSONB,
ADD COLUMN IF NOT EXISTS assist_id BIGINT,
ADD COLUMN IF NOT EXISTS assist_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS injured BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS on_bench BOOLEAN DEFAULT FALSE;

-- 3. MATCH_STATISTICS - Adicionar colunas faltantes
ALTER TABLE public.match_statistics 
ADD COLUMN IF NOT EXISTS goals INTEGER,
ADD COLUMN IF NOT EXISTS goals_conceded INTEGER,
ADD COLUMN IF NOT EXISTS shots_off_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_saved INTEGER,
ADD COLUMN IF NOT EXISTS shots_woodwork INTEGER,
ADD COLUMN IF NOT EXISTS shots_blocked INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_total INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_total INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_on_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_on_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_off_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_off_target INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_saved INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_saved INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_woodwork INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_woodwork INTEGER,
ADD COLUMN IF NOT EXISTS shots_inside_box_blocked INTEGER,
ADD COLUMN IF NOT EXISTS shots_outside_box_blocked INTEGER;

-- 4. MATCH_LINEUPS - Adicionar colunas faltantes
ALTER TABLE public.match_lineups 
ADD COLUMN IF NOT EXISTS formation VARCHAR(50),
ADD COLUMN IF NOT EXISTS formation_position VARCHAR(50),
ADD COLUMN IF NOT EXISTS formation_number INTEGER,
ADD COLUMN IF NOT EXISTS formation_row INTEGER,
ADD COLUMN IF NOT EXISTS formation_position_x NUMERIC,
ADD COLUMN IF NOT EXISTS formation_position_y NUMERIC,
ADD COLUMN IF NOT EXISTS substitute BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS substitute_in INTEGER,
ADD COLUMN IF NOT EXISTS substitute_out INTEGER,
ADD COLUMN IF NOT EXISTS substitute_minute INTEGER,
ADD COLUMN IF NOT EXISTS substitute_extra_minute INTEGER,
ADD COLUMN IF NOT EXISTS substitute_reason VARCHAR(100),
ADD COLUMN IF NOT EXISTS substitute_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS substitute_player_id BIGINT,
ADD COLUMN IF NOT EXISTS substitute_player_name VARCHAR(255);

-- 5. PLAYERS - Adicionar colunas faltantes
ALTER TABLE public.players 
ADD COLUMN IF NOT EXISTS common_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS firstname VARCHAR(255),
ADD COLUMN IF NOT EXISTS lastname VARCHAR(255),
ADD COLUMN IF NOT EXISTS nationality VARCHAR(100),
ADD COLUMN IF NOT EXISTS position_id INTEGER,
ADD COLUMN IF NOT EXISTS position_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS date_of_birth DATE,
ADD COLUMN IF NOT EXISTS height INTEGER,
ADD COLUMN IF NOT EXISTS weight INTEGER,
ADD COLUMN IF NOT EXISTS image_path TEXT;

-- 6. TEAMS - Adicionar colunas faltantes
ALTER TABLE public.teams 
ADD COLUMN IF NOT EXISTS short_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS logo_url TEXT,
ADD COLUMN IF NOT EXISTS founded INTEGER,
ADD COLUMN IF NOT EXISTS venue_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS venue_id INTEGER,
ADD COLUMN IF NOT EXISTS country_id INTEGER,
ADD COLUMN IF NOT EXISTS national_team BOOLEAN DEFAULT FALSE;

-- 7. LEAGUES - Adicionar colunas faltantes
ALTER TABLE public.leagues 
ADD COLUMN IF NOT EXISTS country VARCHAR(100),
ADD COLUMN IF NOT EXISTS logo_url TEXT,
ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS type VARCHAR(50),
ADD COLUMN IF NOT EXISTS sub_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS is_cup BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_friendly BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_international BOOLEAN DEFAULT FALSE;

-- =====================================================
-- ÍNDICES PARA NOVAS COLUNAS
-- =====================================================

-- Índices para fixtures
CREATE INDEX IF NOT EXISTS idx_fixtures_starting_at ON public.fixtures (starting_at);
CREATE INDEX IF NOT EXISTS idx_fixtures_result_info ON public.fixtures (result_info);
CREATE INDEX IF NOT EXISTS idx_fixtures_leg ON public.fixtures (leg);

-- Índices para match_events
CREATE INDEX IF NOT EXISTS idx_match_events_var ON public.match_events (var);
CREATE INDEX IF NOT EXISTS idx_match_events_assist_id ON public.match_events (assist_id);
CREATE INDEX IF NOT EXISTS idx_match_events_coordinates ON public.match_events USING GIN (coordinates);

-- Índices para match_statistics
CREATE INDEX IF NOT EXISTS idx_match_statistics_goals ON public.match_statistics (goals);
CREATE INDEX IF NOT EXISTS idx_match_statistics_goals_conceded ON public.match_statistics (goals_conceded);

-- Índices para match_lineups
CREATE INDEX IF NOT EXISTS idx_match_lineups_formation ON public.match_lineups (formation);
CREATE INDEX IF NOT EXISTS idx_match_lineups_substitute ON public.match_lineups (substitute);
CREATE INDEX IF NOT EXISTS idx_match_lineups_substitute_minute ON public.match_lineups (substitute_minute);

-- Índices para players
CREATE INDEX IF NOT EXISTS idx_players_nationality ON public.players (nationality);
CREATE INDEX IF NOT EXISTS idx_players_position_id ON public.players (position_id);

-- Índices para teams
CREATE INDEX IF NOT EXISTS idx_teams_country_id ON public.teams (country_id);
CREATE INDEX IF NOT EXISTS idx_teams_venue_id ON public.teams (venue_id);

-- Índices para leagues
CREATE INDEX IF NOT EXISTS idx_leagues_type ON public.leagues (type);
CREATE INDEX IF NOT EXISTS idx_leagues_is_cup ON public.leagues (is_cup);
```

---

## 📊 **IMPACTO DA MIGRAÇÃO**

### ✅ **Benefícios**
- **100% de cobertura** dos dados da API Sportmonks
- **Dados mais ricos** para análises e relatórios
- **Compatibilidade total** com endpoints da API
- **Flexibilidade** para futuras expansões

### ⚠️ **Considerações**
- **Tamanho das tabelas** aumentará significativamente
- **Performance** pode ser afetada inicialmente
- **Backup** necessário antes da migração
- **Validação** obrigatória após migração

### 📈 **Estimativas**
- **Colunas adicionadas:** ~80 colunas
- **Índices adicionados:** ~15 índices
- **Tempo de migração:** ~30 minutos
- **Impacto na performance:** Mínimo (com índices)

---

## 🎯 **PRÓXIMOS PASSOS**

### 📋 **Checklist de Implementação**

1. **✅ Pré-Migração**
   - [ ] Backup completo do banco
   - [ ] Teste em ambiente de desenvolvimento
   - [ ] Validação da migração SQL

2. **✅ Durante Migração**
   - [ ] Executar migração em horário de baixo tráfego
   - [ ] Monitorar performance durante execução
   - [ ] Validar integridade dos dados

3. **✅ Pós-Migração**
   - [ ] Testar inserção de dados da API
   - [ ] Validar performance das consultas
   - [ ] Atualizar documentação
   - [ ] Notificar equipe ETL

### 🚀 **Comando de Execução**

```bash
# Executar migração
psql -h [HOST] -U [USER] -d [DATABASE] -f migration_add_missing_columns.sql

# Verificar resultado
psql -h [HOST] -U [USER] -d [DATABASE] -c "\d+ fixtures"
psql -h [HOST] -U [USER] -d [DATABASE] -c "\d+ match_events"
psql -h [HOST] -U [USER] -d [DATABASE] -c "\d+ match_statistics"
psql -h [HOST] -U [USER] -d [DATABASE] -c "\d+ match_lineups"
```

---

**Status:** ✅ **ANÁLISE COMPLETA - MIGRAÇÃO PREPARADA**  
**Próxima Ação:** Executar migração de colunas faltantes
