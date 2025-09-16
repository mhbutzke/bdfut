#!/usr/bin/env python3
"""
PASSO 3: Enriquecer fixtures com events, statistics e lineups
Coleta dados detalhados para todas as fixtures já salvas no banco
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Any

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.sportmonks_client import SportmonksClient
from supabase import create_client
from config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Função principal para enriquecer fixtures com dados detalhados"""
    
    logger.info("=" * 80)
    logger.info("🚀 PASSO 3: ENRIQUECENDO FIXTURES COM EVENTS, STATISTICS E LINEUPS")
    logger.info("=" * 80)
    
    # Inicializar clientes
    try:
        config = Config()
        sportmonks = SportmonksClient()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Clientes inicializados com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar clientes: {e}")
        return
    
    # Buscar fixtures que precisam ser enriquecidas
    logger.info("🔍 Buscando fixtures para enriquecer...")
    
    try:
        # Buscar fixtures que ainda não têm events/statistics/lineups
        fixtures_response = supabase.table('fixtures').select(
            'sportmonks_id,league_id,season_id,match_date'
        ).execute()
        
        fixtures = fixtures_response.data
        logger.info(f"📊 Total de fixtures encontradas: {len(fixtures)}")
        
        if not fixtures:
            logger.warning("⚠️ Nenhuma fixture encontrada para enriquecer")
            return
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar fixtures: {e}")
        return
    
    # Processar fixtures em lotes
    batch_size = 25  # Sportmonks permite até 25 IDs por chamada
    total_processed = 0
    total_events = 0
    total_statistics = 0
    total_lineups = 0
    
    start_time = time.time()
    
    for i in range(0, len(fixtures), batch_size):
        batch = fixtures[i:i + batch_size]
        fixture_ids = [str(f['sportmonks_id']) for f in batch]
        
        logger.info(f"📦 Processando lote {i//batch_size + 1}/{(len(fixtures) + batch_size - 1)//batch_size} ({len(batch)} fixtures)")
        
        try:
            # Buscar dados detalhados da Sportmonks
            ids_str = ','.join(fixture_ids)
            response = sportmonks._make_request(
                f'/fixtures/multi/{ids_str}',
                {'include': 'events;statistics;lineups'}
            )
            detailed_fixtures = response.get('data', [])
            
            if not detailed_fixtures:
                logger.warning(f"⚠️ Nenhum dado detalhado encontrado para lote {i//batch_size + 1}")
                continue
            
            # Processar cada fixture
            for fixture in detailed_fixtures:
                fixture_id = fixture.get('id')
                if not fixture_id:
                    continue
                
                # Salvar events
                events_count = save_events(supabase, fixture)
                total_events += events_count
                
                # Salvar statistics
                stats_count = save_statistics(supabase, fixture)
                total_statistics += stats_count
                
                # Salvar lineups
                lineups_count = save_lineups(supabase, fixture)
                total_lineups += lineups_count
                
                total_processed += 1
            
            logger.info(f"   ✅ {len(batch)} fixtures processadas")
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar lote {i//batch_size + 1}: {e}")
            continue
    
    # Relatório final
    elapsed_time = time.time() - start_time
    logger.info("=" * 80)
    logger.info("📊 STATUS FINAL")
    logger.info("=" * 80)
    logger.info(f"   • Fixtures processadas: {total_processed}")
    logger.info(f"   • Events salvos: {total_events}")
    logger.info(f"   • Statistics salvas: {total_statistics}")
    logger.info(f"   • Lineups salvos: {total_lineups}")
    logger.info(f"   • Tempo total: {elapsed_time:.0f}s")
    
    logger.info("=" * 80)
    logger.info("✅ ENRIQUECIMENTO DE FIXTURES CONCLUÍDO!")
    logger.info("=" * 80)
    logger.info("🎯 PRÓXIMO PASSO:")
    logger.info("   → Execute: python3 04_popular_venues_referees.py")
    logger.info("   Para popular tabelas venues e referees")
    logger.info("=" * 80)

def save_events(supabase, fixture: Dict[str, Any]) -> int:
    """Salva events de uma fixture"""
    events = fixture.get('events', [])
    if not events:
        return 0
    
    events_to_save = []
    for event in events:
        event_data = {
            'id': event.get('id') or f"{fixture['id']}-{event.get('type_id')}-{event.get('minute',0)}-{event.get('player_id')}-{event.get('participant_id')}",
            'fixture_id': fixture['id'],
            'type_id': event.get('type_id'),
            'event_type': map_event_type(event.get('type_id')),
            'minute': event.get('minute', 0),
            'extra_minute': event.get('extra_minute'),
            'team_id': event.get('participant_id'),
            'player_id': event.get('player_id'),
            'related_player_id': event.get('related_player_id'),
            'player_name': (event.get('player') or {}).get('name') if event.get('player') else None,
            'period_id': event.get('period_id'),
            'result': event.get('result'),
            'created_at': datetime.utcnow().isoformat()
        }
        events_to_save.append(event_data)
    
    if events_to_save:
        try:
            supabase.table('match_events').upsert(events_to_save, on_conflict='id').execute()
            return len(events_to_save)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar events: {e}")
            return 0
    
    return 0

def save_statistics(supabase, fixture: Dict[str, Any]) -> int:
    """Salva statistics de uma fixture"""
    statistics = fixture.get('statistics', [])
    if not statistics:
        return 0
    
    stats_by_team = {}
    for stat in statistics:
        team_id = stat.get('participant_id')
        if not team_id:
            continue
        
        if team_id not in stats_by_team:
            stats_by_team[team_id] = {
                'fixture_id': fixture['id'],
                'team_id': team_id,
                'created_at': datetime.utcnow().isoformat()
            }
        
        # Mapear estatísticas específicas
        stat_type = stat.get('type_id')
        value = (stat.get('data') or {}).get('value')
        
        if stat_type == 42:  # Shots Total
            stats_by_team[team_id]['shots_total'] = value
        elif stat_type == 80:  # Shots on Target
            stats_by_team[team_id]['shots_on_target'] = value
        elif stat_type == 34:  # Corners
            stats_by_team[team_id]['corners'] = value
        elif stat_type == 84:  # Yellow Cards
            stats_by_team[team_id]['yellow_cards'] = value
        elif stat_type == 83:  # Red Cards
            stats_by_team[team_id]['red_cards'] = value
        elif stat_type == 88:  # Fouls
            stats_by_team[team_id]['fouls'] = value
        elif stat_type == 85:  # Offsides
            stats_by_team[team_id]['offsides'] = value
        elif stat_type == 45:  # Possession
            stats_by_team[team_id]['ball_possession'] = value
    
    if stats_by_team:
        try:
            stats_rows = list(stats_by_team.values())
            supabase.table('match_statistics').upsert(stats_rows, on_conflict='fixture_id,team_id').execute()
            return len(stats_rows)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar statistics: {e}")
            return 0
    
    return 0

def save_lineups(supabase, fixture: Dict[str, Any]) -> int:
    """Salva lineups de uma fixture"""
    lineups = fixture.get('lineups', [])
    if not lineups:
        return 0
    
    lineups_to_save = []
    for lineup in lineups:
        team_id = lineup.get('participant_id') or lineup.get('team_id')
        players = lineup.get('players', [])
        
        for player in players:
            lineup_data = {
                'id': f"{fixture['id']}-{team_id}-{player.get('player_id')}",
                'fixture_id': fixture['id'],
                'team_id': team_id,
                'player_id': player.get('player_id'),
                'player_name': (player.get('player') or {}).get('name') or player.get('player_name'),
                'type': (lineup.get('type') or {}).get('name') or 'lineup',
                'position_id': player.get('position_id') or (player.get('position') or {}).get('id'),
                'position_name': (player.get('position') or {}).get('name'),
                'jersey_number': player.get('number') or player.get('jersey_number'),
                'captain': bool(player.get('captain')),
                'created_at': datetime.utcnow().isoformat()
            }
            lineups_to_save.append(lineup_data)
    
    if lineups_to_save:
        try:
            supabase.table('match_lineups').upsert(lineups_to_save, on_conflict='id').execute()
            return len(lineups_to_save)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar lineups: {e}")
            return 0
    
    return 0

def map_event_type(type_id: int) -> str:
    """Mapeia type_id para nome do evento"""
    event_map = {
        14: 'goal',
        15: 'penalty_goal',
        16: 'penalty_missed',
        17: 'own_goal',
        19: 'yellow_card',
        20: 'red_card',
        83: 'substitution'
    }
    return event_map.get(type_id, 'other')

if __name__ == "__main__":
    main()
