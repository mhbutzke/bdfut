# Logs do Projeto BDFut

Esta pasta contém todos os arquivos de log gerados durante a execução dos scripts e processos ETL.

## 📁 Conteúdo da Pasta

### Arquivos de Log
- **etl_YYYYMMDD_HHMMSS.log** - Logs de execução do ETL com timestamp
- Logs são gerados automaticamente durante a execução dos scripts
- Contêm informações detalhadas sobre o processo de sincronização

## 📝 Formato dos Logs

### Estrutura do Log
```
2024-09-13 09:09:25 - INFO - Iniciando processo ETL
2024-09-13 09:09:26 - INFO - Conectando à API Sportmonks
2024-09-13 09:09:27 - INFO - Conectando ao Supabase
2024-09-13 09:09:28 - INFO - Sincronizando ligas principais
2024-09-13 09:09:30 - INFO - Liga 648 (Brasil - Serie A) processada
2024-09-13 09:09:32 - INFO - Liga 651 (Brasil - Serie B) processada
...
```

### Níveis de Log
- **INFO**: Informações gerais sobre o processo
- **WARNING**: Avisos sobre situações não críticas
- **ERROR**: Erros que impedem a execução
- **DEBUG**: Informações detalhadas para debugging

## 🔍 Como Analisar

### Verificar Última Execução
```bash
# Listar logs por data
ls -la logs/ | sort -k6,7

# Ver último log
tail -f logs/etl_20240913_091546.log
```

### Buscar Erros
```bash
# Buscar erros nos logs
grep -i "error" logs/*.log

# Buscar warnings
grep -i "warning" logs/*.log
```

### Analisar Performance
```bash
# Contar linhas processadas
grep -c "processada" logs/*.log

# Tempo de execução
grep "Iniciando\|Finalizando" logs/*.log
```

## 🧹 Manutenção

### Limpeza Automática
- Logs são criados automaticamente com timestamp único
- Não há limite automático de tamanho
- Recomenda-se limpeza manual periódica

### Backup de Logs Importantes
```bash
# Backup de logs do último mês
find logs/ -name "*.log" -mtime -30 -exec cp {} backup_logs/ \;
```

## ⚠️ Considerações

- **Tamanho**: Logs podem crescer rapidamente em execuções longas
- **Sensibilidade**: Podem conter informações sobre APIs e estruturas
- **Retenção**: Considere política de retenção baseada no espaço disponível
- **Análise**: Use para debugging e monitoramento de performance
