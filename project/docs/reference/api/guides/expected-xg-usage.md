# Guia — Expected (xG) na prática

## Objetivo
Usar dados de xG para análises ofensivas/defensivas, comparações e tendências.

## Endpoints
- `expected/teams/{team_id}`
- `expected/players/{player_id}`
- Expected lineups (premium): por time/jogador

## Limitações
- Cobertura varia por liga/temporada
- Alguns recursos são premium

## Uso recomendado
- Calcular xG por 90min e rolling averages (últimos N jogos)
- Comparar xG vs gols marcados/sofridos (over/under performance)
- Integrar com estatísticas tradicionais (chutes, passes) para contexto

## ETL
- Armazenar séries por partida/time/jogador
- MVs para rolling windows e normalização por 90min
- Indicadores de cobertura (por liga/season)
