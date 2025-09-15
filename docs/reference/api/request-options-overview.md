# Request Options — Overview

Fonte: `https://docs.sportmonks.com/football`

## Includes

- `include` adiciona entidades relacionadas na mesma resposta.
- Útil para reduzir múltiplas chamadas, mas aumenta payload/complexidade.
- Preferir cache local para dicionários (states/types) e includes estáveis.
- Suporte a **nested includes** com seleção de campos por relação.

## Selecting fields

- `select` limita os campos retornados da entidade base.
- Combine com `include` para reduzir payloads grandes.
- Ex.: `&select=id,name,season_id`

## Filtering

- `filters` aplica filtros específicos do endpoint.
- Pode aceitar múltiplos valores separados por vírgula.
- Exemplos comuns: por `season_id`, `date`, `updated_at`, `idAfter` (ver boas práticas).

## Selecting and filtering

- Combinação de `select` e `filters` para respostas enxutas e específicas.
- Recomendado para listas grandes, evitando transferir campos não usados.

## Ordering and sorting

- Ordenação conforme suporte do endpoint (ex.: por `starting_at`).
- Útil para paginação estável e reprocessos.

## Recomendações

- Evitar incluir relações profundas sem necessidade (nested profundo → alto custo).
- Para ingestões iniciais, preferir `filters=populate` (page size 1000) + paginação.
- Incremental: `idAfter` e/ou filtros por `updated_at` quando suportado.
- Sempre versionar localmente os dicionários para reduzir includes.
