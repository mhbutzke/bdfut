# Runbook de Operações - BDFut 🚀

## Visão Geral

Este runbook fornece procedimentos operacionais detalhados para operação, manutenção e troubleshooting do sistema BDFut em produção.

## Índice

1. [Procedimentos de Deploy](#procedimentos-de-deploy)
2. [Procedimentos de Manutenção](#procedimentos-de-manutenção)
3. [Procedimentos de Backup](#procedimentos-de-backup)
4. [Procedimentos de Recovery](#procedimentos-de-recovery)
5. [Monitoramento e Alertas](#monitoramento-e-alertas)
6. [Procedimentos de Incidentes](#procedimentos-de-incidentes)
7. [Escalação e Contatos](#escalação-e-contatos)

---

## Procedimentos de Deploy

### Deploy em Desenvolvimento

#### Pré-requisitos
- Ambiente de desenvolvimento configurado
- Acesso ao repositório Git
- Credenciais de desenvolvimento

#### Procedimento

```bash
# 1. Acessar ambiente de desenvolvimento
ssh dev-server
cd /opt/bdfut

# 2. Backup da versão atual
cp -r bdfut bdfut.backup.$(date +%Y%m%d_%H%M%S)

# 3. Atualizar código
git fetch origin
git checkout main
git pull origin main

# 4. Atualizar dependências
source venv/bin/activate
pip install -e .

# 5. Executar migrações (se necessário)
supabase db push

# 6. Executar testes
pytest

# 7. Reiniciar serviços
sudo systemctl restart bdfut-dev

# 8. Verificar status
sudo systemctl status bdfut-dev
bdfut show-config
bdfut test-connection
```

#### Rollback

```bash
# 1. Parar serviço
sudo systemctl stop bdfut-dev

# 2. Restaurar backup
rm -rf bdfut
mv bdfut.backup.YYYYMMDD_HHMMSS bdfut

# 3. Reiniciar serviço
sudo systemctl start bdfut-dev

# 4. Verificar status
sudo systemctl status bdfut-dev
```

### Deploy em Produção

#### Pré-requisitos
- Ambiente de produção configurado
- Acesso ao repositório Git
- Credenciais de produção
- Janela de manutenção agendada

#### Procedimento

```bash
# 1. Acessar ambiente de produção
ssh prod-server
cd /opt/bdfut

# 2. Backup completo
./scripts/backup.sh

# 3. Atualizar código
git fetch origin
git checkout main
git pull origin main

# 4. Atualizar dependências
source venv/bin/activate
pip install -e .

# 5. Executar migrações (se necessário)
supabase db push

# 6. Executar testes
pytest

# 7. Manutenção programada
sudo systemctl stop bdfut-prod

# 8. Deploy
sudo systemctl start bdfut-prod

# 9. Verificar status
sudo systemctl status bdfut-prod
bdfut show-config
bdfut test-connection

# 10. Monitorar logs
tail -f logs/production.log
```

#### Rollback

```bash
# 1. Parar serviço
sudo systemctl stop bdfut-prod

# 2. Restaurar backup
./scripts/restore.sh

# 3. Reiniciar serviço
sudo systemctl start bdfut-prod

# 4. Verificar status
sudo systemctl status bdfut-prod
```

---

## Procedimentos de Manutenção

### Manutenção Diária

#### Verificação de Status

```bash
# 1. Verificar status dos serviços
sudo systemctl status bdfut-prod
sudo systemctl status redis

# 2. Verificar conectividade
bdfut test-connection

# 3. Verificar logs de erro
grep "ERROR" logs/production.log | tail -20

# 4. Verificar uso de recursos
df -h
free -h
top -p $(pgrep -f bdfut)

# 5. Verificar métricas de cache
redis-cli info stats
```

#### Limpeza de Logs

```bash
# 1. Rotacionar logs
sudo logrotate -f /etc/logrotate.d/bdfut

# 2. Limpar logs antigos
find logs/ -name "*.log" -mtime +30 -delete

# 3. Limpar dados temporários
rm -rf data/temp/*
```

### Manutenção Semanal

#### Backup de Dados

```bash
# 1. Backup do banco de dados
supabase db dump > backup_$(date +%Y%m%d).sql

# 2. Backup de configurações
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env config/

# 3. Backup de logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/

# 4. Verificar integridade dos backups
gzip -t backup_$(date +%Y%m%d).sql
```

#### Limpeza de Cache

```bash
# 1. Verificar estatísticas do cache
redis-cli info stats

# 2. Limpar cache expirado
redis-cli --scan --pattern "*" | xargs redis-cli del

# 3. Verificar uso de memória
redis-cli info memory
```

### Manutenção Mensal

#### Atualização de Dependências

```bash
# 1. Verificar dependências desatualizadas
pip list --outdated

# 2. Atualizar dependências menores
pip install -U requests tenacity

# 3. Executar testes
pytest

# 4. Verificar compatibilidade
bdfut show-config
bdfut test-connection
```

#### Análise de Performance

```bash
# 1. Analisar logs de performance
grep "performance" logs/production.log | tail -100

# 2. Verificar métricas de cache
redis-cli info stats | grep hit_rate

# 3. Analisar uso de recursos
sar -u 1 60
sar -r 1 60
```

---

## Procedimentos de Backup

### Backup Automático

#### Script de Backup

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/opt/backups/bdfut"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="bdfut_backup_$DATE"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
echo "Fazendo backup do banco de dados..."
supabase db dump > $BACKUP_DIR/${BACKUP_FILE}.sql

# Backup de configurações
echo "Fazendo backup de configurações..."
tar -czf $BACKUP_DIR/${BACKUP_FILE}_config.tar.gz .env config/

# Backup de logs
echo "Fazendo backup de logs..."
tar -czf $BACKUP_DIR/${BACKUP_FILE}_logs.tar.gz logs/

# Backup de dados
echo "Fazendo backup de dados..."
tar -czf $BACKUP_DIR/${BACKUP_FILE}_data.tar.gz data/

# Verificar integridade
echo "Verificando integridade dos backups..."
gzip -t $BACKUP_DIR/${BACKUP_FILE}.sql
tar -tzf $BACKUP_DIR/${BACKUP_FILE}_config.tar.gz > /dev/null
tar -tzf $BACKUP_DIR/${BACKUP_FILE}_logs.tar.gz > /dev/null
tar -tzf $BACKUP_DIR/${BACKUP_FILE}_data.tar.gz > /dev/null

# Limpar backups antigos (manter últimos 7 dias)
find $BACKUP_DIR -name "bdfut_backup_*" -mtime +7 -delete

echo "Backup concluído: $BACKUP_FILE"
```

#### Agendamento

```bash
# Adicionar ao crontab
crontab -e

# Backup diário às 2h
0 2 * * * /opt/bdfut/scripts/backup.sh

# Backup semanal completo aos domingos às 3h
0 3 * * 0 /opt/bdfut/scripts/backup_full.sh
```

### Backup Manual

#### Backup Completo

```bash
# 1. Parar serviços
sudo systemctl stop bdfut-prod

# 2. Executar backup
./scripts/backup.sh

# 3. Backup adicional do Redis
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb /opt/backups/bdfut/redis_backup_$(date +%Y%m%d).rdb

# 4. Reiniciar serviços
sudo systemctl start bdfut-prod
```

#### Backup Incremental

```bash
# 1. Backup apenas de dados modificados
find data/ -name "*.json" -mtime -1 -exec tar -czf incremental_backup_$(date +%Y%m%d).tar.gz {} \;

# 2. Backup de logs do dia
tar -czf logs_daily_$(date +%Y%m%d).tar.gz logs/production.log
```

---

## Procedimentos de Recovery

### Recovery de Dados

#### Recovery Completo

```bash
# 1. Parar serviços
sudo systemctl stop bdfut-prod
sudo systemctl stop redis

# 2. Restaurar banco de dados
supabase db reset
supabase db push < backup_YYYYMMDD.sql

# 3. Restaurar configurações
tar -xzf config_backup_YYYYMMDD.tar.gz

# 4. Restaurar dados
tar -xzf data_backup_YYYYMMDD.tar.gz

# 5. Restaurar Redis
cp redis_backup_YYYYMMDD.rdb /var/lib/redis/dump.rdb
sudo systemctl start redis

# 6. Reiniciar serviços
sudo systemctl start bdfut-prod

# 7. Verificar status
bdfut show-config
bdfut test-connection
```

#### Recovery Parcial

```bash
# 1. Restaurar apenas dados específicos
supabase db reset
supabase db push < backup_YYYYMMDD.sql

# 2. Verificar integridade
bdfut test-connection
```

### Recovery de Serviços

#### Recovery de Aplicação

```bash
# 1. Verificar status
sudo systemctl status bdfut-prod

# 2. Reiniciar serviço
sudo systemctl restart bdfut-prod

# 3. Verificar logs
tail -f logs/production.log

# 4. Verificar conectividade
bdfut test-connection
```

#### Recovery de Cache

```bash
# 1. Verificar status do Redis
redis-cli ping

# 2. Reiniciar Redis
sudo systemctl restart redis

# 3. Verificar dados
redis-cli info stats

# 4. Limpar cache se necessário
redis-cli FLUSHALL
```

---

## Monitoramento e Alertas

### Métricas de Sistema

#### CPU e Memória

```bash
# Verificar uso de CPU
top -p $(pgrep -f bdfut)

# Verificar uso de memória
free -h
ps aux | grep bdfut

# Verificar uso de disco
df -h
du -sh logs/ data/
```

#### Rede e Conectividade

```bash
# Verificar conectividade com APIs
curl -I https://api.sportmonks.com/v3/football
curl -I https://seu-projeto.supabase.co

# Verificar conectividade com Redis
redis-cli ping

# Verificar portas abertas
netstat -tlnp | grep :6379
netstat -tlnp | grep :5432
```

### Métricas de Aplicação

#### Performance de ETL

```bash
# Verificar jobs recentes
python -c "from bdfut.core.etl_metadata import ETLMetadataManager; print(ETLMetadataManager().get_recent_jobs(limit=5))"

# Verificar estatísticas de jobs
python -c "from bdfut.core.etl_metadata import ETLMetadataManager; print(ETLMetadataManager().get_job_stats())"
```

#### Cache Performance

```bash
# Verificar estatísticas do cache
redis-cli info stats

# Verificar hit rate
redis-cli info stats | grep hit_rate

# Verificar uso de memória
redis-cli info memory
```

### Alertas

#### Configuração de Alertas

```bash
# Script de verificação de saúde
#!/bin/bash
# scripts/health_check.sh

# Verificar status do serviço
if ! systemctl is-active --quiet bdfut-prod; then
    echo "ALERTA: Serviço BDFut não está rodando"
    # Enviar notificação
fi

# Verificar conectividade
if ! bdfut test-connection; then
    echo "ALERTA: Problema de conectividade"
    # Enviar notificação
fi

# Verificar uso de disco
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "ALERTA: Uso de disco alto: ${DISK_USAGE}%"
    # Enviar notificação
fi

# Verificar uso de memória
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 80 ]; then
    echo "ALERTA: Uso de memória alto: ${MEM_USAGE}%"
    # Enviar notificação
fi
```

#### Agendamento de Verificações

```bash
# Adicionar ao crontab
crontab -e

# Verificação de saúde a cada 5 minutos
*/5 * * * * /opt/bdfut/scripts/health_check.sh

# Verificação completa a cada hora
0 * * * * /opt/bdfut/scripts/health_check_full.sh
```

---

## Procedimentos de Incidentes

### Classificação de Incidentes

#### Severidade 1 - Crítico
- Sistema completamente indisponível
- Perda de dados
- Falha de segurança

#### Severidade 2 - Alto
- Funcionalidade principal indisponível
- Performance degradada significativamente
- Erros frequentes

#### Severidade 3 - Médio
- Funcionalidade secundária indisponível
- Performance ligeiramente degradada
- Erros esporádicos

#### Severidade 4 - Baixo
- Funcionalidade menor indisponível
- Problemas cosméticos
- Melhorias sugeridas

### Procedimento de Resposta

#### Severidade 1 - Crítico

```bash
# 1. Identificar problema
sudo systemctl status bdfut-prod
tail -f logs/production.log

# 2. Implementar workaround
sudo systemctl restart bdfut-prod

# 3. Se não resolver, rollback
sudo systemctl stop bdfut-prod
./scripts/restore.sh
sudo systemctl start bdfut-prod

# 4. Notificar equipe
# Enviar alerta para equipe de desenvolvimento

# 5. Documentar incidente
# Registrar no sistema de incidentes
```

#### Severidade 2 - Alto

```bash
# 1. Identificar problema
bdfut test-connection
grep "ERROR" logs/production.log | tail -20

# 2. Implementar correção
# Aplicar patch ou correção

# 3. Verificar resolução
bdfut test-connection

# 4. Notificar stakeholders
# Enviar atualização de status

# 5. Documentar incidente
# Registrar no sistema de incidentes
```

#### Severidade 3 - Médio

```bash
# 1. Identificar problema
grep "WARNING" logs/production.log | tail -20

# 2. Implementar correção
# Aplicar correção durante janela de manutenção

# 3. Verificar resolução
# Testar funcionalidade afetada

# 4. Documentar incidente
# Registrar no sistema de incidentes
```

#### Severidade 4 - Baixo

```bash
# 1. Identificar problema
# Revisar logs e métricas

# 2. Planejar correção
# Agendar para próxima janela de manutenção

# 3. Implementar correção
# Aplicar durante janela de manutenção

# 4. Documentar incidente
# Registrar no sistema de incidentes
```

### Comunicação de Incidentes

#### Template de Comunicação

```
INCIDENTE: [Severidade] - [Descrição]

STATUS: [Investigando/Identificado/Resolvido]

IMPACTO: [Descrição do impacto]

AÇÕES TOMADAS:
- [Ação 1]
- [Ação 2]

PRÓXIMOS PASSOS:
- [Próximo passo 1]
- [Próximo passo 2]

ATUALIZAÇÃO: [Data/Hora]
```

#### Canais de Comunicação

- **Slack**: #incidents
- **Email**: incidents@bdfut.com
- **Status Page**: https://status.bdfut.com

---

## Escalação e Contatos

### Matriz de Escalação

#### Nível 1 - Operações
- **Responsabilidade**: Monitoramento básico, reinicialização de serviços
- **Contato**: ops@bdfut.com
- **Disponibilidade**: 24/7

#### Nível 2 - Desenvolvimento
- **Responsabilidade**: Correção de bugs, patches
- **Contato**: dev@bdfut.com
- **Disponibilidade**: Horário comercial

#### Nível 3 - Arquitetura
- **Responsabilidade**: Problemas arquiteturais, mudanças estruturais
- **Contato**: arch@bdfut.com
- **Disponibilidade**: Horário comercial

#### Nível 4 - Gestão
- **Responsabilidade**: Decisões estratégicas, comunicação externa
- **Contato**: mgmt@bdfut.com
- **Disponibilidade**: Horário comercial

### Contatos de Emergência

#### Equipe Principal
- **Tech Lead**: João Silva - joao@bdfut.com - +55 11 99999-9999
- **DevOps**: Maria Santos - maria@bdfut.com - +55 11 99999-9998
- **DBA**: Pedro Costa - pedro@bdfut.com - +55 11 99999-9997

#### Equipe de Suporte
- **Suporte 24/7**: support@bdfut.com - +55 11 99999-9996
- **Emergências**: emergency@bdfut.com - +55 11 99999-9995

### Procedimentos de Escalação

#### Critérios de Escalação

- **Nível 1 → 2**: Incidente não resolvido em 30 minutos
- **Nível 2 → 3**: Incidente não resolvido em 2 horas
- **Nível 3 → 4**: Incidente não resolvido em 4 horas

#### Processo de Escalação

```bash
# 1. Documentar tentativas de resolução
# Registrar todas as ações tomadas

# 2. Escalar para próximo nível
# Enviar email com detalhes do incidente

# 3. Transferir responsabilidade
# Atualizar sistema de incidentes

# 4. Acompanhar resolução
# Manter comunicação com próximo nível
```

---

## Checklists Operacionais

### Checklist Diário

- [ ] Verificar status dos serviços
- [ ] Verificar conectividade com APIs
- [ ] Verificar logs de erro
- [ ] Verificar uso de recursos
- [ ] Verificar métricas de cache
- [ ] Executar backup incremental
- [ ] Verificar alertas

### Checklist Semanal

- [ ] Executar backup completo
- [ ] Limpar logs antigos
- [ ] Verificar dependências
- [ ] Analisar performance
- [ ] Revisar métricas
- [ ] Atualizar documentação
- [ ] Revisar incidentes

### Checklist Mensal

- [ ] Atualizar dependências
- [ ] Analisar logs de performance
- [ ] Revisar configurações
- [ ] Testar procedimentos de recovery
- [ ] Revisar matriz de escalação
- [ ] Atualizar runbook
- [ ] Revisar SLA

---

**Última atualização**: 2025-01-13  
**Versão**: 2.0  
**Responsável**: Technical Writer
