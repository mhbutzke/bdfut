#!/usr/bin/env python3
"""
Script COMPLETO - Salva TUDO do Brasileirão 2025
Partidas + Eventos + Estatísticas + Escalações
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
    26: 'goal_var',
    83: 'substitution',
    52: 'injury'
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
    79: 'interceptions',
    81: 'shots_inside_box',
    82: 'shots_outside_box',
    64: 'ball_possession',
    47: 'free_kicks',
    58: 'throw_ins'
}

def create_tables(supabase):
    """Cria as tabelas necessárias se não existirem"""
    print("\n📊 Criando tabelas de detalhes...")
    
    # SQL para criar tabelas
    sql_events = """
    CREATE TABLE IF NOT EXISTS fixture_events (
        id VARCHAR(255) PRIMARY KEY,
        fixture_id BIGINT NOT NULL,
        type_id INT,
        event_type VARCHAR(50),
        minute INT DEFAULT 0,
        extra_minute INT,
        team_id BIGINT,
        player_id BIGINT,
        related_player_id BIGINT,
        player_name VARCHAR(255),
        period_id INT,
        result VARCHAR(50),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    CREATE INDEX IF NOT EXISTS idx_fixture_events_fixture ON fixture_events(fixture_id);
    CREATE INDEX IF NOT EXISTS idx_fixture_events_type ON fixture_events(event_type);
    """
    
    sql_stats = """
    CREATE TABLE IF NOT EXISTS fixture_statistics (
        id SERIAL PRIMARY KEY,
        fixture_id BIGINT NOT NULL,
        team_id BIGINT NOT NULL,
        shots_total INT,
        shots_on_target INT,
        shots_inside_box INT,
        shots_outside_box INT,
        blocked_shots INT,
        corners INT,
        offsides INT,
        ball_possession DECIMAL(5,2),
        possession DECIMAL(5,2),
        yellow_cards INT,
        red_cards INT,
        fouls INT,
        passes_total INT,
        passes_accurate INT,
        pass_percentage DECIMAL(5,2),
        attacks INT,
        dangerous_attacks INT,
        saves INT,
        tackles INT,
        interceptions INT,
        free_kicks INT,
        throw_ins INT,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(fixture_id, team_id)
    );
    CREATE INDEX IF NOT EXISTS idx_fixture_stats_fixture ON fixture_statistics(fixture_id);
    """
    
    sql_lineups = """
    CREATE TABLE IF NOT EXISTS fixture_lineups (
        id SERIAL PRIMARY KEY,
        fixture_id BIGINT NOT NULL,
        team_id BIGINT NOT NULL,
        player_id BIGINT NOT NULL,
        player_name VARCHAR(255),
        type VARCHAR(50) DEFAULT 'lineup',
        position_id INT,
        position_name VARCHAR(50),
        jersey_number INT,
        captain BOOLEAN DEFAULT FALSE,
        minutes_played INT,
        rating DECIMAL(3,1),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(fixture_id, team_id, player_id)
    );
    CREATE INDEX IF NOT EXISTS idx_fixture_lineups_fixture ON fixture_lineups(fixture_id);
    CREATE INDEX IF NOT EXISTS idx_fixture_lineups_player ON fixture_lineups(player_id);
    """
    
    # Executar SQLs (usando RPC ou raw)
    try:
        # Tentar criar via RPC se existir
        supabase.rpc('exec_sql', {'query': sql_events}).execute()
        supabase.rpc('exec_sql', {'query': sql_stats}).execute()
        supabase.rpc('exec_sql', {'query': sql_lineups}).execute()
        print("   ✅ Tabelas criadas via RPC")
    except:
        # Se não funcionar, pelo menos indicar que precisa criar manualmente
        print("   ⚠️  Execute os SQLs no Supabase SQL Editor para criar as tabelas")
        print("   Tabelas necessárias: fixture_events, fixture_statistics, fixture_lineups")
    
    return True

def generate_event_id(fixture_id, type_id, minute, player_id, team_id):
    """Gera ID único para evento"""
    key = f"{fixture_id}-{type_id}-{minute}-{player_id or 0}-{team_id or 0}"
    return hashlib.md5(key.encode()).hexdigest()[:20]

def sync_brasileirao_completo():
    """Sincronização COMPLETA com todos os dados"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 70)
    print("🏆 BRASILEIRÃO 2025 - SINCRONIZAÇÃO COMPLETA")
    print("=" * 70)
    
    LEAGUE_ID = 648
    
    # Criar tabelas se necessário
    create_tables(supabase)
    
    # ============================================
    # 1. BUSCAR LIGA E TEMPORADA
    # ============================================
    print("\n📋 1. Identificando temporada...")
    try:
        league = sportmonks.get_league_by_id(LEAGUE_ID, include='seasons')
        
        # Encontrar temporada 2025
        current_season = None
        for season in league.get('seasons', []):
            if '2025' in str(season.get('name', '')):
                current_season = season
                break
        
        if not current_season:
            print("   ❌ Temporada 2025 não encontrada!")
            return
        
        SEASON_ID = current_season['id']
        print(f"   ✅ {current_season['name']} (ID: {SEASON_ID})")
        
    except Exception as e:
        logger.error(f"Erro: {e}")
        return
    
    # ============================================
    # 2. BUSCAR IDS DAS PARTIDAS
    # ============================================
    print("\n🎮 2. Buscando partidas da temporada...")
    
    season_response = sportmonks._make_request(
        f'/seasons/{SEASON_ID}',
        {'include': 'fixtures'}
    )
    
    season_data = season_response.get('data', {})
    fixtures_list = season_data.get('fixtures', [])
    
    print(f"   ✅ {len(fixtures_list)} partidas encontradas")
    
    if not fixtures_list:
        print("   ❌ Nenhuma partida encontrada")
        return
    
    fixture_ids = [f['id'] for f in fixtures_list if f.get('id')]
    
    # ============================================
    # 3. BUSCAR DETALHES COMPLETOS EM LOTES
    # ============================================
    print("\n💾 3. Buscando dados completos das partidas...")
    
    batch_size = 20
    all_fixtures = []
    
    for i in range(0, len(fixture_ids), batch_size):
        batch_ids = fixture_ids[i:i + batch_size]
        batch_ids_str = ','.join(map(str, batch_ids))
        
        print(f"\n   🔍 Lote {i//batch_size + 1}/{(len(fixture_ids)-1)//batch_size + 1}")
        
        try:
            response = sportmonks._make_request(
                f'/fixtures/multi/{batch_ids_str}',
                {
                    'include': 'participants;scores;state;venue;events.type;statistics.type;lineups.player;referees'
                }
            )
            
            fixtures_data = response.get('data', [])
            print(f"      ✅ {len(fixtures_data)} partidas com dados completos")
            all_fixtures.extend(fixtures_data)
            
            time.sleep(1)  # Rate limit
            
        except Exception as e:
            logger.error(f"Erro no lote: {e}")
            continue
    
    print(f"\n   📊 Total: {len(all_fixtures)} partidas com dados completos")
    
    # ============================================
    # 4. PROCESSAR E SALVAR TUDO
    # ============================================
    print("\n💾 4. Salvando dados completos...")
    
    fixtures_saved = 0
    events_saved = 0
    stats_saved = 0
    lineups_saved = 0
    
    for fixture in all_fixtures:
        try:
            # ========== DADOS DA PARTIDA ==========
            state = fixture.get('state', {})
            status = state.get('state') or state.get('name') or 'NS'
            
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
            
            # Salvar partida
            supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
            fixtures_saved += 1
            
            # ========== EVENTOS ==========
            if fixture.get('events'):
                events_to_save = []
                
                for event in fixture['events']:
                    type_id = event.get('type_id')
                    
                    # Gerar ID único
                    event_id = event.get('id')
                    if not event_id:
                        event_id = generate_event_id(
                            fixture['id'],
                            type_id,
                            event.get('minute', 0),
                            event.get('player_id'),
                            event.get('participant_id')
                        )
                    
                    # Tipo do evento
                    event_type = EVENT_TYPE_MAP.get(type_id)
                    if not event_type and isinstance(event.get('type'), dict):
                        event_type = event['type'].get('name', 'other').lower().replace(' ', '_')
                    if not event_type:
                        event_type = f'type_{type_id}'
                    
                    event_data = {
                        'id': str(event_id),
                        'fixture_id': fixture['id'],
                        'type_id': type_id,
                        'event_type': event_type,
                        'minute': event.get('minute', 0),
                        'extra_minute': event.get('extra_minute'),
                        'team_id': event.get('participant_id'),
                        'player_id': event.get('player_id'),
                        'related_player_id': event.get('related_player_id'),
                        'player_name': event.get('player_name'),
                        'period_id': event.get('period_id'),
                        'result': event.get('result'),
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    events_to_save.append(event_data)
                
                if events_to_save:
                    try:
                        # Salvar em lotes menores
                        for j in range(0, len(events_to_save), 50):
                            batch = events_to_save[j:j+50]
                            supabase.table('fixture_events').upsert(batch, on_conflict='id').execute()
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
                    
                    if team_id not in stats_by_team:
                        stats_by_team[team_id] = {
                            'fixture_id': fixture['id'],
                            'team_id': team_id,
                            'updated_at': datetime.utcnow().isoformat()
                        }
                    
                    # Mapear estatística
                    type_id = stat.get('type_id')
                    value = stat.get('data', {}).get('value') if isinstance(stat.get('data'), dict) else stat.get('data')
                    
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
            
            # ========== ESCALAÇÕES ==========
            if fixture.get('lineups'):
                lineups_to_save = []
                
                for lineup in fixture['lineups']:
                    team_id = lineup.get('team_id') or lineup.get('participant_id')
                    
                    # Lineups podem ter estruturas diferentes
                    players = []
                    
                    # Estrutura 1: array de players
                    if 'players' in lineup and isinstance(lineup['players'], list):
                        players = lineup['players']
                    # Estrutura 2: lineup direto com player_id
                    elif lineup.get('player_id'):
                        players = [lineup]
                    # Estrutura 3: lineup.player é um objeto
                    elif isinstance(lineup.get('player'), dict):
                        player_data = lineup['player']
                        player_data['player_id'] = player_data.get('id', lineup.get('player_id'))
                        players = [player_data]
                    
                    for player in players:
                        player_id = player.get('player_id') or player.get('id')
                        if not player_id:
                            continue
                        
                        # Nome do jogador
                        player_name = None
                        if isinstance(player.get('player'), dict):
                            player_name = player['player'].get('name')
                        if not player_name:
                            player_name = player.get('player_name') or player.get('name')
                        
                        # Posição
                        position_name = None
                        position_id = None
                        if isinstance(player.get('position'), dict):
                            position_name = player['position'].get('name')
                            position_id = player['position'].get('id')
                        else:
                            position_id = player.get('position_id')
                            position_name = player.get('position_name')
                        
                        lineup_data = {
                            'fixture_id': fixture['id'],
                            'team_id': team_id,
                            'player_id': player_id,
                            'player_name': player_name,
                            'type': lineup.get('type', {}).get('name', 'lineup') if isinstance(lineup.get('type'), dict) else 'lineup',
                            'position_id': position_id,
                            'position_name': position_name,
                            'jersey_number': player.get('jersey_number') or player.get('number'),
                            'captain': bool(player.get('captain')),
                            'minutes_played': player.get('minutes_played'),
                            'rating': player.get('rating'),
                            'updated_at': datetime.utcnow().isoformat()
                        }
                        lineups_to_save.append(lineup_data)
                
                if lineups_to_save:
                    try:
                        # Salvar em lotes
                        for j in range(0, len(lineups_to_save), 50):
                            batch = lineups_to_save[j:j+50]
                            for lineup in batch:
                                try:
                                    supabase.table('fixture_lineups').upsert(
                                        lineup,
                                        on_conflict='fixture_id,team_id,player_id'
                                    ).execute()
                                except:
                                    pass  # Ignorar duplicatas
                        lineups_saved += len(lineups_to_save)
                    except Exception as e:
                        logger.debug(f"Erro ao salvar lineups: {e}")
            
            # Progresso
            if fixtures_saved % 50 == 0:
                print(f"   Processadas {fixtures_saved}/{len(all_fixtures)} partidas...")
            
        except Exception as e:
            logger.error(f"Erro ao processar partida {fixture.get('id')}: {e}")
    
    # ============================================
    # 5. RELATÓRIO FINAL
    # ============================================
    print("\n" + "=" * 70)
    print("✅ SINCRONIZAÇÃO COMPLETA FINALIZADA!")
    print("=" * 70)
    
    print(f"\n📊 DADOS SALVOS:")
    print(f"   • Partidas: {fixtures_saved}")
    print(f"   • Eventos: {events_saved}")
    print(f"   • Estatísticas: {stats_saved}")
    print(f"   • Escalações: {lineups_saved}")
    
    # Verificar totais no banco
    try:
        fixtures_count = supabase.table('fixtures').select('*', count='exact').execute()
        events_count = supabase.table('fixture_events').select('*', count='exact').execute()
        stats_count = supabase.table('fixture_statistics').select('*', count='exact').execute()
        lineups_count = supabase.table('fixture_lineups').select('*', count='exact').execute()
        
        print(f"\n📊 TOTAIS NO BANCO:")
        print(f"   • Partidas: {fixtures_count.count}")
        print(f"   • Eventos: {events_count.count if hasattr(events_count, 'count') else '?'}")
        print(f"   • Estatísticas: {stats_count.count if hasattr(stats_count, 'count') else '?'}")
        print(f"   • Escalações: {lineups_count.count if hasattr(lineups_count, 'count') else '?'}")
        
        # Amostra de eventos
        try:
            sample_events = supabase.table('fixture_events').select('event_type').limit(100).execute()
            if sample_events.data:
                event_types = {}
                for e in sample_events.data:
                    t = e.get('event_type', 'unknown')
                    event_types[t] = event_types.get(t, 0) + 1
                
                print(f"\n🎯 TIPOS DE EVENTOS (amostra):")
                for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"   • {event_type}: {count}")
        except:
            pass
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
    
    print("\n✅ Dados completos do Brasileirão 2025 salvos com sucesso!")
    print("=" * 70)

if __name__ == "__main__":
    sync_brasileirao_completo()
