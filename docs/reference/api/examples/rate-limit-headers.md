# Exemplo — Rate Limit Headers/Body

```
{
  "data": { /* ... */ },
  "rate_limit": {
    "resets_in_seconds": 3540,
    "remaining": 2999,
    "requested_entity": "fixtures"
  }
}
```

Leitura prática:
- Se `remaining` < 50 e `resets_in_seconds` > 600s, reduzir taxa de requisições para a entidade.
- Em 429, aplicar backoff exponencial com jitter e refileirar a requisição.

Pseudo-código:
```
if (resp.status === 429) {
  wait = base * 2^attempt + random(0, jitter)
  sleep(min(wait, maxWait))
  retry()
} else if (resp.rate_limit) {
  tuneThrottle(entity, resp.rate_limit.remaining, resp.rate_limit.resets_in_seconds)
}
```
