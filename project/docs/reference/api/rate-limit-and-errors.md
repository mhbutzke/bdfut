# Rate Limit and Errors — Sportmonks API 3.0

Fonte: `https://docs.sportmonks.com/football`

## Rate limit

- Padrão: **3000 requisições por entidade por hora**.
- Janela reinicia 1h após a primeira requisição.
- Ao estourar o limite da entidade: respostas **429** até reset; outras entidades continuam disponíveis.
- Resposta inclui `rate_limit`:
  - `resets_in_seconds`: segundos restantes para reset
  - `remaining`: requisições restantes na janela
  - `requested_entity`: entidade à qual o limite se aplica

## Boas práticas

- Implementar backoff exponencial com jitter para 429.
- Medir `remaining` e ajustar paralelismo.
- Distribuir chamadas por entidades quando possível.

## Error Codes & Exceptions

- **Error codes**: HTTP padrão (4xx/5xx) + documentação específica da API.
- **Include exceptions**: relações indisponíveis para certos endpoints.
- **Filtering and complexity exceptions**: filtros não suportados ou combinações custosas.
- **Other exceptions**: demais limitações documentadas na seção de erros.

## Observabilidade

- Logar `request_id`, entidade solicitada, latência e resultados (`status`, `remaining`).
- Criar alertas operacionais para taxa de 429 e 5xx acima de thresholds.
