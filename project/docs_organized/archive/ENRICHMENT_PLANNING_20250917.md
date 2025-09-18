# 📋 PLANO DE ENRIQUECIMENTO - MATCH_EVENTS, MATCH_LINEUPS, MATCH_STATISTICS

**Data:** 17 de Setembro de 2025  
**Status:** 🔄 Em Planejamento  
**Objetivo:** Definir padrões corretos para enriquecimento das tabelas de dados de partidas

---

## 🎯 OBJETIVOS

1. **Definir estrutura padrão** para cada tabela
2. **Mapear campos da API** para campos do banco
3. **Otimizar chamadas** da API Sportmonks
4. **Garantir qualidade dos dados** para análise de mercados de cartões

---

## 📊 ANÁLISE DA API SPORTMONKS

### 🔍 Dados Disponíveis por Fixture

**Endpoint:** `/fixtures/{fixture_id}?include=events;lineups;statistics`

#### 🎯 EVENTOS (Events)
```json
{
  "id": 33451388,
  "fixture_id": 11865351,
  "period_id": 3366956,
  "participant_id": 939,           // ID do time
  "type_id": 14,                   // Tipo do evento (gol, cartão, etc.)
  "section": "event",
  "player_id": 84570,               // ID do jogador
  "related_player_id": null,       // Jogador relacionado (substituição, assistência)
  "player_name": "Mikael Anderson",
  "related_player_name": null,
  "result": "1-0",                  // Resultado do evento
  "info": null,
  "addition": "1st Goal",          // Descrição adicional
  "minute": 90,                     // Minuto do evento
  "extra_minute": null,            // Minuto extra
  "injured": null,                 // Se jogador se machucou
  "on_bench": false,               // Se estava no banco
  "coach_id": null,
  "sub_type_id": null,
  "detailed_period_id": null,
  "rescinded": null,
  "sort_order": 1
}
```

#### 👥 LINEUPS (Lineups)
```json
{
  "id": 6807580,
  "sport_id": 1,
  "fixture_id": 11865351,
  "player_id": 82808,
  "team_id": 939,                   // ID do time
  "position_id": 24,                // Posição do jogador
  "formation_field": null,
  "type_id": 11,                    // 11=lineup inicial, 12=substituto
  "formation_position": null,
  "player_name": "Jesper Hansen",
  "jersey_number": 1                // Número da camisa
}
```

#### 📈 ESTATÍSTICAS (Statistics)
```json
{
  "id": 11461019,
  "fixture_id": 11865351,
  "type_id": 41,                    // Tipo da estatística
  "participant_id": 939,            // ID do time
  "data": {"value": 11},            // Valor da estatística
  "location": "home"                // home/away
}
```

---

## 🗄️ ESTRUTURA DAS TABELAS ATUAIS

### 📊 MATCH_EVENTS
```sql
- id (PK)
- fixture_id (FK)
- type_id
- event_type
- minute
- extra_minute
- team_id
- player_id
- related_player_id
- player_name
- period_id
- result
- created_at
- var
- var_reason
- coordinates
- assist_id
- assist_name
- injured
- on_bench
```

### 👥 MATCH_LINEUPS
```sql
- id (PK)
- fixture_id (FK)
- team_id
- player_id
- player_name
- type
- position_id
- position_name
- jersey_number
- captain
- minutes_played
- rating
- created_at
- formation
- formation_position
- formation_number
- formation_row
- formation_position_x
- formation_position_y
- substitute
- substitute_in
- substitute_out
- substitute_minute
- substitute_extra_minute
- substitute_reason
- substitute_type
- substitute_player_id
- substitute_player_name
```

### 📈 MATCH_STATISTICS
```sql
- id (PK)
- fixture_id (FK)
- team_id
- shots_total
- shots_on_target
- shots_inside_box
- shots_outside_box
- blocked_shots
- corners
- offsides
- ball_possession
- yellow_cards
- red_cards
- fouls
- passes_total
- passes_accurate
- pass_percentage
- saves
- tackles
- interceptions
- created_at
- goals
- goals_conceded
- shots_off_target
- shots_saved
- shots_woodwork
- shots_blocked
- shots_inside_box_total
- shots_outside_box_total
- shots_inside_box_on_target
- shots_outside_box_on_target
- shots_inside_box_off_target
- shots_outside_box_off_target
- shots_inside_box_saved
- shots_outside_box_saved
- shots_inside_box_woodwork
- shots_outside_box_woodwork
- shots_inside_box_blocked
- shots_outside_box_blocked
```

---

## 🎯 MAPEAMENTO PROPOSTO

### 🎯 MATCH_EVENTS - Mapeamento Otimizado

| Campo API | Campo Banco | Tipo | Observações |
|-----------|-------------|------|-------------|
| `id` | `id` | string | `{fixture_id}_{api_id}` |
| `fixture_id` | `fixture_id` | int | FK para fixtures |
| `type_id` | `type_id` | int | Tipo do evento (gol=14, cartão=etc) |
| `addition` | `event_type` | string | Descrição do evento |
| `minute` | `minute` | int | Minuto do evento |
| `extra_minute` | `extra_minute` | int | Minuto extra |
| `participant_id` | `team_id` | int | ID do time |
| `player_id` | `player_id` | int | ID do jogador |
| `related_player_id` | `related_player_id` | int | Jogador relacionado |
| `player_name` | `player_name` | string | Nome do jogador |
| `related_player_name` | `related_player_name` | string | Nome do jogador relacionado |
| `period_id` | `period_id` | int | Período do jogo |
| `result` | `result` | string | Resultado do evento |
| `injured` | `injured` | boolean | Se jogador se machucou |
| `on_bench` | `on_bench` | boolean | Se estava no banco |
| `sort_order` | `sort_order` | int | Ordem dos eventos |
| - | `created_at` | timestamp | Timestamp de criação |

**Campos removidos:** `var`, `var_reason`, `coordinates`, `assist_id`, `assist_name` (não disponíveis na API)

### 👥 MATCH_LINEUPS - Mapeamento Otimizado

| Campo API | Campo Banco | Tipo | Observações |
|-----------|-------------|------|-------------|
| `id` | `id` | string | `{fixture_id}_{api_id}` |
| `fixture_id` | `fixture_id` | int | FK para fixtures |
| `team_id` | `team_id` | int | ID do time |
| `player_id` | `player_id` | int | ID do jogador |
| `player_name` | `player_name` | string | Nome do jogador |
| `type_id` | `type` | string | "lineup" (11) ou "substitute" (12) |
| `position_id` | `position_id` | int | Posição do jogador |
| `jersey_number` | `jersey_number` | int | Número da camisa |
| `formation_position` | `formation_position` | int | Posição na formação |
| - | `created_at` | timestamp | Timestamp de criação |

**Campos removidos:** Todos os campos de substituição detalhada (não disponíveis na API)

### 📈 MATCH_STATISTICS - Mapeamento Otimizado

**Estratégia:** Agrupar estatísticas por `team_id` e mapear `type_id` para campos específicos

| Type ID | Campo Banco | Descrição |
|---------|-------------|-----------|
| 41 | `shots_total` | Total de chutes |
| 42 | `shots_on_target` | Chutes no gol |
| 43 | `shots_inside_box` | Chutes dentro da área |
| 44 | `shots_outside_box` | Chutes fora da área |
| 45 | `blocked_shots` | Chutes bloqueados |
| 46 | `corners` | Escanteios |
| 47 | `ball_possession` | Posse de bola (%) |
| 48 | `yellow_cards` | Cartões amarelos |
| 49 | `red_cards` | Cartões vermelhos |
| 50 | `passes_total` | Total de passes |
| 51 | `passes_accurate` | Passes corretos |
| 52 | `pass_percentage` | Percentual de passes |
| 53 | `saves` | Defesas |
| 54 | `interceptions` | Interceptações |

**Estrutura final:**
```sql
- id (PK) - {fixture_id}_{team_id}
- fixture_id (FK)
- team_id
- shots_total, shots_on_target, shots_inside_box, shots_outside_box
- blocked_shots, corners, ball_possession
- yellow_cards, red_cards
- passes_total, passes_accurate, pass_percentage
- saves, interceptions
- created_at
```

---

## 🚀 ESTRATÉGIA DE IMPLEMENTAÇÃO

### 1. **Chamadas da API**
- **Endpoint:** `/fixtures/{fixture_id}?include=events;lineups;statistics`
- **Rate Limit:** 1 requisição por segundo
- **Batch Size:** 100 fixtures por lote

### 2. **Processamento**
- **Eventos:** Inserir todos os eventos encontrados
- **Lineups:** Inserir todos os lineups encontrados
- **Estatísticas:** Agrupar por team_id e mapear type_id

### 3. **Controle de Qualidade**
- Verificar se fixture já foi enriquecida
- Validar dados antes da inserção
- Log de erros e sucessos

### 4. **Otimizações**
- Usar `upsert` com `on_conflict='id'`
- Processar em lotes para melhor performance
- Cache Redis para evitar requisições duplicadas

---

## 📋 PRÓXIMOS PASSOS

1. **✅ Análise completa** das estruturas
2. **🔄 Criar scripts otimizados** baseados no mapeamento
3. **🧪 Testar com amostra** pequena (100 fixtures)
4. **📊 Validar qualidade** dos dados
5. **🚀 Executar enriquecimento** completo (11k+ fixtures)
6. **📈 Análise final** para mercados de cartões

---

## 🎯 DADOS IMPORTANTES PARA MERCADOS DE CARTÕES

### 🟨 Cartões Amarelos
- **Eventos:** `type_id` específico para cartões amarelos
- **Estatísticas:** Campo `yellow_cards` agregado por time

### 🔴 Cartões Vermelhos
- **Eventos:** `type_id` específico para cartões vermelhos
- **Estatísticas:** Campo `red_cards` agregado por time

### ⚽ Faltas e Agressões
- **Eventos:** `type_id` para faltas, agressões, etc.
- **Estatísticas:** Campo `fouls` agregado por time

### 👤 Dados de Jogadores
- **Lineups:** Posições, números de camisa, tipo (titular/substituto)
- **Eventos:** Jogadores envolvidos em eventos importantes

---

**Status:** ✅ Planejamento concluído  
**Próximo:** Implementação dos scripts otimizados
