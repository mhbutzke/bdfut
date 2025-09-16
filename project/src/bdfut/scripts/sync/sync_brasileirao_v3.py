#!/usr/bin/env python3
"""
Script FINAL OTIMIZADO - Brasileirão Série A 2025
Versão 3.0 - Com divisão de períodos e todas as correções
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timedelta
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

# Mapeamentos
EVENT_TYPE_MAP = {
    14: 'goal',
    15: 'own_goal',
    16: 'penalty',
    17: 'missed_penalty',
    18: 'substitution',
    19: 'yellow_card',
    20: 'red_card',
    21: 'yellow_red_card'
}

def split_date_range(start_date, end_date, max_days=90):
    """Divide um período em chunks de no máximo max_days dias"""
    chunks = []
    current_start = datetime.strptime(start_date, '%Y-%m-%d')
    final_end = datetime.strptime(end_date, '%Y-%m-%d')
    
    while current_start < final_end:
        current_end = min(current_start + timedelta(days=max_days - 1), final_end)
        chunks.append((
            current_start.strftime('%Y-%m-%d'),
            current_end.strftime('%Y-%m-%d')
        ))
        current_start = current_end + timedelta(days=1)
    
    return chunks

def sync_brasileirao_final():
    """Versão FINAL com todas as correções"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 70)
    print("🏆 BRASILEIRÃO SÉRIE A 2025 - VERSÃO FINAL 3.0")
    print("=" * 70)
    
    LEAGUE_ID = 648
    
    # 1. LIGA
    print("\n📋 1. Sincronizando liga...")
    try:
        league = sportmonks.get_league_by_id(LEAGUE_ID, include='country;seasons')
        print(f"   ✅ {league.get('name')}")
        
        league_data = {
            'sportmonks_id': league.get('id'),
            'name': league.get('name'),
            'country': league.get('country', {}).get('name') if league.get('country') else 'Brasil',
            'logo_url': league.get('image_path'),
            'active': league.get('active', True),
            'updated_at': datetime.now().isoformat()
        }
        supabase.table('leagues').upsert(league_data, on_conflict='sportmonks_id').execute()
    except Exception as e:
        logger.error(f"Erro: {e}")
        return
    
    # 2. TEMPORADA
    print("\n📅 2. Identificando temporada 2025...")
    current_season = None
    
    if league.get('seasons'):
        for season in league['seasons']:
            if '2025' in str(season.get('name', '')):
                current_season = season
                break
        
        if not current_season:
            current_season = next((s for s in league['seasons'] if s.get('is_current')), 
                                 league['seasons'][-1] if league['seasons'] else None)
    
    if not current_season:
        print("   ❌ Temporada não encontrada!")
        return
    
    SEASON_ID = current_season['id']
    print(f"   ✅ {current_season['name']} (ID: {SEASON_ID})")
    print(f"   📅 {current_season.get('starting_at')} até {current_season.get('ending_at')}")
    
    season_data = {
        'sportmonks_id': SEASON_ID,
        'name': current_season['name'],
        'league_id': LEAGUE_ID,
        'start_date': current_season.get('starting_at'),
        'end_date': current_season.get('ending_at'),
        'current': current_season.get('is_current', False),
        'updated_at': datetime.now().isoformat()
    }
    supabase.table('seasons').upsert(season_data, on_conflict='sportmonks_id').execute()
    
    # 3. TIMES
    print("\n⚽ 3. Sincronizando times...")
    try:
        teams = sportmonks.get_teams_by_season(SEASON_ID, include='venue')
        print(f"   ✅ {len(teams)} times")
        
        for team in teams:
            team_data = {
                'sportmonks_id': team.get('id'),
                'name': team.get('name'),
                'short_code': team.get('short_code'),
                'logo_url': team.get('image_path'),
                'founded': team.get('founded'),
                'venue_name': team.get('venue', {}).get('name') if isinstance(team.get('venue'), dict) else None,
                'updated_at': datetime.now().isoformat()
            }
            supabase.table('teams').upsert(team_data, on_conflict='sportmonks_id').execute()
    except Exception as e:
        logger.error(f"Erro times: {e}")
    
    # 4. PARTIDAS (DIVIDINDO PERÍODO)
    print("\n🎮 4. Buscando partidas (dividindo em períodos de 90 dias)...")
    
    start_date = current_season.get('starting_at', '2025-03-29')
    end_date = current_season.get('ending_at', '2025-12-21')
    
    # Dividir em chunks de 90 dias
    date_chunks = split_date_range(start_date, end_date, 90)
    print(f"   📅 Dividindo em {len(date_chunks)} períodos:")
    for i, (s, e) in enumerate(date_chunks, 1):
        print(f"      {i}. {s} até {e}")
    
    all_fixtures = []
    includes = 'participants;scores;state;venue;events;statistics;lineups;referees'
    
    for chunk_start, chunk_end in date_chunks:
        try:
            print(f"\n   🔍 Buscando partidas de {chunk_start} até {chunk_end}...")
            
            # Buscar com filtro correto
            params = {
                'include': includes,
                'filters': f'leagueIds:{LEAGUE_ID}'
            }
            
            # Buscar com paginação
            page = 1
            chunk_fixtures = []
            
            while True:
                params['page'] = page
                response = sportmonks._make_request(
                    f'/fixtures/between/{chunk_start}/{chunk_end}',
                    params
                )
                
                data = response.get('data', [])
                chunk_fixtures.extend(data)
                
                if not response.get('pagination', {}).get('has_more', False) or page >= 5:
                    break
                    
                page += 1
                time.sleep(0.5)
            
            print(f"      ✅ {len(chunk_fixtures)} partidas encontradas")
            all_fixtures.extend(chunk_fixtures)
            
        except Exception as e:
            logger.error(f"Erro no período {chunk_start}-{chunk_end}: {e}")
            continue
    
    print(f"\n   📊 Total: {len(all_fixtures)} partidas")
    
    # 5. PROCESSAR PARTIDAS
    if all_fixtures:
        print("\n💾 5. Salvando partidas completas...")
        
        success = 0
        events_total = 0
        stats_total = 0
        
        for i, fixture in enumerate(all_fixtures, 1):
            try:
                # Status
                state = fixture.get('state', {})
                status = state.get('state') or state.get('name') or 'NS'
                
                # Dados básicos
                fixture_data = {
                    'sportmonks_id': fixture.get('id'),
                    'league_id': LEAGUE_ID,
                    'season_id': SEASON_ID,
                    'match_date': fixture.get('starting_at'),
                    'status': status,
                    'venue': fixture.get('venue', {}).get('name') if fixture.get('venue') else None,
                    'updated_at': datetime.now().isoformat()
                }
                
                # Times (home/away)
                for p in fixture.get('participants', []):
                    loc = (p.get('meta') or {}).get('location')
                    if loc == 'home':
                        fixture_data['home_team_id'] = p.get('id')
                    elif loc == 'away':
                        fixture_data['away_team_id'] = p.get('id')
                
                # Scores
                for s in fixture.get('scores', []):
                    if s.get('description') == 'CURRENT':
                        if s.get('participant') == 'home':
                            fixture_data['home_score'] = (s.get('score') or {}).get('goals')
                        elif s.get('participant') == 'away':
                            fixture_data['away_score'] = (s.get('score') or {}).get('goals')
                
                # Árbitro
                for ref in fixture.get('referees', []):
                    if (ref.get('type') or {}).get('name') == 'Referee':
                        fixture_data['referee'] = ref.get('name')
                        break
                
                # Salvar partida
                supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
                
                # Contar eventos e estatísticas
                events_total += len(fixture.get('events', []))
                stats_total += len(fixture.get('statistics', []))
                
                success += 1
                
                if i % 20 == 0:
                    print(f"   Processadas {i}/{len(all_fixtures)}...")
                    
            except Exception as e:
                logger.error(f"Erro partida {fixture.get('id')}: {e}")
    
        print(f"\n   ✅ {success} partidas salvas")
        print(f"   🎯 {events_total} eventos encontrados")
        print(f"   📈 {stats_total} estatísticas encontradas")
    
    # 6. RESUMO FINAL
    print("\n" + "=" * 70)
    print("✅ SINCRONIZAÇÃO CONCLUÍDA!")
    print("=" * 70)
    
    try:
        # Contagens corretas
        leagues = supabase.table('leagues').select('*', count='exact').execute()
        seasons = supabase.table('seasons').select('*', count='exact').execute()
        teams = supabase.table('teams').select('*', count='exact').execute()
        fixtures = supabase.table('fixtures').select('*', count='exact').execute()
        
        print("\n📊 BANCO DE DADOS:")
        print(f"   • Ligas: {leagues.count}")
        print(f"   • Temporadas: {seasons.count}")
        print(f"   • Times: {teams.count}")
        print(f"   • Partidas: {fixtures.count}")
        
        # Mostrar algumas partidas recentes
        recent = supabase.table('fixtures').select('*').order('match_date', desc=True).limit(5).execute()
        if recent.data:
            print("\n🎮 Últimas partidas:")
            for f in recent.data:
                home = f.get('home_team_id', '?')
                away = f.get('away_team_id', '?')
                score = f"{f.get('home_score', '-')} x {f.get('away_score', '-')}"
                date = f.get('match_date', '')[:10] if f.get('match_date') else '?'
                print(f"   {date}: Time {home} {score} Time {away}")
                
    except Exception as e:
        logger.error(f"Erro estatísticas: {e}")
    
    print("\n✅ Dados do Brasileirão 2025 sincronizados com sucesso!")
    print("=" * 70)

if __name__ == "__main__":
    sync_brasileirao_final()
