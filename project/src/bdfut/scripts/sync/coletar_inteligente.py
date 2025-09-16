#!/usr/bin/env python3
"""
Coleta Inteligente - Script otimizado para coletar múltiplas ligas
Foca em eficiência e evita duplicações
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
    level=logging.WARNING,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ligas organizadas por prioridade
LIGAS_PRIORIDADE_1 = {
    # Não coletadas ainda - ALTA PRIORIDADE
    2: 'Champions League',
    1122: 'Copa Libertadores', 
    564: 'LaLiga',
    82: 'Bundesliga',
    648: 'Brasileirão Série A',  # Reprocessar
    651: 'Brasileirão Série B',
    654: 'Copa do Brasil',
}

LIGAS_PRIORIDADE_2 = {
    # Segunda prioridade
    636: 'Primera División Argentina',
    1116: 'Copa Sudamericana',
    5: 'Europa League',
    301: 'Ligue 1',
    462: 'Liga Portugal',
}

LIGAS_PRIORIDADE_3 = {
    # Menor prioridade
    9: 'Championship',
    743: 'Liga MX',
    779: 'MLS',
}

def coletar_fixtures_basicas(sportmonks, supabase, league_id, league_name, max_seasons=3):
    """Coleta apenas fixtures básicas de forma rápida"""
    
    print(f"\n{'='*60}")
    print(f"⚡ {league_name} (ID: {league_id})")
    print(f"{'='*60}")
    
    fixtures_salvas = 0
    temporadas_processadas = 0
    
    try:
        # Buscar temporadas
        response = sportmonks._make_request(
            f'/leagues/{league_id}',
            {'include': 'seasons'}
        )
        
        seasons = response.get('data', {}).get('seasons', [])
        
        if not seasons:
            print("   ❌ Sem temporadas")
            return 0
        
        # Ordenar e limitar temporadas
        seasons = sorted(seasons, key=lambda x: x.get('starting_at', ''), reverse=True)[:max_seasons]
        
        print(f"   📅 {len(seasons)} temporadas encontradas")
        
        for season in seasons:
            season_id = season.get('id')
            season_name = season.get('name', 'N/A')
            
            print(f"      • {season_name}: ", end='')
            
            # Buscar fixtures
            try:
                response = sportmonks._make_request(
                    f'/seasons/{season_id}',
                    {'include': 'fixtures'}
                )
                
                fixtures = response.get('data', {}).get('fixtures', [])
                fixture_ids = [f.get('id') for f in fixtures if f.get('id')]
                
                if not fixture_ids:
                    print("0 fixtures")
                    continue
                
                print(f"{len(fixture_ids)} fixtures", end='')
                
                # Processar em lotes pequenos
                batch_size = 20
                includes = 'participants;scores;state'  # Mínimo necessário
                batch_saved = 0
                
                for i in range(0, len(fixture_ids), batch_size):
                    batch_ids = fixture_ids[i:i + batch_size]
                    batch_ids_str = ','.join(map(str, batch_ids))
                    
                    try:
                        # Buscar dados
                        response = sportmonks._make_request(
                            f'/fixtures/multi/{batch_ids_str}',
                            {'include': includes}
                        )
                        
                        fixtures_batch = response.get('data', [])
                        
                        # Salvar cada fixture
                        for fixture in fixtures_batch:
                            fixture_data = {
                                'sportmonks_id': fixture.get('id'),
                                'league_id': league_id,
                                'season_id': season_id,
                                'match_date': fixture.get('starting_at'),
                                'status': fixture.get('state', {}).get('state'),
                                'updated_at': datetime.utcnow().isoformat()
                            }
                            
                            # Times e placar
                            for p in fixture.get('participants', []):
                                loc = (p.get('meta') or {}).get('location')
                                if loc == 'home':
                                    fixture_data['home_team_id'] = p.get('id')
                                    fixture_data['home_team_name'] = p.get('name')
                                elif loc == 'away':
                                    fixture_data['away_team_id'] = p.get('id')
                                    fixture_data['away_team_name'] = p.get('name')
                            
                            for s in fixture.get('scores', []):
                                if s.get('description') in ('CURRENT', 'FT'):
                                    if s.get('participant') == 'home':
                                        fixture_data['home_score'] = (s.get('score') or {}).get('goals')
                                    elif s.get('participant') == 'away':
                                        fixture_data['away_score'] = (s.get('score') or {}).get('goals')
                            
                            try:
                                supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
                                batch_saved += 1
                            except:
                                pass  # Ignorar duplicatas
                        
                        # Rate limit
                        time.sleep(0.2)
                        
                    except Exception as e:
                        logger.debug(f"Erro no lote: {e}")
                        continue
                
                print(f" → {batch_saved} salvas")
                fixtures_salvas += batch_saved
                temporadas_processadas += 1
                
            except Exception as e:
                print(f"erro: {e}")
                continue
        
        print(f"   ✅ Total: {fixtures_salvas} fixtures salvas em {temporadas_processadas} temporadas")
        return fixtures_salvas
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return 0

def coletar_inteligente():
    """Coleta inteligente por prioridade"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 80)
    print("🚀 COLETA INTELIGENTE - MODO RÁPIDO")
    print("=" * 80)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    print(f"🎯 Estratégia: Coletar fixtures básicas primeiro, eventos depois")
    
    total_fixtures = 0
    ligas_processadas = 0
    tempo_inicio = datetime.now()
    
    # ============================================
    # FASE 1: LIGAS PRIORITÁRIAS
    # ============================================
    print("\n" + "="*80)
    print("📌 FASE 1: LIGAS PRIORITÁRIAS")
    print("="*80)
    
    for league_id, league_name in LIGAS_PRIORIDADE_1.items():
        fixtures = coletar_fixtures_basicas(sportmonks, supabase, league_id, league_name, max_seasons=2)
        total_fixtures += fixtures
        if fixtures > 0:
            ligas_processadas += 1
        time.sleep(1)
    
    # ============================================
    # FASE 2: LIGAS SECUNDÁRIAS (se houver tempo)
    # ============================================
    tempo_decorrido = (datetime.now() - tempo_inicio).seconds
    
    if tempo_decorrido < 600:  # Se menos de 10 minutos
        print("\n" + "="*80)
        print("📌 FASE 2: LIGAS SECUNDÁRIAS")
        print("="*80)
        
        for league_id, league_name in LIGAS_PRIORIDADE_2.items():
            fixtures = coletar_fixtures_basicas(sportmonks, supabase, league_id, league_name, max_seasons=2)
            total_fixtures += fixtures
            if fixtures > 0:
                ligas_processadas += 1
            time.sleep(1)
    
    # ============================================
    # RELATÓRIO FINAL
    # ============================================
    tempo_total = (datetime.now() - tempo_inicio).seconds
    
    print("\n" + "=" * 80)
    print("✅ COLETA CONCLUÍDA!")
    print("=" * 80)
    
    print(f"\n📊 RESULTADOS:")
    print(f"   • Ligas processadas: {ligas_processadas}")
    print(f"   • Fixtures coletadas: {total_fixtures:,}")
    print(f"   • Tempo total: {tempo_total//60}min {tempo_total%60}s")
    print(f"   • Média: {total_fixtures//(tempo_total+1)} fixtures/segundo")
    
    # Verificar totais
    try:
        fixtures = supabase.table('fixtures').select('*', count='exact').execute()
        
        # Contar ligas
        fixtures_data = supabase.table('fixtures').select('league_id').execute()
        unique_leagues = len(set(f['league_id'] for f in fixtures_data.data if f.get('league_id')))
        
        print(f"\n📊 BANCO DE DADOS ATUALIZADO:")
        print(f"   • Total de fixtures: {fixtures.count:,}")
        print(f"   • Total de ligas: {unique_leagues}")
    except:
        pass
    
    print("\n🎯 PRÓXIMO PASSO:")
    print("   → Execute: python3 enriquecer_todas_ligas.py")
    print("   Para adicionar eventos, estatísticas e escalações")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    coletar_inteligente()
