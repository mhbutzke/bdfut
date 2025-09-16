#!/usr/bin/env python3
"""
Task 2.2 - Fixtures Temporadas Atuais (Sem Duplicatas)
======================================================

Objetivo: Coletar fixtures das temporadas mais recentes (2016/2017) sem duplicatas
Task Master ID: 2.2
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

def collect_current_fixtures_no_duplicates():
    """Coletar fixtures das temporadas atuais sem duplicatas"""
    print("🚀 Task 2.2 - FIXTURES TEMPORADAS ATUAIS (SEM DUPLICATAS)...")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        supabase = SupabaseClient()
        
        print("📡 Buscando temporadas 2016/2017...")
        
        # Buscar temporadas 2016/2017 (primeiras 3 páginas)
        all_2016_seasons = []
        
        for page in range(1, 4):
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
                
                import time
                time.sleep(0.5)
            else:
                print(f"❌ Erro página {page}: {response.status_code}")
                break
        
        print(f"✅ Encontradas {len(all_2016_seasons)} temporadas 2016/2017")
        
        # Coletar fixtures (limitado para teste)
        all_fixtures = []
        seen_fixture_ids = set()
        
        for i, season in enumerate(all_2016_seasons[:3]):  # Primeiras 3 temporadas
            season_id = season['id']
            season_name = season['name']
            league_id = season.get('league_id')
            
            print(f"📡 Coletando fixtures {i+1}/3: temporada {season_id} (Liga {league_id})")
            
            try:
                fixtures_url = f'{base_url}/fixtures'
                fixtures_params = {
                    'api_token': api_key, 
                    'season_id': season_id,
                    'per_page': 50  # Reduzido para evitar duplicatas
                }
                
                fixtures_response = requests.get(fixtures_url, params=fixtures_params, timeout=15)
                
                if fixtures_response.status_code == 200:
                    fixtures_data = fixtures_response.json()
                    fixtures = fixtures_data.get('data', [])
                    
                    # Remover duplicatas baseado no sportmonks_id
                    unique_fixtures = []
                    for fixture in fixtures:
                        fixture_id = fixture.get('id')
                        if fixture_id and fixture_id not in seen_fixture_ids:
                            seen_fixture_ids.add(fixture_id)
                            unique_fixtures.append(fixture)
                    
                    if unique_fixtures:
                        all_fixtures.extend(unique_fixtures)
                        print(f"  ✅ {len(unique_fixtures)} fixtures únicas (total: {len(all_fixtures)})")
                    else:
                        print(f"  ⚠️ Nenhuma fixture única encontrada")
                else:
                    print(f"  ❌ Erro fixtures: {fixtures_response.status_code}")
                
                import time
                time.sleep(2)  # Pausa maior entre temporadas
                
            except Exception as e:
                print(f"  ❌ Erro temporada {season_id}: {e}")
                continue
        
        print(f"\\n📊 Total de fixtures únicas: {len(all_fixtures)}")
        
        if all_fixtures:
            # Mostrar estatísticas
            print("📋 Estatísticas:")
            leagues = {}
            for fixture in all_fixtures:
                league_id = fixture.get('league_id')
                if league_id:
                    leagues[league_id] = leagues.get(league_id, 0) + 1
            
            print(f"  - Ligas representadas: {len(leagues)}")
            for league_id, count in leagues.items():
                print(f"    Liga {league_id}: {count} fixtures")
            
            # Salvar no Supabase (em lotes menores)
            print("💾 Salvando fixtures no Supabase (em lotes)...")
            
            batch_size = 25
            saved_count = 0
            
            for i in range(0, len(all_fixtures), batch_size):
                batch = all_fixtures[i:i+batch_size]
                print(f"  Salvando lote {i//batch_size + 1}: {len(batch)} fixtures")
                
                try:
                    success = supabase.upsert_fixtures(batch)
                    if success:
                        saved_count += len(batch)
                        print(f"    ✅ Lote salvo ({saved_count}/{len(all_fixtures)})")
                    else:
                        print(f"    ❌ Erro no lote")
                except Exception as e:
                    print(f"    ❌ Erro no lote: {e}")
                
                import time
                time.sleep(1)
            
            print(f"\\n✅ Total salvo: {saved_count}/{len(all_fixtures)} fixtures")
            
            # Verificar no banco
            result = supabase.client.table('fixtures').select('*').execute()
            total_in_db = len(result.data)
            print(f"🔍 Total no banco: {total_in_db} fixtures")
            
            return saved_count > 0
        else:
            print("⚠️ Nenhuma fixture coletada")
            return False
            
    except Exception as e:
        print(f"❌ Erro na coleta: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = collect_current_fixtures_no_duplicates()
    if success:
        print("🎉 Task 2.2 concluída com sucesso!")
        print("📊 Fixtures das temporadas atuais disponíveis coletadas!")
    else:
        print("💥 Task 2.2 falhou!")
