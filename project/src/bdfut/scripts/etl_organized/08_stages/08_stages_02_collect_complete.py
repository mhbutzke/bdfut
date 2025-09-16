#!/usr/bin/env python3
"""
Coleta completa: 25+ stages
TASK-ETL-025: Implementar Sistema de Stages Expandido

Objetivo: Coletar e salvar pelo menos 25 stages da API Sportmonks
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

def collect_stages_complete():
    """Coletar 25+ stages completos"""
    print("🚀 COLETA COMPLETA: Coletando 25+ stages...")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        supabase = SupabaseClient()
        
        all_stages = []
        page = 1
        target_count = 25
        
        while len(all_stages) < target_count and page <= 3:  # Máximo 3 páginas
            print(f"📡 Coletando página {page}...")
            
            url = f'{base_url}/stages'
            params = {
                'api_token': api_key, 
                'per_page': 25,  # 25 por página
                'page': page
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                stages = data.get('data', [])
                
                if not stages:
                    print("⚠️ Nenhum stage encontrado nesta página")
                    break
                
                all_stages.extend(stages)
                print(f"✅ Coletados {len(stages)} stages (total: {len(all_stages)})")
                
                # Se já temos o suficiente, parar
                if len(all_stages) >= target_count:
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
        all_stages = all_stages[:target_count]
        
        print(f"📊 Total coletado: {len(all_stages)} stages")
        
        if all_stages:
            # Mostrar estatísticas
            print("📋 Estatísticas dos stages:")
            leagues = {}
            seasons = {}
            types = {}
            finished_count = 0
            current_count = 0
            
            for stage in all_stages:
                league_id = stage.get('league_id')
                season_id = stage.get('season_id')
                type_id = stage.get('type_id')
                
                if league_id:
                    leagues[league_id] = leagues.get(league_id, 0) + 1
                if season_id:
                    seasons[season_id] = seasons.get(season_id, 0) + 1
                if type_id:
                    types[type_id] = types.get(type_id, 0) + 1
                if stage.get('finished'):
                    finished_count += 1
                if stage.get('is_current'):
                    current_count += 1
            
            print(f"  - Ligas diferentes: {len(leagues)}")
            print(f"  - Temporadas diferentes: {len(seasons)}")
            print(f"  - Tipos diferentes: {len(types)}")
            print(f"  - Stages finalizados: {finished_count}")
            print(f"  - Stages atuais: {current_count}")
            
            # Mostrar alguns tipos mais comuns
            if types:
                sorted_types = sorted(types.items(), key=lambda x: x[1], reverse=True)
                print("  - Tipos mais comuns:")
                for type_id, count in sorted_types[:3]:
                    print(f"    Type {type_id}: {count} stages")
            
            print("💾 Salvando no Supabase...")
            success = supabase.upsert_stages(all_stages)
            
            if success:
                print("✅ Stages salvos com sucesso!")
                
                # Verificar no banco
                result = supabase.client.table('stages').select('*').execute()
                total_in_db = len(result.data)
                print(f"🔍 Total no banco: {total_in_db} stages")
                
                # Mostrar alguns exemplos
                if result.data:
                    print("📋 Exemplos no banco:")
                    for i, stage in enumerate(result.data[:3]):
                        print(f"  {i+1}. ID: {stage.get('sportmonks_id')}, "
                              f"Name: {stage.get('name')}, "
                              f"Season: {stage.get('season_id')}, "
                              f"Type: {stage.get('type_id')}, "
                              f"Finished: {stage.get('finished')}")
                
                return True
            else:
                print("❌ Erro ao salvar stages")
                return False
        else:
            print("⚠️ Nenhum stage coletado")
            return False
            
    except Exception as e:
        print(f"❌ Erro na coleta: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = collect_stages_complete()
    if success:
        print("🎉 Coleta completa concluída com sucesso!")
        print("📊 TASK-ETL-025 - Sistema de Stages Expandido implementado!")
    else:
        print("💥 Coleta completa falhou!")
