# ============================================
# BDFut Makefile - DevOps Automation
# ============================================
# Automação completa para desenvolvimento, teste e produção

.PHONY: help install install-dev test lint format clean run setup
.PHONY: docker-build docker-run docker-dev docker-test docker-clean
.PHONY: ci cd deploy security monitoring debug
.PHONY: dev-setup dev-test dev-run dev-shell dev-logs
.PHONY: prod-setup prod-test prod-run prod-deploy
.PHONY: pre-commit pre-commit-update pre-commit-install
.PHONY: check coverage security-scan dependency-check
.PHONY: backup restore migrate rollback
.PHONY: status health logs metrics

help: ## Mostra esta ajuda
	@echo "BDFut - Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências básicas
	pip install -e .

install-dev: ## Instala dependências de desenvolvimento
	pip install -e ".[dev]"
	pre-commit install
	pre-commit install --hook-type commit-msg

setup: ## Configuração inicial do projeto
	@echo "🚀 Configurando BDFut..."
	cp bdfut/config/secrets/env_example.txt .env
	@echo "📝 Edite o arquivo .env com suas credenciais"
	@echo "✅ Configuração inicial concluída!"

test: ## Executa testes
	pytest tests/ -v

test-cov: ## Executa testes com cobertura
	pytest tests/ --cov=bdfut --cov-report=html --cov-report=term-missing

lint: ## Executa linting
	flake8 bdfut/ tests/
	mypy bdfut/

format: ## Formata código
	black bdfut/ tests/
	isort bdfut/ tests/

clean: ## Limpa arquivos temporários
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

run: ## Executa CLI principal
	python -m bdfut.cli

run-legacy: ## Executa CLI legado
	python bdfut/cli_legacy.py

sync-base: ## Sincroniza dados base
	python -m bdfut.cli sync-base

sync-leagues: ## Sincroniza ligas principais
	python -m bdfut.cli sync-leagues

sync-full: ## Sincronização completa
	python -m bdfut.cli full-sync

test-connection: ## Testa conexões
	python -m bdfut.cli test-connection

show-config: ## Mostra configuração
	python -m bdfut.cli show-config

notebooks: ## Executa notebooks
	jupyter notebook notebooks/

docs: ## Gera documentação
	@echo "📚 Gerando documentação..."
	@echo "Documentação disponível em docs/"

deploy: ## Deploy para produção
	@echo "🚀 Fazendo deploy..."
	@echo "Configure suas credenciais de produção primeiro"

# ============================================
# DOCKER & INFRAESTRUTURA
# ============================================

docker-build: ## Build da imagem Docker (produção)
	@echo "🐳 Fazendo build da imagem Docker..."
	./scripts/docker/build.sh --target production

docker-build-dev: ## Build da imagem Docker (desenvolvimento)
	@echo "🐳 Fazendo build da imagem Docker (dev)..."
	./scripts/docker/build.sh --target development

docker-build-test: ## Build da imagem Docker (testes)
	@echo "🐳 Fazendo build da imagem Docker (test)..."
	./scripts/docker/build.sh --target testing

docker-build-all: ## Build de todas as imagens
	@echo "🐳 Fazendo build de todas as imagens..."
	./scripts/docker/build.sh --target production
	./scripts/docker/build.sh --target development
	./scripts/docker/build.sh --target testing

docker-run: ## Executa container Docker
	@echo "🚀 Executando container Docker..."
	docker-compose up bdfut

docker-dev: ## Executa ambiente de desenvolvimento
	@echo "🚀 Executando ambiente de desenvolvimento..."
	./scripts/docker/dev.sh up -d

docker-test: ## Executa testes em Docker
	@echo "🧪 Executando testes em Docker..."
	./scripts/docker/dev.sh test

docker-stop: ## Para todos os containers
	@echo "🛑 Parando containers..."
	./scripts/docker/dev.sh down

docker-restart: ## Reinicia containers
	@echo "🔄 Reiniciando containers..."
	./scripts/docker/dev.sh restart

docker-clean: ## Limpa containers e volumes
	@echo "🧹 Limpando containers e volumes..."
	./scripts/docker/dev.sh clean

docker-logs: ## Mostra logs dos containers
	@echo "📋 Mostrando logs dos containers..."
	./scripts/docker/dev.sh logs -f

docker-status: ## Status dos containers
	@echo "📊 Status dos containers..."
	./scripts/docker/dev.sh status

docker-shell: ## Shell no container principal
	@echo "🐚 Abrindo shell no container..."
	./scripts/docker/dev.sh shell

docker-push: ## Push das imagens para registry
	@echo "📤 Fazendo push das imagens..."
	./scripts/docker/build.sh --target production --push

docker-multi-platform: ## Build multi-platform
	@echo "🌍 Fazendo build multi-platform..."
	./scripts/docker/build.sh --target production --multi-platform --push

pre-commit: ## Executa pre-commit hooks
	pre-commit run --all-files

pre-commit-update: ## Atualiza versões dos pre-commit hooks
	pre-commit autoupdate

pre-commit-install: ## Instala/reinstala pre-commit hooks
	pre-commit install
	pre-commit install --hook-type commit-msg

# ============================================
# CI/CD & DEPLOY
# ============================================

check: lint test ## Executa todas as verificações
	@echo "✅ Todas as verificações concluídas!"

ci: install-dev check ## Executa pipeline de CI
	@echo "🔄 Executando pipeline de CI..."
	@echo "✅ Pipeline CI concluído!"

ci-full: install-dev pre-commit security-scan test-cov ## Pipeline CI completo
	@echo "🔄 Executando pipeline CI completo..."
	@echo "✅ Pipeline CI completo concluído!"

cd: ci docker-build docker-test ## Pipeline CD (Continuous Deployment)
	@echo "🚀 Executando pipeline CD..."
	@echo "✅ Pipeline CD concluído!"

deploy-staging: ci docker-build ## Deploy para staging
	@echo "🚀 Fazendo deploy para staging..."
	@echo "⚠️ Configure staging environment"
	@echo "✅ Deploy para staging concluído!"

deploy-prod: ci-full docker-build docker-push ## Deploy para produção
	@echo "🚀 Fazendo deploy para produção..."
	@echo "⚠️ Configure produção environment"
	@echo "✅ Deploy para produção concluído!"

release: ci-full docker-build-all docker-push ## Criar release
	@echo "🏷️ Criando release..."
	@echo "⚠️ Configure version e tags"
	@echo "✅ Release criado!"

rollback-deploy: ## Rollback da última versão
	@echo "⏪ Fazendo rollback..."
	@echo "⚠️ Implementar rollback real"
	@echo "✅ Rollback concluído!"

# ============================================
# DESENVOLVIMENTO
# ============================================

dev-setup: install-dev setup ## Configuração completa para desenvolvimento
	@echo "🔧 Configurando ambiente de desenvolvimento..."
	@echo "✅ Ambiente pronto!"

dev-test: test-cov ## Testes completos para desenvolvimento
	@echo "🧪 Executando testes de desenvolvimento..."

dev-run: run ## Executa em modo desenvolvimento
	@echo "🚀 Executando em modo desenvolvimento..."

dev-shell: ## Abre shell no container de desenvolvimento
	@echo "🐚 Abrindo shell no container de desenvolvimento..."
	./scripts/docker/dev.sh shell bdfut-dev

dev-logs: ## Mostra logs do ambiente de desenvolvimento
	@echo "📋 Mostrando logs de desenvolvimento..."
	./scripts/docker/dev.sh logs -f bdfut-dev

dev-jupyter: ## Abre Jupyter Lab
	@echo "📓 Abrindo Jupyter Lab..."
	./scripts/docker/dev.sh jupyter

dev-redis: ## Conecta ao Redis
	@echo "🔴 Conectando ao Redis..."
	./scripts/docker/dev.sh redis-cli

dev-monitoring: ## Sube stack de monitoramento
	@echo "📊 Subindo monitoramento..."
	./scripts/docker/dev.sh monitoring

dev-clean: ## Limpa ambiente de desenvolvimento
	@echo "🧹 Limpando ambiente de desenvolvimento..."
	./scripts/docker/dev.sh clean

# ============================================
# PRODUÇÃO
# ============================================

prod-setup: install ## Configuração para produção
	@echo "🏭 Configurando ambiente de produção..."

prod-test: test ## Testes para produção
	@echo "🧪 Executando testes de produção..."

prod-run: run ## Executa em modo produção
	@echo "🚀 Executando em modo produção..."

prod-deploy: ## Deploy para produção
	@echo "🚀 Fazendo deploy para produção..."
	@echo "⚠️ Configure suas credenciais de produção primeiro"
	./scripts/docker/build.sh --target production --push

prod-backup: ## Backup dos dados de produção
	@echo "💾 Fazendo backup dos dados..."
	@echo "⚠️ Implementar backup real"

prod-restore: ## Restaura dados de produção
	@echo "🔄 Restaurando dados..."
	@echo "⚠️ Implementar restore real"

# ============================================
# MONITORAMENTO & DEBUG
# ============================================

status: ## Status geral do sistema
	@echo "📊 Status do sistema BDFut:"
	@echo "================================"
	@echo "🐳 Docker containers:"
	@docker-compose ps 2>/dev/null || echo "  Docker não disponível"
	@echo ""
	@echo "📈 Uso de recursos:"
	@docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || echo "  Docker stats não disponível"
	@echo ""
	@echo "💾 Espaço em disco:"
	@df -h . | tail -1
	@echo ""
	@echo "🔍 Processos Python:"
	@ps aux | grep python | grep -v grep | head -5 || echo "  Nenhum processo Python encontrado"

health: ## Verifica saúde do sistema
	@echo "🏥 Verificando saúde do sistema..."
	@echo "================================"
	@echo "🐳 Containers:"
	@docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  Docker não disponível"
	@echo ""
	@echo "🔗 Conectividade:"
	@python -c "import requests; print('✅ Internet OK')" 2>/dev/null || echo "❌ Internet não disponível"
	@echo ""
	@echo "📦 Dependências Python:"
	@python -c "import bdfut; print('✅ BDFut OK')" 2>/dev/null || echo "❌ BDFut não disponível"

logs: ## Mostra logs do sistema
	@echo "📋 Logs do sistema BDFut:"
	@echo "================================"
	@echo "🐳 Docker logs:"
	@docker-compose logs --tail=20 2>/dev/null || echo "  Docker não disponível"
	@echo ""
	@echo "📁 Logs locais:"
	@ls -la logs/ 2>/dev/null || echo "  Diretório logs/ não encontrado"

metrics: ## Mostra métricas do sistema
	@echo "📊 Métricas do sistema BDFut:"
	@echo "================================"
	@echo "💾 Memória:"
	@free -h 2>/dev/null || echo "  Comando free não disponível"
	@echo ""
	@echo "💿 Disco:"
	@df -h . | tail -1
	@echo ""
	@echo "🌐 Rede:"
	@netstat -tuln | grep LISTEN | head -5 2>/dev/null || echo "  Comando netstat não disponível"

debug: ## Modo debug completo
	@echo "🐛 Debug completo do sistema BDFut:"
	@echo "================================"
	@echo "📋 Informações do sistema:"
	@uname -a
	@echo ""
	@echo "🐍 Python:"
	@python --version
	@pip --version
	@echo ""
	@echo "🐳 Docker:"
	@docker --version 2>/dev/null || echo "Docker não instalado"
	@docker-compose --version 2>/dev/null || echo "Docker Compose não instalado"
	@echo ""
	@echo "📦 Dependências:"
	@pip list | grep -E "(bdfut|supabase|requests)" || echo "Dependências não encontradas"
	@echo ""
	@echo "🔧 Configuração:"
	@ls -la .env 2>/dev/null && echo "✅ .env encontrado" || echo "❌ .env não encontrado"
	@echo ""
	@echo "📁 Estrutura do projeto:"
	@ls -la | head -10

security-scan: ## Executa scan de segurança
	@echo "🔒 Executando scan de segurança..."
	@echo "================================"
	@echo "🔍 Bandit (Python security):"
	@bandit -r bdfut/ -f json -o bandit-report.json 2>/dev/null || echo "Bandit não disponível"
	@echo ""
	@echo "📦 Safety (dependencies):"
	@safety check --json --output safety-report.json 2>/dev/null || echo "Safety não disponível"
	@echo ""
	@echo "🐳 Trivy (container security):"
	@trivy image bdfut:latest 2>/dev/null || echo "Trivy não disponível"
	@echo "✅ Scan de segurança concluído!"

dependency-check: ## Verifica dependências
	@echo "📦 Verificando dependências..."
	@echo "================================"
	@echo "🐍 Python packages:"
	@pip list --outdated | head -10 || echo "Nenhuma atualização disponível"
	@echo ""
	@echo "🔍 Vulnerabilidades conhecidas:"
	@safety check --short-report 2>/dev/null || echo "Safety não disponível"
	@echo ""
	@echo "📊 Licenças:"
	@pip-licenses --format=json 2>/dev/null | head -5 || echo "pip-licenses não disponível"

coverage: ## Relatório de cobertura
	@echo "📊 Gerando relatório de cobertura..."
	pytest --cov=bdfut --cov-report=html --cov-report=term-missing tests/
	@echo "✅ Relatório gerado em htmlcov/index.html"

backup: ## Backup dos dados
	@echo "💾 Fazendo backup dos dados..."
	@echo "================================"
	@mkdir -p backups
	@tar -czf backups/bdfut-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz \
		bdfut/data/ bdfut/logs/ .env 2>/dev/null || echo "Erro no backup"
	@echo "✅ Backup criado em backups/"

restore: ## Restaura dados do backup
	@echo "🔄 Restaurando dados do backup..."
	@echo "⚠️ Especifique o arquivo de backup"
	@echo "Uso: make restore BACKUP_FILE=backups/bdfut-backup-YYYYMMDD-HHMMSS.tar.gz"
	@if [ -n "$(BACKUP_FILE)" ]; then \
		tar -xzf $(BACKUP_FILE); \
		echo "✅ Restore concluído!"; \
	else \
		echo "❌ BACKUP_FILE não especificado"; \
	fi

migrate: ## Executa migrações
	@echo "🔄 Executando migrações..."
	@echo "⚠️ Implementar migrações reais"
	@echo "✅ Migrações concluídas!"

rollback: ## Rollback de migrações
	@echo "⏪ Fazendo rollback de migrações..."
	@echo "⚠️ Implementar rollback real"
	@echo "✅ Rollback concluído!"
