# GitHub Actions - Pipelines CI/CD 🚀

## 📋 **Visão Geral**

O BDFut possui um sistema completo de CI/CD implementado com GitHub Actions, garantindo qualidade, segurança e automação em todo o ciclo de desenvolvimento.

## 🔄 **Workflows Implementados**

### 1. **CI/CD Pipeline** (`test.yml`)
**Trigger:** Push/PR para main/develop  
**Objetivo:** Validação de qualidade e testes

#### 🎯 **Jobs:**
- **Quality & Security:** 
  - Pre-commit hooks
  - Bandit (security scan)
  - Safety (dependency vulnerabilities)
  - Upload de relatórios de segurança

- **Multi-Version Testing:**
  - Testes em Python 3.8, 3.9, 3.10, 3.11
  - Coverage com threshold de 60%
  - Upload para Codecov
  - Artefatos de teste

### 2. **Build & Deploy** (`build-deploy.yml`)
**Trigger:** Workflow CI/CD completo + Push para main + Tags  
**Objetivo:** Build, deploy e validação em ambientes

#### 🎯 **Jobs:**
- **Build Docker Image:**
  - Multi-platform (AMD64/ARM64)
  - Push para GitHub Container Registry
  - Cache otimizado

- **Container Security Scan:**
  - Trivy vulnerability scanner
  - Upload para GitHub Security

- **Deploy to Staging:**
  - Deploy automático para staging
  - Environment protection

- **Integration Tests:**
  - Testes contra staging environment

- **Deploy to Production:**
  - Deploy apenas com tags de release
  - Environment protection
  - Deployment summary

### 3. **Dependencies & Security** (`dependencies.yml`)
**Trigger:** Schedule (domingos 02:00 UTC) + Mudanças em deps  
**Objetivo:** Monitoramento contínuo de segurança

#### 🎯 **Jobs:**
- **Dependency Audit:**
  - Safety check
  - Pip-audit
  - Upload de relatórios

- **Dependency Updates:**
  - Check de atualizações disponíveis
  - Lista de packages outdated

- **License Compliance:**
  - Verificação de licenças
  - Detecção de licenças problemáticas

- **Dependency Graph:**
  - Árvore de dependências
  - Detecção de conflitos

- **Create Security Issue:**
  - Issue automática em caso de vulnerabilidades

### 4. **Release Automation** (`release.yml`)
**Trigger:** Tags v* + Workflow manual  
**Objetivo:** Automação completa de releases

#### 🎯 **Jobs:**
- **Validate Release:**
  - Validação do formato da versão
  - Verificação de tag existente

- **Build Release Artifacts:**
  - Build de wheel e source distribution
  - Verificação de integridade

- **Generate Changelog:**
  - Changelog automático baseado em commits
  - Categorização por tipo (feat, fix, docs, etc.)

- **Create GitHub Release:**
  - Release no GitHub
  - Upload de artefatos
  - Support para pre-releases

- **Publish to PyPI:**
  - Publicação automática no PyPI
  - Apenas para releases stable

- **Post-Release Notifications:**
  - Sumário de release
  - Next steps

### 5. **Docker & Infrastructure** (`docker.yml`)
**Trigger:** Mudanças em Dockerfile/docker-compose + Manual  
**Objetivo:** Validação de infraestrutura

#### 🎯 **Jobs:**
- **Dockerfile Linting:**
  - Hadolint para Dockerfile
  - Validação de docker-compose

- **Docker Build Test:**
  - Build multi-platform
  - Upload de artefatos

- **Container Security Scan:**
  - Trivy security scan
  - Upload para GitHub Security

- **Container Functionality Test:**
  - Teste de inicialização
  - Teste de importação do módulo
  - Teste de CLI

- **Docker Compose Test:**
  - Teste de build
  - Validação de serviços

- **Infrastructure Validation:**
  - Verificação de arquivos obrigatórios
  - Validação da estrutura do projeto
  - Relatório de infraestrutura

- **Performance Test:**
  - Benchmark de startup time
  - Análise de tamanho da imagem

## 🔒 **Segurança**

### **Ferramentas Integradas:**
- **Bandit:** Análise de código Python para vulnerabilidades
- **Safety:** Verificação de dependências vulneráveis
- **Trivy:** Scanner de vulnerabilidades em containers
- **Hadolint:** Linting de Dockerfiles
- **CodeQL:** Análise de código (via SARIF uploads)

### **Práticas de Segurança:**
- Scan automático de dependências
- Verificação de licenças
- Security issues automáticas
- Container security scanning
- Secrets não expostos em logs

## 📊 **Monitoramento e Qualidade**

### **Métricas Coletadas:**
- **Coverage:** Threshold mínimo de 60%
- **Performance:** Tempo de startup de containers
- **Security:** Vulnerabilidades em deps e containers
- **Dependencies:** Packages outdated
- **Infrastructure:** Validação de estrutura

### **Relatórios Automáticos:**
- Security reports (artefatos)
- Test results (artefatos)
- Coverage reports (Codecov)
- Dependency trees
- Infrastructure status

## 🚀 **Como Usar**

### **Para Desenvolvimento:**
1. **Push/PR:** Triggers automático do CI/CD
2. **Pre-commit:** Validações locais antes do commit
3. **Coverage:** Mantenha acima de 60%

### **Para Releases:**
1. **Create tag:** `git tag v1.2.3`
2. **Push tag:** `git push origin v1.2.3`
3. **Automático:** Release workflow executa
4. **Manual:** Use workflow dispatch se necessário

### **Para Monitoramento:**
1. **Weekly:** Check security issues automáticas
2. **Dependencies:** Review outdated packages
3. **Performance:** Monitor container metrics

## 🛠️ **Configuração**

### **Secrets Necessários:**
```bash
# GitHub Secrets
CODECOV_TOKEN=<codecov_token>
PYPI_API_TOKEN=<pypi_token>

# Environment Variables
SUPABASE_URL=<supabase_url>
SUPABASE_KEY=<supabase_key>
SPORTMONKS_API_KEY=<sportmonks_key>
```

### **Environments:**
- **staging:** Deploy automático de main branch
- **production:** Deploy apenas com tags + approval

### **Branch Protection:**
- **main:** Require PR + CI passing
- **develop:** Allow direct push + CI passing

## 📈 **Métricas de Sucesso**

### **DevOps KPIs:**
- ✅ **Deploy time:** < 5 minutos
- ✅ **Zero downtime:** Deployments
- ✅ **99.9% uptime:** Target
- ✅ **Response time:** < 15min para incidentes

### **Quality Gates:**
- ✅ **Coverage:** ≥ 60%
- ✅ **Security:** Zero vulnerabilidades críticas
- ✅ **Performance:** Container startup < 5s
- ✅ **Dependencies:** Atualizadas semanalmente

## 🔧 **Troubleshooting**

### **Problemas Comuns:**

#### **CI Failing:**
```bash
# Executar localmente
make ci
make test-cov
make lint
```

#### **Docker Build Failing:**
```bash
# Testar build local
docker build -t bdfut .
docker run --rm bdfut python --version
```

#### **Security Issues:**
```bash
# Verificar vulnerabilidades
safety check
bandit -r bdfut/
```

#### **Coverage Baixo:**
```bash
# Gerar relatório local
pytest --cov=bdfut --cov-report=html
# Abrir htmlcov/index.html
```

## 📚 **Recursos Adicionais**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/best-practices/)
- [Security Best Practices](https://docs.github.com/en/code-security)
- [PyPI Publishing Guide](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)

---

**🎯 Este sistema de CI/CD garante qualidade, segurança e automação completa para o projeto BDFut!**
