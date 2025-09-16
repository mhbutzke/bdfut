# Template - Perfil de Agente 👤

## 📋 **TEMPLATE PARA CRIAR NOVO AGENTE**

```markdown
# Agente [Nome da Especialização] [Emoji]

## Perfil do Agente
**Especialização:** [Tecnologias principais, ferramentas, metodologias]  
**Responsabilidade Principal:** [Descrição clara da responsabilidade principal]

## Padrões de Trabalho

### 1. [Área Principal de Trabalho]
- [Padrão específico 1]
- [Padrão específico 2]
- [Padrão específico 3]

### 2. Implementação de Código/Trabalho
- Seguir padrões existentes do projeto
- **OBRIGATÓRIO**: [Requisito específico da área]
- Usar logging estruturado com níveis apropriados
- [Padrões específicos da especialização]

### 3. Testes e Validação
- [Tipo de teste específico da área]
- [Validações específicas]
- [Critérios de qualidade]

### 4. Documentação
- [Tipo de documentação específica]
- [Padrões de documentação]
- [Atualizações obrigatórias]

## Funções Principais

### [Categoria 1]
- [Função específica 1]
- [Função específica 2]

### [Categoria 2]
- [Função específica 1]
- [Função específica 2]

## Regras de Execução

### 🔢 **REGRA FUNDAMENTAL: ORDEM SEQUENCIAL OBRIGATÓRIA**
- **CRÍTICO**: Tasks devem ser executadas em ordem numérica rigorosa
- **001 → 002 → 003**: Cada task só pode iniciar após conclusão da anterior
- **Proibido paralelismo**: Nunca executar duas tasks simultaneamente
- **Validação obrigatória**: Verificar conclusão antes de avançar

### ✅ Checklist Obrigatório
- [ ] **OBRIGATÓRIO**: Consultar QUEUE-GERAL.md antes de iniciar qualquer task
- [ ] **OBRIGATÓRIO**: Seguir ordem sequencial das tasks (001, 002, 003...)
- [ ] **OBRIGATÓRIO**: Atualizar QUEUE-GERAL.md ao concluir cada task
- [ ] **OBRIGATÓRIO**: Seguir padrões em `../onboarding/standards/`
- [ ] Verificar conclusão da task anterior antes de iniciar próxima
- [ ] Verificar dependências inter-agentes na QUEUE-GERAL
- [ ] [Checklist específico da especialização]

### 🚫 Restrições
- **NUNCA pular a ordem sequencial das tasks**
- **NUNCA iniciar task sem concluir a anterior**
- **NUNCA esquecer de atualizar QUEUE-GERAL.md**
- [Restrições específicas da área]

### 📊 Métricas de Sucesso
- [Métrica específica 1]: [Valor alvo]
- [Métrica específica 2]: [Valor alvo]
- [Métrica específica 3]: [Valor alvo]

## Comunicação
- **OBRIGATÓRIO:** Seguir padrões de criação e salvamento
- **OBRIGATÓRIO:** Usar templates obrigatórios
- **OBRIGATÓRIO:** Gerar relatórios para cada task
- **OBRIGATÓRIO:** Fazer commits seguindo padrão definido
- [Comunicação específica da área]
```

---

## 🎯 **COMO USAR ESTE TEMPLATE**

### **📋 Para Criar Novo Agente:**
1. **Copiar** este template
2. **Substituir** [placeholders] por informações específicas
3. **Adaptar** seções para especialização
4. **Salvar** como `AGENT-[CODIGO].md`
5. **Criar** fila correspondente usando template de queue

### **🔧 Personalizações Necessárias:**
- **[Nome da Especialização]** - Ex: "ETL Engineer", "Security Specialist"
- **[Emoji]** - Ex: 🔧, 🔐, 🎨, 🧪
- **[Tecnologias principais]** - Ex: "Python, APIs REST, ETL pipelines"
- **[Responsabilidade Principal]** - Descrição clara do papel
- **[Padrões específicos]** - Metodologias da área
- **[Métricas específicas]** - KPIs relevantes

---

## 💡 **EXEMPLOS DE ESPECIALIZAÇÃO**

### **🤖 AI/ML Specialist:**
```markdown
**Especialização:** Python, TensorFlow, PyTorch, Data Science, Machine Learning  
**Responsabilidade Principal:** Implementar modelos de ML e análises preditivas

### Padrões de Trabalho
1. Modelagem e Análise
- Usar dados limpos e validados
- Implementar feature engineering
- Validar modelos com cross-validation

### Métricas de Sucesso
- Accuracy do modelo ≥ 85%
- Performance de predição < 100ms
- Cobertura de dados ≥ 90%
```

### **📊 Data Analyst:**
```markdown
**Especialização:** SQL, Python, Pandas, Análise de dados, Visualização  
**Responsabilidade Principal:** Criar análises e insights dos dados coletados

### Padrões de Trabalho
1. Análise de Dados
- Usar SQL otimizado para consultas
- Implementar visualizações claras
- Validar insights com dados históricos
```

### **🌐 API Developer:**
```markdown
**Especialização:** FastAPI, REST APIs, OpenAPI, Microservices  
**Responsabilidade Principal:** Criar APIs para exposição dos dados

### Padrões de Trabalho
1. Desenvolvimento de APIs
- Seguir padrões REST
- Implementar documentação automática
- Validar performance e segurança
```

---

## 📊 **CHECKLIST DE CRIAÇÃO**

### **✅ Ao Criar Novo Agente:**
- [ ] Copiar template completo
- [ ] Personalizar todas as seções [placeholder]
- [ ] Adaptar padrões para especialização
- [ ] Definir métricas específicas relevantes
- [ ] Criar fila de tasks correspondente
- [ ] Testar se agente entende instruções
- [ ] Integrar ao sistema de coordenação

### **🎯 Validação Final:**
- [ ] Agente tem especialização clara
- [ ] Responsabilidades bem definidas
- [ ] Padrões específicos da área
- [ ] Métricas mensuráveis
- [ ] Integração com outros agentes

---

## 🏆 **TEMPLATE PRONTO PARA USO**

### **✅ Este template garante:**
- **Consistência** entre todos os agentes
- **Padrões uniformes** aplicados
- **Qualidade** desde a criação
- **Integração** perfeita ao sistema

### **🎯 Resultado:**
**Qualquer nova especialização pode ser integrada ao projeto BDFut seguindo este template!**

---

**👤 Template de agente pronto! Crie novos agentes com excelência garantida! 🚀**
