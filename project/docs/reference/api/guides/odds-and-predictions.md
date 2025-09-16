# Guia — Odds e Predictions

## Objetivo
Consumir odds (pré/inplay) e predictions, respeitando limites de plano e performance.

## Endpoints
- Standard Odds Feed (pre/inplay): all/by fixture/by fixture+bookmaker/by fixture+market/last updated
- Premium Odds Feed: pre-match premium + históricos
- Predictions: probabilities, predictability by league, value bets

## Considerações de plano
- Parte dos feeds são **premium** e exigem assinatura específica.
- Histórico e atualizações dentro de intervalos são premium.

## Exemplos
- Odds pre-match por fixture:
```
/v3/football/odds/pre-match/fixtures/{fixture_id}
```
- Predictions por fixture:
```
/v3/football/predictions/fixtures/{fixture_id}
```

## ETL/Operação
- Usar endpoints de "latest/updated" para deltas frequentes.
- Armazenar snapshots com timestamp para séries e auditoria.
- Indexar por `fixture_id`, `bookmaker_id`, `market_id`.

## Boas práticas
- Evitar includes pesados; puxar odds por granularidade necessária.
- Validar cobertura por liga e definir fallback quando ausente.
