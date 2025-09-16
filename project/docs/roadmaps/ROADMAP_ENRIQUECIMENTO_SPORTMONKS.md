# 🗺️ ROADMAP COMPLETO - ENRIQUECIMENTO SPORTMONKS API

## 📊 VISÃO GERAL DO ROADMAP

**Objetivo:** Transformar o sistema ETL enterprise em uma **plataforma de inteligência esportiva única**  
**Período:** 4 fases, 12-16 semanas  
**Crescimento esperado:** +331% (105.841 → 455.841+ registros)  
**ROI:** Transformação em líder de mercado de dados esportivos  

### ⚠️ **IMPORTANTE: ENDPOINTS RESTRITOS POR PLANO**
**Se retornar:** `"You do not have access to this endpoint"`  
**Ação:** Pular para próximo endpoint da lista de prioridades  
**Estratégia:** Sistema de fallback inteligente implementado  

---

## 🎯 FASE 1: DADOS CRÍTICOS DE MERCADO (Semanas 1-3)

### **💰 EPIC 1.1: SISTEMA DE TRANSFERS**
**Duração:** 2 semanas | **Prioridade:** 🔴 CRÍTICA | **ROI:** MUITO ALTO

#### **Sprint 1.1.1 - Infraestrutura Transfers (Semana 1)**

**🔧 Day 1-2: Criar Tabela Transfers**
```sql
-- EXECUTAR NO SQL EDITOR DO SUPABASE
CREATE TABLE IF NOT EXISTS public.transfers (
    id BIGSERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE NOT NULL,
    player_id BIGINT,
    from_team_id BIGINT,
    to_team_id BIGINT,
    transfer_date DATE,
    transfer_type TEXT, -- permanent, loan, free, exchange
    fee_amount BIGINT,
    fee_currency TEXT DEFAULT 'EUR',
    contract_duration INTEGER, -- meses
    announcement_date DATE,
    window_period TEXT, -- summer, winter, emergency
    agent_name TEXT,
    medical_completed BOOLEAN DEFAULT FALSE,
    official_confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_transfers_player_id ON public.transfers(player_id);
CREATE INDEX idx_transfers_from_team ON public.transfers(from_team_id);
CREATE INDEX idx_transfers_to_team ON public.transfers(to_team_id);
CREATE INDEX idx_transfers_date ON public.transfers(transfer_date);
CREATE INDEX idx_transfers_type ON public.transfers(transfer_type);
CREATE INDEX idx_transfers_amount ON public.transfers(fee_amount);

-- Comentários
COMMENT ON TABLE public.transfers IS 'Transferências de jogadores entre clubes';
COMMENT ON COLUMN public.transfers.fee_amount IS 'Valor da transferência em centavos';
COMMENT ON COLUMN public.transfers.transfer_type IS 'Tipo: permanent, loan, free, exchange';
```

**🔧 Day 3-4: Implementar SportmonksClient**
```python
# ADICIONAR EM: bdfut/core/sportmonks_client.py
# LOCALIZAÇÃO: Após o método get_standings_by_league()

def get_transfers(self, include: Optional[str] = None) -> List[Dict]:
    """Busca todas as transferências"""
    endpoint = '/transfers'
    params = {}
    if include:
        params['include'] = include
    return self.get_paginated_data(endpoint, params)

def get_transfers_by_player(self, player_id: int, include: Optional[str] = None) -> List[Dict]:
    """Busca transferências de um jogador específico"""
    endpoint = '/transfers'
    params = {'player_id': player_id}
    if include:
        params['include'] = include
    response = self._make_request(endpoint, params, 'transfers')
    return response.get('data', []) if response else []

def get_transfers_by_team(self, team_id: int, include: Optional[str] = None) -> List[Dict]:
    """Busca transferências de um time específico"""
    endpoint = '/transfers'
    params = {'team_id': team_id}
    if include:
        params['include'] = include
    response = self._make_request(endpoint, params, 'transfers')
    return response.get('data', []) if response else []

def get_transfers_by_date_range(self, start_date: str, end_date: str, include: Optional[str] = None) -> List[Dict]:
    """Busca transferências por período"""
    endpoint = '/transfers'
    params = {
        'start_date': start_date,
        'end_date': end_date
    }
    if include:
        params['include'] = include
    response = self._make_request(endpoint, params, 'transfers')
    return response.get('data', []) if response else []
```

**🔧 Day 5: Implementar SupabaseClient**
```python
# ADICIONAR EM: bdfut/core/supabase_client.py
# LOCALIZAÇÃO: Após o método upsert_standings()

def upsert_transfers(self, transfers: List[Dict]) -> bool:
    """Insere ou atualiza transferências"""
    try:
        data = []
        for transfer in transfers:
            # Mapear campos da API para tabela
            transfer_data = {
                'sportmonks_id': transfer.get('id'),
                'player_id': transfer.get('player_id'),
                'from_team_id': transfer.get('from_team_id'),
                'to_team_id': transfer.get('to_team_id'),
                'transfer_date': transfer.get('date'),
                'transfer_type': transfer.get('type'),
                'fee_amount': transfer.get('fee', {}).get('amount') if transfer.get('fee') else None,
                'fee_currency': transfer.get('fee', {}).get('currency') if transfer.get('fee') else 'EUR',
                'contract_duration': transfer.get('contract_duration'),
                'announcement_date': transfer.get('announcement_date'),
                'window_period': transfer.get('window'),
                'agent_name': transfer.get('agent', {}).get('name') if transfer.get('agent') else None,
                'medical_completed': transfer.get('medical_completed', False),
                'official_confirmed': transfer.get('confirmed', False)
            }
            
            # Remover campos None
            transfer_data = {k: v for k, v in transfer_data.items() if v is not None}
            data.append(transfer_data)
        
        if data:
            self.client.table('transfers').upsert(data, on_conflict='sportmonks_id').execute()
            logger.info(f"Upserted {len(data)} transfers")
            return True
        else:
            logger.warning("Nenhum transfer válido para upsert")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao fazer upsert de transfers: {str(e)}")
        return False
```

#### **Sprint 1.1.2 - Coleta e Validação (Semana 2)**

**🔧 Day 1-3: Script de Coleta Completa**
```python
# CRIAR ARQUIVO: collect_transfers_complete.py
#!/usr/bin/env python3
"""
Coleta completa de transfers com sistema de fallback
===================================================
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bdfut'))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
import time

def test_endpoint_access(sportmonks, endpoint_name, test_method):
    """Testa se endpoint está disponível no plano"""
    try:
        print(f"🔍 Testando acesso ao endpoint {endpoint_name}...")
        result = test_method()
        
        if result is None:
            print(f"⚠️ Endpoint {endpoint_name} retornou dados vazios")
            return False
        
        print(f"✅ Endpoint {endpoint_name} acessível - {len(result) if isinstance(result, list) else 1} registros")
        return True
        
    except Exception as e:
        error_msg = str(e).lower()
        if "you do not have access" in error_msg or "access to this endpoint" in error_msg:
            print(f"❌ Endpoint {endpoint_name} RESTRITO pelo plano")
            return False
        else:
            print(f"⚠️ Erro técnico em {endpoint_name}: {str(e)[:50]}")
            return False

def main():
    print('💰 COLETA COMPLETA DE TRANSFERS (COM FALLBACK)')
    print('=' * 60)
    
    sportmonks = SportmonksClient(enable_cache=True, use_redis=True)
    supabase = SupabaseClient(use_service_role=True)
    
    # LISTA DE ENDPOINTS POR PRIORIDADE (FALLBACK INTELIGENTE)
    endpoints_priority = [
        {
            'name': 'transfers',
            'test_method': lambda: sportmonks.get_transfers(),
            'collect_method': lambda: sportmonks.get_transfers(include='player,from_team,to_team'),
            'priority': 1,
            'description': 'Transferências completas'
        },
        {
            'name': 'player_transfers',
            'test_method': lambda: sportmonks.get_transfers_by_player(37614792),  # Player ID teste
            'collect_method': lambda: collect_transfers_by_players(sportmonks, supabase),
            'priority': 2,
            'description': 'Transfers por jogador'
        },
        {
            'name': 'team_transfers',
            'test_method': lambda: sportmonks.get_transfers_by_team(19),  # Team ID teste
            'collect_method': lambda: collect_transfers_by_teams(sportmonks, supabase),
            'priority': 3,
            'description': 'Transfers por time'
        }
    ]
    
    total_transfers_collected = 0
    successful_endpoint = None
    
    # Testar endpoints em ordem de prioridade
    for endpoint in endpoints_priority:
        print(f"\n🎯 TENTATIVA {endpoint['priority']}: {endpoint['description']}")
        print("-" * 50)
        
        if test_endpoint_access(sportmonks, endpoint['name'], endpoint['test_method']):
            print(f"✅ Endpoint {endpoint['name']} disponível - iniciando coleta...")
            
            try:
                # Executar coleta
                if endpoint['name'] == 'transfers':
                    # Coleta direta
                    all_transfers = sportmonks.get_transfers(include='player,from_team,to_team,agent')
                    
                    if all_transfers:
                        success = supabase.upsert_transfers(all_transfers)
                        if success:
                            total_transfers_collected = len(all_transfers)
                            print(f"💾 {total_transfers_collected:,} transfers salvas")
                            successful_endpoint = endpoint['name']
                            break
                else:
                    # Coleta via método específico
                    collected = endpoint['collect_method']()
                    if collected > 0:
                        total_transfers_collected = collected
                        successful_endpoint = endpoint['name']
                        break
                        
            except Exception as e:
                print(f"❌ Erro na coleta via {endpoint['name']}: {e}")
                continue
        else:
            print(f"⏭️ Pulando para próximo endpoint...")
            continue
    
    # Resultado final
    if successful_endpoint:
        print(f"\n🎉 COLETA BEM-SUCEDIDA!")
        print(f"✅ Endpoint usado: {successful_endpoint}")
        print(f"📊 Transfers coletadas: {total_transfers_collected:,}")
        return True
    else:
        print(f"\n❌ NENHUM ENDPOINT DE TRANSFERS DISPONÍVEL NO PLANO")
        print(f"📋 Recomendação: Focar em outros endpoints disponíveis")
        return False

def collect_transfers_by_players(sportmonks, supabase):
    """Coleta transfers via jogadores individuais"""
    main_players = supabase.client.table('players').select('sportmonks_id').limit(100).execute()
    total = 0
    
    for player in main_players.data:
        transfers = sportmonks.get_transfers_by_player(player['sportmonks_id'])
        if transfers:
            supabase.upsert_transfers(transfers)
            total += len(transfers)
    
    return total

def collect_transfers_by_teams(sportmonks, supabase):
    """Coleta transfers via times individuais"""
    main_teams = supabase.client.table('teams').select('sportmonks_id').limit(50).execute()
    total = 0
    
    for team in main_teams.data:
        transfers = sportmonks.get_transfers_by_team(team['sportmonks_id'])
        if transfers:
            supabase.upsert_transfers(transfers)
            total += len(transfers)
    
    return total

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 COLETA DE TRANSFERS CONCLUÍDA!")
    else:
        print("⚠️ Transfers não disponível - continuar com próximo endpoint")
```
        
        # FASE 2: Coleta por jogadores principais
        print("\n🔄 Coletando transfers por jogadores...")
        
        main_players = supabase.client.table('players').select('sportmonks_id').limit(1000).execute()
        
        additional_transfers = 0
        for i, player in enumerate(main_players.data):
            if i % 100 == 0:
                print(f"  📊 Progresso: {i}/1000 jogadores")
            
            player_transfers = sportmonks.get_transfers_by_player(
                player['sportmonks_id'], 
                include='from_team,to_team'
            )
            
            if player_transfers:
                success = supabase.upsert_transfers(player_transfers)
                if success:
                    additional_transfers += len(player_transfers)
            
            # Pausa para rate limiting
            if i % 50 == 49:
                time.sleep(2)
        
        print(f"✅ {additional_transfers:,} transfers adicionais coletadas")
        
        # VALIDAÇÃO FINAL
        total_result = supabase.client.table('transfers').select('id', count='exact').execute()
        total_transfers = total_result.count if total_result.count is not None else 0
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"  • Total de transfers: {total_transfers:,}")
        print(f"  • Meta atingida: {'✅' if total_transfers >= 50000 else '⚠️'}")
        
        return total_transfers >= 10000  # Meta mínima
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 COLETA DE TRANSFERS CONCLUÍDA!")
    else:
        print("❌ Coleta falhou")
```

**🔧 Day 4: Validação e Testes**
```python
# CRIAR ARQUIVO: validate_transfers_quality.py
#!/usr/bin/env python3
"""
Validação de qualidade dos transfers
===================================
"""

def main():
    print('🔍 VALIDAÇÃO DE QUALIDADE - TRANSFERS')
    
    supabase = SupabaseClient(use_service_role=True)
    
    # Verificações de qualidade
    checks = [
        "SELECT COUNT(*) FROM transfers WHERE fee_amount IS NULL",
        "SELECT COUNT(*) FROM transfers WHERE transfer_date IS NULL", 
        "SELECT COUNT(*) FROM transfers WHERE player_id IS NULL",
        "SELECT COUNT(DISTINCT player_id) FROM transfers",
        "SELECT transfer_type, COUNT(*) FROM transfers GROUP BY transfer_type"
    ]
    
    for check in checks:
        result = supabase.client.rpc('exec_sql', {'sql': check}).execute()
        print(f"✅ {check}: {result}")

if __name__ == "__main__":
    main()
```

**🔧 Day 5: Integração ETL**
```python
# ATUALIZAR: bdfut/core/etl_process.py
# ADICIONAR método process_transfers()

def process_transfers(self):
    """Processar transferências no pipeline ETL"""
    try:
        self.metadata_manager.start_job('transfers_sync')
        
        # Coleta incremental
        last_sync = self.metadata_manager.get_last_checkpoint('transfers')
        if last_sync:
            start_date = last_sync.strftime('%Y-%m-%d')
        else:
            start_date = '2020-01-01'  # Data inicial
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        transfers = self.sportmonks.get_transfers_by_date_range(
            start_date, end_date, include='player,from_team,to_team'
        )
        
        if transfers:
            success = self.supabase.upsert_transfers(transfers)
            if success:
                self.metadata_manager.save_checkpoint('transfers', datetime.now())
                self.metadata_manager.complete_job('transfers_sync', len(transfers))
        
        return True
    except Exception as e:
        self.metadata_manager.fail_job('transfers_sync', str(e))
        return False
```

**📊 Entregáveis:**
- ✅ Tabela `transfers` com 15+ campos
- ✅ 50.000+ transferências coletadas
- ✅ Sistema de coleta automatizado
- ✅ Relatórios de análise de mercado

**🎯 KPIs:**
- Meta: 50.000+ transfers
- Qualidade: 95%+ dados válidos
- Performance: <2 seg/batch
- Cobertura: Ligas principais 100%

### **💎 EPIC 1.2: MARKET VALUES & VALUATIONS**
**Duração:** 1 semana | **Prioridade:** 🟡 ALTA | **ROI:** ALTO

#### **Sprint 1.2.1 - Valores de Mercado (Semana 3)**
- [ ] **Day 1-2:** Adicionar colunas de market_value em players/teams
- [ ] **Day 3-4:** Implementar coleta de valuations
- [ ] **Day 5:** Histórico de valorização

**📊 Meta:** 25.000+ valuations históricas

---

## 🎯 FASE 2: MÉTRICAS AVANÇADAS (Semanas 4-7)

### **🎯 EPIC 2.1: EXPECTED GOALS (xG) SYSTEM**
**Duração:** 2 semanas | **Prioridade:** 🔴 CRÍTICA | **ROI:** MUITO ALTO

#### **Sprint 2.1.1 - Infraestrutura xG (Semana 4)**

**🔧 Day 1-2: Criar Tabelas Expected**
```sql
-- EXECUTAR NO SQL EDITOR DO SUPABASE

-- Tabela para Expected Goals por fixture
CREATE TABLE IF NOT EXISTS public.expected_stats (
    id BIGSERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE NOT NULL,
    fixture_id BIGINT,
    team_id BIGINT,
    expected_goals DECIMAL(4,2),
    expected_assists DECIMAL(4,2),
    expected_points DECIMAL(4,2),
    actual_goals INTEGER,
    actual_assists INTEGER,
    performance_index DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela para Expected Goals por jogador
CREATE TABLE IF NOT EXISTS public.expected_by_player (
    id BIGSERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE NOT NULL,
    player_id BIGINT,
    fixture_id BIGINT,
    team_id BIGINT,
    expected_goals DECIMAL(4,2),
    expected_assists DECIMAL(4,2),
    actual_goals INTEGER,
    actual_assists INTEGER,
    minutes_played INTEGER,
    positions_played TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_expected_stats_fixture ON public.expected_stats(fixture_id);
CREATE INDEX idx_expected_stats_team ON public.expected_stats(team_id);
CREATE INDEX idx_expected_player_player ON public.expected_by_player(player_id);
CREATE INDEX idx_expected_player_fixture ON public.expected_by_player(fixture_id);
```

**🔧 Day 3-4: Implementar SportmonksClient xG**
```python
# ADICIONAR EM: bdfut/core/sportmonks_client.py

def get_expected_by_fixture(self, fixture_id: int, include: Optional[str] = None) -> List[Dict]:
    """Busca Expected Goals de uma fixture"""
    endpoint = f'/expected/fixtures/{fixture_id}'
    params = {}
    if include:
        params['include'] = include
    response = self._make_request(endpoint, params, 'expected')
    return response.get('data', []) if response else []

def get_expected_by_player(self, player_id: int, include: Optional[str] = None) -> List[Dict]:
    """Busca Expected Goals de um jogador"""
    endpoint = f'/expected/players/{player_id}'
    params = {}
    if include:
        params['include'] = include
    response = self._make_request(endpoint, params, 'expected')
    return response.get('data', []) if response else []

def get_expected_by_team(self, team_id: int, include: Optional[str] = None) -> List[Dict]:
    """Busca Expected Goals de um time"""
    endpoint = f'/expected/teams/{team_id}'
    params = {}
    if include:
        params['include'] = include
    response = self._make_request(endpoint, params, 'expected')
    return response.get('data', []) if response else []

def get_all_expected(self, include: Optional[str] = None) -> List[Dict]:
    """Busca todos os Expected Goals"""
    endpoint = '/expected'
    params = {}
    if include:
        params['include'] = include
    return self.get_paginated_data(endpoint, params)
```

**🔧 Day 5: Implementar SupabaseClient xG**
```python
# ADICIONAR EM: bdfut/core/supabase_client.py

def upsert_expected_stats(self, expected_stats: List[Dict]) -> bool:
    """Insere ou atualiza expected stats"""
    try:
        data = []
        for stat in expected_stats:
            expected_data = {
                'sportmonks_id': stat.get('id'),
                'fixture_id': stat.get('fixture_id'),
                'team_id': stat.get('team_id'),
                'expected_goals': stat.get('expected_goals'),
                'expected_assists': stat.get('expected_assists'),
                'expected_points': stat.get('expected_points'),
                'actual_goals': stat.get('actual_goals'),
                'actual_assists': stat.get('actual_assists'),
                'performance_index': stat.get('performance_index')
            }
            
            expected_data = {k: v for k, v in expected_data.items() if v is not None}
            data.append(expected_data)
        
        if data:
            self.client.table('expected_stats').upsert(data, on_conflict='sportmonks_id').execute()
            logger.info(f"Upserted {len(data)} expected stats")
            return True
        return True
    except Exception as e:
        logger.error(f"Erro ao fazer upsert de expected stats: {str(e)}")
        return False

def upsert_expected_by_player(self, expected_players: List[Dict]) -> bool:
    """Insere ou atualiza expected by player"""
    try:
        data = []
        for player_stat in expected_players:
            player_data = {
                'sportmonks_id': player_stat.get('id'),
                'player_id': player_stat.get('player_id'),
                'fixture_id': player_stat.get('fixture_id'),
                'team_id': player_stat.get('team_id'),
                'expected_goals': player_stat.get('expected_goals'),
                'expected_assists': player_stat.get('expected_assists'),
                'actual_goals': player_stat.get('actual_goals'),
                'actual_assists': player_stat.get('actual_assists'),
                'minutes_played': player_stat.get('minutes_played'),
                'positions_played': player_stat.get('positions_played')
            }
            
            player_data = {k: v for k, v in player_data.items() if v is not None}
            data.append(player_data)
        
        if data:
            self.client.table('expected_by_player').upsert(data, on_conflict='sportmonks_id').execute()
            logger.info(f"Upserted {len(data)} expected by player")
            return True
        return True
    except Exception as e:
        logger.error(f"Erro ao fazer upsert de expected by player: {str(e)}")
        return False
```

#### **Sprint 2.1.2 - Coleta Massiva xG (Semana 5)**

**🔧 Day 1-3: Script de Coleta xG**
```python
# CRIAR ARQUIVO: collect_expected_goals_complete.py
#!/usr/bin/env python3
"""
Coleta completa de Expected Goals
================================
"""

def main():
    print('🎯 COLETA COMPLETA DE EXPECTED GOALS')
    
    sportmonks = SportmonksClient(enable_cache=True, use_redis=True)
    supabase = SupabaseClient(use_service_role=True)
    
    # FASE 1: xG por fixtures finalizadas
    finished_fixtures = supabase.client.table('fixtures').select(
        'sportmonks_id'
    ).eq('status', 'FT').limit(10000).execute()
    
    total_xg_collected = 0
    
    for i, fixture in enumerate(finished_fixtures.data):
        fixture_id = fixture['sportmonks_id']
        
        # Buscar xG da fixture
        expected_data = sportmonks.get_expected_by_fixture(
            fixture_id, include='team,player'
        )
        
        if expected_data:
            # Separar dados por tipo
            fixture_xg = [e for e in expected_data if e.get('type') == 'fixture']
            player_xg = [e for e in expected_data if e.get('type') == 'player']
            
            # Salvar dados
            if fixture_xg:
                supabase.upsert_expected_stats(fixture_xg)
                total_xg_collected += len(fixture_xg)
            
            if player_xg:
                supabase.upsert_expected_by_player(player_xg)
                total_xg_collected += len(player_xg)
        
        # Progress e rate limiting
        if i % 100 == 99:
            print(f"📊 Progresso: {i+1}/10000 fixtures, {total_xg_collected:,} xG coletados")
            time.sleep(2)
    
    print(f"✅ Total xG coletados: {total_xg_collected:,}")
    return total_xg_collected >= 100000

if __name__ == "__main__":
    main()
```

**🔧 Day 4-5: Análises de Performance**
```python
# CRIAR ARQUIVO: analyze_xg_performance.py
#!/usr/bin/env python3
"""
Análises de performance xG vs Real
==================================
"""

def main():
    print('📊 ANÁLISES xG vs PERFORMANCE REAL')
    
    supabase = SupabaseClient(use_service_role=True)
    
    # Análise 1: Over/Under performers
    over_performers = supabase.client.rpc('exec_sql', {
        'sql': '''
        SELECT 
            team_id,
            AVG(actual_goals - expected_goals) as goal_difference,
            COUNT(*) as matches_analyzed
        FROM expected_stats 
        WHERE actual_goals IS NOT NULL 
        GROUP BY team_id 
        HAVING AVG(actual_goals - expected_goals) > 0.5
        ORDER BY goal_difference DESC
        LIMIT 20
        '''
    }).execute()
    
    print(f"🎯 Top 20 Over-Performers identificados")
    
    # Análise 2: Accuracy de Expected Goals
    accuracy = supabase.client.rpc('exec_sql', {
        'sql': '''
        SELECT 
            AVG(ABS(actual_goals - expected_goals)) as avg_error,
            STDDEV(actual_goals - expected_goals) as std_error,
            COUNT(*) as total_predictions
        FROM expected_stats 
        WHERE actual_goals IS NOT NULL
        '''
    }).execute()
    
    print(f"📈 Accuracy de xG calculada")
    
    return True

if __name__ == "__main__":
    main()
```

**📊 Entregáveis:**
- ✅ 200.000+ métricas xG
- ✅ Análises de performance avançadas
- ✅ Dashboard de xG vs Goals reais
- ✅ Rankings de over/under performance

### **📈 EPIC 2.2: ADVANCED PLAYER STATISTICS**
**Duração:** 2 semanas | **Prioridade:** 🟡 ALTA | **ROI:** ALTO

#### **Sprint 2.2.1 - Estatísticas Detalhadas (Semana 6)**
- [ ] **Day 1-2:** Expandir match_statistics com 20+ novos campos
- [ ] **Day 3-4:** Heat maps e passing networks
- [ ] **Day 5:** Defensive actions detalhadas

#### **Sprint 2.2.2 - Performance Tracking (Semana 7)**
- [ ] **Day 1-3:** Sistema de tracking de performance
- [ ] **Day 4-5:** Trends e análises temporais

**📊 Meta:** 100.000+ estatísticas avançadas

---

## 🎯 FASE 3: ANÁLISES PREDITIVAS (Semanas 8-11)

### **🔮 EPIC 3.1: PREDICTIONS & PROBABILITIES**
**Duração:** 2 semanas | **Prioridade:** 🔴 CRÍTICA | **ROI:** MUITO ALTO

#### **Sprint 3.1.1 - Sistema de Predições (Semana 8)**

**🔧 Day 1-2: Criar Tabela Predictions**
```sql
-- EXECUTAR NO SQL EDITOR DO SUPABASE
CREATE TABLE IF NOT EXISTS public.predictions (
    id BIGSERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE NOT NULL,
    fixture_id BIGINT,
    home_win_probability DECIMAL(5,2),
    draw_probability DECIMAL(5,2),
    away_win_probability DECIMAL(5,2),
    over_2_5_probability DECIMAL(5,2),
    under_2_5_probability DECIMAL(5,2),
    both_teams_score_probability DECIMAL(5,2),
    confidence_score DECIMAL(3,2),
    prediction_date TIMESTAMP WITH TIME ZONE,
    actual_result TEXT, -- home_win, draw, away_win
    correct_prediction BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela para Value Bets
CREATE TABLE IF NOT EXISTS public.value_bets (
    id BIGSERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE NOT NULL,
    fixture_id BIGINT,
    market_type TEXT,
    selection TEXT,
    predicted_probability DECIMAL(5,2),
    bookmaker_odds DECIMAL(6,2),
    value_percentage DECIMAL(5,2),
    confidence_level TEXT, -- high, medium, low
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_predictions_fixture ON public.predictions(fixture_id);
CREATE INDEX idx_predictions_confidence ON public.predictions(confidence_score);
CREATE INDEX idx_predictions_date ON public.predictions(prediction_date);
CREATE INDEX idx_value_bets_fixture ON public.value_bets(fixture_id);
CREATE INDEX idx_value_bets_value ON public.value_bets(value_percentage);
```

**🔧 Day 3-4: Implementar SportmonksClient Predictions**
```python
# ADICIONAR EM: bdfut/core/sportmonks_client.py

def get_predictions_by_fixture(self, fixture_id: int, include: Optional[str] = None) -> List[Dict]:
    """Busca predições de uma fixture"""
    endpoint = f'/predictions/fixtures/{fixture_id}'
    params = {}
    if include:
        params['include'] = include
    response = self._make_request(endpoint, params, 'predictions')
    return response.get('data', []) if response else []

def get_probabilities_by_fixture(self, fixture_id: int, include: Optional[str] = None) -> List[Dict]:
    """Busca probabilidades de uma fixture"""
    endpoint = f'/predictions/probabilities/fixtures/{fixture_id}'
    params = {}
    if include:
        params['include'] = include
    response = self._make_request(endpoint, params, 'probabilities')
    return response.get('data', []) if response else []

def get_value_bets_by_fixture(self, fixture_id: int, include: Optional[str] = None) -> List[Dict]:
    """Busca value bets de uma fixture"""
    endpoint = f'/predictions/value-bets/fixtures/{fixture_id}'
    params = {}
    if include:
        params['include'] = include
    response = self._make_request(endpoint, params, 'value_bets')
    return response.get('data', []) if response else []

def get_all_predictions(self, include: Optional[str] = None) -> List[Dict]:
    """Busca todas as predições"""
    endpoint = '/predictions'
    params = {}
    if include:
        params['include'] = include
    return self.get_paginated_data(endpoint, params)
```

**🔧 Day 5: Implementar SupabaseClient Predictions**
```python
# ADICIONAR EM: bdfut/core/supabase_client.py

def upsert_predictions(self, predictions: List[Dict]) -> bool:
    """Insere ou atualiza predições"""
    try:
        data = []
        for prediction in predictions:
            prediction_data = {
                'sportmonks_id': prediction.get('id'),
                'fixture_id': prediction.get('fixture_id'),
                'home_win_probability': prediction.get('home_win_probability'),
                'draw_probability': prediction.get('draw_probability'),
                'away_win_probability': prediction.get('away_win_probability'),
                'over_2_5_probability': prediction.get('over_2_5_probability'),
                'under_2_5_probability': prediction.get('under_2_5_probability'),
                'both_teams_score_probability': prediction.get('both_teams_score_probability'),
                'confidence_score': prediction.get('confidence_score'),
                'prediction_date': prediction.get('prediction_date')
            }
            
            prediction_data = {k: v for k, v in prediction_data.items() if v is not None}
            data.append(prediction_data)
        
        if data:
            self.client.table('predictions').upsert(data, on_conflict='sportmonks_id').execute()
            logger.info(f"Upserted {len(data)} predictions")
            return True
        return True
    except Exception as e:
        logger.error(f"Erro ao fazer upsert de predictions: {str(e)}")
        return False

def upsert_value_bets(self, value_bets: List[Dict]) -> bool:
    """Insere ou atualiza value bets"""
    try:
        data = []
        for bet in value_bets:
            bet_data = {
                'sportmonks_id': bet.get('id'),
                'fixture_id': bet.get('fixture_id'),
                'market_type': bet.get('market_type'),
                'selection': bet.get('selection'),
                'predicted_probability': bet.get('predicted_probability'),
                'bookmaker_odds': bet.get('bookmaker_odds'),
                'value_percentage': bet.get('value_percentage'),
                'confidence_level': bet.get('confidence_level')
            }
            
            bet_data = {k: v for k, v in bet_data.items() if v is not None}
            data.append(bet_data)
        
        if data:
            self.client.table('value_bets').upsert(data, on_conflict='sportmonks_id').execute()
            logger.info(f"Upserted {len(data)} value bets")
            return True
        return True
    except Exception as e:
        logger.error(f"Erro ao fazer upsert de value bets: {str(e)}")
        return False
```

#### **Sprint 3.1.2 - Análises Preditivas (Semana 9)**

**🔧 Day 1-3: Script de Coleta Predictions**
```python
# CRIAR ARQUIVO: collect_predictions_complete.py
#!/usr/bin/env python3
"""
Coleta completa de predictions
=============================
"""

def main():
    print('🔮 COLETA COMPLETA DE PREDICTIONS')
    
    sportmonks = SportmonksClient(enable_cache=True, use_redis=True)
    supabase = SupabaseClient(use_service_role=True)
    
    # FASE 1: Predictions para fixtures futuras
    upcoming_fixtures = supabase.client.table('fixtures').select(
        'sportmonks_id'
    ).gte('match_date', datetime.now().strftime('%Y-%m-%d')).limit(5000).execute()
    
    total_predictions = 0
    
    for i, fixture in enumerate(upcoming_fixtures.data):
        fixture_id = fixture['sportmonks_id']
        
        try:
            # Buscar predições
            predictions = sportmonks.get_predictions_by_fixture(
                fixture_id, include='fixture'
            )
            
            # Buscar probabilidades
            probabilities = sportmonks.get_probabilities_by_fixture(
                fixture_id, include='fixture'
            )
            
            # Buscar value bets
            value_bets = sportmonks.get_value_bets_by_fixture(
                fixture_id, include='fixture,bookmaker'
            )
            
            # Salvar dados
            if predictions:
                supabase.upsert_predictions(predictions)
                total_predictions += len(predictions)
            
            if probabilities:
                supabase.upsert_predictions(probabilities)  # Mesmo formato
                total_predictions += len(probabilities)
            
            if value_bets:
                supabase.upsert_value_bets(value_bets)
                total_predictions += len(value_bets)
            
            # Rate limiting
            if i % 50 == 49:
                print(f"📊 Progresso: {i+1}/5000, {total_predictions:,} predictions")
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Erro fixture {fixture_id}: {e}")
    
    print(f"✅ Total predictions: {total_predictions:,}")
    return total_predictions >= 50000

if __name__ == "__main__":
    main()
```

**🔧 Day 4-5: Validation System**
```python
# CRIAR ARQUIVO: validate_predictions_accuracy.py
#!/usr/bin/env python3
"""
Sistema de validação de accuracy das predictions
===============================================
"""

def main():
    print('🎯 VALIDAÇÃO DE ACCURACY - PREDICTIONS')
    
    supabase = SupabaseClient(use_service_role=True)
    
    # Atualizar predictions com resultados reais
    finished_fixtures = supabase.client.table('fixtures').select(
        'sportmonks_id, home_score, away_score'
    ).eq('status', 'FT').execute()
    
    predictions_updated = 0
    
    for fixture in finished_fixtures.data:
        fixture_id = fixture['sportmonks_id']
        home_score = fixture.get('home_score', 0)
        away_score = fixture.get('away_score', 0)
        
        # Determinar resultado real
        if home_score > away_score:
            actual_result = 'home_win'
        elif away_score > home_score:
            actual_result = 'away_win'
        else:
            actual_result = 'draw'
        
        # Atualizar prediction com resultado real
        update_result = supabase.client.table('predictions').update({
            'actual_result': actual_result
        }).eq('fixture_id', fixture_id).execute()
        
        if update_result:
            predictions_updated += 1
    
    # Calcular accuracy
    accuracy_sql = '''
    UPDATE predictions 
    SET correct_prediction = (
        CASE 
            WHEN actual_result = 'home_win' AND home_win_probability = GREATEST(home_win_probability, draw_probability, away_win_probability) THEN TRUE
            WHEN actual_result = 'draw' AND draw_probability = GREATEST(home_win_probability, draw_probability, away_win_probability) THEN TRUE  
            WHEN actual_result = 'away_win' AND away_win_probability = GREATEST(home_win_probability, draw_probability, away_win_probability) THEN TRUE
            ELSE FALSE
        END
    )
    WHERE actual_result IS NOT NULL
    '''
    
    supabase.client.rpc('exec_sql', {'sql': accuracy_sql}).execute()
    
    print(f"✅ {predictions_updated:,} predictions atualizadas com resultados")
    return True

if __name__ == "__main__":
    main()
```

**📊 Entregáveis:**
- ✅ 100.000+ predições coletadas
- ✅ Sistema de validação de modelos
- ✅ Accuracy reports automáticos
- ✅ Benchmarking de performance

### **📊 EPIC 3.2: ODDS & BETTING INTELLIGENCE**
**Duração:** 2 semanas | **Prioridade:** 🟡 ALTA | **ROI:** ALTO

#### **Sprint 3.2.1 - Odds Collection (Semana 10)**
- [ ] **Day 1-3:** Sistema de coleta de odds
- [ ] **Day 4-5:** Análises de movimento de odds

#### **Sprint 3.2.2 - Market Intelligence (Semana 11)**
- [ ] **Day 1-3:** Análises de mercado de apostas
- [ ] **Day 4-5:** Value betting identification

**📊 Meta:** 500.000+ odds históricas

---

## 🎯 FASE 4: RANKINGS E ESTRUTURAS (Semanas 12-16)

### **🥅 EPIC 4.1: PERFORMANCE RANKINGS**
**Duração:** 2 semanas | **Prioridade:** 🟡 ALTA | **ROI:** ALTO

#### **Sprint 4.1.1 - Top Scorers System (Semana 12)**

**🔧 Day 1-2: Criar Tabela Top Scorers**
```sql
-- EXECUTAR NO SQL EDITOR DO SUPABASE
CREATE TABLE IF NOT EXISTS public.top_scorers (
    id BIGSERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE NOT NULL,
    season_id BIGINT,
    league_id BIGINT,
    player_id BIGINT,
    team_id BIGINT,
    position INTEGER,
    goals INTEGER,
    assists INTEGER,
    minutes_played INTEGER,
    appearances INTEGER,
    goals_per_90 DECIMAL(4,2),
    assists_per_90 DECIMAL(4,2),
    goal_involvement DECIMAL(4,2),
    penalty_goals INTEGER,
    penalty_misses INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_top_scorers_season ON public.top_scorers(season_id);
CREATE INDEX idx_top_scorers_league ON public.top_scorers(league_id);
CREATE INDEX idx_top_scorers_player ON public.top_scorers(player_id);
CREATE INDEX idx_top_scorers_goals ON public.top_scorers(goals);
CREATE INDEX idx_top_scorers_position ON public.top_scorers(position);
```

**🔧 Day 3-5: Implementar Sistema Top Scorers**
```python
# ADICIONAR EM: bdfut/core/sportmonks_client.py

def get_top_scorers_by_season(self, season_id: int, include: Optional[str] = None) -> List[Dict]:
    """Busca artilheiros de uma temporada"""
    endpoint = f'/topscorers/seasons/{season_id}'
    params = {}
    if include:
        params['include'] = include
    response = self._make_request(endpoint, params, 'topscorers')
    return response.get('data', []) if response else []

def get_top_scorers_by_league(self, league_id: int, include: Optional[str] = None) -> List[Dict]:
    """Busca artilheiros de uma liga"""
    endpoint = f'/topscorers/leagues/{league_id}'
    params = {}
    if include:
        params['include'] = include
    response = self._make_request(endpoint, params, 'topscorers')
    return response.get('data', []) if response else []

def get_all_top_scorers(self, include: Optional[str] = None) -> List[Dict]:
    """Busca todos os artilheiros"""
    endpoint = '/topscorers'
    params = {}
    if include:
        params['include'] = include
    return self.get_paginated_data(endpoint, params)

# ADICIONAR EM: bdfut/core/supabase_client.py

def upsert_top_scorers(self, top_scorers: List[Dict]) -> bool:
    """Insere ou atualiza top scorers"""
    try:
        data = []
        for scorer in top_scorers:
            scorer_data = {
                'sportmonks_id': scorer.get('id'),
                'season_id': scorer.get('season_id'),
                'league_id': scorer.get('league_id'),
                'player_id': scorer.get('player_id'),
                'team_id': scorer.get('team_id'),
                'position': scorer.get('position'),
                'goals': scorer.get('goals'),
                'assists': scorer.get('assists'),
                'minutes_played': scorer.get('minutes_played'),
                'appearances': scorer.get('appearances'),
                'goals_per_90': scorer.get('goals_per_90'),
                'assists_per_90': scorer.get('assists_per_90'),
                'goal_involvement': scorer.get('goal_involvement'),
                'penalty_goals': scorer.get('penalty_goals'),
                'penalty_misses': scorer.get('penalty_misses')
            }
            
            scorer_data = {k: v for k, v in scorer_data.items() if v is not None}
            data.append(scorer_data)
        
        if data:
            self.client.table('top_scorers').upsert(data, on_conflict='sportmonks_id').execute()
            logger.info(f"Upserted {len(data)} top scorers")
            return True
        return True
    except Exception as e:
        logger.error(f"Erro ao fazer upsert de top scorers: {str(e)}")
        return False
```

#### **Sprint 4.1.2 - Advanced Rankings (Semana 13)**

**🔧 Day 1-3: Script de Coleta Top Scorers**
```python
# CRIAR ARQUIVO: collect_top_scorers_complete.py
#!/usr/bin/env python3
"""
Coleta completa de top scorers
=============================
"""

def main():
    print('🥅 COLETA COMPLETA DE TOP SCORERS')
    
    sportmonks = SportmonksClient(enable_cache=True, use_redis=True)
    supabase = SupabaseClient(use_service_role=True)
    
    # Buscar todas as temporadas para coletar artilheiros
    seasons = supabase.client.table('seasons').select(
        'sportmonks_id, league_id, name'
    ).gte('starting_at', '2020-01-01').execute()
    
    total_scorers = 0
    
    for i, season in enumerate(seasons.data):
        season_id = season['sportmonks_id']
        league_id = season.get('league_id')
        season_name = season.get('name', 'Unknown')
        
        print(f"🏆 {i+1}/{len(seasons.data)}: {season_name} (Liga {league_id})")
        
        try:
            # Buscar top scorers da temporada
            scorers = sportmonks.get_top_scorers_by_season(
                season_id, include='player,team,season'
            )
            
            if scorers:
                success = supabase.upsert_top_scorers(scorers)
                if success:
                    total_scorers += len(scorers)
                    print(f"  ✅ {len(scorers)} artilheiros coletados")
            else:
                print(f"  ⚠️ Sem artilheiros")
            
            # Rate limiting
            if i % 20 == 19:
                time.sleep(2)
                print(f"📊 Progresso total: {total_scorers:,} artilheiros")
                
        except Exception as e:
            print(f"  ❌ Erro: {str(e)[:40]}")
    
    print(f"✅ Total artilheiros coletados: {total_scorers:,}")
    return total_scorers >= 5000

if __name__ == "__main__":
    main()
```

**📊 Meta:** 10.000+ rankings

### **👥 EPIC 4.2: TEAM COMPOSITION ANALYSIS**
**Duração:** 2 semanas | **Prioridade:** 🟡 ALTA | **ROI:** MÉDIO

#### **Sprint 4.2.1 - Team Squads (Semana 14)**

**🔧 Day 1-3: Criar Sistema Team Squads**
```sql
-- EXECUTAR NO SQL EDITOR DO SUPABASE
CREATE TABLE IF NOT EXISTS public.team_squads (
    id BIGSERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE NOT NULL,
    team_id BIGINT,
    season_id BIGINT,
    player_id BIGINT,
    jersey_number INTEGER,
    position_id INTEGER,
    position_name TEXT,
    captain BOOLEAN DEFAULT FALSE,
    vice_captain BOOLEAN DEFAULT FALSE,
    contract_start DATE,
    contract_end DATE,
    market_value BIGINT,
    salary_annual BIGINT,
    loan_player BOOLEAN DEFAULT FALSE,
    youth_academy BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_team_squads_team ON public.team_squads(team_id);
CREATE INDEX idx_team_squads_season ON public.team_squads(season_id);
CREATE INDEX idx_team_squads_player ON public.team_squads(player_id);
CREATE INDEX idx_team_squads_position ON public.team_squads(position_id);
CREATE INDEX idx_team_squads_jersey ON public.team_squads(jersey_number);
```

```python
# ADICIONAR EM: bdfut/core/sportmonks_client.py

def get_team_squad_by_season(self, team_id: int, season_id: int, include: Optional[str] = None) -> List[Dict]:
    """Busca elenco de um time em uma temporada"""
    endpoint = f'/team-squads/teams/{team_id}/seasons/{season_id}'
    params = {}
    if include:
        params['include'] = include
    response = self._make_request(endpoint, params, 'squad')
    return response.get('data', []) if response else []

def get_team_squad_current(self, team_id: int, include: Optional[str] = None) -> List[Dict]:
    """Busca elenco atual de um time"""
    endpoint = f'/team-squads/teams/{team_id}'
    params = {}
    if include:
        params['include'] = include
    response = self._make_request(endpoint, params, 'squad')
    return response.get('data', []) if response else []

def get_all_team_squads(self, include: Optional[str] = None) -> List[Dict]:
    """Busca todos os elencos"""
    endpoint = '/team-squads'
    params = {}
    if include:
        params['include'] = include
    return self.get_paginated_data(endpoint, params)

# ADICIONAR EM: bdfut/core/supabase_client.py

def upsert_team_squads(self, squads: List[Dict]) -> bool:
    """Insere ou atualiza elencos de times"""
    try:
        data = []
        for squad in squads:
            squad_data = {
                'sportmonks_id': squad.get('id'),
                'team_id': squad.get('team_id'),
                'season_id': squad.get('season_id'),
                'player_id': squad.get('player_id'),
                'jersey_number': squad.get('jersey_number'),
                'position_id': squad.get('position_id'),
                'position_name': squad.get('position', {}).get('name') if squad.get('position') else None,
                'captain': squad.get('captain', False),
                'vice_captain': squad.get('vice_captain', False),
                'contract_start': squad.get('contract_start'),
                'contract_end': squad.get('contract_end'),
                'market_value': squad.get('market_value'),
                'salary_annual': squad.get('salary_annual'),
                'loan_player': squad.get('loan_player', False),
                'youth_academy': squad.get('youth_academy', False)
            }
            
            squad_data = {k: v for k, v in squad_data.items() if v is not None}
            data.append(squad_data)
        
        if data:
            self.client.table('team_squads').upsert(data, on_conflict='sportmonks_id').execute()
            logger.info(f"Upserted {len(data)} team squads")
            return True
        return True
    except Exception as e:
        logger.error(f"Erro ao fazer upsert de team squads: {str(e)}")
        return False
```

**🔧 Day 4-5: Script de Coleta Squads**
```python
# CRIAR ARQUIVO: collect_team_squads_complete.py
#!/usr/bin/env python3
"""
Coleta completa de team squads
=============================
"""

def main():
    print('👥 COLETA COMPLETA DE TEAM SQUADS')
    
    sportmonks = SportmonksClient(enable_cache=True, use_redis=True)
    supabase = SupabaseClient(use_service_role=True)
    
    # Buscar teams e temporadas atuais
    teams = supabase.client.table('teams').select('sportmonks_id, name').execute()
    current_seasons = supabase.client.table('seasons').select(
        'sportmonks_id, league_id'
    ).eq('is_current', True).execute()
    
    total_squad_records = 0
    
    for team in teams.data:
        team_id = team['sportmonks_id']
        team_name = team.get('name', 'Unknown')
        
        print(f"👥 {team_name} (ID: {team_id})")
        
        # Elenco atual
        try:
            current_squad = sportmonks.get_team_squad_current(
                team_id, include='player,position,team'
            )
            
            if current_squad:
                success = supabase.upsert_team_squads(current_squad)
                if success:
                    total_squad_records += len(current_squad)
                    print(f"  ✅ {len(current_squad)} jogadores no elenco atual")
            
            # Elencos por temporada (últimas 3)
            for season in current_seasons.data[:3]:
                season_id = season['sportmonks_id']
                
                season_squad = sportmonks.get_team_squad_by_season(
                    team_id, season_id, include='player,position'
                )
                
                if season_squad:
                    success = supabase.upsert_team_squads(season_squad)
                    if success:
                        total_squad_records += len(season_squad)
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Erro: {str(e)[:40]}")
    
    print(f"✅ Total squad records: {total_squad_records:,}")
    return total_squad_records >= 20000

if __name__ == "__main__":
    main()
```

#### **Sprint 4.2.2 - Squad Evolution (Semana 15)**

**🔧 Day 1-3: Análises de Evolução**
```python
# CRIAR ARQUIVO: analyze_squad_evolution.py
#!/usr/bin/env python3
"""
Análises de evolução de elencos
==============================
"""

def main():
    print('📊 ANÁLISES DE EVOLUÇÃO DE ELENCOS')
    
    supabase = SupabaseClient(use_service_role=True)
    
    # Análise 1: Mudanças de elenco por temporada
    squad_changes = supabase.client.rpc('exec_sql', {
        'sql': '''
        WITH squad_comparison AS (
            SELECT 
                team_id,
                season_id,
                COUNT(*) as squad_size,
                AVG(market_value) as avg_market_value,
                SUM(market_value) as total_squad_value
            FROM team_squads 
            GROUP BY team_id, season_id
        )
        SELECT 
            team_id,
            season_id,
            squad_size,
            avg_market_value,
            total_squad_value,
            LAG(total_squad_value) OVER (PARTITION BY team_id ORDER BY season_id) as previous_value,
            (total_squad_value - LAG(total_squad_value) OVER (PARTITION BY team_id ORDER BY season_id)) as value_change
        FROM squad_comparison
        ORDER BY team_id, season_id
        '''
    }).execute()
    
    print(f"📈 Análise de evolução de valores de elenco concluída")
    
    # Análise 2: Players mais valiosos por posição
    top_players_by_position = supabase.client.rpc('exec_sql', {
        'sql': '''
        SELECT 
            position_name,
            player_id,
            MAX(market_value) as max_value,
            COUNT(*) as seasons_tracked
        FROM team_squads 
        WHERE market_value IS NOT NULL
        GROUP BY position_name, player_id
        ORDER BY position_name, max_value DESC
        '''
    }).execute()
    
    print(f"🏆 Rankings por posição calculados")
    
    return True

if __name__ == "__main__":
    main()
```

**📊 Meta:** 50.000+ registros de squad

### **🏆 EPIC 4.3: COMPETITION STRUCTURES**
**Duração:** 1 semana | **Prioridade:** 🟢 MÉDIA | **ROI:** MÉDIO

#### **Sprint 4.3.1 - Rounds & Stages (Semana 16)**
- [ ] **Day 1-3:** Estruturas de campeonatos
- [ ] **Day 4-5:** Análises por fase/rodada

**📊 Meta:** 15.000+ estruturas

---

## 📊 CRONOGRAMA DETALHADO

| **Semana** | **Epic** | **Foco Principal** | **Entregáveis** | **Registros** |
|------------|----------|-------------------|-----------------|---------------|
| **1-2** | Transfers | 💰 Dados de mercado | Tabela + 50k transfers | 50.000 |
| **3** | Market Values | 💎 Valuations | 25k valuations | 25.000 |
| **4-5** | Expected Goals | 🎯 Métricas xG | 200k métricas xG | 200.000 |
| **6-7** | Advanced Stats | 📈 Estatísticas | 100k stats avançadas | 100.000 |
| **8-9** | Predictions | 🔮 Predições | 100k predictions | 100.000 |
| **10-11** | Odds | 📊 Betting data | 500k odds | 500.000 |
| **12-13** | Rankings | 🥅 Top scorers | 10k rankings | 10.000 |
| **14-15** | Team Squads | 👥 Elencos | 50k squad data | 50.000 |
| **16** | Structures | 🏆 Rounds/Stages | 15k structures | 15.000 |

**📈 CRESCIMENTO PROGRESSIVO:**
- **Semana 2:** 155.841 registros (+47%)
- **Semana 5:** 355.841 registros (+236%)
- **Semana 9:** 555.841 registros (+425%)
- **Semana 16:** 1.055.841 registros (+897%)

---

## 🎯 MILESTONES CRÍTICOS

### **🔴 MILESTONE 1 (Semana 3): DADOS DE MERCADO**
- ✅ 75.000+ registros de mercado (transfers + values)
- ✅ Análises financeiras habilitadas
- ✅ Intelligence de transferências funcionando

### **🔴 MILESTONE 2 (Semana 7): MÉTRICAS AVANÇADAS**
- ✅ 300.000+ métricas xG e estatísticas avançadas
- ✅ Análises de performance moderna
- ✅ Capacidades de scouting avançado

### **🔴 MILESTONE 3 (Semana 11): INTELIGÊNCIA PREDITIVA**
- ✅ 600.000+ dados preditivos e odds
- ✅ Sistema de validação de modelos
- ✅ Capacidades de betting intelligence

### **🔴 MILESTONE 4 (Semana 16): PLATAFORMA COMPLETA**
- ✅ 1.000.000+ registros totais
- ✅ Sistema de inteligência esportiva completo
- ✅ Liderança de mercado estabelecida

---

## 💰 INVESTIMENTO E ROI

### **📊 ESTIMATIVA DE ESFORÇO**
- **Total:** 16 semanas (4 meses)
- **Esforço por sprint:** 3-5 dias
- **Complexidade:** Média-Alta
- **Recursos:** 1 desenvolvedor ETL especialista

### **💎 ROI ESPERADO**
- **Valor dos dados:** 10x superior
- **Capacidades analíticas:** 5x expandidas
- **Diferenciação competitiva:** Única no mercado
- **Potencial de monetização:** Múltiplas oportunidades

---

## 🚀 PRÓXIMA AÇÃO IMEDIATA

### **🔴 RECOMENDAÇÃO CRÍTICA:**
**Implementar EPIC 1.1 - Sistema de Transfers** como primeira expansão

**Justificativas:**
1. **Valor imediato** para análises de mercado
2. **Dados únicos** e diferenciados
3. **ROI comprovado** em sistemas similares
4. **Complexidade gerenciável** (2 semanas)
5. **Base sólida** para próximas expansões

### **📋 PRIMEIRA SPRINT (Próximos 5 dias):**
1. **Day 1:** Criar tabela `transfers` 
2. **Day 2:** Implementar `get_transfers()` 
3. **Day 3:** Implementar `upsert_transfers()`
4. **Day 4:** Script de coleta massiva
5. **Day 5:** Validação e integração

---

## 🎯 CONCLUSÃO

**Este roadmap transformará nosso sistema ETL enterprise em uma das plataformas de dados esportivos mais avançadas e completas do mundo.**

### **🌟 IMPACTO FINAL ESPERADO:**
- **1.000.000+ registros** de dados únicos
- **Inteligência esportiva** de classe mundial
- **Capacidades preditivas** avançadas
- **Liderança de mercado** estabelecida

**🚀 Pronto para iniciar a transformação com TRANSFERS?**
