# 🎯 ROADMAP REALISTA - BASEADO NO PLANO ATUAL

## 📊 ENDPOINTS CONFIRMADOS DISPONÍVEIS

**Teste realizado em:** 16 setembro 2025  
**Endpoints testados:** 10  
**Disponíveis:** 3 (30%)  
**Estratégia:** Focar nos disponíveis + criar sistemas próprios  

---

## ✅ FASE 1: IMPLEMENTAR ENDPOINTS DISPONÍVEIS (Semanas 1-2)

### **💰 EPIC 1.1: TRANSFERS SYSTEM (CRÍTICO)**
**Duração:** 1 semana | **Status:** ✅ Disponível | **Registros:** 25+

#### **🔧 Implementação Completa (5 dias)**

**Day 1: Criar Tabela**
```sql
-- EXECUTAR NO SQL EDITOR DO SUPABASE
CREATE TABLE IF NOT EXISTS public.transfers (
    id BIGSERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE NOT NULL,
    player_id BIGINT,
    from_team_id BIGINT,
    to_team_id BIGINT,
    transfer_date DATE,
    transfer_type TEXT,
    fee_amount BIGINT,
    fee_currency TEXT DEFAULT 'EUR',
    contract_duration INTEGER,
    announcement_date DATE,
    window_period TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_transfers_player_id ON public.transfers(player_id);
CREATE INDEX idx_transfers_date ON public.transfers(transfer_date);
```

**Day 2-3: Implementar Métodos**
```python
# ADICIONAR EM: bdfut/core/sportmonks_client.py
def get_transfers(self, include: Optional[str] = None) -> List[Dict]:
    """Busca transferências (CONFIRMADO DISPONÍVEL)"""
    endpoint = '/transfers'
    params = {}
    if include:
        params['include'] = include
    return self.get_paginated_data(endpoint, params)

# ADICIONAR EM: bdfut/core/supabase_client.py
def upsert_transfers(self, transfers: List[Dict]) -> bool:
    """Insere transferências"""
    try:
        data = []
        for transfer in transfers:
            transfer_data = {
                'sportmonks_id': transfer.get('id'),
                'player_id': transfer.get('player_id'),
                'from_team_id': transfer.get('from_team_id'),
                'to_team_id': transfer.get('to_team_id'),
                'transfer_date': transfer.get('date'),
                'transfer_type': transfer.get('type'),
                'fee_amount': transfer.get('fee', {}).get('amount') if transfer.get('fee') else None,
                'fee_currency': transfer.get('fee', {}).get('currency', 'EUR') if transfer.get('fee') else 'EUR'
            }
            data.append({k: v for k, v in transfer_data.items() if v is not None})
        
        if data:
            self.client.table('transfers').upsert(data, on_conflict='sportmonks_id').execute()
            return True
        return True
    except Exception as e:
        logger.error(f"Erro upsert transfers: {e}")
        return False
```

**Day 4-5: Coleta e Validação**
```python
# CRIAR ARQUIVO: collect_transfers_available.py
#!/usr/bin/env python3
"""
Coleta de transfers (endpoint confirmado disponível)
===================================================
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bdfut'))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient

def main():
    print('💰 COLETA DE TRANSFERS (CONFIRMADO DISPONÍVEL)')
    print('=' * 60)
    
    sportmonks = SportmonksClient(enable_cache=True, use_redis=True)
    supabase = SupabaseClient(use_service_role=True)
    
    try:
        # Coleta com includes otimizados
        print("🔄 Coletando transfers...")
        transfers = sportmonks.get_transfers(include='player,from_team,to_team')
        
        if transfers:
            print(f"✅ {len(transfers):,} transfers encontradas")
            success = supabase.upsert_transfers(transfers)
            if success:
                print(f"💾 Transfers salvas no banco")
                return True
        else:
            print("⚠️ Nenhuma transfer encontrada")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print("✅ TRANSFERS IMPLEMENTADO!" if success else "❌ Falha na implementação")
```

### **🔄 EPIC 1.2: ROUNDS SYSTEM**
**Duração:** 2 dias | **Status:** ✅ Disponível | **Registros:** 25+

```sql
-- Criar tabela rounds
CREATE TABLE IF NOT EXISTS public.rounds (
    id BIGSERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE NOT NULL,
    sport_id INTEGER,
    league_id INTEGER,
    season_id INTEGER,
    stage_id INTEGER,
    name TEXT,
    finished BOOLEAN DEFAULT FALSE,
    is_current BOOLEAN DEFAULT FALSE,
    starting_at TIMESTAMP WITH TIME ZONE,
    ending_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

```python
# Implementar métodos rounds
def get_rounds(self, include: Optional[str] = None) -> List[Dict]:
    """Busca rounds (CONFIRMADO DISPONÍVEL)"""
    endpoint = '/rounds'
    params = {}
    if include:
        params['include'] = include
    return self.get_paginated_data(endpoint, params)
```

### **🏆 EPIC 1.3: STAGES SYSTEM**
**Duração:** 2 dias | **Status:** ✅ Disponível | **Registros:** 25+

```sql
-- Expandir tabela stages existente se necessário
ALTER TABLE public.stages ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE public.stages ADD COLUMN IF NOT EXISTS stage_type TEXT;
```

---

## 🔧 FASE 2: SISTEMAS PRÓPRIOS PARA DADOS INDISPONÍVEIS (Semanas 3-6)

### **🎯 EPIC 2.1: EXPECTED GOALS PRÓPRIO**
**Estratégia:** Calcular xG baseado em dados existentes

```python
# CRIAR ARQUIVO: calculate_own_expected_goals.py
#!/usr/bin/env python3
"""
Sistema próprio de Expected Goals
=================================
"""

def calculate_xg_from_events():
    """Calcular xG baseado em events existentes"""
    
    # Usar match_events para calcular xG aproximado
    sql_xg = '''
    CREATE TABLE IF NOT EXISTS public.calculated_xg AS
    SELECT 
        fixture_id,
        team_id,
        player_id,
        COUNT(CASE WHEN event_type = 'goal' THEN 1 END) as actual_goals,
        COUNT(CASE WHEN event_type IN ('goal', 'shot_on_target', 'shot_off_target') THEN 1 END) as total_shots,
        -- Calcular xG aproximado baseado em posição e tipo de chute
        SUM(
            CASE 
                WHEN event_type = 'goal' THEN 1.0
                WHEN event_type = 'shot_on_target' AND minute BETWEEN 1 AND 18 THEN 0.8  -- Área
                WHEN event_type = 'shot_on_target' THEN 0.4  -- Fora da área
                WHEN event_type = 'shot_off_target' AND minute BETWEEN 1 AND 18 THEN 0.3
                WHEN event_type = 'shot_off_target' THEN 0.1
                ELSE 0
            END
        ) as calculated_xg
    FROM match_events 
    WHERE event_type IN ('goal', 'shot_on_target', 'shot_off_target')
    GROUP BY fixture_id, team_id, player_id
    '''
    
    return sql_xg
```

### **🥅 EPIC 2.2: TOP SCORERS PRÓPRIO**
**Estratégia:** Calcular rankings baseado em events

```python
# CRIAR ARQUIVO: calculate_own_top_scorers.py
#!/usr/bin/env python3
"""
Sistema próprio de Top Scorers
==============================
"""

def calculate_top_scorers_from_events():
    """Calcular artilheiros baseado em events"""
    
    sql_scorers = '''
    CREATE TABLE IF NOT EXISTS public.calculated_top_scorers AS
    SELECT 
        e.player_id,
        f.season_id,
        f.league_id,
        COUNT(CASE WHEN e.event_type = 'goal' THEN 1 END) as goals,
        COUNT(CASE WHEN e.event_type = 'assist' THEN 1 END) as assists,
        COUNT(DISTINCT f.sportmonks_id) as appearances,
        ROUND(
            COUNT(CASE WHEN e.event_type = 'goal' THEN 1 END) * 90.0 / 
            NULLIF(SUM(COALESCE(l.minutes_played, 90)), 0), 2
        ) as goals_per_90
    FROM match_events e
    JOIN fixtures f ON e.fixture_id = f.sportmonks_id
    LEFT JOIN match_lineups l ON e.fixture_id = l.fixture_id AND e.player_id = l.player_id
    WHERE e.event_type IN ('goal', 'assist')
    GROUP BY e.player_id, f.season_id, f.league_id
    HAVING COUNT(CASE WHEN e.event_type = 'goal' THEN 1 END) > 0
    ORDER BY f.season_id DESC, goals DESC
    '''
    
    return sql_scorers
```

### **👥 EPIC 2.3: TEAM SQUADS PRÓPRIO**
**Estratégia:** Inferir elencos baseado em lineups

```python
# CRIAR ARQUIVO: calculate_own_team_squads.py
#!/usr/bin/env python3
"""
Sistema próprio de Team Squads
==============================
"""

def calculate_squads_from_lineups():
    """Calcular elencos baseado em lineups"""
    
    sql_squads = '''
    CREATE TABLE IF NOT EXISTS public.calculated_team_squads AS
    SELECT DISTINCT
        ROW_NUMBER() OVER (ORDER BY l.team_id, f.season_id, l.player_id) as id,
        l.team_id,
        f.season_id,
        l.player_id,
        l.player_name,
        l.position_id,
        l.position_name,
        MODE() WITHIN GROUP (ORDER BY l.jersey_number) as most_used_jersey,
        COUNT(DISTINCT f.sportmonks_id) as appearances,
        MAX(l.captain::int) > 0 as was_captain,
        MIN(f.match_date) as first_appearance,
        MAX(f.match_date) as last_appearance
    FROM match_lineups l
    JOIN fixtures f ON l.fixture_id = f.sportmonks_id
    WHERE l.player_id IS NOT NULL
    GROUP BY l.team_id, f.season_id, l.player_id, l.player_name, l.position_id, l.position_name
    HAVING COUNT(DISTINCT f.sportmonks_id) >= 3  -- Mínimo 3 aparições
    ORDER BY l.team_id, f.season_id, appearances DESC
    '''
    
    return sql_squads
```

---

## 🚀 ROADMAP REALISTA FINAL

### **📊 IMPLEMENTAÇÃO IMEDIATA (Semana 1):**
1. ✅ **TRANSFERS** - Dados de mercado únicos
2. ✅ **ROUNDS** - Estrutura de campeonatos
3. ✅ **STAGES** - Fases de competições

### **🔧 SISTEMAS PRÓPRIOS (Semanas 2-4):**
4. 🎯 **Expected Goals calculado** - baseado em events
5. 🥅 **Top Scorers calculado** - baseado em events  
6. 👥 **Team Squads calculado** - baseado em lineups

### **📈 VALOR REALISTA ESPERADO:**
- **Transfers:** 25+ registros reais
- **Rounds:** 25+ estruturas
- **Stages:** 25+ fases
- **Sistemas próprios:** 50.000+ registros calculados
- **Total adicional:** ~50.100 registros

---

## 🎯 PRÓXIMA AÇÃO RECOMENDADA

**IMPLEMENTAR TRANSFERS IMEDIATAMENTE** - é o único endpoint de alto valor disponível no plano atual.

**Depois criar sistemas próprios** para suprir os dados não disponíveis, transformando limitações em oportunidades de inovação!

🚀 **FOCO: MAXIMIZAR VALOR COM RECURSOS DISPONÍVEIS!**
