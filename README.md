# BDFut v2.0 - Sistema ETL Profissional para Dados de Futebol

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Sistema completo e profissional de ETL (Extract, Transform, Load) para sincronizar dados de futebol da API Sportmonks com banco de dados Supabase.

## 🚀 Características Principais

- ✅ **Arquitetura Modular** - Código organizado em módulos especializados
- ✅ **Múltiplos Ambientes** - Suporte para desenvolvimento e produção
- ✅ **CLI Profissional** - Interface de linha de comando intuitiva
- ✅ **Configuração Centralizada** - Sistema de configuração flexível
- ✅ **Testes Automatizados** - Suite completa de testes
- ✅ **Documentação Completa** - Documentação técnica detalhada
- ✅ **Rate Limiting Inteligente** - Respeita limites da API automaticamente
- ✅ **Logging Avançado** - Sistema de logs estruturado
- ✅ **Cache Inteligente** - Sistema de cache para otimização
- ✅ **Monitoramento** - Métricas e health checks

## 📋 Funcionalidades

### 🔄 Sincronização de Dados
- Ligas e temporadas completas
- Times e jogadores
- Partidas e eventos
- Estatísticas detalhadas
- Classificações e standings

### 🌍 Ligas Suportadas
- **Brasil**: Serie A, Serie B, Copa do Brasil
- **Argentina**: Liga Profesional
- **Europa**: Premier League, La Liga, Bundesliga, Ligue 1, etc.
- **Internacionais**: Champions League, Europa League, Copa Libertadores

### 🛠️ Ferramentas de Desenvolvimento
- Scripts ETL organizados por categoria
- Utilitários de manutenção
- Notebooks para análise
- Ferramentas de deployment

## 🏗️ Arquitetura do Projeto

```
bdfut/
├── bdfut/                    # Pacote principal
│   ├── core/                 # Módulos principais
│   │   ├── sportmonks_client.py
│   │   ├── supabase_client.py
│   │   └── etl_process.py
│   ├── config/               # Configurações
│   │   ├── settings.py
│   │   ├── environments/
│   │   └── secrets/
│   ├── scripts/              # Scripts organizados
│   │   ├── etl/              # Scripts de ETL
│   │   ├── sync/             # Scripts de sincronização
│   │   ├── maintenance/      # Scripts de manutenção
│   │   ├── testing/          # Scripts de teste
│   │   └── utils/            # Scripts utilitários
│   ├── tools/                # Ferramentas e utilitários
│   ├── notebooks/            # Notebooks Jupyter
│   ├── data/                 # Dados e arquivos JSON
│   ├── logs/                 # Arquivos de log
│   ├── archive/              # Arquivos arquivados
│   └── cli.py                # Interface CLI
├── docs/                     # Documentação
│   ├── agents/               # Documentação dos agentes
│   ├── queues/               # Documentação das filas
│   ├── api/                  # Documentação da API
│   ├── guides/               # Guias e tutoriais
│   └── examples/             # Exemplos de uso
├── tests/                    # Testes automatizados
├── deployment/               # Configurações de deployment
│   └── supabase/             # Configurações do Supabase
├── pyproject.toml            # Configuração do projeto
├── requirements.txt          # Dependências
├── setup.py                  # Setup do projeto
├── Dockerfile                # Configuração Docker
├── docker-compose.yml        # Compose Docker
├── Makefile                  # Comandos Make
└── README.md                 # Este arquivo
```

## 🚀 Instalação

### 1. Clone o Repositório
```bash
git clone https://github.com/bdfut/bdfut.git
cd bdfut
```

### 2. Instale as Dependências
```bash
# Instalação básica
pip install -e .

# Instalação com dependências de desenvolvimento
pip install -e ".[dev]"
```

### 3. Configure o Ambiente
```bash
# Copie o arquivo de exemplo
cp bdfut/config/secrets/env_example.txt .env

# Edite as configurações
nano .env
```

### 4. Configure o Banco de Dados
Execute as migrações no Supabase SQL Editor:
```sql
-- Arquivo: migrations/001_create_sportmonks_schema.sql
```

## 📖 Uso

### CLI Principal
```bash
# Verificar configuração
bdfut show-config

# Testar conexões
bdfut test-connection

# Sincronização básica
bdfut sync-base

# Sincronizar ligas específicas
bdfut sync-leagues -l 648 -l 651

# Sincronização completa
bdfut full-sync

# Sincronização incremental
bdfut incremental
```

### Scripts Específicos
```bash
# Scripts de ETL
python bdfut/scripts/etl/01_popular_leagues_seasons.py

# Scripts de sincronização
python bdfut/scripts/sync/sync_brasileirao_final.py

# Scripts de manutenção
python bdfut/scripts/maintenance/35_coletar_todos_types_paginacao.py

# Scripts de teste
python bdfut/scripts/testing/30_testar_token_api.py

# Scripts utilitários
python bdfut/scripts/utils/51_verificar_estrutura_fixtures.py
python bdfut/scripts/utils/test_sportmonks_api.py
```

### Notebooks
```bash
# Instalar Jupyter
pip install jupyter

# Executar notebooks
jupyter notebook bdfut/notebooks/
```

## ⚙️ Configuração

### Ambientes
- **Desenvolvimento**: `BDFUT_ENV=development`
- **Produção**: `BDFUT_ENV=production`

### Variáveis de Ambiente
```bash
# API Sportmonks
SPORTMONKS_API_KEY=sua_chave_aqui

# Supabase
SUPABASE_URL=sua_url_aqui
SUPABASE_KEY=sua_chave_aqui

# Configurações ETL
RATE_LIMIT_PER_HOUR=3000
BATCH_SIZE=100
MAX_RETRIES=3
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Testes com cobertura
pytest --cov=bdfut --cov-report=html

# Testes específicos
pytest tests/test_sportmonks_client.py
```

## 📊 Monitoramento

### Logs
- **Desenvolvimento**: `bdfut/logs/development.log`
- **Produção**: `bdfut/logs/production.log`

### Métricas
- Rate limiting da API
- Performance de sincronização
- Erros e warnings
- Health checks

## 🔧 Desenvolvimento

### Estrutura de Código
- **Core**: Módulos principais do sistema
- **Config**: Configurações e ambientes
- **Scripts**: Scripts organizados por função
- **Tools**: Utilitários e ferramentas
- **Tests**: Testes automatizados

### Padrões de Código
- **Black**: Formatação automática
- **Flake8**: Linting
- **MyPy**: Verificação de tipos
- **Pytest**: Testes

### Contribuição
1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📚 Documentação

- **API**: `docs/api/` - Documentação da API Sportmonks
- **Guias**: `docs/guides/` - Tutoriais e guias
- **Exemplos**: `docs/examples/` - Exemplos de uso
- **Notebooks**: `bdfut/notebooks/` - Análises e exemplos interativos

## 🚀 Deployment

### Supabase
```bash
# Configurar Supabase CLI
supabase login
supabase link --project-ref seu-project-id

# Executar migrações
supabase db push

# Migrações estão em deployment/supabase/migrations/
```

### Docker (Em breve)
```bash
# Build da imagem
docker build -t bdfut .

# Executar container
docker run -d --env-file .env bdfut
```

## 📈 Roadmap

- [ ] **v2.1**: Dashboard web
- [ ] **v2.2**: API REST própria
- [ ] **v2.3**: Cache Redis
- [ ] **v2.4**: Webhooks em tempo real
- [ ] **v2.5**: Machine Learning para previsões

## 🤝 Suporte

- **Issues**: [GitHub Issues](https://github.com/bdfut/bdfut/issues)
- **Documentação**: [Wiki](https://github.com/bdfut/bdfut/wiki)
- **Discord**: [Comunidade BDFut](https://discord.gg/bdfut)

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **Sportmonks** pela excelente API de dados de futebol
- **Supabase** pela plataforma de banco de dados
- **Comunidade Python** pelas ferramentas incríveis

---

**BDFut v2.0** - Desenvolvido com ❤️ para a comunidade de futebol