# 🚀 Criar Tabela Stages no Supabase Dashboard

## 📋 Passos para Criar a Tabela

### 1. Acesse o Supabase Dashboard
- **URL**: https://supabase.com/dashboard/project/qoqeshyuwmxfrjdkhwii
- Faça login na sua conta

### 2. Vá para o SQL Editor
- No menu lateral, clique em **"SQL Editor"**
- Clique em **"New query"**

### 3. Execute o SQL para Criar a Tabela
Cole e execute este SQL:

```sql
CREATE TABLE IF NOT EXISTS stages (
    id SERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE NOT NULL,
    sport_id INTEGER,
    country_id INTEGER,
    league_id INTEGER,
    season_id INTEGER,
    type_id INTEGER,
    name VARCHAR(255),
    short_code VARCHAR(10),
    sort_order INTEGER,
    finished BOOLEAN DEFAULT FALSE,
    is_current BOOLEAN DEFAULT FALSE,
    starting_at TIMESTAMP,
    ending_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 4. Verificar se a Tabela foi Criada
Execute este SQL para verificar:

```sql
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'stages' 
ORDER BY ordinal_position;
```

### 5. Contar Registros (deve ser 0 inicialmente)
```sql
SELECT COUNT(*) FROM stages;
```

## ✅ Após Criar a Tabela

Quando você confirmar que a tabela foi criada com sucesso, me avise e eu executarei:

```bash
python3 43_criar_tabela_stages_supabase.py
```

Isso irá inserir todos os **1.250 stages** coletados da Sportmonks API na tabela!

## 📊 Dados Prontos para Inserção

- **Arquivo JSON**: `stages_data_20250913_192232.json`
- **Total de stages**: 1.250
- **Páginas coletadas**: 50 (25 por página)
- **Status**: Todos os dados coletados e validados

## 🎯 Resultado Esperado

Após a inserção, você terá:
- ✅ Tabela `stages` criada
- ✅ 1.250 stages inseridos
- ✅ Dados completos de todas as ligas principais
- ✅ Relatório final com estatísticas
