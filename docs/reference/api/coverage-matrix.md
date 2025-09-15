# Coverage Matrix — Recursos x Ligas/Planos (conceitual)

Fonte: `https://docs.sportmonks.com/football`

> Observação: a cobertura pode variar por plano e por liga/temporada. Use esta matriz como guia inicial e valide em ambiente real.

## Recursos principais
- Fixtures (global)
- Statistics (season/stage/round)
- Teams/Players/Squads/Referees
- Standings/Topscorers
- Expected (xG)
- Odds/Predictions

## Ligas (exemplos)
- Top-5 Europa (ENG, ESP, ITA, GER, FRA)
- CONMEBOL (Brasileirão, Argentino)
- MLS
- UCL/UEL/UCL novo formato

## Cobertura sugerida (alto nível)
- Fixtures: alta
- Statistics: alta, porém granularidade pode variar
- xG: parcial/premium em algumas ligas
- Odds/Predictions: disponível, com diferenciação premium
- Standings/Topscorers: alta
- Referees: boa, mas variação histórica por país

## Notas operacionais
- Verificar disponibilidade de `expected`/xG por liga antes de definir KPIs
- Odds premium/históricas requerem plano adequado
- Usar `Latest Updated` endpoints para delta em fixtures/odds
- Medir completude por liga (percentual de fixtures com stats/xG/odds)
