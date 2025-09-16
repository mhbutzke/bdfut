# Sportmonks Football API 3.0 — Overview

Fonte: `https://docs.sportmonks.com/football`

## Sumário

- Getting Started, Quick Start e Autenticação
- Request Options (Includes, Selecting, Filtering, Ordering)
- Syntax (parâmetros e notação de includes aninhados)
- Rate limit, Meta description, Error codes e exceções
- Endpoints & Entities (Livescores, Fixtures, States, Types, Leagues, Seasons, Statistics, Schedules, Stages, Rounds, Standings, Topscorers, Teams, Players, Squads, Coaches, Referees, Transfers, Venues, TV Stations, Expected, Predictions, Odds, News, Rivals, Commentaries)
- Tutorials & Guides (how-tos, exemplos e boas práticas)
- Changelog

## Destaques

- API 3.0: novo modelo de sintaxe (inclui `select`, `include`, `filters`), endpoints ampliados e documentação centrada em entidades.
- Entidades possuem rate limit independente (3000 req/hora por entidade). Veja Rate limit.
- Padronização de includes e nested includes com seleção de campos por relação.

## Conceitos-Chave

- Entidades principais: `fixtures`, `leagues`, `seasons`, `teams`, `players`, `referees`, `venues`, `statistics`, `standings`, `expected`, `odds`, `predictions`.
- Dicionários: `states` e `types` devem ser sincronizados e usados localmente para reduzir includes.
- Padrões de ingestão: carga inicial com `filters=populate` + incremental com `idAfter` e janela deslizante.

## Links Úteis

- Página inicial: `https://docs.sportmonks.com/football`
- Request Options: `https://docs.sportmonks.com/football/api/request-options`
- Syntax: `https://docs.sportmonks.com/football/api/syntax`
- Rate limit: `https://docs.sportmonks.com/football/api/rate-limit`
- Endpoints: `https://docs.sportmonks.com/football/endpoints-and-entities/endpoints`
- Entities: `https://docs.sportmonks.com/football/endpoints-and-entities/entities`
- Tutorials: `https://docs.sportmonks.com/football/tutorials-and-guides/tutorials`
- Guides: `https://docs.sportmonks.com/football/tutorials-and-guides/guides`
- Changelog: `https://docs.sportmonks.com/football/changelog/changelog`

## Resumo executivo

- Sintaxe universal:
  - `select` limita campos; `include` adiciona relações; `filters` filtra registros; `;` separa relações; `:` seleciona campos do include; `,` separa múltiplos valores.
- Request Options:
  - Prefira cache local de `types`/`states` para reduzir includes. Use `select` em todas as chamadas que retornam listas grandes.
- Rate limit:
  - 3000 req/h por entidade/hora. Tratar 429 com backoff + jitter e monitorar `rate_limit.remaining`.
- Endpoints críticos:
  - Fixtures (janela ampla `between` + detalhamento de alterados), Statistics (season/stage/round), Teams/Players/Squads, Referees (perfil disciplinar), Standings/Topscorers, Expected(xG) e Odds/Predictions (premium em alguns casos).
- ETL recomendado (projeto):
  - Diário: dicionários (`types`, `states`), janela ampla `fixtures/between` com `participants,state,venue`, detalhar apenas fixtures alterados (`events;statistics;lineups;referees`).
  - Banco: UPSERT idempotente com chaves determinísticas, MVs para 90min/períodos, índices por joins e filtros recorrentes.
