# Syntax and Filters — Sportmonks API 3.0

Fonte: `https://docs.sportmonks.com/football`

## Sintaxe

| Parte | Uso | Exemplo |
|---|---|---|
| `&select=` | Seleciona campos da entidade base | `&select=name,season_id` |
| `&include=` | Inclui relações | `&include=lineups;events` |
| `&filters=` | Aplica filtros | `&filters=eventTypes:15` |
| `;` | Finaliza relação e inicia outra | `&include=lineups;events;participants` |
| `:` | Seleciona campos dentro do include | `&include=events:player_name,minute` |
| `,` | Separa múltiplos campos/IDs | `player_name,related_player_name` |

### Exemplo completo

```
/v3/football/fixtures/{id}
  ?select=id,name,season_id
  &include=participants:name,short_code;events:player_name,related_player_name,minute;lineups
  &filters=eventTypes:15
```

## Filtros comuns

- Por identificadores: `league_id`, `season_id`, `team_id`, `player_id`
- Por tempo: `date`, `between`, `updated_at` (quando suportado)
- Por delta incremental: `idAfter:<ID>` (pós-carga inicial)

## Recomendações

- Combine `select` + `include:<campos>` para reduzir payload
- Evite nested profundo sem necessidade
- Use paginação e `filters=populate` em cargas iniciais
