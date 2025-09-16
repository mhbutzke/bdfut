#!/usr/bin/env python3
"""
Script OTIMIZADO - Brasileirão 2025
Usando a abordagem correta: Season -> Fixture IDs -> Multi fetch
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

def sync_brasileirao_otimizado():
    """Versão OTIMIZADA usando Season->Fixtures->Multi"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 70)
    print("🏆 BRASILEIRÃO 2025 - VERSÃO OTIMIZADA")
    print("=" * 70)
    
    LEAGUE_ID = 648
    
    # ============================================
    # 1. BUSCAR LIGA
    # ============================================
    print("\n📋 1. Buscando liga...")
    try:
        league = sportmonks.get_league_by_id(LEAGUE_ID, include='country;seasons')
        print(f"   ✅ {league.get('name')}")
        
        # Salvar liga
        league_data = {
            'sportmonks_id': league.get('id'),
            'name': league.get('name'),
            'country': league.get('country', {}).get('name') if league.get('country') else 'Brasil',
            'logo_url': league.get('image_path'),
            'active': league.get('active', True),
            'updated_at': datetime.utcnow().isoformat()
        }
        supabase.table('leagues').upsert(league_data, on_conflict='sportmonks_id').execute()
        
    except Exception as e:
        logger.error(f"Erro: {e}")
        return
    
    # ============================================
    # 2. IDENTIFICAR TEMPORADA 2025
    # ============================================
    print("\n📅 2. Identificando temporada 2025...")
    current_season = None
    
    if league.get('seasons'):
        for season in league['seasons']:
            if '2025' in str(season.get('name', '')):
                current_season = season
                break
    
    if not current_season:
        print("   ❌ Temporada 2025 não encontrada!")
        return
    
    SEASON_ID = current_season['id']
    print(f"   ✅ {current_season['name']} (ID: {SEASON_ID})")
    
    # ============================================
    # 3. BUSCAR TEMPORADA COM FIXTURES
    # ============================================
    print("\n🎮 3. Buscando IDs das partidas da temporada...")
    
    # CHAMADA CHAVE: Buscar temporada com fixtures incluídas
    season_response = sportmonks._make_request(
        f'/seasons/{SEASON_ID}',
        {'include': 'fixtures'}
    )
    
    season_data = season_response.get('data', {})
    fixtures_list = season_data.get('fixtures', [])
    
    print(f"   ✅ {len(fixtures_list)} partidas encontradas na temporada")
    
    if not fixtures_list:
        print("   ❌ Nenhuma partida encontrada")
        return
    
    # Extrair IDs das fixtures
    fixture_ids = [f['id'] for f in fixtures_list if f.get('id')]
    print(f"   📊 IDs extraídos: {len(fixture_ids)}")
    
    # ============================================
    # 4. BUSCAR FIXTURES EM LOTES
    # ============================================
    print("\n💾 4. Buscando detalhes completos das partidas...")
    
    # Dividir em lotes de 20 IDs (limite da API)
    batch_size = 20
    all_fixtures = []
    
    for i in range(0, len(fixture_ids), batch_size):
        batch_ids = fixture_ids[i:i + batch_size]
        batch_ids_str = ','.join(map(str, batch_ids))
        
        print(f"\n   🔍 Lote {i//batch_size + 1}/{(len(fixture_ids)-1)//batch_size + 1}")
        print(f"      IDs: {batch_ids_str[:50]}...")
        
        try:
            # BUSCAR MÚLTIPLAS FIXTURES COM TODOS OS DADOS
            response = sportmonks._make_request(
                f'/fixtures/multi/{batch_ids_str}',
                {
                    'include': 'participants;scores;state;venue;events;statistics;lineups;referees'
                }
            )
            
            fixtures_data = response.get('data', [])
            print(f"      ✅ {len(fixtures_data)} partidas recebidas")
            all_fixtures.extend(fixtures_data)
            
            # Rate limit
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Erro no lote: {e}")
            continue
    
    print(f"\n   📊 Total de partidas com detalhes: {len(all_fixtures)}")
    
    # ============================================
    # 5. PROCESSAR E SALVAR PARTIDAS
    # ============================================
    print("\n💾 5. Salvando partidas no banco...")
    
    fixtures_saved = 0
    events_count = 0
    stats_count = 0
    
    for fixture in all_fixtures:
        try:
            # Status
            state = fixture.get('state', {})
            status = state.get('state') or state.get('name') or 'NS'
            
            # Dados da partida
            fixture_data = {
                'sportmonks_id': fixture.get('id'),
                'league_id': fixture.get('league_id'),
                'season_id': fixture.get('season_id'),
                'match_date': fixture.get('starting_at'),
                'status': status,
                'venue': fixture.get('venue', {}).get('name') if isinstance(fixture.get('venue'), dict) else None,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Times
            for p in fixture.get('participants', []):
                loc = (p.get('meta') or {}).get('location')
                if loc == 'home':
                    fixture_data['home_team_id'] = p.get('id')
                elif loc == 'away':
                    fixture_data['away_team_id'] = p.get('id')
            
            # Placar
            home_score = away_score = None
            for s in fixture.get('scores', []):
                if s.get('description') in ('CURRENT', 'FT'):
                    if s.get('participant') == 'home':
                        home_score = (s.get('score') or {}).get('goals')
                    elif s.get('participant') == 'away':
                        away_score = (s.get('score') or {}).get('goals')
            
            fixture_data['home_score'] = home_score
            fixture_data['away_score'] = away_score
            
            # Árbitro
            for ref in fixture.get('referees', []):
                if (ref.get('type') or {}).get('name') == 'Referee':
                    fixture_data['referee'] = ref.get('name')
                    break
            
            # Salvar
            supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
            fixtures_saved += 1
            
            # Contar eventos e estatísticas
            events = fixture.get('events', [])
            stats = fixture.get('statistics', [])
            events_count += len(events)
            stats_count += len(stats)
            
            # Mostrar amostra de dados
            if fixtures_saved == 1:
                print(f"\n   📝 Exemplo de partida:")
                print(f"      ID: {fixture.get('id')}")
                print(f"      Data: {fixture.get('starting_at')}")
                print(f"      Eventos: {len(events)}")
                print(f"      Estatísticas: {len(stats)}")
                if events:
                    print(f"      Tipos de eventos: {set(e.get('type_id') for e in events[:5])}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar partida {fixture.get('id')}: {e}")
    
    # ============================================
    # 6. RELATÓRIO FINAL
    # ============================================
    print("\n" + "=" * 70)
    print("✅ SINCRONIZAÇÃO CONCLUÍDA!")
    print("=" * 70)
    
    print(f"\n📊 RESUMO DA IMPORTAÇÃO:")
    print(f"   • Partidas salvas: {fixtures_saved}/{len(all_fixtures)}")
    print(f"   • Total de eventos: {events_count}")
    print(f"   • Total de estatísticas: {stats_count}")
    
    # Estatísticas do banco
    try:
        fixtures = supabase.table('fixtures').select('*', count='exact').execute()
        print(f"\n📊 TOTAL NO BANCO:")
        print(f"   • Partidas: {fixtures.count}")
        
        # Últimas partidas
        recent = supabase.table('fixtures').select('*').order('match_date', desc=True).limit(5).execute()
        if recent.data:
            print("\n🎮 Últimas 5 partidas:")
            for f in recent.data:
                date = f.get('match_date', '')[:10] if f.get('match_date') else '?'
                home = f.get('home_team_id', '?')
                away = f.get('away_team_id', '?')
                score = f"{f.get('home_score', '-')} x {f.get('away_score', '-')}"
                print(f"   {date}: Time {home} {score} Time {away}")
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
    
    print("\n✅ Processo finalizado com sucesso!")
    print("=" * 70)

if __name__ == "__main__":
    sync_brasileirao_otimizado()
