# Padrões de Criação e Salvamento - Todos os Agentes 📁

## 🎯 **PADRÕES UNIVERSAIS PARA TODOS OS AGENTES**

### **📋 REGRAS FUNDAMENTAIS:**
1. **SEMPRE** seguir estrutura de pastas definida
2. **SEMPRE** usar templates obrigatórios
3. **SEMPRE** gerar relatórios de execução
4. **SEMPRE** fazer commits seguindo padrão
5. **SEMPRE** atualizar QUEUE-GERAL.md

---

## 🗂️ **ESTRUTURA DE PASTAS POR AGENTE**

### **🔧 ETL ENGINEER:**
```
project/src/bdfut/scripts/etl_organized/
├── 01_setup/              🏗️ Configuração inicial
├── 02_base_data/          📊 Dados base
├── 03_leagues_seasons/    🏆 Ligas e temporadas
├── 04_fixtures_events/    ⚽ Fixtures e eventos
└── 05_quality_checks/     ✅ Validações

project/src/bdfut/tools/   🛠️ Ferramentas ETL
project/data/logs/         📊 Logs e relatórios
```

### **🎨 FRONTEND DEVELOPER:**
```
project/frontend/src/
├── app/                   📱 Páginas (App Router)
├── components/            🧩 Componentes
│   ├── ui/               🎨 UI base
│   ├── auth/             🔐 Autenticação
│   ├── dashboard/        📊 Dashboard
│   └── charts/           📈 Gráficos
├── hooks/                🎣 Hooks customizados
└── lib/                  📚 Bibliotecas
```

### **🗄️ DATABASE SPECIALIST:**
```
project/deployment/supabase/migrations/  📊 Migrações SQL
project/src/bdfut/scripts/maintenance/   🔧 Scripts manutenção
project/data/logs/                       📋 Logs database
```

### **🔐 SECURITY SPECIALIST:**
```
project/src/bdfut/tools/                 🛠️ Ferramentas segurança
project/docs/guides/security/            📚 Guias segurança
project/deployment/supabase/migrations/  🔐 Migrações segurança
```

### **🧪 QA ENGINEER:**
```
project/tests/                           🧪 Todos os testes
project/tests/htmlcov/                   📊 Relatórios cobertura
project/src/bdfut/scripts/testing/      🔧 Scripts de teste
```

### **⚙️ DEVOPS ENGINEER:**
```
.github/workflows/                       🔄 CI/CD
project/config/                          ⚙️ Configurações
project/monitoring/                      📊 Observabilidade
project/scripts/                         🔧 Scripts DevOps
```

### **📚 TECHNICAL WRITER:**
```
project/docs/                            📚 Toda documentação
project/docs/guides/                     📖 Guias categorizados
project/docs/reference/                  📋 Referência técnica
```

---

## 📝 **PADRÕES DE NOMENCLATURA POR AGENTE**

### **🔧 ETL ENGINEER:**
```python
# Scripts: XX_categoria_YY_descricao.py
04_fixtures_events_11_enrich_events_2023.py

# Relatórios: TASK_ETL_XXX_REPORT_YYYYMMDD.md
TASK_ETL_008_REPORT_20250915.md

# Logs: task_etl_xxx_YYYYMMDD_HHMMSS.log
task_etl_008_20250915_143022.log
```

### **🎨 FRONTEND DEVELOPER:**
```typescript
// Componentes: PascalCase + função
MetricCard.tsx
RealtimeMetrics.tsx

// Hooks: use + funcionalidade
useETLData.ts
useDataQuality.ts

// Páginas: page.tsx em pasta
dashboard/page.tsx
```

### **🗄️ DATABASE SPECIALIST:**
```sql
-- Migrações: YYYYMMDD_HHMMSS_descricao.sql
20250915_120000_create_transfers_table.sql

-- Scripts: validate_categoria_YYYYMMDD.py
validate_constraints_20250915.py
```

### **🔐 SECURITY SPECIALIST:**
```python
# Ferramentas: categoria_manager.py
audit_manager.py
encryption_manager.py

# Migrações: YYYYMMDD_security_funcionalidade.sql
20250915_security_enable_rls.sql
```

### **🧪 QA ENGINEER:**
```python
# Testes: test_categoria_funcionalidade.py
test_etl_process_complete.py
test_security_rls_policies.py

# Relatórios: test_report_YYYYMMDD.md
test_report_20250915.md
```

---

## 🎯 **TEMPLATES OBRIGATÓRIOS**

### **📜 Template Script ETL:**
```python
#!/usr/bin/env python3
"""
TASK-ETL-XXX: [Título]
=====================

Objetivo: [Descrição]
Dependência: TASK-ETL-XXX ✅
Estimativa: X dias
"""

import sys, os, logging
from datetime import datetime
from pathlib import Path

# [IMPORTS E CONFIGURAÇÃO]

def main():
    logger.info("🚀 INICIANDO TASK-ETL-XXX")
    
    # [IMPLEMENTAÇÃO]
    
    logger.info("✅ TASK-ETL-XXX CONCLUÍDA")
    return True

if __name__ == "__main__":
    main()
```

### **🎨 Template Componente Frontend:**
```typescript
'use client'

import { ComponentProps } from 'react'

interface [Component]Props {
  // Props do componente
}

export default function [Component]({ 
  // Destructuring
}: [Component]Props) {
  return (
    <div className="[tailwind-classes]">
      {/* Implementação */}
    </div>
  )
}
```

### **🗄️ Template Migração Database:**
```sql
-- TASK-DB-XXX: [Título]
-- Data: YYYY-MM-DD
-- Objetivo: [Descrição]

-- [IMPLEMENTAÇÃO SQL]

-- Comentários
COMMENT ON TABLE [tabela] IS '[Descrição]';
```

### **🔐 Template Ferramenta Security:**
```python
#!/usr/bin/env python3
"""
Security Tool: [Nome]
====================

Objetivo: [Descrição]
Compliance: LGPD/GDPR
"""

class [ToolName]:
    def __init__(self):
        # Inicialização
        
    def execute(self):
        # Implementação
        
if __name__ == "__main__":
    tool = [ToolName]()
    tool.execute()
```

---

## 📋 **CHECKLIST UNIVERSAL PARA TODOS**

### **✅ Antes de Iniciar Qualquer Task:**
- [ ] Consultar **QUEUE-GERAL.md** para status
- [ ] Verificar **dependência anterior** concluída
- [ ] Confirmar **ordem sequencial** (XXX-1 ✅ → XXX)
- [ ] Preparar **ambiente** específico do agente
- [ ] Configurar **logging/tracking** da task

### **✅ Durante Execução:**
- [ ] Seguir **template obrigatório** do agente
- [ ] Usar **estrutura de pastas** correta
- [ ] Implementar **validação de qualidade**
- [ ] Documentar **progresso** em logs
- [ ] Testar **funcionalidade** implementada

### **✅ Ao Finalizar:**
- [ ] Validar **todos os critérios** de sucesso
- [ ] Gerar **relatório** de execução
- [ ] Atualizar **fila individual** (QUEUE-XXX.md)
- [ ] Atualizar **QUEUE-GERAL.md** via script
- [ ] Fazer **commit** seguindo padrão
- [ ] Notificar **próxima task** desbloqueada

---

## 🔄 **PADRÃO UNIVERSAL DE COMMIT**

### **Formato Obrigatório:**
```bash
git add .
git commit -m "feat([agente]): TASK-[AGENTE]-XXX - [Título]

✅ TASK-[AGENTE]-XXX CONCLUÍDA:
- [Resultado principal 1]
- [Resultado principal 2]
- [Resultado principal 3]

📊 MÉTRICAS:
- [Métrica específica do agente]
- [Performance ou qualidade]
- [Volume ou cobertura]

🎯 PRÓXIMA TASK:
- TASK-[AGENTE]-XXX desbloqueada
- Dependências atendidas

📁 ARQUIVOS:
- [Localização dos arquivos criados]"

git push origin main
```

### **Exemplos por Agente:**
```bash
# ETL
feat(etl): TASK-ETL-008 - Coleta Completa Players

# Frontend  
feat(frontend): TASK-FE-007 - Integração Dados Reais

# Database
feat(database): TASK-DB-007 - Otimização Performance

# Security
feat(security): TASK-SEC-007 - Auditoria Compliance

# QA
feat(qa): TASK-QA-008 - Testes E2E Avançados

# DevOps
feat(devops): TASK-DEVOPS-007 - Monitoramento Avançado

# Docs
feat(docs): TASK-DOCS-007 - Manual Operacional
```

---

## 📊 **RELATÓRIOS OBRIGATÓRIOS**

### **Template Universal de Relatório:**
```markdown
# TASK-[AGENTE]-XXX - Relatório de Execução ✅

## 📊 **RESUMO DA EXECUÇÃO**
**Task:** TASK-[AGENTE]-XXX  
**Agente:** [Emoji] [Nome do Agente]  
**Data:** YYYY-MM-DD  
**Status:** ✅ CONCLUÍDA  

## 🎯 **OBJETIVO ALCANÇADO**
[Descrição do que foi implementado]

## ✅ **CRITÉRIOS DE SUCESSO ATENDIDOS**
- [x] [Critério 1] - [Como foi atendido]
- [x] [Critério 2] - [Como foi atendido]
- [x] [Critério 3] - [Como foi atendido]

## 📋 **ENTREGÁVEIS PRODUZIDOS**
- ✅ [Entregável 1] - [Localização]
- ✅ [Entregável 2] - [Localização]

## 📊 **MÉTRICAS ALCANÇADAS**
- [Métrica específica do agente]

## 🎯 **PRÓXIMA TASK**
**TASK-[AGENTE]-XXX** pode iniciar

## 📁 **ARQUIVOS CRIADOS**
- [Lista de arquivos com localizações]
```

---

## 🛠️ **FERRAMENTAS DE GESTÃO**

### **📊 Atualização de Status:**
```bash
cd project/docs/management/queues
python3 tools/update_queue_geral.py --complete "TASK-XXX" "🔧 Agente" "Notas"
```

### **📋 Verificação de Status:**
```bash
python3 tools/update_queue_geral.py --status
python3 tools/manage_queues.py --agent [CODIGO]
```

---

## 📞 **COMUNICAÇÃO ENTRE AGENTES**

### **🔄 Notificação de Conclusão:**
```markdown
📢 **TASK-[AGENTE]-XXX CONCLUÍDA**

Para: [Agentes dependentes]
De: [Agente executor]

✅ **Status:** TASK-[AGENTE]-XXX finalizada com sucesso
🎯 **Impacto:** [Tasks desbloqueadas]
📁 **Arquivos:** [Localizações importantes]
🔄 **Próximo:** [Próximas ações]
```

---

## 🏆 **PADRÕES DE QUALIDADE**

### **📊 Métricas Mínimas por Agente:**
- **🔧 ETL:** Qualidade ≥95%, Performance <5s/batch
- **🎨 Frontend:** Bundle <300kB, Performance <3s, Acessibilidade >90%
- **🗄️ Database:** Query <100ms, Uptime >99.9%
- **🔐 Security:** Vulnerabilidades = 0, Compliance 100%
- **🧪 QA:** Cobertura ≥70%, Testes passando 100%
- **⚙️ DevOps:** Deploy <5min, Uptime >99.9%
- **📚 Docs:** Completude 100%, Clareza >4.5/5

---

## 🎯 **APLICAÇÃO DOS PADRÕES**

### **📋 Para Cada Agente:**
1. **Ler** este arquivo completamente
2. **Aplicar** padrões específicos da sua área
3. **Usar** templates obrigatórios
4. **Seguir** estrutura de pastas
5. **Manter** qualidade definida

### **🔄 Para o Orquestrador:**
1. **Monitorar** aplicação dos padrões
2. **Validar** conformidade nas tasks
3. **Corrigir** desvios identificados
4. **Garantir** qualidade consistente

---

## 🚀 **PRÓXIMAS AÇÕES**

### **Para Todos os Agentes:**
1. **Estudar** padrões específicos da sua área
2. **Aplicar** em todas as próximas tasks
3. **Manter** consistência de qualidade
4. **Seguir** ordem sequencial obrigatória

### **Resultado Esperado:**
**Projeto BDFut com padrões de classe mundial aplicados consistentemente por todos os agentes!**

---

**📊 Padrões definidos | Estruturas organizadas | Qualidade garantida | Agentes orientados! 🏆**
