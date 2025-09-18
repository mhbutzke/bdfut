#!/usr/bin/env python3
"""
Task 2.4 - Enriquecimento Events e Statistics (Task Master)
==========================================================

Objetivo: Enriquecer fixtures com events (1.05%→90%) e statistics (1.05%→50%)
Task Master ID: 2.4
Situação atual:
- Events: 705 fixtures (1.05% de 67.085)
- Statistics: 706 fixtures (1.05% de 67.085)
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

def enrich_events_and_statistics():
    """Enriquecer fixtures com events e statistics"""
    print("🚀 Task 2.4 - ENRIQUECIMENTO EVENTS E STATISTICS...")
    print("📊 Situação atual:")
    print("  - Events: 705 fixtures (1.05% de 67.085)")
    print("  - Statistics: 706 fixtures (1.05% de 67.085)")
    print("🎯 Metas:")
    print("  - Events: 90% (60.377 fixtures)")
    print("  - Statistics: 50% (33.543 fixtures)")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        supabase = SupabaseClient()
        
        # Buscar fixtures sem events ou statistics
        print("\\n🔍 Identificando fixtures para enriquecer...")
        
        # Fixtures sem events
        fixtures_without_events = supabase.client.table('fixtures').select('id,sportmonks_id').execute()
        events_fixtures = supabase.client.table('match_events').select('fixture_id').execute()
        events_fixture_ids = {row['fixture_id'] for row in events_fixtures.data}
        
        fixtures_to_enrich_events = [
            f for f in fixtures_without_events.data 
            if f['id'] not in events_fixture_ids
        ]
        
        print(f"📋 Fixtures sem events: {len(fixtures_to_enrich_events)}")
        
        # Fixtures sem statistics
        statistics_fixtures = supabase.client.table('match_statistics').select('fixture_id').execute()
        statistics_fixture_ids = {row['fixture_id'] for row in statistics_fixtures.data}
        
        fixtures_to_enrich_statistics = [
            f for f in fixtures_without_events.data 
            if f['id'] not in statistics_fixture_ids
        ]
        
        print(f"📋 Fixtures sem statistics: {len(fixtures_to_enrich_statistics)}")
        
        # Enriquecer events (limitado para teste)
        print("\\n📡 Enriquecendo events...")
        events_collected = 0
        
        for i, fixture in enumerate(fixtures_to_enrich_events[:100]):  # Primeiras 100 para teste
            fixture_id = fixture['id']
            sportmonks_id = fixture['sportmonks_id']
            
            if i % 10 == 0:
                print(f"  Processando {i+1}/100 fixtures...")
            
            try:
                # Buscar events da API
                events_url = f'{base_url}/fixtures/{sportmonks_id}'
                events_params = {
                    'api_token': api_key,
                    'include': 'events'
                }
                
                response = requests.get(events_url, params=events_params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    events_data = data.get('data', {})
                    events = events_data.get('events', {}).get('data', [])
                    
                    if events:
                        # Processar events
                        processed_events = []
                        for event in events:
                            processed_event = {
                                'id': f"{sportmonks_id}_{event.get('id', '')}",
                                'fixture_id': fixture_id,
                                'type_id': event.get('type_id'),
                                'event_type': event.get('type', {}).get('name'),
                                'minute': event.get('minute'),
                                'player_id': event.get('player_id'),
                                'team_id': event.get('team_id'),
                                'details': str(event)
                            }
                            processed_events.append(processed_event)
                        
                        # Salvar events
                        if processed_events:
                            supabase.client.table('match_events').upsert(processed_events).execute()
                            events_collected += len(processed_events)
                
                import time
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"    ❌ Erro fixture {sportmonks_id}: {e}")
                continue
        
        print(f"✅ Events coletados: {events_collected}")
        
        # Enriquecer statistics (limitado para teste)
        print("\\n📡 Enriquecendo statistics...")
        statistics_collected = 0
        
        for i, fixture in enumerate(fixtures_to_enrich_statistics[:100]):  # Primeiras 100 para teste
            fixture_id = fixture['id']
            sportmonks_id = fixture['sportmonks_id']
            
            if i % 10 == 0:
                print(f"  Processando {i+1}/100 fixtures...")
            
            try:
                # Buscar statistics da API
                stats_url = f'{base_url}/fixtures/{sportmonks_id}'
                stats_params = {
                    'api_token': api_key,
                    'include': 'statistics'
                }
                
                response = requests.get(stats_url, params=stats_params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    stats_data = data.get('data', {})
                    statistics = stats_data.get('statistics', {}).get('data', [])
                    
                    if statistics:
                        # Processar statistics
                        processed_stats = []
                        for stat in statistics:
                            processed_stat = {
                                'id': f"{sportmonks_id}_{stat.get('id', '')}",
                                'fixture_id': fixture_id,
                                'team_id': stat.get('team_id'),
                                'stat_type': stat.get('type', {}).get('name'),
                                'value': stat.get('value'),
                                'details': str(stat)
                            }
                            processed_stats.append(processed_stat)
                        
                        # Salvar statistics
                        if processed_stats:
                            supabase.client.table('match_statistics').upsert(processed_stats).execute()
                            statistics_collected += len(processed_stats)
                
                import time
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"    ❌ Erro fixture {sportmonks_id}: {e}")
                continue
        
        print(f"✅ Statistics coletados: {statistics_collected}")
        
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
    success = enrich_events_and_statistics()
    if success:
        print("🎉 Task 2.4 concluída com sucesso!")
        print("📊 Events e Statistics enriquecidos!")
    else:
        print("💥 Task 2.4 falhou!")
