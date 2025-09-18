#!/usr/bin/env python3
"""
Task 2.6 - Expansão Ligas Secundárias (Task Master)
==================================================

Objetivo: Expandir ligas secundárias para países com poucas ligas
Task Master ID: 2.6
Situação atual: 113 ligas, alguns países com apenas 1-2 ligas
Meta: Expandir para países importantes como Japão, México, Polônia, etc.
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

def expand_secondary_leagues():
    """Expandir ligas secundárias para países com poucas ligas"""
    print("🚀 Task 2.6 - EXPANSÃO LIGAS SECUNDÁRIAS...")
    print("📊 Situação atual: 113 ligas")
    print("🎯 Meta: Expandir países com apenas 1-2 ligas")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        supabase = SupabaseClient()
        
        # Países prioritários para expansão (com apenas 1 liga)
        priority_countries = [
            {"id": 143, "name": "Austria", "current_leagues": 1},
            {"id": 1004, "name": "Canada", "current_leagues": 1},
            {"id": 5618, "name": "China", "current_leagues": 1},
            {"id": 266, "name": "Croatia", "current_leagues": 1},
            {"id": 245, "name": "Czech Republic", "current_leagues": 1},
            {"id": 886, "name": "Egypt", "current_leagues": 1},
            {"id": 1233, "name": "Finland", "current_leagues": 1},
            {"id": 125, "name": "Greece", "current_leagues": 1},
            {"id": 153732, "name": "India", "current_leagues": 1},
            {"id": 488, "name": "Iran", "current_leagues": 1},
            {"id": 802, "name": "Israel", "current_leagues": 1},
            {"id": 23, "name": "Ivory Coast", "current_leagues": 1},
            {"id": 479, "name": "Japan", "current_leagues": 1},
            {"id": 458, "name": "Mexico", "current_leagues": 1},
            {"id": 1424, "name": "Morocco", "current_leagues": 1},
            {"id": 1578, "name": "Norway", "current_leagues": 1},
            {"id": 2, "name": "Poland", "current_leagues": 1},
            {"id": 20, "name": "Portugal", "current_leagues": 1}
        ]
        
        print(f"\\n🎯 Expandindo {len(priority_countries)} países prioritários...")
        
        leagues_collected = 0
        
        for i, country in enumerate(priority_countries[:5]):  # Testar com 5 países primeiro
            country_id = country["id"]
            country_name = country["name"]
            
            print(f"\\n📡 Processando país {i+1}/{min(len(priority_countries), 5)}: {country_name} (ID: {country_id})")
            
            try:
                # Buscar ligas do país na API
                leagues_url = f'{base_url}/leagues'
                leagues_params = {
                    'api_token': api_key,
                    'country_id': country_id,
                    'include': 'country'
                }
                
                leagues_response = requests.get(leagues_url, params=leagues_params, timeout=15)
                
                if leagues_response.status_code == 200:
                    leagues_data = leagues_response.json()
                    leagues = leagues_data.get('data', [])
                    
                    if leagues:
                        print(f"  ✅ {len(leagues)} ligas encontradas na API")
                        
                        # Processar ligas
                        processed_leagues = []
                        for league in leagues:
                            # Verificar se a liga já existe
                            existing_league = supabase.client.table('leagues').select('id').eq('sportmonks_id', league.get('id')).execute()
                            
                            if not existing_league.data:  # Liga não existe
                                processed_league = {
                                    'sportmonks_id': league.get('id'),
                                    'name': league.get('name'),
                                    'country': str(country_id),  # Manter como string para compatibilidade
                                    'logo_url': league.get('image_path'),
                                    'active': league.get('active', True)
                                }
                                processed_leagues.append(processed_league)
                        
                        # Salvar novas ligas
                        if processed_leagues:
                            try:
                                supabase.client.table('leagues').upsert(processed_leagues).execute()
                                leagues_collected += len(processed_leagues)
                                print(f"    💾 {len(processed_leagues)} novas ligas salvas")
                            except Exception as e:
                                print(f"    ❌ Erro ao salvar ligas: {e}")
                        else:
                            print(f"    ⚠️ Todas as ligas já existem no banco")
                    else:
                        print(f"  ⚠️ Nenhuma liga encontrada para {country_name}")
                else:
                    print(f"  ❌ Erro ao buscar ligas: {leagues_response.status_code}")
                
            except Exception as e:
                print(f"  ❌ Erro ao processar {country_name}: {e}")
            
            # Pausa entre países
            import time
            time.sleep(1)
        
        print(f"\\n📊 Resumo da expansão:")
        print(f"  - Novas ligas coletadas: {leagues_collected}")
        
        # Verificar nova cobertura
        print("\\n📊 Verificando nova cobertura...")
        
        total_leagues = supabase.client.table('leagues').select('id').execute()
        leagues_count_new = len(total_leagues.data)
        
        print(f"📈 Nova cobertura:")
        print(f"  - Total de ligas: {leagues_count_new}")
        print(f"  - Expansão: +{leagues_count_new - 113} ligas")
        
        return leagues_collected > 0
        
    except Exception as e:
        print(f"❌ Erro na expansão: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = expand_secondary_leagues()
    if success:
        print("🎉 Task 2.6 concluída com sucesso!")
        print("📊 Ligas secundárias expandidas!")
    else:
        print("💥 Task 2.6 falhou!")
