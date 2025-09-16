# Guia de Instalação - BDFut 🚀

## Visão Geral

Este guia fornece instruções detalhadas para instalar e configurar o sistema BDFut em diferentes ambientes e sistemas operacionais.

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Instalação Rápida](#instalação-rápida)
3. [Instalação Detalhada](#instalação-detalhada)
4. [Configuração Inicial](#configuração-inicial)
5. [Verificação da Instalação](#verificação-da-instalação)
6. [Troubleshooting](#troubleshooting)

---

## Pré-requisitos

### Sistema Operacional

| Sistema | Versão Mínima | Status |
|---------|---------------|--------|
| Ubuntu | 18.04 LTS | ✅ Suportado |
| Debian | 9+ | ✅ Suportado |
| CentOS | 7+ | ✅ Suportado |
| RHEL | 7+ | ✅ Suportado |
| macOS | 10.14+ | ✅ Suportado |
| Windows | 10+ | ⚠️ WSL Recomendado |

### Software Necessário

#### Python
- **Versão**: 3.8 ou superior
- **Pip**: Incluído com Python
- **Venv**: Incluído com Python

#### Git
- **Versão**: 2.0 ou superior
- **Uso**: Clonar repositório

#### Redis (Opcional)
- **Versão**: 3.0 ou superior
- **Uso**: Cache de dados
- **Status**: Recomendado para produção

### Contas e Serviços

#### Sportmonks API
- **Conta**: Gratuita disponível
- **API Key**: Necessária
- **Limite**: 100 requests/dia (gratuito)

#### Supabase
- **Conta**: Gratuita disponível
- **Projeto**: Necessário
- **Credenciais**: URL e chave anon

---

## Instalação Rápida

### Script de Instalação Automática

```bash
# Download e execução do script de instalação
curl -fsSL https://raw.githubusercontent.com/bdfut/bdfut/main/scripts/install.sh | bash

# Ou usando wget
wget -O - https://raw.githubusercontent.com/bdfut/bdfut/main/scripts/install.sh | bash
```

### Instalação Manual Rápida

```bash
# Clone o repositório
git clone https://github.com/bdfut/bdfut.git
cd bdfut

# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale dependências
pip install -e .

# Configure
cp bdfut/config/secrets/env_example.txt .env
nano .env

# Teste
bdfut show-config
```

---

## Instalação Detalhada

### 1. Instalação do Python

#### Ubuntu/Debian

```bash
# Atualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar Python 3.9
sudo apt install python3.9 python3.9-pip python3.9-venv python3.9-dev

# Instalar dependências do sistema
sudo apt install build-essential libssl-dev libffi-dev

# Verificar instalação
python3.9 --version
pip3.9 --version
```

#### CentOS/RHEL

```bash
# Instalar EPEL
sudo yum install epel-release

# Instalar Python 3.9
sudo yum install python39 python39-pip python39-devel

# Instalar dependências do sistema
sudo yum groupinstall "Development Tools"
sudo yum install openssl-devel libffi-devel

# Verificar instalação
python3.9 --version
pip3.9 --version
```

#### macOS

```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python 3.9
brew install python@3.9

# Verificar instalação
python3.9 --version
pip3.9 --version
```

#### Windows

1. **Download do Python**:
   - Acesse [python.org](https://www.python.org/downloads/)
   - Download Python 3.9.x
   - Execute o instalador
   - ✅ Marque "Add Python to PATH"

2. **Verificar Instalação**:
   ```cmd
   python --version
   pip --version
   ```

3. **WSL (Recomendado)**:
   ```bash
   # Instalar WSL2
   wsl --install

   # Instalar Ubuntu no WSL
   wsl --install -d Ubuntu

   # Seguir instruções do Ubuntu
   ```

### 2. Instalação do Git

#### Ubuntu/Debian
```bash
sudo apt install git
```

#### CentOS/RHEL
```bash
sudo yum install git
```

#### macOS
```bash
brew install git
```

#### Windows
- Download do [Git for Windows](https://git-scm.com/download/win)
- Execute o instalador
- Use as configurações padrão

### 3. Instalação do Redis (Opcional)

#### Ubuntu/Debian
```bash
# Instalar Redis
sudo apt install redis-server

# Configurar Redis
sudo nano /etc/redis/redis.conf

# Iniciar Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verificar status
sudo systemctl status redis-server
redis-cli ping
```

#### CentOS/RHEL
```bash
# Instalar Redis
sudo yum install redis

# Iniciar Redis
sudo systemctl start redis
sudo systemctl enable redis

# Verificar status
sudo systemctl status redis
redis-cli ping
```

#### macOS
```bash
# Instalar Redis
brew install redis

# Iniciar Redis
brew services start redis

# Verificar status
redis-cli ping
```

#### Docker
```bash
# Executar Redis em container
docker run -d --name redis -p 6379:6379 redis:alpine

# Verificar status
docker exec redis redis-cli ping
```

### 4. Clone do Repositório

```bash
# Clone o repositório
git clone https://github.com/bdfut/bdfut.git
cd bdfut

# Verificar estrutura
ls -la
```

**Estrutura esperada:**
```
bdfut/
├── bdfut/
├── docs/
├── tests/
├── requirements.txt
├── setup.py
├── README.md
└── .gitignore
```

### 5. Criação do Ambiente Virtual

```bash
# Criar ambiente virtual
python3.9 -m venv venv

# Ativar ambiente virtual
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# Verificar ativação
which python
# Deve mostrar: /path/to/bdfut/venv/bin/python
```

### 6. Instalação das Dependências

```bash
# Atualizar pip
pip install --upgrade pip

# Instalação básica
pip install -e .

# Instalação com dependências de desenvolvimento
pip install -e ".[dev]"

# Verificar instalação
pip list | grep bdfut
```

**Dependências principais:**
- requests
- supabase
- redis
- tenacity
- click
- tqdm

### 7. Verificação da Instalação

```bash
# Verificar comando CLI
bdfut --help

# Verificar versão
bdfut --version

# Verificar configuração
bdfut show-config
```

---

## Configuração Inicial

### 1. Obter Credenciais

#### Sportmonks API

1. **Acesse**: [Sportmonks](https://www.sportmonks.com/)
2. **Crie conta**: Registro gratuito
3. **Navegue**: Dashboard > API
4. **Gere chave**: Create New API Key
5. **Copie chave**: Salve a chave gerada

#### Supabase

1. **Acesse**: [Supabase Dashboard](https://supabase.com/dashboard)
2. **Crie projeto**: New Project
3. **Configure**: Nome e senha do banco
4. **Aguarde**: Criação do projeto (2-3 minutos)
5. **Obtenha credenciais**: Settings > API
6. **Copie**: URL e chave anon

### 2. Configuração do Ambiente

```bash
# Copiar arquivo de exemplo
cp bdfut/config/secrets/env_example.txt .env

# Editar configurações
nano .env
```

**Conteúdo do arquivo .env:**
```bash
# ====================================
# CONFIGURAÇÃO SPORTMONKS API
# ====================================
SPORTMONKS_API_KEY=sua_chave_aqui
SPORTMONKS_BASE_URL=https://api.sportmonks.com/v3/football

# ====================================
# CONFIGURAÇÃO SUPABASE
# ====================================
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon_aqui

# ====================================
# CONFIGURAÇÕES DE ETL
# ====================================
RATE_LIMIT_PER_HOUR=3000
BATCH_SIZE=100
MAX_RETRIES=3
RETRY_DELAY=5

# ====================================
# CONFIGURAÇÕES DE CACHE
# ====================================
REDIS_URL=redis://localhost:6379
CACHE_TTL_HOURS=24
ENABLE_CACHE=true

# ====================================
# CONFIGURAÇÕES DE AMBIENTE
# ====================================
BDFUT_ENV=development
LOG_LEVEL=INFO
```

### 3. Configuração do Banco de Dados

#### Via Supabase CLI

```bash
# Instalar Supabase CLI
npm install -g supabase

# Login
supabase login

# Link do projeto
supabase link --project-ref seu-project-id

# Executar migrações
supabase db push
```

#### Via SQL Editor

1. **Acesse**: Supabase Dashboard > SQL Editor
2. **Execute**: Arquivo `deployment/supabase/migrations/001_create_sportmonks_schema.sql`
3. **Verifique**: Tables > Verificar se tabelas foram criadas

### 4. Configuração de Cache

#### Redis Local
```bash
# Verificar Redis
redis-cli ping

# Configurar no .env
REDIS_URL=redis://localhost:6379
ENABLE_CACHE=true
```

#### Redis Remoto
```bash
# Configurar no .env
REDIS_URL=redis://user:password@redis-server:6379
ENABLE_CACHE=true
```

#### Sem Cache
```bash
# Configurar no .env
ENABLE_CACHE=false
```

---

## Verificação da Instalação

### 1. Teste de Configuração

```bash
# Verificar configuração
bdfut show-config

# Saída esperada:
# ✅ Sportmonks API: Configurada
# ✅ Supabase: Configurada
# ✅ Redis: Configurada (se habilitado)
# ✅ Ambiente: development
```

### 2. Teste de Conectividade

```bash
# Testar conectividade
bdfut test-connection

# Saída esperada:
# ✅ Sportmonks: Conectado
# ✅ Supabase: Conectado
# ✅ Redis: Conectado (se habilitado)
```

### 3. Teste de Funcionalidade

```bash
# Sincronização básica
bdfut sync-base

# Saída esperada:
# ✅ Countries sincronizados: X
# ✅ States sincronizados: Y
# ✅ Types sincronizados: Z
```

### 4. Verificação de Logs

```bash
# Verificar logs
tail -f logs/development.log

# Saída esperada:
# 2025-01-13 10:00:00 - INFO - Iniciando sincronização
# 2025-01-13 10:00:01 - INFO - Countries sincronizados: 195
# 2025-01-13 10:00:02 - INFO - Sincronização concluída
```

---

## Troubleshooting

### Problemas Comuns

#### 1. Python não encontrado

**Erro:**
```bash
python3.9: command not found
```

**Solução:**
```bash
# Ubuntu/Debian
sudo apt install python3.9

# CentOS/RHEL
sudo yum install python39

# macOS
brew install python@3.9

# Verificar instalação
python3.9 --version
```

#### 2. Pip não encontrado

**Erro:**
```bash
pip: command not found
```

**Solução:**
```bash
# Instalar pip
sudo apt install python3.9-pip  # Ubuntu/Debian
sudo yum install python39-pip   # CentOS/RHEL

# Ou usar módulo
python3.9 -m pip --version
```

#### 3. Erro de permissão

**Erro:**
```bash
Permission denied
```

**Solução:**
```bash
# Usar --user
pip install --user -e .

# Ou usar sudo (não recomendado)
sudo pip install -e .
```

#### 4. Erro de dependências

**Erro:**
```bash
Failed building wheel for cryptography
```

**Solução:**
```bash
# Instalar dependências do sistema
sudo apt install build-essential libssl-dev libffi-dev  # Ubuntu/Debian
sudo yum groupinstall "Development Tools"               # CentOS/RHEL
sudo yum install openssl-devel libffi-devel            # CentOS/RHEL

# Reinstalar
pip install --upgrade pip
pip install -e .
```

#### 5. Erro de Redis

**Erro:**
```bash
redis: command not found
```

**Solução:**
```bash
# Instalar Redis
sudo apt install redis-server  # Ubuntu/Debian
sudo yum install redis         # CentOS/RHEL
brew install redis             # macOS

# Ou desabilitar cache
echo "ENABLE_CACHE=false" >> .env
```

#### 6. Erro de API Key

**Erro:**
```bash
❌ Sportmonks: 401 Unauthorized
```

**Solução:**
```bash
# Verificar API key
echo $SPORTMONKS_API_KEY

# Regenerar API key
# Acesse Sportmonks Dashboard > API > Generate New Key

# Atualizar .env
nano .env
```

#### 7. Erro de Supabase

**Erro:**
```bash
❌ Supabase: Connection refused
```

**Solução:**
```bash
# Verificar URL
echo $SUPABASE_URL

# URL deve ser: https://seu-projeto.supabase.co
# Não incluir /api/v1 ou outros paths

# Atualizar .env
nano .env
```

### Logs de Debug

```bash
# Habilitar debug
export LOG_LEVEL=DEBUG

# Executar com debug
bdfut sync-base

# Verificar logs detalhados
tail -f logs/development.log
```

### Reset Completo

```bash
# Parar processos
pkill -f bdfut

# Remover ambiente virtual
rm -rf venv

# Limpar cache
redis-cli FLUSHALL

# Reinstalar
python3.9 -m venv venv
source venv/bin/activate
pip install -e .
```

---

## Próximos Passos

Após a instalação bem-sucedida:

1. **Configure automação**: [Guia de Operação](USER_GUIDES.md#guia-de-operação-etl)
2. **Monitore sistema**: [Guia de Monitoramento](USER_GUIDES.md#monitoramento)
3. **Personalize sincronização**: [Guia de Configuração](USER_GUIDES.md#guia-de-configuração)
4. **Reporte problemas**: [GitHub Issues](https://github.com/bdfut/bdfut/issues)

---

**Última atualização**: 2025-01-13  
**Versão**: 2.0  
**Responsável**: Technical Writer
