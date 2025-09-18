# 🎯 PLANO FINAL DE ENRIQUECIMENTO - VALIDAÇÃO COMPLETA

**Data:** 17 de Setembro de 2025  
**Status:** ✅ Validado e Pronto para Execução  
**Objetivo:** Enriquecer match_events, match_lineups e match_statistics com dados da API Sportmonks

---

## 📊 STATUS ATUAL DAS TABELAS

- **match_events**: 62.781 registros
- **match_lineups**: 18.424 registros  
- **match_statistics**: 1.474 registros

**Fixtures que precisam de enriquecimento**: ~11.000 fixtures finalizadas

---

## ✅ MAPEAMENTO VALIDADO

### 🎯 MATCH_EVENTS - Mapeamento Confirmado

| Campo API | Campo Banco | Status | Observações |
|-----------|-------------|--------|-------------|
| `id` | `id` | ✅ | `{fixture_id}_{api_id}` |
| `fixture_id` | `fixture_id` | ✅ | FK para fixtures |
| `type_id` | `type_id` | ✅ | Tipo do evento (18=substituição, etc) |
| `addition` | `event_type` | ✅ | Descrição do evento (pode ser null) |
| `minute` | `minute` | ✅ | Minuto do evento |
| `extra_minute` | `extra_minute` | ✅ | Minuto extra |
| `participant_id` | `team_id` | ✅ | ID do time |
| `player_id` | `player_id` | ✅ | ID do jogador |
| `related_player_id` | `related_player_id` | ✅ | Jogador relacionado |
| `player_name` | `player_name` | ✅ | Nome do jogador |
| `related_player_name` | `related_player_name` | ✅ | Nome do jogador relacionado |
| `period_id` | `period_id` | ✅ | Período do jogo |
| `result` | `result` | ✅ | Resultado do evento |
| `injured` | `injured` | ✅ | Se jogador se machucou |
| `on_bench` | `on_bench` | ✅ | Se estava no banco |
| `sort_order` | `sort_order` | ✅ | Ordem dos eventos |

**Exemplo de dados encontrados:**
- 19 eventos por fixture
- Substituições (type_id=18), lesões, cartões
- Dados completos de jogadores e times

### 👥 MATCH_LINEUPS - Mapeamento Confirmado

| Campo API | Campo Banco | Status | Observações |
|-----------|-------------|--------|-------------|
| `id` | `id` | ✅ | `{fixture_id}_{api_id}` |
| `fixture_id` | `fixture_id` | ✅ | FK para fixtures |
| `team_id` | `team_id` | ✅ | ID do time |
| `player_id` | `player_id` | ✅ | ID do jogador |
| `player_name` | `player_name` | ✅ | Nome do jogador |
| `type_id` | `type` | ✅ | "lineup" (11) ou "substitute" (12) |
| `position_id` | `position_id` | ✅ | Posição do jogador |
| `jersey_number` | `jersey_number` | ✅ | Número da camisa |
| `formation_position` | `formation_position` | ✅ | Posição na formação |

**Exemplo de dados encontrados:**
- 40 lineups por fixture (titulares + substitutos)
- Dados completos de jogadores, posições e números

### 📈 MATCH_STATISTICS - Mapeamento Confirmado

**Estratégia:** Agrupar por `team_id` e mapear `type_id` para campos específicos

| Type ID | Campo Banco | Status | Descrição |
|---------|-------------|--------|-----------|
| 41 | `shots_total` | ✅ | Total de chutes |
| 42 | `shots_on_target` | ✅ | Chutes no gol |
| 43 | `shots_inside_box` | ✅ | Chutes dentro da área |
| 44 | `shots_outside_box` | ✅ | Chutes fora da área |
| 45 | `blocked_shots` | ✅ | Chutes bloqueados |
| 46 | `corners` | ✅ | Escanteios |
| 47 | `ball_possession` | ✅ | Posse de bola (%) |
| 48 | `yellow_cards` | ✅ | Cartões amarelos |
| 49 | `red_cards` | ✅ | Cartões vermelhos |
| 50 | `passes_total` | ✅ | Total de passes |
| 51 | `passes_accurate` | ✅ | Passes corretos |
| 52 | `pass_percentage` | ✅ | Percentual de passes |
| 53 | `saves` | ✅ | Defesas |
| 54 | `interceptions` | ✅ | Interceptações |

**Exemplo de dados encontrados:**
- 86 estatísticas por fixture (43 por time)
- 2 registros agrupados por time
- Dados completos de performance

---

## 🚀 ESTRATÉGIA DE EXECUÇÃO

### 1. **Scripts Otimizados Criados**
- `20_events_enrichment.py` - Enriquecimento de eventos
- `20_lineups_enrichment.py` - Enriquecimento de lineups  
- `20_statistics_enrichment.py` - Enriquecimento de estatísticas
- `20_test_single_fixture.py` - Validação de mapeamento

### 2. **Configurações Otimizadas**
- **Rate Limit**: 1 requisição por segundo
- **Batch Size**: 100 fixtures por lote
- **Upsert Strategy**: `on_conflict='id'`
- **Error Handling**: Logs detalhados e recuperação

### 3. **Controle de Qualidade**
- Verificar fixtures já enriquecidas
- Validar dados antes da inserção
- Log de progresso em tempo real
- Relatórios de performance

---

## 📋 DADOS IMPORTANTES PARA MERCADOS DE CARTÕES

### 🟨 Cartões Amarelos
- **Eventos**: `type_id` específico para cartões amarelos
- **Estatísticas**: Campo `yellow_cards` agregado por time
- **Jogadores**: Nomes e IDs dos jogadores que receberam cartões

### 🔴 Cartões Vermelhos  
- **Eventos**: `type_id` específico para cartões vermelhos
- **Estatísticas**: Campo `red_cards` agregado por time
- **Impacto**: Dados de substituições forçadas

### ⚽ Faltas e Agressões
- **Eventos**: `type_id` para faltas, agressões, etc.
- **Estatísticas**: Campo `fouls` agregado por time
- **Contexto**: Minuto, período, jogadores envolvidos

### 👤 Dados de Jogadores
- **Lineups**: Posições, números de camisa, tipo (titular/substituto)
- **Eventos**: Jogadores envolvidos em eventos importantes
- **Performance**: Estatísticas individuais e de time

---

## 🎯 PRÓXIMOS PASSOS

1. **✅ Validação completa** do mapeamento
2. **🔄 Executar enriquecimento** com scripts otimizados
3. **📊 Monitorar progresso** em tempo real
4. **🧪 Validar qualidade** dos dados inseridos
5. **📈 Análise final** para mercados de cartões

---

## 📊 ESTIMATIVAS DE PERFORMANCE

- **Fixtures para processar**: ~11.000
- **Tempo estimado**: ~18 minutos (1 req/seg)
- **Dados esperados**:
  - ~209.000 eventos (19 por fixture)
  - ~440.000 lineups (40 por fixture)  
  - ~22.000 estatísticas (2 por fixture)

---

**Status:** ✅ Pronto para execução  
**Próximo:** Executar enriquecimento completo
