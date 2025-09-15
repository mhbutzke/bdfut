#!/usr/bin/env python3
"""
Script FINAL para salvar TODOS os dados do Brasileirão nas tabelas
Eventos + Estatísticas + Escalações
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
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

# Mapeamento de estatísticas
STAT_TYPE_MAP = {
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

def generate_event_id(fixture_id, type_id, minute, player_id, team_id, index=0):
    """Gera ID único para evento"""
    key = f"{fixture_id}-{type_id}-{minute}-{player_id or 0}-{team_id or 0}-{index}"
    return hashlib.md5(key.encode()).hexdigest()[:20]

def salvar_dados_completos():
    """Salva todos os dados nas tabelas criadas"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 70)
    print("💾 SALVANDO DADOS COMPLETOS DO BRASILEIRÃO 2025")
    print("=" * 70)
    
    # ============================================
    # 1. BUSCAR FIXTURES DO BRASILEIRÃO
    # ============================================
    print("\n📋 1. Buscando fixtures do Brasileirão...")
    
    try:
        fixtures_db = supabase.table('fixtures').select('sportmonks_id').eq('league_id', 648).execute()
        fixture_ids = [f['sportmonks_id'] for f in fixtures_db.data if f.get('sportmonks_id')]
        
        print(f"   ✅ {len(fixture_ids)} fixtures encontradas")
        
        if not fixture_ids:
            print("   ❌ Nenhuma fixture encontrada!")
            return
            
    except Exception as e:
        logger.error(f"Erro ao buscar fixtures: {e}")
        return
    
    # ============================================
    # 2. PROCESSAR E SALVAR DADOS
    # ============================================
    print("\n💾 2. Processando e salvando dados...")
    
    includes = 'participants;scores;state;events;statistics;lineups;referees'
    
    batch_size = 20
    total_events_saved = 0
    total_stats_saved = 0
    total_lineups_saved = 0
    
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
            
            # Processar cada fixture
            for fixture in fixtures_data:
                fixture_id = fixture.get('id')
                
                # ========== SALVAR EVENTOS ==========
                if fixture.get('events'):
                    events_to_save = []
                    event_index = {}
                    
                    for event in fixture['events']:
                        type_id = event.get('type_id')
                        minute = event.get('minute', 0)
                        team_id = event.get('participant_id')
                        player_id = event.get('player_id')
                        
                        # Criar chave para contar eventos duplicados
                        event_key = f"{type_id}-{minute}-{player_id}-{team_id}"
                        event_index[event_key] = event_index.get(event_key, 0) + 1
                        
                        # Gerar ID único
                        event_id = event.get('id')
                        if not event_id:
                            event_id = generate_event_id(
                                fixture_id, type_id, minute, 
                                player_id, team_id, event_index[event_key]
                            )
                        
                        # Tipo do evento
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
                    
                    # Salvar eventos em lote
                    if events_to_save:
                        try:
                            for j in range(0, len(events_to_save), 50):
                                batch = events_to_save[j:j+50]
                                supabase.table('match_events').upsert(batch, on_conflict='id').execute()
                            total_events_saved += len(events_to_save)
                        except Exception as e:
                            logger.debug(f"Erro ao salvar eventos: {e}")
                
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
                        
                        # Extrair valor
                        if isinstance(stat.get('data'), dict):
                            value = stat['data'].get('value')
                        elif stat.get('data') is not None:
                            value = stat.get('data')
                        
                        # Mapear estatística
                        if type_id == 42:
                            stats_by_team[team_id]['shots_total'] = value
                        elif type_id == 80:
                            stats_by_team[team_id]['shots_on_target'] = value
                        elif type_id == 34:
                            stats_by_team[team_id]['corners'] = value
                        elif type_id == 84:
                            stats_by_team[team_id]['yellow_cards'] = value
                        elif type_id == 83:
                            stats_by_team[team_id]['red_cards'] = value
                        elif type_id == 88:
                            stats_by_team[team_id]['fouls'] = value
                        elif type_id == 85:
                            stats_by_team[team_id]['offsides'] = value
                        elif type_id == 45:
                            stats_by_team[team_id]['ball_possession'] = value
                        elif type_id == 52:
                            stats_by_team[team_id]['passes_total'] = value
                        elif type_id == 53:
                            stats_by_team[team_id]['passes_accurate'] = value
                        elif type_id == 54:
                            stats_by_team[team_id]['pass_percentage'] = value
                        elif type_id == 86:
                            stats_by_team[team_id]['saves'] = value
                        elif type_id == 214:
                            stats_by_team[team_id]['tackles'] = value
                        elif type_id == 79:
                            stats_by_team[team_id]['interceptions'] = value
                        elif type_id == 81:
                            stats_by_team[team_id]['shots_inside_box'] = value
                        elif type_id == 82:
                            stats_by_team[team_id]['shots_outside_box'] = value
                        elif type_id == 78:
                            stats_by_team[team_id]['blocked_shots'] = value
                    
                    # Salvar estatísticas
                    if stats_by_team:
                        try:
                            for team_stats in stats_by_team.values():
                                supabase.table('match_statistics').upsert(
                                    team_stats,
                                    on_conflict='fixture_id,team_id'
                                ).execute()
                            total_stats_saved += len(stats_by_team)
                        except Exception as e:
                            logger.debug(f"Erro ao salvar estatísticas: {e}")
                
                # ========== SALVAR ESCALAÇÕES ==========
                if fixture.get('lineups'):
                    lineups_to_save = []
                    
                    for lineup in fixture['lineups']:
                        team_id = lineup.get('team_id') or lineup.get('participant_id')
                        player_id = lineup.get('player_id')
                        
                        if not player_id or not team_id:
                            continue
                        
                        # Nome do jogador
                        player_name = None
                        if isinstance(lineup.get('player'), dict):
                            player_name = lineup['player'].get('name')
                        if not player_name:
                            player_name = lineup.get('player_name')
                        
                        # Posição
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
                            for j in range(0, len(lineups_to_save), 50):
                                batch = lineups_to_save[j:j+50]
                                for lineup in batch:
                                    try:
                                        supabase.table('match_lineups').upsert(
                                            lineup,
                                            on_conflict='fixture_id,team_id,player_id'
                                        ).execute()
                                        total_lineups_saved += 1
                                    except:
                                        pass  # Ignorar duplicatas
                        except Exception as e:
                            logger.debug(f"Erro ao salvar escalações: {e}")
            
            print(f"      ✅ Lote processado - Eventos: {total_events_saved}, Stats: {total_stats_saved}, Lineups: {total_lineups_saved}")
            
            # Rate limit
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Erro no lote: {e}")
            continue
    
    # ============================================
    # 3. RELATÓRIO FINAL
    # ============================================
    print("\n" + "=" * 70)
    print("✅ DADOS SALVOS COM SUCESSO!")
    print("=" * 70)
    
    print(f"\n📊 RESUMO DO SALVAMENTO:")
    print(f"   • Eventos salvos: {total_events_saved:,}")
    print(f"   • Estatísticas salvas: {total_stats_saved:,}")
    print(f"   • Escalações salvas: {total_lineups_saved:,}")
    
    # Verificar totais no banco
    try:
        events = supabase.table('match_events').select('*', count='exact').execute()
        stats = supabase.table('match_statistics').select('*', count='exact').execute()
        lineups = supabase.table('match_lineups').select('*', count='exact').execute()
        
        print(f"\n📊 TOTAIS NO BANCO:")
        print(f"   • Total de eventos: {events.count:,}")
        print(f"   • Total de estatísticas: {stats.count:,}")
        print(f"   • Total de escalações: {lineups.count:,}")
        
        # Amostra de eventos
        sample_events = supabase.table('match_events').select('event_type').limit(100).execute()
        if sample_events.data:
            event_types = {}
            for e in sample_events.data:
                t = e.get('event_type', 'unknown')
                event_types[t] = event_types.get(t, 0) + 1
            
            print(f"\n🎯 TIPOS DE EVENTOS SALVOS:")
            for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   • {event_type}: {count}")
        
    except Exception as e:
        logger.error(f"Erro ao buscar totais: {e}")
    
    print("\n✅ Banco de dados populado com sucesso!")
    print("🏆 Brasileirão 2025 - Dados completos disponíveis!")
    print("=" * 70)

if __name__ == "__main__":
    salvar_dados_completos()
