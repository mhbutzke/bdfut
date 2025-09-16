# Templates de Scripts - Todos os Agentes 📜

## 🎯 **TEMPLATES OBRIGATÓRIOS POR AGENTE**

### **🔧 ETL ENGINEER - Template Script ETL**

```python
#!/usr/bin/env python3
"""
TASK-ETL-XXX: [Título da Task]
===============================

Objetivo: [Descrição clara do objetivo]
Dependência: TASK-ETL-XXX deve estar CONCLUÍDA
Estimativa: X dias
Data: YYYY-MM-DD

Critérios de Sucesso:
- [ ] Critério 1
- [ ] Critério 2
- [ ] Critério 3

Entregáveis:
- Script funcional
- Relatório de execução
- Validação de qualidade
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
from bdfut.core.etl_metadata import ETLMetadataManager
from bdfut.core.data_quality import DataQualityManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'../../../../data/logs/task_etl_xxx_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Função principal da task"""
    logger.info("🚀 INICIANDO TASK-ETL-XXX")
    logger.info("=" * 60)
    
    # Inicializar clientes
    sportmonks = SportmonksClient(enable_cache=True, use_redis=True)
    supabase = SupabaseClient(use_service_role=True)
    metadata = ETLMetadataManager(supabase)
    quality = DataQualityManager(supabase)
    
    try:
        # Iniciar job no sistema de metadados
        job_id = metadata.start_job('task_etl_xxx')
        logger.info(f"📊 Job iniciado: {job_id}")
        
        # [IMPLEMENTAÇÃO DA TASK AQUI]
        # 
        # Exemplo de implementação:
        # data = sportmonks.get_something()
        # success = supabase.upsert_something(data)
        # 
        records_processed = 0  # Contar registros processados
        
        # Validar qualidade dos dados
        quality_score = quality.validate_table('tabela_alvo')
        logger.info(f"📊 Score de qualidade: {quality_score}%")
        
        # Finalizar job
        metadata.complete_job(job_id, records_processed)
        
        # Gerar relatório
        generate_task_report(records_processed, quality_score)
        
        logger.info("✅ TASK-ETL-XXX CONCLUÍDA COM SUCESSO")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na TASK-ETL-XXX: {str(e)}")
        metadata.fail_job(job_id, str(e))
        return False

def generate_task_report(records_processed, quality_score):
    """Gerar relatório da task"""
    report_content = f"""# TASK-ETL-XXX - Relatório de Execução ✅

## 📊 **RESUMO DA EXECUÇÃO**
**Task:** TASK-ETL-XXX  
**Agente:** 🔧 ETL Engineer  
**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Status:** ✅ CONCLUÍDA  

## 🎯 **OBJETIVO ALCANÇADO**
[Descrição do que foi implementado]

## ✅ **CRITÉRIOS DE SUCESSO ATENDIDOS**
- [x] Critério 1 - [Como foi atendido]
- [x] Critério 2 - [Como foi atendido]
- [x] Critério 3 - [Como foi atendido]

## 📋 **ENTREGÁVEIS PRODUZIDOS**
- ✅ Script funcional - [Localização]
- ✅ Relatório de execução - Este arquivo
- ✅ Validação de qualidade - Score {quality_score}%

## 📊 **MÉTRICAS ALCANÇADAS**
- **Registros processados:** {records_processed:,}
- **Qualidade:** {quality_score}%
- **Performance:** [X] seg/batch
- **Taxa de sucesso:** [X]%

## 🎯 **PRÓXIMA TASK DESBLOQUEADA**
**TASK-ETL-XXX** pode iniciar imediatamente

## 📁 **ARQUIVOS CRIADOS**
- **Script:** `project/src/bdfut/scripts/etl_organized/XX_categoria/XX_script.py`
- **Relatório:** `project/data/logs/TASK_ETL_XXX_REPORT_{datetime.now().strftime('%Y%m%d')}.md`
- **Logs:** `project/data/logs/task_etl_xxx_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log`
"""
    
    report_path = f"../../../../data/logs/TASK_ETL_XXX_REPORT_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    logger.info(f"📋 Relatório salvo: {report_path}")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
```

---

### **🎨 FRONTEND DEVELOPER - Template Componente**

```typescript
'use client'

import { ComponentProps } from 'react'

interface [ComponentName]Props {
  /**
   * [Descrição da prop]
   */
  prop1: string
  /**
   * [Descrição da prop]
   */
  prop2?: number
  /**
   * [Descrição da prop]
   */
  children?: React.ReactNode
}

/**
 * [Descrição do componente]
 * 
 * @param props - Props do componente
 * @returns JSX.Element
 */
export default function [ComponentName]({ 
  prop1,
  prop2 = 0,
  children
}: [ComponentName]Props) {
  return (
    <div className="[tailwind-classes]">
      <div className="[estrutura-do-componente]">
        {/* Implementação do componente */}
        {children}
      </div>
    </div>
  )
}

// Exportar tipos para uso em outros componentes
export type { [ComponentName]Props }
```

### **🎨 FRONTEND DEVELOPER - Template Hook**

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { queryConfigs } from '@/lib/query-client'

// Tipos específicos do hook
export interface [DataType] {
  id: number
  // Outros campos específicos
}

/**
 * Hook para [descrição da funcionalidade]
 */
export function use[HookName]() {
  return useQuery({
    queryKey: ['categoria', 'subcategoria'],
    queryFn: async (): Promise<[DataType][]> => {
      const { data, error } = await supabase
        .from('tabela')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      return data || []
    },
    ...queryConfigs.categoria,
  })
}

/**
 * Hook para [ação específica]
 */
export function use[ActionName]() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (params: [ParamType]) => {
      const { error } = await supabase
        .from('tabela')
        .insert(params)
      
      if (error) throw error
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categoria'] })
    },
  })
}
```

---

### **🗄️ DATABASE SPECIALIST - Template Migração**

```sql
-- TASK-DB-XXX: [Título da Task]
-- Data: YYYY-MM-DD
-- Objetivo: [Descrição clara do objetivo]
-- Dependência: TASK-DB-XXX deve estar CONCLUÍDA

-- [IMPLEMENTAÇÃO SQL]

-- Exemplo de criação de tabela
CREATE TABLE IF NOT EXISTS public.[nome_tabela] (
    id BIGSERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE NOT NULL,
    [campo1] TEXT,
    [campo2] INTEGER,
    [campo3] DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_[tabela]_[campo] ON public.[nome_tabela]([campo]);
CREATE INDEX IF NOT EXISTS idx_[tabela]_created ON public.[nome_tabela](created_at);

-- Comentários para documentação
COMMENT ON TABLE public.[nome_tabela] IS '[Descrição da tabela]';
COMMENT ON COLUMN public.[nome_tabela].[campo] IS '[Descrição do campo]';

-- Exemplo de otimização
ANALYZE public.[nome_tabela];
```

---

### **🔐 SECURITY SPECIALIST - Template Ferramenta**

```python
#!/usr/bin/env python3
"""
Security Tool: [Nome da Ferramenta]
==================================

Objetivo: [Descrição clara do objetivo]
Compliance: LGPD/GDPR
Task: TASK-SEC-XXX
Data: YYYY-MM-DD
"""

import logging
from datetime import datetime
from pathlib import Path
import sys

# Configurar path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class [ToolName]:
    """[Descrição da ferramenta]"""
    
    def __init__(self):
        """Inicializar ferramenta de segurança"""
        self.supabase = SupabaseClient(use_service_role=True)
        logger.info("🔐 Ferramenta de segurança inicializada")
    
    def execute(self):
        """Executar operação de segurança"""
        try:
            logger.info("🚀 Iniciando operação de segurança")
            
            # [IMPLEMENTAÇÃO DA FERRAMENTA]
            
            logger.info("✅ Operação de segurança concluída")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na operação: {str(e)}")
            return False
    
    def validate(self):
        """Validar configuração de segurança"""
        # [IMPLEMENTAÇÃO DA VALIDAÇÃO]
        pass
    
    def generate_report(self):
        """Gerar relatório de segurança"""
        report_content = f"""# Relatório de Segurança - {self.__class__.__name__}

## 📊 Resumo
- **Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **Ferramenta:** {self.__class__.__name__}
- **Status:** ✅ EXECUTADA

## 🔐 Resultados
[Resultados da execução]

## ✅ Validações
[Validações realizadas]
"""
        
        report_path = f"../../../data/logs/SECURITY_{self.__class__.__name__.upper()}_REPORT_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        logger.info(f"📋 Relatório salvo: {report_path}")

def main():
    """Função principal"""
    tool = [ToolName]()
    success = tool.execute()
    tool.generate_report()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
```

---

### **🧪 QA ENGINEER - Template Teste**

```python
#!/usr/bin/env python3
"""
TASK-QA-XXX: [Título dos Testes]
===============================

Objetivo: [Descrição dos testes]
Dependência: TASK-QA-XXX deve estar CONCLUÍDA
Estimativa: X dias
Data: YYYY-MM-DD
"""

import pytest
import sys
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient

class Test[Funcionalidade]:
    """Testes para [funcionalidade específica]"""
    
    @pytest.fixture
    def setup_clients(self):
        """Setup dos clientes para testes"""
        sportmonks = SportmonksClient(enable_cache=False)
        supabase = SupabaseClient(use_service_role=False)
        return sportmonks, supabase
    
    def test_[funcionalidade_especifica](self, setup_clients):
        """Teste específico da funcionalidade"""
        sportmonks, supabase = setup_clients
        
        # [IMPLEMENTAÇÃO DO TESTE]
        
        # Assertions
        assert resultado is not None
        assert len(resultado) > 0
        # Outras validações específicas
    
    def test_[validacao_qualidade](self, setup_clients):
        """Teste de qualidade dos dados"""
        # [IMPLEMENTAÇÃO DA VALIDAÇÃO]
        pass
    
    def test_[performance](self, setup_clients):
        """Teste de performance"""
        import time
        
        start_time = time.time()
        # [OPERAÇÃO A SER TESTADA]
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 5.0  # Máximo 5 segundos
    
    def test_[integracao](self, setup_clients):
        """Teste de integração"""
        # [TESTE DE INTEGRAÇÃO]
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
```

---

### **⚙️ DEVOPS ENGINEER - Template GitHub Action**

```yaml
# TASK-DEVOPS-XXX: [Título da Action]
# Objetivo: [Descrição do workflow]
# Dependência: TASK-DEVOPS-XXX deve estar CONCLUÍDA

name: [Nome do Workflow]

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  [job-name]:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Setup [Tecnologia]
      uses: [action-específica]
      with:
        [configurações]
    
    - name: Install dependencies
      run: |
        [comandos de instalação]
    
    - name: Run [operação principal]
      run: |
        [comandos principais]
    
    - name: [Validação específica]
      run: |
        [comandos de validação]
    
    - name: Upload results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: [nome-artifact]
        path: [caminho-resultados]
```

---

### **📚 TECHNICAL WRITER - Template Documentação**

```markdown
# [Título do Documento] 📚

## 🎯 **Objetivo**
[Descrição clara do que este documento aborda]

## 📋 **Público-Alvo**
- [Tipo de usuário 1]
- [Tipo de usuário 2]

---

## 📊 **Visão Geral**
[Introdução ao tópico]

### **Conceitos Principais:**
- **[Conceito 1]:** [Definição]
- **[Conceito 2]:** [Definição]

---

## 🔧 **Implementação**

### **Passo 1: [Título do Passo]**
[Descrição detalhada]

```[linguagem]
# Código exemplo
[código específico]
```

### **Passo 2: [Título do Passo]**
[Descrição detalhada]

---

## ✅ **Validação**

### **Como verificar se está funcionando:**
- [ ] [Critério de validação 1]
- [ ] [Critério de validação 2]

### **Comandos de teste:**
```bash
[comandos para testar]
```

---

## 🚨 **Troubleshooting**

### **Problema Comum 1:**
**Sintoma:** [Descrição do problema]  
**Causa:** [Causa provável]  
**Solução:** [Como resolver]

### **Problema Comum 2:**
**Sintoma:** [Descrição do problema]  
**Causa:** [Causa provável]  
**Solução:** [Como resolver]

---

## 📞 **Suporte**
- **Dúvidas técnicas:** [Canal/pessoa]
- **Problemas:** [Como reportar]
- **Melhorias:** [Como sugerir]

---

**📚 Documentação atualizada em: {datetime.now().strftime('%Y-%m-%d')}**
```

---

## 🎯 **COMO USAR OS TEMPLATES**

### **📋 Para Cada Agente:**
1. **Copiar** template específico da sua área
2. **Substituir** [placeholders] por informações reais
3. **Adaptar** para sua task específica
4. **Salvar** na estrutura correta de pastas
5. **Executar** seguindo padrões

### **🔧 Personalizações Obrigatórias:**
- **[XXX]** → Número da task (008, 009, etc.)
- **[Título]** → Título específico da task
- **[Objetivo]** → Objetivo claro e mensurável
- **[Implementação]** → Código específico da task
- **[Validações]** → Testes e verificações

---

## 📊 **VALIDAÇÃO DOS TEMPLATES**

### **✅ Template está correto quando:**
- [ ] Todos os [placeholders] foram substituídos
- [ ] Imports estão corretos para o agente
- [ ] Logging está configurado apropriadamente
- [ ] Relatório é gerado automaticamente
- [ ] Estrutura de pastas está correta

### **🎯 Qualidade Garantida:**
- **Consistência** entre todos os agentes
- **Padrões uniformes** aplicados
- **Relatórios automáticos** gerados
- **Logs estruturados** salvos

---

## 🏆 **TEMPLATES PRONTOS PARA USO**

### **✅ Benefícios:**
- **Desenvolvimento 80% mais rápido**
- **Qualidade consistente** garantida
- **Padrões uniformes** aplicados
- **Relatórios automáticos**

### **🎯 Resultado:**
**Qualquer agente pode criar código de qualidade seguindo os templates!**

---

**📜 Templates dominados! Você pode criar código com padrões de excelência! 🚀**
