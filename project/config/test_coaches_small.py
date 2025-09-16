#!/usr/bin/env python3
"""
Teste pequeno de coaches - validação antes da coleta massiva
===========================================================
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bdfut'))

from bdfut.core.supabase_client import SupabaseClient
from bdfut.core.sportmonks_client import SportmonksClient

def main():
    print('👨‍💼 TESTE PEQUENO DE COACHES')
    print('=' * 40)
    
    supabase = SupabaseClient()
    sportmonks = SportmonksClient(enable_cache=True, use_redis=True)
    
    try:
        # Teste 1: Verificar estrutura da tabela coaches
        print(f"\n🔍 TESTE 1: ESTRUTURA DA TABELA")
        try:
            sample = supabase.client.table('coaches').select('*').limit(1).execute()
            if sample.data:
                coach = sample.data[0]
                print(f"✅ Campos disponíveis: {list(coach.keys())}")
            else:
                print(f"⚠️ Tabela vazia")
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
        
        # Teste 2: Buscar coaches de 1 team
        print(f"\n🔍 TESTE 2: COACHES DE 1 TEAM")
        try:
            # Buscar um team para teste
            team_result = supabase.client.table('teams').select('sportmonks_id, name').limit(1).execute()
            if team_result.data:
                team = team_result.data[0]
                team_id = team['sportmonks_id']
                team_name = team['name']
                
                print(f"🏟️ Testando team: {team_name} (ID: {team_id})")
                
                coaches = sportmonks.get_coaches_by_team(team_id)
                print(f"👨‍💼 Coaches encontrados: {len(coaches) if coaches else 0}")
                
                if coaches:
                    coach = coaches[0]
                    print(f"📊 Exemplo: {coach.get('coach_id', '?')} - Campos: {list(coach.keys())[:5]}")
            else:
                print(f"❌ Nenhum team encontrado")
                return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
        
        # Teste 3: Buscar dados de 1 coach específico
        print(f"\n🔍 TESTE 3: DADOS DE 1 COACH")
        try:
            if coaches and coaches[0].get('coach_id'):
                coach_id = coaches[0]['coach_id']
                print(f"🔄 Buscando coach ID: {coach_id}")
                
                coach_details = sportmonks.get_coach_by_id(coach_id)
                if coach_details:
                    print(f"✅ Coach encontrado: {coach_details.get('name', 'Unknown')}")
                    print(f"📊 Campos: {list(coach_details.keys())[:8]}")
                else:
                    print(f"⚠️ Coach não encontrado")
            else:
                print(f"⚠️ Nenhum coach_id para testar")
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # Teste 4: Tentar salvar 1 coach
        print(f"\n🔍 TESTE 4: SALVAR 1 COACH")
        try:
            if 'coach_details' in locals() and coach_details and coach_details.get('name'):
                print(f"💾 Testando salvamento de: {coach_details.get('name', 'Unknown')}")
                
                success = supabase.upsert_coaches([coach_details])
                if success:
                    print(f"✅ Coach salvo com sucesso!")
                else:
                    print(f"❌ Erro ao salvar coach")
            else:
                print(f"⚠️ Nenhum coach válido para testar salvamento")
        except Exception as e:
            print(f"❌ Erro no salvamento: {e}")
            return False
        
        print(f"\n✅ TODOS OS TESTES PASSARAM!")
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'='*40}")
    if success:
        print("✅ SISTEMA PRONTO PARA COLETA MASSIVA!")
    else:
        print("❌ Corrigir problemas antes de prosseguir")
