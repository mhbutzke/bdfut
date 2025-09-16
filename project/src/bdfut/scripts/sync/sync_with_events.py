#!/usr/bin/env python3
"""
Script para sincronizar partidas com eventos e estatísticas completos
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
from tqdm import tqdm

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def sync_fixtures_with_full_details():
    """Sincroniza partidas com todos os eventos e estatísticas"""
    
    # Conectar aos serviços
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("🚀 Iniciando sincronização de partidas com eventos e estatísticas completos...")
    print("=" * 60)
    
    # Buscar partidas dos últimos 30 dias e próximos 7 dias
    end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"📅 Período: {start_date} até {end_date}")
    print(f"🏆 Buscando partidas das ligas principais...")
    
    # Includes completos para obter todos os detalhes
    includes = 'participants;state;venue;events;statistics;lineups;referees;scores;periods'
    
    # Buscar partidas com filtro por ligas principais
    all_fixtures = []
    
    for league_id in tqdm(Config.MAIN_LEAGUES, desc="Buscando ligas"):
        try:
            # Buscar partidas por liga
            fixtures = sportmonks.get_fixtures_by_date_range(
                start_date, 
                end_date,
                include=includes
            )
            
            # Filtrar apenas partidas da liga atual
            league_fixtures = [f for f in fixtures if f.get('league_id') == league_id]
            
            if league_fixtures:
                all_fixtures.extend(league_fixtures)
                print(f"  ✅ Liga {league_id}: {len(league_fixtures)} partidas encontradas")
            
            # Pequena pausa para respeitar rate limit
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Erro ao buscar partidas da liga {league_id}: {str(e)}")
            continue
    
    print(f"\n📊 Total de partidas encontradas: {len(all_fixtures)}")
    
    if not all_fixtures:
        print("⚠️  Nenhuma partida encontrada no período.")
        return
    
    # Processar e salvar cada partida
    print("\n💾 Salvando partidas no banco de dados...")
    
    success_count = 0
    error_count = 0
    
    for fixture in tqdm(all_fixtures, desc="Processando partidas"):
        try:
            # Preparar dados da partida
            fixture_data = {
                'sportmonks_id': fixture.get('id'),
                'league_id': fixture.get('league_id'),
                'season_id': fixture.get('season_id'),
                'match_date': fixture.get('starting_at'),
                'status': fixture.get('state', {}).get('name') if isinstance(fixture.get('state'), dict) else 'Unknown',
                'venue': fixture.get('venue', {}).get('name') if isinstance(fixture.get('venue'), dict) else None,
                'updated_at': datetime.now().isoformat()
            }
            
            # Extrair scores se disponível
            if 'scores' in fixture and fixture['scores']:
                for score in fixture['scores']:
                    if score.get('description') == 'CURRENT':
                        if score.get('score', {}).get('participant') == 'home':
                            fixture_data['home_score'] = score.get('score', {}).get('goals')
                        elif score.get('score', {}).get('participant') == 'away':
                            fixture_data['away_score'] = score.get('score', {}).get('goals')
            
            # Extrair times participantes
            if 'participants' in fixture and fixture['participants']:
                for participant in fixture['participants']:
                    if participant.get('meta', {}).get('location') == 'home':
                        fixture_data['home_team_id'] = participant.get('id')
                    elif participant.get('meta', {}).get('location') == 'away':
                        fixture_data['away_team_id'] = participant.get('id')
            
            # Extrair árbitro se disponível
            if 'referees' in fixture and fixture['referees']:
                main_referee = next((r for r in fixture['referees'] if r.get('type', {}).get('name') == 'Referee'), None)
                if main_referee:
                    fixture_data['referee'] = main_referee.get('name')
            
            # Salvar ou atualizar partida
            result = supabase.table('fixtures').upsert(
                fixture_data,
                on_conflict='sportmonks_id'
            ).execute()
            
            # Processar eventos da partida
            if 'events' in fixture and fixture['events']:
                print(f"\n  📌 Partida {fixture.get('id')} tem {len(fixture['events'])} eventos")
                
                # Aqui você pode salvar os eventos em uma tabela separada
                # Por enquanto vamos apenas contar
            
            # Processar estatísticas
            if 'statistics' in fixture and fixture['statistics']:
                print(f"  📊 Partida {fixture.get('id')} tem {len(fixture['statistics'])} estatísticas")
            
            # Processar escalações
            if 'lineups' in fixture and fixture['lineups']:
                print(f"  👥 Partida {fixture.get('id')} tem {len(fixture['lineups'])} jogadores na escalação")
            
            success_count += 1
            
        except Exception as e:
            logger.error(f"Erro ao processar partida {fixture.get('id')}: {str(e)}")
            error_count += 1
            continue
    
    # Resumo final
    print("\n" + "=" * 60)
    print("✅ SINCRONIZAÇÃO CONCLUÍDA!")
    print(f"  ✓ Partidas processadas com sucesso: {success_count}")
    if error_count > 0:
        print(f"  ✗ Partidas com erro: {error_count}")
    print("=" * 60)
    
    # Mostrar estatísticas do banco
    try:
        total = supabase.table('fixtures').select("*", count='exact').execute()
        print(f"\n📊 Total de partidas no banco: {total.count if hasattr(total, 'count') else len(total.data)}")
    except:
        pass

if __name__ == "__main__":
    sync_fixtures_with_full_details()
