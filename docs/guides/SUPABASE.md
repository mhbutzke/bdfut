# 📚 SUPABASE - Guia de Acesso e Modificação do Banco de Dados

## 🔑 Credenciais de Acesso

### **Supabase Dashboard**
- **URL**: https://supabase.com/dashboard/project/qoqeshyuwmxfrjdkhwii
- **Projeto**: qoqeshyuwmxfrjdkhwii

### **Chaves de API**
```bash
# Chave Anônima (para operações básicas)
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFvcWVzaHl1d214ZnJqZGtod2lpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc2OTMxNzQsImV4cCI6MjA3MzI2OTE3NH0.4nj58uQ6FeKXAlJn4H2Qe13lws8JK9jrk7r8RwoP_10

# Chave de Serviço (para operações administrativas)
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFvcWVzaHl1d214ZnJqZGtod2lpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzY5MzE3NCwiZXhwIjoyMDczMjY5MTc0fQ.QPgk88JViYHXekcJwsHtBgIU7CjKWx1ZUkd1nEkRGoQ

# URL da API
SUPABASE_URL=https://qoqeshyuwmxfrjdkhwii.supabase.co
```

### **PostgreSQL Direto**
```bash
# Host Principal (pode ter timeout)
Host: db.qoqeshyuwmxfrjdkhwii.supabase.co
Port: 5432
Database: postgres
User: postgres
Password: HRX*rht.htq7ufx@hpz

# Session Pooler (recomendado para conexões estáveis)
Host: aws-0-us-west-1.pooler.supabase.com
Port: 6543
Database: postgres
User: postgres.qoqeshyuwmxfrjdkhwii
Password: HRX*rht.htq7ufx@hpz
```

## 🛠️ Métodos de Acesso

### **1. Supabase Client (Python)**
```python
from supabase import create_client
from config.config import Config

# Inicializar cliente
config = Config()
supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

# Operações básicas
result = supabase.table('leagues').select('*').execute()
supabase.table('leagues').insert(data).execute()
supabase.table('leagues').update(data).eq('id', 1).execute()
supabase.table('leagues').delete().eq('id', 1).execute()
```

### **2. PostgreSQL Direto (psycopg2)**
```python
import psycopg2

# Conectar ao PostgreSQL
conn = psycopg2.connect(
    host='aws-0-us-west-1.pooler.supabase.com',
    port=6543,
    database='postgres',
    user='postgres.qoqeshyuwmxfrjdkhwii',
    password='HRX*rht.htq7ufx@hpz'
)

conn.autocommit = True
cursor = conn.cursor()

# Executar SQL
cursor.execute("SELECT * FROM leagues;")
result = cursor.fetchall()

cursor.close()
conn.close()
```

### **3. Supabase Dashboard (Interface Web)**
- Acesse: https://supabase.com/dashboard/project/qoqeshyuwmxfrjdkhwii
- Navegue para "Table Editor"
- Visualize e edite dados diretamente
- Use "SQL Editor" para queries customizadas

## 📊 Estrutura das Tabelas

### **Tabelas Principais**
```sql
-- Tabela de países
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE,
    continent_id INTEGER,
    name VARCHAR(255),
    official_name VARCHAR(255),
    fifa_name VARCHAR(255),
    iso2 VARCHAR(2) UNIQUE,
    iso3 VARCHAR(3) UNIQUE,
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    borders TEXT,
    image_path TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de ligas
CREATE TABLE leagues (
    id SERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE,
    name VARCHAR(255),
    country VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de tipos
CREATE TABLE types (
    id SERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE,
    name VARCHAR(255),
    code VARCHAR(50),
    developer_name VARCHAR(255),
    model_type VARCHAR(50),
    stat_group VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 Modificações de Estrutura

### **Adicionar Colunas**
```python
# Método 1: Via Supabase Client (limitado)
# Não funciona para DDL - apenas para DML

# Método 2: Via PostgreSQL Direto (recomendado)
import psycopg2

def add_column_to_table(table_name, column_name, column_type):
    conn = psycopg2.connect(
        host='aws-0-us-west-1.pooler.supabase.com',
        port=6543,
        database='postgres',
        user='postgres.qoqeshyuwmxfrjdkhwii',
        password='HRX*rht.htq7ufx@hpz'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_type};"
    cursor.execute(sql)
    
    cursor.close()
    conn.close()
```

### **Remover Colunas**
```python
def drop_column_from_table(table_name, column_name):
    conn = psycopg2.connect(
        host='aws-0-us-west-1.pooler.supabase.com',
        port=6543,
        database='postgres',
        user='postgres.qoqeshyuwmxfrjdkhwii',
        password='HRX*rht.htq7ufx@hpz'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    sql = f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {column_name};"
    cursor.execute(sql)
    
    cursor.close()
    conn.close()
```

### **Criar Tabelas**
```python
def create_table(table_name, columns_sql):
    conn = psycopg2.connect(
        host='aws-0-us-west-1.pooler.supabase.com',
        port=6543,
        database='postgres',
        user='postgres.qoqeshyuwmxfrjdkhwii',
        password='HRX*rht.htq7ufx@hpz'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql});"
    cursor.execute(sql)
    
    cursor.close()
    conn.close()
```

## 📝 Operações de Dados

### **Inserção em Lote**
```python
def insert_batch_data(table_name, data_list, batch_size=50):
    config = Config()
    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i + batch_size]
        try:
            supabase.table(table_name).insert(batch).execute()
            print(f"✅ Lote {i//batch_size + 1}: {len(batch)} registros salvos")
        except Exception as e:
            print(f"⚠️ Erro no lote {i//batch_size + 1}: {e}")
            # Salvar individualmente em caso de erro
            for item in batch:
                try:
                    supabase.table(table_name).insert(item).execute()
                except Exception as e2:
                    print(f"❌ Erro ao salvar item: {e2}")
```

### **Upsert (Inserir ou Atualizar)**
```python
def upsert_data(table_name, data, conflict_column='sportmonks_id'):
    config = Config()
    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    
    try:
        supabase.table(table_name).upsert(data, on_conflict=conflict_column).execute()
        print(f"✅ Upsert realizado com sucesso")
    except Exception as e:
        print(f"❌ Erro no upsert: {e}")
```

### **Consultas com Paginação**
```python
def get_paginated_data(table_name, page_size=25, page=1):
    config = Config()
    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    
    result = supabase.table(table_name).select('*').range(
        (page-1) * page_size, 
        page * page_size - 1
    ).execute()
    
    return result.data
```

## 🔍 Consultas Úteis

### **Verificar Estrutura de Tabela**
```sql
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'leagues' 
ORDER BY ordinal_position;
```

### **Contar Registros**
```python
def count_records(table_name):
    config = Config()
    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    
    result = supabase.table(table_name).select('*', count='exact').execute()
    return result.count
```

### **Verificar Constraints**
```sql
SELECT conname, contype, confrelid::regclass 
FROM pg_constraint 
WHERE conrelid = 'leagues'::regclass;
```

## ⚠️ Limitações e Considerações

### **Supabase Client**
- ✅ Excelente para operações DML (INSERT, UPDATE, DELETE, SELECT)
- ❌ Não suporta DDL (CREATE, ALTER, DROP) via API
- ✅ Suporte nativo a paginação e filtros
- ✅ Tratamento automático de JSON

### **PostgreSQL Direto**
- ✅ Suporte completo a DDL e DDL
- ✅ Controle total sobre transações
- ⚠️ Pode ter problemas de conectividade com host principal
- ✅ Session pooler resolve problemas de timeout

### **Rate Limiting**
- Supabase: 3000 requests/hora por entidade
- PostgreSQL: Sem limite específico, mas respeitar recursos
- Recomendação: 0.5s entre requisições para APIs externas

## 🚀 Scripts de Exemplo

### **Script Completo de Modificação**
```python
#!/usr/bin/env python3
"""
Script para modificar estrutura de tabela no Supabase
"""

import psycopg2
import logging

def modify_table_structure():
    # Credenciais
    DB_CONFIG = {
        'host': 'aws-0-us-west-1.pooler.supabase.com',
        'port': 6543,
        'database': 'postgres',
        'user': 'postgres.qoqeshyuwmxfrjdkhwii',
        'password': 'HRX*rht.htq7ufx@hpz'
    }
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Adicionar colunas
        columns_to_add = [
            "ALTER TABLE leagues ADD COLUMN IF NOT EXISTS sport_id INTEGER;",
            "ALTER TABLE leagues ADD COLUMN IF NOT EXISTS active BOOLEAN;",
            "ALTER TABLE leagues ADD COLUMN IF NOT EXISTS short_code VARCHAR(10);"
        ]
        
        for sql in columns_to_add:
            cursor.execute(sql)
            print(f"✅ Executado: {sql}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    modify_table_structure()
```

## 📋 Checklist de Operações

### **Antes de Modificar**
- [ ] Backup dos dados importantes
- [ ] Testar em ambiente de desenvolvimento
- [ ] Verificar se há dependências (foreign keys)
- [ ] Documentar mudanças

### **Durante a Modificação**
- [ ] Usar transações quando possível
- [ ] Verificar logs de erro
- [ ] Testar conectividade
- [ ] Monitorar performance

### **Após a Modificação**
- [ ] Verificar estrutura final
- [ ] Testar operações básicas
- [ ] Atualizar documentação
- [ ] Notificar equipe sobre mudanças

## 🔗 Links Úteis

- **Supabase Dashboard**: https://supabase.com/dashboard/project/qoqeshyuwmxfrjdkhwii
- **Documentação Supabase**: https://supabase.com/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **psycopg2 Docs**: https://www.psycopg.org/docs/

---

**Última atualização**: 13 de Setembro de 2025  
**Versão**: 1.0  
**Autor**: Sistema de Documentação Automática
