#!/bin/bash
# ============================================
# BDFut Docker Build Script
# ============================================
# Script para build otimizado das imagens Docker

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
IMAGE_NAME="bdfut"
REGISTRY="${REGISTRY:-ghcr.io/bdfut}"
VERSION="${VERSION:-latest}"

echo -e "${BLUE}🐳 BDFut Docker Build Script${NC}"
echo "========================================"

# Função para mostrar uso
show_usage() {
    echo "Uso: $0 [OPÇÕES]"
    echo ""
    echo "Opções:"
    echo "  -t, --target TARGET     Target do build (production, development, testing)"
    echo "  -v, --version VERSION   Versão da imagem (default: latest)"
    echo "  -r, --registry REGISTRY Registry para push (default: ghcr.io/bdfut)"
    echo "  -p, --push              Fazer push da imagem após build"
    echo "  -c, --cache             Usar cache do Docker"
    echo "  --no-cache              Build sem cache"
    echo "  --multi-platform        Build para múltiplas plataformas"
    echo "  -h, --help              Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 -t production -v 1.0.0 -p"
    echo "  $0 --target development --no-cache"
    echo "  $0 --multi-platform -t production -v latest"
}

# Valores padrão
TARGET="production"
PUSH=false
USE_CACHE=true
MULTI_PLATFORM=false

# Parse de argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--target)
            TARGET="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -p|--push)
            PUSH=true
            shift
            ;;
        -c|--cache)
            USE_CACHE=true
            shift
            ;;
        --no-cache)
            USE_CACHE=false
            shift
            ;;
        --multi-platform)
            MULTI_PLATFORM=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Opção desconhecida: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Validar target
case $TARGET in
    production|development|testing)
        ;;
    *)
        echo -e "${RED}❌ Target inválido: $TARGET${NC}"
        echo "Targets válidos: production, development, testing"
        exit 1
        ;;
esac

# Construir nome completo da imagem
FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${VERSION}-${TARGET}"

echo -e "${BLUE}📋 Configuração do Build:${NC}"
echo "  Target: $TARGET"
echo "  Imagem: $FULL_IMAGE_NAME"
echo "  Cache: $([ "$USE_CACHE" = true ] && echo "Habilitado" || echo "Desabilitado")"
echo "  Multi-platform: $([ "$MULTI_PLATFORM" = true ] && echo "Sim" || echo "Não")"
echo "  Push: $([ "$PUSH" = true ] && echo "Sim" || echo "Não")"
echo ""

# Verificar se Docker está rodando
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando${NC}"
    exit 1
fi

# Verificar se Dockerfile existe
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Dockerfile não encontrado${NC}"
    exit 1
fi

# Preparar argumentos do build
BUILD_ARGS=()
BUILD_ARGS+=("--target" "$TARGET")
BUILD_ARGS+=("--tag" "$FULL_IMAGE_NAME")

if [ "$USE_CACHE" = false ]; then
    BUILD_ARGS+=("--no-cache")
fi

# Build args para informações de build
BUILD_ARGS+=("--build-arg" "BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')")
BUILD_ARGS+=("--build-arg" "VERSION=$VERSION")
BUILD_ARGS+=("--build-arg" "TARGET=$TARGET")

if command -v git >/dev/null 2>&1; then
    GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    BUILD_ARGS+=("--build-arg" "GIT_COMMIT=$GIT_COMMIT")
fi

# Configurar para multi-platform se solicitado
if [ "$MULTI_PLATFORM" = true ]; then
    if ! docker buildx version >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker Buildx não está disponível${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}🔧 Configurando buildx para multi-platform...${NC}"
    docker buildx create --use --name bdfut-builder >/dev/null 2>&1 || true
    
    BUILD_ARGS+=("--platform" "linux/amd64,linux/arm64")
    
    if [ "$PUSH" = true ]; then
        BUILD_ARGS+=("--push")
    else
        BUILD_ARGS+=("--load")
    fi
    
    BUILD_COMMAND="docker buildx build"
else
    BUILD_COMMAND="docker build"
fi

# Executar build
echo -e "${BLUE}🔨 Iniciando build...${NC}"
echo "Comando: $BUILD_COMMAND ${BUILD_ARGS[*]} ."
echo ""

if $BUILD_COMMAND "${BUILD_ARGS[@]}" .; then
    echo -e "${GREEN}✅ Build concluído com sucesso!${NC}"
else
    echo -e "${RED}❌ Build falhou${NC}"
    exit 1
fi

# Push se solicitado (apenas para build single-platform)
if [ "$PUSH" = true ] && [ "$MULTI_PLATFORM" = false ]; then
    echo -e "${BLUE}📤 Fazendo push da imagem...${NC}"
    if docker push "$FULL_IMAGE_NAME"; then
        echo -e "${GREEN}✅ Push concluído com sucesso!${NC}"
    else
        echo -e "${RED}❌ Push falhou${NC}"
        exit 1
    fi
fi

# Mostrar informações da imagem
echo ""
echo -e "${BLUE}📊 Informações da Imagem:${NC}"
if [ "$MULTI_PLATFORM" = false ]; then
    docker images "$FULL_IMAGE_NAME" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
fi

# Mostrar comandos úteis
echo ""
echo -e "${BLUE}🔧 Comandos úteis:${NC}"
echo "  # Executar container:"
echo "  docker run --rm -it $FULL_IMAGE_NAME"
echo ""
echo "  # Executar com docker-compose:"
echo "  docker-compose up bdfut-$(echo $TARGET | sed 's/production//')"
echo ""
echo "  # Inspecionar imagem:"
echo "  docker inspect $FULL_IMAGE_NAME"

echo ""
echo -e "${GREEN}🎉 Build concluído!${NC}"
