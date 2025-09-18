# Scripts ETL - Coleta Incremental

Este diretório contém os scripts para coleta incremental de dados do Sportmonks API.

## Arquivos

- `incremental_collector.py` - Classe principal de coleta incremental
- `chunk_manager.py` - Gerenciador de chunks por liga/temporada
- `batch_collector.py` - Sistema de batch processing otimizado
- `monitoring.py` - Sistema de monitoramento e logs estruturados
- `config.py` - Configurações centralizadas
- `run_incremental_collection.py` - Script de execução com argumentos
- `run_chunk_processing.py` - Script de processamento de chunks
- `run_monitored_chunk_processing.py` - Script integrado com monitoramento
- `test_batch_processing.py` - Testes de batch processing
- `simple_batch_test.py` - Teste básico de validação
- `etl_dashboard.py` - Dashboard de visualização de métricas
- `requirements.txt` - Dependências Python
- `README.md` - Este arquivo

## Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com:

```bash
# API Sportmonks
SPORTMONKS_API_KEY=sua_chave_api_aqui

# Supabase
SUPABASE_CONNECTION_STRING=postgresql://usuario:senha@host:porta/database

# Opcional
ETL_LOG_LEVEL=INFO
```

### 2. Instalação de Dependências

```bash
cd project/scripts/etl
pip install -r requirements.txt
```

## Uso

### Coleta Padrão

```bash
python run_incremental_collection.py
```

### Coleta Específica de Liga

```bash
python run_incremental_collection.py --league-id 82 --batch-size 50
```

### Coleta de Teste

```bash
python run_incremental_collection.py --max-fixtures 10 --batch-size 10
```

### Modo Dry Run (Simulação)

```bash
python run_incremental_collection.py --dry-run
```

## Processamento de Chunks

### Processamento Padrão

```bash
python run_chunk_processing.py
```

### Processamento Limitado

```bash
python run_chunk_processing.py --max-chunks 10 --batch-size 200
```

### Processamento com Checkpoint

```bash
python run_chunk_processing.py --continue
```

### Modo Dry Run para Chunks

```bash
python run_chunk_processing.py --dry-run
```

## Batch Processing Otimizado

### Teste de Batch Processing

```bash
python test_batch_processing.py --test single --batch-size 10
```

### Comparação de Performance

```bash
python test_batch_processing.py --test compare --fixture-count 50
```

### Teste de Chunk com Batch

```bash
python test_batch_processing.py --test chunk --league-id 2451 --season-id 23026
```

### Teste Completo

```bash
python test_batch_processing.py --test all
```

## Processamento com Monitoramento

### Processamento Padrão com Monitoramento

```bash
python run_monitored_chunk_processing.py
```

### Processamento com Rastreamento de Performance

```bash
python run_monitored_chunk_processing.py --track-performance --max-chunks 10
```

### Processamento com Exportação de Métricas

```bash
python run_monitored_chunk_processing.py --export-metrics metrics.json
```

## Dashboard de Monitoramento

### Status Geral do Sistema

```bash
python etl_dashboard.py
```

### Resumo de Execução Específica

```bash
python etl_dashboard.py --execution-id etl_20250117_143022_abc123
```

### Logs Recentes

```bash
python etl_dashboard.py --logs --limit 50
```

### Métricas das Últimas 6 Horas

```bash
python etl_dashboard.py --metrics --hours 6
```

### Verificar Alertas

```bash
python etl_dashboard.py --alerts
```

### Exportar Dados

```bash
python etl_dashboard.py --export etl_data.json
```

## Argumentos Disponíveis

### Coleta Incremental (`run_incremental_collection.py`)
- `--batch-size`: Tamanho do lote (padrão: 100)
- `--league-id`: Filtrar por liga específica
- `--season-id`: Filtrar por temporada específica
- `--max-fixtures`: Máximo de fixtures para processar
- `--dry-run`: Apenas simula, não executa
- `--verbose`: Log detalhado

### Processamento de Chunks (`run_chunk_processing.py`)
- `--max-chunks`: Máximo de chunks para processar
- `--batch-size`: Tamanho do lote de fixtures por chunk (padrão: 100)
- `--min-fixtures`: Número mínimo de fixtures por chunk (padrão: 10)
- `--continue`: Continua processamento usando checkpoint
- `--clear-checkpoint`: Limpa checkpoint e inicia do zero
- `--dry-run`: Apenas simula, não executa
- `--verbose`: Log detalhado

### Testes de Batch Processing (`test_batch_processing.py`)
- `--test`: Tipo de teste (single, chunk, compare, all)
- `--batch-size`: Tamanho do lote para teste (padrão: 10)
- `--league-id`: ID da liga para teste de chunk
- `--season-id`: ID da temporada para teste de chunk
- `--fixture-count`: Número de fixtures para comparação (padrão: 20)
- `--verbose`: Log detalhado

### Processamento com Monitoramento (`run_monitored_chunk_processing.py`)
- `--max-chunks`: Máximo de chunks para processar
- `--batch-size`: Tamanho do lote de fixtures por chunk (padrão: 100)
- `--min-fixtures`: Número mínimo de fixtures por chunk (padrão: 10)
- `--continue`: Continua processamento usando checkpoint
- `--clear-checkpoint`: Limpa checkpoint e inicia do zero
- `--dry-run`: Apenas simula, não executa
- `--verbose`: Log detalhado
- `--track-performance`: Rastreamento detalhado de performance
- `--export-metrics`: Exporta métricas para arquivo JSON

### Dashboard (`etl_dashboard.py`)
- `--execution-id`: ID da execução para mostrar resumo detalhado
- `--logs`: Mostrar logs recentes
- `--limit`: Número de logs para mostrar (padrão: 20)
- `--metrics`: Mostrar resumo de métricas
- `--hours`: Horas para métricas (padrão: 24)
- `--alerts`: Verificar alertas do sistema
- `--export`: Exportar dados para arquivo JSON
- `--verbose`: Log detalhado

## Funcionalidades

### ✅ Implementadas

1. **Coleta Incremental Inteligente**
   - Identifica fixtures que precisam ser processadas
   - Sistema de priorização por score
   - Evita reprocessamento desnecessário

2. **Sistema de Chunks por Liga/Temporada**
   - Processamento em chunks otimizado
   - Sistema de checkpoint para recuperação
   - Priorização inteligente de chunks
   - Estatísticas detalhadas por chunk

3. **Sistema de Batch Processing Otimizado**
   - Endpoint multi da API Sportmonks (até 100 fixtures/requisição)
   - Redução de 80% nas chamadas à API
   - Rate limiting inteligente baseado em headers reais
   - Retry automático com backoff exponencial
   - Upsert otimizado em lote no banco de dados

4. **Sistema de Monitoramento Avançado**
   - Logs estruturados com timestamps
   - Métricas de performance em tempo real
   - Dashboard de visualização
   - Sistema de alertas automáticos
   - Rastreamento de execuções ETL
   - Exportação de dados para análise

5. **Rate Limiting**
   - Respeita limites da API Sportmonks
   - Retry automático em caso de rate limit
   - Intervalo configurável entre requests

6. **Flexibilidade**
   - Filtros por liga/temporada
   - Tamanho de lote configurável
   - Modo dry run para testes
   - Checkpoint e recuperação
   - Configuração dinâmica

### 🔄 Em Desenvolvimento

- Otimizações avançadas de performance
- Integração com sistemas de alerta externos
- Cache Redis para otimização de performance
- Rate limiting dinâmico baseado em headers da API
- Machine learning para otimização de chunks

## Logs

Os logs são salvos em:
- `etl_incremental.log` - Arquivo de log
- Console - Output em tempo real

## Exemplos de Log

```
2025-01-17 14:30:15 - INFO - === INICIANDO COLETA INCREMENTAL ===
2025-01-17 14:30:15 - INFO - Estatísticas antes da coleta: {'total_fixtures': 67085, 'unprocessed_fixtures': 67085}
2025-01-17 14:30:15 - INFO - Encontradas 100 fixtures para processar
2025-01-17 14:30:16 - INFO - Processando fixture 19154664 (prioridade: 100)
2025-01-17 14:30:17 - INFO - Fixture 19154664 processada com sucesso (qualidade: 100)
...
2025-01-17 14:35:20 - INFO - === COLETA INCREMENTAL CONCLUÍDA ===
2025-01-17 14:35:20 - INFO - Total processadas: 100
2025-01-17 14:35:20 - INFO - Sucessos: 98
2025-01-17 14:35:20 - INFO - Falhas: 2
2025-01-17 14:35:20 - INFO - Duração: 0:05:05
2025-01-17 14:35:20 - INFO - Taxa: 19.7 fixtures/min
```

## Troubleshooting

### Erro de Conexão com Banco

```
❌ Variáveis de ambiente faltando: SUPABASE_CONNECTION_STRING
```

**Solução**: Verifique se a variável `SUPABASE_CONNECTION_STRING` está definida corretamente.

### Erro de API Key

```
❌ Variáveis de ambiente faltando: SPORTMONKS_API_KEY
```

**Solução**: Verifique se a variável `SPORTMONKS_API_KEY` está definida corretamente.

### Rate Limit da API

```
WARNING - Rate limit atingido para fixture 12345
```

**Solução**: O script já implementa retry automático. Se persistir, aumente o `MIN_REQUEST_INTERVAL` no config.

## Próximos Passos

1. Implementar sistema de chunks (Task 2.3)
2. Adicionar monitoramento avançado (Task 2.4)
3. Executar testes completos (Task 2.5)
