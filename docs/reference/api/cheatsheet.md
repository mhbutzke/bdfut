# Cheatsheet — Sportmonks API 3.0

## Sintaxe
- `&select=field1,field2`
- `&include=rel1;rel2:fieldA,fieldB`
- `&filters=key:value`

## Exemplos rápidos
- Fixture com participantes:
```
/v3/football/fixtures/{id}?include=participants
```
- Fixture detalhado (pós-jogo):
```
/v3/football/fixtures/{id}?include=participants;events;statistics;lineups;referees;venue
```
- Intervalo de datas (janela ampla):
```
/v3/football/fixtures/between/{from}/{to}?include=participants,state,venue&select=id,league_id,season_id,starting_at,state_id,venue_id
```
- Estatísticas por temporada/time:
```
/v3/football/statistics/seasons/{season_id}/teams/{team_id}?select=team_id,season_id,shots_total,goals,passes_total
```
- Árbitros por temporada:
```
/v3/football/referees/seasons/{season_id}
```

## Dicas
- Use `filters=populate` para carga inicial + paginação (1000/page)
- Após carga, use `idAfter:<ID>` para delta
- Cacheie `types` e `states` localmente
- Trate 429 com backoff + jitter; monitore `rate_limit.remaining`
