#!/usr/bin/env python3
"""
Coleta completa: 25+ rounds
TASK-ETL-024: Implementar Sistema de Rounds

Objetivo: Coletar e salvar pelo menos 25 rounds da API Sportmonks
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

import requests
import json
import logging
from datetime import datetime
from bdfut.core.supabase_client import SupabaseClient
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_rounds_complete():
    """Coletar 25+ rounds completos"""
    print("🚀 COLETA COMPLETA: Coletando 25+ rounds...")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        supabase = SupabaseClient()
        
        all_rounds = []
        page = 1
        target_count = 25
        
        while len(all_rounds) < target_count and page <= 3:  # Máximo 3 páginas
            print(f"📡 Coletando página {page}...")
            
            url = f'{base_url}/rounds'
            params = {
                'api_token': api_key, 
                'per_page': 25,  # 25 por página
                'page': page
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                rounds = data.get('data', [])
                
                if not rounds:
                    print("⚠️ Nenhum round encontrado nesta página")
                    break
                
                all_rounds.extend(rounds)
                print(f"✅ Coletados {len(rounds)} rounds (total: {len(all_rounds)})")
                
                # Se já temos o suficiente, parar
                if len(all_rounds) >= target_count:
                    break
                    
                page += 1
                
                # Pausa entre requisições
                import time
                time.sleep(1)
                
            else:
                print(f"❌ Erro na API página {page}: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                break
        
        # Limitar ao target
        all_rounds = all_rounds[:target_count]
        
        print(f"📊 Total coletado: {len(all_rounds)} rounds")
        
        if all_rounds:
            # Mostrar estatísticas
            print("📋 Estatísticas dos rounds:")
            leagues = {}
            seasons = {}
            finished_count = 0
            current_count = 0
            
            for round_item in all_rounds:
                league_id = round_item.get('league_id')
                season_id = round_item.get('season_id')
                
                if league_id:
                    leagues[league_id] = leagues.get(league_id, 0) + 1
                if season_id:
                    seasons[season_id] = seasons.get(season_id, 0) + 1
                if round_item.get('finished'):
                    finished_count += 1
                if round_item.get('is_current'):
                    current_count += 1
            
            print(f"  - Ligas diferentes: {len(leagues)}")
            print(f"  - Temporadas diferentes: {len(seasons)}")
            print(f"  - Rounds finalizados: {finished_count}")
            print(f"  - Rounds atuais: {current_count}")
            
            print("💾 Salvando no Supabase...")
            success = supabase.upsert_rounds(all_rounds)
            
            if success:
                print("✅ Rounds salvos com sucesso!")
                
                # Verificar no banco
                result = supabase.client.table('rounds').select('*').execute()
                total_in_db = len(result.data)
                print(f"🔍 Total no banco: {total_in_db} rounds")
                
                # Mostrar alguns exemplos
                if result.data:
                    print("📋 Exemplos no banco:")
                    for i, round_item in enumerate(result.data[:3]):
                        print(f"  {i+1}. ID: {round_item.get('sportmonks_id')}, "
                              f"Name: {round_item.get('name')}, "
                              f"Season: {round_item.get('season_id')}, "
                              f"Finished: {round_item.get('finished')}")
                
                return True
            else:
                print("❌ Erro ao salvar rounds")
                return False
        else:
            print("⚠️ Nenhum round coletado")
            return False
            
    except Exception as e:
        print(f"❌ Erro na coleta: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = collect_rounds_complete()
    if success:
        print("🎉 Coleta completa concluída com sucesso!")
        print("📊 TASK-ETL-024 - Sistema de Rounds implementado!")
    else:
        print("💥 Coleta completa falhou!")
