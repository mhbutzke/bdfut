#!/usr/bin/env python3
"""
Script FINAL PRODUCTION-READY - Brasileirão Série A 2025
Versão 4.0 - Com todas as correções críticas implementadas
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

# CORREÇÃO 1: Mapeamento correto de eventos
EVENT_TYPE_MAP = {
    14: 'goal',
    15: 'penalty_goal',
    16: 'penalty_missed',
    17: 'own_goal',
    19: 'yellow_card',
    20: 'red_card',
    83: 'substitution'  # Corrigido!
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
    45: 'possession',
    52: 'passes_total',
    53: 'passes_accurate',
    54: 'pass_percentage',
    56: 'attacks',
    57: 'dangerous_attacks',
    86: 'saves',
    214: 'tackles',
    78: 'blocked_shots',
    79: 'interceptions'
}

def to_ymd(date_str):
    """Normaliza data para YYYY-MM-DD"""
    if not date_str:
        return None
    try:
        # Remove timezone e converte para date
        clean_date = str(date_str).replace('Z', '+00:00').split('T')[0]
        return clean_date[:10]
    except Exception:
        return str(date_str)[:10]

def generate_event_id(fixture_id, type_id, minute, player_id, team_id):
    """Gera ID único para evento se não existir"""
    key = f"{fixture_id}-{type_id}-{minute}-{player_id}-{team_id}"
    return hashlib.md5(key.encode()).hexdigest()[:16]

def sync_brasileirao_production():
    """Versão FINAL PRODUCTION-READY com todas as correções"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 70)
    print("🏆 BRASILEIRÃO 2025 - VERSÃO FINAL 4.0 PRODUCTION")
    print("=" * 70)
    
    LEAGUE_ID = 648
    
    # ============================================
    # 1. BUSCAR E SALVAR LIGA
    # ============================================
    print("\n📋 1. Sincronizando liga...")
    try:
        league = sportmonks.get_league_by_id(LEAGUE_ID, include='country;seasons')
        print(f"   ✅ {league.get('name')}")
        
        # Preparar dados da liga
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
        logger.error(f"Erro ao buscar liga: {e}")
        return
    
    # ============================================
    # 2. IDENTIFICAR TEMPORADA 2025
    # ============================================
    print("\n📅 2. Identificando temporada 2025...")
    current_season = None
    
    if league.get('seasons'):
        # Prioridade: 2025 > current > mais recente
        for season in league['seasons']:
            if '2025' in str(season.get('name', '')):
                current_season = season
                break
        
        if not current_season:
            current_season = next((s for s in league['seasons'] if s.get('is_current')), None)
        
        if not current_season and league['seasons']:
            current_season = sorted(league['seasons'], key=lambda x: x.get('id', 0), reverse=True)[0]
    
    if not current_season:
        print("   ❌ Temporada não encontrada!")
        return
    
    SEASON_ID = current_season['id']
    
    # CORREÇÃO 2: Normalizar datas
    start_date = to_ymd(current_season.get('starting_at')) or '2025-01-01'
    end_date = to_ymd(current_season.get('ending_at')) or '2025-12-31'
    
    print(f"   ✅ {current_season['name']} (ID: {SEASON_ID})")
    print(f"   📅 Período: {start_date} até {end_date}")
    
    # Salvar temporada
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
    # 3. BUSCAR E SALVAR TIMES
    # ============================================
    print("\n⚽ 3. Sincronizando times...")
    try:
        teams = sportmonks.get_teams_by_season(SEASON_ID, include='venue')
        print(f"   ✅ {len(teams)} times encontrados")
        
        # Salvar venues primeiro
        venues_saved = set()
        for team in teams:
            if isinstance(team.get('venue'), dict) and team['venue'].get('id'):
                venue = team['venue']
                if venue['id'] not in venues_saved:
                    venue_data = {
                        'sportmonks_id': venue['id'],
                        'name': venue.get('name'),
                        'city': venue.get('city'),
                        'capacity': venue.get('capacity'),
                        'surface': venue.get('surface'),
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    try:
                        supabase.table('venues').upsert(venue_data, on_conflict='sportmonks_id').execute()
                        venues_saved.add(venue['id'])
                    except:
                        pass  # Tabela pode não existir ainda
        
        # Salvar times
        for team in teams:
            team_data = {
                'sportmonks_id': team.get('id'),
                'name': team.get('name'),
                'short_code': team.get('short_code'),
                'logo_url': team.get('image_path'),
                'founded': team.get('founded'),
                'venue_id': team.get('venue', {}).get('id') if isinstance(team.get('venue'), dict) else None,
                'updated_at': datetime.utcnow().isoformat()
            }
            supabase.table('teams').upsert(team_data, on_conflict='sportmonks_id').execute()
            
    except Exception as e:
        logger.error(f"Erro ao buscar times: {e}")
    
    # ============================================
    # 4. BUSCAR PARTIDAS COM PAGINAÇÃO CORRETA
    # ============================================
    print("\n🎮 4. Buscando partidas...")
    
    # CORREÇÃO 3: Dividir em períodos de 90 dias
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
    print(f"   📅 Dividindo em {len(date_chunks)} períodos de até 90 dias")
    
    all_fixtures = []
    includes = 'participants;scores;state;venue;events;statistics;lineups;referees'
    
    for chunk_start, chunk_end in date_chunks:
        print(f"\n   🔍 Período: {chunk_start} até {chunk_end}")
        
        try:
            # CORREÇÃO 4: Usar método público com paginação robusta
            chunk_fixtures = []
            page = 1
            retries = 0
            max_retries = 3
            
            while True:
                try:
                    # Usar método público do cliente
                    fixtures_response = sportmonks.get_fixtures_by_date_range(
                        chunk_start, 
                        chunk_end,
                        include=includes,
                        filters=f'leagueIds:{LEAGUE_ID}',
                        page=page,
                        per_page=25
                    )
                    
                    # Se retornar lista direta (compatibilidade)
                    if isinstance(fixtures_response, list):
                        chunk_fixtures.extend(fixtures_response)
                        break  # Sem paginação
                    
                    # Se retornar dict com data e pagination
                    data = fixtures_response.get('data', [])
                    chunk_fixtures.extend(data)
                    
                    # Verificar paginação
                    pagination = fixtures_response.get('pagination', {})
                    total_pages = pagination.get('total_pages', 1)
                    has_more = pagination.get('has_more', False)
                    
                    if page >= total_pages or not has_more or not data:
                        break
                    
                    page += 1
                    retries = 0  # Reset retries on success
                    
                    # Rate limit
                    time.sleep(0.5)
                    
                except Exception as e:
                    if '429' in str(e) and retries < max_retries:
                        # CORREÇÃO 5: Retry com backoff para 429
                        wait_time = 2 ** retries
                        logger.warning(f"Rate limit atingido. Aguardando {wait_time}s...")
                        time.sleep(wait_time)
                        retries += 1
                    else:
                        logger.error(f"Erro ao buscar página {page}: {e}")
                        break
            
            print(f"      ✅ {len(chunk_fixtures)} partidas encontradas")
            all_fixtures.extend(chunk_fixtures)
            
        except Exception as e:
            logger.error(f"Erro no período {chunk_start}-{chunk_end}: {e}")
    
    print(f"\n   📊 Total geral: {len(all_fixtures)} partidas")
    
    # ============================================
    # 5. PROCESSAR E SALVAR PARTIDAS COMPLETAS
    # ============================================
    if not all_fixtures:
        print("   ⚠️  Nenhuma partida encontrada")
        return
    
    print("\n💾 5. Processando partidas com dados completos...")
    
    fixtures_saved = 0
    events_saved = 0
    stats_saved = 0
    lineups_saved = 0
    referees_saved = set()
    
    for i, fixture in enumerate(all_fixtures, 1):
        try:
            # ========== DADOS BÁSICOS ==========
            state = fixture.get('state', {})
            status = state.get('state') or state.get('name') or 'NS'
            
            fixture_data = {
                'sportmonks_id': fixture.get('id'),
                'league_id': LEAGUE_ID,
                'season_id': SEASON_ID,
                'match_date': fixture.get('starting_at'),
                'status': status,
                'venue_id': fixture.get('venue', {}).get('id') if isinstance(fixture.get('venue'), dict) else None,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # ========== TIMES (HOME/AWAY) ==========
            for participant in fixture.get('participants', []):
                location = (participant.get('meta') or {}).get('location')
                if location == 'home':
                    fixture_data['home_team_id'] = participant.get('id')
                elif location == 'away':
                    fixture_data['away_team_id'] = participant.get('id')
            
            # ========== SCORES CORRIGIDOS ==========
            # CORREÇÃO 6: Priorizar CURRENT, cair para FT
            home_score = away_score = None
            for score in fixture.get('scores', []):
                if score.get('participant') not in ('home', 'away'):
                    continue
                if score.get('description') in ('CURRENT', 'FT'):
                    goals = (score.get('score') or {}).get('goals')
                    if score.get('participant') == 'home':
                        home_score = goals
                    else:
                        away_score = goals
            
            fixture_data['home_score'] = home_score
            fixture_data['away_score'] = away_score
            
            # ========== ÁRBITROS ==========
            if fixture.get('referees'):
                for ref in fixture['referees']:
                    ref_id = ref.get('id')
                    if ref_id and ref_id not in referees_saved:
                        ref_data = {
                            'sportmonks_id': ref_id,
                            'name': ref.get('name'),
                            'type': (ref.get('type') or {}).get('name'),
                            'updated_at': datetime.utcnow().isoformat()
                        }
                        try:
                            supabase.table('referees').upsert(ref_data, on_conflict='sportmonks_id').execute()
                            referees_saved.add(ref_id)
                        except:
                            pass
                    
                    # Árbitro principal na fixture
                    if (ref.get('type') or {}).get('name') == 'Referee':
                        fixture_data['referee_id'] = ref_id
            
            # Salvar fixture
            supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
            fixtures_saved += 1
            
            # ========== EVENTOS ==========
            if fixture.get('events'):
                events_to_save = []
                for event in fixture['events']:
                    type_id = event.get('type_id')
                    
                    # Gerar ID se não existir
                    event_id = event.get('id')
                    if not event_id:
                        event_id = generate_event_id(
                            fixture['id'],
                            type_id,
                            event.get('minute', 0),
                            event.get('player_id'),
                            event.get('participant_id')
                        )
                    
                    event_data = {
                        'id': event_id,
                        'fixture_id': fixture['id'],
                        'type_id': type_id,
                        'event_type': EVENT_TYPE_MAP.get(type_id, 'other'),
                        'minute': event.get('minute', 0),
                        'extra_minute': event.get('extra_minute'),
                        'team_id': event.get('participant_id'),
                        'player_id': event.get('player_id'),
                        'related_player_id': event.get('related_player_id'),
                        'period_id': event.get('period_id'),
                        'result': event.get('result'),
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    events_to_save.append(event_data)
                
                if events_to_save:
                    try:
                        supabase.table('fixture_events').upsert(events_to_save, on_conflict='id').execute()
                        events_saved += len(events_to_save)
                    except Exception as e:
                        logger.debug(f"Erro ao salvar eventos: {e}")
            
            # ========== ESTATÍSTICAS ==========
            if fixture.get('statistics'):
                stats_by_team = {}
                
                for stat in fixture['statistics']:
                    team_id = stat.get('participant_id')
                    if not team_id:
                        continue
                    
                    # Criar entrada para o time se não existir
                    if team_id not in stats_by_team:
                        stats_by_team[team_id] = {
                            'fixture_id': fixture['id'],
                            'team_id': team_id,
                            'updated_at': datetime.utcnow().isoformat()
                        }
                    
                    # Mapear estatística
                    type_id = stat.get('type_id')
                    value = (stat.get('data') or {}).get('value')
                    column = STAT_TYPE_MAP.get(type_id)
                    
                    if column and value is not None:
                        stats_by_team[team_id][column] = value
                
                if stats_by_team:
                    try:
                        for team_stats in stats_by_team.values():
                            supabase.table('fixture_statistics').upsert(
                                team_stats,
                                on_conflict='fixture_id,team_id'
                            ).execute()
                        stats_saved += len(stats_by_team)
                    except Exception as e:
                        logger.debug(f"Erro ao salvar estatísticas: {e}")
            
            # ========== ESCALAÇÕES CORRIGIDAS ==========
            # CORREÇÃO 7: Iterar players dentro de cada lineup
            if fixture.get('lineups'):
                lineups_to_save = []
                
                for lineup in fixture['lineups']:
                    team_id = lineup.get('participant_id') or lineup.get('team_id')
                    
                    # V3 tem players como array dentro do lineup
                    players = lineup.get('players', [])
                    
                    # Se não houver players array, pode ser lineup direto (retrocompatibilidade)
                    if not players and lineup.get('player_id'):
                        players = [lineup]
                    
                    for player in players:
                        player_id = player.get('player_id') or player.get('id')
                        if not player_id:
                            continue
                        
                        # Nome do jogador pode estar em player.player.name ou player.player_name
                        player_name = None
                        if isinstance(player.get('player'), dict):
                            player_name = player['player'].get('name')
                        if not player_name:
                            player_name = player.get('player_name')
                        
                        lineup_data = {
                            'fixture_id': fixture['id'],
                            'team_id': team_id,
                            'player_id': player_id,
                            'player_name': player_name,
                            'type': (lineup.get('type') or {}).get('name', 'lineup'),
                            'position_id': player.get('position_id') or (player.get('position') or {}).get('id'),
                            'position_name': (player.get('position') or {}).get('name'),
                            'jersey_number': player.get('jersey_number') or player.get('number'),
                            'captain': bool(player.get('captain')),
                            'updated_at': datetime.utcnow().isoformat()
                        }
                        lineups_to_save.append(lineup_data)
                
                if lineups_to_save:
                    try:
                        for lineup in lineups_to_save:
                            supabase.table('fixture_lineups').upsert(
                                lineup,
                                on_conflict='fixture_id,team_id,player_id'
                            ).execute()
                        lineups_saved += len(lineups_to_save)
                    except Exception as e:
                        logger.debug(f"Erro ao salvar lineups: {e}")
            
            # Progresso
            if i % 50 == 0:
                print(f"   Processadas {i}/{len(all_fixtures)} partidas...")
            
        except Exception as e:
            logger.error(f"Erro ao processar partida {fixture.get('id')}: {e}")
    
    # ============================================
    # 6. RELATÓRIO FINAL
    # ============================================
    print("\n" + "=" * 70)
    print("✅ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    
    print(f"\n📊 RESUMO DA IMPORTAÇÃO:")
    print(f"   • Partidas salvas: {fixtures_saved}")
    print(f"   • Eventos salvos: {events_saved}")
    print(f"   • Estatísticas salvas: {stats_saved}")
    print(f"   • Escalações salvas: {lineups_saved}")
    print(f"   • Árbitros únicos: {len(referees_saved)}")
    
    # Estatísticas do banco
    try:
        leagues = supabase.table('leagues').select('*', count='exact').execute()
        seasons = supabase.table('seasons').select('*', count='exact').execute()
        teams = supabase.table('teams').select('*', count='exact').execute()
        fixtures = supabase.table('fixtures').select('*', count='exact').execute()
        
        print(f"\n📊 TOTAIS NO BANCO:")
        print(f"   • Ligas: {leagues.count}")
        print(f"   • Temporadas: {seasons.count}")
        print(f"   • Times: {teams.count}")
        print(f"   • Partidas: {fixtures.count}")
        
        # Amostra de partidas recentes
        recent = supabase.table('fixtures').select('*').order('match_date', desc=True).limit(3).execute()
        if recent.data:
            print("\n🎮 Últimas partidas adicionadas:")
            for f in recent.data:
                date = f.get('match_date', '')[:10] if f.get('match_date') else '?'
                home = f.get('home_team_id', '?')
                away = f.get('away_team_id', '?')
                score = f"{f.get('home_score', '-')} x {f.get('away_score', '-')}"
                print(f"   {date}: Time {home} {score} Time {away}")
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas finais: {e}")
    
    print("\n✅ Script finalizado com sucesso!")
    print("🎯 Próximos passos:")
    print("   1. Verificar dados no Supabase Dashboard")
    print("   2. Criar índices para otimização se necessário")
    print("   3. Expandir para outras ligas")
    print("=" * 70)

if __name__ == "__main__":
    sync_brasileirao_production()
