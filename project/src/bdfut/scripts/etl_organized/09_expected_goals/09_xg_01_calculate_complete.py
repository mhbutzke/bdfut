#!/usr/bin/env python3
"""
Cálculo completo: Expected Goals próprio
TASK-ETL-026: Sistema Próprio de Expected Goals

Objetivo: Calcular xG para 50+ fixtures usando algoritmo próprio
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

import logging
from datetime import datetime
from bdfut.core.supabase_client import SupabaseClient
from bdfut.core.expected_goals_calculator import ExpectedGoalsCalculator, ExpectedGoalsResult

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_expected_goals_complete():
    """Calcular Expected Goals para fixtures completos"""
    print("🚀 CÁLCULO COMPLETO: Expected Goals próprio...")
    
    try:
        supabase = SupabaseClient()
        calculator = ExpectedGoalsCalculator()
        
        print("📡 Coletando dados de fixtures com estatísticas...")
        
        # Buscar fixtures com dados de estatísticas e eventos
        fixtures_query = """
        SELECT DISTINCT f.id as fixture_id, f.home_team_id, f.away_team_id
        FROM fixtures f
        INNER JOIN match_statistics ms ON f.id = ms.fixture_id
        INNER JOIN match_events me ON f.id = me.fixture_id
        WHERE f.id IS NOT NULL
        LIMIT 50
        """
        
        fixtures_result = supabase.client.rpc('execute_sql', {'query': fixtures_query}).execute()
        
        if not fixtures_result.data or not fixtures_result.data[0].get('result'):
            print("❌ Erro ao buscar fixtures")
            return False
        
        fixtures = fixtures_result.data[0]['result']
        print(f"✅ Encontrados {len(fixtures)} fixtures para processar")
        
        all_results = []
        processed_count = 0
        
        for fixture in fixtures:
            fixture_id = fixture['fixture_id']
            home_team_id = fixture['home_team_id']
            away_team_id = fixture['away_team_id']
            
            print(f"📊 Processando fixture {fixture_id} ({processed_count + 1}/{len(fixtures)})...")
            
            try:
                # Processar time da casa
                home_result = process_team_in_fixture(
                    supabase, calculator, fixture_id, home_team_id, is_home=True
                )
                if home_result:
                    all_results.append(home_result)
                
                # Processar time visitante
                away_result = process_team_in_fixture(
                    supabase, calculator, fixture_id, away_team_id, is_home=False
                )
                if away_result:
                    all_results.append(away_result)
                
                processed_count += 1
                
                if processed_count % 10 == 0:
                    print(f"✅ Processados {processed_count} fixtures...")
                
            except Exception as e:
                logger.error(f"Erro ao processar fixture {fixture_id}: {e}")
                continue
        
        print(f"📊 Total de resultados calculados: {len(all_results)}")
        
        if all_results:
            # Salvar no banco
            print("💾 Salvando resultados no Supabase...")
            success = save_expected_goals_results(supabase, all_results)
            
            if success:
                print("✅ Resultados salvos com sucesso!")
                
                # Mostrar estatísticas
                show_calculation_statistics(all_results)
                
                return True
            else:
                print("❌ Erro ao salvar resultados")
                return False
        else:
            print("⚠️ Nenhum resultado calculado")
            return False
            
    except Exception as e:
        print(f"❌ Erro no cálculo: {e}")
        import traceback
        traceback.print_exc()
        return False

def process_team_in_fixture(supabase: SupabaseClient, 
                           calculator: ExpectedGoalsCalculator,
                           fixture_id: int, 
                           team_id: int, 
                           is_home: bool) -> ExpectedGoalsResult:
    """Processa um time em uma fixture específica"""
    
    # Buscar estatísticas do time
    stats_query = f"""
    SELECT shots_total, shots_inside_box, shots_outside_box
    FROM match_statistics
    WHERE fixture_id = {fixture_id} AND team_id = {team_id}
    LIMIT 1
    """
    
    stats_result = supabase.client.rpc('execute_sql', {'query': stats_query}).execute()
    stats = stats_result.data[0]['result'][0] if stats_result.data and stats_result.data[0].get('result') else {}
    
    # Buscar eventos do time (gols)
    events_query = f"""
    SELECT event_type, player_id, assist_id
    FROM match_events
    WHERE fixture_id = {fixture_id} AND team_id = {team_id}
    """
    
    events_result = supabase.client.rpc('execute_sql', {'query': events_query}).execute()
    events = events_result.data[0]['result'] if events_result.data and events_result.data[0].get('result') else []
    
    # Separar eventos por tipo
    goals = [e for e in events if e['event_type'] in ['goal', 'own_goal', 'penalty_goal']]
    penalties = [e for e in events if e['event_type'] in ['penalty_goal', 'penalty_missed']]
    
    # Calcular xG
    result = calculator.calculate_team_xg(
        fixture_id=fixture_id,
        team_id=team_id,
        shots_total=stats.get('shots_total', 0) or 0,
        shots_inside_box=stats.get('shots_inside_box', 0) or 0,
        shots_outside_box=stats.get('shots_outside_box', 0) or 0,
        goals=goals,
        penalties=penalties,
        is_home=is_home
    )
    
    return result

def save_expected_goals_results(supabase: SupabaseClient, results: list) -> bool:
    """Salva resultados no banco de dados"""
    
    try:
        data = []
        calculator = ExpectedGoalsCalculator()
        
        for result in results:
            # Calcular métricas de validação
            metrics = calculator.validate_calculation(result)
            
            data.append({
                'fixture_id': result.fixture_id,
                'team_id': result.team_id,
                'player_id': result.player_id,
                'expected_goals': result.expected_goals,
                'expected_assists': result.expected_assists,
                'expected_points': result.expected_points,
                'actual_goals': result.actual_goals,
                'actual_assists': result.actual_assists,
                'shots_total': result.shots_total,
                'shots_inside_box': result.shots_inside_box,
                'shots_outside_box': result.shots_outside_box,
                'penalties_taken': result.penalties_taken,
                'big_chances': result.big_chances,
                'performance_index': metrics.get('performance_index', 0),
                'goal_efficiency': metrics.get('goal_efficiency', 0),
                'assist_efficiency': metrics.get('assist_efficiency', 0),
                'calculation_method': result.calculation_method,
                'calculation_date': datetime.now().isoformat()
            })
        
        # Usar método do SupabaseClient
        return supabase.upsert_expected_stats(data)
        
    except Exception as e:
        logger.error(f"Erro ao salvar resultados: {e}")
        return False

def show_calculation_statistics(results: list):
    """Mostra estatísticas dos cálculos"""
    
    if not results:
        return
    
    total_xg = sum(r.expected_goals for r in results)
    total_actual = sum(r.actual_goals for r in results)
    total_shots = sum(r.shots_total for r in results)
    
    avg_xg = total_xg / len(results)
    avg_actual = total_actual / len(results)
    
    print("\n📊 ESTATÍSTICAS DOS CÁLCULOS:")
    print("=" * 50)
    print(f"Total de cálculos: {len(results)}")
    print(f"Expected Goals total: {total_xg:.2f}")
    print(f"Goals reais total: {total_actual}")
    print(f"Shots total: {total_shots}")
    print(f"Média xG por time: {avg_xg:.2f}")
    print(f"Média goals reais por time: {avg_actual:.2f}")
    
    # Accuracy geral
    if total_xg > 0:
        accuracy = max(0, 100 - (abs(total_actual - total_xg) / max(total_actual, total_xg) * 100))
        print(f"Accuracy geral: {accuracy:.1f}%")
    
    # Distribuição de xG
    xg_ranges = {'0-0.5': 0, '0.5-1.0': 0, '1.0-2.0': 0, '2.0+': 0}
    for result in results:
        xg = result.expected_goals
        if xg < 0.5:
            xg_ranges['0-0.5'] += 1
        elif xg < 1.0:
            xg_ranges['0.5-1.0'] += 1
        elif xg < 2.0:
            xg_ranges['1.0-2.0'] += 1
        else:
            xg_ranges['2.0+'] += 1
    
    print("\n📈 DISTRIBUIÇÃO DE xG:")
    for range_name, count in xg_ranges.items():
        percentage = (count / len(results)) * 100
        print(f"  {range_name}: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    success = calculate_expected_goals_complete()
    if success:
        print("🎉 Cálculo de Expected Goals concluído com sucesso!")
        print("📊 TASK-ETL-026 - Sistema Próprio de Expected Goals implementado!")
    else:
        print("💥 Cálculo de Expected Goals falhou!")
