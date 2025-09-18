#!/usr/bin/env python3
"""
Script de Coleta Incremental para ETL Sportmonks
=================================================

Este script implementa coleta incremental otimizada usando as funções SQL
criadas na Task 2.1 e seguindo as melhores práticas do Agente ETL.

Autor: ETL Engineer
Data: 17 de Janeiro de 2025
Task: 2.2 - Criar Script Python de Coleta Incremental
"""

import os
import sys
import time
import logging
import requests
import psycopg2
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_incremental.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class FixtureData:
    """Estrutura de dados para fixture"""
    fixture_id: int
    league_id: int
    season_id: int
    home_team_id: int
    away_team_id: int
    starting_at: Optional[datetime]
    collection_reason: str
    priority_score: int

@dataclass
class CollectionStats:
    """Estatísticas de coleta"""
    total_processed: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    start_time: datetime = None
    end_time: datetime = None

class SportmonksAPIClient:
    """Cliente para API Sportmonks v3 com rate limiting"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.sportmonks.com/v3/football"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json',
            'User-Agent': 'BDFut-ETL/1.0'
        })
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms entre requests (10 req/s)
    
    def _rate_limit(self):
        """Implementa rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def get_fixture(self, fixture_id: int, includes: str = "events,lineups,statistics") -> Optional[Dict]:
        """
        Obtém dados de uma fixture específica
        
        Args:
            fixture_id: ID da fixture
            includes: Includes da API (events,lineups,statistics)
        
        Returns:
            Dados da fixture ou None se erro
        """
        self._rate_limit()
        
        # ✅ SINTAXE CORRETA OBRIGATÓRIA (Agente ETL)
        params = {
            'id': fixture_id,
            'include': includes,
            'per_page': 1
        }
        
        try:
            url = urljoin(self.base_url, f"/fixtures/{fixture_id}")
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    return data['data']
                else:
                    logger.warning(f"Fixture {fixture_id} não encontrada na API")
                    return None
            elif response.status_code == 429:
                logger.warning(f"Rate limit atingido para fixture {fixture_id}")
                time.sleep(1)  # Aguarda 1 segundo
                return self.get_fixture(fixture_id, includes)  # Retry
            else:
                logger.error(f"Erro API para fixture {fixture_id}: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexão para fixture {fixture_id}: {e}")
            return None

class DatabaseManager:
    """Gerenciador de conexão com Supabase"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
    
    def connect(self):
        """Conecta ao banco de dados"""
        try:
            self.connection = psycopg2.connect(self.connection_string)
            logger.info("Conectado ao banco de dados Supabase")
        except psycopg2.Error as e:
            logger.error(f"Erro ao conectar ao banco: {e}")
            raise
    
    def disconnect(self):
        """Desconecta do banco de dados"""
        if self.connection:
            self.connection.close()
            logger.info("Desconectado do banco de dados")
    
    def get_fixtures_for_collection(self, batch_size: int = 100, 
                                  league_id: Optional[int] = None,
                                  season_id: Optional[int] = None) -> List[FixtureData]:
        """Obtém fixtures para coleta incremental"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT fixture_id, league_id, season_id, home_team_id, away_team_id,
                       starting_at, collection_reason, priority_score
                FROM get_fixtures_for_incremental_collection(%s, %s, %s, 24)
            """, (batch_size, league_id, season_id))
            
            fixtures = []
            for row in cursor.fetchall():
                fixtures.append(FixtureData(
                    fixture_id=row[0],
                    league_id=row[1],
                    season_id=row[2],
                    home_team_id=row[3],
                    away_team_id=row[4],
                    starting_at=row[5],
                    collection_reason=row[6],
                    priority_score=row[7]
                ))
            
            cursor.close()
            return fixtures
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao obter fixtures: {e}")
            return []
    
    def update_fixture_metadata(self, fixture_id: int, etl_version: str = "v1.0",
                               data_quality_score: int = 100,
                               has_events: Optional[bool] = None,
                               has_lineups: Optional[bool] = None,
                               has_statistics: Optional[bool] = None) -> bool:
        """Atualiza metadados ETL de uma fixture"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT update_fixture_etl_metadata(%s, %s, %s, %s, %s, %s)
            """, (fixture_id, etl_version, data_quality_score, 
                  has_events, has_lineups, has_statistics))
            
            result = cursor.fetchone()[0]
            cursor.close()
            self.connection.commit()
            return result
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao atualizar metadados da fixture {fixture_id}: {e}")
            self.connection.rollback()
            return False
    
    def get_collection_stats(self) -> Dict:
        """Obtém estatísticas de coleta"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM get_incremental_collection_stats()")
            row = cursor.fetchone()
            cursor.close()
            
            return {
                'total_fixtures': row[0],
                'unprocessed_fixtures': row[1],
                'recently_updated_fixtures': row[2],
                'incomplete_data_fixtures': row[3],
                'low_quality_fixtures': row[4],
                'old_version_fixtures': row[5],
                'last_collection_time': row[6]
            }
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}

class IncrementalCollector:
    """Coletor incremental principal"""
    
    def __init__(self, api_key: str, db_connection_string: str):
        self.api_client = SportmonksAPIClient(api_key)
        self.db_manager = DatabaseManager(db_connection_string)
        self.stats = CollectionStats()
    
    def process_fixture(self, fixture: FixtureData) -> bool:
        """
        Processa uma fixture individual
        
        Args:
            fixture: Dados da fixture para processar
        
        Returns:
            True se sucesso, False se erro
        """
        try:
            logger.info(f"Processando fixture {fixture.fixture_id} (prioridade: {fixture.priority_score})")
            
            # Determina includes baseado no motivo da coleta
            includes = self._get_includes_for_reason(fixture.collection_reason)
            
            # Coleta dados da API
            api_data = self.api_client.get_fixture(fixture.fixture_id, includes)
            
            if not api_data:
                logger.warning(f"Dados não encontrados para fixture {fixture.fixture_id}")
                return self.db_manager.update_fixture_metadata(
                    fixture.fixture_id, 
                    data_quality_score=0
                )
            
            # Calcula qualidade dos dados
            quality_score = self._calculate_data_quality(api_data)
            
            # Determina flags de dados disponíveis
            has_events = 'events' in api_data and len(api_data.get('events', [])) > 0
            has_lineups = 'lineups' in api_data and len(api_data.get('lineups', [])) > 0
            has_statistics = 'statistics' in api_data and len(api_data.get('statistics', [])) > 0
            
            # Atualiza metadados no banco
            success = self.db_manager.update_fixture_metadata(
                fixture.fixture_id,
                etl_version="v1.0",
                data_quality_score=quality_score,
                has_events=has_events,
                has_lineups=has_lineups,
                has_statistics=has_statistics
            )
            
            if success:
                logger.info(f"Fixture {fixture.fixture_id} processada com sucesso (qualidade: {quality_score})")
                return True
            else:
                logger.error(f"Erro ao atualizar metadados da fixture {fixture.fixture_id}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao processar fixture {fixture.fixture_id}: {e}")
            return False
    
    def _get_includes_for_reason(self, reason: str) -> str:
        """Determina includes baseado no motivo da coleta"""
        if reason == "NEVER_PROCESSED":
            return "events,lineups,statistics"
        elif reason == "INCOMPLETE_DATA":
            return "events,lineups,statistics"
        elif reason == "UPDATED_RECENTLY":
            return "events,lineups,statistics"
        else:
            return "events,lineups,statistics"
    
    def _calculate_data_quality(self, api_data: Dict) -> int:
        """Calcula score de qualidade dos dados"""
        score = 0
        
        # Dados básicos (40 pontos)
        if api_data.get('name'):
            score += 10
        if api_data.get('starting_at'):
            score += 10
        if api_data.get('home_team_id') and api_data.get('away_team_id'):
            score += 10
        if api_data.get('league_id') and api_data.get('season_id'):
            score += 10
        
        # Dados de resultado (30 pontos)
        if api_data.get('home_score') is not None and api_data.get('away_score') is not None:
            score += 30
        
        # Dados enriquecidos (30 pontos)
        if api_data.get('events') and len(api_data['events']) > 0:
            score += 10
        if api_data.get('lineups') and len(api_data['lineups']) > 0:
            score += 10
        if api_data.get('statistics') and len(api_data['statistics']) > 0:
            score += 10
        
        return min(score, 100)
    
    def run_collection(self, batch_size: int = 100, 
                      league_id: Optional[int] = None,
                      season_id: Optional[int] = None,
                      max_fixtures: Optional[int] = None) -> CollectionStats:
        """
        Executa coleta incremental
        
        Args:
            batch_size: Tamanho do lote
            league_id: Filtrar por liga
            season_id: Filtrar por temporada
            max_fixtures: Máximo de fixtures para processar
        
        Returns:
            Estatísticas da coleta
        """
        self.stats = CollectionStats()
        self.stats.start_time = datetime.now()
        
        try:
            # Conecta ao banco
            self.db_manager.connect()
            
            # Log de início
            logger.info("=== INICIANDO COLETA INCREMENTAL ===")
            stats_before = self.db_manager.get_collection_stats()
            logger.info(f"Estatísticas antes da coleta: {stats_before}")
            
            # Obtém fixtures para processar
            fixtures = self.db_manager.get_fixtures_for_collection(
                batch_size=batch_size,
                league_id=league_id,
                season_id=season_id
            )
            
            if not fixtures:
                logger.info("Nenhuma fixture encontrada para processar")
                return self.stats
            
            logger.info(f"Encontradas {len(fixtures)} fixtures para processar")
            
            # Processa fixtures
            processed_count = 0
            for fixture in fixtures:
                if max_fixtures and processed_count >= max_fixtures:
                    logger.info(f"Limite de {max_fixtures} fixtures atingido")
                    break
                
                success = self.process_fixture(fixture)
                processed_count += 1
                
                if success:
                    self.stats.successful += 1
                else:
                    self.stats.failed += 1
                
                self.stats.total_processed += 1
                
                # Log de progresso a cada 10 fixtures
                if processed_count % 10 == 0:
                    logger.info(f"Progresso: {processed_count}/{len(fixtures)} fixtures processadas")
            
            # Log de finalização
            self.stats.end_time = datetime.now()
            duration = self.stats.end_time - self.stats.start_time
            
            logger.info("=== COLETA INCREMENTAL CONCLUÍDA ===")
            logger.info(f"Total processadas: {self.stats.total_processed}")
            logger.info(f"Sucessos: {self.stats.successful}")
            logger.info(f"Falhas: {self.stats.failed}")
            logger.info(f"Duração: {duration}")
            logger.info(f"Taxa: {self.stats.total_processed / duration.total_seconds() * 60:.1f} fixtures/min")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Erro durante coleta incremental: {e}")
            raise
        finally:
            self.db_manager.disconnect()

def main():
    """Função principal"""
    # Configuração via variáveis de ambiente
    api_key = os.getenv('SPORTMONKS_API_KEY')
    db_connection_string = os.getenv('SUPABASE_CONNECTION_STRING')
    
    if not api_key:
        logger.error("SPORTMONKS_API_KEY não definida")
        sys.exit(1)
    
    if not db_connection_string:
        logger.error("SUPABASE_CONNECTION_STRING não definida")
        sys.exit(1)
    
    # Cria coletor
    collector = IncrementalCollector(api_key, db_connection_string)
    
    # Executa coleta
    try:
        stats = collector.run_collection(
            batch_size=50,  # Processa 50 fixtures por vez
            max_fixtures=100  # Limite para teste inicial
        )
        
        logger.info(f"Coleta concluída: {stats.successful}/{stats.total_processed} sucessos")
        
    except KeyboardInterrupt:
        logger.info("Coleta interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
