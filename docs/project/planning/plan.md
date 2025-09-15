## BDFut – Plano de Desenvolvimento

### Visão Geral
Enriquecer e manter um banco de dados no Supabase com dados completos e atualizados da API Sportmonks (ligas, seasons, teams, fixtures, events, statistics, lineups, venues, referees, players, coaches), com pipelines ETL robustos, históricos completos, atualizações incrementais, qualidade de dados, desempenho e observabilidade.

### Status Atual do Projeto ✅
**IMPLEMENTADO:**
- ✅ CLI funcional (`bdfut/cli.py`) com comandos básicos
- ✅ Core ETL (`SportmonksClient`, `SupabaseClient`, `ETLProcess`)
- ✅ Configuração centralizada (`Config` com validação)
- ✅ Scripts ETL extensivos (25+ scripts de enriquecimento)
- ✅ Migrações Supabase (schema básico implementado)
- ✅ Sistema de logging estruturado
- ✅ Enriquecimento inicial das tabelas (15 tabelas populadas)
- ✅ Estrutura de projeto modular e organizada

**PENDENTE:**
- ⏳ Otimização da coleta de fixtures (problemas com filtros API v3)
- ⏳ Sistema de cache e rate limiting robusto
- ⏳ Testes automatizados
- ⏳ Documentação técnica completa
- ⏳ Dashboard de monitoramento

## 1. Configuração do Projeto

- [x] ~~Configuração do repositório~~ ✅ **CONCLUÍDO**
  - ✅ Estrutura modular implementada
  - ✅ pyproject.toml configurado
  - [ ] Ativar pre-commit (black, flake8, isort, mypy)
  - [ ] Configurar GitHub Actions (lint, testes, segurança, build)
  - [ ] Definir CODEOWNERS e PR templates

- [x] ~~Configuração do ambiente de desenvolvimento~~ ✅ **CONCLUÍDO**
  - ✅ `.env` padronizado com chaves necessárias
  - ✅ CLI funcional (`bdfut sync-base`, etc.)
  - [ ] Makefile com alvos: setup, lint, test, run, migrations
  - [ ] Dockerfile + docker-compose (db local opcional)
  - [ ] Scripts de bootstrap: `bdfut show-config`, `bdfut test-connection`

- [x] ~~Configuração do banco de dados~~ ✅ **PARCIALMENTE CONCLUÍDO**
  - ✅ Schema básico implementado (15 tabelas)
  - ✅ Migrações SQL versionadas (supabase/migrations)
  - [ ] Auditar constraints e índices existentes
  - [ ] Habilitar extensões úteis (pgcrypto, uuid-ossp)
  - [ ] Considerar partitioning por data para fixtures

- [x] ~~Estrutura inicial do projeto~~ ✅ **CONCLUÍDO**
  - ✅ `bdfut/core` validado e funcional
  - ✅ Sistema de logs estruturado implementado
  - [ ] Criar tabela de metadados ETL (`etl_jobs`, `etl_checkpoints`, `api_cache`)

## 2. Base do Backend

- [x] ~~Migrações e modelos do banco de dados~~ ✅ **CONCLUÍDO**
  - ✅ Entidades implementadas: `countries`, `states`, `types`, `leagues`, `seasons`, `stages`
  - ✅ Competição e jogo:
    - ✅ `fixtures` (FKs para league, season, venue; chaves naturais Sportmonks)
    - ✅ `match_events` (tipos, minuto, jogador, time, período)
    - ✅ `match_statistics` (por fixture+team; métricas padronizadas)
    - ✅ `match_lineups` (fixture+team+player; posição, formação, capitão)
  - ✅ Pessoas e locais:
    - ✅ `players`, `coaches`, `referees`, `venues`, `teams`
  - [ ] Apoio:
    - [ ] `api_cache` (chave: endpoint+params; TTL)
    - [ ] `etl_jobs`, `etl_checkpoints` (idempotência, retomada)
  - [ ] Constraints e índices:
    - [ ] Auditar unicidade por `sportmonks_id`
    - [ ] FKs rigorosas (ON UPDATE/DELETE)
    - [ ] Índices: `fixtures(season_id, starting_at)`, `events(fixture_id, minute)`, `statistics(fixture_id, team_id)`

- [x] ~~Sistema de autenticação~~ ✅ **CONCLUÍDO**
  - ✅ Gestão segura de `SUPABASE_SERVICE_KEY`
  - [ ] RLS para tabelas expostas publicamente (se houver API pública)

- [x] ~~Serviços e utilitários principais~~ ✅ **CONCLUÍDO**
  - ✅ Cliente Sportmonks com retries/backoff, paginação
  - ✅ Cliente Supabase com upsert idempotente
  - [ ] Cache (memória + `api_cache` com TTL e invalidadores)
  - ✅ Serializadores/normalizadores (mapeamento de tipos, nomes, enums)

- [ ] Estrutura base da API
  - [ ] API interna (opcional) para consumo por dashboards: fixtures, events, stats agregadas
  - [ ] Endpoints read-only + paginação + filtros padrão (league, season, date range)

## 3. Backend Específico de Funcionalidades

- [ ] Endpoints da API para cada funcionalidade (opcional)
  - `/leagues`, `/seasons`, `/fixtures`, `/fixtures/{id}/events`, `/teams/{id}/stats`, `/players/{id}/seasons`

- [x] ~~Implementação da lógica de negócios~~ ✅ **PARCIALMENTE CONCLUÍDO**
  - ✅ ETL Base:
    - ✅ Coletar `states`, `types`, `countries` (backfill completo implementado)
  - ✅ Ligas/Seasons:
    - ✅ `get_league_by_id(include=seasons)`, backfill histórico, marcação `is_current`
  - ✅ Times/Elencos:
    - ✅ `get_teams_by_season(include=venue)`, elencos ativos por season
    - ✅ `get_player_by_id`, `get_coaches_by_team`, dedupe por `sportmonks_id`
  - ⚠️ Fixtures:
    - ⚠️ **PROBLEMA IDENTIFICADO**: Filtros de temporada não funcionam na API v3
    - ✅ Paginação implementada
    - ✅ Includes suportados (participants, state, venue, events, statistics, lineups, referees)
    - [ ] **CRÍTICO**: Resolver estratégia de coleta por data/período
    - [ ] Backfill histórico: últimas 3-5 seasons por liga principal; em lote
    - [ ] Incremental: varrer por `updated_at` ou janelas rolantes
  - ✅ Eventos/Estatísticas/Lineups:
    - ✅ Normalização consistente dos tipos (gols, cartões, VAR, pênaltis, substituições)
    - ✅ Estatísticas por time e período; cálculo de derivadas
    - ✅ Lineups com posições padronizadas e formações por time

- [x] ~~Validação e processamento de dados~~ ✅ **CONCLUÍDO**
  - ✅ Regras de validação (campos obrigatórios; ranges; enums)
  - ✅ Canonicalização de nomes (times/jogadores com aliases)
  - ✅ Deduplicação idempotente (upsert por `sportmonks_id`)
  - [ ] Rejeições registradas em `etl_rejections` com motivo

- [x] ~~Integração com serviços externos~~ ✅ **CONCLUÍDO**
  - ✅ Sportmonks v3 com conformidade a endpoints e limites
  - [ ] (Opcional) CDN de imagens (badges, fotos) via Supabase Storage

## 4. Base do Frontend

- [ ] Configuração do framework de UI
  - Next.js/Vite (sugestão) para dashboard interno de ETL/observabilidade
  - Integração com Supabase Auth (se necessário)

- [ ] Biblioteca de componentes
  - Tabela de jobs, cards de métricas, gráficos de volume de eventos/fixtures

- [ ] Sistema de rotas
  - `/etl/overview`, `/etl/jobs`, `/data/quality`, `/metrics`

- [ ] Gerenciamento de estado
  - React Query/RTK Query para dados do dashboard (API interna)

- [ ] UI de autenticação
  - Acesso restrito ao dashboard (admin/dev)

## 5. Frontend Específico de Funcionalidades

- [ ] Componentes de UI para cada funcionalidade
  - Visão de fixtures recentes com status de ingestão e contagem de eventos
  - Tabelas de qualidade de dados (nulos, FKs quebradas, duplicatas)

- [ ] Layouts de páginas e navegação
  - Navegação por liga/season/fixture

- [ ] Interações do usuário e formulários
  - Reprocessar job de ETL
  - Acionar backfill de uma season/fixture específica

- [ ] Tratamento de erros e feedback
  - Toasts, banners de erro, vazão de reprocessamento

## 6. Integração

- [ ] Integração com API
  - SDK mínimo para consumo do dashboard
  - Padrões de paginação e cache client-side

- [ ] Conexões de funcionalidades ponta a ponta
  - Botão “Reprocessar fixture” → fila ETL → logs → atualização de métricas em tempo real

## 7. Testes

- [ ] Testes unitários
  - Clientes (Sportmonks/Supabase), normalizadores, validadores

- [ ] Testes de integração
  - ETL em sandbox Supabase (schema isolado)
  - Migrações idempotentes

- [ ] Testes ponta a ponta
  - Cenários: backfill de 3 seasons de liga principal; incremental diário; reprocessamento

- [ ] Testes de desempenho
  - Carga: ingestão de 100k events; medição de latência de upserts e índices

- [ ] Testes de segurança
  - Vazamento de chaves; RLS nas tabelas expostas; princípio do menor privilégio

## 8. Documentação

- [ ] Documentação da API
  - Especificação de endpoints internos (se aplicável) + exemplos

- [ ] Guias para usuários
  - Operação de ETL, execução de backfill, incremental e reprocesso

- [ ] Documentação para desenvolvedores
  - Estrutura do código, invariantes do schema, padrões de nome

- [ ] Documentação da arquitetura do sistema
  - Diagramas de fluxo ETL, modelo de dados, estratégias de partição/índices

## 9. Implantação

- [ ] Configuração de pipeline CI/CD
  - Linters, testes, migrações automáticas com preview e approvals

- [ ] Ambiente de staging
  - Projeto Supabase separado; dados mascarados/anônimos

- [ ] Ambiente de produção
  - Migrações versionadas e reversíveis; janelas de manutenção

- [ ] Configuração de monitoramento
  - Alertas (falhas de job, taxa de erro, latência)
  - Painéis de métricas (jobs/dia, registros processados, uso de API)

## 10. Manutenção

- [ ] Procedimentos para correção de bugs
  - Playbook de incidentes; rollback seguro; comunicados

- [ ] Processos de atualização
  - Rotas de atualização do schema compatíveis (expand/contract)

- [ ] Estratégias de backup
  - Snapshots diários; restauração testada regularmente

- [ ] Monitoramento de desempenho
  - Review periódico de índices/partições; vacuum/analyze; custo de queries

### Plano de Execução Atualizado (baseado no status atual)

**PRIORIDADE CRÍTICA - Semana 1:**
- [ ] **RESOLVER PROBLEMA DE FIXTURES**: Implementar coleta por data/período (sem filtros inválidos)
- [ ] Auditar e otimizar índices existentes no Supabase
- [ ] Implementar sistema de cache (`api_cache`) para otimização
- [ ] Criar tabelas de metadados ETL (`etl_jobs`, `etl_checkpoints`)

**PRIORIDADE ALTA - Semana 2:**
- [ ] Backfill histórico: últimas 3-5 seasons para ligas principais
- [ ] Implementar sincronização incremental diária
- [ ] Data quality checks automatizados
- [ ] Materialized views para agregados (player_season_stats, team_match_aggregates)

**PRIORIDADE MÉDIA - Semana 3:**
- [ ] Sistema de testes automatizados (unitários, integração, E2E)
- [ ] Documentação técnica completa
- [ ] Dashboard de monitoramento básico
- [ ] Hardening de segurança (RLS, validações)

**PRIORIDADE BAIXA - Semana 4:**
- [ ] Observabilidade completa (alertas, métricas)
- [ ] CI/CD pipeline
- [ ] Runbook de operações
- [ ] Otimizações de performance

### Status de Conclusão Atual: ~60% ✅

**CONCLUÍDO:**
- ✅ Estrutura base do projeto (100%)
- ✅ Core ETL e clientes (100%)
- ✅ Schema do banco de dados (90%)
- ✅ Enriquecimento inicial das tabelas (100%)
- ✅ Sistema de logging (100%)

**EM ANDAMENTO:**
- ⚠️ Coleta de fixtures (60% - problema com filtros API v3)
- ⚠️ Sistema de cache (0%)
- ⚠️ Testes automatizados (0%)

**PENDENTE:**
- ⏳ Dashboard de monitoramento (0%)
- ⏳ Documentação técnica (20%)
- ⏳ CI/CD pipeline (0%)

### Observações Finais Atualizadas:
- **CRÍTICO**: Resolver problema de coleta de fixtures por temporada (filtros não funcionam na API v3)
- **IMPORTANTE**: Implementar estratégia de coleta por data/período como alternativa
- **OTIMIZAÇÃO**: Criar views/materialized views para acesso rápido: "player_season_stats", "team_match_aggregates", "fixture_timeline_expanded"
- **SEGURANÇA**: Implementar RLS nas tabelas e validações de acesso
