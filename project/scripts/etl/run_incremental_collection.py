#!/usr/bin/env python3
"""
Script de Execução da Coleta Incremental
========================================

Script principal para executar coleta incremental com diferentes configurações.

Autor: ETL Engineer
Data: 17 de Janeiro de 2025
Task: 2.2 - Script de Execução da Coleta Incremental
"""

import argparse
import sys
import os
from datetime import datetime

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.incremental_collector import IncrementalCollector
from etl.config import ETLConfig

def main():
    """Função principal com argumentos de linha de comando"""
    parser = argparse.ArgumentParser(
        description='Executa coleta incremental de fixtures do Sportmonks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Coleta padrão (100 fixtures)
  python run_incremental_collection.py

  # Coleta específica de uma liga
  python run_incremental_collection.py --league-id 82 --batch-size 50

  # Coleta de teste (apenas 10 fixtures)
  python run_incremental_collection.py --max-fixtures 10 --batch-size 10

  # Coleta de uma temporada específica
  python run_incremental_collection.py --season-id 23744 --batch-size 200
        """
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=ETLConfig.DEFAULT_BATCH_SIZE,
        help=f'Tamanho do lote de fixtures (padrão: {ETLConfig.DEFAULT_BATCH_SIZE})'
    )
    
    parser.add_argument(
        '--league-id',
        type=int,
        help='ID da liga para filtrar (opcional)'
    )
    
    parser.add_argument(
        '--season-id',
        type=int,
        help='ID da temporada para filtrar (opcional)'
    )
    
    parser.add_argument(
        '--max-fixtures',
        type=int,
        help='Máximo de fixtures para processar (opcional)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Apenas mostra o que seria processado, sem executar'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Log detalhado'
    )
    
    args = parser.parse_args()
    
    # Valida configurações
    if not ETLConfig.validate():
        sys.exit(1)
    
    # Configura logging
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Cria coletor
    config = ETLConfig.get_connection_params()
    collector = IncrementalCollector(
        api_key=config['api_key'],
        db_connection_string=config['connection_string']
    )
    
    # Log de início
    print("🚀 Iniciando Coleta Incremental")
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📦 Batch Size: {args.batch_size}")
    if args.league_id:
        print(f"🏆 Liga ID: {args.league_id}")
    if args.season_id:
        print(f"📅 Temporada ID: {args.season_id}")
    if args.max_fixtures:
        print(f"🔢 Máximo de Fixtures: {args.max_fixtures}")
    if args.dry_run:
        print("🔍 Modo Dry Run (apenas simulação)")
    print("-" * 50)
    
    try:
        if args.dry_run:
            # Modo dry run - apenas mostra estatísticas
            collector.db_manager.connect()
            stats = collector.db_manager.get_collection_stats()
            collector.db_manager.disconnect()
            
            print("📊 Estatísticas Atuais:")
            print(f"   Total de fixtures: {stats.get('total_fixtures', 0):,}")
            print(f"   Não processadas: {stats.get('unprocessed_fixtures', 0):,}")
            print(f"   Dados incompletos: {stats.get('incomplete_data_fixtures', 0):,}")
            print(f"   Baixa qualidade: {stats.get('low_quality_fixtures', 0):,}")
            print(f"   Versão antiga: {stats.get('old_version_fixtures', 0):,}")
            
            # Simula quantas fixtures seriam processadas
            fixtures = collector.db_manager.get_fixtures_for_collection(
                batch_size=args.batch_size,
                league_id=args.league_id,
                season_id=args.season_id
            )
            
            print(f"\n🎯 Fixtures que seriam processadas: {len(fixtures)}")
            if fixtures:
                print("   Primeiras 5 fixtures:")
                for i, fixture in enumerate(fixtures[:5]):
                    print(f"   {i+1}. ID {fixture.fixture_id} - {fixture.collection_reason} (prioridade: {fixture.priority_score})")
            
        else:
            # Executa coleta real
            stats = collector.run_collection(
                batch_size=args.batch_size,
                league_id=args.league_id,
                season_id=args.season_id,
                max_fixtures=args.max_fixtures
            )
            
            # Log de resultados
            print("\n✅ Coleta Concluída!")
            print(f"📊 Total processadas: {stats.total_processed}")
            print(f"✅ Sucessos: {stats.successful}")
            print(f"❌ Falhas: {stats.failed}")
            if stats.end_time and stats.start_time:
                duration = stats.end_time - stats.start_time
                print(f"⏱️  Duração: {duration}")
                if duration.total_seconds() > 0:
                    rate = stats.total_processed / duration.total_seconds() * 60
                    print(f"🚀 Taxa: {rate:.1f} fixtures/min")
    
    except KeyboardInterrupt:
        print("\n⏹️  Coleta interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
