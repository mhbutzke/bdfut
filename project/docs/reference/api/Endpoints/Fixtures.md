# Fixtures — Guia Prático

Fonte: `https://docs.sportmonks.com/football`

## Endpoints principais
- All Fixtures; By ID; Multiple IDs; By Date; Date Range; Date Range for Team; Head-to-Head; Search by Name; Upcoming/Past by TV/Market; Latest Updated

## Includes úteis
- `participants`, `events`, `statistics`, `lineups`, `referees`, `venue`, `scores`, `periods`
- Ex.: `&include=participants;events;statistics;lineups;referees;venue`

## Campos e filtros frequentes
- Filtros: `season_id`, `league_id`, `date`, `between`, `updated_at` (quando suportado), `idAfter`
- Seleção: `&select=id,name,season_id,starting_at,state_id,venue_id`

## Exemplos
- Fixture básico com participantes:
```
/v3/football/fixtures/{id}?include=participants
```
- Fixture detalhado (pós-jogo):
```
/v3/football/fixtures/{id}?include=participants;events;statistics;lineups;referees;venue
```
- Intervalo de datas (janela ampla) com metadados essenciais:
```
/v3/football/fixtures/between/{from}/{to}?include=participants,state,venue&select=id,league_id,season_id,starting_at,state_id,venue_id
```

## Estratégia ETL (projeto)
- Carga regular: `fixtures/between` com `include=participants,state,venue`.
- Detalhar somente fixtures **alterados**: `include=events;statistics;lineups;referees`.
- Incremental diário: combinar paginação e `updated_at`/`idAfter` quando disponível.
- Idempotência: UPSERT por IDs da API; chaves determinísticas.

## Boas práticas
- Limitar nested includes; usar `select` para enxugar payload.
- Cachear dicionários (states/types) localmente.
- Tratar 429 com backoff + jitter; observar `rate_limit.remaining`.
