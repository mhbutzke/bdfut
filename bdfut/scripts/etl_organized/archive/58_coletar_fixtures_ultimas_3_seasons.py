#!/usr/bin/env python3
"""
Script para coletar fixtures das últimas 3 temporadas de cada liga
Este script busca dados históricos importantes para análise
"""

import os
import sys
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from tqdm import tqdm
from supabase import create_client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/Users/mhbutzke/Documents/BDFut/bdfut/bdfut/logs/coleta_fixtures_3_seasons_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FixturesCollector:
    """Classe para coletar fixtures das últimas 3 temporadas de cada liga"""
    
    def __init__(self):
        self.api_key = os.getenv("SPORTMONKS_API_KEY")
        self.base_url = "https://api.sportmonks.com/v3/football"
        
        if not self.api_key:
            raise ValueError("SPORTMONKS_API_KEY deve estar configurado no .env")
        
        # Cliente Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar configurados no .env")
        
        self.supabase = create_client(supabase_url, supabase_key)
        
        # Controle de rate limit
        self.requests_made = 0
        self.max_requests_per_hour = 3000
        self.start_time = datetime.now()
    
    def make_request(self, url: str, params: Dict = None) -> Dict:
        """Fazer requisição para a API com controle de rate limit"""
        if params is None:
            params = {}
        
        params['api_token'] = self.api_key
        
        try:
            response = requests.get(url, params=params)
            self.requests_made += 1
            
            # Controle de rate limit
            if self.requests_made % 50 == 0:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                rate = self.requests_made / (elapsed / 3600) if elapsed > 0 else 0
                logger.info(f"📊 {self.requests_made} requisições feitas (taxa: {rate:.1f}/hora)")
                
                if rate > self.max_requests_per_hour * 0.9:  # 90% do limite
                    logger.warning("⚠️ Aproximando do limite de rate limit, pausando...")
                    time.sleep(60)  # Pausa de 1 minuto
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na requisição para {url}: {str(e)}")
            if response.status_code == 429:  # Rate limit exceeded
                logger.warning("⏳ Rate limit excedido, aguardando 60 segundos...")
                time.sleep(60)
            raise
    
    def get_leagues_with_seasons(self) -> List[Dict]:
        """Obter ligas com suas temporadas mais recentes"""
        logger.info("🔍 Buscando ligas com temporadas disponíveis...")
        
        try:
            # Buscar todas as ligas
            leagues_response = self.supabase.table('leagues').select('sportmonks_id,name').execute()
            leagues = leagues_response.data
            
            # Filtrar ligas que têm pelo menos 3 temporadas
            leagues_with_seasons = []
            
            for league in leagues:
                league_id = league['sportmonks_id']
                league_name = league['name']
                
                # Contar temporadas desta liga
                seasons_response = self.supabase.table('seasons').select('id').eq('league_id', league_id).execute()
                season_count = len(seasons_response.data)
                
                if season_count >= 3:
                    leagues_with_seasons.append({
                        'league_id': league_id,
                        'league_name': league_name,
                        'total_seasons': season_count
                    })
            
            logger.info(f"📊 {len(leagues_with_seasons)} ligas encontradas com pelo menos 3 temporadas")
            return leagues_with_seasons
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar ligas: {str(e)}")
            return []
    
    def get_latest_3_seasons_for_league(self, league_id: int) -> List[Dict]:
        """Obter as 3 temporadas mais recentes de uma liga"""
        try:
            query = """
            SELECT 
                sportmonks_id,
                name,
                starting_at,
                ending_at,
                is_current
            FROM seasons 
            WHERE league_id = %s
            ORDER BY starting_at DESC
            LIMIT 3
            """
            
            response = self.supabase.table('seasons').select('sportmonks_id,name,starting_at,ending_at,is_current').eq('league_id', league_id).order('starting_at', desc=True).limit(3).execute()
            
            return response.data
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar temporadas da liga {league_id}: {str(e)}")
            return []
    
    def collect_fixtures_for_season(self, season_id: int, season_name: str) -> int:
        """Coletar fixtures de uma temporada específica"""
        logger.info(f"⚽ Coletando fixtures da temporada {season_name} (ID: {season_id})...")
        
        try:
            # Buscar fixtures da temporada com dados detalhados
            url = f"{self.base_url}/fixtures"
            params = {
                'season_id': season_id,
                'include': 'participants;state;venue;events;statistics;lineups;referees',
                'per_page': 100  # Máximo por página
            }
            
            all_fixtures = []
            page = 1
            
            while True:
                params['page'] = page
                response = self.make_request(url, params)
                
                fixtures = response.get('data', [])
                if not fixtures:
                    break
                
                all_fixtures.extend(fixtures)
                
                # Verificar se há mais páginas
                pagination = response.get('pagination', {})
                if not pagination.get('has_more', False):
                    break
                
                page += 1
                time.sleep(0.5)  # Pausa entre páginas
            
            logger.info(f"📊 {len(all_fixtures)} fixtures encontradas na temporada {season_name}")
            
            # Processar e salvar fixtures
            saved_count = self.process_and_save_fixtures(all_fixtures, season_id)
            
            return saved_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar fixtures da temporada {season_id}: {str(e)}")
            return 0
    
    def process_and_save_fixtures(self, fixtures: List[Dict], season_id: int) -> int:
        """Processar e salvar fixtures com dados relacionados"""
        saved_count = 0
        
        for fixture in tqdm(fixtures, desc=f"Processando fixtures da temporada {season_id}"):
            try:
                fixture_id = fixture.get('id')
                
                # Processar venues
                if 'venue' in fixture and fixture['venue']:
                    venue_data = {
                        'sportmonks_id': fixture['venue'].get('id'),
                        'name': fixture['venue'].get('name'),
                        'city': fixture['venue'].get('city_name'),
                        'capacity': fixture['venue'].get('capacity'),
                        'surface': fixture['venue'].get('surface'),
                        'country': fixture['venue'].get('country_name'),
                        'image_path': fixture['venue'].get('image_path'),
                        'updated_at': datetime.now().isoformat()
                    }
                    self.supabase.table('venues').upsert(venue_data, on_conflict='sportmonks_id').execute()
                
                # Processar árbitros
                if 'referees' in fixture and fixture['referees']:
                    for referee in fixture['referees']:
                        referee_data = {
                            'sportmonks_id': referee.get('id'),
                            'name': referee.get('name'),
                            'common_name': referee.get('common_name'),
                            'firstname': referee.get('firstname'),
                            'lastname': referee.get('lastname'),
                            'nationality': referee.get('nationality'),
                            'image_path': referee.get('image_path'),
                            'updated_at': datetime.now().isoformat()
                        }
                        self.supabase.table('referees').upsert(referee_data, on_conflict='sportmonks_id').execute()
                
                # Salvar fixture principal
                fixture_data = {
                    'sportmonks_id': fixture_id,
                    'league_id': fixture.get('league_id'),
                    'season_id': fixture.get('season_id'),
                    'home_team_id': fixture.get('participants', [{}])[0].get('id') if fixture.get('participants') else None,
                    'away_team_id': fixture.get('participants', [{}])[1].get('id') if len(fixture.get('participants', [])) > 1 else None,
                    'match_date': fixture.get('starting_at'),
                    'status': fixture.get('state', {}).get('name') if fixture.get('state') else None,
                    'home_score': fixture.get('result_info', {}).get('home_score') if fixture.get('result_info') else None,
                    'away_score': fixture.get('result_info', {}).get('away_score') if fixture.get('result_info') else None,
                    'venue': fixture.get('venue', {}).get('name') if fixture.get('venue') else None,
                    'referee': fixture.get('referees', [{}])[0].get('name') if fixture.get('referees') else None,
                    'updated_at': datetime.now().isoformat()
                }
                
                self.supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
                
                # Processar eventos se existirem
                if 'events' in fixture and fixture['events']:
                    self.process_fixture_events(fixture_id, fixture['events'])
                
                # Processar estatísticas se existirem
                if 'statistics' in fixture and fixture['statistics']:
                    self.process_fixture_statistics(fixture_id, fixture['statistics'])
                
                # Processar lineups se existirem
                if 'lineups' in fixture and fixture['lineups']:
                    self.process_fixture_lineups(fixture_id, fixture['lineups'])
                
                saved_count += 1
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao processar fixture {fixture.get('id')}: {str(e)}")
                continue
        
        return saved_count
    
    def process_fixture_events(self, fixture_id: int, events: List[Dict]):
        """Processar eventos de uma fixture"""
        try:
            for event in events:
                event_data = {
                    'id': f"{fixture_id}_{event.get('id')}",
                    'fixture_id': fixture_id,
                    'type_id': event.get('type_id'),
                    'event_type': event.get('type', {}).get('name') if event.get('type') else None,
                    'minute': event.get('minute', 0),
                    'extra_minute': event.get('extra_minute'),
                    'team_id': event.get('participant_id'),
                    'player_id': event.get('player_id'),
                    'related_player_id': event.get('related_player_id'),
                    'player_name': event.get('player_name'),
                    'period_id': event.get('period_id'),
                    'result': event.get('result'),
                    'created_at': datetime.now().isoformat()
                }
                
                self.supabase.table('match_events').upsert(event_data, on_conflict='id').execute()
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao processar eventos da fixture {fixture_id}: {str(e)}")
    
    def process_fixture_statistics(self, fixture_id: int, statistics: List[Dict]):
        """Processar estatísticas de uma fixture"""
        try:
            for stat in statistics:
                stat_data = {
                    'fixture_id': fixture_id,
                    'team_id': stat.get('participant_id'),
                    'shots_total': stat.get('shots_total'),
                    'shots_on_target': stat.get('shots_on_target'),
                    'shots_inside_box': stat.get('shots_inside_box'),
                    'shots_outside_box': stat.get('shots_outside_box'),
                    'blocked_shots': stat.get('blocked_shots'),
                    'corners': stat.get('corners'),
                    'offsides': stat.get('offsides'),
                    'ball_possession': stat.get('ball_possession'),
                    'yellow_cards': stat.get('yellow_cards'),
                    'red_cards': stat.get('red_cards'),
                    'fouls': stat.get('fouls'),
                    'passes_total': stat.get('passes_total'),
                    'passes_accurate': stat.get('passes_accurate'),
                    'pass_percentage': stat.get('pass_percentage'),
                    'saves': stat.get('saves'),
                    'tackles': stat.get('tackles'),
                    'interceptions': stat.get('interceptions'),
                    'created_at': datetime.now().isoformat()
                }
                
                self.supabase.table('match_statistics').upsert(stat_data, on_conflict='fixture_id,team_id').execute()
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao processar estatísticas da fixture {fixture_id}: {str(e)}")
    
    def process_fixture_lineups(self, fixture_id: int, lineups: List[Dict]):
        """Processar lineups de uma fixture"""
        try:
            for lineup in lineups:
                lineup_data = {
                    'fixture_id': fixture_id,
                    'team_id': lineup.get('participant_id'),
                    'player_id': lineup.get('player_id'),
                    'player_name': lineup.get('player_name'),
                    'type': lineup.get('type', 'lineup'),
                    'position_id': lineup.get('position_id'),
                    'position_name': lineup.get('position', {}).get('name') if lineup.get('position') else None,
                    'jersey_number': lineup.get('jersey_number'),
                    'captain': lineup.get('captain', False),
                    'minutes_played': lineup.get('minutes_played'),
                    'rating': lineup.get('rating'),
                    'created_at': datetime.now().isoformat()
                }
                
                self.supabase.table('match_lineups').upsert(lineup_data, on_conflict='fixture_id,team_id,player_id').execute()
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao processar lineups da fixture {fixture_id}: {str(e)}")
    
    def collect_fixtures_for_all_leagues(self):
        """Coletar fixtures das últimas 3 temporadas para todas as ligas"""
        logger.info("=" * 80)
        logger.info("🚀 INICIANDO COLETA DE FIXTURES DAS ÚLTIMAS 3 TEMPORADAS")
        logger.info("=" * 80)
        
        # Obter ligas
        leagues = self.get_leagues_with_seasons()
        
        if not leagues:
            logger.error("❌ Nenhuma liga encontrada")
            return
        
        total_fixtures_collected = 0
        leagues_processed = 0
        
        for league in tqdm(leagues, desc="Processando ligas"):
            league_id = league['league_id']
            league_name = league['league_name']
            total_seasons = league['total_seasons']
            
            logger.info(f"\n🏆 Processando liga: {league_name} (ID: {league_id}) - {total_seasons} temporadas")
            
            # Obter últimas 3 temporadas
            seasons = self.get_latest_3_seasons_for_league(league_id)
            
            if len(seasons) < 3:
                logger.warning(f"⚠️ Liga {league_name} tem apenas {len(seasons)} temporadas disponíveis")
            
            league_fixtures = 0
            
            for season in seasons:
                season_id = season['sportmonks_id']
                season_name = season['name']
                starting_at = season['starting_at']
                is_current = season['is_current']
                
                logger.info(f"📅 Temporada: {season_name} ({starting_at}) {'[ATUAL]' if is_current else ''}")
                
                # Coletar fixtures da temporada
                fixtures_count = self.collect_fixtures_for_season(season_id, season_name)
                league_fixtures += fixtures_count
                
                # Pausa entre temporadas
                time.sleep(1)
            
            total_fixtures_collected += league_fixtures
            leagues_processed += 1
            
            logger.info(f"✅ Liga {league_name}: {league_fixtures} fixtures coletadas")
            
            # Pausa entre ligas para respeitar rate limit
            time.sleep(2)
        
        # Relatório final
        logger.info("=" * 80)
        logger.info("📊 RELATÓRIO FINAL DA COLETA")
        logger.info("=" * 80)
        logger.info(f"🏆 Ligas processadas: {leagues_processed}")
        logger.info(f"⚽ Total de fixtures coletadas: {total_fixtures_collected:,}")
        logger.info(f"📊 Total de requisições feitas: {self.requests_made}")
        
        # Tempo total
        end_time = datetime.now()
        duration = end_time - self.start_time
        logger.info(f"⏱️ Tempo total: {duration}")
        
        logger.info("=" * 80)
        logger.info("🎉 COLETA DE FIXTURES CONCLUÍDA!")
        logger.info("=" * 80)

def main():
    """Função principal"""
    
    logger.info("🚀 Iniciando coleta de fixtures das últimas 3 temporadas...")
    
    try:
        # Executar coleta
        collector = FixturesCollector()
        collector.collect_fixtures_for_all_leagues()
        
    except Exception as e:
        logger.error(f"❌ Erro no processo principal: {str(e)}")
        raise

if __name__ == "__main__":
    main()
