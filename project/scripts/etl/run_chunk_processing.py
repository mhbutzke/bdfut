#!/usr/bin/env python3
"""
Script de Execução do Processamento de Chunks
=============================================

Script principal para executar processamento de chunks por liga/temporada.

Autor: ETL Engineer
Data: 17 de Janeiro de 2025
Task: 2.3 - Script de Execução do Processamento de Chunks
"""

import argparse
import sys
import os
from datetime import datetime

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.chunk_manager import ChunkManager, ChunkProcessor
from etl.incremental_collector import IncrementalCollector
from etl.config import ETLConfig

def main():
    """Função principal com argumentos de linha de comando"""
    parser = argparse.ArgumentParser(
        description='Executa processamento de chunks por liga/temporada',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Processamento padrão (todos os chunks)
  python run_chunk_processing.py

  # Processamento limitado (apenas 10 chunks)
  python run_chunk_processing.py --max-chunks 10

  # Processamento com batch size maior
  python run_chunk_processing.py --batch-size 200 --max-chunks 20

  # Processamento apenas chunks com muitas fixtures
  python run_chunk_processing.py --min-fixtures 100

  # Modo dry run (apenas estatísticas)
  python run_chunk_processing.py --dry-run

  # Continuar processamento (com checkpoint)
  python run_chunk_processing.py --continue
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
    
    # Cria gerenciadores
    chunk_manager = ChunkManager(config['connection_string'])
    collector = IncrementalCollector(
        api_key=config['api_key'],
        db_connection_string=config['connection_string']
    )
    processor = ChunkProcessor(chunk_manager, collector)
    
    # Log de início
    print("🚀 Iniciando Processamento de Chunks")
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📦 Batch Size: {args.batch_size}")
    print(f"🔢 Min Fixtures: {args.min_fixtures}")
    if args.max_chunks:
        print(f"🎯 Max Chunks: {args.max_chunks}")
    if args.continue_processing:
        print("🔄 Modo Continuar (com checkpoint)")
    if args.dry_run:
        print("🔍 Modo Dry Run (apenas simulação)")
    print("-" * 50)
    
    try:
        if args.dry_run:
            # Modo dry run - apenas mostra estatísticas
            chunk_manager.connect()
            stats = chunk_manager.get_chunk_statistics()
            chunks = chunk_manager.get_chunks(
                chunk_size=args.max_chunks or 100,
                min_fixtures=args.min_fixtures
            )
            chunk_manager.disconnect()
            
            print("📊 Estatísticas dos Chunks:")
            print(f"   Total de chunks: {stats.total_chunks}")
            print(f"   Alta prioridade: {stats.high_priority_chunks}")
            print(f"   Média prioridade: {stats.medium_priority_chunks}")
            print(f"   Baixa prioridade: {stats.low_priority_chunks}")
            print(f"   Total não processadas: {stats.total_unprocessed_fixtures:,}")
            print(f"   Média por chunk: {stats.avg_fixtures_per_chunk:.1f}")
            
            print(f"\n🎯 Chunks que seriam processados: {len(chunks)}")
            if chunks:
                print("   Primeiros 5 chunks:")
                for i, chunk in enumerate(chunks[:5]):
                    print(f"   {i+1}. Liga {chunk.league_id}/Temporada {chunk.season_id} - {chunk.unprocessed_count} fixtures (prioridade: {chunk.priority_score})")
            
            # Mostra checkpoint se existir
            if args.continue_processing:
                processor.load_checkpoint()
                print(f"\n📋 Checkpoint: {len(processor.processed_chunks)} chunks já processados")
        
        else:
            # Executa processamento real
            stats = processor.process_all_chunks(
                max_chunks=args.max_chunks,
                batch_size=args.batch_size,
                min_fixtures=args.min_fixtures
            )
            
            # Log de resultados
            print("\n✅ Processamento de Chunks Concluído!")
            print(f"📊 Chunks processados: {stats['total_chunks']}")
            print(f"📊 Total de fixtures: {stats['total_processed']}")
            print(f"✅ Sucessos: {stats['total_successful']}")
            print(f"❌ Falhas: {stats['total_failed']}")
            print(f"⏱️  Duração: {stats['total_duration']:.2f}s")
            if stats['total_duration'] > 0:
                rate = stats['total_processed'] / stats['total_duration']
                print(f"🚀 Taxa: {rate:.1f} fixtures/s")
    
    except KeyboardInterrupt:
        print("\n⏹️  Processamento interrompido pelo usuário")
        print("💾 Checkpoint salvo automaticamente")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
