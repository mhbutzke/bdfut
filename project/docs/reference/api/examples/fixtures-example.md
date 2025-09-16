# Exemplo — Fixtures (JSON truncado)

```
{
  "data": {
    "id": 19032598,
    "league_id": 1326,
    "season_id": 22842,
    "starting_at": "2024-07-14 19:00:00",
    "state_id": 5,
    "venue_id": 1944,
    "participants": [
      { "id": 18710, "name": "Spain", "meta": { "location": "home", "winner": true }},
      { "id": 18645, "name": "England", "meta": { "location": "away", "winner": false }}
    ],
    "events": [
      { "type_id": 14, "minute": 12, "player_id": 123, "related_player_id": null },
      { "type_id": 18, "minute": 77, "player_id": 456, "related_player_id": 789 }
    ],
    "statistics": [
      { "team_id": 18710, "shots_total": 12, "shots_on_target": 6, "passes_total": 520 },
      { "team_id": 18645, "shots_total": 8, "shots_on_target": 3, "passes_total": 465 }
    ]
  },
  "rate_limit": { "remaining": 2999, "resets_in_seconds": 3540, "requested_entity": "fixtures" }
}
```

Campos chave:
- `participants.meta.location`: home/away
- `events.type_id`: mapear via `types`
- `statistics`: agregar por período quando disponível

Inclui sugeridos:
- `participants;events;statistics;lineups;referees;venue`
