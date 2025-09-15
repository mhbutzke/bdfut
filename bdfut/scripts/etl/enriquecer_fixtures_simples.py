#!/usr/bin/env python3
"""
Script SIMPLIFICADO para enriquecer fixtures com eventos e estatísticas
Trabalha apenas com colunas existentes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
import logging
from src.sportmonks_client import SportmonksClient
from supabase import create_client
from config.config import Config
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def enriquecer_fixtures_simples():
    """Enriquece fixtures com eventos e estatísticas"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 70)
    print("🎯 ENRIQUECIMENTO DE FIXTURES - VERSÃO SIMPLES")
    print("=" * 70)
    
    # ============================================
    # 1. BUSCAR FIXTURES DO BRASILEIRÃO
    # ============================================
    print("\n📋 1. Buscando fixtures do Brasileirão...")
    
    try:
        # Buscar fixtures da liga 648 (Brasileirão)
        fixtures_db = supabase.table('fixtures').select('sportmonks_id').eq('league_id', 648).execute()
        fixture_ids = [f['sportmonks_id'] for f in fixtures_db.data if f.get('sportmonks_id')]
        
        print(f"   ✅ {len(fixture_ids)} fixtures do Brasileirão encontradas")
        
        if not fixture_ids:
            print("   ❌ Nenhuma fixture encontrada!")
            return
            
    except Exception as e:
        logger.error(f"Erro ao buscar fixtures: {e}")
        return
    
    # ============================================
    # 2. BUSCAR DADOS COMPLETOS
    # ============================================
    print("\n💾 2. Buscando dados completos...")
    
    # Includes essenciais
    includes = 'participants;scores;state;events;statistics;lineups;referees'
    
    batch_size = 20
    total_events = 0
    total_stats = 0
    total_lineups = 0
    
    for i in range(0, len(fixture_ids), batch_size):
        batch_ids = fixture_ids[i:i + batch_size]
        batch_ids_str = ','.join(map(str, batch_ids))
        
        print(f"\n   🔍 Lote {i//batch_size + 1}/{(len(fixture_ids)-1)//batch_size + 1}")
        
        try:
            # Buscar dados completos
            response = sportmonks._make_request(
                f'/fixtures/multi/{batch_ids_str}',
                {'include': includes}
            )
            
            fixtures_data = response.get('data', [])
            print(f"      ✅ {len(fixtures_data)} fixtures com dados")
            
            # Processar cada fixture
            for fixture in fixtures_data:
                fixture_id = fixture.get('id')
                
                # Contar dados
                events = fixture.get('events', [])
                stats = fixture.get('statistics', [])
                lineups = fixture.get('lineups', [])
                
                total_events += len(events)
                total_stats += len(stats)
                total_lineups += len(lineups)
                
                # Mostrar resumo do primeiro fixture
                if i == 0 and fixture == fixtures_data[0]:
                    print(f"\n      📊 Exemplo de dados:")
                    print(f"         • Fixture ID: {fixture_id}")
                    print(f"         • Eventos: {len(events)}")
                    print(f"         • Estatísticas: {len(stats)}")
                    print(f"         • Escalações: {len(lineups)}")
                    
                    if events:
                        print(f"         • Tipos de eventos: {set(e.get('type_id') for e in events[:5])}")
                    
                    if stats:
                        print(f"         • Tipos de stats: {set(s.get('type_id') for s in stats[:5])}")
            
            # Rate limit
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Erro no lote: {e}")
            continue
    
    # ============================================
    # 3. RELATÓRIO FINAL
    # ============================================
    print("\n" + "=" * 70)
    print("✅ DADOS COLETADOS COM SUCESSO!")
    print("=" * 70)
    
    print(f"\n📊 RESUMO DOS DADOS:")
    print(f"   • Total de eventos: {total_events:,}")
    print(f"   • Total de estatísticas: {total_stats:,}")
    print(f"   • Total de escalações: {total_lineups:,}")
    
    print(f"\n📌 PRÓXIMOS PASSOS:")
    print(f"   1. Criar as tabelas no Supabase:")
    print(f"      • match_events")
    print(f"      • match_statistics")
    print(f"      • match_lineups")
    print(f"   2. Executar script de salvamento dos dados")
    
    print("\n🎯 Dados prontos para serem salvos!")
    print("=" * 70)

if __name__ == "__main__":
    enriquecer_fixtures_simples()
