# Estrutura de Arquivos - Padrões Obrigatórios 📁

## 🗂️ **ESTRUTURA OBRIGATÓRIA POR AGENTE**

### **🔧 ETL ENGINEER:**
```
project/src/bdfut/
├── scripts/etl_organized/         📜 SEUS SCRIPTS PRINCIPAIS
│   ├── 01_setup/                  🏗️ Configuração inicial
│   ├── 02_base_data/              📊 Dados base
│   ├── 03_leagues_seasons/        🏆 Ligas, temporadas, teams
│   ├── 04_fixtures_events/        ⚽ Fixtures, eventos, stats
│   └── 05_quality_checks/         ✅ Validações
├── tools/                         🛠️ SUAS FERRAMENTAS
│   ├── *_manager.py               🎯 Gerenciadores
│   ├── test_*.py                  🧪 Scripts teste
│   └── validation_*.py            ✅ Validações
└── core/                          💎 COMPONENTES CORE
    ├── sportmonks_client.py       📡 Cliente API
    ├── supabase_client.py          🗄️ Cliente Supabase
    ├── etl_process.py              🔄 Processo ETL
    └── ...                         (outros módulos)

project/data/logs/                 📊 SEUS LOGS E RELATÓRIOS
├── task_etl_*.md                  📋 Relatórios tasks
├── collection_*.log               📊 Logs coleta
└── validation_*.md                ✅ Relatórios validação
```

### **🎨 FRONTEND DEVELOPER:**
```
project/frontend/src/              🎨 SEU CÓDIGO FRONTEND
├── app/                           📱 SUAS PÁGINAS
│   ├── dashboard/                 📊 Dashboard principal
│   ├── etl/                       🔧 Monitoramento ETL
│   ├── data-quality/              🧪 Qualidade dados
│   ├── metrics/                   📈 Métricas sistema
│   └── ...                        (outras páginas)
├── components/                    🧩 SEUS COMPONENTES
│   ├── ui/                        🎨 Componentes base
│   ├── auth/                      🔐 Autenticação
│   ├── dashboard/                 📊 Dashboard específicos
│   ├── charts/                    📈 Gráficos
│   └── ...                        (outros componentes)
├── hooks/                         🎣 SEUS HOOKS
│   ├── useETLData.ts              🔧 Dados ETL
│   ├── useDataQuality.ts          🧪 Qualidade
│   ├── useSystemMetrics.ts        📊 Métricas
│   └── ...                        (outros hooks)
└── lib/                           📚 SUAS BIBLIOTECAS
    ├── supabase.ts                🗄️ Cliente Supabase
    ├── query-client.ts            🔄 React Query
    └── ...                        (outras libs)
```

### **🗄️ DATABASE SPECIALIST:**
```
project/deployment/supabase/       🗄️ SUAS MIGRAÇÕES
├── migrations/                    📊 SUAS MIGRAÇÕES SQL
│   ├── *_create_*.sql             🏗️ Criação tabelas
│   ├── *_optimize_*.sql           ⚡ Otimizações
│   ├── *_constraints_*.sql        🔗 Constraints
│   └── ...                        (outras migrações)
└── config.toml                    ⚙️ Configuração

project/src/bdfut/scripts/maintenance/  🔧 SEUS SCRIPTS
├── validate_*.py                  ✅ Validações
├── optimize_*.py                  ⚡ Otimizações
└── monitor_*.py                   📊 Monitoramento
```

### **🔐 SECURITY SPECIALIST:**
```
project/src/bdfut/tools/           🛠️ SUAS FERRAMENTAS
├── audit_manager.py               📝 Auditoria
├── encryption_manager.py          🔒 Criptografia
├── lgpd_compliance_manager.py     📋 LGPD
├── security_monitoring_manager.py 📊 Monitoramento
└── test_*_system.py               🧪 Testes segurança

project/docs/guides/security/      📚 SEUS GUIAS
├── LGPD_COMPLIANCE_MANUAL.md      📋 Manual LGPD
├── SECURITY_TESTING_GUIDE.md      🧪 Testes
└── ...                            (outros guias)
```

### **🧪 QA ENGINEER:**
```
project/tests/                     🧪 SEUS TESTES
├── test_*.py                      🧪 Testes unitários
├── test_integration.py            🔄 Testes integração
├── test_e2e.py                    🎯 Testes E2E
├── test_performance.py            📊 Testes performance
├── test_security.py               🔐 Testes segurança
├── conftest.py                    ⚙️ Configuração
└── htmlcov/                       📊 Relatórios cobertura
```

### **⚙️ DEVOPS ENGINEER:**
```
.github/workflows/                 🔄 SEU CI/CD
├── test.yml                       🧪 Testes automáticos
├── build-deploy.yml               🚀 Build e deploy
└── ...                            (outros workflows)

project/config/                    ⚙️ SUAS CONFIGURAÇÕES
├── docker-compose.yml             🐳 Docker
├── Dockerfile                     📦 Imagem
├── Makefile                       🎯 Automação
└── ...                            (outras configs)

project/monitoring/                📊 SUA OBSERVABILIDADE
├── prometheus.yml                 📈 Métricas
├── grafana/                       📊 Dashboards
└── alertmanager.yml               🚨 Alertas
```

### **📚 TECHNICAL WRITER:**
```
project/docs/                      📚 TODA SUA DOCUMENTAÇÃO
├── guides/                        📖 SEUS GUIAS
│   ├── user/                      👤 Usuários
│   ├── technical/                 🔧 Técnicos
│   └── security/                  🔐 Segurança
├── reference/                     📋 SUA REFERÊNCIA
│   ├── api/                       🌐 API Sportmonks
│   └── architecture/              🏗️ Arquitetura
└── management/                    🎭 Gestão (compartilhado)
```

---

## 📝 **CONVENÇÕES DE NOMENCLATURA**

### **🔧 ETL Scripts:**
```python
# Formato: XX_categoria_YY_descricao_especifica.py
04_fixtures_events_11_enrich_events_2023.py
03_leagues_seasons_08_complete_coaches.py
05_quality_checks_07_validate_enrichment.py
```

### **🎨 Frontend Componentes:**
```typescript
// PascalCase + função específica
MetricCard.tsx              // Componente UI
RealtimeMetrics.tsx         // Dashboard específico
DataQualityChart.tsx        // Gráfico específico
```

### **🗄️ Database Migrações:**
```sql
-- Formato: YYYYMMDD_HHMMSS_descricao_funcionalidade.sql
20250915_120000_create_transfers_table.sql
20250915_130000_optimize_fixtures_indices.sql
```

### **🔐 Security Ferramentas:**
```python
# Formato: categoria_manager.py
audit_manager.py
encryption_manager.py
lgpd_compliance_manager.py
```

### **🧪 QA Testes:**
```python
# Formato: test_categoria_funcionalidade.py
test_etl_process_complete.py
test_security_rls_policies.py
test_frontend_components.py
```

### **⚙️ DevOps Configs:**
```yaml
# Formato: funcionalidade.yml ou categoria-funcionalidade.yml
test.yml                    # CI/CD testes
build-deploy.yml            # Build e deploy
prometheus.yml              # Monitoramento
```

### **📚 Documentação:**
```markdown
# Formato: CATEGORIA_FUNCIONALIDADE.md ou GUIDE_CATEGORIA.md
INSTALLATION_GUIDE.md
DEVELOPMENT_STANDARDS.md
SECURITY_TESTING_GUIDE.md
```

---

## 📊 **RELATÓRIOS OBRIGATÓRIOS**

### **Formato Universal:**
```markdown
# TASK-[AGENTE]-XXX - Relatório de Execução ✅

## 📊 Resumo da Execução
**Task:** TASK-[AGENTE]-XXX
**Agente:** [Emoji] [Nome]
**Data:** YYYY-MM-DD
**Status:** ✅ CONCLUÍDA

## 🎯 Objetivo Alcançado
[Descrição do que foi feito]

## ✅ Critérios Atendidos
- [x] Critério 1
- [x] Critério 2

## 📋 Entregáveis
- ✅ [Arquivo 1] - [Localização]
- ✅ [Arquivo 2] - [Localização]

## 📊 Métricas
- [Métrica específica do agente]

## 🎯 Próxima Task
TASK-[AGENTE]-XXX pode iniciar
```

---

## 🔄 **LOCALIZAÇÃO DOS RELATÓRIOS**

### **Por Agente:**
- **🔧 ETL:** `project/data/logs/TASK_ETL_XXX_REPORT_YYYYMMDD.md`
- **🎨 Frontend:** `project/frontend/docs/TASK_FE_XXX_REPORT_YYYYMMDD.md`
- **🗄️ Database:** `project/data/logs/TASK_DB_XXX_REPORT_YYYYMMDD.md`
- **🔐 Security:** `project/data/logs/TASK_SEC_XXX_REPORT_YYYYMMDD.md`
- **🧪 QA:** `project/tests/reports/TASK_QA_XXX_REPORT_YYYYMMDD.md`
- **⚙️ DevOps:** `project/config/reports/TASK_DEVOPS_XXX_REPORT_YYYYMMDD.md`
- **📚 Docs:** `project/docs/reports/TASK_DOCS_XXX_REPORT_YYYYMMDD.md`

---

## 🛠️ **FERRAMENTAS DE VALIDAÇÃO**

### **📊 Verificar Estrutura:**
```bash
# Verificar se arquivos estão nos locais corretos
find project -name "TASK_*_REPORT_*.md" | sort

# Verificar estrutura de pastas
tree project -d -L 3
```

### **✅ Validar Nomenclatura:**
```bash
# Scripts ETL seguem padrão?
ls project/src/bdfut/scripts/etl_organized/*/*.py

# Componentes Frontend seguem padrão?
ls project/frontend/src/components/*/*.tsx
```

---

## 🎯 **COMPLIANCE E QUALIDADE**

### **📋 Checklist de Estrutura:**
- [ ] Arquivos na pasta correta do agente
- [ ] Nomenclatura seguindo padrão
- [ ] Relatórios gerados corretamente
- [ ] Logs salvos na localização apropriada
- [ ] Documentação atualizada

### **🏆 Padrões de Excelência:**
- **Organização:** 100% dos arquivos na estrutura correta
- **Nomenclatura:** 100% seguindo convenções
- **Relatórios:** 100% das tasks com relatório
- **Qualidade:** Padrões específicos do agente atendidos

---

## 🚀 **PRÓXIMO PASSO**

### **Para Novos Agentes:**
**Ler `NAMING_CONVENTIONS.md` para dominar as convenções de nomenclatura!**

### **Para Agentes Existentes:**
**Revisar e aplicar estrutura nas próximas tasks!**

---

**📁 Estrutura de arquivos dominada! Você sabe onde salvar tudo! 🗂️**
