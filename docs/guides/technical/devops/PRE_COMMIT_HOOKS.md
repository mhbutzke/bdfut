# Pre-commit Hooks - BDFut 🔒

## 📋 **Visão Geral**

O BDFut utiliza um sistema abrangente de pre-commit hooks para garantir qualidade de código, segurança e consistência antes de cada commit. Esta configuração implementa as melhores práticas de DevOps e desenvolvimento seguro.

## 🚀 **Instalação Rápida**

### **Método Automatizado (Recomendado):**
```bash
# Execute o script de setup
./scripts/development/setup-pre-commit.sh
```

### **Método Manual:**
```bash
# Instalar pre-commit
pip install pre-commit

# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Instalar hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Primeira execução (pode demorar)
pre-commit run --all-files
```

## 🔧 **Hooks Implementados**

### **1. 📁 Basic File Quality Hooks**
Garantem qualidade básica dos arquivos:

- **trailing-whitespace**: Remove espaços em branco no final das linhas
- **end-of-file-fixer**: Garante que arquivos terminem com nova linha
- **mixed-line-ending**: Padroniza line endings para LF
- **check-yaml**: Valida sintaxe YAML (incluindo multi-documento)
- **check-json**: Valida e formata arquivos JSON
- **check-toml**: Valida sintaxe TOML
- **check-added-large-files**: Previne commit de arquivos grandes (>1MB)
- **check-merge-conflict**: Detecta marcadores de merge conflict
- **debug-statements**: Detecta imports de debugger e breakpoints
- **detect-private-key**: Detecta chaves privadas
- **check-ast**: Valida sintaxe Python (AST)
- **check-builtin-literals**: Verifica uso correto de literais built-in
- **check-docstring-first**: Garante que docstrings venham primeiro
- **name-tests-test**: Valida nomenclatura de arquivos de teste

### **2. 🐍 Python Code Formatting**
Formatação automática do código Python:

- **Black** (v23.12.1): Formatação automática de código
  - Line length: 88 caracteres
  - Python 3.8+ compatible
  
- **isort** (v5.13.2): Organização de imports
  - Profile: black (compatibilidade)
  - Line length: 88 caracteres
  
- **pyupgrade** (v3.15.0): Modernização de sintaxe
  - Target: Python 3.8+
  - Upgrade automático para syntax mais recente

### **3. 🔍 Python Code Quality**
Análise de qualidade e linting:

- **Flake8** (v6.1.0): Linting abrangente
  - Max line length: 88
  - Ignore: E203, W503 (compatibilidade com Black)
  - Max complexity: 10
  - **Plugins incluídos:**
    - flake8-docstrings: Validação de docstrings
    - flake8-bugbear: Detecção de bugs comuns
    - flake8-comprehensions: Otimização de comprehensions
    - flake8-simplify: Sugestões de simplificação

- **MyPy** (v1.8.0): Type checking
  - Strict optional checking
  - Ignore missing imports
  - **Type stubs incluídos:**
    - types-requests
    - types-click
    - types-python-dateutil

### **4. 🔒 Security Hooks**
Validações de segurança:

- **Bandit** (v1.7.5): Security linting
  - Recursive scanning
  - Skip B101 (assert_used) e B601 (paramiko_calls)
  - Exclude tests/ directory

- **GitGuardian ggshield** (v1.25.0): Secrets detection
  - Detecção de API keys, tokens, passwords
  - Integração com GitGuardian database
  - Executa apenas no stage de commit

### **5. 🐳 Docker Hooks**
Validação de containers:

- **Hadolint** (v2.12.0): Dockerfile linting
  - Ignore DL3008 (apt-get version pinning)
  - Ignore DL3009 (apt-get clean)
  - Best practices enforcement

### **6. 📚 Documentation Hooks**
Qualidade de documentação:

- **python-check-blanket-noqa**: Evita noqa genérico
- **python-check-blanket-type-ignore**: Evita type: ignore genérico
- **python-no-log-warn**: Detecta log.warn deprecated
- **python-use-type-annotations**: Força type annotations
- **rst-backticks**: Valida backticks em RST
- **rst-directive-colons**: Valida colons em diretivas RST
- **rst-inline-touching-normal**: Valida formatação RST

### **7. 💬 Commit Message Hooks**
Padronização de commits:

- **Commitizen** (v3.13.0): Conventional commits
  - Força formato: `type(scope): description`
  - Types válidos: feat, fix, docs, style, refactor, test, chore
  - Executa no stage commit-msg

### **8. 🧪 Performance and Testing**
Validações de teste e performance:

- **pytest-check**: Executa testes antes do commit
  - Execução: `pytest tests/ --tb=short`
  - Sempre executa (always_run: true)

- **coverage-check**: Verifica cobertura de testes
  - Threshold mínimo: 60%
  - Relatório: term-missing
  - Falha se cobertura < 60%

## ⚙️ **Configuração Avançada**

### **Arquivo de Configuração Local**
Crie `.pre-commit-config.local.yaml` para customizações locais:

```yaml
# Configurações locais (ignorado pelo git)
repos:
  - repo: local
    hooks:
      - id: custom-hook
        name: Custom validation
        entry: ./scripts/custom-validation.sh
        language: system
        pass_filenames: false
```

### **Configuração por Projeto**
Ajuste `.pre-commit-config.yaml` conforme necessário:

```yaml
# Desabilitar hook específico
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        exclude: ^(tests/|scripts/)  # Excluir diretórios
```

## 🚀 **Comandos Úteis**

### **Execução Manual:**
```bash
# Executar todos os hooks
pre-commit run --all-files

# Executar hook específico
pre-commit run black
pre-commit run flake8
pre-commit run mypy

# Executar apenas em arquivos modificados
pre-commit run
```

### **Manutenção:**
```bash
# Atualizar versões dos hooks
pre-commit autoupdate

# Limpar cache
pre-commit clean

# Reinstalar hooks
pre-commit uninstall
pre-commit install

# Ver hooks instalados
pre-commit run --all-files --verbose
```

### **Bypass (Use com Cuidado):**
```bash
# Pular hooks específicos
SKIP=flake8,mypy git commit -m "WIP: temporary commit"

# Pular todos os hooks (NÃO RECOMENDADO)
git commit --no-verify -m "Emergency fix"
```

## 🔧 **Integração com IDEs**

### **VS Code**
Adicione ao `settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### **PyCharm**
1. Configure Black como formatter externo
2. Configure isort para organização de imports
3. Configure Flake8 como linter
4. Habilite "Reformat code" e "Optimize imports" no commit

## 📊 **Métricas e Monitoramento**

### **Hooks por Categoria:**
- **Qualidade de Arquivo**: 13 hooks
- **Formatação Python**: 3 hooks  
- **Qualidade Python**: 2 hooks
- **Segurança**: 2 hooks
- **Docker**: 1 hook
- **Documentação**: 7 hooks
- **Commit Messages**: 1 hook
- **Testes**: 2 hooks

**Total: 31 hooks ativos**

### **Tempo de Execução Esperado:**
- **Primeira execução**: 2-5 minutos (download de dependências)
- **Execuções subsequentes**: 10-30 segundos
- **Apenas arquivos modificados**: 5-15 segundos

## 🐛 **Troubleshooting**

### **Problemas Comuns:**

#### **Hook falha com "command not found":**
```bash
# Reinstalar pre-commit
pip uninstall pre-commit
pip install pre-commit
pre-commit clean
pre-commit install
```

#### **MyPy falha com imports:**
```bash
# Instalar type stubs
pip install types-requests types-click types-python-dateutil
```

#### **Bandit falha em tests:**
```bash
# Verificar se exclude está configurado
# No .pre-commit-config.yaml:
exclude: ^tests/
```

#### **Coverage muito baixo:**
```bash
# Executar coverage localmente
pytest --cov=bdfut --cov-report=html
# Abrir htmlcov/index.html para ver detalhes
```

#### **GitGuardian falha:**
```bash
# Verificar se há secrets no código
ggshield secret scan path .
# Remover secrets e usar variáveis de ambiente
```

### **Performance Issues:**
```bash
# Limpar cache
pre-commit clean

# Executar apenas hooks essenciais
SKIP=mypy,bandit pre-commit run --all-files

# Atualizar hooks
pre-commit autoupdate
```

## 🔄 **CI/CD Integration**

Os hooks são automaticamente executados no GitHub Actions:

```yaml
# .github/workflows/test.yml
- name: Run pre-commit hooks
  uses: pre-commit/action@v3.0.0
```

## 📈 **Métricas de Qualidade**

### **Objetivos:**
- ✅ **100% dos commits** passam pelos hooks
- ✅ **Zero vulnerabilidades** detectadas pelo Bandit
- ✅ **Zero secrets** detectados pelo GitGuardian
- ✅ **Cobertura ≥ 60%** mantida
- ✅ **Complexidade ≤ 10** por função

### **KPIs:**
- **Tempo médio de hook**: < 30 segundos
- **Taxa de falha**: < 5%
- **False positives**: < 1%

## 📚 **Recursos Adicionais**

- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Code Style](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Bandit Security Linter](https://bandit.readthedocs.io/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**🎯 Este sistema de pre-commit hooks garante qualidade, segurança e consistência em todos os commits do projeto BDFut!**
