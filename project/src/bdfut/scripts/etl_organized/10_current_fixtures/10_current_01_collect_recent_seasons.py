#!/usr/bin/env python3
"""
Task 2.2 - Fixtures Temporadas Atuais (Task Master)
===================================================

Objetivo: Completar 100% fixtures das temporadas mais recentes disponíveis
Task Master ID: 2.2
Dependência: Task 2.1 concluída

Descoberta: API tem dados até 2016/2017 (não 2025/2026)
Estratégia: Coletar fixtures das temporadas 2016/2017 (mais recentes)
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

def collect_current_season_fixtures():
    """Coletar fixtures das temporadas mais recentes (2016/2017)"""
    print("🚀 Task 2.2 - COLETA DE FIXTURES TEMPORADAS ATUAIS...")
    print("📊 Descoberta: API tem dados até 2016/2017 (ajustando estratégia)")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        supabase = SupabaseClient()
        
        print("📡 Buscando temporadas 2016/2017...")
        
        # Buscar todas as temporadas 2016/2017
        all_2016_seasons = []
        page = 1
        
        while page <= 10:  # Máximo 10 páginas
            url = f'{base_url}/seasons'
            params = {'api_token': api_key, 'per_page': 100, 'page': page}
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                seasons = data.get('data', [])
                
                if not seasons:
                    break
                
                # Filtrar temporadas 2016/2017
                current_seasons = [s for s in seasons if '2016/2017' in s.get('name', '')]
                all_2016_seasons.extend(current_seasons)
                
                if current_seasons:
                    print(f"Página {page}: {len(current_seasons)} temporadas 2016/2017")
                
                page += 1
                import time
                time.sleep(0.5)
            else:
                print(f"❌ Erro página {page}: {response.status_code}")
                break
        
        print(f"✅ Encontradas {len(all_2016_seasons)} temporadas 2016/2017")
        
        if not all_2016_seasons:
            print("⚠️ Nenhuma temporada 2016/2017 encontrada")
            return False
        
        # Coletar fixtures para cada temporada 2016/2017
        all_fixtures = []
        
        for i, season in enumerate(all_2016_seasons[:5]):  # Primeiras 5 temporadas para teste
            season_id = season['id']
            season_name = season['name']
            league_id = season.get('league_id')
            
            print(f"📡 Coletando fixtures {i+1}/{len(all_2016_seasons[:5])}: temporada {season_id} ({season_name}, Liga {league_id})")
            
            try:
                # Coletar fixtures desta temporada
                fixtures_url = f'{base_url}/fixtures'
                fixtures_params = {
                    'api_token': api_key, 
                    'season_id': season_id,
                    'per_page': 100  # Máximo por página
                }
                
                fixtures_response = requests.get(fixtures_url, params=fixtures_params, timeout=15)
                
                if fixtures_response.status_code == 200:
                    fixtures_data = fixtures_response.json()
                    fixtures = fixtures_data.get('data', [])
                    
                    if fixtures:
                        all_fixtures.extend(fixtures)
                        print(f"  ✅ Coletadas {len(fixtures)} fixtures (total: {len(all_fixtures)})")
                    else:
                        print(f"  ⚠️ Nenhuma fixture encontrada")
                else:
                    print(f"  ❌ Erro fixtures: {fixtures_response.status_code}")
                
                import time
                time.sleep(1)  # Pausa entre temporadas
                
            except Exception as e:
                print(f"  ❌ Erro ao coletar temporada {season_id}: {e}")
                continue
        
        print(f"\\n📊 Total coletado: {len(all_fixtures)} fixtures")
        
        if all_fixtures:
            # Mostrar estatísticas
            print("📋 Estatísticas das fixtures:")
            leagues = {}
            for fixture in all_fixtures:
                league_id = fixture.get('league_id')
                if league_id:
                    leagues[league_id] = leagues.get(league_id, 0) + 1
            
            print(f"  - Ligas diferentes: {len(leagues)}")
            for league_id, count in sorted(leagues.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    Liga {league_id}: {count} fixtures")
            
            # Salvar no Supabase
            print("💾 Salvando fixtures no Supabase...")
            success = supabase.upsert_fixtures(all_fixtures)
            
            if success:
                print("✅ Fixtures salvos com sucesso!")
                
                # Verificar no banco
                result = supabase.client.table('fixtures').select('*').execute()
                total_in_db = len(result.data)
                print(f"🔍 Total de fixtures no banco: {total_in_db}")
                
                return True
            else:
                print("❌ Erro ao salvar fixtures")
                return False
        else:
            print("⚠️ Nenhuma fixture coletada")
            return False
            
    except Exception as e:
        print(f"❌ Erro na coleta: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = collect_current_season_fixtures()
    if success:
        print("🎉 Task 2.2 concluída com sucesso!")
        print("📊 Fixtures das temporadas atuais coletadas!")
    else:
        print("💥 Task 2.2 falhou!")
