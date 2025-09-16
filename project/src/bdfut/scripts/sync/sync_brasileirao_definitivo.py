#!/usr/bin/env python3
"""
Script DEFINITIVO - Brasileirão Série A 2025
Versão 5.0 - Compatível com SportmonksClient atual
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
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mapeamento correto de eventos (v3)
EVENT_TYPE_MAP = {
    14: 'goal',
    15: 'penalty_goal',
    16: 'penalty_missed',
    17: 'own_goal',
    19: 'yellow_card',
    20: 'red_card',
    83: 'substitution'
}

# Mapeamento de estatísticas
STAT_TYPE_MAP = {
    42: 'shots_total',
    80: 'shots_on_target',
    34: 'corners',
    84: 'yellow_cards',
    83: 'red_cards',
    88: 'fouls',
    85: 'offsides',
    45: 'possession'
}

def to_ymd(date_str):
    """Normaliza data para YYYY-MM-DD"""
    if not date_str:
        return None
    try:
        clean_date = str(date_str).replace('Z', '+00:00').split('T')[0]
        return clean_date[:10]
    except:
        return str(date_str)[:10]

def sync_brasileirao_definitivo():
    """Versão DEFINITIVA compatível com o cliente atual"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 70)
    print("🏆 BRASILEIRÃO 2025 - VERSÃO DEFINITIVA 5.0")
    print("=" * 70)
    
    LEAGUE_ID = 648
    
    # ============================================
    # 1. LIGA
    # ============================================
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
            'updated_at': datetime.utcnow().isoformat()
        }
        
        supabase.table('leagues').upsert(league_data, on_conflict='sportmonks_id').execute()
        
    except Exception as e:
        logger.error(f"Erro: {e}")
        return
    
    # ============================================
    # 2. TEMPORADA
    # ============================================
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
    start_date = to_ymd(current_season.get('starting_at')) or '2025-03-29'
    end_date = to_ymd(current_season.get('ending_at')) or '2025-12-21'
    
    print(f"   ✅ {current_season['name']} (ID: {SEASON_ID})")
    print(f"   📅 Período: {start_date} até {end_date}")
    
    season_data = {
        'sportmonks_id': SEASON_ID,
        'name': current_season['name'],
        'league_id': LEAGUE_ID,
        'start_date': start_date,
        'end_date': end_date,
        'current': current_season.get('is_current', False),
        'updated_at': datetime.utcnow().isoformat()
    }
    supabase.table('seasons').upsert(season_data, on_conflict='sportmonks_id').execute()
    
    # ============================================
    # 3. TIMES
    # ============================================
    print("\n⚽ 3. Sincronizando times...")
    try:
        teams = sportmonks.get_teams_by_season(SEASON_ID, include='venue')
        print(f"   ✅ {len(teams)} times encontrados")
        
        for team in teams:
            team_data = {
                'sportmonks_id': team.get('id'),
                'name': team.get('name'),
                'short_code': team.get('short_code'),
                'logo_url': team.get('image_path'),
                'founded': team.get('founded'),
                # Salvar nome do venue ao invés de ID (já que não temos tabela venues)
                'venue_name': team.get('venue', {}).get('name') if isinstance(team.get('venue'), dict) else None,
                'updated_at': datetime.utcnow().isoformat()
            }
            supabase.table('teams').upsert(team_data, on_conflict='sportmonks_id').execute()
            
    except Exception as e:
        logger.error(f"Erro times: {e}")
    
    # ============================================
    # 4. BUSCAR PARTIDAS
    # ============================================
    print("\n🎮 4. Buscando partidas do Brasileirão...")
    
    # Dividir em períodos de 90 dias
    def split_date_range(start, end, max_days=90):
        chunks = []
        current = datetime.strptime(start, '%Y-%m-%d')
        final = datetime.strptime(end, '%Y-%m-%d')
        
        while current < final:
            chunk_end = min(current + timedelta(days=max_days - 1), final)
            chunks.append((
                current.strftime('%Y-%m-%d'),
                chunk_end.strftime('%Y-%m-%d')
            ))
            current = chunk_end + timedelta(days=1)
        
        return chunks
    
    date_chunks = split_date_range(start_date, end_date, 90)
    print(f"   📅 Dividindo em {len(date_chunks)} períodos")
    
    all_fixtures = []
    includes = 'participants;scores;state;venue;events;statistics;lineups;referees'
    
    for chunk_start, chunk_end in date_chunks:
        print(f"\n   🔍 Buscando {chunk_start} até {chunk_end}...")
        
        try:
            # Buscar partidas do período
            fixtures = sportmonks.get_fixtures_by_date_range(
                chunk_start,
                chunk_end,
                include=includes
            )
            
            # Filtrar apenas partidas do Brasileirão
            brasileirao_fixtures = [
                f for f in fixtures 
                if f.get('league_id') == LEAGUE_ID
            ]
            
            print(f"      ✅ {len(brasileirao_fixtures)} partidas do Brasileirão")
            all_fixtures.extend(brasileirao_fixtures)
            
            # Rate limit
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Erro período {chunk_start}-{chunk_end}: {e}")
    
    print(f"\n   📊 Total: {len(all_fixtures)} partidas do Brasileirão")
    
    # ============================================
    # 5. PROCESSAR PARTIDAS
    # ============================================
    if not all_fixtures:
        print("   ⚠️  Nenhuma partida encontrada")
        return
    
    print("\n💾 5. Processando e salvando partidas...")
    
    fixtures_saved = 0
    events_total = 0
    stats_total = 0
    lineups_total = 0
    
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
                'venue': fixture.get('venue', {}).get('name') if isinstance(fixture.get('venue'), dict) else None,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Times (home/away)
            for p in fixture.get('participants', []):
                loc = (p.get('meta') or {}).get('location')
                if loc == 'home':
                    fixture_data['home_team_id'] = p.get('id')
                elif loc == 'away':
                    fixture_data['away_team_id'] = p.get('id')
            
            # Scores
            home_score = away_score = None
            for s in fixture.get('scores', []):
                if s.get('participant') not in ('home', 'away'):
                    continue
                if s.get('description') in ('CURRENT', 'FT'):
                    goals = (s.get('score') or {}).get('goals')
                    if s.get('participant') == 'home':
                        home_score = goals
                    else:
                        away_score = goals
            
            fixture_data['home_score'] = home_score
            fixture_data['away_score'] = away_score
            
            # Árbitro principal
            if fixture.get('referees'):
                for ref in fixture['referees']:
                    if (ref.get('type') or {}).get('name') == 'Referee':
                        fixture_data['referee'] = ref.get('name')
                        break
            
            # Salvar fixture
            supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
            fixtures_saved += 1
            
            # Contar eventos, estatísticas e escalações
            events_total += len(fixture.get('events', []))
            stats_total += len(fixture.get('statistics', []))
            
            # Contar jogadores nas escalações
            for lineup in fixture.get('lineups', []):
                players = lineup.get('players', [])
                if not players and lineup.get('player_id'):
                    lineups_total += 1
                else:
                    lineups_total += len(players)
            
            # Progresso
            if i % 50 == 0 or i == len(all_fixtures):
                print(f"   Processadas {i}/{len(all_fixtures)} partidas...")
            
        except Exception as e:
            logger.error(f"Erro partida {fixture.get('id')}: {e}")
    
    # ============================================
    # 6. RELATÓRIO FINAL
    # ============================================
    print("\n" + "=" * 70)
    print("✅ SINCRONIZAÇÃO CONCLUÍDA!")
    print("=" * 70)
    
    print(f"\n📊 RESUMO:")
    print(f"   • Partidas processadas: {fixtures_saved}")
    print(f"   • Eventos encontrados: {events_total}")
    print(f"   • Estatísticas encontradas: {stats_total}")
    print(f"   • Jogadores em escalações: {lineups_total}")
    
    # Totais no banco
    try:
        leagues = supabase.table('leagues').select('*', count='exact').execute()
        seasons = supabase.table('seasons').select('*', count='exact').execute()
        teams = supabase.table('teams').select('*', count='exact').execute()
        fixtures = supabase.table('fixtures').select('*', count='exact').execute()
        
        print(f"\n📊 BANCO DE DADOS:")
        print(f"   • Ligas: {leagues.count}")
        print(f"   • Temporadas: {seasons.count}")
        print(f"   • Times: {teams.count}")
        print(f"   • Partidas: {fixtures.count}")
        
        # Últimas partidas
        recent = supabase.table('fixtures').select('*').order('match_date', desc=True).limit(3).execute()
        if recent.data:
            print("\n🎮 Últimas partidas:")
            for f in recent.data:
                date = f.get('match_date', '')[:10] if f.get('match_date') else '?'
                home = f.get('home_team_id', '?')
                away = f.get('away_team_id', '?')
                score = f"{f.get('home_score', '-')} x {f.get('away_score', '-')}"
                status = f.get('status', 'NS')
                print(f"   {date} [{status}]: Time {home} {score} Time {away}")
        
    except Exception as e:
        logger.error(f"Erro estatísticas: {e}")
    
    print("\n🎯 Próximos passos:")
    print("   1. Criar tabelas de eventos/estatísticas/escalações")
    print("   2. Executar nova versão com salvamento completo")
    print("   3. Adicionar outras ligas")
    print("=" * 70)

if __name__ == "__main__":
    sync_brasileirao_definitivo()
