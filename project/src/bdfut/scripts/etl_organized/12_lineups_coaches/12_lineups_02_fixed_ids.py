#!/usr/bin/env python3
"""
Task 2.5 - Enriquecimento de Lineups (IDs Corrigidos)
====================================================

Versão que gera IDs locais para evitar overflow de integer
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

import requests
import logging
import hashlib
from datetime import datetime
from bdfut.core.supabase_client import SupabaseClient
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_local_id(sportmonks_id, player_id, team_id):
    """Gerar ID local baseado nos dados da API"""
    # Criar hash único baseado nos dados
    data = f"{sportmonks_id}_{player_id}_{team_id}"
    hash_obj = hashlib.md5(data.encode())
    # Converter para inteiro positivo
    return abs(int(hash_obj.hexdigest()[:8], 16))

def enrich_lineups_fixed():
    """Enriquecer fixtures com lineups (IDs corrigidos)"""
    print("🚀 Task 2.5 - ENRIQUECIMENTO DE LINEUPS (IDs CORRIGIDOS)...")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        supabase = SupabaseClient()
        
        # Buscar algumas fixtures para testar
        print("🔍 Buscando fixtures para enriquecer...")
        
        fixtures_result = supabase.client.table('fixtures').select('id,sportmonks_id').limit(10).execute()
        test_fixtures = fixtures_result.data
        
        print(f"📋 Testando com {len(test_fixtures)} fixtures")
        
        lineups_collected = 0
        
        for i, fixture in enumerate(test_fixtures):
            fixture_id = fixture['id']
            sportmonks_id = fixture['sportmonks_id']
            
            print(f"\\n📡 Processando fixture {i+1}/{len(test_fixtures)}: {sportmonks_id}")
            
            try:
                # Buscar lineups da API
                lineups_url = f'{base_url}/fixtures/{sportmonks_id}'
                lineups_params = {
                    'api_token': api_key,
                    'include': 'lineups'
                }
                
                lineups_response = requests.get(lineups_url, params=lineups_params, timeout=15)
                
                if lineups_response.status_code == 200:
                    lineups_data = lineups_response.json()
                    fixture_data = lineups_data.get('data', {})
                    lineups = fixture_data.get('lineups', [])
                    
                    if lineups:
                        print(f"  ✅ {len(lineups)} lineups encontrados")
                        
                        # Processar lineups com IDs corrigidos
                        processed_lineups = []
                        for lineup in lineups:
                            # Gerar ID local
                            local_id = generate_local_id(
                                sportmonks_id, 
                                lineup.get('player_id', 0), 
                                lineup.get('team_id', 0)
                            )
                            
                            processed_lineup = {
                                'id': local_id,
                                'fixture_id': fixture_id,
                                'team_id': lineup.get('team_id'),
                                'player_id': lineup.get('player_id'),
                                'player_name': lineup.get('player_name'),
                                'type': lineup.get('type_id'),  # Mapear type_id para type
                                'position_id': lineup.get('position_id'),
                                'position_name': lineup.get('formation_position'),
                                'jersey_number': lineup.get('jersey_number'),
                                'captain': False  # Default
                            }
                            processed_lineups.append(processed_lineup)
                        
                        # Salvar lineups
                        if processed_lineups:
                            try:
                                supabase.client.table('match_lineups').upsert(processed_lineups).execute()
                                lineups_collected += len(processed_lineups)
                                print(f"    💾 {len(processed_lineups)} lineups salvos")
                            except Exception as e:
                                print(f"    ❌ Erro ao salvar lineups: {e}")
                    else:
                        print(f"  ⚠️ Nenhum lineup encontrado")
                else:
                    print(f"  ❌ Erro lineups: {lineups_response.status_code}")
                
            except Exception as e:
                print(f"  ❌ Erro lineups: {e}")
            
            # Pausa entre fixtures
            import time
            time.sleep(1)
        
        print(f"\\n📊 Resumo da coleta:")
        print(f"  - Lineups coletados: {lineups_collected}")
        
        # Verificar nova cobertura
        print("\\n📊 Verificando nova cobertura...")
        
        lineups_count = supabase.client.table('match_lineups').select('fixture_id').execute()
        lineups_fixtures_new = len(set(row['fixture_id'] for row in lineups_count.data))
        
        total_fixtures = 67085
        lineups_coverage = round(lineups_fixtures_new * 100.0 / total_fixtures, 2)
        
        print(f"📈 Nova cobertura:")
        print(f"  - Lineups: {lineups_fixtures_new} fixtures ({lineups_coverage}%)")
        
        return lineups_collected > 0
        
    except Exception as e:
        print(f"❌ Erro na coleta: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = enrich_lineups_fixed()
    if success:
        print("🎉 Task 2.5 (Lineups) concluída com sucesso!")
        print("📊 Lineups enriquecidos!")
    else:
        print("💥 Task 2.5 (Lineups) falhou!")
