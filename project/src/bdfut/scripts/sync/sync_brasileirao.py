#!/usr/bin/env python3
"""
Script para sincronizar dados completos do Brasileirão Série A 2025
Liga ID: 648
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

def sync_brasileirao_2025():
    """Sincroniza dados completos do Brasileirão 2025"""
    
    # Conectar aos serviços
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 70)
    print("🏆 SINCRONIZAÇÃO BRASILEIRÃO SÉRIE A 2025")
    print("=" * 70)
    
    LEAGUE_ID = 648  # Brasileirão Série A
    
    # 1. BUSCAR INFORMAÇÕES DA LIGA
    print("\n📋 1. Buscando informações da liga...")
    try:
        league = sportmonks.get_league_by_id(LEAGUE_ID, include='country;seasons')
        print(f"   ✅ Liga: {league.get('name')}")
        print(f"   📍 País: {league.get('country', {}).get('name', 'Brasil')}")
        
        # Salvar liga no banco
        league_data = {
            'sportmonks_id': league.get('id'),
            'name': league.get('name'),
            'country': league.get('country', {}).get('name'),
            'logo_url': league.get('image_path'),
            'active': league.get('active', True),
            'updated_at': datetime.now().isoformat()
        }
        supabase.table('leagues').upsert(league_data, on_conflict='sportmonks_id').execute()
        
    except Exception as e:
        logger.error(f"Erro ao buscar liga: {str(e)}")
        return
    
    # 2. BUSCAR TEMPORADA ATUAL (2025)
    print("\n📅 2. Buscando temporada 2025...")
    current_season = None
    
    if 'seasons' in league and league['seasons']:
        # Buscar temporada de 2025 ou a mais recente
        for season in league['seasons']:
            if '2025' in str(season.get('name', '')):
                current_season = season
                break
        
        # Se não encontrar 2025, pegar a temporada atual
        if not current_season:
            current_season = next((s for s in league['seasons'] if s.get('is_current')), None)
        
        # Se ainda não encontrar, pegar a mais recente
        if not current_season and league['seasons']:
            current_season = sorted(league['seasons'], key=lambda x: x.get('id', 0), reverse=True)[0]
    
    if not current_season:
        print("   ❌ Temporada não encontrada!")
        return
    
    SEASON_ID = current_season.get('id')
    print(f"   ✅ Temporada: {current_season.get('name')} (ID: {SEASON_ID})")
    print(f"   📅 Período: {current_season.get('starting_at')} até {current_season.get('ending_at')}")
    
    # Salvar temporada no banco
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
    
    # 3. BUSCAR TIMES DA TEMPORADA
    print("\n⚽ 3. Buscando times da temporada...")
    try:
        teams = sportmonks.get_teams_by_season(SEASON_ID, include='venue')
        print(f"   ✅ {len(teams)} times encontrados")
        
        # Salvar times no banco
        for team in teams:
            team_data = {
                'sportmonks_id': team.get('id'),
                'name': team.get('name'),
                'short_code': team.get('short_code'),
                'logo_url': team.get('logo_path'),
                'founded': team.get('founded'),
                'venue_name': team.get('venue', {}).get('name') if team.get('venue') else None,
                'updated_at': datetime.now().isoformat()
            }
            supabase.table('teams').upsert(team_data, on_conflict='sportmonks_id').execute()
        
        # Mostrar alguns times
        for i, team in enumerate(teams[:5], 1):
            print(f"     {i}. {team.get('name')}")
        if len(teams) > 5:
            print(f"     ... e mais {len(teams) - 5} times")
            
    except Exception as e:
        logger.error(f"Erro ao buscar times: {str(e)}")
        teams = []
    
    # 4. BUSCAR PARTIDAS DA TEMPORADA COM TODOS OS DETALHES
    print("\n🎮 4. Buscando partidas com eventos e estatísticas completos...")
    
    # Buscar datas da temporada
    if current_season.get('starting_at') and current_season.get('ending_at'):
        start_date = current_season.get('starting_at')
        end_date = current_season.get('ending_at')
    else:
        # Usar período padrão se não tiver datas
        start_date = '2025-01-01'
        end_date = '2025-12-31'
    
    print(f"   📅 Buscando partidas de {start_date} até {end_date}")
    
    # Includes completos para obter TODOS os detalhes
    includes = 'participants;state;venue;events;statistics;lineups;referees;scores;periods'
    
    try:
        # Buscar todas as partidas da temporada
        fixtures = sportmonks.get_fixtures_by_date_range(
            start_date,
            end_date,
            include=includes
        )
        
        # Filtrar apenas partidas do Brasileirão
        brasileirao_fixtures = [f for f in fixtures if f.get('league_id') == LEAGUE_ID]
        
        print(f"   ✅ {len(brasileirao_fixtures)} partidas encontradas")
        
        # Processar cada partida
        total_events = 0
        total_stats = 0
        total_lineups = 0
        
        print("\n💾 5. Salvando partidas no banco de dados...")
        
        for i, fixture in enumerate(brasileirao_fixtures, 1):
            try:
                # Preparar dados básicos da partida
                fixture_data = {
                    'sportmonks_id': fixture.get('id'),
                    'league_id': fixture.get('league_id'),
                    'season_id': fixture.get('season_id'),
                    'match_date': fixture.get('starting_at'),
                    'status': fixture.get('state', {}).get('name') if isinstance(fixture.get('state'), dict) else 'Unknown',
                    'venue': fixture.get('venue', {}).get('name') if isinstance(fixture.get('venue'), dict) else None,
                    'updated_at': datetime.now().isoformat()
                }
                
                # Extrair times participantes
                if 'participants' in fixture and fixture['participants']:
                    for participant in fixture['participants']:
                        if participant.get('meta', {}).get('location') == 'home':
                            fixture_data['home_team_id'] = participant.get('id')
                        elif participant.get('meta', {}).get('location') == 'away':
                            fixture_data['away_team_id'] = participant.get('id')
                
                # Extrair scores
                if 'scores' in fixture and fixture['scores']:
                    for score in fixture['scores']:
                        if score.get('description') == 'CURRENT':
                            if score.get('score', {}).get('participant') == 'home':
                                fixture_data['home_score'] = score.get('score', {}).get('goals')
                            elif score.get('score', {}).get('participant') == 'away':
                                fixture_data['away_score'] = score.get('score', {}).get('goals')
                
                # Extrair árbitro principal
                if 'referees' in fixture and fixture['referees']:
                    main_referee = next((r for r in fixture['referees'] if r.get('type', {}).get('name') == 'Referee'), None)
                    if main_referee:
                        fixture_data['referee'] = main_referee.get('name')
                
                # Salvar partida
                supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
                
                # Contar dados adicionais
                if 'events' in fixture:
                    total_events += len(fixture.get('events', []))
                if 'statistics' in fixture:
                    total_stats += len(fixture.get('statistics', []))
                if 'lineups' in fixture:
                    total_lineups += len(fixture.get('lineups', []))
                
                # Mostrar progresso
                if i % 10 == 0:
                    print(f"   Processadas {i}/{len(brasileirao_fixtures)} partidas...")
                
                # Pequena pausa para não sobrecarregar
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Erro ao processar partida {fixture.get('id')}: {str(e)}")
                continue
        
        print(f"\n   ✅ Partidas salvas com sucesso!")
        print(f"   📊 Total de eventos: {total_events}")
        print(f"   📈 Total de estatísticas: {total_stats}")
        print(f"   👥 Total de escalações: {total_lineups}")
        
    except Exception as e:
        logger.error(f"Erro ao buscar partidas: {str(e)}")
    
    # 6. BUSCAR CLASSIFICAÇÃO ATUAL
    print("\n🏅 6. Buscando classificação atual...")
    try:
        standings = sportmonks.get_standings_by_season(SEASON_ID, include='participant;details')
        
        if standings:
            print(f"   ✅ Classificação encontrada")
            print("\n   📊 TOP 5:")
            
            # Ordenar por posição
            sorted_standings = sorted(standings, key=lambda x: x.get('position', 999))
            
            for standing in sorted_standings[:5]:
                participant = standing.get('participant', {})
                if isinstance(participant, dict):
                    team_name = participant.get('name', 'Time')
                else:
                    team_name = 'Time'
                
                print(f"     {standing.get('position', 0)}º - {team_name}: {standing.get('points', 0)} pontos")
    
    except Exception as e:
        logger.error(f"Erro ao buscar classificação: {str(e)}")
    
    # 7. RESUMO FINAL
    print("\n" + "=" * 70)
    print("✅ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    
    # Estatísticas finais do banco
    try:
        leagues_count = supabase.table('leagues').select("*", count='exact').execute()
        seasons_count = supabase.table('seasons').select("*", count='exact').execute()
        teams_count = supabase.table('teams').select("*", count='exact').execute()
        fixtures_count = supabase.table('fixtures').select("*", count='exact').execute()
        
        print("\n📊 DADOS NO BANCO:")
        print(f"   • Ligas: {len(leagues_count.data)}")
        print(f"   • Temporadas: {len(seasons_count.data)}")
        print(f"   • Times: {len(teams_count.data)}")
        print(f"   • Partidas: {len(fixtures_count.data)}")
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {str(e)}")
    
    print("\n🎯 Próximos passos:")
    print("   1. Verificar os dados no Supabase")
    print("   2. Ajustar o script se necessário")
    print("   3. Expandir para outras ligas")
    print("=" * 70)

if __name__ == "__main__":
    sync_brasileirao_2025()
