# Análise de Colunas Faltantes - API Sportmonks vs Supabase

**Data:** 17 de Janeiro de 2025  
**Agente:** ETL Engineer  
**Task:** 1.1 - Mapear Colunas Faltantes da API  

## 🎯 Objetivo
Identificar quais colunas da API Sportmonks estão faltando nas tabelas do Supabase para otimizar operações ETL.

## 📊 Análise Realizada

### Tabela Principal: `fixtures` (67,085 registros)

**Estrutura Atual do Supabase:**
- ✅ **Campos Básicos:** fixture_id, league_id, season_id, home_team_id, away_team_id
- ✅ **Timestamps:** starting_at, created_at, updated_at
- ✅ **Flags:** has_events, has_lineups, has_statistics, has_odds
- ✅ **Metadados:** venue_id, state_id, round_id, stage_id
- ✅ **Nomes Enriquecidos:** venue_name, league_name, season_name, home_team_name, away_team_name

### ❌ COLUNAS FALTANTES IDENTIFICADAS:

#### **1. Colunas Essenciais para ETL (ALTA PRIORIDADE):**
```sql
-- Nome da partida
name VARCHAR(255) NOT NULL

-- Informação do resultado
result_info TEXT

-- Placar da partida
home_score INTEGER
away_score INTEGER

-- Perna da partida (ex: "1/1", "2/2")
leg VARCHAR(50)
```

#### **2. Colunas de Controle ETL (MÉDIA PRIORIDADE):**
```sql
-- Controle de processamento
last_processed_at TIMESTAMP

-- Versionamento do ETL
etl_version VARCHAR(20) DEFAULT 'v1.0'

-- ID do esporte (1 = futebol)
sport_id INTEGER DEFAULT 1

-- Dados adicionais da API
details JSONB
```

## 🔍 Evidências da API Sportmonks

**Exemplo de Resposta da API:**
```json
{
  "id": 19427494,
  "sport_id": 1,
  "league_id": 8,
  "season_id": 25583,
  "name": "West Ham United vs Tottenham Hotspur",
  "starting_at": "2025-09-13 16:30:00",
  "result_info": "Tottenham Hotspur won after full-time.",
  "leg": "1/1",
  "details": null,
  "length": 90,
  "placeholder": false
}
```

## 📋 Migration SQL Proposta

```sql
-- Migration: Adicionar colunas faltantes para ETL
-- Arquivo: 003_add_fixtures_etl_columns.sql

-- Colunas essenciais
ALTER TABLE fixtures ADD COLUMN name VARCHAR(255);
ALTER TABLE fixtures ADD COLUMN result_info TEXT;
ALTER TABLE fixtures ADD COLUMN home_score INTEGER;
ALTER TABLE fixtures ADD COLUMN away_score INTEGER;
ALTER TABLE fixtures ADD COLUMN leg VARCHAR(50);

-- Colunas de controle ETL
ALTER TABLE fixtures ADD COLUMN last_processed_at TIMESTAMP;
ALTER TABLE fixtures ADD COLUMN etl_version VARCHAR(20) DEFAULT 'v1.0';
ALTER TABLE fixtures ADD COLUMN sport_id INTEGER DEFAULT 1;
ALTER TABLE fixtures ADD COLUMN details JSONB;

-- Comentários para documentação
COMMENT ON COLUMN fixtures.name IS 'Nome da partida (ex: "Team A vs Team B")';
COMMENT ON COLUMN fixtures.result_info IS 'Informação do resultado da partida';
COMMENT ON COLUMN fixtures.home_score IS 'Placar do time da casa';
COMMENT ON COLUMN fixtures.away_score IS 'Placar do time visitante';
COMMENT ON COLUMN fixtures.leg IS 'Perna da partida (ex: "1/1", "2/2")';
COMMENT ON COLUMN fixtures.last_processed_at IS 'Timestamp do último processamento ETL';
COMMENT ON COLUMN fixtures.etl_version IS 'Versão do ETL que processou este registro';
COMMENT ON COLUMN fixtures.sport_id IS 'ID do esporte (1 = futebol)';
COMMENT ON COLUMN fixtures.details IS 'Dados adicionais da API Sportmonks';
```

## 🚀 Próximos Passos

1. **Task 1.2:** Criar migration SQL para adicionar colunas
2. **Task 1.3:** Otimizar índices para performance ETL
3. **Implementar:** Lógica de upsert para preencher dados existentes
4. **Validar:** Testes com dados reais da API

## 📊 Impacto Esperado

- **Performance ETL:** Melhoria significativa com campos dedicados
- **Qualidade de Dados:** Controle de versionamento e timestamps
- **Funcionalidade:** Suporte completo aos dados da API Sportmonks
- **Manutenibilidade:** Estrutura padronizada para operações ETL

---

**Status:** ✅ Concluído  
**Próxima Task:** 1.2 - Criar Migration para Fixtures
