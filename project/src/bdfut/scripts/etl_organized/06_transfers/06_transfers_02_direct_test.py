#!/usr/bin/env python3
"""
Teste direto: Coletar transfers via HTTP direto e salvar no Supabase
TASK-ETL-023: Implementar Sistema de Transfers

Objetivo: Validar coleta e upsert sem usar SportmonksClient
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

def test_transfers_direct():
    """Teste direto com HTTP"""
    print("🔍 TESTE DIRETO: Coletando transfers via HTTP...")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        
        # Fazer requisição direta
        url = f'{base_url}/transfers'
        params = {'api_token': api_key, 'per_page': 5}
        
        print("📡 Fazendo requisição HTTP...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            transfers = data.get('data', [])
            print(f"✅ Coletados {len(transfers)} transfers")
            
            if transfers:
                print("📋 Exemplo de transfer:")
                transfer = transfers[0]
                print(f"  ID: {transfer.get('id')}")
                print(f"  Player ID: {transfer.get('player_id')}")
                print(f"  From Team: {transfer.get('from_team_id')}")
                print(f"  To Team: {transfer.get('to_team_id')}")
                print(f"  Type: {transfer.get('type')}")
                print(f"  Date: {transfer.get('date')}")
                
                # Salvar no Supabase
                print("💾 Salvando no Supabase...")
                supabase = SupabaseClient()
                success = supabase.upsert_transfers(transfers)
                
                if success:
                    print("✅ Transfers salvos com sucesso!")
                    
                    # Verificar no banco
                    result = supabase.client.table('transfers').select('*').limit(5).execute()
                    print(f"🔍 Verificação: {len(result.data)} transfers no banco")
                    
                    if result.data:
                        db_transfer = result.data[0]
                        print(f"  Banco - ID: {db_transfer.get('id')}, Sportmonks ID: {db_transfer.get('sportmonks_id')}")
                    
                    return True
                else:
                    print("❌ Erro ao salvar transfers")
                    return False
            else:
                print("⚠️ Nenhum transfer encontrado")
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
    success = test_transfers_direct()
    if success:
        print("🎉 Teste direto concluído com sucesso!")
    else:
        print("💥 Teste direto falhou!")
