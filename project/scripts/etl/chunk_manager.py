#!/usr/bin/env python3
"""
Gerenciador de Chunks para ETL Sportmonks
=========================================

Este módulo implementa o sistema de chunks por liga/temporada para
otimizar a coleta incremental de dados.

Autor: ETL Engineer
Data: 17 de Janeiro de 2025
Task: 2.3 - Implementar Sistema de Chunks por Liga/Temporada
"""

import logging
import psycopg2
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import time

logger = logging.getLogger(__name__)

@dataclass
class ChunkInfo:
    """Informações de um chunk (liga/temporada)"""
    league_id: int
    season_id: int
    league_name: Optional[str]
    season_name: Optional[str]
    fixture_count: int
    unprocessed_count: int
    priority_score: int

@dataclass
class ChunkStats:
    """Estatísticas do sistema de chunks"""
    total_chunks: int
    high_priority_chunks: int
    medium_priority_chunks: int
    low_priority_chunks: int
    total_unprocessed_fixtures: int
    avg_fixtures_per_chunk: float

class ChunkManager:
    """Gerenciador de chunks para processamento em lotes"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
    
    def connect(self):
        """Conecta ao banco de dados"""
        try:
            self.connection = psycopg2.connect(self.connection_string)
            logger.info("Conectado ao banco de dados para gerenciamento de chunks")
        except psycopg2.Error as e:
            logger.error(f"Erro ao conectar ao banco: {e}")
            raise
    
    def disconnect(self):
        """Desconecta do banco de dados"""
        if self.connection:
            self.connection.close()
            logger.info("Desconectado do banco de dados")
    
    def get_chunks(self, chunk_size: int = 100, min_fixtures: int = 10) -> List[ChunkInfo]:
        """
        Obtém lista de chunks ordenados por prioridade
        
        Args:
            chunk_size: Número máximo de chunks a retornar
            min_fixtures: Número mínimo de fixtures por chunk
        
        Returns:
            Lista de chunks ordenados por prioridade
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT league_id, season_id, league_name, season_name,
                       fixture_count, unprocessed_count, priority_score
                FROM get_league_season_chunks(%s, %s)
            """, (chunk_size, min_fixtures))
            
            chunks = []
            for row in cursor.fetchall():
                chunks.append(ChunkInfo(
                    league_id=row[0],
                    season_id=row[1],
                    league_name=row[2],
                    season_name=row[3],
                    fixture_count=row[4],
                    unprocessed_count=row[5],
                    priority_score=row[6]
                ))
            
            cursor.close()
            logger.info(f"Obtidos {len(chunks)} chunks para processamento")
            return chunks
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao obter chunks: {e}")
            return []
    
    def get_chunk_statistics(self) -> ChunkStats:
        """Obtém estatísticas do sistema de chunks"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM get_chunk_statistics()")
            row = cursor.fetchone()
            cursor.close()
            
            return ChunkStats(
                total_chunks=row[0],
                high_priority_chunks=row[1],
                medium_priority_chunks=row[2],
                low_priority_chunks=row[3],
                total_unprocessed_fixtures=row[4],
                avg_fixtures_per_chunk=float(row[5])
            )
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao obter estatísticas de chunks: {e}")
            return ChunkStats(0, 0, 0, 0, 0, 0.0)
    
    def get_fixtures_for_chunk(self, league_id: int, season_id: int, 
                              batch_size: int = 100) -> List[Dict]:
        """
        Obtém fixtures de um chunk específico
        
        Args:
            league_id: ID da liga
            season_id: ID da temporada
            batch_size: Tamanho do lote de fixtures
        
        Returns:
            Lista de fixtures do chunk
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT fixture_id, league_id, season_id, home_team_id, away_team_id,
                       starting_at, collection_reason, priority_score
                FROM get_fixtures_for_chunk(%s, %s, %s, 24)
            """, (league_id, season_id, batch_size))
            
            fixtures = []
            for row in cursor.fetchall():
                fixtures.append({
                    'fixture_id': row[0],
                    'league_id': row[1],
                    'season_id': row[2],
                    'home_team_id': row[3],
                    'away_team_id': row[4],
                    'starting_at': row[5],
                    'collection_reason': row[6],
                    'priority_score': row[7]
                })
            
            cursor.close()
            return fixtures
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao obter fixtures do chunk {league_id}/{season_id}: {e}")
            return []
    
    def log_chunk_progress(self, chunk: ChunkInfo, processed: int, 
                          successful: int, failed: int, duration: float):
        """Registra progresso de um chunk"""
        logger.info(f"Chunk {chunk.league_id}/{chunk.season_id} concluído:")
        logger.info(f"  Fixtures processadas: {processed}/{chunk.unprocessed_count}")
        logger.info(f"  Sucessos: {successful}, Falhas: {failed}")
        logger.info(f"  Duração: {duration:.2f}s")
        if duration > 0:
            rate = processed / duration
            logger.info(f"  Taxa: {rate:.1f} fixtures/s")

class ChunkProcessor:
    """Processador de chunks com checkpoint e recuperação"""
    
    def __init__(self, chunk_manager: ChunkManager, incremental_collector):
        self.chunk_manager = chunk_manager
        self.collector = incremental_collector
        self.checkpoint_file = "chunk_checkpoint.json"
        self.processed_chunks = set()
    
    def load_checkpoint(self):
        """Carrega checkpoint de chunks processados"""
        try:
            import json
            with open(self.checkpoint_file, 'r') as f:
                data = json.load(f)
                self.processed_chunks = set(data.get('processed_chunks', []))
            logger.info(f"Checkpoint carregado: {len(self.processed_chunks)} chunks processados")
        except FileNotFoundError:
            logger.info("Nenhum checkpoint encontrado, iniciando do zero")
        except Exception as e:
            logger.warning(f"Erro ao carregar checkpoint: {e}")
    
    def save_checkpoint(self):
        """Salva checkpoint de chunks processados"""
        try:
            import json
            data = {
                'processed_chunks': list(self.processed_chunks),
                'last_update': datetime.now().isoformat()
            }
            with open(self.checkpoint_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Checkpoint salvo: {len(self.processed_chunks)} chunks processados")
        except Exception as e:
            logger.error(f"Erro ao salvar checkpoint: {e}")
    
    def is_chunk_processed(self, league_id: int, season_id: int) -> bool:
        """Verifica se um chunk já foi processado"""
        chunk_key = f"{league_id}_{season_id}"
        return chunk_key in self.processed_chunks
    
    def mark_chunk_processed(self, league_id: int, season_id: int):
        """Marca um chunk como processado"""
        chunk_key = f"{league_id}_{season_id}"
        self.processed_chunks.add(chunk_key)
    
    def process_chunk(self, chunk: ChunkInfo, batch_size: int = 100) -> Dict:
        """
        Processa um chunk específico
        
        Args:
            chunk: Informações do chunk
            batch_size: Tamanho do lote de fixtures
        
        Returns:
            Estatísticas do processamento
        """
        start_time = time.time()
        
        logger.info(f"Processando chunk {chunk.league_id}/{chunk.season_id}")
        logger.info(f"  Liga: {chunk.league_name or 'N/A'}")
        logger.info(f"  Temporada: {chunk.season_name or 'N/A'}")
        logger.info(f"  Fixtures não processadas: {chunk.unprocessed_count}")
        logger.info(f"  Prioridade: {chunk.priority_score}")
        
        # Obtém fixtures do chunk
        fixtures = self.chunk_manager.get_fixtures_for_chunk(
            chunk.league_id, chunk.season_id, batch_size
        )
        
        if not fixtures:
            logger.info(f"Nenhuma fixture encontrada no chunk {chunk.league_id}/{chunk.season_id}")
            return {'processed': 0, 'successful': 0, 'failed': 0}
        
        logger.info(f"Encontradas {len(fixtures)} fixtures para processar no chunk")
        
        # Processa fixtures
        successful = 0
        failed = 0
        
        for fixture_data in fixtures:
            try:
                # Converte para objeto FixtureData
                from incremental_collector import FixtureData
                fixture = FixtureData(
                    fixture_id=fixture_data['fixture_id'],
                    league_id=fixture_data['league_id'],
                    season_id=fixture_data['season_id'],
                    home_team_id=fixture_data['home_team_id'],
                    away_team_id=fixture_data['away_team_id'],
                    starting_at=fixture_data['starting_at'],
                    collection_reason=fixture_data['collection_reason'],
                    priority_score=fixture_data['priority_score']
                )
                
                # Processa fixture
                if self.collector.process_fixture(fixture):
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Erro ao processar fixture {fixture_data['fixture_id']}: {e}")
                failed += 1
        
        # Calcula estatísticas
        duration = time.time() - start_time
        processed = successful + failed
        
        # Log de progresso
        self.chunk_manager.log_chunk_progress(chunk, processed, successful, failed, duration)
        
        # Marca chunk como processado
        self.mark_chunk_processed(chunk.league_id, chunk.season_id)
        
        return {
            'processed': processed,
            'successful': successful,
            'failed': failed,
            'duration': duration
        }
    
    def process_all_chunks(self, max_chunks: Optional[int] = None, 
                          batch_size: int = 100, min_fixtures: int = 10) -> Dict:
        """
        Processa todos os chunks disponíveis
        
        Args:
            max_chunks: Máximo de chunks para processar
            batch_size: Tamanho do lote de fixtures
            min_fixtures: Número mínimo de fixtures por chunk
        
        Returns:
            Estatísticas gerais do processamento
        """
        start_time = time.time()
        
        # Carrega checkpoint
        self.load_checkpoint()
        
        # Conecta ao banco
        self.chunk_manager.connect()
        
        try:
            # Obtém estatísticas iniciais
            initial_stats = self.chunk_manager.get_chunk_statistics()
            logger.info("=== INICIANDO PROCESSAMENTO DE CHUNKS ===")
            logger.info(f"Total de chunks: {initial_stats.total_chunks}")
            logger.info(f"Chunks de alta prioridade: {initial_stats.high_priority_chunks}")
            logger.info(f"Chunks de média prioridade: {initial_stats.medium_priority_chunks}")
            logger.info(f"Chunks de baixa prioridade: {initial_stats.low_priority_chunks}")
            logger.info(f"Total de fixtures não processadas: {initial_stats.total_unprocessed_fixtures:,}")
            logger.info(f"Média de fixtures por chunk: {initial_stats.avg_fixtures_per_chunk:.1f}")
            
            # Obtém chunks para processar
            chunks = self.chunk_manager.get_chunks(
                chunk_size=max_chunks or 1000,
                min_fixtures=min_fixtures
            )
            
            if not chunks:
                logger.info("Nenhum chunk encontrado para processar")
                return {'total_chunks': 0, 'total_processed': 0, 'total_successful': 0, 'total_failed': 0}
            
            logger.info(f"Processando {len(chunks)} chunks")
            
            # Processa chunks
            total_processed = 0
            total_successful = 0
            total_failed = 0
            processed_chunks = 0
            
            for i, chunk in enumerate(chunks, 1):
                # Verifica se chunk já foi processado
                if self.is_chunk_processed(chunk.league_id, chunk.season_id):
                    logger.info(f"Chunk {chunk.league_id}/{chunk.season_id} já processado, pulando")
                    continue
                
                logger.info(f"Processando chunk {i}/{len(chunks)}: {chunk.league_id}/{chunk.season_id}")
                
                # Processa chunk
                chunk_stats = self.process_chunk(chunk, batch_size)
                
                total_processed += chunk_stats['processed']
                total_successful += chunk_stats['successful']
                total_failed += chunk_stats['failed']
                processed_chunks += 1
                
                # Salva checkpoint a cada 10 chunks
                if processed_chunks % 10 == 0:
                    self.save_checkpoint()
                    logger.info(f"Checkpoint salvo após {processed_chunks} chunks")
                
                # Log de progresso geral
                if i % 10 == 0:
                    logger.info(f"Progresso geral: {i}/{len(chunks)} chunks processados")
            
            # Salva checkpoint final
            self.save_checkpoint()
            
            # Calcula estatísticas finais
            total_duration = time.time() - start_time
            
            logger.info("=== PROCESSAMENTO DE CHUNKS CONCLUÍDO ===")
            logger.info(f"Chunks processados: {processed_chunks}")
            logger.info(f"Total de fixtures processadas: {total_processed}")
            logger.info(f"Sucessos: {total_successful}")
            logger.info(f"Falhas: {total_failed}")
            logger.info(f"Duração total: {total_duration:.2f}s")
            if total_duration > 0:
                rate = total_processed / total_duration
                logger.info(f"Taxa média: {rate:.1f} fixtures/s")
            
            return {
                'total_chunks': processed_chunks,
                'total_processed': total_processed,
                'total_successful': total_successful,
                'total_failed': total_failed,
                'total_duration': total_duration
            }
            
        finally:
            self.chunk_manager.disconnect()
