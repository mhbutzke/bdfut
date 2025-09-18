# Plano de Enriquecimento de Tabelas - 17/09/2025

## 📊 Situação Atual

### Estrutura das Tabelas
- **match_events**: 12.657 registros (705 fixtures únicas) - ~1% cobertura
- **match_lineups**: 12.893 registros (293 fixtures únicas) - ~0.4% cobertura  
- **match_statistics**: 1.412 registros (706 fixtures únicas) - ~1% cobertura

### Total de Fixtures por Ano
- **2026**: 2.451 fixtures (futuras)
- **2025**: 6.977 fixtures (até hoje)
- **2024**: 29.483 fixtures
- **2023**: 27.364 fixtures
- **Total**: 67.085 fixtures

## 🎯 Objetivo

Enriquecer as tabelas com dados da API Sportmonks para análise de **mercados de cartões**, focando em:
- Cartões amarelos e vermelhos
- Faltas e VAR
- Escalações e substituições
- Estatísticas de jogo

## 📋 Tasks Criadas (15 tasks)

### Fase 1: Análise e Preparação
1. ✅ **Análise da Estrutura das Tabelas** - CONCLUÍDA
2. **Teste da API Sportmonks para Eventos** - PENDENTE
3. **Teste da API Sportmonks para Escalações** - PENDENTE
4. **Teste da API Sportmonks para Estatísticas** - PENDENTE
5. **Criação de Scripts de Teste** - PENDENTE

### Fase 2: Enriquecimento Incremental por Ano
6. **Enriquecimento de Fixtures 2025** - PENDENTE
7. **Validação de Dados 2025** - PENDENTE
8. **Enriquecimento de Fixtures 2024** - PENDENTE
9. **Validação de Dados 2024** - PENDENTE
10. **Enriquecimento de Fixtures 2023** - PENDENTE
11. **Validação de Dados 2023** - PENDENTE

### Fase 3: Análise e Otimização
12. **Análise de Dados para Mercados de Cartões** - PENDENTE
13. **Otimização de Scripts** - PENDENTE
14. **Documentação e Relatórios** - PENDENTE
15. **Monitoramento Contínuo** - PENDENTE

## 🔧 Campos Críticos Identificados

### match_events (Cartões e Eventos)
- `fixture_id`, `type_id`, `event_type`, `minute`, `extra_minute`
- `team_id`, `player_id`, `related_player_id`, `player_name`
- `period_id`, `result`, `var`, `var_reason`, `coordinates`

### match_lineups (Escalações)
- `fixture_id`, `team_id`, `player_id`, `player_name`, `type`
- `position_id`, `position_name`, `jersey_number`, `captain`
- `minutes_played`, `rating`, `formation`, `substitute`
- `substitute_in`, `substitute_out`, `substitute_minute`

### match_statistics (Estatísticas)
- `fixture_id`, `team_id`, `yellow_cards`, `red_cards`, `fouls`
- `shots_total`, `shots_on_target`, `corners`, `offsides`
- `ball_possession`, `passes_total`, `passes_accurate`, `pass_percentage`

## 🚀 Estratégia de Implementação

### Abordagem Incremental
1. **Pequenos testes** com validação
2. **2025 primeiro** (6.977 fixtures) - dados mais recentes
3. **2024 depois** (29.483 fixtures) - maior volume
4. **2023 por último** (27.364 fixtures) - base histórica

### Rate Limiting
- Respeitar limites da API Sportmonks
- Implementar delays entre chamadas
- Usar batch processing quando possível

### Validação de Dados
- Verificar integridade antes de inserir
- Usar upsert para evitar duplicatas
- Validar foreign keys (fixture_id, team_id, player_id)

## 📈 Métricas de Sucesso

### Cobertura Alvo
- **2025**: 80%+ das fixtures
- **2024**: 80%+ das fixtures  
- **2023**: 80%+ das fixtures

### Qualidade dos Dados
- Dados válidos e consistentes
- Campos críticos preenchidos
- Relacionamentos corretos (foreign keys)

## 🎯 Próximos Passos

1. **Testar API Sportmonks** para eventos, escalações e estatísticas
2. **Criar scripts de teste** com pequenos lotes
3. **Implementar enriquecimento** incremental por ano
4. **Validar qualidade** dos dados coletados
5. **Analisar dados** para mercados de cartões

---

**Status**: Task 1 concluída ✅  
**Próxima**: Task 2 - Teste da API Sportmonks para Eventos  
**Data**: 17/09/2025
