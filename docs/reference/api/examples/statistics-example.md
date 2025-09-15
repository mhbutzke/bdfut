# Exemplo — Statistics (JSON truncado)

```
{
  "data": {
    "season_id": 22842,
    "team_id": 18710,
    "statistics": {
      "shots_total": 410,
      "shots_on_target": 186,
      "goals": 78,
      "passes_total": 20450,
      "passes_accurate": 18210,
      "yellow_cards": 68,
      "red_cards": 5
    }
  }
}
```

Notas:
- Disponibilidade por liga pode variar; xG pode estar em endpoint separado
- Normalizar por 90 minutos para comparações (ex.: `goals_per_90`)
- Manter MVs para tendências por rodada/mês
