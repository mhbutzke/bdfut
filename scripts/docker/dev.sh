#!/bin/bash
# ============================================
# BDFut Docker Development Script
# ============================================
# Script para facilitar desenvolvimento com Docker

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 BDFut Docker Development Helper${NC}"
echo "========================================"

# Função para mostrar uso
show_usage() {
    echo "Uso: $0 COMANDO [OPÇÕES]"
    echo ""
    echo "Comandos:"
    echo "  up                      Subir ambiente de desenvolvimento"
    echo "  down                    Parar ambiente de desenvolvimento"
    echo "  restart                 Reiniciar ambiente"
    echo "  logs [SERVICE]          Mostrar logs (opcional: serviço específico)"
    echo "  shell [SERVICE]         Abrir shell no container"
    echo "  exec SERVICE CMD        Executar comando em serviço"
    echo "  test                    Executar testes"
    echo "  build                   Build das imagens"
    echo "  clean                   Limpar containers e volumes"
    echo "  status                  Status dos serviços"
    echo "  jupyter                 Abrir Jupyter Lab"
    echo "  redis-cli               Conectar ao Redis"
    echo "  monitoring              Subir stack de monitoramento"
    echo ""
    echo "Opções:"
    echo "  -d, --detach           Executar em background"
    echo "  -f, --follow           Seguir logs em tempo real"
    echo "  --no-deps              Não subir dependências"
    echo "  --build                Forçar rebuild"
    echo "  -h, --help             Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 up -d                    # Subir em background"
    echo "  $0 logs bdfut-dev -f        # Seguir logs do dev"
    echo "  $0 shell bdfut-dev          # Shell no container dev"
    echo "  $0 exec bdfut-dev pytest   # Executar pytest"
}

# Verificar se docker-compose está disponível
if ! command -v docker-compose >/dev/null 2>&1; then
    echo -e "${RED}❌ docker-compose não encontrado${NC}"
    exit 1
fi

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ docker-compose.yml não encontrado${NC}"
    echo "Execute este script a partir do diretório raiz do projeto"
    exit 1
fi

# Parse do comando
COMMAND=""
SERVICE=""
CMD_ARGS=""
DETACH=false
FOLLOW=false
NO_DEPS=false
BUILD=false

if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

COMMAND="$1"
shift

# Parse de argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--detach)
            DETACH=true
            shift
            ;;
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        --no-deps)
            NO_DEPS=true
            shift
            ;;
        --build)
            BUILD=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            if [ -z "$SERVICE" ]; then
                SERVICE="$1"
            else
                CMD_ARGS="$CMD_ARGS $1"
            fi
            shift
            ;;
    esac
done

# Função para executar docker-compose com opções
run_compose() {
    local cmd="$1"
    shift
    
    local compose_args=()
    
    if [ "$BUILD" = true ]; then
        compose_args+=("--build")
    fi
    
    if [ "$NO_DEPS" = true ]; then
        compose_args+=("--no-deps")
    fi
    
    if [ "$DETACH" = true ]; then
        compose_args+=("-d")
    fi
    
    echo -e "${BLUE}🐳 Executando: docker-compose $cmd ${compose_args[*]} $*${NC}"
    docker-compose "$cmd" "${compose_args[@]}" "$@"
}

# Executar comando
case $COMMAND in
    up)
        echo -e "${BLUE}🚀 Subindo ambiente de desenvolvimento...${NC}"
        if [ -n "$SERVICE" ]; then
            run_compose up "$SERVICE"
        else
            run_compose up bdfut-dev redis
        fi
        
        if [ "$DETACH" = true ]; then
            echo -e "${GREEN}✅ Ambiente iniciado em background${NC}"
            echo -e "${BLUE}📋 Para ver logs: $0 logs -f${NC}"
            echo -e "${BLUE}📋 Para parar: $0 down${NC}"
        fi
        ;;
        
    down)
        echo -e "${BLUE}🛑 Parando ambiente...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ Ambiente parado${NC}"
        ;;
        
    restart)
        echo -e "${BLUE}🔄 Reiniciando ambiente...${NC}"
        if [ -n "$SERVICE" ]; then
            docker-compose restart "$SERVICE"
        else
            docker-compose restart bdfut-dev redis
        fi
        echo -e "${GREEN}✅ Ambiente reiniciado${NC}"
        ;;
        
    logs)
        echo -e "${BLUE}📋 Mostrando logs...${NC}"
        local log_args=()
        
        if [ "$FOLLOW" = true ]; then
            log_args+=("-f")
        fi
        
        if [ -n "$SERVICE" ]; then
            docker-compose logs "${log_args[@]}" "$SERVICE"
        else
            docker-compose logs "${log_args[@]}"
        fi
        ;;
        
    shell)
        if [ -z "$SERVICE" ]; then
            SERVICE="bdfut-dev"
        fi
        
        echo -e "${BLUE}🐚 Abrindo shell em $SERVICE...${NC}"
        docker-compose exec "$SERVICE" /bin/bash
        ;;
        
    exec)
        if [ -z "$SERVICE" ]; then
            echo -e "${RED}❌ Serviço não especificado${NC}"
            exit 1
        fi
        
        if [ -z "$CMD_ARGS" ]; then
            echo -e "${RED}❌ Comando não especificado${NC}"
            exit 1
        fi
        
        echo -e "${BLUE}⚡ Executando '$CMD_ARGS' em $SERVICE...${NC}"
        docker-compose exec "$SERVICE" $CMD_ARGS
        ;;
        
    test)
        echo -e "${BLUE}🧪 Executando testes...${NC}"
        docker-compose up --build bdfut-test
        echo -e "${GREEN}✅ Testes concluídos${NC}"
        ;;
        
    build)
        echo -e "${BLUE}🔨 Fazendo build das imagens...${NC}"
        docker-compose build --no-cache
        echo -e "${GREEN}✅ Build concluído${NC}"
        ;;
        
    clean)
        echo -e "${YELLOW}⚠️ Limpando containers e volumes...${NC}"
        echo "Isso irá remover:"
        echo "  - Containers parados"
        echo "  - Volumes não utilizados"
        echo "  - Imagens dangling"
        
        read -p "Continuar? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v --remove-orphans
            docker system prune -f
            docker volume prune -f
            echo -e "${GREEN}✅ Limpeza concluída${NC}"
        else
            echo "Operação cancelada"
        fi
        ;;
        
    status)
        echo -e "${BLUE}📊 Status dos serviços:${NC}"
        docker-compose ps
        echo ""
        echo -e "${BLUE}📈 Uso de recursos:${NC}"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
        ;;
        
    jupyter)
        echo -e "${BLUE}📓 Abrindo Jupyter Lab...${NC}"
        docker-compose up -d jupyter
        
        echo "Aguardando Jupyter inicializar..."
        sleep 5
        
        JUPYTER_URL="http://localhost:8888"
        echo -e "${GREEN}✅ Jupyter Lab disponível em: $JUPYTER_URL${NC}"
        
        # Tentar abrir no browser (macOS/Linux)
        if command -v open >/dev/null 2>&1; then
            open "$JUPYTER_URL"
        elif command -v xdg-open >/dev/null 2>&1; then
            xdg-open "$JUPYTER_URL"
        fi
        ;;
        
    redis-cli)
        echo -e "${BLUE}🔴 Conectando ao Redis...${NC}"
        docker-compose exec redis redis-cli
        ;;
        
    monitoring)
        echo -e "${BLUE}📊 Subindo stack de monitoramento...${NC}"
        docker-compose --profile monitoring up -d prometheus grafana
        
        echo "Aguardando serviços inicializarem..."
        sleep 10
        
        echo -e "${GREEN}✅ Monitoramento disponível:${NC}"
        echo "  - Prometheus: http://localhost:9090"
        echo "  - Grafana: http://localhost:3000 (admin/admin)"
        ;;
        
    *)
        echo -e "${RED}❌ Comando desconhecido: $COMMAND${NC}"
        show_usage
        exit 1
        ;;
esac
