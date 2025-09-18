#!/bin/bash

# Script de Backup Seguro da Tabela Fixtures
# Author: Database Optimization Team
# Date: 2025-01-18

set -e  # Parar em caso de erro

# Configurações
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
BACKUP_FILE="fixtures_backup_${TIMESTAMP}.sql"
LOG_FILE="backup_log_${TIMESTAMP}.log"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando backup da tabela fixtures...${NC}"

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Log de início
echo "$(date): Iniciando backup da tabela fixtures" > $BACKUP_DIR/$LOG_FILE

# Verificar se variáveis de ambiente estão configuradas
if [ -z "$SUPABASE_DB_URL" ]; then
    echo -e "${RED}❌ Erro: SUPABASE_DB_URL não configurada${NC}"
    echo "Configure as variáveis de ambiente do Supabase primeiro."
    exit 1
fi

echo -e "${YELLOW}📊 Verificando tamanho da tabela fixtures...${NC}"

# Verificar quantos registros temos
RECORD_COUNT=$(psql "$SUPABASE_DB_URL" -t -c "SELECT COUNT(*) FROM fixtures;" 2>/dev/null || echo "0")
echo -e "${BLUE}📈 Registros na tabela fixtures: ${RECORD_COUNT}${NC}"

if [ "$RECORD_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️ Aviso: Tabela fixtures está vazia${NC}"
fi

echo -e "${YELLOW}💾 Criando backup da tabela fixtures...${NC}"

# Executar backup com compressão
if psql "$SUPABASE_DB_URL" -c "\copy (SELECT * FROM fixtures) TO STDOUT WITH CSV HEADER" | gzip > "$BACKUP_DIR/${BACKUP_FILE}.gz" 2>>$BACKUP_DIR/$LOG_FILE; then
    echo -e "${GREEN}✅ Backup criado com sucesso: $BACKUP_DIR/${BACKUP_FILE}.gz${NC}"
else
    echo -e "${RED}❌ Erro ao criar backup${NC}"
    exit 1
fi

# Verificar tamanho do backup
BACKUP_SIZE=$(ls -lh "$BACKUP_DIR/${BACKUP_FILE}.gz" | awk '{print $5}')
echo -e "${BLUE}📦 Tamanho do backup: ${BACKUP_SIZE}${NC}"

# Criar também backup SQL estrutural
echo -e "${YELLOW}🏗️ Criando backup estrutural (schema + dados)...${NC}"

if pg_dump "$SUPABASE_DB_URL" -t fixtures --no-owner --no-privileges > "$BACKUP_DIR/fixtures_schema_${TIMESTAMP}.sql" 2>>$BACKUP_DIR/$LOG_FILE; then
    echo -e "${GREEN}✅ Backup estrutural criado: $BACKUP_DIR/fixtures_schema_${TIMESTAMP}.sql${NC}"
else
    echo -e "${RED}❌ Erro ao criar backup estrutural${NC}"
fi

# Verificar integridade do backup
echo -e "${YELLOW}🔍 Verificando integridade do backup...${NC}"

# Contar linhas no backup CSV
BACKUP_LINES=$(zcat "$BACKUP_DIR/${BACKUP_FILE}.gz" | wc -l)
EXPECTED_LINES=$((RECORD_COUNT + 1))  # +1 para header

if [ "$BACKUP_LINES" -eq "$EXPECTED_LINES" ]; then
    echo -e "${GREEN}✅ Integridade do backup verificada: ${BACKUP_LINES} linhas${NC}"
else
    echo -e "${RED}❌ Possível problema na integridade: esperado ${EXPECTED_LINES}, obtido ${BACKUP_LINES}${NC}"
fi

# Log final
echo "$(date): Backup concluído com sucesso" >> $BACKUP_DIR/$LOG_FILE
echo "Registros: $RECORD_COUNT" >> $BACKUP_DIR/$LOG_FILE
echo "Arquivo: ${BACKUP_FILE}.gz" >> $BACKUP_DIR/$LOG_FILE
echo "Tamanho: $BACKUP_SIZE" >> $BACKUP_DIR/$LOG_FILE

echo -e "${GREEN}🎉 Backup da tabela fixtures concluído com sucesso!${NC}"
echo -e "${BLUE}📁 Arquivos criados:${NC}"
echo -e "  • $BACKUP_DIR/${BACKUP_FILE}.gz (dados CSV comprimidos)"
echo -e "  • $BACKUP_DIR/fixtures_schema_${TIMESTAMP}.sql (schema + dados SQL)"
echo -e "  • $BACKUP_DIR/$LOG_FILE (log da operação)"
echo ""
echo -e "${YELLOW}💡 Para restaurar em caso de emergência:${NC}"
echo -e "  zcat $BACKUP_DIR/${BACKUP_FILE}.gz | psql \"\$SUPABASE_DB_URL\" -c \"\\copy fixtures FROM STDIN WITH CSV HEADER\""
echo ""
echo -e "${GREEN}✅ Pronto para executar a migration!${NC}"
