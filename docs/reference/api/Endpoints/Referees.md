# Referees — Guia Prático

Fonte: `https://docs.sportmonks.com/football`

## Endpoints
- All Referees; Referee by ID; Referees by Country ID; Referees by Season ID; Referees Search by Name

## Uso típico
- Construir perfil disciplinar por árbitro (médias por partida de amarelos/vermelhos, pênaltis, faltas).
- Acompanhar partidas apitadas e distribuição por ligas/temporadas.

## Filtros e includes
- Filtros comuns: `country_id`, `season_id`, `search` (nome).
- Combinar com fixtures apitados do árbitro via joins locais.
- Includes: quando disponível, associar `fixtures` (ou via relacionamento local no DB).

## Exemplos
- Referees por temporada:
```
/v3/football/referees/seasons/{season_id}
```
- Busca por nome:
```
/v3/football/referees/search/{name}
```

## Estratégia ETL (projeto)
- Paginar e armazenar árbitros por país (ex.: BR) e por temporada relevante.
- Atualizar tabela `referees` e estatísticas derivadas via função `update_referee_stats` após ingestão de fixtures/cards.
- Enriquecer com contagens de cartões a partir de `match_cards` + `matches.referee_id`.

## Boas práticas
- Cachear lista base e atualizar incrementos (últimos atualizados quando disponível).
- Indexar por `referee_id`, `season_id` e `country_id` para consultas rápidas.
- Exibir indicadores de cobertura por liga/temporada.
