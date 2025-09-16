# Docker Guide - BDFut 🐳

## 📋 **Visão Geral**

O BDFut utiliza uma arquitetura Docker moderna com multi-stage builds, orquestração via Docker Compose e monitoramento integrado. Esta documentação cobre todos os aspectos do uso de containers no projeto.

## 🏗️ **Arquitetura Docker**

### **Multi-Stage Dockerfile**
O Dockerfile implementa 5 estágios otimizados:

1. **Base** - Dependências essenciais do sistema
2. **Builder** - Build das dependências Python
3. **Development** - Ambiente de desenvolvimento completo
4. **Production** - Imagem otimizada para produção
5. **Testing** - Ambiente específico para testes

### **Benefícios da Arquitetura:**
- ✅ **Imagens menores** em produção
- ✅ **Cache otimizado** entre builds
- ✅ **Ambientes isolados** por propósito
- ✅ **Segurança aprimorada** com usuário não-root
- ✅ **Multi-platform support** (AMD64/ARM64)

## 🚀 **Quick Start**

### **1. Setup Inicial**
```bash
# Clone e entre no projeto
git clone <repo-url>
cd bdfut

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# Build das imagens
./scripts/docker/build.sh --target development
```

### **2. Desenvolvimento**
```bash
# Subir ambiente completo
./scripts/docker/dev.sh up -d

# Ver logs
./scripts/docker/dev.sh logs -f

# Shell no container
./scripts/docker/dev.sh shell

# Executar testes
./scripts/docker/dev.sh test
```

### **3. Produção**
```bash
# Build para produção
./scripts/docker/build.sh --target production --version 1.0.0

# Subir com docker-compose
docker-compose up bdfut
```

## 📦 **Imagens Disponíveis**

### **Development Image**
```bash
# Build
docker build --target development -t bdfut:dev .

# Características:
# - Ferramentas de desenvolvimento (git, vim, htop)
# - Dependências de dev instaladas
# - Volume mount para live reload
# - Debug tools habilitados
```

### **Production Image**
```bash
# Build
docker build --target production -t bdfut:prod .

# Características:
# - Imagem otimizada (~200MB menor)
# - Apenas dependências de produção
# - Usuário não-root
# - Health checks configurados
```

### **Testing Image**
```bash
# Build
docker build --target testing -t bdfut:test .

# Características:
# - Ferramentas de teste adicionais
# - Coverage tools
# - Pytest configurado
# - Ambientes de teste isolados
```

## 🔧 **Scripts de Automação**

### **Build Script (`scripts/docker/build.sh`)**
Script avançado para build das imagens:

```bash
# Uso básico
./scripts/docker/build.sh --target production

# Opções avançadas
./scripts/docker/build.sh \
    --target production \
    --version 1.2.3 \
    --registry ghcr.io/bdfut \
    --push \
    --multi-platform
```

**Opções disponíveis:**
- `--target`: Stage do Dockerfile (production, development, testing)
- `--version`: Versão da imagem (default: latest)
- `--registry`: Registry para push
- `--push`: Fazer push após build
- `--multi-platform`: Build para AMD64 e ARM64
- `--no-cache`: Build sem cache

### **Development Script (`scripts/docker/dev.sh`)**
Facilita operações de desenvolvimento:

```bash
# Comandos principais
./scripts/docker/dev.sh up -d          # Subir ambiente
./scripts/docker/dev.sh down           # Parar ambiente
./scripts/docker/dev.sh logs -f        # Ver logs
./scripts/docker/dev.sh shell          # Abrir shell
./scripts/docker/dev.sh test           # Executar testes
./scripts/docker/dev.sh clean          # Limpar tudo

# Comandos específicos
./scripts/docker/dev.sh jupyter        # Abrir Jupyter
./scripts/docker/dev.sh redis-cli      # Conectar Redis
./scripts/docker/dev.sh monitoring     # Subir Grafana/Prometheus
```

## 🐳 **Docker Compose Services**

### **Serviços Principais**

#### **bdfut (Production)**
```yaml
bdfut:
  build:
    target: production
  environment:
    - BDFUT_ENV=production
  volumes:
    - bdfut_logs:/app/logs
    - bdfut_data:/app/data
  restart: unless-stopped
```

#### **bdfut-dev (Development)**
```yaml
bdfut-dev:
  build:
    target: development
  volumes:
    - .:/app  # Live reload
  ports:
    - "8000:8000"
  restart: "no"
```

#### **bdfut-test (Testing)**
```yaml
bdfut-test:
  build:
    target: testing
  command: pytest tests/ -v --cov=bdfut
  volumes:
    - test_results:/app/test-results
```

### **Serviços de Infraestrutura**

#### **Redis (Cache)**
```yaml
redis:
  image: redis:7-alpine
  volumes:
    - redis_data:/data
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
  command: redis-server --maxmemory 512mb
```

#### **Jupyter (Notebooks)**
```yaml
jupyter:
  build:
    target: development
  ports:
    - "8888:8888"
  command: jupyter lab --ip=0.0.0.0
  volumes:
    - ./notebooks:/app/notebooks
```

### **Monitoramento**

#### **Prometheus**
```yaml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
  profiles:
    - monitoring
```

#### **Grafana**
```yaml
grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  profiles:
    - monitoring
```

## 🔍 **Health Checks**

### **Application Health Check**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import bdfut; print('OK')" || exit 1
```

### **Redis Health Check**
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s
```

### **Verificar Health Status**
```bash
# Status de todos os containers
docker-compose ps

# Logs de health check
docker inspect bdfut-app --format='{{.State.Health.Status}}'

# Detalhes do health check
docker inspect bdfut-app --format='{{json .State.Health}}'
```

## 📊 **Monitoramento e Observabilidade**

### **Métricas Coletadas**
- **Application**: Performance, errors, requests
- **Redis**: Memory usage, hit rate, connections
- **Docker**: CPU, memory, network, disk I/O
- **System**: Node metrics (se disponível)

### **Dashboards Grafana**
- **BDFut Overview**: Métricas gerais da aplicação
- **Redis Performance**: Cache metrics
- **Container Resources**: Docker stats
- **Error Tracking**: Logs e erros

### **Acessar Monitoramento**
```bash
# Subir stack de monitoramento
./scripts/docker/dev.sh monitoring

# Acessar interfaces
open http://localhost:9090  # Prometheus
open http://localhost:3000  # Grafana (admin/admin)
```

## 🔧 **Comandos Úteis**

### **Build e Deploy**
```bash
# Build multi-platform
docker buildx build --platform linux/amd64,linux/arm64 -t bdfut:latest .

# Tag para registry
docker tag bdfut:latest ghcr.io/bdfut/bdfut:latest

# Push para registry
docker push ghcr.io/bdfut/bdfut:latest
```

### **Desenvolvimento**
```bash
# Rebuild sem cache
docker-compose build --no-cache bdfut-dev

# Executar comando específico
docker-compose exec bdfut-dev python -m bdfut.cli --help

# Copiar arquivos
docker cp bdfut-dev:/app/logs/app.log ./logs/
```

### **Debugging**
```bash
# Logs detalhados
docker-compose logs --timestamps --follow bdfut-dev

# Inspecionar container
docker inspect bdfut-dev

# Processos no container
docker-compose exec bdfut-dev ps aux

# Uso de recursos
docker stats bdfut-dev
```

### **Limpeza**
```bash
# Parar tudo
docker-compose down -v --remove-orphans

# Limpar imagens
docker system prune -a -f

# Limpar volumes
docker volume prune -f

# Script de limpeza completa
./scripts/docker/dev.sh clean
```

## 🔒 **Segurança**

### **Práticas Implementadas**
- ✅ **Usuário não-root** em todos os containers
- ✅ **Imagens base** atualizadas (python:3.11-slim)
- ✅ **Secrets** via environment variables
- ✅ **Volumes** com permissões adequadas
- ✅ **Network isolation** via Docker networks
- ✅ **Health checks** para detectar problemas

### **Variáveis de Ambiente Sensíveis**
```bash
# Nunca commitar no código
SPORTMONKS_API_KEY=your_api_key
SUPABASE_KEY=your_supabase_key
GRAFANA_PASSWORD=secure_password

# Use .env file ou secrets do Docker
docker secret create sportmonks_key sportmonks_api_key.txt
```

### **Network Security**
```yaml
networks:
  bdfut-network:
    driver: bridge
    internal: false  # Permite acesso externo apenas quando necessário
```

## 📈 **Performance**

### **Otimizações Implementadas**
- **Multi-stage builds**: Reduz tamanho das imagens
- **Layer caching**: Acelera rebuilds
- **Volume mounts**: Evita copy desnecessário
- **Health checks**: Detecta problemas rapidamente
- **Resource limits**: Previne uso excessivo

### **Métricas de Performance**
- **Build time**: ~3-5 minutos (primeira vez), ~30s (cached)
- **Image size**: 
  - Development: ~800MB
  - Production: ~400MB
  - Testing: ~850MB
- **Startup time**: ~10-15 segundos
- **Memory usage**: ~200-500MB (dependendo da carga)

### **Tuning de Performance**
```yaml
# Limites de recursos
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
    reservations:
      memory: 512M
      cpus: '0.25'
```

## 🐛 **Troubleshooting**

### **Problemas Comuns**

#### **Build Falha**
```bash
# Verificar logs detalhados
docker build --no-cache --progress=plain .

# Verificar espaço em disco
docker system df

# Limpar cache
docker builder prune -a
```

#### **Container não Inicia**
```bash
# Ver logs de startup
docker-compose logs bdfut-dev

# Verificar health check
docker inspect bdfut-dev --format='{{.State.Health.Status}}'

# Executar shell para debug
docker-compose exec bdfut-dev /bin/bash
```

#### **Problemas de Conectividade**
```bash
# Verificar network
docker network ls
docker network inspect bdfut-network

# Testar conectividade
docker-compose exec bdfut-dev ping redis
docker-compose exec bdfut-dev curl -I http://prometheus:9090
```

#### **Performance Issues**
```bash
# Monitorar recursos
docker stats

# Verificar logs de sistema
docker-compose logs --timestamps

# Analisar métricas
curl http://localhost:9090/metrics
```

### **Debug Avançado**
```bash
# Entrar no container como root
docker-compose exec --user root bdfut-dev /bin/bash

# Verificar processos
docker-compose exec bdfut-dev ps aux

# Verificar variáveis de ambiente
docker-compose exec bdfut-dev env

# Verificar arquivos de configuração
docker-compose exec bdfut-dev cat /app/.env
```

## 📚 **Recursos Adicionais**

### **Documentação Oficial**
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Multi-stage builds](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)

### **Melhores Práticas**
- [Dockerfile best practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose best practices](https://docs.docker.com/compose/production/)
- [Container security](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

### **Ferramentas Relacionadas**
- [Hadolint](https://github.com/hadolint/hadolint) - Dockerfile linter
- [Dive](https://github.com/wagoodman/dive) - Analyze Docker images
- [Trivy](https://github.com/aquasecurity/trivy) - Security scanner

---

**🎯 Com esta configuração Docker, o BDFut tem uma infraestrutura robusta, segura e escalável para todos os ambientes!**
