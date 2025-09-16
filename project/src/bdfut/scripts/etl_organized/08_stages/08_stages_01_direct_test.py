#!/usr/bin/env python3
"""
Teste direto: Coletar stages via HTTP direto e salvar no Supabase
TASK-ETL-025: Implementar Sistema de Stages Expandido

Objetivo: Validar coleta e upsert de stages
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

def test_stages_direct():
    """Teste direto com HTTP"""
    print("🔍 TESTE DIRETO: Coletando stages via HTTP...")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        
        # Fazer requisição direta
        url = f'{base_url}/stages'
        params = {'api_token': api_key, 'per_page': 10}
        
        print("📡 Fazendo requisição HTTP...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stages = data.get('data', [])
            print(f"✅ Coletados {len(stages)} stages")
            
            if stages:
                print("📋 Exemplo de stage:")
                stage = stages[0]
                print(f"  ID: {stage.get('id')}")
                print(f"  Name: {stage.get('name')}")
                print(f"  Season ID: {stage.get('season_id')}")
                print(f"  League ID: {stage.get('league_id')}")
                print(f"  Type ID: {stage.get('type_id')}")
                print(f"  Finished: {stage.get('finished')}")
                print(f"  Sort Order: {stage.get('sort_order')}")
                print(f"  Starting: {stage.get('starting_at')}")
                print(f"  Ending: {stage.get('ending_at')}")
                
                # Salvar no Supabase
                print("💾 Salvando no Supabase...")
                supabase = SupabaseClient()
                success = supabase.upsert_stages(stages)
                
                if success:
                    print("✅ Stages salvos com sucesso!")
                    
                    # Verificar no banco
                    result = supabase.client.table('stages').select('*').limit(10).execute()
                    print(f"🔍 Verificação: {len(result.data)} stages no banco")
                    
                    if result.data:
                        db_stage = result.data[0]
                        print(f"  Banco - ID: {db_stage.get('id')}, Sportmonks ID: {db_stage.get('sportmonks_id')}, Name: {db_stage.get('name')}")
                    
                    return True
                else:
                    print("❌ Erro ao salvar stages")
                    return False
            else:
                print("⚠️ Nenhum stage encontrado")
                return False
        else:
            print(f"❌ Erro na API: {response.status_code} - {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_stages_direct()
    if success:
        print("🎉 Teste direto concluído com sucesso!")
    else:
        print("💥 Teste direto falhou!")
