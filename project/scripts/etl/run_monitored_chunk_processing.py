#!/usr/bin/env python3
"""
Script de Processamento de Chunks com Monitoramento
==================================================

Script principal para executar processamento de chunks com monitoramento
avançado, logs estruturados e métricas de performance.

Autor: ETL Engineer
Data: 17 de Janeiro de 2025
Task: 2.4 - Script Integrado de Chunks com Monitoramento
"""

import argparse
import sys
import os
from datetime import datetime
import time

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.chunk_manager import ChunkManager, ChunkProcessor
from etl.incremental_collector import IncrementalCollector
from etl.monitoring import create_monitoring_setup, ETLMonitor
from etl.config import ETLConfig

def main():
    """Função principal com argumentos de linha de comando"""
    parser = argparse.ArgumentParser(
        description='Executa processamento de chunks com monitoramento avançado',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Processamento padrão com monitoramento
  python run_monitored_chunk_processing.py

  # Processamento limitado com logs detalhados
  python run_monitored_chunk_processing.py --max-chunks 10 --batch-size 200 --verbose

  # Processamento com métricas específicas
  python run_monitored_chunk_processing.py --max-chunks 5 --track-performance

  # Modo dry run com monitoramento
  python run_monitored_chunk_processing.py --dry-run

  # Continuar processamento com checkpoint
  python run_monitored_chunk_processing.py --continue
        """
    )
    
    parser.add_argument(
        '--max-chunks',
        type=int,
        help='Máximo de chunks para processar (opcional)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Tamanho do lote de fixtures por chunk (padrão: 100)'
    )
    
    parser.add_argument(
        '--min-fixtures',
        type=int,
        default=10,
        help='Número mínimo de fixtures por chunk (padrão: 10)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Apenas mostra estatísticas, sem executar'
    )
    
    parser.add_argument(
        '--continue',
        action='store_true',
        dest='continue_processing',
        help='Continua processamento usando checkpoint'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Log detalhado'
    )
    
    parser.add_argument(
        '--clear-checkpoint',
        action='store_true',
        help='Limpa checkpoint e inicia do zero'
    )
    
    parser.add_argument(
        '--track-performance',
        action='store_true',
        help='Rastreamento detalhado de performance'
    )
    
    parser.add_argument(
        '--export-metrics',
        help='Exporta métricas para arquivo JSON'
    )
    
    args = parser.parse_args()
    
    # Valida configurações
    if not ETLConfig.validate():
        sys.exit(1)
    
    # Configura logging
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Limpa checkpoint se solicitado
    if args.clear_checkpoint:
        checkpoint_file = "chunk_checkpoint.json"
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
            print(f"✅ Checkpoint removido: {checkpoint_file}")
    
    # Configuração
    config = ETLConfig.get_connection_params()
    
    # Setup de monitoramento
    monitor, etl_logger, tracker, alert_manager = create_monitoring_setup(
        config['connection_string']
    )
    
    execution_id = monitor.execution_id
    
    # Log de início
    etl_logger.info("CHUNK_PROCESSOR", "Iniciando processamento de chunks com monitoramento")
    etl_logger.info("CHUNK_PROCESSOR", f"Execution ID: {execution_id}")
    etl_logger.info("CHUNK_PROCESSOR", f"Batch Size: {args.batch_size}")
    etl_logger.info("CHUNK_PROCESSOR", f"Min Fixtures: {args.min_fixtures}")
    
    if args.max_chunks:
        etl_logger.info("CHUNK_PROCESSOR", f"Max Chunks: {args.max_chunks}")
    if args.continue_processing:
        etl_logger.info("CHUNK_PROCESSOR", "Modo Continuar (com checkpoint)")
    if args.dry_run:
        etl_logger.info("CHUNK_PROCESSOR", "Modo Dry Run (apenas simulação)")
    if args.track_performance:
        etl_logger.info("CHUNK_PROCESSOR", "Rastreamento de performance ativado")
    
    print("🚀 Iniciando Processamento de Chunks com Monitoramento")
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🆔 Execution ID: {execution_id}")
    print(f"📦 Batch Size: {args.batch_size}")
    print(f"🔢 Min Fixtures: {args.min_fixtures}")
    if args.max_chunks:
        print(f"🎯 Max Chunks: {args.max_chunks}")
    if args.continue_processing:
        print("🔄 Modo Continuar (com checkpoint)")
    if args.dry_run:
        print("🔍 Modo Dry Run (apenas simulação)")
    if args.track_performance:
        print("📊 Rastreamento de performance ativado")
    print("-" * 50)
    
    try:
        # Cria gerenciadores
        chunk_manager = ChunkManager(config['connection_string'])
        collector = IncrementalCollector(
            api_key=config['api_key'],
            db_connection_string=config['connection_string']
        )
        processor = ChunkProcessor(chunk_manager, collector)
        
        # Conecta ao banco
        chunk_manager.connect()
        
        # Obtém estatísticas iniciais
        initial_stats = chunk_manager.get_chunk_statistics()
        etl_logger.info("CHUNK_PROCESSOR", f"Total de chunks: {initial_stats.total_chunks}")
        etl_logger.info("CHUNK_PROCESSOR", f"Chunks de alta prioridade: {initial_stats.high_priority_chunks}")
        etl_logger.info("CHUNK_PROCESSOR", f"Total de fixtures não processadas: {initial_stats.total_unprocessed_fixtures:,}")
        
        # Registra métricas iniciais
        tracker.record_metric("total_chunks", initial_stats.total_chunks)
        tracker.record_metric("total_unprocessed_fixtures", initial_stats.total_unprocessed_fixtures)
        tracker.record_metric("high_priority_chunks", initial_stats.high_priority_chunks)
        
        print("📊 Estatísticas Iniciais:")
        print(f"   Total de chunks: {initial_stats.total_chunks}")
        print(f"   Alta prioridade: {initial_stats.high_priority_chunks}")
        print(f"   Média prioridade: {initial_stats.medium_priority_chunks}")
        print(f"   Baixa prioridade: {initial_stats.low_priority_chunks}")
        print(f"   Total não processadas: {initial_stats.total_unprocessed_fixtures:,}")
        print(f"   Média por chunk: {initial_stats.avg_fixtures_per_chunk:.1f}")
        
        if args.dry_run:
            # Modo dry run - apenas mostra estatísticas
            chunks = chunk_manager.get_chunks(
                chunk_size=args.max_chunks or 100,
                min_fixtures=args.min_fixtures
            )
            
            etl_logger.info("CHUNK_PROCESSOR", f"Chunks que seriam processados: {len(chunks)}")
            
            print(f"\n🎯 Chunks que seriam processados: {len(chunks)}")
            if chunks:
                print("   Primeiros 5 chunks:")
                for i, chunk in enumerate(chunks[:5]):
                    print(f"   {i+1}. Liga {chunk.league_id}/Temporada {chunk.season_id} - {chunk.unprocessed_count} fixtures (prioridade: {chunk.priority_score})")
            
            # Mostra checkpoint se existir
            if args.continue_processing:
                processor.load_checkpoint()
                print(f"\n📋 Checkpoint: {len(processor.processed_chunks)} chunks já processados")
            
            # Finaliza execução
            monitor.finish_execution(
                execution_id=execution_id,
                status='COMPLETED',
                total_chunks=len(chunks),
                processed_chunks=0
            )
            
            etl_logger.info("CHUNK_PROCESSOR", "Dry run concluído com sucesso")
        
        else:
            # Executa processamento real
            start_time = time.time()
            
            # Carrega checkpoint
            processor.load_checkpoint()
            
            # Obtém chunks para processar
            chunks = chunk_manager.get_chunks(
                chunk_size=args.max_chunks or 1000,
                min_fixtures=args.min_fixtures
            )
            
            if not chunks:
                etl_logger.warning("CHUNK_PROCESSOR", "Nenhum chunk encontrado para processar")
                print("📝 Nenhum chunk encontrado para processar")
                
                # Finaliza execução
                monitor.finish_execution(
                    execution_id=execution_id,
                    status='COMPLETED',
                    total_chunks=0,
                    processed_chunks=0
                )
                return
            
            etl_logger.info("CHUNK_PROCESSOR", f"Processando {len(chunks)} chunks")
            print(f"\n🔄 Processando {len(chunks)} chunks")
            
            # Processa chunks
            total_processed = 0
            total_successful = 0
            total_failed = 0
            processed_chunks = 0
            
            for i, chunk in enumerate(chunks, 1):
                # Verifica se chunk já foi processado
                if processor.is_chunk_processed(chunk.league_id, chunk.season_id):
                    etl_logger.info("CHUNK_PROCESSOR", f"Chunk {chunk.league_id}/{chunk.season_id} já processado, pulando")
                    continue
                
                chunk_start_time = time.time()
                chunk_id = f"{chunk.league_id}_{chunk.season_id}"
                
                etl_logger.info("CHUNK_PROCESSOR", f"Processando chunk {i}/{len(chunks)}: {chunk_id}")
                etl_logger.info("CHUNK_PROCESSOR", f"Liga: {chunk.league_name or 'N/A'}, Temporada: {chunk.season_name or 'N/A'}")
                etl_logger.info("CHUNK_PROCESSOR", f"Fixtures não processadas: {chunk.unprocessed_count}, Prioridade: {chunk.priority_score}")
                
                print(f"\n📦 Chunk {i}/{len(chunks)}: {chunk_id}")
                print(f"   Liga: {chunk.league_name or 'N/A'}")
                print(f"   Temporada: {chunk.season_name or 'N/A'}")
                print(f"   Fixtures não processadas: {chunk.unprocessed_count}")
                print(f"   Prioridade: {chunk.priority_score}")
                
                try:
                    # Processa chunk com rastreamento de performance
                    if args.track_performance:
                        with tracker.track_operation(f"chunk_processing", {"chunk_id": chunk_id}):
                            chunk_stats = processor.process_chunk(chunk, args.batch_size)
                    else:
                        chunk_stats = processor.process_chunk(chunk, args.batch_size)
                    
                    chunk_duration = time.time() - chunk_start_time
                    
                    # Registra métricas do chunk
                    tracker.record_metric("chunk_duration", chunk_duration, "seconds", {"chunk_id": chunk_id})
                    tracker.record_metric("chunk_fixtures_processed", chunk_stats['processed'], "count", {"chunk_id": chunk_id})
                    tracker.record_metric("chunk_success_rate", 
                                        chunk_stats['successful'] / chunk_stats['processed'] if chunk_stats['processed'] > 0 else 0,
                                        "ratio", {"chunk_id": chunk_id})
                    
                    # Log de progresso do chunk
                    etl_logger.info("CHUNK_PROCESSOR", f"Chunk {chunk_id} concluído",
                                  chunk_id=chunk_id,
                                  processed=chunk_stats['processed'],
                                  successful=chunk_stats['successful'],
                                  failed=chunk_stats['failed'],
                                  duration_ms=int(chunk_duration * 1000))
                    
                    total_processed += chunk_stats['processed']
                    total_successful += chunk_stats['successful']
                    total_failed += chunk_stats['failed']
                    processed_chunks += 1
                    
                    # Log de progresso geral
                    if i % 10 == 0:
                        etl_logger.info("CHUNK_PROCESSOR", f"Progresso geral: {i}/{len(chunks)} chunks processados")
                        print(f"📊 Progresso: {i}/{len(chunks)} chunks processados")
                    
                    # Salva checkpoint a cada 10 chunks
                    if processed_chunks % 10 == 0:
                        processor.save_checkpoint()
                        etl_logger.info("CHUNK_PROCESSOR", f"Checkpoint salvo após {processed_chunks} chunks")
                
                except Exception as e:
                    etl_logger.error("CHUNK_PROCESSOR", f"Erro ao processar chunk {chunk_id}: {e}",
                                   chunk_id=chunk_id)
                    print(f"❌ Erro no chunk {chunk_id}: {e}")
                    total_failed += chunk.unprocessed_count  # Assume que todas falharam
            
            # Salva checkpoint final
            processor.save_checkpoint()
            
            # Calcula estatísticas finais
            total_duration = time.time() - start_time
            
            # Registra métricas finais
            tracker.record_metric("total_duration", total_duration, "seconds")
            tracker.record_metric("total_processed", total_processed, "count")
            tracker.record_metric("total_successful", total_successful, "count")
            tracker.record_metric("total_failed", total_failed, "count")
            tracker.record_metric("processed_chunks", processed_chunks, "count")
            tracker.record_metric("overall_success_rate", 
                                total_successful / total_processed if total_processed > 0 else 0,
                                "ratio")
            
            if total_duration > 0:
                tracker.record_metric("fixtures_per_second", total_processed / total_duration, "rate")
            
            # Log de resultados
            etl_logger.info("CHUNK_PROCESSOR", "Processamento de chunks concluído",
                          total_chunks=len(chunks),
                          processed_chunks=processed_chunks,
                          total_processed=total_processed,
                          total_successful=total_successful,
                          total_failed=total_failed,
                          duration_ms=int(total_duration * 1000))
            
            print("\n✅ Processamento de Chunks Concluído!")
            print(f"📊 Chunks processados: {processed_chunks}")
            print(f"📊 Total de fixtures: {total_processed}")
            print(f"✅ Sucessos: {total_successful}")
            print(f"❌ Falhas: {total_failed}")
            print(f"⏱️  Duração: {total_duration:.2f}s")
            if total_duration > 0:
                rate = total_processed / total_duration
                print(f"🚀 Taxa: {rate:.1f} fixtures/s")
            
            # Finaliza execução
            monitor.finish_execution(
                execution_id=execution_id,
                status='COMPLETED',
                total_fixtures=total_processed,
                processed_fixtures=total_processed,
                successful_fixtures=total_successful,
                failed_fixtures=total_failed,
                total_chunks=len(chunks),
                processed_chunks=processed_chunks
            )
            
            # Exporta métricas se solicitado
            if args.export_metrics:
                from etl.etl_dashboard import export_data
                export_data(monitor, args.export_metrics)
                print(f"📊 Métricas exportadas para: {args.export_metrics}")
        
        # Verifica alertas
        alerts = alert_manager.check_execution_alerts(execution_id)
        if alerts:
            print("\n🚨 Alertas encontrados:")
            for alert in alerts:
                print(f"   • {alert}")
                etl_logger.warning("ALERT_MANAGER", f"Alerta: {alert}")
        else:
            print("\n✅ Nenhum alerta encontrado")
            etl_logger.info("ALERT_MANAGER", "Nenhum alerta encontrado")
    
    except KeyboardInterrupt:
        print("\n⏹️  Processamento interrompido pelo usuário")
        etl_logger.warning("CHUNK_PROCESSOR", "Processamento interrompido pelo usuário")
        
        # Finaliza execução com status de cancelamento
        monitor.finish_execution(
            execution_id=execution_id,
            status='CANCELLED',
            error_message="Interrompido pelo usuário"
        )
        
        print("💾 Checkpoint salvo automaticamente")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        etl_logger.critical("CHUNK_PROCESSOR", f"Erro fatal: {e}")
        
        # Finaliza execução com status de falha
        monitor.finish_execution(
            execution_id=execution_id,
            status='FAILED',
            error_message=str(e)
        )
        
        sys.exit(1)
    finally:
        chunk_manager.disconnect()
        monitor.disconnect()

if __name__ == "__main__":
    main()
