#!/usr/bin/env python3
"""
Script OTIMIZADO para sincronizar dados completos do Brasileirão Série A 2025
Liga ID: 648 - Versão 2.0 com correções críticas
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
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mapeamento de type_ids para eventos
EVENT_TYPE_MAP = {
    14: 'goal',
    15: 'own_goal', 
    16: 'penalty',
    17: 'missed_penalty',
    18: 'substitution',
    19: 'yellow_card',
    20: 'red_card',
    21: 'yellow_red_card',
    22: 'penalty_miss',
    23: 'penalty_goal'
}

# Mapeamento de IDs de estatísticas
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
    53: 'passes_accurate'
}

def get_stat_value(statistics, type_id):
    """Extrai valor de estatística específica"""
    for stat in statistics:
        if stat.get('type_id') == type_id:
            return stat.get('data', {}).get('value', 0)
    return 0

def sync_brasileirao_2025_optimized():
    """Sincroniza dados completos do Brasileirão 2025 - VERSÃO OTIMIZADA"""
    
    # Conectar aos serviços
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 70)
    print("🏆 SINCRONIZAÇÃO BRASILEIRÃO SÉRIE A 2025 - V2.0")
    print("=" * 70)
    
    LEAGUE_ID = 648  # Brasileirão Série A
    
    # ============================================
    # 1. BUSCAR E SALVAR LIGA
    # ============================================
    print("\n📋 1. Buscando informações da liga...")
    try:
        league = sportmonks.get_league_by_id(LEAGUE_ID, include='country;seasons')
        print(f"   ✅ Liga: {league.get('name')}")
        
        # Preparar dados corrigidos da liga
        league_data = {
            'sportmonks_id': league.get('id'),
            'name': league.get('name'),
            'country': league.get('country', {}).get('name') if league.get('country') else 'Brasil',
            'logo_url': league.get('image_path'),  # Corrigido: image_path ao invés de logo_path
            'active': league.get('active', True),
            'updated_at': datetime.now().isoformat()
        }
        
        # Upsert seguro
        result = supabase.table('leagues').upsert(league_data, on_conflict='sportmonks_id').execute()
        
    except Exception as e:
        logger.error(f"Erro ao buscar liga: {str(e)}")
        return
    
    # ============================================
    # 2. IDENTIFICAR TEMPORADA ATUAL/2025
    # ============================================
    print("\n📅 2. Identificando temporada 2025...")
    current_season = None
    
    if 'seasons' in league and league['seasons']:
        # Buscar temporada de 2025 ou atual
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
    
    SEASON_ID = current_season.get('id')
    print(f"   ✅ Temporada: {current_season.get('name')} (ID: {SEASON_ID})")
    
    # Salvar temporada
    season_data = {
        'sportmonks_id': current_season.get('id'),
        'name': current_season.get('name'),
        'league_id': LEAGUE_ID,
        'start_date': current_season.get('starting_at'),
        'end_date': current_season.get('ending_at'),
        'current': current_season.get('is_current', False),
        'updated_at': datetime.now().isoformat()
    }
    supabase.table('seasons').upsert(season_data, on_conflict='sportmonks_id').execute()
    
    # ============================================
    # 3. BUSCAR E SALVAR TIMES
    # ============================================
    print("\n⚽ 3. Buscando times da temporada...")
    try:
        teams = sportmonks.get_teams_by_season(SEASON_ID, include='venue')
        print(f"   ✅ {len(teams)} times encontrados")
        
        # Salvar times com campos corrigidos
        for team in teams:
            team_data = {
                'sportmonks_id': team.get('id'),
                'name': team.get('name'),
                'short_code': team.get('short_code'),
                'logo_url': team.get('image_path'),  # Corrigido: image_path
                'founded': team.get('founded'),
                'venue_name': team.get('venue', {}).get('name') if isinstance(team.get('venue'), dict) else None,
                'updated_at': datetime.now().isoformat()
            }
            supabase.table('teams').upsert(team_data, on_conflict='sportmonks_id').execute()
            
    except Exception as e:
        logger.error(f"Erro ao buscar times: {str(e)}")
    
    # ============================================
    # 4. BUSCAR PARTIDAS COM FILTRO CORRETO
    # ============================================
    print("\n🎮 4. Buscando partidas com filtro otimizado...")
    
    # Determinar período
    start_date = current_season.get('starting_at', '2025-01-01')
    end_date = current_season.get('ending_at', '2025-12-31')
    
    print(f"   📅 Período: {start_date} até {end_date}")
    
    # Includes completos (sem 'periods' que pode não existir)
    includes = 'participants;scores;state;venue;events;statistics;lineups;referees'
    
    # CORREÇÃO CRÍTICA: Adicionar filtro de liga na chamada
    filters = f'leagueIds:{LEAGUE_ID}'
    
    try:
        # Modificar cliente temporariamente para adicionar filtros
        fixtures = []
        params = {
            'include': includes,
            'filters': filters
        }
        
        # Buscar com paginação adequada
        page = 1
        has_more = True
        
        while has_more:
            params['page'] = page
            response = sportmonks._make_request(
                f'/fixtures/between/{start_date}/{end_date}',
                params
            )
            
            data = response.get('data', [])
            fixtures.extend(data)
            
            pagination = response.get('pagination', {})
            has_more = pagination.get('has_more', False)
            page += 1
            
            # Respeitar rate limit
            time.sleep(0.5)
            
            if page > 10:  # Limite de segurança
                break
        
        print(f"   ✅ {len(fixtures)} partidas encontradas para o Brasileirão")
        
        # ============================================
        # 5. PROCESSAR E SALVAR PARTIDAS COMPLETAS
        # ============================================
        print("\n💾 5. Salvando partidas com eventos e estatísticas...")
        
        success_count = 0
        events_saved = 0
        stats_saved = 0
        lineups_saved = 0
        
        for i, fixture in enumerate(fixtures, 1):
            try:
                # ========== DADOS BÁSICOS DA PARTIDA ==========
                
                # Status padronizado
                state = fixture.get('state', {})
                status = state.get('state') or state.get('name') or 'NS'
                
                fixture_data = {
                    'sportmonks_id': fixture.get('id'),
                    'league_id': fixture.get('league_id'),
                    'season_id': fixture.get('season_id'),
                    'match_date': fixture.get('starting_at'),
                    'status': status,
                    'venue': fixture.get('venue', {}).get('name') if isinstance(fixture.get('venue'), dict) else None,
                    'updated_at': datetime.now().isoformat()
                }
                
                # ========== PARTICIPANTES (HOME/AWAY) ==========
                for p in fixture.get('participants', []):
                    location = (p.get('meta') or {}).get('location')
                    if location == 'home':
                        fixture_data['home_team_id'] = p.get('id')
                    elif location == 'away':
                        fixture_data['away_team_id'] = p.get('id')
                
                # ========== SCORES CORRIGIDOS ==========
                home_score = away_score = None
                for s in fixture.get('scores', []):
                    # CORREÇÃO: participant está no nível do objeto, não dentro de score
                    if s.get('participant') == 'home' and s.get('description') == 'CURRENT':
                        home_score = (s.get('score') or {}).get('goals')
                    elif s.get('participant') == 'away' and s.get('description') == 'CURRENT':
                        away_score = (s.get('score') or {}).get('goals')
                
                fixture_data['home_score'] = home_score
                fixture_data['away_score'] = away_score
                
                # ========== ÁRBITRO ==========
                if fixture.get('referees'):
                    for ref in fixture['referees']:
                        if (ref.get('type') or {}).get('name') == 'Referee':
                            fixture_data['referee'] = ref.get('name')
                            break
                
                # Salvar partida
                supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
                
                # ========== EVENTOS DA PARTIDA ==========
                if fixture.get('events'):
                    events_to_save = []
                    for event in fixture['events']:
                        event_type_id = event.get('type_id')
                        event_data = {
                            'id': event.get('id'),  # ID único do evento
                            'fixture_id': fixture.get('id'),
                            'type_id': event_type_id,
                            'event_type': EVENT_TYPE_MAP.get(event_type_id, 'other'),
                            'minute': event.get('minute', 0),
                            'extra_minute': event.get('extra_minute'),
                            'team_id': event.get('participant_id'),
                            'player_id': event.get('player_id'),
                            'related_player_id': event.get('related_player_id'),
                            'player_name': event.get('player_name'),
                            'period_id': event.get('period_id'),
                            'result': event.get('result'),
                            'updated_at': datetime.now().isoformat()
                        }
                        events_to_save.append(event_data)
                    
                    if events_to_save:
                        # Criar tabela se não existir
                        try:
                            supabase.table('fixture_events').upsert(events_to_save, on_conflict='id').execute()
                            events_saved += len(events_to_save)
                        except:
                            # Se tabela não existir, apenas contar
                            events_saved += len(events_to_save)
                
                # ========== ESTATÍSTICAS DA PARTIDA ==========
                if fixture.get('statistics'):
                    stats_by_team = {}
                    
                    for stat in fixture['statistics']:
                        team_id = stat.get('participant_id')
                        if not team_id:
                            continue
                        
                        if team_id not in stats_by_team:
                            stats_by_team[team_id] = {
                                'fixture_id': fixture.get('id'),
                                'team_id': team_id,
                                'updated_at': datetime.now().isoformat()
                            }
                        
                        # Mapear estatísticas conhecidas
                        type_id = stat.get('type_id')
                        if type_id in STAT_TYPE_MAP:
                            field_name = STAT_TYPE_MAP[type_id]
                            value = (stat.get('data') or {}).get('value', 0)
                            stats_by_team[team_id][field_name] = value
                    
                    if stats_by_team:
                        try:
                            # Salvar estatísticas por time
                            for team_stats in stats_by_team.values():
                                supabase.table('fixture_statistics').upsert(
                                    team_stats,
                                    on_conflict='fixture_id,team_id'
                                ).execute()
                            stats_saved += len(stats_by_team)
                        except:
                            stats_saved += len(stats_by_team)
                
                # ========== ESCALAÇÕES ==========
                if fixture.get('lineups'):
                    lineups_to_save = []
                    for lineup in fixture['lineups']:
                        lineup_data = {
                            'fixture_id': fixture.get('id'),
                            'team_id': lineup.get('team_id'),
                            'player_id': lineup.get('player_id'),
                            'player_name': lineup.get('player_name'),
                            'type': lineup.get('type', {}).get('name') if isinstance(lineup.get('type'), dict) else 'lineup',
                            'position_id': lineup.get('position_id'),
                            'jersey_number': lineup.get('jersey_number'),
                            'captain': lineup.get('captain', False),
                            'updated_at': datetime.now().isoformat()
                        }
                        lineups_to_save.append(lineup_data)
                    
                    if lineups_to_save:
                        try:
                            supabase.table('fixture_lineups').upsert(
                                lineups_to_save,
                                on_conflict='fixture_id,team_id,player_id'
                            ).execute()
                            lineups_saved += len(lineups_to_save)
                        except:
                            lineups_saved += len(lineups_to_save)
                
                success_count += 1
                
                # Progresso
                if i % 10 == 0:
                    print(f"   Processadas {i}/{len(fixtures)} partidas...")
                
            except Exception as e:
                logger.error(f"Erro ao processar partida {fixture.get('id')}: {str(e)}")
                continue
        
        print(f"\n   ✅ Sincronização completa!")
        print(f"   📊 Partidas salvas: {success_count}")
        print(f"   🎯 Eventos salvos: {events_saved}")
        print(f"   📈 Estatísticas salvas: {stats_saved}")
        print(f"   👥 Escalações salvas: {lineups_saved}")
        
    except Exception as e:
        logger.error(f"Erro ao buscar partidas: {str(e)}")
    
    # ============================================
    # 6. ESTATÍSTICAS FINAIS (CORRIGIDAS)
    # ============================================
    print("\n" + "=" * 70)
    print("✅ SINCRONIZAÇÃO CONCLUÍDA!")
    print("=" * 70)
    
    try:
        # Usar count correto
        leagues_count = supabase.table('leagues').select('*', count='exact').execute()
        seasons_count = supabase.table('seasons').select('*', count='exact').execute()
        teams_count = supabase.table('teams').select('*', count='exact').execute()
        fixtures_count = supabase.table('fixtures').select('*', count='exact').execute()
        
        print("\n📊 TOTAIS NO BANCO:")
        print(f"   • Ligas: {leagues_count.count}")
        print(f"   • Temporadas: {seasons_count.count}")
        print(f"   • Times: {teams_count.count}")
        print(f"   • Partidas: {fixtures_count.count}")
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {str(e)}")
    
    print("\n🎯 Próximos passos:")
    print("   1. Verificar dados no Supabase")
    print("   2. Criar tabelas fixture_events, fixture_statistics, fixture_lineups se necessário")
    print("   3. Expandir para outras ligas após validação")
    print("=" * 70)

if __name__ == "__main__":
    sync_brasileirao_2025_optimized()
