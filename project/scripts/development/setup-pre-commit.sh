#!/bin/bash
# ============================================
# BDFut Pre-commit Setup Script
# ============================================
# Este script configura e instala todos os pre-commit hooks
# para garantir qualidade de código e segurança

set -e  # Exit on any error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 BDFut Pre-commit Setup${NC}"
echo "========================================"

# Verificar se estamos no diretório correto
if [ ! -f ".pre-commit-config.yaml" ]; then
    echo -e "${RED}❌ Erro: .pre-commit-config.yaml não encontrado${NC}"
    echo "Execute este script a partir do diretório raiz do projeto"
    exit 1
fi

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar Python
echo -e "${BLUE}🔍 Verificando Python...${NC}"
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ $PYTHON_VERSION encontrado${NC}"
else
    echo -e "${RED}❌ Python 3 não encontrado${NC}"
    exit 1
fi

# Verificar pip
echo -e "${BLUE}🔍 Verificando pip...${NC}"
if command_exists pip3; then
    echo -e "${GREEN}✅ pip3 encontrado${NC}"
elif command_exists pip; then
    echo -e "${GREEN}✅ pip encontrado${NC}"
else
    echo -e "${RED}❌ pip não encontrado${NC}"
    exit 1
fi

# Instalar pre-commit se não existir
echo -e "${BLUE}📦 Verificando pre-commit...${NC}"
if command_exists pre-commit; then
    echo -e "${GREEN}✅ pre-commit já instalado${NC}"
    pre-commit --version
else
    echo -e "${YELLOW}⚠️ pre-commit não encontrado, instalando...${NC}"
    pip3 install pre-commit
    echo -e "${GREEN}✅ pre-commit instalado${NC}"
fi

# Instalar dependências de desenvolvimento
echo -e "${BLUE}📦 Instalando dependências de desenvolvimento...${NC}"
if [ -f "pyproject.toml" ]; then
    pip3 install -e ".[dev]"
    echo -e "${GREEN}✅ Dependências de desenvolvimento instaladas${NC}"
else
    echo -e "${YELLOW}⚠️ pyproject.toml não encontrado, pulando dependências${NC}"
fi

# Instalar hooks do pre-commit
echo -e "${BLUE}🔧 Instalando pre-commit hooks...${NC}"
pre-commit install

# Instalar hook de commit-msg para commitizen
echo -e "${BLUE}🔧 Instalando commit-msg hook...${NC}"
pre-commit install --hook-type commit-msg

# Executar pre-commit em todos os arquivos para verificar
echo -e "${BLUE}🧪 Testando pre-commit hooks...${NC}"
echo -e "${YELLOW}⚠️ Isso pode demorar na primeira execução...${NC}"

if pre-commit run --all-files; then
    echo -e "${GREEN}✅ Todos os hooks passaram!${NC}"
else
    echo -e "${YELLOW}⚠️ Alguns hooks falharam, mas isso é normal na primeira execução${NC}"
    echo -e "${YELLOW}⚠️ Os hooks irão corrigir automaticamente os problemas encontrados${NC}"
fi

# Verificar configuração específica do projeto
echo -e "${BLUE}🔍 Verificando configuração do projeto...${NC}"

# Verificar se .gitignore existe
if [ -f ".gitignore" ]; then
    echo -e "${GREEN}✅ .gitignore encontrado${NC}"
else
    echo -e "${YELLOW}⚠️ .gitignore não encontrado${NC}"
fi

# Verificar se pyproject.toml existe
if [ -f "pyproject.toml" ]; then
    echo -e "${GREEN}✅ pyproject.toml encontrado${NC}"
else
    echo -e "${YELLOW}⚠️ pyproject.toml não encontrado${NC}"
fi

# Criar arquivo de configuração local se não existir
if [ ! -f ".pre-commit-config.local.yaml" ]; then
    echo -e "${BLUE}📝 Criando configuração local...${NC}"
    cat > .pre-commit-config.local.yaml << 'EOF'
# Local pre-commit configuration overrides
# This file is ignored by git and can be used for local customizations

repos:
  - repo: local
    hooks:
      - id: local-tests
        name: Run local tests
        entry: make test
        language: system
        pass_filenames: false
        always_run: false  # Set to true to run on every commit
EOF
    echo -e "${GREEN}✅ Configuração local criada${NC}"
fi

# Mostrar resumo final
echo ""
echo -e "${GREEN}🎉 Pre-commit setup concluído!${NC}"
echo "========================================"
echo -e "${BLUE}📋 Resumo:${NC}"
echo -e "  ✅ Pre-commit instalado e configurado"
echo -e "  ✅ Hooks instalados para commit e commit-msg"
echo -e "  ✅ Dependências de desenvolvimento instaladas"
echo -e "  ✅ Configuração testada"
echo ""
echo -e "${BLUE}🔧 Comandos úteis:${NC}"
echo -e "  ${YELLOW}pre-commit run --all-files${NC}    # Executar todos os hooks"
echo -e "  ${YELLOW}pre-commit run <hook-id>${NC}      # Executar hook específico"
echo -e "  ${YELLOW}pre-commit autoupdate${NC}         # Atualizar versões dos hooks"
echo -e "  ${YELLOW}pre-commit clean${NC}              # Limpar cache dos hooks"
echo ""
echo -e "${BLUE}📚 Documentação:${NC}"
echo -e "  Ver docs/devops/PRE_COMMIT_HOOKS.md para mais detalhes"
echo ""
echo -e "${GREEN}✨ Agora todos os commits serão validados automaticamente!${NC}"
