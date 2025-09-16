#!/usr/bin/env python3
"""
Teste direto: Coletar rounds via HTTP direto e salvar no Supabase
TASK-ETL-024: Implementar Sistema de Rounds

Objetivo: Validar coleta e upsert de rounds
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

def test_rounds_direct():
    """Teste direto com HTTP"""
    print("🔍 TESTE DIRETO: Coletando rounds via HTTP...")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        
        # Fazer requisição direta
        url = f'{base_url}/rounds'
        params = {'api_token': api_key, 'per_page': 10}
        
        print("📡 Fazendo requisição HTTP...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rounds = data.get('data', [])
            print(f"✅ Coletados {len(rounds)} rounds")
            
            if rounds:
                print("📋 Exemplo de round:")
                round_item = rounds[0]
                print(f"  ID: {round_item.get('id')}")
                print(f"  Name: {round_item.get('name')}")
                print(f"  Season ID: {round_item.get('season_id')}")
                print(f"  League ID: {round_item.get('league_id')}")
                print(f"  Finished: {round_item.get('finished')}")
                print(f"  Starting: {round_item.get('starting_at')}")
                print(f"  Ending: {round_item.get('ending_at')}")
                
                # Salvar no Supabase
                print("💾 Salvando no Supabase...")
                supabase = SupabaseClient()
                success = supabase.upsert_rounds(rounds)
                
                if success:
                    print("✅ Rounds salvos com sucesso!")
                    
                    # Verificar no banco
                    result = supabase.client.table('rounds').select('*').limit(10).execute()
                    print(f"🔍 Verificação: {len(result.data)} rounds no banco")
                    
                    if result.data:
                        db_round = result.data[0]
                        print(f"  Banco - ID: {db_round.get('id')}, Sportmonks ID: {db_round.get('sportmonks_id')}, Name: {db_round.get('name')}")
                    
                    return True
                else:
                    print("❌ Erro ao salvar rounds")
                    return False
            else:
                print("⚠️ Nenhum round encontrado")
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
    success = test_rounds_direct()
    if success:
        print("🎉 Teste direto concluído com sucesso!")
    else:
        print("💥 Teste direto falhou!")
