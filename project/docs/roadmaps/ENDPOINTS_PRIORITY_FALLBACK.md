# 🔄 SISTEMA DE FALLBACK - ENDPOINTS POR PRIORIDADE

## ⚠️ IMPORTANTE: RESTRIÇÕES DE PLANO

**Mensagem de erro:** `"You do not have access to this endpoint"`  
**Ação:** Pular automaticamente para próximo endpoint da lista  
**Estratégia:** Sistema de fallback inteligente por prioridade  

---

## 🎯 LISTA DE PRIORIDADES POR CATEGORIA

### **💰 TRANSFERS & MARKET DATA**

#### **Prioridade 1: Transfers Direto**
```python
# Teste: sportmonks.get_transfers()
# URL: https://api.sportmonks.com/v3/football/transfers?api_token={{token}}
# Include: player,from_team,to_team,agent
```

#### **Prioridade 2: Transfers por Player**
```python
# Teste: sportmonks.get_transfers_by_player(player_id)
# URL: https://api.sportmonks.com/v3/football/transfers?player_id={id}&api_token={{token}}
# Include: from_team,to_team
```

#### **Prioridade 3: Market Values**
```python
# Teste: sportmonks.get_market_values()
# URL: https://api.sportmonks.com/v3/football/market-values?api_token={{token}}
# Include: player,team
```

#### **Fallback Final: Contract Data via Players**
```python
# Usar dados de contratos dos players existentes
# Expandir coleta de players com include='contract,market_value'
```

---

### **🎯 EXPECTED GOALS (xG)**

#### **Prioridade 1: Expected por Fixture**
```python
# Teste: sportmonks.get_expected_by_fixture(fixture_id)
# URL: https://api.sportmonks.com/v3/football/expected/fixtures/{id}?api_token={{token}}
# Include: team,player,fixture
```

#### **Prioridade 2: Expected por Player**
```python
# Teste: sportmonks.get_expected_by_player(player_id)
# URL: https://api.sportmonks.com/v3/football/expected/players/{id}?api_token={{token}}
# Include: fixture,team
```

#### **Prioridade 3: Expected Geral**
```python
# Teste: sportmonks.get_all_expected()
# URL: https://api.sportmonks.com/v3/football/expected?api_token={{token}}
# Include: fixture,team,player
```

#### **Fallback Final: Statistics Avançadas**
```python
# Usar statistics existentes e calcular xG aproximado
# Expandir match_statistics com campos de qualidade de chute
```

---

### **🔮 PREDICTIONS & PROBABILITIES**

#### **Prioridade 1: Predictions por Fixture**
```python
# Teste: sportmonks.get_predictions_by_fixture(fixture_id)
# URL: https://api.sportmonks.com/v3/football/predictions/fixtures/{id}?api_token={{token}}
# Include: fixture,probabilities
```

#### **Prioridade 2: Probabilities Direto**
```python
# Teste: sportmonks.get_probabilities_by_fixture(fixture_id)
# URL: https://api.sportmonks.com/v3/football/predictions/probabilities/fixtures/{id}?api_token={{token}}
# Include: fixture
```

#### **Prioridade 3: Value Bets**
```python
# Teste: sportmonks.get_value_bets_by_fixture(fixture_id)
# URL: https://api.sportmonks.com/v3/football/predictions/value-bets/fixtures/{id}?api_token={{token}}
# Include: fixture,bookmaker
```

#### **Fallback Final: Odds Analysis**
```python
# Usar odds existentes para calcular probabilidades implícitas
# Implementar sistema próprio de predições baseado em dados históricos
```

---

### **🥅 TOP SCORERS & RANKINGS**

#### **Prioridade 1: Top Scorers por Season**
```python
# Teste: sportmonks.get_top_scorers_by_season(season_id)
# URL: https://api.sportmonks.com/v3/football/topscorers/seasons/{id}?api_token={{token}}
# Include: player,team,season
```

#### **Prioridade 2: Top Scorers por League**
```python
# Teste: sportmonks.get_top_scorers_by_league(league_id)
# URL: https://api.sportmonks.com/v3/football/topscorers/leagues/{id}?api_token={{token}}
# Include: player,team
```

#### **Prioridade 3: Top Scorers Geral**
```python
# Teste: sportmonks.get_all_top_scorers()
# URL: https://api.sportmonks.com/v3/football/topscorers?api_token={{token}}
# Include: player,team,season
```

#### **Fallback Final: Calcular Rankings**
```python
# Usar match_events para calcular rankings próprios
# Agregar goals por player_id e season_id
# Criar rankings baseados em dados existentes
```

---

### **👥 TEAM SQUADS & COMPOSITION**

#### **Prioridade 1: Squad por Team e Season**
```python
# Teste: sportmonks.get_team_squad_by_season(team_id, season_id)
# URL: https://api.sportmonks.com/v3/football/team-squads/teams/{team_id}/seasons/{season_id}?api_token={{token}}
# Include: player,position,team
```

#### **Prioridade 2: Squad Atual**
```python
# Teste: sportmonks.get_team_squad_current(team_id)
# URL: https://api.sportmonks.com/v3/football/team-squads/teams/{id}?api_token={{token}}
# Include: player,position
```

#### **Prioridade 3: Todos os Squads**
```python
# Teste: sportmonks.get_all_team_squads()
# URL: https://api.sportmonks.com/v3/football/team-squads?api_token={{token}}
# Include: team,player,position
```

#### **Fallback Final: Lineups Analysis**
```python
# Usar match_lineups para inferir composição de elencos
# Agregar players por team_id e season_id
# Criar elencos baseados em escalações históricas
```

---

## 🔧 TEMPLATE DE TESTE UNIVERSAL

### **📋 Função de Teste Padrão**
```python
def test_and_collect_endpoint(sportmonks, supabase, endpoint_config):
    """Template universal para testar e coletar dados de qualquer endpoint"""
    
    print(f"🔍 TESTANDO: {endpoint_config['name']}")
    
    try:
        # Teste inicial
        test_result = endpoint_config['test_method']()
        
        if test_result is None:
            print(f"⚠️ {endpoint_config['name']}: Dados vazios")
            return False, 0
        
        print(f"✅ {endpoint_config['name']}: Acessível")
        
        # Coleta completa
        all_data = endpoint_config['collect_method']()
        
        if all_data:
            success = endpoint_config['upsert_method'](all_data)
            if success:
                count = len(all_data) if isinstance(all_data, list) else all_data
                print(f"💾 {count:,} registros salvos")
                return True, count
        
        return False, 0
        
    except Exception as e:
        error_msg = str(e).lower()
        if "you do not have access" in error_msg:
            print(f"❌ {endpoint_config['name']}: RESTRITO pelo plano")
            return False, 0
        else:
            print(f"⚠️ {endpoint_config['name']}: Erro técnico - {str(e)[:50]}")
            return False, 0
```

### **📋 Script Master de Coleta**
```python
# CRIAR ARQUIVO: collect_all_available_endpoints.py
#!/usr/bin/env python3
"""
Script master para coletar todos os endpoints disponíveis
=========================================================
"""

def main():
    print('🚀 COLETA MASTER - TODOS OS ENDPOINTS DISPONÍVEIS')
    print('=' * 70)
    
    sportmonks = SportmonksClient(enable_cache=True, use_redis=True)
    supabase = SupabaseClient(use_service_role=True)
    
    # CONFIGURAÇÃO DE TODOS OS ENDPOINTS
    all_endpoints = [
        # TRANSFERS
        {
            'name': 'transfers',
            'category': 'market_data',
            'priority': 1,
            'test_method': lambda: sportmonks.get_transfers(),
            'collect_method': lambda: sportmonks.get_transfers(include='player,from_team,to_team'),
            'upsert_method': lambda data: supabase.upsert_transfers(data),
            'fallback': 'player_based_transfers'
        },
        
        # EXPECTED GOALS
        {
            'name': 'expected_goals',
            'category': 'advanced_metrics',
            'priority': 2,
            'test_method': lambda: sportmonks.get_expected_by_fixture(19352879),  # Fixture teste
            'collect_method': lambda: collect_all_expected_goals(sportmonks),
            'upsert_method': lambda data: supabase.upsert_expected_stats(data),
            'fallback': 'statistics_based_xg'
        },
        
        # PREDICTIONS
        {
            'name': 'predictions',
            'category': 'predictive',
            'priority': 3,
            'test_method': lambda: sportmonks.get_predictions_by_fixture(19441526),  # Fixture futura
            'collect_method': lambda: collect_all_predictions(sportmonks),
            'upsert_method': lambda data: supabase.upsert_predictions(data),
            'fallback': 'odds_based_predictions'
        },
        
        # TOP SCORERS
        {
            'name': 'top_scorers',
            'category': 'rankings',
            'priority': 4,
            'test_method': lambda: sportmonks.get_top_scorers_by_season(19734),  # Season teste
            'collect_method': lambda: collect_all_top_scorers(sportmonks),
            'upsert_method': lambda data: supabase.upsert_top_scorers(data),
            'fallback': 'events_based_rankings'
        },
        
        # TEAM SQUADS
        {
            'name': 'team_squads',
            'category': 'composition',
            'priority': 5,
            'test_method': lambda: sportmonks.get_team_squad_current(19),  # Team teste
            'collect_method': lambda: collect_all_team_squads(sportmonks),
            'upsert_method': lambda data: supabase.upsert_team_squads(data),
            'fallback': 'lineups_based_squads'
        }
    ]
    
    successful_endpoints = []
    failed_endpoints = []
    total_records_collected = 0
    
    # Executar coleta para cada endpoint
    for endpoint in all_endpoints:
        print(f"\n{'='*50}")
        print(f"🎯 PROCESSANDO: {endpoint['name'].upper()}")
        print(f"📊 Categoria: {endpoint['category']}")
        print(f"🔢 Prioridade: {endpoint['priority']}")
        print("=" * 50)
        
        success, count = test_and_collect_endpoint(sportmonks, supabase, endpoint)
        
        if success:
            successful_endpoints.append({
                'name': endpoint['name'],
                'count': count,
                'category': endpoint['category']
            })
            total_records_collected += count
            print(f"✅ {endpoint['name']}: SUCESSO - {count:,} registros")
        else:
            failed_endpoints.append({
                'name': endpoint['name'],
                'reason': 'restricted_or_error',
                'fallback': endpoint['fallback']
            })
            print(f"❌ {endpoint['name']}: FALHOU - usando fallback")
            
            # Implementar fallback se necessário
            if endpoint['fallback']:
                print(f"🔄 Executando fallback: {endpoint['fallback']}")
                # Aqui implementaria o método de fallback
    
    # RELATÓRIO FINAL
    print(f"\n{'='*70}")
    print(f"📊 RELATÓRIO FINAL DA COLETA MASTER")
    print("=" * 70)
    
    print(f"✅ Endpoints bem-sucedidos: {len(successful_endpoints)}")
    for endpoint in successful_endpoints:
        print(f"  • {endpoint['name']}: {endpoint['count']:,} registros")
    
    print(f"\n❌ Endpoints restritos: {len(failed_endpoints)}")
    for endpoint in failed_endpoints:
        print(f"  • {endpoint['name']}: {endpoint['reason']}")
    
    print(f"\n📈 Total coletado: {total_records_collected:,} registros")
    print(f"🎯 Taxa de sucesso: {(len(successful_endpoints) / len(all_endpoints)) * 100:.1f}%")
    
    return {
        'successful': len(successful_endpoints),
        'failed': len(failed_endpoints),
        'total_records': total_records_collected,
        'success_rate': (len(successful_endpoints) / len(all_endpoints)) * 100
    }

# FUNÇÕES AUXILIARES DE COLETA
def collect_all_expected_goals(sportmonks):
    """Coleta todos os expected goals disponíveis"""
    # Implementar lógica específica
    pass

def collect_all_predictions(sportmonks):
    """Coleta todas as predictions disponíveis"""
    # Implementar lógica específica
    pass

def collect_all_top_scorers(sportmonks):
    """Coleta todos os top scorers disponíveis"""
    # Implementar lógica específica
    pass

def collect_all_team_squads(sportmonks):
    """Coleta todos os team squads disponíveis"""
    # Implementar lógica específica
    pass

if __name__ == "__main__":
    result = main()
    print(f"\n🎉 COLETA MASTER CONCLUÍDA!")
    print(f"📊 {result['successful']}/{result['successful'] + result['failed']} endpoints coletados")
    print(f"📈 {result['total_records']:,} registros adicionados")
```

---

## 🔄 ESTRATÉGIAS DE FALLBACK

### **💰 Se TRANSFERS não disponível:**
1. **Usar dados de lineups** para inferir mudanças de elenco
2. **Analisar match_events** para identificar novos jogadores
3. **Expandir coleta de players** com dados contratuais
4. **Criar sistema próprio** de tracking de mudanças

### **🎯 Se EXPECTED GOALS não disponível:**
1. **Expandir match_statistics** com métricas de qualidade
2. **Calcular xG aproximado** baseado em shots e posição
3. **Usar dados de events** para análises de performance
4. **Implementar modelo próprio** de Expected Goals

### **🔮 Se PREDICTIONS não disponível:**
1. **Usar standings** para calcular probabilidades
2. **Analisar histórico** de head-to-head
3. **Criar modelo próprio** baseado em form e statistics
4. **Usar odds** para inferir probabilidades

### **🥅 Se TOP SCORERS não disponível:**
1. **Agregar match_events** por player_id
2. **Calcular rankings** baseado em goals/assists
3. **Usar statistics** para métricas de performance
4. **Criar sistema próprio** de rankings

### **👥 Se TEAM SQUADS não disponível:**
1. **Usar match_lineups** para inferir elencos
2. **Analisar transfers** para composição
3. **Expandir dados de players** com team_history
4. **Criar elencos** baseado em escalações históricas

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### **🔍 Para cada endpoint:**
- [ ] **Teste inicial** com fixture/player/team conhecido
- [ ] **Verificar mensagem** de erro específica
- [ ] **Implementar fallback** se restrito
- [ ] **Documentar** resultado no log
- [ ] **Continuar** com próximo endpoint

### **📊 Métricas de sucesso:**
- [ ] **Taxa de sucesso** ≥ 60% dos endpoints
- [ ] **Registros coletados** ≥ 100.000 novos
- [ ] **Qualidade mantida** ≥ 90%
- [ ] **Performance** ≤ 3 seg/batch

---

## 🎯 RECOMENDAÇÃO FINAL

**SEMPRE IMPLEMENTAR SISTEMA DE FALLBACK** para garantir que o sistema continue evoluindo mesmo com restrições de plano.

**O objetivo é maximizar o valor coletado com os endpoints disponíveis e criar sistemas próprios para suprir lacunas quando necessário.**

🚀 **FOCO: TRANSFORMAR LIMITAÇÕES EM OPORTUNIDADES DE INOVAÇÃO!**
