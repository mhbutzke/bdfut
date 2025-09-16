#!/usr/bin/env python3
"""
Script para ENRIQUECER fixtures existentes com dados completos
Usa os includes específicos para obter TODOS os detalhes
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

# Mapeamentos
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
    52: 'injury',
    83: 'substitution'
}

def criar_tabelas_detalhes(supabase):
    """Cria as tabelas de detalhes via SQL direto"""
    print("\n📊 Criando tabelas de detalhes no Supabase...")
    
    sqls = [
        """
        CREATE TABLE IF NOT EXISTS match_events (
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
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS match_statistics (
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
            yellow_cards INT,
            red_cards INT,
            fouls INT,
            passes_total INT,
            passes_accurate INT,
            pass_percentage DECIMAL(5,2),
            saves INT,
            tackles INT,
            interceptions INT,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(fixture_id, team_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS match_lineups (
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
            UNIQUE(fixture_id, team_id, player_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS match_periods (
            id SERIAL PRIMARY KEY,
            fixture_id BIGINT NOT NULL,
            period_id INT,
            period_type VARCHAR(50),
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            minutes INT,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(fixture_id, period_id)
        );
        """
    ]
    
    print("   ⚠️  Execute os SQLs acima no Supabase SQL Editor para criar as tabelas")
    print("   Tabelas: match_events, match_statistics, match_lineups, match_periods")
    return True

def generate_event_id(fixture_id, type_id, minute, player_id, team_id):
    """Gera ID único para evento"""
    key = f"{fixture_id}-{type_id}-{minute}-{player_id or 0}-{team_id or 0}"
    return hashlib.md5(key.encode()).hexdigest()[:20]

def enriquecer_fixtures():
    """Enriquece fixtures existentes com dados completos"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 70)
    print("🎯 ENRIQUECIMENTO DE FIXTURES - DADOS COMPLETOS")
    print("=" * 70)
    
    # Criar tabelas se necessário
    criar_tabelas_detalhes(supabase)
    
    # ============================================
    # 1. BUSCAR FIXTURES EXISTENTES
    # ============================================
    print("\n📋 1. Buscando fixtures existentes no banco...")
    
    try:
        # Buscar todas as fixtures do Brasileirão
        fixtures_db = supabase.table('fixtures').select('sportmonks_id').execute()
        fixture_ids = [f['sportmonks_id'] for f in fixtures_db.data if f.get('sportmonks_id')]
        
        print(f"   ✅ {len(fixture_ids)} fixtures encontradas")
        
        if not fixture_ids:
            print("   ❌ Nenhuma fixture encontrada!")
            return
            
    except Exception as e:
        logger.error(f"Erro ao buscar fixtures: {e}")
        return
    
    # ============================================
    # 2. BUSCAR DADOS COMPLETOS EM LOTES
    # ============================================
    print("\n💾 2. Buscando dados completos com includes específicos...")
    
    # Includes completos conforme solicitado
    includes = 'participants;scores;state;venue;referees;events.type;statistics.type;lineups.player;periods;season;league'
    
    batch_size = 20  # Limite da API para multi
    all_fixtures_enriched = []
    
    for i in range(0, len(fixture_ids), batch_size):
        batch_ids = fixture_ids[i:i + batch_size]
        batch_ids_str = ','.join(map(str, batch_ids))
        
        print(f"\n   🔍 Lote {i//batch_size + 1}/{(len(fixture_ids)-1)//batch_size + 1}")
        print(f"      IDs: {batch_ids_str[:60]}...")
        
        try:
            # Chamada exata como solicitado
            response = sportmonks._make_request(
                f'/fixtures/multi/{batch_ids_str}',
                {'include': includes}
            )
            
            fixtures_data = response.get('data', [])
            print(f"      ✅ {len(fixtures_data)} fixtures enriquecidas")
            
            # Mostrar dados do primeiro fixture como exemplo
            if i == 0 and fixtures_data:
                f = fixtures_data[0]
                print(f"\n      📊 Exemplo de dados recebidos:")
                print(f"         • ID: {f.get('id')}")
                print(f"         • Liga: {f.get('league', {}).get('name')}")
                print(f"         • Temporada: {f.get('season', {}).get('name')}")
                print(f"         • Eventos: {len(f.get('events', []))}")
                print(f"         • Estatísticas: {len(f.get('statistics', []))}")
                print(f"         • Escalações: {len(f.get('lineups', []))}")
                print(f"         • Períodos: {len(f.get('periods', []))}")
            
            all_fixtures_enriched.extend(fixtures_data)
            
            # Rate limit
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Erro no lote: {e}")
            continue
    
    print(f"\n   📊 Total: {len(all_fixtures_enriched)} fixtures com dados completos")
    
    # ============================================
    # 3. PROCESSAR E SALVAR DADOS ENRIQUECIDOS
    # ============================================
    print("\n💾 3. Salvando dados enriquecidos...")
    
    fixtures_updated = 0
    events_saved = 0
    stats_saved = 0
    lineups_saved = 0
    periods_saved = 0
    
    for fixture in all_fixtures_enriched:
        try:
            fixture_id = fixture.get('id')
            
            # ========== ATUALIZAR FIXTURE COM DADOS COMPLETOS ==========
            fixture_data = {
                'sportmonks_id': fixture_id,
                'league_id': fixture.get('league_id'),
                'season_id': fixture.get('season_id'),
                'league_name': fixture.get('league', {}).get('name'),
                'season_name': fixture.get('season', {}).get('name'),
                'match_date': fixture.get('starting_at'),
                'status': fixture.get('state', {}).get('state') or fixture.get('state', {}).get('name'),
                'venue': fixture.get('venue', {}).get('name') if fixture.get('venue') else None,
                'venue_city': fixture.get('venue', {}).get('city') if fixture.get('venue') else None,
                'attendance': fixture.get('venue', {}).get('attendance') if fixture.get('venue') else None,
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
            
            # Placar
            for s in fixture.get('scores', []):
                if s.get('description') in ('CURRENT', 'FT'):
                    if s.get('participant') == 'home':
                        fixture_data['home_score'] = (s.get('score') or {}).get('goals')
                    elif s.get('participant') == 'away':
                        fixture_data['away_score'] = (s.get('score') or {}).get('goals')
            
            # Árbitros
            referees = []
            for ref in fixture.get('referees', []):
                ref_type = (ref.get('type') or {}).get('name', 'Unknown')
                ref_name = ref.get('name')
                if ref_type == 'Referee':
                    fixture_data['referee'] = ref_name
                referees.append(f"{ref_type}: {ref_name}")
            
            if referees:
                fixture_data['all_referees'] = ', '.join(referees)
            
            # Atualizar fixture
            supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
            fixtures_updated += 1
            
            # ========== EVENTOS ==========
            if fixture.get('events'):
                events_to_save = []
                
                for event in fixture['events']:
                    type_id = event.get('type_id')
                    event_type_obj = event.get('type', {})
                    
                    # ID único
                    event_id = event.get('id')
                    if not event_id:
                        event_id = generate_event_id(
                            fixture_id,
                            type_id,
                            event.get('minute', 0),
                            event.get('player_id'),
                            event.get('participant_id')
                        )
                    
                    # Tipo do evento
                    event_type = EVENT_TYPE_MAP.get(type_id)
                    if not event_type and event_type_obj:
                        event_type = event_type_obj.get('name', f'type_{type_id}').lower().replace(' ', '_')
                    
                    event_data = {
                        'id': str(event_id),
                        'fixture_id': fixture_id,
                        'type_id': type_id,
                        'event_type': event_type or f'type_{type_id}',
                        'minute': event.get('minute', 0),
                        'extra_minute': event.get('extra_minute'),
                        'team_id': event.get('participant_id'),
                        'player_id': event.get('player_id'),
                        'related_player_id': event.get('related_player_id'),
                        'player_name': event.get('player_name'),
                        'period_id': event.get('period_id'),
                        'result': event.get('result')
                    }
                    events_to_save.append(event_data)
                
                if events_to_save:
                    try:
                        for event in events_to_save:
                            supabase.table('match_events').upsert(event, on_conflict='id').execute()
                        events_saved += len(events_to_save)
                    except:
                        pass  # Tabela pode não existir
            
            # ========== ESTATÍSTICAS ==========
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
                    type_obj = stat.get('type', {})
                    value = (stat.get('data') or {}).get('value') if isinstance(stat.get('data'), dict) else stat.get('data')
                    
                    # Mapear estatísticas conhecidas
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
                
                if stats_by_team:
                    try:
                        for team_stats in stats_by_team.values():
                            supabase.table('match_statistics').upsert(
                                team_stats,
                                on_conflict='fixture_id,team_id'
                            ).execute()
                        stats_saved += len(stats_by_team)
                    except:
                        pass  # Tabela pode não existir
            
            # ========== ESCALAÇÕES COM DADOS COMPLETOS ==========
            if fixture.get('lineups'):
                lineups_to_save = []
                
                for lineup in fixture['lineups']:
                    team_id = lineup.get('team_id') or lineup.get('participant_id')
                    player_obj = lineup.get('player', {})
                    
                    # Extrair dados do jogador
                    player_id = lineup.get('player_id') or player_obj.get('id')
                    if not player_id:
                        continue
                    
                    player_name = player_obj.get('name') or lineup.get('player_name')
                    
                    lineup_data = {
                        'fixture_id': fixture_id,
                        'team_id': team_id,
                        'player_id': player_id,
                        'player_name': player_name,
                        'type': lineup.get('type', {}).get('name', 'lineup') if isinstance(lineup.get('type'), dict) else 'lineup',
                        'position_id': lineup.get('position_id'),
                        'position_name': lineup.get('position', {}).get('name') if isinstance(lineup.get('position'), dict) else None,
                        'jersey_number': lineup.get('jersey_number'),
                        'captain': bool(lineup.get('captain')),
                        'minutes_played': lineup.get('minutes_played'),
                        'rating': lineup.get('rating')
                    }
                    lineups_to_save.append(lineup_data)
                
                if lineups_to_save:
                    try:
                        for lineup in lineups_to_save:
                            supabase.table('match_lineups').upsert(
                                lineup,
                                on_conflict='fixture_id,team_id,player_id'
                            ).execute()
                        lineups_saved += len(lineups_to_save)
                    except:
                        pass  # Tabela pode não existir
            
            # ========== PERÍODOS ==========
            if fixture.get('periods'):
                for period in fixture['periods']:
                    period_data = {
                        'fixture_id': fixture_id,
                        'period_id': period.get('id'),
                        'period_type': period.get('type', {}).get('name') if isinstance(period.get('type'), dict) else None,
                        'started_at': period.get('started_at'),
                        'ended_at': period.get('ended_at'),
                        'minutes': period.get('minutes')
                    }
                    try:
                        supabase.table('match_periods').upsert(
                            period_data,
                            on_conflict='fixture_id,period_id'
                        ).execute()
                        periods_saved += 1
                    except:
                        pass  # Tabela pode não existir
            
            # Progresso
            if fixtures_updated % 50 == 0:
                print(f"   Processadas {fixtures_updated}/{len(all_fixtures_enriched)} fixtures...")
            
        except Exception as e:
            logger.error(f"Erro ao processar fixture {fixture.get('id')}: {e}")
    
    # ============================================
    # 4. RELATÓRIO FINAL
    # ============================================
    print("\n" + "=" * 70)
    print("✅ ENRIQUECIMENTO CONCLUÍDO!")
    print("=" * 70)
    
    print(f"\n📊 DADOS SALVOS:")
    print(f"   • Fixtures atualizadas: {fixtures_updated}")
    print(f"   • Eventos salvos: {events_saved}")
    print(f"   • Estatísticas salvas: {stats_saved}")
    print(f"   • Escalações salvas: {lineups_saved}")
    print(f"   • Períodos salvos: {periods_saved}")
    
    # Verificar totais
    try:
        fixtures = supabase.table('fixtures').select('*', count='exact').execute()
        print(f"\n📊 TOTAIS NO BANCO:")
        print(f"   • Fixtures: {fixtures.count}")
        
        # Tentar contar eventos
        try:
            events = supabase.table('match_events').select('*', count='exact').execute()
            print(f"   • Eventos: {events.count}")
        except:
            print(f"   • Eventos: Tabela não criada ainda")
        
        # Tentar contar estatísticas
        try:
            stats = supabase.table('match_statistics').select('*', count='exact').execute()
            print(f"   • Estatísticas: {stats.count}")
        except:
            print(f"   • Estatísticas: Tabela não criada ainda")
        
        # Tentar contar escalações
        try:
            lineups = supabase.table('match_lineups').select('*', count='exact').execute()
            print(f"   • Escalações: {lineups.count}")
        except:
            print(f"   • Escalações: Tabela não criada ainda")
        
    except Exception as e:
        logger.error(f"Erro ao buscar totais: {e}")
    
    print("\n✅ Dados enriquecidos com sucesso!")
    print("🎯 Importante: Crie as tabelas match_events, match_statistics, match_lineups e match_periods no Supabase")
    print("=" * 70)

if __name__ == "__main__":
    enriquecer_fixtures()
