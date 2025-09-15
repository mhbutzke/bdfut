# Utilitários do Projeto BDFut

Esta pasta contém utilitários e ferramentas auxiliares para manutenção e configuração do projeto.

## 📁 Conteúdo da Pasta

### Scripts de Estrutura de Banco
- **18_adicionar_colunas_types.sql** - SQL para adicionar colunas na tabela types
- **19_adicionar_colunas_types_postgres.py** - Script Python para adicionar colunas types
- **22_adicionar_colunas_countries_postgres.py** - Script para adicionar colunas countries
- **24_ajustar_estrutura_countries.py** - Script para ajustar estrutura da tabela countries

### Scripts de Coleta Especializada
- **27_coletar_countries_paginacao_completa.py** - Coleta completa de countries com paginação
- **28_simular_coleta_countries_completa.py** - Simulação de coleta completa
- **29_coletar_countries_api_real.py** - Coleta real de countries via API

## 🚀 Como Usar

### Ajustar Estrutura de Tabelas
```bash
# Adicionar colunas na tabela types
python3 utils/19_adicionar_colunas_types_postgres.py

# Ajustar estrutura da tabela countries
python3 utils/24_ajustar_estrutura_countries.py
```

### Coleta Especializada
```bash
# Coletar countries com paginação
python3 utils/27_coletar_countries_paginacao_completa.py

# Simular coleta completa
python3 utils/28_simular_coleta_countries_completa.py
```

## ⚠️ Cuidados

- **Backup**: Sempre faça backup do banco antes de executar scripts de estrutura
- **Teste**: Teste em ambiente de desenvolvimento antes de produção
- **Dependências**: Verifique se as tabelas existem antes de executar scripts de modificação
- **Permissões**: Alguns scripts podem precisar de permissões especiais no Supabase

## 📝 Notas Técnicas

- Scripts SQL devem ser executados diretamente no Supabase SQL Editor
- Scripts Python podem ser executados localmente com as credenciais configuradas
- Todos os scripts foram atualizados para funcionar com a nova estrutura de pastas
- Logs de execução são salvos automaticamente na pasta `logs/`
