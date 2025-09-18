# Análise de Mapeamento: API Sportmonks vs Banco de Dados BDFut

## Resumo Executivo

Esta análise compara a estrutura atual das tabelas do Supabase com os dados retornados pela API Sportmonks, identificando colunas faltantes e oportunidades de otimização.

## Tabela FIXTURES - Análise Detalhada

### Colunas Existentes vs API Sportmonks

#### ✅ Colunas Já Mapeadas Corretamente:
- `fixture_id` → `id` (API)
- `sport_id` → `sport_id` (API) 
- `league_id` → `league_id` (API)
- `season_id` → `season_id` (API)
- `stage_id` → `stage_id` (API)
- `round_id` → `round_id` (API)
- `state_id` → `state_id` (API)
- `venue_id` → `venue_id` (API)
- `group_id` → `group_id` (API)
- `aggregate_id` → `aggregate_id` (API)
- `starting_at` → `starting_at` (API)
- `starting_at_timestamp` → `starting_at_timestamp` (API)
- `length` → `length` (API)
- `placeholder` → `placeholder` (API)
- `has_odds` → `has_odds` (API)
- `has_premium_odds` → `has_premium_odds` (API)

#### ❌ Colunas Faltantes da API:
- `name` → Campo principal com nome da partida (ex: "Celtic vs Rangers")
- `result_info` → Informação do resultado (ex: "Celtic won after full-time")
- `leg` → Informação da perna do jogo (ex: "1/1")
- `details` → Detalhes adicionais da partida
- `last_processed_at` → Timestamp do último processamento
- `home_score` → Placar do time da casa
- `away_score` → Placar do time visitante

#### ⚠️ Colunas com Nomenclatura Diferente:
- Nossa: `home_team_id` / `away_team_id`
- API: Usa `participants` com `location: "home"/"away"`
- Nossa: `match_date`
- API: `starting_at` (já temos este campo)

### Análise de Outras Tabelas Principais

#### TEAMS
**Colunas Faltantes Importantes:**
- `display_name` (nome para exibição)
- `official_name` (nome oficial)
- `common_name` (nome comum)
- `national_team` (se é seleção nacional)
- `logo_path` (caminho do logo - temos `image_path`)

#### PLAYERS  
**Colunas Faltantes Importantes:**
- `detailed_position_id` (posição detalhada)
- `market_value_id` (valor de mercado)
- `injured` (se está lesionado)
- `minutes_played` (minutos jogados na temporada)

#### MATCH_EVENTS
**Estrutura Bem Mapeada, mas faltam:**
- `var` (VAR - Video Assistant Referee)
- `var_reason` (motivo do VAR)
- `coordinates` (coordenadas do evento no campo)

## Recomendações de Melhorias

### 1. Tabela FIXTURES - Prioridade ALTA
```sql
-- Adicionar colunas essenciais faltantes
ALTER TABLE fixtures ADD COLUMN name VARCHAR(255);
ALTER TABLE fixtures ADD COLUMN result_info TEXT;
ALTER TABLE fixtures ADD COLUMN leg VARCHAR(10) DEFAULT '1/1';
ALTER TABLE fixtures ADD COLUMN details TEXT;
ALTER TABLE fixtures ADD COLUMN last_processed_at TIMESTAMP;
ALTER TABLE fixtures ADD COLUMN home_score INTEGER DEFAULT 0;
ALTER TABLE fixtures ADD COLUMN away_score INTEGER DEFAULT 0;

-- Adicionar índices para performance
CREATE INDEX idx_fixtures_name ON fixtures(name);
CREATE INDEX idx_fixtures_starting_at ON fixtures(starting_at);
CREATE INDEX idx_fixtures_league_season ON fixtures(league_id, season_id);
```

### 2. Tabela TEAMS - Prioridade MÉDIA
```sql
-- Adicionar campos para melhor identificação
ALTER TABLE teams ADD COLUMN display_name VARCHAR(200);
ALTER TABLE teams ADD COLUMN official_name VARCHAR(255);
ALTER TABLE teams ADD COLUMN common_name VARCHAR(200);
ALTER TABLE teams ADD COLUMN national_team BOOLEAN DEFAULT FALSE;
ALTER TABLE teams ADD COLUMN logo_path TEXT; -- Renomear image_path para logo_path
```

### 3. Tabela PLAYERS - Prioridade MÉDIA
```sql
-- Adicionar campos para informações detalhadas
ALTER TABLE players ADD COLUMN detailed_position_id INTEGER;
ALTER TABLE players ADD COLUMN market_value_id INTEGER;
ALTER TABLE players ADD COLUMN injured BOOLEAN DEFAULT FALSE;
ALTER TABLE players ADD COLUMN minutes_played INTEGER DEFAULT 0;
```

### 4. Otimizações da Tabela FIXTURES como Centro Agregador

#### Colunas Agregadas Sugeridas:
```sql
-- Estatísticas agregadas para performance
ALTER TABLE fixtures ADD COLUMN total_goals INTEGER GENERATED ALWAYS AS (COALESCE(home_score, 0) + COALESCE(away_score, 0)) STORED;
ALTER TABLE fixtures ADD COLUMN goal_difference INTEGER GENERATED ALWAYS AS (COALESCE(home_score, 0) - COALESCE(away_score, 0)) STORED;
ALTER TABLE fixtures ADD COLUMN match_result VARCHAR(10); -- 'home_win', 'away_win', 'draw'

-- Flags para dados disponíveis (já existem algumas)
ALTER TABLE fixtures ADD COLUMN has_lineups BOOLEAN DEFAULT FALSE;
ALTER TABLE fixtures ADD COLUMN has_statistics BOOLEAN DEFAULT FALSE;
ALTER TABLE fixtures ADD COLUMN has_events BOOLEAN DEFAULT FALSE;
ALTER TABLE fixtures ADD COLUMN has_commentary BOOLEAN DEFAULT FALSE;

-- Metadados ETL
ALTER TABLE fixtures ADD COLUMN etl_processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE fixtures ADD COLUMN etl_version VARCHAR(20);
ALTER TABLE fixtures ADD COLUMN data_quality_score DECIMAL(3,2); -- 0.00 a 1.00
```

## Views Recomendadas

### 1. View de Fixtures Completas
```sql
CREATE VIEW v_fixtures_complete AS
SELECT 
    f.*,
    l.name as league_name,
    s.name as season_name,
    ht.name as home_team_name,
    at.name as away_team_name,
    v.name as venue_name,
    st.name as state_name
FROM fixtures f
LEFT JOIN leagues l ON f.league_id = l.league_id
LEFT JOIN seasons s ON f.season_id = s.season_id
LEFT JOIN teams ht ON f.home_team_id = ht.team_id
LEFT JOIN teams at ON f.away_team_id = at.team_id
LEFT JOIN venues v ON f.venue_id = v.venue_id
LEFT JOIN states st ON f.state_id = st.state_id;
```

### 2. View de Estatísticas por Liga
```sql
CREATE VIEW v_league_statistics AS
SELECT 
    l.league_id,
    l.name as league_name,
    s.season_id,
    s.name as season_name,
    COUNT(f.fixture_id) as total_matches,
    COUNT(CASE WHEN f.state_id = 5 THEN 1 END) as finished_matches,
    AVG(f.total_goals) as avg_goals_per_match,
    COUNT(CASE WHEN f.has_events THEN 1 END) as matches_with_events
FROM leagues l
JOIN seasons s ON l.league_id = s.league_id
LEFT JOIN fixtures f ON s.season_id = f.season_id
GROUP BY l.league_id, l.name, s.season_id, s.name;
```

## Plano de Implementação

### Fase 1: Fixtures Enhancement (Semana 1)
1. Adicionar colunas essenciais à tabela fixtures
2. Criar índices de performance
3. Implementar campos calculados
4. Testar performance das consultas

### Fase 2: Teams e Players Enhancement (Semana 2)  
1. Adicionar campos faltantes em teams
2. Adicionar campos faltantes em players
3. Criar constraints de integridade
4. Atualizar dados existentes

### Fase 3: Views e Otimizações (Semana 3)
1. Criar views principais
2. Implementar índices compostos
3. Otimizar consultas existentes
4. Documentar mudanças

### Fase 4: Validação e Deploy (Semana 4)
1. Scripts de validação de dados
2. Testes de performance
3. Deploy em produção
4. Monitoramento pós-deploy

## Métricas de Sucesso

- [ ] 100% das colunas principais da API mapeadas
- [ ] Redução de 50% no tempo de consultas agregadas
- [ ] Views funcionais para todas as consultas principais
- [ ] Zero perda de dados durante migrations
- [ ] Documentação completa da nova estrutura

## Riscos Identificados

1. **Alto**: Alteração da tabela fixtures com 67k registros
2. **Médio**: Impacto nas consultas existentes
3. **Baixo**: Inconsistências em dados históricos

## Próximos Passos

1. ✅ Análise da estrutura atual concluída
2. 🔄 Mapeamento da API em progresso  
3. ⏳ Criar scripts de migração
4. ⏳ Implementar testes de validação
5. ⏳ Deploy em ambiente de desenvolvimento
