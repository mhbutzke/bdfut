#!/usr/bin/env python3
"""
Script para coletar fixtures das últimas 3 temporadas das ligas principais
Versão simplificada focada nas principais ligas europeias
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
        logging.FileHandler(f'/Users/mhbutzke/Documents/BDFut/bdfut/bdfut/logs/coleta_fixtures_principais_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FixturesCollectorPrincipal:
    """Classe para coletar fixtures das ligas principais"""
    
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
        
        # Ligas principais para focar
        self.main_leagues = [
            {"id": 8, "name": "Premier League"},
            {"id": 82, "name": "Bundesliga"},
            {"id": 564, "name": "Serie A"},
            {"id": 564, "name": "La Liga"},
            {"id": 2, "name": "Champions League"},
            {"id": 5, "name": "Europa League"},
            {"id": 24, "name": "FA Cup"},
            {"id": 109, "name": "DFB Pokal"},
            {"id": 600, "name": "Super Lig"},
            {"id": 573, "name": "Allsvenskan"}
        ]
        
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
            
            # Rate limiting inteligente usando headers da API
            remaining = int(response.headers.get('x-ratelimit-remaining', 3000))
            limit = int(response.headers.get('x-ratelimit-limit', 3000))
            
            # Log de progresso a cada 100 requisições
            if self.requests_made % 100 == 0:
                logger.info(f"📊 {self.requests_made} requisições feitas (restantes: {remaining}/{limit})")
            
            # Rate limiting baseado nos headers reais da API
            if remaining < 50:  # Menos de 50 requisições restantes
                logger.warning(f"⚠️ Rate limit baixo ({remaining} restantes), pausando 30s...")
                time.sleep(30)
            elif remaining < 100:  # Menos de 100 requisições restantes
                logger.warning(f"⚠️ Rate limit médio ({remaining} restantes), pausando 10s...")
                time.sleep(10)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na requisição para {url}: {str(e)}")
            if response.status_code == 429:  # Rate limit exceeded
                logger.warning("⏳ Rate limit excedido, aguardando 60 segundos...")
                time.sleep(60)
            raise
    
    def get_latest_3_seasons_for_league(self, league_id: int) -> List[Dict]:
        """Obter as 3 temporadas mais recentes de uma liga"""
        try:
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
                'include': 'participants;state;venue',
                'per_page': 500  # Otimizado para reduzir requisições
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
                time.sleep(0.1)  # Pausa otimizada entre páginas
            
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
                    'updated_at': datetime.now().isoformat()
                }
                
                self.supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
                
                saved_count += 1
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao processar fixture {fixture.get('id')}: {str(e)}")
                continue
        
        return saved_count
    
    def collect_fixtures_for_main_leagues(self):
        """Coletar fixtures das últimas 3 temporadas para as ligas principais"""
        logger.info("=" * 80)
        logger.info("🚀 INICIANDO COLETA DE FIXTURES DAS LIGAS PRINCIPAIS")
        logger.info("=" * 80)
        
        total_fixtures_collected = 0
        leagues_processed = 0
        
        for league in tqdm(self.main_leagues, desc="Processando ligas principais"):
            league_id = league['id']
            league_name = league['name']
            
            logger.info(f"\n🏆 Processando liga: {league_name} (ID: {league_id})")
            
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
    
    logger.info("🚀 Iniciando coleta de fixtures das ligas principais...")
    
    try:
        # Executar coleta
        collector = FixturesCollectorPrincipal()
        collector.collect_fixtures_for_main_leagues()
        
    except Exception as e:
        logger.error(f"❌ Erro no processo principal: {str(e)}")
        raise

if __name__ == "__main__":
    main()
