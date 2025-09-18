# 🔧 Diretrizes para Agente ETL - Task Master Organizado

## 🎯 Escopo Específico do Agente ETL

### ✅ **RESPONSABILIDADES DO AGENTE ETL:**
- **Organização do Schema** - Estruturar tabelas para operações ETL otimizadas
- **Coleta de Dados** - Implementar coleta incremental e batch processing
- **Performance ETL** - Otimizar rate limiting, cache e processamento
- **Validação de Dados** - Garantir qualidade e integridade dos dados coletados
- **Enriquecimento** - Automatizar enriquecimento de fixtures com dados completos
- **Monitoramento ETL** - Alertas e métricas específicas para operações ETL

### ❌ **FORA DO ESCOPO (REMOVIDO):**
- Frontend/UI development
- DevOps genérico (CI/CD, Docker)
- Documentação geral do projeto
- Monitoramento de infraestrutura
- Deploy de aplicações
- Configurações de ambiente genéricas

## 📋 Tasks Organizadas para ETL

### **Task 1: Organizar Schema das Tabelas** (PRIORIDADE ALTA)
**Objetivo**: Preparar estrutura do banco para operações ETL eficientes

#### Subtasks:
- **1.1** - Mapear colunas faltantes da API Sportmonks
- **1.2** - Criar migration para tabela fixtures 
- **1.3** - Otimizar índices para operações ETL

**Impacto**: Base fundamental para todas as operações ETL

### **Task 2: Coleta Incremental** (PRIORIDADE ALTA)
**Objetivo**: Implementar coleta eficiente que processa apenas dados novos/atualizados

**Funcionalidades**:
- Identificar fixtures novas desde última coleta
- Detectar fixtures atualizadas (mudança de status)
- Controle por timestamps (last_processed_at)
- Flags de controle (etl_version, data_quality_score)

### **Task 3: Performance ETL** (PRIORIDADE ALTA)
**Objetivo**: Otimizar velocidade e eficiência das operações ETL

**Otimizações**:
- Batch processing para múltiplas fixtures
- Cache Redis com TTL inteligente
- Rate limiting baseado em headers reais
- Retry policies com backoff exponencial

### **Task 4: Validação de Dados** (PRIORIDADE MÉDIA)
**Objetivo**: Garantir qualidade dos dados coletados

**Validações**:
- Integridade referencial entre tabelas
- Completude de dados obrigatórios
- Detecção de duplicatas
- Consistência de formatos
- Score de qualidade automático

### **Task 5: Enriquecimento Automático** (PRIORIDADE MÉDIA)
**Objetivo**: Automatizar coleta de dados complementares

**Dados Coletados**:
- Events (gols, cartões, substituições)
- Lineups (escalações, formações)
- Statistics (chutes, posse, passes)
- Participants (team IDs corretos)
- Referees e Periods

### **Task 6: Monitoramento ETL** (PRIORIDADE BAIXA)
**Objetivo**: Acompanhar performance e detectar problemas

**Métricas**:
- Registros processados por hora
- Taxa de sucesso das coletas
- Qualidade dos dados
- Performance de rate limiting
- Alertas para falhas críticas

## 🔧 Padrões ETL Estabelecidos

### **1. Estrutura de Dados Essencial**
```sql
-- Colunas obrigatórias para ETL eficiente:
ALTER TABLE fixtures ADD COLUMN name VARCHAR(255);           -- Nome da partida
ALTER TABLE fixtures ADD COLUMN result_info TEXT;            -- Resultado
ALTER TABLE fixtures ADD COLUMN home_score INTEGER;          -- Placar casa
ALTER TABLE fixtures ADD COLUMN away_score INTEGER;          -- Placar visitante
ALTER TABLE fixtures ADD COLUMN last_processed_at TIMESTAMP; -- Controle ETL
ALTER TABLE fixtures ADD COLUMN etl_version VARCHAR(20);     -- Versão ETL
ALTER TABLE fixtures ADD COLUMN data_quality_score DECIMAL(3,2); -- Qualidade
```

### **2. Índices para Performance ETL**
```sql
-- Índices essenciais para operações ETL:
CREATE INDEX idx_fixtures_etl_incremental ON fixtures(last_processed_at, etl_version);
CREATE INDEX idx_fixtures_etl_quality ON fixtures(data_quality_score) WHERE data_quality_score < 0.95;
CREATE INDEX idx_fixtures_etl_flags ON fixtures(has_events, has_lineups, has_statistics);
CREATE INDEX idx_fixtures_etl_date_league ON fixtures(starting_at, league_id);
```

### **3. Operações ETL Otimizadas**
```python
# Padrão para coleta incremental:
def collect_incremental_fixtures():
    # Buscar fixtures que precisam de atualização
    last_sync = get_last_sync_timestamp()
    fixtures_to_update = supabase.table('fixtures').select('fixture_id').gte('updated_at', last_sync).execute()
    
    # Processar em batches
    for batch in chunk_list(fixtures_to_update.data, 10):
        fixture_ids = [f['fixture_id'] for f in batch]
        enriched_data = sportmonks.get_fixtures_multi(fixture_ids, include='events;lineups;statistics')
        
        # Upsert com metadados ETL
        for fixture in enriched_data:
            fixture['last_processed_at'] = datetime.now()
            fixture['etl_version'] = 'v2.1'
            fixture['data_quality_score'] = calculate_quality_score(fixture)
        
        supabase.upsert_fixtures_batch(enriched_data)
```

## 🚀 Fluxo de Implementação

### **Fase 1: Preparação (Task 1)**
1. **1.1** - Mapear colunas faltantes ⏳
2. **1.2** - Criar migration fixtures ⏳  
3. **1.3** - Otimizar índices ⏳

### **Fase 2: Otimização (Tasks 2-3)**
4. **Task 2** - Coleta incremental ⏳
5. **Task 3** - Performance ETL ⏳

### **Fase 3: Qualidade (Tasks 4-5)**
6. **Task 4** - Validação de dados ⏳
7. **Task 5** - Enriquecimento automático ⏳

### **Fase 4: Monitoramento (Task 6)**
8. **Task 6** - Sistema de monitoramento ⏳

## 📊 Métricas de Sucesso para ETL

### **Performance**
- Coleta incremental < 5 minutos
- Batch processing 10 fixtures/requisição
- Cache hit rate > 70%
- Rate limiting respeitado (< 3000 req/hora)

### **Qualidade**
- Score de qualidade > 95%
- Zero duplicatas
- 100% integridade referencial
- Validação automática ativa

### **Operacional**
- Alertas funcionais para falhas
- Logs estruturados e pesquisáveis
- Rollback automático em caso de erro
- Monitoramento em tempo real

## 🎯 Comandos para Agente ETL

### **Navegação no Task Master:**
```bash
# Ver próxima task
task-master next

# Ver detalhes de task específica
task-master show 1

# Marcar subtask como em progresso
task-master set-status --id=1.1 --status=in-progress

# Atualizar progresso de subtask
task-master update-subtask --id=1.1 --prompt="Progresso: mapeamento 50% concluído"

# Marcar como concluída
task-master set-status --id=1.1 --status=done
```

### **Execução de Scripts ETL:**
```bash
# Navegar para scripts organizados
cd src/bdfut/scripts/etl_organized/

# Executar em ordem sequencial
python3 01_setup/01_setup_02_create_tables_supabase.py
python3 02_base_data/02_base_data_01_populate_countries.py
# ... continuar sequência
```

## ✅ **TASK MASTER REORGANIZADO E PRONTO!**

**Resumo da Reorganização:**
- ✅ **Escopo focado** apenas em ETL
- ✅ **6 tasks essenciais** priorizadas
- ✅ **3 subtasks detalhadas** para início
- ✅ **Dependências claras** mapeadas
- ✅ **Métricas de sucesso** definidas

**Próxima ação**: `task-master next` para ver primeira task prioritária! 🚀
