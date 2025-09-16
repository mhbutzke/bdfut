# ETL Playbook — Sportmonks API 3.0 (Projeto)

## Objetivos
- Ingestão global com janela ampla e detalhamento condicional
- Incremental diário confiável, idempotente e observável
- Banco histórico no Supabase com MVs e índices

## Fluxo Principal
1) Dicionários (diário)
- `/core/types`, `/football/states` → armazenar local; evitar includes

2) Janela ampla (fixtures)
- `fixtures/between/{from}/{to}` com `include=participants,state,venue`
- Selecionar campos essenciais via `select`

3) Detalhamento de fixtures alterados
- Quando `updated_at`/delta indicar mudança: `include=events;statistics;lineups;referees`
- Persistir `matches`, `match_events`, `match_statistics`, `referees` (associação por `matches.referee_id`)

4) Estatísticas agregadas
- Calcular e atualizar MVs (por período, por 90min, disciplinares, xG quando disponível)
- Atualizar `referee_stats` via função de banco após cada batch

## Estratégias
- Idempotência: UPSERT com chaves determinísticas (IDs da API)
- Paginação: `filters=populate` em cargas iniciais (page size 1000)
- Incremental: `idAfter` + filtros de `updated_at` quando suportado
- Paralelismo controlado: por liga/temporada (evitar bursts de 429)

## Rate Limit
- 3000 req/h por entidade
- Backoff exponencial com jitter para 429; observar `rate_limit.remaining`
- Distribuir chamadas por entidade e por janela temporal

## Observabilidade
- Métricas por job: latência, volume, 2xx/4xx/5xx, 429
- Logs com `request_id`, `league_id`, `season_id`, janela consultada
- Alertas: falha de cron, taxa de 429 > limiar, backlog de fixtures

## Esquema e Índices (Supabase)
- Índices em `league_id`, `season_id`, `fixture_id`, `date`, `team_id`, `player_id`, `referee_id`
- Constraints de unicidade por combinadores (ex.: `fixture_id + event_minute + event_type` quando aplicável)
- MVs: atualizadas após ingest diário (jobs agendados)

## Segurança
- Tokens em `.env` (nunca logar/expor)
- RLS: leitura pública seletiva; escrita somente via Edge Functions (role de serviço)

## Checklists
- [ ] Dicionários sincronizados hoje
- [ ] Janela ampla executada
- [ ] Fixtures alterados detalhados
- [ ] MVs recalculadas
- [ ] Métricas e alertas verificados
