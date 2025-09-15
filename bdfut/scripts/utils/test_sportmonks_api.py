#!/usr/bin/env python3
"""
Script para testar a API Sportmonks e diagnosticar problemas de sintaxe de filtros.
"""

import os
import sys
import requests
import json
from datetime import datetime

# Adicionar o diretório bdfut ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bdfut'))

from bdfut.config.config import Config

def test_api_endpoints():
    """Testa diferentes endpoints da API Sportmonks para identificar problemas"""
    
    print("=" * 80)
    print("🔍 TESTANDO API SPORTMONKS - DIAGNÓSTICO DE PROBLEMAS")
    print("=" * 80)
    
    # Validar configuração
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        print(f"✅ Configuração válida")
        print(f"📡 Base URL: {base_url}")
        print(f"🔑 API Key: {api_key[:10]}...")
    except Exception as e:
        print(f"❌ Erro de configuração: {e}")
        return
    
    # Testar diferentes sintaxes de filtros
    test_cases = [
        {
            "name": "Teste 1: Sem filtros",
            "url": f"{base_url}/fixtures",
            "params": {"api_token": api_key, "per_page": 5}
        },
        {
            "name": "Teste 2: Filtro season_id (sintaxe atual)",
            "url": f"{base_url}/fixtures",
            "params": {"api_token": api_key, "filters": "season_id:25583", "per_page": 5}
        },
        {
            "name": "Teste 3: Filtro season_id (nova sintaxe)",
            "url": f"{base_url}/fixtures",
            "params": {"api_token": api_key, "season_id": 25583, "per_page": 5}
        },
        {
            "name": "Teste 4: Filtro season_id (sintaxe alternativa)",
            "url": f"{base_url}/fixtures",
            "params": {"api_token": api_key, "filter[season_id]": 25583, "per_page": 5}
        },
        {
            "name": "Teste 5: Filtro season_id (sintaxe com where)",
            "url": f"{base_url}/fixtures",
            "params": {"api_token": api_key, "where": "season_id=25583", "per_page": 5}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['name']}")
        print(f"📡 URL: {test_case['url']}")
        print(f"📋 Params: {test_case['params']}")
        
        try:
            response = requests.get(test_case['url'], params=test_case['params'], timeout=30)
            
            print(f"📊 Status: {response.status_code}")
            print(f"📋 Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                fixtures_count = len(data.get('data', []))
                print(f"✅ Sucesso! {fixtures_count} fixtures retornadas")
                
                if fixtures_count > 0:
                    print("📋 Exemplo de fixture:")
                    fixture = data['data'][0]
                    for key, value in fixture.items():
                        if key != 'participants':  # Evitar print muito longo
                            print(f"  • {key}: {value}")
            else:
                print(f"❌ Erro {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📋 Detalhes do erro: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📋 Resposta: {response.text}")
                    
        except Exception as e:
            print(f"❌ Exceção: {str(e)}")
    
    # Testar endpoint de seasons para validar IDs
    print(f"\n🧪 Teste 6: Validar season_id 25583")
    try:
        season_url = f"{base_url}/seasons/25583"
        season_response = requests.get(season_url, params={"api_token": api_key}, timeout=30)
        
        print(f"📊 Status: {season_response.status_code}")
        if season_response.status_code == 200:
            season_data = season_response.json()
            print(f"✅ Season válida: {season_data.get('data', {}).get('name', 'N/A')}")
        else:
            print(f"❌ Season inválida: {season_response.text}")
    except Exception as e:
        print(f"❌ Erro ao testar season: {str(e)}")

if __name__ == "__main__":
    test_api_endpoints()
