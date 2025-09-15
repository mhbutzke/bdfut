# Rate Limit Playbook — Sportmonks API 3.0

## Objetivos
Garantir alto throughput sem violar limites (3000 req/h por entidade), com resiliência a 429 e visibilidade operacional.

## Conceitos
- Limite por entidade/hora, janela deslizante reinicia 1h após a primeira chamada.
- Respostas incluem `rate_limit`: `remaining`, `resets_in_seconds`, `requested_entity`.

## Estratégias de Cliente
- Throttling por entidade: fila com capacidade dinâmica baseada em `remaining`.
- Backoff exponencial com jitter em 429 (ex.: base 1s, fator 2, jitter 0–250ms, teto 60s).
- Paralelismo controlado por partição (liga/temporada) para cargas.
- Preferir endpoints "latest/updated" para deltas frequentes.

## Planejamento de Janela
- Distribuir chamadas ao longo da hora (evitar bursts).
- Se `remaining/tempo_restante` < limiar, reduzir taxa e priorizar entidades críticas.

## SLOs e Alertas
- SLO: 429 < 0.5% das requisições/dia por entidade.
- Limiar de alerta: 429 > 2% em 15min; `remaining` < 5% faltando > 10min para reset.
- Métricas: por entidade {req_total, 2xx, 4xx, 5xx, 429, p50/p95 latência, remaining_min, resets_min}.

## Observabilidade
- Logar por requisição: `request_id`, entidade, status, `remaining`, `resets_in_seconds`.
- Dashboard: série temporal de `remaining` por entidade; heatmap de 429.

## Integração com ETL
- Jobs diários: agendar janelas com buffers; reduzir taxa automática ao detectar `remaining` baixo.
- Carga inicial: `filters=populate` + paginação em blocos, com throttle conservador.
- Incremental: `idAfter`/"latest" endpoints + limitação por entidade.

## Boas práticas
- Reuso de cache de dicionários (states/types) para cortar includes.
- `select` mínimo necessário; evitar nested includes profundos.
- Requisições idempotentes para retentativas seguras.
