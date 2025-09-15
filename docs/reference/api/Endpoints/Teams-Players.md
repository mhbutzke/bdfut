# Teams & Players — Guia Prático

Fonte: `https://docs.sportmonks.com/football`

## Teams
- Endpoints: All, By ID, By Country ID, By Season ID, Search by Name
- Includes úteis: `country`, `venue`, `coach` (quando aplicável)
- Filtros comuns: `country_id`, `season_id`, `search`

## Players
- Endpoints: All, By ID, By Country ID, Search by Name, Last Updated
- Includes úteis: `teams`, `statistics` (quando aplicável)
- Filtros: `country_id`, `search`

## Team Squads
- Endpoints: By Team ID, Extended By Team ID, By Team and Season ID
- Uso: obter elencos por temporada/time, mapear minutos e posições

## Exemplos
- Times por temporada:
```
/v3/football/teams/seasons/{season_id}
```
- Squad por time e temporada:
```
/v3/football/squads/teams/{team_id}/seasons/{season_id}
```
- Jogadores por país:
```
/v3/football/players/countries/{country_id}
```

## Estratégia ETL (projeto)
- Sincronizar times por temporada (chaves: `team_id`, `season_id`).
- Carregar `squads` para consolidar elencos e relacionar com `players`.
- Atualizar jogadores por busca/últimos atualizados para acompanhar transferências.
- Índices: `team_id`, `season_id`, `player_id`, `country_id`.

## Boas práticas
- Cache de entidades estáveis (times) e atualização incremental de jogadores.
- Tratar homônimos com busca por ID da API e `short_code`.
- Usar `select` para reduzir payload e normalizar por 90min em análises.
