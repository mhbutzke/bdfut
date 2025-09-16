#!/usr/bin/env python3
"""
Teste pequeno: Coletar e salvar 5 transfers
TASK-ETL-023: Implementar Sistema de Transfers

Objetivo: Validar endpoint e sistema de upsert com amostra pequena
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_transfers_small():
    """Teste pequeno: 5 transfers"""
    print("🔍 TESTE PEQUENO: Coletando 5 transfers...")
    
    try:
        # Clientes sem cache para teste simples
        sportmonks = SportmonksClient(enable_cache=False)
        supabase = SupabaseClient()
        
        print("📡 Coletando transfers da API...")
        transfers = sportmonks.get_transfers(per_page=5)
        
        print(f"✅ Coletados {len(transfers)} transfers")
        
        if transfers:
            print("📋 Exemplo de transfer:")
            print(json.dumps(transfers[0], indent=2, ensure_ascii=False))
            
            print("💾 Salvando no Supabase...")
            success = supabase.upsert_transfers(transfers)
            
            if success:
                print("✅ Transfers salvos com sucesso!")
                
                # Verificar no banco
                result = supabase.client.table('transfers').select('*').limit(5).execute()
                print(f"🔍 Verificação: {len(result.data)} transfers no banco")
                
                return True
            else:
                print("❌ Erro ao salvar transfers")
                return False
        else:
            print("⚠️ Nenhum transfer encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_transfers_small()
    if success:
        print("🎉 Teste pequeno concluído com sucesso!")
    else:
        print("💥 Teste pequeno falhou!")