#!/usr/bin/env python3
"""
Script para enriquecer tabelas usando dados reais da API Sportmonks
Este script busca dados adicionais da API para enriquecer ainda mais as tabelas
"""

import os
import sys
import time
import logging
import requests
from datetime import datetime
from typing import List, Dict, Any
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
        logging.FileHandler(f'/Users/mhbutzke/Documents/BDFut/bdfut/bdfut/logs/enriquecimento_api_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SportmonksAPIEnricher:
    """Classe para enriquecer dados usando a API Sportmonks"""
    
    def __init__(self):
        self.api_key = os.getenv("SPORTMONKS_API_KEY")
        self.base_url = "https://api.sportmonks.com/v3/football"
        self.core_url = "https://api.sportmonks.com/v3/core"
        
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
    
    def make_request(self, url: str, params: Dict = None) -> Dict:
        """Fazer requisição para a API com controle de rate limit"""
        if params is None:
            params = {}
        
        params['api_token'] = self.api_key
        
        try:
            response = requests.get(url, params=params)
            self.requests_made += 1
            
            # Controle de rate limit
            if self.requests_made % 100 == 0:
                logger.info(f"📊 {self.requests_made} requisições feitas")
                time.sleep(1)  # Pausa a cada 100 requisições
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na requisição para {url}: {str(e)}")
            raise
    
    def enriquecer_referees_api(self):
        """Enriquecer árbitros com dados da API"""
        logger.info("🟨 Enriquecendo árbitros com dados da API...")
        
        try:
            # Buscar árbitros da API
            url = f"{self.base_url}/referees"
            response = self.make_request(url)
            
            referees = response.get('data', [])
            
            if referees:
                enriched_count = 0
                for referee in tqdm(referees, desc="Enriquecendo árbitros"):
                    try:
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
                        enriched_count += 1
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao enriquecer árbitro: {str(e)}")
                        continue
                
                logger.info(f"✅ {enriched_count} árbitros enriquecidos com dados da API")
                return enriched_count
            else:
                logger.warning("⚠️ Nenhum árbitro encontrado na API")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer árbitros: {str(e)}")
            return 0
    
    def enriquecer_venues_api(self):
        """Enriquecer estádios com dados da API"""
        logger.info("🏟️ Enriquecendo estádios com dados da API...")
        
        try:
            # Buscar estádios da API
            url = f"{self.base_url}/venues"
            response = self.make_request(url)
            
            venues = response.get('data', [])
            
            if venues:
                enriched_count = 0
                for venue in tqdm(venues, desc="Enriquecendo estádios"):
                    try:
                        venue_data = {
                            'sportmonks_id': venue.get('id'),
                            'name': venue.get('name'),
                            'city': venue.get('city_name'),
                            'capacity': venue.get('capacity'),
                            'surface': venue.get('surface'),
                            'country': venue.get('country_name'),
                            'image_path': venue.get('image_path'),
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        self.supabase.table('venues').upsert(venue_data, on_conflict='sportmonks_id').execute()
                        enriched_count += 1
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao enriquecer estádio: {str(e)}")
                        continue
                
                logger.info(f"✅ {enriched_count} estádios enriquecidos com dados da API")
                return enriched_count
            else:
                logger.warning("⚠️ Nenhum estádio encontrado na API")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer estádios: {str(e)}")
            return 0
    
    def enriquecer_players_detalhados(self):
        """Enriquecer jogadores com dados detalhados da API"""
        logger.info("⚽ Enriquecendo jogadores com dados detalhados da API...")
        
        try:
            # Buscar jogadores únicos dos eventos e lineups
            players_set = set()
            
            # Players dos eventos
            events_response = self.supabase.table('match_events').select('player_id,player_name').not_.is_('player_id', 'null').limit(50).execute()
            for event in events_response.data:
                player_id = event.get('player_id')
                player_name = event.get('player_name')
                if player_id and player_name:
                    players_set.add((player_id, player_name))
            
            logger.info(f"📊 {len(players_set)} jogadores únicos encontrados para enriquecimento")
            
            enriched_count = 0
            for player_id, player_name in tqdm(players_set, desc="Enriquecendo jogadores"):
                try:
                    # Buscar dados detalhados do jogador
                    url = f"{self.base_url}/players/{player_id}"
                    response = self.make_request(url)
                    
                    player_data = response.get('data', {})
                    
                    if player_data:
                        enriched_player = {
                            'sportmonks_id': player_id,
                            'name': player_data.get('name', player_name),
                            'common_name': player_data.get('common_name'),
                            'firstname': player_data.get('firstname'),
                            'lastname': player_data.get('lastname'),
                            'nationality': player_data.get('nationality'),
                            'position_id': player_data.get('position_id'),
                            'position_name': player_data.get('position_name'),
                            'date_of_birth': player_data.get('date_of_birth'),
                            'height': player_data.get('height'),
                            'weight': player_data.get('weight'),
                            'image_path': player_data.get('image_path'),
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        self.supabase.table('players').upsert(enriched_player, on_conflict='sportmonks_id').execute()
                        enriched_count += 1
                    
                    # Pequena pausa para respeitar rate limit
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao enriquecer jogador {player_name} (ID: {player_id}): {str(e)}")
                    continue
            
            logger.info(f"✅ {enriched_count} jogadores enriquecidos com dados detalhados")
            return enriched_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer jogadores: {str(e)}")
            return 0
    
    def enriquecer_fixtures_detalhadas(self):
        """Enriquecer fixtures com dados mais detalhados"""
        logger.info("⚽ Enriquecendo fixtures com dados detalhados...")
        
        try:
            # Buscar algumas fixtures para enriquecer
            fixtures_response = self.supabase.table('fixtures').select('sportmonks_id').limit(20).execute()
            
            enriched_count = 0
            
            for fixture in tqdm(fixtures_response.data, desc="Enriquecendo fixtures"):
                fixture_id = fixture.get('sportmonks_id')
                
                try:
                    # Buscar dados detalhados da fixture
                    url = f"{self.base_url}/fixtures/{fixture_id}"
                    params = {'include': 'participants;state;venue;events;statistics;lineups;referees'}
                    response = self.make_request(url, params)
                    
                    detailed_fixture = response.get('data', {})
                    
                    if detailed_fixture:
                        # Processar venues
                        if 'venue' in detailed_fixture and detailed_fixture['venue']:
                            venue_data = {
                                'sportmonks_id': detailed_fixture['venue'].get('id'),
                                'name': detailed_fixture['venue'].get('name'),
                                'city': detailed_fixture['venue'].get('city_name'),
                                'capacity': detailed_fixture['venue'].get('capacity'),
                                'surface': detailed_fixture['venue'].get('surface'),
                                'country': detailed_fixture['venue'].get('country_name'),
                                'image_path': detailed_fixture['venue'].get('image_path'),
                                'updated_at': datetime.now().isoformat()
                            }
                            self.supabase.table('venues').upsert(venue_data, on_conflict='sportmonks_id').execute()
                        
                        # Processar árbitros
                        if 'referees' in detailed_fixture and detailed_fixture['referees']:
                            for referee in detailed_fixture['referees']:
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
                        
                        enriched_count += 1
                    
                    time.sleep(0.2)  # Rate limit
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao enriquecer fixture {fixture_id}: {str(e)}")
                    continue
            
            logger.info(f"✅ {enriched_count} fixtures enriquecidas com dados detalhados")
            return enriched_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer fixtures: {str(e)}")
            return 0
    
    def gerar_relatorio_final(self):
        """Gerar relatório final do enriquecimento"""
        logger.info("📊 Gerando relatório final...")
        
        try:
            # Contar registros em todas as tabelas
            all_tables = [
                'leagues', 'seasons', 'teams', 'fixtures', 
                'match_events', 'match_statistics', 'match_lineups',
                'countries', 'states', 'types', 'venues', 
                'referees', 'players', 'coaches', 'stages'
            ]
            
            total_records = 0
            logger.info("\n📋 CONTAGEM FINAL DE REGISTROS:")
            logger.info("=" * 60)
            
            for table in all_tables:
                try:
                    response = self.supabase.table(table).select('*', count='exact').execute()
                    count = response.count
                    total_records += count
                    status = "✅" if count > 0 else "❌"
                    logger.info(f"{status} {table:20}: {count:>8,} registros")
                except Exception as e:
                    logger.warning(f"⚠️ {table:20}: erro ao contar - {e}")
            
            logger.info("=" * 60)
            logger.info(f"📊 TOTAL GERAL: {total_records:>8,} registros")
            logger.info(f"📊 REQUISIÇÕES FEITAS: {self.requests_made}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {str(e)}")
    
    def executar_enriquecimento_api(self):
        """Executar enriquecimento usando API Sportmonks"""
        logger.info("=" * 80)
        logger.info("🚀 ENRIQUECENDO TABELAS COM API SPORTMONKS")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        total_enriched = 0
        
        # 1. Enriquecer árbitros
        total_enriched += self.enriquecer_referees_api()
        
        # 2. Enriquecer estádios
        total_enriched += self.enriquecer_venues_api()
        
        # 3. Enriquecer jogadores detalhados
        total_enriched += self.enriquecer_players_detalhados()
        
        # 4. Enriquecer fixtures detalhadas
        total_enriched += self.enriquecer_fixtures_detalhadas()
        
        # Tempo total
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Relatório final
        logger.info("=" * 80)
        logger.info("📊 RELATÓRIO FINAL DO ENRIQUECIMENTO COM API")
        logger.info("=" * 80)
        logger.info(f"⏱️ Tempo total: {duration}")
        logger.info(f"📈 Registros enriquecidos: {total_enriched:,}")
        logger.info(f"📊 Requisições feitas: {self.requests_made}")
        
        # Gerar relatório detalhado
        self.gerar_relatorio_final()
        
        logger.info("=" * 80)
        logger.info("🎉 ENRIQUECIMENTO COM API CONCLUÍDO!")
        logger.info("=" * 80)

def main():
    """Função principal"""
    
    logger.info("🚀 Iniciando enriquecimento com API Sportmonks...")
    
    try:
        # Executar enriquecimento
        enricher = SportmonksAPIEnricher()
        enricher.executar_enriquecimento_api()
        
    except Exception as e:
        logger.error(f"❌ Erro no processo principal: {str(e)}")
        raise

if __name__ == "__main__":
    main()
