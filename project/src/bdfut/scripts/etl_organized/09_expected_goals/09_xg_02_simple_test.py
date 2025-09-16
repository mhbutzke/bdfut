#!/usr/bin/env python3
"""
Teste simples: Expected Goals próprio
TASK-ETL-026: Sistema Próprio de Expected Goals

Objetivo: Testar cálculo xG com dados simples
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

import logging
from datetime import datetime
from bdfut.core.supabase_client import SupabaseClient
from bdfut.core.expected_goals_calculator import ExpectedGoalsCalculator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_expected_goals_simple():
    """Teste simples de Expected Goals"""
    print("🔍 TESTE SIMPLES: Expected Goals próprio...")
    
    try:
        supabase = SupabaseClient()
        calculator = ExpectedGoalsCalculator()
        
        print("📡 Buscando fixtures com dados...")
        
        # Buscar algumas fixtures com estatísticas
        stats_result = supabase.client.table('match_statistics').select('fixture_id, team_id, shots_total, shots_inside_box, shots_outside_box').limit(20).execute()
        
        if not stats_result.data:
            print("❌ Nenhuma estatística encontrada")
            return False
        
        print(f"✅ Encontradas {len(stats_result.data)} estatísticas")
        
        all_results = []
        
        for i, stat in enumerate(stats_result.data[:10]):  # Processar apenas 10 para teste
            fixture_id = stat['fixture_id']
            team_id = stat['team_id']
            
            print(f"📊 Processando {i+1}/10: fixture {fixture_id}, team {team_id}")
            
            # Buscar eventos de gol para este time/fixture
            events_result = supabase.client.table('match_events').select('event_type, player_id, assist_id').eq('fixture_id', fixture_id).eq('team_id', team_id).execute()
            
            events = events_result.data or []
            goals = [e for e in events if e['event_type'] in ['goal', 'own_goal', 'penalty_goal']]
            penalties = [e for e in events if e['event_type'] in ['penalty_goal', 'penalty_missed']]
            
            # Calcular xG
            result = calculator.calculate_team_xg(
                fixture_id=fixture_id,
                team_id=team_id,
                shots_total=stat.get('shots_total', 0) or 0,
                shots_inside_box=stat.get('shots_inside_box', 0) or 0,
                shots_outside_box=stat.get('shots_outside_box', 0) or 0,
                goals=goals,
                penalties=penalties,
                is_home=True  # Assumir casa para simplificar
            )
            
            all_results.append(result)
            
            print(f"  xG: {result.expected_goals:.2f}, Goals: {result.actual_goals}, Shots: {result.shots_total}")
        
        print(f"\n📊 Total calculado: {len(all_results)} resultados")
        
        if all_results:
            # Salvar no banco
            print("💾 Salvando no Supabase...")
            
            # Converter para formato do SupabaseClient
            data = []
            for result in all_results:
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
                    'calculation_method': result.calculation_method
                })
            
            success = supabase.upsert_expected_stats(data)
            
            if success:
                print("✅ Resultados salvos com sucesso!")
                
                # Verificar no banco
                result = supabase.client.table('expected_stats').select('*').limit(10).execute()
                print(f"🔍 Verificação: {len(result.data)} registros no banco")
                
                if result.data:
                    print("📋 Exemplos no banco:")
                    for i, stat in enumerate(result.data[:3]):
                        print(f"  {i+1}. Fixture: {stat.get('fixture_id')}, xG: {stat.get('expected_goals')}, Goals: {stat.get('actual_goals')}")
                
                # Mostrar estatísticas
                show_simple_statistics(all_results)
                
                return True
            else:
                print("❌ Erro ao salvar resultados")
                return False
        else:
            print("⚠️ Nenhum resultado calculado")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_simple_statistics(results: list):
    """Mostra estatísticas simples"""
    
    if not results:
        return
    
    total_xg = sum(r.expected_goals for r in results)
    total_actual = sum(r.actual_goals for r in results)
    
    print("\n📊 ESTATÍSTICAS SIMPLES:")
    print("=" * 40)
    print(f"Cálculos realizados: {len(results)}")
    print(f"Expected Goals total: {total_xg:.2f}")
    print(f"Goals reais total: {total_actual}")
    print(f"Média xG: {total_xg/len(results):.2f}")
    print(f"Média goals reais: {total_actual/len(results):.2f}")
    
    # Accuracy simples
    if total_xg > 0:
        accuracy = max(0, 100 - (abs(total_actual - total_xg) / max(total_actual, total_xg, 1) * 100))
        print(f"Accuracy: {accuracy:.1f}%")

if __name__ == "__main__":
    success = test_expected_goals_simple()
    if success:
        print("🎉 Teste simples concluído com sucesso!")
        print("📊 TASK-ETL-026 - Sistema xG testado!")
    else:
        print("💥 Teste simples falhou!")
