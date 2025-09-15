#!/usr/bin/env python3
"""
Script de EXPANSÃO COMPLETA para múltiplas ligas
Coleta temporada atual + 2 temporadas anteriores
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
import hashlib
from collections import Counter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração das ligas
LIGAS_CONFIG = {
    # Brasil
    648: {'nome': 'Brasileirão Série A', 'pais': 'Brasil'},
    651: {'nome': 'Brasileirão Série B', 'pais': 'Brasil'},
    654: {'nome': 'Copa do Brasil', 'pais': 'Brasil'},
    
    # Argentina
    636: {'nome': 'Primera División', 'pais': 'Argentina'},
    
    # CONMEBOL
    1122: {'nome': 'Copa Libertadores', 'pais': 'CONMEBOL'},
    1116: {'nome': 'Copa Sudamericana', 'pais': 'CONMEBOL'},
    
    # UEFA
    2: {'nome': 'Champions League', 'pais': 'UEFA'},
    5: {'nome': 'Europa League', 'pais': 'UEFA'},
    
    # Inglaterra
    8: {'nome': 'Premier League', 'pais': 'Inglaterra'},
    9: {'nome': 'Championship', 'pais': 'Inglaterra'},
    
    # Outros países
    564: {'nome': 'LaLiga', 'pais': 'Espanha'},
    462: {'nome': 'Liga Portugal', 'pais': 'Portugal'},
    301: {'nome': 'Ligue 1', 'pais': 'França'},
    82: {'nome': 'Bundesliga', 'pais': 'Alemanha'},
    743: {'nome': 'Liga MX', 'pais': 'México'},
    779: {'nome': 'MLS', 'pais': 'EUA'}
}

# Mapeamento de eventos
EVENT_TYPE_MAP = {
    14: 'goal',
    15: 'penalty_goal',
    16: 'penalty_missed',
    17: 'own_goal',
    18: 'substitution',
    19: 'yellow_card',
    20: 'red_card',
    21: 'yellow_red_card',
    83: 'substitution',
    52: 'injury',
    26: 'goal_var'
}

def generate_event_id(fixture_id, type_id, minute, player_id, team_id, index=0):
    """Gera ID único para evento"""
    key = f"{fixture_id}-{type_id}-{minute}-{player_id or 0}-{team_id or 0}-{index}"
    return hashlib.md5(key.encode()).hexdigest()[:20]

def processar_liga(sportmonks, supabase, league_id, league_info, num_temporadas=3):
    """Processa uma liga específica"""
    
    print(f"\n{'='*70}")
    print(f"🏆 {league_info['nome']} ({league_info['pais']}) - ID: {league_id}")
    print(f"{'='*70}")
    
    total_fixtures = 0
    total_events = 0
    total_stats = 0
    total_lineups = 0
    
    try:
        # ============================================
        # 1. BUSCAR TEMPORADAS
        # ============================================
        print(f"\n📅 Buscando temporadas...")
        
        # Buscar liga com temporadas
        response = sportmonks._make_request(
            f'/leagues/{league_id}',
            {'include': 'seasons'}
        )
        
        league_data = response.get('data', {})
        seasons = league_data.get('seasons', [])
        
        if not seasons:
            print(f"   ❌ Nenhuma temporada encontrada")
            return
        
        # Ordenar temporadas por data de início (mais recentes primeiro)
        seasons_sorted = sorted(seasons, 
                               key=lambda x: x.get('starting_at', ''), 
                               reverse=True)
        
        # Pegar as N temporadas mais recentes
        seasons_to_process = seasons_sorted[:num_temporadas]
        
        print(f"   ✅ {len(seasons_to_process)} temporadas encontradas:")
        for season in seasons_to_process:
            print(f"      • {season.get('name')} (ID: {season.get('id')})")
        
        # ============================================
        # 2. PROCESSAR CADA TEMPORADA
        # ============================================
        for season_idx, season in enumerate(seasons_to_process, 1):
            season_id = season.get('id')
            season_name = season.get('name')
            
            print(f"\n   📊 Temporada {season_idx}/{len(seasons_to_process)}: {season_name}")
            
            # Buscar fixtures da temporada
            print(f"      🔍 Buscando fixtures...")
            
            # Usar endpoint otimizado - buscar temporada com fixtures
            response = sportmonks._make_request(
                f'/seasons/{season_id}',
                {'include': 'fixtures'}
            )
            
            fixtures_data = response.get('data', {}).get('fixtures', [])
            fixture_ids = [f.get('id') for f in fixtures_data if f.get('id')]
            
            print(f"      ✅ {len(fixture_ids)} fixtures encontradas")
            
            if not fixture_ids:
                continue
            
            # ============================================
            # 3. BUSCAR DADOS COMPLETOS EM LOTES
            # ============================================
            includes = 'participants;scores;state;events;statistics;lineups;referees;venue'
            batch_size = 20
            
            season_events = 0
            season_stats = 0
            season_lineups = 0
            
            for i in range(0, len(fixture_ids), batch_size):
                batch_ids = fixture_ids[i:i + batch_size]
                batch_ids_str = ','.join(map(str, batch_ids))
                
                if i % 100 == 0:
                    print(f"      📦 Processando lote {i//batch_size + 1}/{(len(fixture_ids)-1)//batch_size + 1}...")
                
                try:
                    # Buscar dados completos
                    response = sportmonks._make_request(
                        f'/fixtures/multi/{batch_ids_str}',
                        {'include': includes}
                    )
                    
                    fixtures_batch = response.get('data', [])
                    
                    # Processar cada fixture
                    for fixture in fixtures_batch:
                        fixture_id = fixture.get('id')
                        
                        # ========== SALVAR FIXTURE ==========
                        fixture_data = {
                            'sportmonks_id': fixture_id,
                            'league_id': league_id,
                            'season_id': season_id,
                            'match_date': fixture.get('starting_at'),
                            'status': fixture.get('state', {}).get('state') or fixture.get('state', {}).get('name'),
                            'venue': fixture.get('venue', {}).get('name') if fixture.get('venue') else None,
                            'referee': None,
                            'updated_at': datetime.utcnow().isoformat()
                        }
                        
                        # Times
                        for p in fixture.get('participants', []):
                            loc = (p.get('meta') or {}).get('location')
                            if loc == 'home':
                                fixture_data['home_team_id'] = p.get('id')
                                fixture_data['home_team_name'] = p.get('name')
                            elif loc == 'away':
                                fixture_data['away_team_id'] = p.get('id')
                                fixture_data['away_team_name'] = p.get('name')
                        
                        # Placar
                        for s in fixture.get('scores', []):
                            if s.get('description') in ('CURRENT', 'FT'):
                                if s.get('participant') == 'home':
                                    fixture_data['home_score'] = (s.get('score') or {}).get('goals')
                                elif s.get('participant') == 'away':
                                    fixture_data['away_score'] = (s.get('score') or {}).get('goals')
                        
                        # Árbitro principal
                        for ref in fixture.get('referees', []):
                            if (ref.get('type') or {}).get('name') == 'Referee':
                                fixture_data['referee'] = ref.get('name')
                                break
                        
                        # Salvar fixture
                        try:
                            supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
                            total_fixtures += 1
                        except:
                            pass
                        
                        # ========== SALVAR EVENTOS ==========
                        if fixture.get('events'):
                            events_to_save = []
                            event_index = {}
                            
                            for event in fixture['events']:
                                type_id = event.get('type_id')
                                minute = event.get('minute', 0)
                                team_id = event.get('participant_id')
                                player_id = event.get('player_id')
                                
                                # Criar ID único
                                event_key = f"{type_id}-{minute}-{player_id}-{team_id}"
                                event_index[event_key] = event_index.get(event_key, 0) + 1
                                
                                event_id = event.get('id')
                                if not event_id:
                                    event_id = generate_event_id(
                                        fixture_id, type_id, minute, 
                                        player_id, team_id, event_index[event_key]
                                    )
                                
                                event_type = EVENT_TYPE_MAP.get(type_id, f'type_{type_id}')
                                
                                event_data = {
                                    'id': str(event_id)[:255],
                                    'fixture_id': fixture_id,
                                    'type_id': type_id,
                                    'event_type': event_type,
                                    'minute': minute,
                                    'extra_minute': event.get('extra_minute'),
                                    'team_id': team_id,
                                    'player_id': player_id,
                                    'related_player_id': event.get('related_player_id'),
                                    'player_name': event.get('player_name'),
                                    'period_id': event.get('period_id'),
                                    'result': event.get('result')
                                }
                                events_to_save.append(event_data)
                            
                            # Salvar eventos
                            if events_to_save:
                                try:
                                    for j in range(0, len(events_to_save), 50):
                                        batch = events_to_save[j:j+50]
                                        supabase.table('match_events').upsert(batch, on_conflict='id').execute()
                                    season_events += len(events_to_save)
                                except:
                                    pass
                        
                        # ========== SALVAR ESTATÍSTICAS ==========
                        if fixture.get('statistics'):
                            stats_by_team = {}
                            
                            for stat in fixture['statistics']:
                                team_id = stat.get('participant_id')
                                if not team_id:
                                    continue
                                
                                if team_id not in stats_by_team:
                                    stats_by_team[team_id] = {
                                        'fixture_id': fixture_id,
                                        'team_id': team_id
                                    }
                                
                                type_id = stat.get('type_id')
                                value = None
                                
                                if isinstance(stat.get('data'), dict):
                                    value = stat['data'].get('value')
                                elif stat.get('data') is not None:
                                    value = stat.get('data')
                                
                                # Mapear estatísticas conhecidas
                                stat_map = {
                                    42: 'shots_total',
                                    80: 'shots_on_target',
                                    34: 'corners',
                                    84: 'yellow_cards',
                                    83: 'red_cards',
                                    88: 'fouls',
                                    85: 'offsides',
                                    45: 'ball_possession',
                                    52: 'passes_total',
                                    53: 'passes_accurate',
                                    54: 'pass_percentage',
                                    86: 'saves',
                                    214: 'tackles',
                                    79: 'interceptions',
                                    81: 'shots_inside_box',
                                    82: 'shots_outside_box',
                                    78: 'blocked_shots'
                                }
                                
                                if type_id in stat_map:
                                    stats_by_team[team_id][stat_map[type_id]] = value
                            
                            # Salvar estatísticas
                            if stats_by_team:
                                try:
                                    for team_stats in stats_by_team.values():
                                        supabase.table('match_statistics').upsert(
                                            team_stats,
                                            on_conflict='fixture_id,team_id'
                                        ).execute()
                                    season_stats += len(stats_by_team)
                                except:
                                    pass
                        
                        # ========== SALVAR ESCALAÇÕES ==========
                        if fixture.get('lineups'):
                            lineups_to_save = []
                            
                            for lineup in fixture['lineups']:
                                team_id = lineup.get('team_id') or lineup.get('participant_id')
                                player_id = lineup.get('player_id')
                                
                                if not player_id or not team_id:
                                    continue
                                
                                player_name = None
                                if isinstance(lineup.get('player'), dict):
                                    player_name = lineup['player'].get('name')
                                if not player_name:
                                    player_name = lineup.get('player_name')
                                
                                position_name = None
                                position_id = lineup.get('position_id')
                                if isinstance(lineup.get('position'), dict):
                                    position_name = lineup['position'].get('name')
                                    if not position_id:
                                        position_id = lineup['position'].get('id')
                                
                                lineup_data = {
                                    'fixture_id': fixture_id,
                                    'team_id': team_id,
                                    'player_id': player_id,
                                    'player_name': player_name,
                                    'type': 'lineup',
                                    'position_id': position_id,
                                    'position_name': position_name,
                                    'jersey_number': lineup.get('jersey_number') or lineup.get('number'),
                                    'captain': bool(lineup.get('captain')),
                                    'minutes_played': lineup.get('minutes_played'),
                                    'rating': lineup.get('rating')
                                }
                                lineups_to_save.append(lineup_data)
                            
                            # Salvar escalações
                            if lineups_to_save:
                                try:
                                    for lineup in lineups_to_save:
                                        try:
                                            supabase.table('match_lineups').upsert(
                                                lineup,
                                                on_conflict='fixture_id,team_id,player_id'
                                            ).execute()
                                            season_lineups += 1
                                        except:
                                            pass
                                except:
                                    pass
                    
                    # Rate limit
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.debug(f"Erro no lote: {e}")
                    continue
            
            # Resumo da temporada
            print(f"      ✅ Temporada processada:")
            print(f"         • Eventos: {season_events}")
            print(f"         • Estatísticas: {season_stats}")
            print(f"         • Escalações: {season_lineups}")
            
            total_events += season_events
            total_stats += season_stats
            total_lineups += season_lineups
        
        # Resumo da liga
        print(f"\n   📊 RESUMO - {league_info['nome']}:")
        print(f"      • Fixtures: {total_fixtures}")
        print(f"      • Eventos: {total_events}")
        print(f"      • Estatísticas: {total_stats}")
        print(f"      • Escalações: {total_lineups}")
        
        return {
            'fixtures': total_fixtures,
            'events': total_events,
            'stats': total_stats,
            'lineups': total_lineups
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar liga {league_id}: {e}")
        return None

def expandir_ligas():
    """Expande coleta para todas as ligas configuradas"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 80)
    print("🌍 EXPANSÃO COMPLETA - MÚLTIPLAS LIGAS")
    print("=" * 80)
    print(f"📅 Início: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    print(f"🏆 {len(LIGAS_CONFIG)} ligas para processar")
    print(f"📊 3 temporadas por liga (atual + 2 anteriores)")
    print()
    
    # Estatísticas globais
    global_stats = {
        'fixtures': 0,
        'events': 0,
        'stats': 0,
        'lineups': 0,
        'ligas_processadas': 0,
        'ligas_com_erro': 0
    }
    
    # Processar cada liga
    for league_id, league_info in LIGAS_CONFIG.items():
        resultado = processar_liga(sportmonks, supabase, league_id, league_info, num_temporadas=3)
        
        if resultado:
            global_stats['fixtures'] += resultado['fixtures']
            global_stats['events'] += resultado['events']
            global_stats['stats'] += resultado['stats']
            global_stats['lineups'] += resultado['lineups']
            global_stats['ligas_processadas'] += 1
        else:
            global_stats['ligas_com_erro'] += 1
        
        # Pausa entre ligas para respeitar rate limit
        time.sleep(2)
    
    # ============================================
    # RELATÓRIO FINAL
    # ============================================
    print("\n" + "=" * 80)
    print("✅ EXPANSÃO CONCLUÍDA!")
    print("=" * 80)
    
    print(f"\n📊 ESTATÍSTICAS GLOBAIS:")
    print(f"   • Ligas processadas: {global_stats['ligas_processadas']}/{len(LIGAS_CONFIG)}")
    print(f"   • Fixtures: {global_stats['fixtures']:,}")
    print(f"   • Eventos: {global_stats['events']:,}")
    print(f"   • Estatísticas: {global_stats['stats']:,}")
    print(f"   • Escalações: {global_stats['lineups']:,}")
    
    if global_stats['ligas_com_erro'] > 0:
        print(f"   ⚠️  Ligas com erro: {global_stats['ligas_com_erro']}")
    
    # Verificar totais no banco
    try:
        print(f"\n📊 TOTAIS NO BANCO DE DADOS:")
        
        fixtures = supabase.table('fixtures').select('*', count='exact').execute()
        print(f"   • Total de fixtures: {fixtures.count:,}")
        
        events = supabase.table('match_events').select('*', count='exact').execute()
        print(f"   • Total de eventos: {events.count:,}")
        
        stats = supabase.table('match_statistics').select('*', count='exact').execute()
        print(f"   • Total de estatísticas: {stats.count:,}")
        
        lineups = supabase.table('match_lineups').select('*', count='exact').execute()
        print(f"   • Total de escalações: {lineups.count:,}")
        
        # Contar ligas únicas
        fixtures_data = supabase.table('fixtures').select('league_id').execute()
        if fixtures_data.data:
            unique_leagues = len(set(f['league_id'] for f in fixtures_data.data if f.get('league_id')))
            print(f"   • Ligas com dados: {unique_leagues}")
        
    except Exception as e:
        logger.error(f"Erro ao buscar totais: {e}")
    
    print(f"\n📅 Término: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    print("=" * 80)
    print("🏆 Banco de dados expandido com sucesso!")
    print("=" * 80)

if __name__ == "__main__":
    expandir_ligas()
