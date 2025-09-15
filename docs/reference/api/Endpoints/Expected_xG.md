# Expected (xG) — Guia Prático

Fonte: `https://docs.sportmonks.com/football`

## Endpoints
- Expected by Team
- Expected by Player
- Premium Expected Lineups (by Team, by Player)

## Cobertura e limitações
- Parte dos recursos de `expected` e `expected lineups` podem ser **premium** e requerem plano específico.
- Cobertura pode variar por liga/temporada; validar disponibilidade antes de depender para KPIs críticos.

## Exemplos
- xG por time:
```
/v3/football/expected/teams/{team_id}
```
- xG por jogador:
```
/v3/football/expected/players/{player_id}
```
- Expected lineups (premium):
```
/v3/football/expected-lineups/teams/{team_id}
```

## Estratégia ETL (projeto)
- Sincronizar xG quando disponível para complementar estatísticas ofensivas.
- Armazenar séries temporais de xG por time/jogador e por partida.
- Materialized Views para xG por 90min, rolling averages (últimos N jogos) e comparação com gols reais.

## Boas práticas
- Indicar cobertura e confidence/availability por liga.
- Tratar indisponibilidades com fallback para estatísticas tradicionais.
- Indexar por `team_id`, `player_id`, `fixture_id` para análises e joins frequentes.
