# Sportmonks Football API — Índice de Documentação

Fonte principal: `https://docs.sportmonks.com/football`

## Visão Geral
- [overview.md](overview.md)
- [endpoints-overview.md](endpoints-overview.md)
- [request-options-overview.md](request-options-overview.md)
- [syntax-and-filters.md](syntax-and-filters.md)
- [rate-limit-and-errors.md](rate-limit-and-errors.md)

## Endpoints (Guias Práticos)
- [Endpoints/Fixtures.md](Endpoints/Fixtures.md)
- [Endpoints/Statistics.md](Endpoints/Statistics.md)
- [Endpoints/Referees.md](Endpoints/Referees.md)
- [Endpoints/Teams-Players.md](Endpoints/Teams-Players.md)
- [Endpoints/Standings.md](Endpoints/Standings.md)
- [Endpoints/Expected_xG.md](Endpoints/Expected_xG.md)

## Coverage
- [coverage-matrix.md](coverage-matrix.md)

## Examples
- [examples/fixtures-example.md](examples/fixtures-example.md)
- [examples/statistics-example.md](examples/statistics-example.md)
- [examples/rate-limit-headers.md](examples/rate-limit-headers.md)

## Guides
- [guides/building-match-page.md](guides/building-match-page.md)
- [guides/odds-and-predictions.md](guides/odds-and-predictions.md)
- [guides/expected-xg-usage.md](guides/expected-xg-usage.md)
- [guides/rate-limit-playbook.md](guides/rate-limit-playbook.md)

## Tutoriais e Opções
- Request Options (originais): [Request Options/](Request%20Options/)
- Sintaxe e Códigos (originais): [Syntax e Codes/](Syntax%20e%20Codes/)
- Entities (originais): [Entities/](Entities/)
- Types e definicões (originais): [types_markdowns/](types_markdowns/)
- Boas práticas: [best-practices.md](best-practices.md)

## Playbooks (Projeto)
- [etl-playbook.md](etl-playbook.md) — ETL alinhado ao nosso projeto (janela ampla, incremental, MVs)
- [cheatsheet.md](cheatsheet.md) — Sintaxe rápida, exemplos e includes frequentes

## Como usar
1. Comece por overview para entender a API 3.0.
2. Veja `request-options-overview.md` e `syntax-and-filters.md` para aprender a montar as queries.
3. Use os guias de Endpoints para casos concretos (Fixtures/Statistics/…)
4. Aplique o `etl-playbook.md` para ingestão, cache de dicionários e idempotência.
