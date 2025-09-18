#!/usr/bin/env python3
"""
Task 2.4 - Teste Simples de Enriquecimento
==========================================

Teste simples para entender a estrutura da API e corrigir problemas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

import requests
import json
from bdfut.config.config import Config

def test_api_structure():
    """Testar estrutura da API para events e statistics"""
    print("🔍 Testando estrutura da API...")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        
        # Testar uma fixture específica
        test_fixture_id = 463  # Fixture conhecida
        
        print(f"📡 Testando fixture {test_fixture_id}...")
        
        # Teste 1: Fixture básica
        url = f'{base_url}/fixtures/{test_fixture_id}'
        params = {'api_token': api_key}
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Fixture básica OK")
            print(f"  - ID: {data.get('data', {}).get('id')}")
            print(f"  - Status: {data.get('data', {}).get('state_name')}")
        else:
            print(f"❌ Erro fixture básica: {response.status_code}")
            return
        
        # Teste 2: Fixture com events
        print("\\n📡 Testando events...")
        events_url = f'{base_url}/fixtures/{test_fixture_id}'
        events_params = {
            'api_token': api_key,
            'include': 'events'
        }
        
        events_response = requests.get(events_url, params=events_params, timeout=15)
        
        if events_response.status_code == 200:
            events_data = events_response.json()
            print("✅ Events OK")
            
            # Verificar estrutura
            fixture_data = events_data.get('data', {})
            events = fixture_data.get('events', {})
            
            if isinstance(events, dict):
                events_list = events.get('data', [])
                print(f"  - Events encontrados: {len(events_list)}")
                
                if events_list:
                    event = events_list[0]
                    print(f"  - Exemplo event: {event}")
            else:
                print(f"  - Events structure: {type(events)}")
                print(f"  - Events content: {events}")
        else:
            print(f"❌ Erro events: {events_response.status_code}")
        
        # Teste 3: Fixture com statistics
        print("\\n📡 Testando statistics...")
        stats_url = f'{base_url}/fixtures/{test_fixture_id}'
        stats_params = {
            'api_token': api_key,
            'include': 'statistics'
        }
        
        stats_response = requests.get(stats_url, params=stats_params, timeout=15)
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print("✅ Statistics OK")
            
            # Verificar estrutura
            fixture_data = stats_data.get('data', {})
            statistics = fixture_data.get('statistics', {})
            
            if isinstance(statistics, dict):
                stats_list = statistics.get('data', [])
                print(f"  - Statistics encontrados: {len(stats_list)}")
                
                if stats_list:
                    stat = stats_list[0]
                    print(f"  - Exemplo stat: {stat}")
            else:
                print(f"  - Statistics structure: {type(statistics)}")
                print(f"  - Statistics content: {statistics}")
        else:
            print(f"❌ Erro statistics: {stats_response.status_code}")
        
        # Teste 4: Fixture com ambos
        print("\\n📡 Testando events + statistics...")
        both_url = f'{base_url}/fixtures/{test_fixture_id}'
        both_params = {
            'api_token': api_key,
            'include': 'events,statistics'
        }
        
        both_response = requests.get(both_url, params=both_params, timeout=15)
        
        if both_response.status_code == 200:
            both_data = both_response.json()
            print("✅ Events + Statistics OK")
            
            fixture_data = both_data.get('data', {})
            print(f"  - Keys disponíveis: {list(fixture_data.keys())}")
        else:
            print(f"❌ Erro events + statistics: {both_response.status_code}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_structure()
