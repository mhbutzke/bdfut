#!/usr/bin/env python3
"""
Script para limpar seasons desnecessárias e manter apenas as principais
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client
from config.config import Config

def main():
    """Limpa seasons desnecessárias"""
    
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("🧹 LIMPANDO SEASONS DESNECESSÁRIAS")
    print("="*50)
    
    # Ligas principais que queremos manter
    ligas_principais = [648, 651, 654, 636, 1122, 1116, 2, 5, 8, 9, 564, 462, 301, 82, 743, 779]
    
    # Seasons que queremos manter (atual + 2 anteriores por liga)
    seasons_manter = {
        648: [25184, 23265, 21207],  # Brasileirão Série A: 2025, 2024, 2023
        651: [25185, 23291, 21210],  # Brasileirão Série B: 2025, 2024, 2023
        654: [25165, 23161, 21194],  # Copa do Brasil: 2025, 2024, 2023
        636: [24969, 23024, 20873],  # Primera División: 2025, 2024, 2023
        1122: [24957, 22969, 21019], # Copa Libertadores: 2025, 2024, 2023
        1116: [24955, 22971, 21020], # Copa Sudamericana: 2025, 2024, 2023
        2: [25580, 23619, 21638],    # Champions League: 2025/2026, 2024/2025, 2023/2024
        5: [25582, 23620, 22130],    # Europa League: 2025/2026, 2024/2025, 2023/2024
        8: [25583, 23614, 21646],    # Premier League: 2025/2026, 2024/2025, 2023/2024
        9: [25648, 23672, 21689],    # Championship: 2025/2026, 2024/2025, 2023/2024
        564: [25659, 23621, 21694],  # La Liga: 2025/2026, 2024/2025, 2023/2024
        462: [25745, 23793, 21825],  # Liga Portugal: 2025/2026, 2024/2025, 2023/2024
        301: [25651, 23643, 21779],  # Ligue 1: 2025/2026, 2024/2025, 2023/2024
        82: [25646, 23744, 21795],   # Bundesliga: 2025/2026, 2024/2025, 2023/2024
        743: [25539, 23586, 21623],  # Liga MX: 2025/2026, 2024/2025, 2023/2024
        779: [24962, 22974, 20901]   # MLS: 2025, 2024, 2023
    }
    
    # Criar lista de IDs para manter
    ids_manter = []
    for league_id, season_ids in seasons_manter.items():
        ids_manter.extend(season_ids)
    
    print(f"📋 Seasons para manter: {len(ids_manter)}")
    
    # Buscar todas as seasons
    todas_seasons = supabase.table('seasons').select('*').execute()
    
    seasons_para_deletar = []
    seasons_manter_lista = []
    
    for season in todas_seasons.data:
        sportmonks_id = season.get('sportmonks_id')
        league_id = season.get('league_id')
        name = season.get('name')
        
        if sportmonks_id in ids_manter:
            seasons_manter_lista.append(season)
        else:
            seasons_para_deletar.append(season)
    
    print(f"✅ Seasons para manter: {len(seasons_manter_lista)}")
    print(f"🗑️  Seasons para deletar: {len(seasons_para_deletar)}")
    
    if seasons_para_deletar:
        print("\n📋 Seasons que serão deletadas:")
        for season in seasons_para_deletar[:10]:  # Mostrar só as primeiras 10
            league_id = season.get('league_id')
            name = season.get('name')
            sportmonks_id = season.get('sportmonks_id')
            print(f"   • Liga {league_id}: {name} (ID: {sportmonks_id})")
        
        if len(seasons_para_deletar) > 10:
            print(f"   ... e mais {len(seasons_para_deletar) - 10} seasons")
        
        # Confirmar deleção
        resposta = input(f"\n❓ Deletar {len(seasons_para_deletar)} seasons desnecessárias? (s/N): ")
        
        if resposta.lower() == 's':
            print("\n🗑️  Deletando seasons...")
            
            # Deletar em lotes
            batch_size = 50
            deletadas = 0
            
            for i in range(0, len(seasons_para_deletar), batch_size):
                batch = seasons_para_deletar[i:i + batch_size]
                ids_batch = [s.get('sportmonks_id') for s in batch]
                
                try:
                    # Deletar por sportmonks_id
                    for sportmonks_id in ids_batch:
                        supabase.table('seasons').delete().eq('sportmonks_id', sportmonks_id).execute()
                        deletadas += 1
                    
                    print(f"   ✅ Lote {i//batch_size + 1}: {len(batch)} seasons deletadas")
                    
                except Exception as e:
                    print(f"   ❌ Erro no lote {i//batch_size + 1}: {e}")
            
            print(f"\n✅ Total de seasons deletadas: {deletadas}")
            
            # Verificar resultado final
            total_final = supabase.table('seasons').select('*', count='exact').execute()
            print(f"📊 Seasons restantes no banco: {total_final.count}")
            
        else:
            print("❌ Operação cancelada")
    else:
        print("✅ Nenhuma season desnecessária encontrada!")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main()
