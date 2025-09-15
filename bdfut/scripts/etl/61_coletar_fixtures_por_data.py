#!/usr/bin/env python3
"""
Script para coletar fixtures por período de datas
Abordagem alternativa já que os filtros de temporada não funcionam
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
        logging.FileHandler(f'/Users/mhbutzke/Documents/BDFut/bdfut/bdfut/logs/coleta_fixtures_por_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FixturesCollectorPorData:
    """Classe para coletar fixtures por período de datas"""
    
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
    
    def get_main_leagues(self) -> List[Dict]:
        """Obter ligas principais do banco"""
        try:
            # Buscar ligas principais
            response = self.supabase.table('leagues').select('sportmonks_id,name').in_('sportmonks_id', [8, 82, 564, 2, 5, 24, 109, 600, 573]).execute()
            return response.data
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar ligas: {str(e)}")
            return []
    
    def collect_fixtures_by_date_range(self, start_date: str, end_date: str) -> int:
        """Coletar fixtures por período de datas"""
        logger.info(f"📅 Coletando fixtures de {start_date} a {end_date}...")
        
        try:
            url = f"{self.base_url}/fixtures"
            params = {
                'include': 'participants;state;venue',
                'per_page': 100
            }
            
            all_fixtures = []
            page = 1
            
            while True:
                params['page'] = page
                response = self.make_request(url, params)
                
                fixtures = response.get('data', [])
                if not fixtures:
                    break
                
                # Filtrar fixtures por data
                filtered_fixtures = []
                for fixture in fixtures:
                    fixture_date = fixture.get('starting_at')
                    if fixture_date:
                        try:
                            fixture_dt = datetime.fromisoformat(fixture_date.replace('Z', '+00:00'))
                            start_dt = datetime.fromisoformat(start_date)
                            end_dt = datetime.fromisoformat(end_date)
                            
                            if start_dt <= fixture_dt <= end_dt:
                                filtered_fixtures.append(fixture)
                        except:
                            continue
                
                all_fixtures.extend(filtered_fixtures)
                
                # Verificar se há mais páginas
                pagination = response.get('pagination', {})
                if not pagination.get('has_more', False):
                    break
                
                page += 1
                time.sleep(0.5)  # Pausa entre páginas
            
            logger.info(f"📊 {len(all_fixtures)} fixtures encontradas no período")
            
            # Processar e salvar fixtures
            saved_count = self.process_and_save_fixtures(all_fixtures)
            
            return saved_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar fixtures: {str(e)}")
            return 0
    
    def process_and_save_fixtures(self, fixtures: List[Dict]) -> int:
        """Processar e salvar fixtures com dados relacionados"""
        saved_count = 0
        
        for fixture in tqdm(fixtures, desc="Processando fixtures"):
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
    
    def collect_recent_fixtures(self):
        """Coletar fixtures dos últimos 2 anos"""
        logger.info("=" * 80)
        logger.info("🚀 INICIANDO COLETA DE FIXTURES POR PERÍODO")
        logger.info("=" * 80)
        
        # Definir períodos de coleta (últimos 2 anos)
        current_date = datetime.now()
        
        periods = [
            {
                'name': 'Últimos 6 meses',
                'start': (current_date - timedelta(days=180)).isoformat(),
                'end': current_date.isoformat()
            },
            {
                'name': '6 meses anteriores',
                'start': (current_date - timedelta(days=360)).isoformat(),
                'end': (current_date - timedelta(days=180)).isoformat()
            },
            {
                'name': '1 ano anterior',
                'start': (current_date - timedelta(days=540)).isoformat(),
                'end': (current_date - timedelta(days=360)).isoformat()
            }
        ]
        
        total_fixtures_collected = 0
        
        for period in periods:
            logger.info(f"\n📅 Período: {period['name']}")
            logger.info(f"De: {period['start']} até: {period['end']}")
            
            fixtures_count = self.collect_fixtures_by_date_range(
                period['start'], 
                period['end']
            )
            
            total_fixtures_collected += fixtures_count
            logger.info(f"✅ {fixtures_count} fixtures coletadas neste período")
            
            # Pausa entre períodos
            time.sleep(2)
        
        # Relatório final
        logger.info("=" * 80)
        logger.info("📊 RELATÓRIO FINAL DA COLETA")
        logger.info("=" * 80)
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
    
    logger.info("🚀 Iniciando coleta de fixtures por período...")
    
    try:
        # Executar coleta
        collector = FixturesCollectorPorData()
        collector.collect_recent_fixtures()
        
    except Exception as e:
        logger.error(f"❌ Erro no processo principal: {str(e)}")
        raise

if __name__ == "__main__":
    main()
