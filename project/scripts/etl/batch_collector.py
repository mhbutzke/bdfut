#!/usr/bin/env python3
"""
Sistema de Batch Processing para ETL Sportmonks
===============================================

Este módulo implementa coleta em lote de múltiplas fixtures usando
o endpoint multi da API Sportmonks para otimizar performance.

Autor: ETL Engineer
Data: 17 de Janeiro de 2025
Task: 3.1 - Implementar Batch Processing para Múltiplas Fixtures
"""

import os
import time
import logging
import requests
import psycopg2
from psycopg2 import extras
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class BatchRequest:
    """Dados de uma requisição em lote"""
    fixture_ids: List[int]
    league_id: Optional[int] = None
    season_id: Optional[int] = None
    includes: List[str] = None
    batch_size: int = 100

@dataclass
class BatchResult:
    """Resultado de uma requisição em lote"""
    fixture_ids: List[int]
    successful_fixtures: List[Dict]
    failed_fixtures: List[int]
    errors: List[str]
    duration_ms: int
    api_calls_made: int

class SportmonksBatchAPI:
    """Cliente otimizado para requisições em lote da API Sportmonks"""
    
    BASE_URL = "https://api.sportmonks.com/v3/football"
    MAX_BATCH_SIZE = 100  # Limite da API Sportmonks
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.session = requests.Session()
        self.session.params = {'api_token': self.api_token}
        
        # Headers para otimização
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'BDFut-ETL/1.0',
            'Connection': 'keep-alive'
        })
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Faz requisição com retry automático"""
        url = f"{self.BASE_URL}/{endpoint}"
        full_params = {**self.session.params, **(params if params else {})}
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(f"Requesting: {url} with params {full_params}")
                response = self.session.get(url, params=full_params, timeout=30)
                response.raise_for_status()
                
                # Log de rate limiting
                remaining = int(response.headers.get('x-ratelimit-remaining', 3000))
                limit = int(response.headers.get('x-ratelimit-limit', 3000))
                logger.debug(f"Rate limit: {remaining}/{limit}")
                
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    retry_after = int(response.headers.get('retry-after', 60))
                    logger.warning(f"Rate limit hit. Retrying in {retry_after} seconds...")
                    time.sleep(retry_after)
                elif response.status_code == 400:
                    logger.error(f"Bad Request (400) for {url}: {e}")
                    return None
                else:
                    logger.error(f"HTTP error {response.status_code} for {url}: {e}")
                    if attempt < self.MAX_RETRIES - 1:
                        time.sleep(self.RETRY_DELAY * (2 ** attempt))  # Backoff exponencial
                    else:
                        logger.error(f"Max retries reached for {url}")
                        return None
                        
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {url}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (2 ** attempt))
                else:
                    logger.error(f"Max retries reached for {url}")
                    return None
        
        return None
    
    def get_fixtures_multi(self, fixture_ids: List[int], 
                          includes: List[str] = None) -> Optional[Dict]:
        """
        Coleta múltiplas fixtures em uma única requisição
        
        Args:
            fixture_ids: Lista de IDs das fixtures (máximo 100)
            includes: Lista de includes (ex: ['statistics', 'events', 'lineups'])
        
        Returns:
            Dados das fixtures ou None em caso de erro
        """
        if len(fixture_ids) > self.MAX_BATCH_SIZE:
            logger.warning(f"Batch size {len(fixture_ids)} exceeds limit {self.MAX_BATCH_SIZE}")
            fixture_ids = fixture_ids[:self.MAX_BATCH_SIZE]
        
        # Constrói parâmetros
        params = {
            'ids': ','.join(map(str, fixture_ids)),
            'per_page': len(fixture_ids)
        }
        
        if includes:
            params['include'] = ';'.join(includes)
        
        logger.info(f"Requesting {len(fixture_ids)} fixtures via multi endpoint")
        return self._make_request('fixtures/multi', params)
    
    def get_fixtures_by_league_season(self, league_id: int, season_id: int,
                                    includes: List[str] = None,
                                    page: int = 1, per_page: int = 500) -> Optional[Dict]:
        """
        Coleta fixtures por liga/temporada
        
        Args:
            league_id: ID da liga
            season_id: ID da temporada
            includes: Lista de includes
            page: Página (para paginação)
            per_page: Fixtures por página
        
        Returns:
            Dados das fixtures ou None em caso de erro
        """
        params = {
            'league_id': league_id,
            'season_id': season_id,
            'page': page,
            'per_page': per_page
        }
        
        if includes:
            params['include'] = ';'.join(includes)
        
        logger.info(f"Requesting fixtures for league {league_id}, season {season_id}")
        return self._make_request('fixtures', params)

class BatchCollector:
    """Coletor otimizado para processamento em lote"""
    
    def __init__(self, api_token: str, db_connection_string: str):
        self.api = SportmonksBatchAPI(api_token)
        self.db_connection_string = db_connection_string
        self.connection = None
    
    def connect(self):
        """Conecta ao banco de dados"""
        try:
            self.connection = psycopg2.connect(self.db_connection_string)
            logger.info("Conectado ao banco de dados para batch processing")
        except psycopg2.Error as e:
            logger.error(f"Erro ao conectar ao banco: {e}")
            raise
    
    def disconnect(self):
        """Desconecta do banco de dados"""
        if self.connection:
            self.connection.close()
            logger.info("Desconectado do banco de dados")
    
    def get_fixtures_for_batch(self, batch_size: int = 100, 
                              league_id: int = None, season_id: int = None) -> List[int]:
        """
        Obtém fixture IDs para processamento em lote
        
        Args:
            batch_size: Tamanho do lote
            league_id: Filtrar por liga (opcional)
            season_id: Filtrar por temporada (opcional)
        
        Returns:
            Lista de fixture IDs
        """
        try:
            cursor = self.connection.cursor()
            
            # Query para obter fixtures não processadas
            query = """
                SELECT fixture_id
                FROM fixtures
                WHERE last_processed_at IS NULL
                AND is_deleted = false
            """
            params = []
            
            if league_id:
                query += " AND league_id = %s"
                params.append(league_id)
            
            if season_id:
                query += " AND season_id = %s"
                params.append(season_id)
            
            query += " ORDER BY starting_at DESC LIMIT %s"
            params.append(batch_size)
            
            cursor.execute(query, params)
            fixture_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            logger.info(f"Encontradas {len(fixture_ids)} fixtures para processamento em lote")
            return fixture_ids
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao obter fixtures para lote: {e}")
            return []
    
    def process_batch(self, fixture_ids: List[int], 
                     includes: List[str] = None) -> BatchResult:
        """
        Processa um lote de fixtures
        
        Args:
            fixture_ids: Lista de fixture IDs
            includes: Lista de includes para enriquecimento
        
        Returns:
            Resultado do processamento em lote
        """
        start_time = time.time()
        api_calls_made = 0
        
        successful_fixtures = []
        failed_fixtures = []
        errors = []
        
        if not fixture_ids:
            logger.warning("Nenhuma fixture para processar")
            return BatchResult([], [], [], [], 0, 0)
        
        logger.info(f"Processando lote de {len(fixture_ids)} fixtures")
        
        try:
            # Faz requisição em lote
            api_calls_made += 1
            data = self.api.get_fixtures_multi(fixture_ids, includes)
            
            if data is None:
                logger.error("Falha na requisição em lote")
                return BatchResult(
                    fixture_ids, [], fixture_ids, 
                    ["Falha na requisição em lote"], 
                    int((time.time() - start_time) * 1000), api_calls_made
                )
            
            # Processa resposta
            fixtures_data = data.get('data', [])
            
            for fixture_data in fixtures_data:
                try:
                    # Valida dados básicos
                    if not fixture_data.get('id'):
                        failed_fixtures.append(fixture_data.get('id', 'unknown'))
                        errors.append(f"Fixture sem ID: {fixture_data}")
                        continue
                    
                    # Adiciona metadados de processamento
                    fixture_data['_processed_at'] = datetime.now(timezone.utc).isoformat()
                    fixture_data['_batch_size'] = len(fixture_ids)
                    
                    successful_fixtures.append(fixture_data)
                    
                except Exception as e:
                    fixture_id = fixture_data.get('id', 'unknown')
                    failed_fixtures.append(fixture_id)
                    errors.append(f"Erro ao processar fixture {fixture_id}: {e}")
                    logger.error(f"Erro ao processar fixture {fixture_id}: {e}")
            
            # Identifica fixtures que não retornaram dados
            returned_ids = {f.get('id') for f in fixtures_data}
            missing_ids = [fid for fid in fixture_ids if fid not in returned_ids]
            failed_fixtures.extend(missing_ids)
            
            if missing_ids:
                errors.append(f"Fixtures não retornadas pela API: {missing_ids}")
            
        except Exception as e:
            logger.error(f"Erro geral no processamento em lote: {e}")
            errors.append(f"Erro geral: {e}")
            failed_fixtures = fixture_ids.copy()
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        logger.info(f"Lote processado: {len(successful_fixtures)} sucessos, "
                   f"{len(failed_fixtures)} falhas, {duration_ms}ms, {api_calls_made} chamadas API")
        
        return BatchResult(
            fixture_ids, successful_fixtures, failed_fixtures, 
            errors, duration_ms, api_calls_made
        )
    
    def save_batch_results(self, result: BatchResult):
        """
        Salva resultados do lote no banco de dados
        
        Args:
            result: Resultado do processamento em lote
        """
        if not result.successful_fixtures:
            logger.info("Nenhuma fixture para salvar")
            return
        
        try:
            cursor = self.connection.cursor()
            
            # Prepara dados para upsert
            upsert_data = []
            for fixture_data in result.successful_fixtures:
                # Mapeia dados da API para estrutura do banco
                db_data = {
                    'fixture_id': fixture_data.get('id'),
                    'league_id': fixture_data.get('league_id'),
                    'season_id': fixture_data.get('season_id'),
                    'home_team_id': fixture_data.get('participants', [{}])[0].get('id') if fixture_data.get('participants') else None,
                    'away_team_id': fixture_data.get('participants', [{}])[1].get('id') if len(fixture_data.get('participants', [])) > 1 else None,
                    'starting_at': datetime.fromisoformat(fixture_data['starting_at']['date_time'].replace('Z', '+00:00')) if fixture_data.get('starting_at', {}).get('date_time') else None,
                    'status': fixture_data.get('status'),
                    'last_processed_at': datetime.now(timezone.utc),
                    'etl_version': 'v2.0-batch',
                    'data_quality_score': 100,
                    'has_events': bool(fixture_data.get('events')),
                    'has_lineups': bool(fixture_data.get('lineups')),
                    'has_statistics': bool(fixture_data.get('statistics'))
                }
                upsert_data.append(db_data)
            
            # Executa upsert em lote
            if upsert_data:
                # Usa executemany para inserção eficiente
                insert_query = """
                    INSERT INTO fixtures (
                        fixture_id, league_id, season_id, home_team_id, away_team_id,
                        starting_at, status, last_processed_at, etl_version,
                        data_quality_score, has_events, has_lineups, has_statistics
                    ) VALUES (
                        %(fixture_id)s, %(league_id)s, %(season_id)s, %(home_team_id)s, %(away_team_id)s,
                        %(starting_at)s, %(status)s, %(last_processed_at)s, %(etl_version)s,
                        %(data_quality_score)s, %(has_events)s, %(has_lineups)s, %(has_statistics)s
                    )
                    ON CONFLICT (fixture_id) DO UPDATE SET
                        league_id = EXCLUDED.league_id,
                        season_id = EXCLUDED.season_id,
                        home_team_id = EXCLUDED.home_team_id,
                        away_team_id = EXCLUDED.away_team_id,
                        starting_at = EXCLUDED.starting_at,
                        status = EXCLUDED.status,
                        last_processed_at = EXCLUDED.last_processed_at,
                        etl_version = EXCLUDED.etl_version,
                        data_quality_score = EXCLUDED.data_quality_score,
                        has_events = EXCLUDED.has_events,
                        has_lineups = EXCLUDED.has_lineups,
                        has_statistics = EXCLUDED.has_statistics,
                        updated_at = NOW()
                """
                
                cursor.executemany(insert_query, upsert_data)
                self.connection.commit()
                
                logger.info(f"Salvas {len(upsert_data)} fixtures no banco de dados")
            
            cursor.close()
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao salvar resultados do lote: {e}")
            self.connection.rollback()
            raise
    
    def process_chunk_batch(self, chunk_info: Dict, batch_size: int = 100) -> Dict:
        """
        Processa um chunk usando batch processing
        
        Args:
            chunk_info: Informações do chunk (league_id, season_id, etc.)
            batch_size: Tamanho do lote
        
        Returns:
            Estatísticas do processamento
        """
        start_time = time.time()
        
        league_id = chunk_info.get('league_id')
        season_id = chunk_info.get('season_id')
        
        logger.info(f"Processando chunk {league_id}/{season_id} com batch processing")
        
        # Obtém fixtures para o chunk
        fixture_ids = self.get_fixtures_for_batch(batch_size, league_id, season_id)
        
        if not fixture_ids:
            logger.info(f"Nenhuma fixture encontrada para chunk {league_id}/{season_id}")
            return {
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'api_calls': 0,
                'duration': 0
            }
        
        # Processa em lotes
        total_processed = 0
        total_successful = 0
        total_failed = 0
        total_api_calls = 0
        
        # Divide em lotes menores se necessário
        for i in range(0, len(fixture_ids), batch_size):
            batch_fixture_ids = fixture_ids[i:i + batch_size]
            
            # Processa lote
            result = self.process_batch(
                batch_fixture_ids, 
                includes=['statistics', 'events', 'lineups']
            )
            
            # Salva resultados
            if result.successful_fixtures:
                self.save_batch_results(result)
            
            # Acumula estatísticas
            total_processed += len(result.fixture_ids)
            total_successful += len(result.successful_fixtures)
            total_failed += len(result.failed_fixtures)
            total_api_calls += result.api_calls_made
            
            # Log de progresso
            logger.info(f"Lote {i//batch_size + 1}: {len(result.successful_fixtures)} sucessos, "
                       f"{len(result.failed_fixtures)} falhas")
        
        duration = time.time() - start_time
        
        logger.info(f"Chunk {league_id}/{season_id} concluído: "
                   f"{total_processed} processadas, {total_successful} sucessos, "
                   f"{total_failed} falhas, {total_api_calls} chamadas API, {duration:.2f}s")
        
        return {
            'processed': total_processed,
            'successful': total_successful,
            'failed': total_failed,
            'api_calls': total_api_calls,
            'duration': duration
        }

def create_batch_collector(api_token: str, db_connection_string: str) -> BatchCollector:
    """Cria instância do coletor em lote"""
    collector = BatchCollector(api_token, db_connection_string)
    collector.connect()
    return collector
