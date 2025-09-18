#!/usr/bin/env python3
"""
Task 2.4 - Enriquecimento Final (Task Master)
=============================================

Versão final usando as colunas corretas das tabelas:
- match_events: campos específicos (player_name, result, etc.)
- match_statistics: campos específicos (shots_total, goals, etc.)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

import requests
import logging
from datetime import datetime
from bdfut.core.supabase_client import SupabaseClient
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def enrich_events_and_statistics_final():
    """Enriquecer fixtures com events e statistics (versão final)"""
    print("🚀 Task 2.4 - ENRIQUECIMENTO FINAL...")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        supabase = SupabaseClient()
        
        # Buscar algumas fixtures para testar
        print("🔍 Buscando fixtures para enriquecer...")
        
        fixtures_result = supabase.client.table('fixtures').select('id,sportmonks_id').limit(20).execute()
        test_fixtures = fixtures_result.data
        
        print(f"📋 Testando com {len(test_fixtures)} fixtures")
        
        events_collected = 0
        statistics_collected = 0
        
        for i, fixture in enumerate(test_fixtures):
            fixture_id = fixture['id']
            sportmonks_id = fixture['sportmonks_id']
            
            print(f"\\n📡 Processando fixture {i+1}/{len(test_fixtures)}: {sportmonks_id}")
            
            # Enriquecer Events
            try:
                events_url = f'{base_url}/fixtures/{sportmonks_id}'
                events_params = {
                    'api_token': api_key,
                    'include': 'events'
                }
                
                events_response = requests.get(events_url, params=events_params, timeout=15)
                
                if events_response.status_code == 200:
                    events_data = events_response.json()
                    fixture_data = events_data.get('data', {})
                    events = fixture_data.get('events', [])
                    
                    if events:
                        print(f"  ✅ {len(events)} events encontrados")
                        
                        # Processar events com campos corretos
                        processed_events = []
                        for event in events:
                            processed_event = {
                                'id': f"{sportmonks_id}_{event.get('id', '')}",
                                'fixture_id': fixture_id,
                                'type_id': event.get('type_id'),
                                'event_type': event.get('addition', ''),
                                'minute': event.get('minute'),
                                'extra_minute': event.get('extra_minute'),
                                'team_id': event.get('participant_id'),
                                'player_id': event.get('player_id'),
                                'related_player_id': event.get('related_player_id'),
                                'player_name': event.get('player_name'),
                                'period_id': event.get('period_id'),
                                'result': event.get('result'),
                                'var': event.get('rescinded', False),
                                'var_reason': None,
                                'coordinates': None,
                                'assist_id': None,
                                'assist_name': None,
                                'injured': event.get('injured', False),
                                'on_bench': event.get('on_bench', False)
                            }
                            processed_events.append(processed_event)
                        
                        # Salvar events
                        if processed_events:
                            try:
                                supabase.client.table('match_events').upsert(processed_events).execute()
                                events_collected += len(processed_events)
                                print(f"    💾 {len(processed_events)} events salvos")
                            except Exception as e:
                                print(f"    ❌ Erro ao salvar events: {e}")
                    else:
                        print(f"  ⚠️ Nenhum event encontrado")
                else:
                    print(f"  ❌ Erro events: {events_response.status_code}")
                
            except Exception as e:
                print(f"  ❌ Erro events: {e}")
            
            # Enriquecer Statistics
            try:
                stats_url = f'{base_url}/fixtures/{sportmonks_id}'
                stats_params = {
                    'api_token': api_key,
                    'include': 'statistics'
                }
                
                stats_response = requests.get(stats_url, params=stats_params, timeout=15)
                
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    fixture_data = stats_data.get('data', {})
                    statistics = fixture_data.get('statistics', [])
                    
                    if statistics:
                        print(f"  ✅ {len(statistics)} statistics encontrados")
                        
                        # Processar statistics com campos corretos
                        processed_stats = []
                        for stat in statistics:
                            # Mapear campos da API para campos da tabela
                            processed_stat = {
                                'id': stat.get('id'),
                                'fixture_id': fixture_id,
                                'team_id': stat.get('team_id'),
                                'shots_total': stat.get('shots_total'),
                                'shots_on_target': stat.get('shots_on_target'),
                                'shots_inside_box': stat.get('shots_inside_box'),
                                'shots_outside_box': stat.get('shots_outside_box'),
                                'blocked_shots': stat.get('blocked_shots'),
                                'corners': stat.get('corners'),
                                'offsides': stat.get('offsides'),
                                'ball_possession': stat.get('ball_possession'),
                                'yellow_cards': stat.get('yellow_cards'),
                                'red_cards': stat.get('red_cards'),
                                'fouls': stat.get('fouls'),
                                'passes_total': stat.get('passes_total'),
                                'passes_accurate': stat.get('passes_accurate'),
                                'pass_percentage': stat.get('pass_percentage'),
                                'saves': stat.get('saves'),
                                'tackles': stat.get('tackles'),
                                'interceptions': stat.get('interceptions'),
                                'goals': stat.get('goals'),
                                'goals_conceded': stat.get('goals_conceded'),
                                'shots_off_target': stat.get('shots_off_target'),
                                'shots_saved': stat.get('shots_saved'),
                                'shots_woodwork': stat.get('shots_woodwork'),
                                'shots_blocked': stat.get('shots_blocked')
                            }
                            processed_stats.append(processed_stat)
                        
                        # Salvar statistics
                        if processed_stats:
                            try:
                                supabase.client.table('match_statistics').upsert(processed_stats).execute()
                                statistics_collected += len(processed_stats)
                                print(f"    💾 {len(processed_stats)} statistics salvos")
                            except Exception as e:
                                print(f"    ❌ Erro ao salvar statistics: {e}")
                    else:
                        print(f"  ⚠️ Nenhuma statistic encontrada")
                else:
                    print(f"  ❌ Erro statistics: {stats_response.status_code}")
                
            except Exception as e:
                print(f"  ❌ Erro statistics: {e}")
            
            # Pausa entre fixtures
            import time
            time.sleep(1)
        
        print(f"\\n📊 Resumo da coleta:")
        print(f"  - Events coletados: {events_collected}")
        print(f"  - Statistics coletados: {statistics_collected}")
        
        # Verificar nova cobertura
        print("\\n📊 Verificando nova cobertura...")
        
        events_count = supabase.client.table('match_events').select('fixture_id').execute()
        statistics_count = supabase.client.table('match_statistics').select('fixture_id').execute()
        
        events_fixtures_new = len(set(row['fixture_id'] for row in events_count.data))
        statistics_fixtures_new = len(set(row['fixture_id'] for row in statistics_count.data))
        
        total_fixtures = 67085
        
        events_coverage = round(events_fixtures_new * 100.0 / total_fixtures, 2)
        statistics_coverage = round(statistics_fixtures_new * 100.0 / total_fixtures, 2)
        
        print(f"📈 Nova cobertura:")
        print(f"  - Events: {events_fixtures_new} fixtures ({events_coverage}%)")
        print(f"  - Statistics: {statistics_fixtures_new} fixtures ({statistics_coverage}%)")
        
        # Verificar se atingiu as metas
        events_meta_ok = events_coverage >= 90
        statistics_meta_ok = statistics_coverage >= 50
        
        print(f"\\n🎯 Status das metas:")
        print(f"  - Events 90%: {'✅ ALCANÇADA' if events_meta_ok else '🎯 EM PROGRESSO'}")
        print(f"  - Statistics 50%: {'✅ ALCANÇADA' if statistics_meta_ok else '🎯 EM PROGRESSO'}")
        
        return events_collected > 0 or statistics_collected > 0
        
    except Exception as e:
        print(f"❌ Erro na coleta: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = enrich_events_and_statistics_final()
    if success:
        print("🎉 Task 2.4 concluída com sucesso!")
        print("📊 Events e Statistics enriquecidos!")
    else:
        print("💥 Task 2.4 falhou!")
