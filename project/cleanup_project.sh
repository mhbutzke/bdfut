#!/bin/bash

# Script de Limpeza do Projeto BDFut
# Remove arquivos desnecessários e organiza estrutura
# Author: Project Organization Team
# Date: 2025-01-18

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧹 Iniciando limpeza e organização do projeto BDFut...${NC}"

# Função para confirmar ação
confirm() {
    read -p "$1 (y/N): " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# 1. Remover arquivos de log antigos
echo -e "${YELLOW}📋 Limpando logs antigos...${NC}"
if [ -d "data/logs" ]; then
    find data/logs -name "*.log" -mtime +30 -type f -delete 2>/dev/null || true
    echo -e "${GREEN}✅ Logs antigos (>30 dias) removidos${NC}"
fi

# 2. Limpar cache Python
echo -e "${YELLOW}🐍 Limpando cache Python...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Cache Python limpo${NC}"

# 3. Remover arquivos temporários
echo -e "${YELLOW}🗑️ Removendo arquivos temporários...${NC}"
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Arquivos temporários removidos${NC}"

# 4. Organizar estrutura de pastas
echo -e "${YELLOW}📁 Verificando estrutura de pastas...${NC}"

# Criar pastas necessárias se não existirem
mkdir -p archive/api_samples
mkdir -p docs_organized/{core,etl,database,archive}
mkdir -p data/logs
mkdir -p src/bdfut/scripts/etl_organized/{01_setup,02_base_data,03_leagues_seasons,04_fixtures_events,05_quality_checks}

echo -e "${GREEN}✅ Estrutura de pastas organizada${NC}"

# 5. Verificar arquivos essenciais
echo -e "${YELLOW}🔍 Verificando arquivos essenciais...${NC}"

essential_files=(
    "src/bdfut/core/sportmonks_client.py"
    "src/bdfut/core/supabase_client.py"
    ".taskmaster/tasks/tasks.json"
    "config/requirements.txt"
    "README.md"
)

missing_files=()
for file in "${essential_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ Todos os arquivos essenciais estão presentes${NC}"
else
    echo -e "${RED}⚠️ Arquivos essenciais faltando:${NC}"
    for file in "${missing_files[@]}"; do
        echo -e "${RED}  - $file${NC}"
    done
fi

# 6. Estatísticas finais
echo -e "${BLUE}📊 Estatísticas do projeto:${NC}"

# Contar arquivos por tipo
py_files=$(find src/ -name "*.py" -type f | wc -l)
md_files=$(find docs_organized/ -name "*.md" -type f | wc -l)
sql_files=$(find . -name "*.sql" -type f | wc -l)
json_files=$(find archive/ -name "*.json" -type f | wc -l)

echo -e "${GREEN}  📄 Arquivos Python: $py_files${NC}"
echo -e "${GREEN}  📝 Arquivos Markdown: $md_files${NC}"
echo -e "${GREEN}  🗃️ Arquivos SQL: $sql_files${NC}"
echo -e "${GREEN}  📦 Arquivos JSON arquivados: $json_files${NC}"

# Tamanho das pastas principais
echo -e "${BLUE}📁 Tamanho das pastas principais:${NC}"
du -sh src/ docs_organized/ archive/ .taskmaster/ 2>/dev/null | while read size dir; do
    echo -e "${GREEN}  $dir: $size${NC}"
done

echo ""
echo -e "${GREEN}🎉 Limpeza e organização concluída com sucesso!${NC}"
echo ""
echo -e "${BLUE}🎯 Próximos passos:${NC}"
echo -e "${YELLOW}  1. task-master next${NC}"
echo -e "${YELLOW}  2. task-master show 1${NC}"
echo -e "${YELLOW}  3. Implementar Task 1.1${NC}"
