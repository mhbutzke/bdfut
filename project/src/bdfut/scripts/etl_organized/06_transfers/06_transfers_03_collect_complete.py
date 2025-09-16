#!/usr/bin/env python3
"""
Coleta completa: 25+ transfers
TASK-ETL-023: Implementar Sistema de Transfers

Objetivo: Coletar e salvar pelo menos 25 transfers da API Sportmonks
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

def collect_transfers_complete():
    """Coletar 25+ transfers completos"""
    print("🚀 COLETA COMPLETA: Coletando 25+ transfers...")
    
    try:
        Config.validate()
        api_key = Config.SPORTMONKS_API_KEY
        base_url = Config.SPORTMONKS_BASE_URL
        supabase = SupabaseClient()
        
        all_transfers = []
        page = 1
        target_count = 25
        
        while len(all_transfers) < target_count and page <= 5:  # Máximo 5 páginas
            print(f"📡 Coletando página {page}...")
            
            url = f'{base_url}/transfers'
            params = {
                'api_token': api_key, 
                'per_page': 25,  # 25 por página
                'page': page
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                transfers = data.get('data', [])
                
                if not transfers:
                    print("⚠️ Nenhum transfer encontrado nesta página")
                    break
                
                all_transfers.extend(transfers)
                print(f"✅ Coletados {len(transfers)} transfers (total: {len(all_transfers)})")
                
                # Se já temos o suficiente, parar
                if len(all_transfers) >= target_count:
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
        all_transfers = all_transfers[:target_count]
        
        print(f"📊 Total coletado: {len(all_transfers)} transfers")
        
        if all_transfers:
            # Mostrar estatísticas
            print("📋 Estatísticas dos transfers:")
            types = {}
            for transfer in all_transfers:
                t_type = transfer.get('type') or 'Unknown'
                types[t_type] = types.get(t_type, 0) + 1
            
            for t_type, count in types.items():
                print(f"  - {t_type}: {count}")
            
            print("💾 Salvando no Supabase...")
            success = supabase.upsert_transfers(all_transfers)
            
            if success:
                print("✅ Transfers salvos com sucesso!")
                
                # Verificar no banco
                result = supabase.client.table('transfers').select('*').execute()
                total_in_db = len(result.data)
                print(f"🔍 Total no banco: {total_in_db} transfers")
                
                # Mostrar alguns exemplos
                if result.data:
                    print("📋 Exemplos no banco:")
                    for i, transfer in enumerate(result.data[:3]):
                        print(f"  {i+1}. ID: {transfer.get('sportmonks_id')}, "
                              f"Player: {transfer.get('player_id')}, "
                              f"Date: {transfer.get('transfer_date')}")
                
                return True
            else:
                print("❌ Erro ao salvar transfers")
                return False
        else:
            print("⚠️ Nenhum transfer coletado")
            return False
            
    except Exception as e:
        print(f"❌ Erro na coleta: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = collect_transfers_complete()
    if success:
        print("🎉 Coleta completa concluída com sucesso!")
        print("📊 TASK-ETL-023 - Sistema de Transfers implementado!")
    else:
        print("💥 Coleta completa falhou!")
