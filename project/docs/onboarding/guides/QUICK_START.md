# Quick Start - Novos Agentes ⚡

## 🚀 **INÍCIO EM 5 MINUTOS**

### **📋 PASSO 1: Entenda o Sistema (2 minutos)**
1. **Projeto:** BDFut - Sistema ETL para dados de futebol
2. **Sua função:** Agente especialista em [SUA ÁREA]
3. **Sistema:** 8 agentes trabalhando coordenadamente
4. **Método:** Ordem sequencial obrigatória (001 → 002 → 003...)

### **📋 PASSO 2: Localize Seus Arquivos (2 minutos)**
1. **Seu perfil:** `project/docs/management/agents/AGENT-[CODIGO].md`
2. **Suas tasks:** `project/docs/management/queues/QUEUE-[CODIGO].md`
3. **Status geral:** `project/docs/management/queues/QUEUE-GERAL.md`
4. **Seus arquivos:** `project/[SUA-PASTA-ESPECIFICA]/`

### **📋 PASSO 3: Primeira Ação (1 minuto)**
```bash
cd project/docs/management/queues
python3 tools/update_queue_geral.py --status
```

---

## 🔢 **REGRA ÚNICA QUE VOCÊ PRECISA SABER**

### **ORDEM SEQUENCIAL OBRIGATÓRIA:**
- **Sempre execute: 001 → 002 → 003 → 004...**
- **NUNCA pule a ordem**
- **NUNCA inicie task sem concluir anterior**
- **SEMPRE atualize QUEUE-GERAL.md ao concluir**

---

## 📁 **ONDE SALVAR SEUS ARQUIVOS**

### **🔧 ETL Engineer:**
- **Scripts:** `project/src/bdfut/scripts/etl_organized/`
- **Ferramentas:** `project/src/bdfut/tools/`
- **Logs:** `project/data/logs/`

### **🎨 Frontend Developer:**
- **Componentes:** `project/frontend/src/components/`
- **Hooks:** `project/frontend/src/hooks/`
- **Páginas:** `project/frontend/src/app/`

### **🗄️ Database Specialist:**
- **Migrações:** `project/deployment/supabase/migrations/`
- **Scripts:** `project/src/bdfut/scripts/maintenance/`

### **🔐 Security Specialist:**
- **Ferramentas:** `project/src/bdfut/tools/`
- **Guias:** `project/docs/guides/security/`

### **🧪 QA Engineer:**
- **Testes:** `project/tests/`
- **Scripts:** `project/src/bdfut/scripts/testing/`

### **⚙️ DevOps Engineer:**
- **CI/CD:** `.github/workflows/`
- **Config:** `project/config/`
- **Monitoring:** `project/monitoring/`

### **📚 Technical Writer:**
- **Docs:** `project/docs/`
- **Guias:** `project/docs/guides/`

---

## ⚡ **COMANDOS ESSENCIAIS**

### **Ver status geral:**
```bash
cd project/docs/management/queues
python3 tools/update_queue_geral.py --status
```

### **Ver sua fila:**
```bash
python3 tools/manage_queues.py --agent [SEU-CODIGO]
```

### **Marcar task concluída:**
```bash
python3 tools/update_queue_geral.py --complete "TASK-ID" "SEU-AGENTE" "Notas"
```

---

## 🎯 **SUA PRIMEIRA TASK**

### **📋 Como encontrar:**
1. Abrir `project/docs/management/queues/QUEUE-[SEU-CODIGO].md`
2. Procurar primeira task com status 🟡 PENDENTE
3. Verificar se dependências estão ✅ CONCLUÍDAS
4. Iniciar seguindo template obrigatório

### **📋 Como executar:**
1. **Ler** todos os critérios de sucesso
2. **Usar** template obrigatório da sua área
3. **Salvar** na estrutura correta de pastas
4. **Gerar** relatório ao concluir
5. **Atualizar** QUEUE-GERAL.md

---

## 🏆 **VOCÊ ESTÁ PRONTO!**

### **✅ Com estas informações você pode:**
- Localizar seus arquivos
- Executar sua primeira task
- Seguir padrões de qualidade
- Manter coordenação com outros agentes

### **📞 Se tiver dúvidas:**
- **Processo:** Consultar `standards/`
- **Templates:** Consultar `templates/`
- **Exemplos:** Consultar `examples/`
- **Impedimentos:** Escalar para Orquestrador

---

**🎯 Bem-vindo ao projeto BDFut! Você está pronto para trabalhar com excelência! 🚀**
