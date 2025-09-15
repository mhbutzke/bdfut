# Statistics — Guia Prático

Fonte: `https://docs.sportmonks.com/football`

## Endpoints
- Season Statistics by Participant
- Stage Statistics by ID
- Round Statistics by ID

## Cobertura de métricas
- Métricas amplas de time/jogador/partida/temporada (lista oficial mantida em planilha pela Sportmonks).
- Verificar cobertura por liga e plano (algumas métricas são premium).

## Includes e seleção
- Combinar com `participants`, `teams`, `players` quando aplicável.
- Usar `select` para reduzir payload às métricas necessárias.

## Exemplos
- Estatísticas por temporada e participante (time):
```
/v3/football/statistics/seasons/{season_id}/teams/{team_id}
  ?select=team_id,season_id,shots_total,shots_on_target,goals,passes_total,passes_accurate
```
- Estatísticas por stage:
```
/v3/football/statistics/stages/{stage_id}
```
- Estatísticas por round:
```
/v3/football/statistics/rounds/{round_id}
```

## Estratégia ETL (projeto)
- Priorizar ingestão de estatísticas para fixtures **alterados** (pós-jogo) junto com `events`.
- Agregar estatísticas por período (1T/2T/prorrogação) quando disponível.
- Materialized Views para métricas derivadas (por 90min, tendências mensais, disciplinares, xG quando disponível).

## Boas práticas
- Normalizar por 90min para comparações entre times/ligas.
- Indexar colunas de junção (league_id, season_id, team_id, fixture_id).
- Validar completude de dados por liga (indicadores de coverage).
