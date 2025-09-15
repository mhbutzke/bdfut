"""
Processo principal de ETL para dados da Sportmonks API
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from tqdm import tqdm
import time

from .sportmonks_client import SportmonksClient
from .supabase_client import SupabaseClient
from .etl_metadata import ETLMetadataManager, ETLJobContext
from ..config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ETLProcess:
    """Coordena o processo de ETL dos dados"""
    
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.metadata_manager = ETLMetadataManager()
        self.main_leagues = Config.MAIN_LEAGUES
    
    def sync_base_data(self):
        """Sincroniza dados base (countries, states, types)"""
        with ETLJobContext(
            job_name="sync_base_data",
            job_type="base_data",
            metadata_manager=self.metadata_manager,
            script_path="bdfut/core/etl_process.py"
        ) as job:
            
            logger.info("Iniciando sincronização de dados base...")
            job.log("INFO", "Iniciando sincronização de dados base")
            
            total_records = 0
            
            # Sincronizar States
            logger.info("Sincronizando states...")
            job.log("INFO", "Sincronizando states")
            states = self.sportmonks.get_states()
            job.increment_api_requests(1)
            
            if states:
                self.supabase.upsert_states(states)
                job.increment_records(processed=len(states), inserted=len(states))
                total_records += len(states)
                logger.info(f"✅ {len(states)} states sincronizados")
                job.log("INFO", f"States sincronizados: {len(states)}")
            
            # Checkpoint após states
            job.checkpoint("states_completed", {
                "states_count": len(states) if states else 0,
                "next_step": "types"
            }, progress_percentage=33.0)
            
            # Sincronizar Types
            logger.info("Sincronizando types...")
            job.log("INFO", "Sincronizando types")
            types = self.sportmonks.get_types()
            job.increment_api_requests(1)
            
            if types:
                self.supabase.upsert_types(types)
                job.increment_records(processed=len(types), inserted=len(types))
                total_records += len(types)
                logger.info(f"✅ {len(types)} types sincronizados")
                job.log("INFO", f"Types sincronizados: {len(types)}")
            
            # Checkpoint após types
            job.checkpoint("types_completed", {
                "types_count": len(types) if types else 0,
                "next_step": "countries"
            }, progress_percentage=66.0)
            
            # Sincronizar Countries
            logger.info("Sincronizando countries...")
            job.log("INFO", "Sincronizando countries")
            countries = self.sportmonks.get_countries()
            job.increment_api_requests(1)
            
            if countries:
                self.supabase.upsert_countries(countries)
                job.increment_records(processed=len(countries), inserted=len(countries))
                total_records += len(countries)
                logger.info(f"✅ {len(countries)} countries sincronizados")
                job.log("INFO", f"Countries sincronizados: {len(countries)}")
            
            # Checkpoint final
            job.checkpoint("base_data_completed", {
                "states_count": len(states) if states else 0,
                "types_count": len(types) if types else 0,
                "countries_count": len(countries) if countries else 0,
                "total_records": total_records
            }, progress_percentage=100.0)
            
            logger.info("✅ Dados base sincronizados com sucesso!")
            job.log("INFO", f"Dados base sincronizados com sucesso - Total: {total_records} registros")
    
    def sync_leagues(self, league_ids: Optional[List[int]] = None):
        """Sincroniza ligas e suas temporadas"""
        if league_ids is None:
            league_ids = self.main_leagues
        
        logger.info(f"Sincronizando {len(league_ids)} ligas...")
        
        leagues_data = []
        seasons_data = []
        
        for league_id in tqdm(league_ids, desc="Ligas"):
            try:
                # Buscar dados da liga com temporadas
                league = self.sportmonks.get_league_by_id(league_id, include='seasons')
                if league:
                    leagues_data.append(league)
                    
                    # Extrair temporadas
                    if 'seasons' in league:
                        seasons_data.extend(league['seasons'])
                
                # Pequena pausa entre requisições
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Erro ao buscar liga {league_id}: {str(e)}")
                continue
        
        # Salvar ligas
        if leagues_data:
            self.supabase.upsert_leagues(leagues_data)
            logger.info(f"✅ {len(leagues_data)} ligas sincronizadas")
        
        # Salvar temporadas
        if seasons_data:
            self.supabase.upsert_seasons(seasons_data)
            logger.info(f"✅ {len(seasons_data)} temporadas sincronizadas")
    
    def sync_teams_by_season(self, season_id: int):
        """Sincroniza times de uma temporada específica"""
        logger.info(f"Sincronizando times da temporada {season_id}...")
        
        try:
            teams = self.sportmonks.get_teams_by_season(season_id, include='venue')
            
            if teams:
                # Extrair venues
                venues_data = []
                for team in teams:
                    if 'venue' in team and team['venue']:
                        venues_data.append(team['venue'])
                
                # Salvar venues primeiro
                if venues_data:
                    self.supabase.upsert_venues(venues_data)
                    logger.info(f"✅ {len(venues_data)} venues sincronizados")
                
                # Salvar times
                self.supabase.upsert_teams(teams)
                logger.info(f"✅ {len(teams)} times sincronizados")
                
                return True
        except Exception as e:
            logger.error(f"Erro ao sincronizar times da temporada {season_id}: {str(e)}")
            return False
    
    def sync_fixtures_by_date_range(self, start_date: str, end_date: str, 
                                    include_details: bool = False):
        """
        Sincroniza partidas em um intervalo de datas
        
        Args:
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            include_details: Se deve incluir detalhes completos das partidas
        """
        logger.info(f"Sincronizando partidas de {start_date} até {end_date}...")
        
        # Includes básicos
        includes = 'participants;state;venue'
        
        if include_details:
            includes += ';events;statistics;lineups;referees'
        
        try:
            fixtures = self.sportmonks.get_fixtures_by_date_range(
                start_date, end_date, include=includes
            )
            
            if fixtures:
                # Processar venues
                venues_data = []
                for fixture in fixtures:
                    if 'venue' in fixture and fixture['venue']:
                        venues_data.append(fixture['venue'])
                
                if venues_data:
                    self.supabase.upsert_venues(venues_data)
                
                # Processar árbitros se incluídos
                if include_details:
                    referees_data = []
                    for fixture in fixtures:
                        if 'referees' in fixture and fixture['referees']:
                            referees_data.extend(fixture['referees'])
                    
                    if referees_data:
                        self.supabase.upsert_referees(referees_data)
                
                # Salvar fixtures
                self.supabase.upsert_fixtures(fixtures)
                logger.info(f"✅ {len(fixtures)} partidas sincronizadas")
                
                # Processar participantes e detalhes
                for fixture in tqdm(fixtures, desc="Processando detalhes"):
                    fixture_id = fixture['id']
                    
                    # Participantes
                    if 'participants' in fixture:
                        self.supabase.upsert_fixture_participants(
                            fixture_id, fixture['participants']
                        )
                    
                    # Eventos (se incluídos)
                    if 'events' in fixture and fixture['events']:
                        self.supabase.upsert_fixture_events(
                            fixture_id, fixture['events']
                        )
                
                return True
                
        except Exception as e:
            logger.error(f"Erro ao sincronizar partidas: {str(e)}")
            return False
    
    def sync_recent_fixtures(self, days_back: int = 7, days_forward: int = 7):
        """Sincroniza partidas recentes e próximas"""
        end_date = (datetime.now() + timedelta(days=days_forward)).strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        return self.sync_fixtures_by_date_range(start_date, end_date, include_details=True)
    
    def sync_fixture_details(self, fixture_id: int):
        """Sincroniza detalhes completos de uma partida específica"""
        logger.info(f"Sincronizando detalhes da partida {fixture_id}...")
        
        try:
            fixture = self.sportmonks.get_fixture_by_id(
                fixture_id,
                include='participants;state;venue;events;statistics;lineups;referees'
            )
            
            if fixture:
                # Processar todas as entidades relacionadas
                if 'venue' in fixture and fixture['venue']:
                    self.supabase.upsert_venues([fixture['venue']])
                
                if 'referees' in fixture and fixture['referees']:
                    self.supabase.upsert_referees(fixture['referees'])
                
                # Salvar fixture
                self.supabase.upsert_fixtures([fixture])
                
                # Participantes
                if 'participants' in fixture:
                    self.supabase.upsert_fixture_participants(
                        fixture_id, fixture['participants']
                    )
                
                # Eventos
                if 'events' in fixture and fixture['events']:
                    self.supabase.upsert_fixture_events(
                        fixture_id, fixture['events']
                    )
                
                logger.info(f"✅ Detalhes da partida {fixture_id} sincronizados")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao sincronizar detalhes da partida {fixture_id}: {str(e)}")
            return False
    
    def full_sync(self):
        """Executa sincronização completa dos dados principais"""
        logger.info("=" * 50)
        logger.info("INICIANDO SINCRONIZAÇÃO COMPLETA")
        logger.info("=" * 50)
        
        # 1. Dados base
        self.sync_base_data()
        
        # 2. Ligas principais
        self.sync_leagues()
        
        # 3. Times das temporadas atuais
        logger.info("Sincronizando times das temporadas atuais...")
        # Aqui você precisaria buscar as temporadas atuais das ligas principais
        # Por simplicidade, vamos usar IDs fixos de temporadas conhecidas
        
        # 4. Partidas recentes e próximas
        self.sync_recent_fixtures(days_back=30, days_forward=30)
        
        logger.info("=" * 50)
        logger.info("✅ SINCRONIZAÇÃO COMPLETA FINALIZADA!")
        logger.info("=" * 50)
    
    def incremental_sync(self):
        """Executa sincronização incremental (apenas atualizações)"""
        logger.info("Executando sincronização incremental...")
        
        # Sincronizar partidas dos últimos 2 dias e próximos 14 dias
        self.sync_recent_fixtures(days_back=2, days_forward=14)
        
        logger.info("✅ Sincronização incremental concluída!")
