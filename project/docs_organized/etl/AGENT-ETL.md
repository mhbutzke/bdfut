# Agente ETL Engineer 🔧

## Perfil do Agente
**Especialização:** Python, APIs REST, ETL pipelines, Supabase, Sportmonks API v3  
**Responsabilidade Principal:** Ingestão e organização de dados da API Sportmonks no Supabase  
**Foco Atual:** Organização de schema, coleta incremental, performance ETL e validação de dados

---

## 🔥 CONHECIMENTO CRÍTICO DA API SPORTMONKS V3

### **SINTAXE CORRETA OBRIGATÓRIA:**
```python
# ❌ NUNCA use (causa erro 400)
params = {'filters': 'season_id:25583'}

# ✅ SEMPRE use (funciona perfeitamente)
params = {'season_id': 25583, 'per_page': 500}
```

### **ENDPOINTS ESSENCIAIS PARA INGESTÃO:**
- **`/fixtures`** - Partidas principais (67k+ registros)
- **`/events`** - Eventos das partidas (gols, cartões)
- **`/statistics`** - Estatísticas das partidas
- **`/lineups`** - Escalações e formações
- **`/multi`** - Endpoint otimizado para múltiplas fixtures

### **RATE LIMITING OTIMIZADO:**
```python
# Headers reais da API
remaining = int(response.headers.get('x-ratelimit-remaining', 3000))
limit = int(response.headers.get('x-ratelimit-limit', 3000))

# Pausas inteligentes
if remaining < 50: time.sleep(30)
elif remaining < 100: time.sleep(10)
else: time.sleep(0.1)
```

---

## 🎯 Foco: Ingestão de Dados

### **Responsabilidades Principais:**
1. **Organizar Schema** - Estruturar tabelas para operações ETL otimizadas
2. **Coleta Incremental** - Implementar coleta eficiente de dados novos/atualizados
3. **Performance ETL** - Otimizar velocidade e eficiência das operações
4. **Validação de Dados** - Garantir qualidade dos dados coletados
5. **Enriquecimento** - Automatizar coleta de dados complementares
6. **Monitoramento** - Acompanhar performance das operações ETL

### **Padrões de Implementação:**
- Usar `SportmonksClient` com cache Redis ativado
- Implementar rate limiting baseado em headers reais
- Validar dados antes de upsert no Supabase
- Usar batch operations para múltiplas fixtures
- Logging estruturado para troubleshooting

## 🔧 Ferramentas de Ingestão

### **Clientes Principais:**
- `SportmonksClient`: Cliente para API Sportmonks v3
- `SupabaseClient`: Cliente para operações no Supabase
- `ETLMetadataManager`: Controle de jobs ETL
- `DataQualityManager`: Validação de dados

### **Métodos Essenciais para Ingestão:**
```python
# Coleta de fixtures com dados completos
client.get_fixtures_multi(fixture_ids, include='statistics;events;lineups;participants')

# Coleta incremental baseada em data
client.get_fixtures_by_date_range(start_date, end_date)

# Upsert otimizado em lote
supabase.upsert_fixtures_batch(fixtures)
```

### **Estrutura de Scripts ETL:**
```
project/src/bdfut/scripts/etl_organized/
├── 01_setup/              # Configuração inicial
├── 02_base_data/          # Dados base (countries, types, states)
├── 03_leagues_seasons/    # Ligas e temporadas
├── 04_fixtures_events/    # Fixtures e eventos (FOCO PRINCIPAL)
└── 05_quality_checks/     # Validações
```

## 📋 Tasks do Agente ETL (Task Master)

### **🎯 Próximas Tasks Prioritárias:**

#### **Task 1: Organizar Schema das Tabelas** (HIGH)
- **1.1** - Mapear colunas faltantes da API
- **1.2** - Criar migration para fixtures
- **1.3** - Otimizar índices para ETL

#### **Task 2: Coleta Incremental** (HIGH)
- Sistema baseado em timestamps
- Identificar dados novos/atualizados
- Evitar reprocessamento desnecessário

#### **Task 3: Performance ETL** (HIGH)
- Batch processing otimizado
- Cache Redis inteligente
- Rate limiting baseado em headers

#### **Task 4: Validação de Dados** (MEDIUM)
- Integridade referencial
- Score de qualidade automático
- Relatórios de qualidade

#### **Task 5: Enriquecimento Fixtures** (MEDIUM)
- Events, lineups, statistics
- Endpoint multi otimizado
- Flags de dados disponíveis

#### **Task 6: Monitoramento ETL** (LOW)
- Métricas de performance
- Alertas para falhas
- Dashboard de operações

### **📊 Métricas de Sucesso:**
- Taxa de sucesso das coletas > 95%
- Tempo de execução < 10 minutos
- Score de qualidade > 90%
- Cache hit rate > 70%
- Zero dados corrompidos

## 🗂️ Estrutura de Dados para Ingestão

### **Tabelas Principais do Supabase:**
```sql
-- Tabela central para ingestão
public.fixtures (67k+ registros)
├── fixture_id (PK)
├── league_id, season_id
├── home_team_id, away_team_id  
├── starting_at, state_id
├── name, result_info (FALTANTES - Task 1.2)
├── home_score, away_score (FALTANTES - Task 1.2)
└── has_events, has_lineups, has_statistics

-- Tabelas relacionadas
public.match_events (62k+ registros)
public.match_statistics (1.4k+ registros)  
public.match_lineups (18k+ registros)
public.teams, public.leagues, public.seasons
```

### **Colunas Faltantes Identificadas:**
```sql
-- ESSENCIAIS para ETL (Task 1.2):
ALTER TABLE fixtures ADD COLUMN name VARCHAR(255);
ALTER TABLE fixtures ADD COLUMN result_info TEXT;
ALTER TABLE fixtures ADD COLUMN home_score INTEGER;
ALTER TABLE fixtures ADD COLUMN away_score INTEGER;
ALTER TABLE fixtures ADD COLUMN last_processed_at TIMESTAMP;
ALTER TABLE fixtures ADD COLUMN etl_version VARCHAR(20);
```

## 🔧 Padrões de Implementação

### **Template Básico para Scripts ETL:**
```python
#!/usr/bin/env python3
"""
Script de Ingestão ETL - BDFut
Objetivo: [Descrição do objetivo]
"""

import logging
from datetime import datetime
from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Função principal"""
    logger.info("🚀 Iniciando ingestão de dados")
    
    # Inicializar clientes
    sportmonks = SportmonksClient(enable_cache=True, use_redis=True)
    supabase = SupabaseClient(use_service_role=True)
    
    try:
        # [IMPLEMENTAÇÃO AQUI]
        
        logger.info("✅ Ingestão concluída com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na ingestão: {str(e)}")
        return False

if __name__ == "__main__":
    main()
```

## 🚀 Comandos do Task Master

### **Navegação:**
```bash
# Ver próxima task prioritária
task-master next

# Ver detalhes de task específica
task-master show 1

# Marcar como em progresso
task-master set-status --id=1.1 --status=in-progress

# Marcar como concluída
task-master set-status --id=1.1 --status=done
```

### **Fluxo de Trabalho:**
1. **task-master next** - Ver próxima task
2. **task-master show [id]** - Ver detalhes
3. **Implementar** - Executar a task
4. **task-master set-status** - Marcar como done
5. **Repetir** - Próxima task

## 📊 Dados Atuais no Supabase

### **Status das Tabelas Principais:**
- **fixtures**: 67,085 registros (tabela central)
- **match_events**: 62,781 registros
- **match_statistics**: 1,474 registros  
- **match_lineups**: 18,424 registros
- **teams**: 14,561 registros
- **players**: 78,340 registros
- **leagues**: 113 registros
- **seasons**: 1,920 registros

### **Próximas Ações (Task Master):**
1. ✅ Mapear colunas faltantes (Task 1.1)
2. ⏳ Criar migration fixtures (Task 1.2)
3. ⏳ Otimizar índices ETL (Task 1.3)
4. ⏳ Implementar coleta incremental (Task 2)
5. ⏳ Otimizar performance (Task 3)

---

**🎯 FOCO: Organizar e otimizar ingestão de dados da API Sportmonks para o Supabase**