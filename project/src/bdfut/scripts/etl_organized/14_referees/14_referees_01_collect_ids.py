#!/usr/bin/env python3
"""
Task 2.8 - Coleta de Referees (IDs Principais)
==============================================

Objetivo: Coletar IDs dos referees principais (type=6) das fixtures
Task Master ID: 2.8
Situação atual: 0% de cobertura de referees
Meta: Coletar referee IDs para enriquecer fixtures
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

def collect_referee_ids():
    """Coletar IDs dos referees principais das fixtures"""
    print("🚀 Task 2.8 - COLETA DE REFEREES (IDs PRINCIPAIS)...")
    print("📊 Situação atual: 0% de cobertura de referees")
    print("🎯 Meta: Coletar referee IDs (type=6) para enriquecer fixtures")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        supabase = SupabaseClient()
        
        # Buscar fixtures sem referee para enriquecer
        print("\\n🔍 Identificando fixtures para enriquecer...")
        
        fixtures_result = supabase.client.table('fixtures').select('id,sportmonks_id').limit(50).execute()
        test_fixtures = fixtures_result.data
        
        print(f"📋 Testando com {len(test_fixtures)} fixtures")
        
        referee_ids_collected = 0
        fixtures_updated = 0
        
        # Processar fixtures em lotes de 10 (limite da API multi)
        batch_size = 10
        for i in range(0, len(test_fixtures), batch_size):
            batch = test_fixtures[i:i+batch_size]
            fixture_ids = [str(f['sportmonks_id']) for f in batch]
            fixture_ids_str = ','.join(fixture_ids)
            
            print(f"\\n📡 Processando lote {i//batch_size + 1}: {len(batch)} fixtures")
            
            try:
                # Buscar referees da API multi
                url = f'{base_url}/fixtures/multi/{fixture_ids_str}'
                params = {
                    'api_token': api_key,
                    'include': 'referees'
                }
                
                response = requests.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    fixtures_data = data.get('data', [])
                    
                    print(f"  ✅ {len(fixtures_data)} fixtures processadas da API")
                    
                    # Processar cada fixture
                    for fixture_data in fixtures_data:
                        sportmonks_id = fixture_data.get('id')
                        referees = fixture_data.get('referees', [])
                        
                        # Filtrar apenas referees principais (type=6)
                        main_referees = [r for r in referees if r.get('type_id') == 6]
                        
                        if main_referees:
                            # Pegar o primeiro referee principal
                            main_referee = main_referees[0]
                            referee_id = main_referee.get('id')
                            
                            if referee_id:
                                # Encontrar fixture correspondente no banco
                                db_fixture = next((f for f in batch if f['sportmonks_id'] == sportmonks_id), None)
                                
                                if db_fixture:
                                    # Atualizar fixture com referee ID
                                    try:
                                        supabase.client.table('fixtures').update({
                                            'referee': str(referee_id)  # Armazenar como string
                                        }).eq('id', db_fixture['id']).execute()
                                        
                                        referee_ids_collected += 1
                                        fixtures_updated += 1
                                        print(f"    💾 Fixture {sportmonks_id}: referee ID {referee_id}")
                                    except Exception as e:
                                        print(f"    ❌ Erro ao atualizar fixture {sportmonks_id}: {e}")
                        else:
                            print(f"    ⚠️ Fixture {sportmonks_id}: nenhum referee principal encontrado")
                else:
                    print(f"  ❌ Erro na API: {response.status_code}")
                
            except Exception as e:
                print(f"  ❌ Erro no lote: {e}")
            
            # Pausa entre lotes
            import time
            time.sleep(1)
        
        print(f"\\n📊 Resumo da coleta:")
        print(f"  - Referee IDs coletados: {referee_ids_collected}")
        print(f"  - Fixtures atualizadas: {fixtures_updated}")
        
        # Verificar nova cobertura
        print("\\n📊 Verificando nova cobertura...")
        
        coverage_result = supabase.client.table('fixtures').select('id').is_('referee', 'null').execute()
        fixtures_without_referee = len(coverage_result.data)
        
        total_fixtures = 67085
        fixtures_with_referee = total_fixtures - fixtures_without_referee
        referee_coverage = round(fixtures_with_referee * 100.0 / total_fixtures, 2)
        
        print(f"📈 Nova cobertura:")
        print(f"  - Fixtures com referee: {fixtures_with_referee} ({referee_coverage}%)")
        print(f"  - Fixtures sem referee: {fixtures_without_referee}")
        
        return referee_ids_collected > 0
        
    except Exception as e:
        print(f"❌ Erro na coleta: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = collect_referee_ids()
    if success:
        print("🎉 Task 2.8 (Referees IDs) concluída com sucesso!")
        print("📊 Referee IDs coletados!")
    else:
        print("💥 Task 2.8 (Referees IDs) falhou!")
