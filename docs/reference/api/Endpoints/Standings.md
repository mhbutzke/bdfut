# Standings & Topscorers — Guia Prático

Fonte: `https://docs.sportmonks.com/football`

## Standings
- Endpoints: All; By Season ID; By Round ID; Standing Correction by Season ID; Live Standings by League ID
- Includes úteis: `participants`, `stages`, `rounds` (quando aplicável)
- Filtros: `season_id`, `round_id`, `league_id`

## Topscorers
- Endpoints: By Season ID; By Stage ID
- Uso: artilharia por temporada/etapa; rankings de gols/assistências (conforme cobertura)

## Exemplos
- Classificação por temporada:
```
/v3/football/standings/seasons/{season_id}
```
- Topscorers por temporada:
```
/v3/football/topscorers/seasons/{season_id}
```

## Estratégia ETL (projeto)
- Sincronizar standings ao final de cada rodada (ou diariamente) para manter histórico.
- Guardar correções (standing corrections) quando existirem ajustes oficiais.
- Materialized Views para tendências de posição, pontos por rodada, G/P/E agregados.

## Boas práticas
- Indexar por `season_id`, `round_id`, `league_id`.
- Exibir timestamp da última atualização e indicador de live standings quando usado.
- Normalizar métricas para comparações multi-liga.
