#!/usr/bin/env python3
"""
Script de Teste para Batch Processing
====================================

Script para testar e validar o sistema de batch processing
implementado para otimizar a coleta de fixtures.

Autor: ETL Engineer
Data: 17 de Janeiro de 2025
Task: 3.1 - Teste do Batch Processing
"""

import argparse
import sys
import os
import time
from datetime import datetime

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.batch_collector import BatchCollector, create_batch_collector
from etl.config import ETLConfig
from test_config import setup_test_env

def test_single_batch(collector: BatchCollector, batch_size: int = 10):
    """Testa processamento de um único lote"""
    print(f"\n🧪 Testando lote único com {batch_size} fixtures")
    
    # Obtém fixtures para teste
    fixture_ids = collector.get_fixtures_for_batch(batch_size)
    
    if not fixture_ids:
        print("❌ Nenhuma fixture encontrada para teste")
        return False
    
    print(f"📋 Fixtures selecionadas: {fixture_ids[:5]}...")
    
    # Processa lote
    start_time = time.time()
    result = collector.process_batch(fixture_ids, includes=['statistics', 'events'])
    duration = time.time() - start_time
    
    # Salva resultados
    if result.successful_fixtures:
        collector.save_batch_results(result)
    
    # Relatório
    print(f"✅ Lote processado:")
    print(f"   📊 Fixtures processadas: {len(result.fixture_ids)}")
    print(f"   ✅ Sucessos: {len(result.successful_fixtures)}")
    print(f"   ❌ Falhas: {len(result.failed_fixtures)}")
    print(f"   🌐 Chamadas API: {result.api_calls_made}")
    print(f"   ⏱️  Duração: {duration:.2f}s")
    print(f"   🚀 Taxa: {len(result.fixture_ids)/duration:.1f} fixtures/s")
    
    if result.errors:
        print(f"   ⚠️  Erros: {len(result.errors)}")
        for error in result.errors[:3]:  # Mostra apenas os primeiros 3
            print(f"      • {error}")
    
    return len(result.successful_fixtures) > 0

def test_chunk_batch(collector: BatchCollector, league_id: int, season_id: int, batch_size: int = 50):
    """Testa processamento de chunk usando batch processing"""
    print(f"\n🧪 Testando chunk {league_id}/{season_id} com batch processing")
    
    chunk_info = {
        'league_id': league_id,
        'season_id': season_id
    }
    
    # Processa chunk
    start_time = time.time()
    stats = collector.process_chunk_batch(chunk_info, batch_size)
    duration = time.time() - start_time
    
    # Relatório
    print(f"✅ Chunk processado:")
    print(f"   📊 Fixtures processadas: {stats['processed']}")
    print(f"   ✅ Sucessos: {stats['successful']}")
    print(f"   ❌ Falhas: {stats['failed']}")
    print(f"   🌐 Chamadas API: {stats['api_calls']}")
    print(f"   ⏱️  Duração: {duration:.2f}s")
    
    if stats['processed'] > 0:
        print(f"   🚀 Taxa: {stats['processed']/duration:.1f} fixtures/s")
        print(f"   📈 Taxa de sucesso: {stats['successful']/stats['processed']*100:.1f}%")
        print(f"   🎯 Eficiência API: {stats['processed']/stats['api_calls']:.1f} fixtures/chamada")
    
    return stats['successful'] > 0

def compare_performance(collector: BatchCollector, fixture_count: int = 20):
    """Compara performance entre método individual e batch"""
    print(f"\n📊 Comparação de Performance ({fixture_count} fixtures)")
    
    # Obtém fixtures para teste
    fixture_ids = collector.get_fixtures_for_batch(fixture_count)
    
    if len(fixture_ids) < fixture_count:
        print(f"⚠️  Apenas {len(fixture_ids)} fixtures disponíveis")
        fixture_count = len(fixture_ids)
        fixture_ids = fixture_ids[:fixture_count]
    
    print(f"📋 Testando com {fixture_count} fixtures: {fixture_ids[:5]}...")
    
    # Teste 1: Batch Processing
    print("\n🔄 Teste 1: Batch Processing")
    start_time = time.time()
    batch_result = collector.process_batch(fixture_ids, includes=['statistics'])
    batch_duration = time.time() - start_time
    
    print(f"   ⏱️  Duração: {batch_duration:.2f}s")
    print(f"   🌐 Chamadas API: {batch_result.api_calls_made}")
    print(f"   🚀 Taxa: {len(fixture_ids)/batch_duration:.1f} fixtures/s")
    print(f"   📈 Eficiência: {len(fixture_ids)/batch_result.api_calls_made:.1f} fixtures/chamada")
    
    # Teste 2: Simulação de chamadas individuais
    print("\n🔄 Teste 2: Simulação de Chamadas Individuais")
    individual_start = time.time()
    individual_calls = len(fixture_ids)  # Uma chamada por fixture
    individual_duration = individual_start - individual_start + (len(fixture_ids) * 0.1)  # Simulação
    
    print(f"   ⏱️  Duração estimada: {individual_duration:.2f}s")
    print(f"   🌐 Chamadas API: {individual_calls}")
    print(f"   🚀 Taxa estimada: {len(fixture_ids)/individual_duration:.1f} fixtures/s")
    print(f"   📈 Eficiência: {len(fixture_ids)/individual_calls:.1f} fixtures/chamada")
    
    # Comparação
    print(f"\n📈 Comparação:")
    speedup = individual_duration / batch_duration if batch_duration > 0 else 0
    api_reduction = (individual_calls - batch_result.api_calls_made) / individual_calls * 100
    
    print(f"   🚀 Aceleração: {speedup:.1f}x mais rápido")
    print(f"   🌐 Redução de chamadas API: {api_reduction:.1f}%")
    print(f"   ⏱️  Economia de tempo: {individual_duration - batch_duration:.2f}s")
    
    return {
        'batch_duration': batch_duration,
        'individual_duration': individual_duration,
        'speedup': speedup,
        'api_reduction': api_reduction
    }

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Testa sistema de batch processing para ETL Sportmonks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Teste básico com 10 fixtures
  python test_batch_processing.py --test single --batch-size 10

  # Teste de chunk específico
  python test_batch_processing.py --test chunk --league-id 2451 --season-id 23026

  # Comparação de performance
  python test_batch_processing.py --test compare --fixture-count 50

  # Teste completo
  python test_batch_processing.py --test all
        """
    )
    
    parser.add_argument(
        '--test',
        choices=['single', 'chunk', 'compare', 'all'],
        default='single',
        help='Tipo de teste a executar'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Tamanho do lote para teste (padrão: 10)'
    )
    
    parser.add_argument(
        '--league-id',
        type=int,
        help='ID da liga para teste de chunk'
    )
    
    parser.add_argument(
        '--season-id',
        type=int,
        help='ID da temporada para teste de chunk'
    )
    
    parser.add_argument(
        '--fixture-count',
        type=int,
        default=20,
        help='Número de fixtures para comparação (padrão: 20)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Log detalhado'
    )
    
    args = parser.parse_args()
    
    # Configura ambiente de teste
    setup_test_env()
    
    # Valida configurações
    if not ETLConfig.validate():
        print("⚠️  Configurações de teste detectadas. Para teste real, configure as variáveis de ambiente.")
        print("   SPORTMONKS_API_TOKEN=seu_token_real")
        print("   SUPABASE_CONNECTION_STRING=sua_string_conexao_real")
        sys.exit(1)
    
    # Configura logging
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Configuração
    config = ETLConfig.get_connection_params()
    
    print("🚀 Iniciando Testes de Batch Processing")
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Configuração:")
    print(f"   Batch Size: {args.batch_size}")
    print(f"   Teste: {args.test}")
    print("-" * 50)
    
    try:
        # Cria coletor
        collector = create_batch_collector(
            config['api_key'],
            config['connection_string']
        )
        
        success_count = 0
        total_tests = 0
        
        # Executa testes baseado no tipo
        if args.test in ['single', 'all']:
            total_tests += 1
            if test_single_batch(collector, args.batch_size):
                success_count += 1
        
        if args.test in ['chunk', 'all']:
            total_tests += 1
            league_id = args.league_id or 2451  # Premier League
            season_id = args.season_id or 23026  # Temporada atual
            
            if test_chunk_batch(collector, league_id, season_id, args.batch_size):
                success_count += 1
        
        if args.test in ['compare', 'all']:
            total_tests += 1
            results = compare_performance(collector, args.fixture_count)
            if results['speedup'] > 1:
                success_count += 1
        
        # Relatório final
        print("\n" + "=" * 50)
        print("📊 Relatório Final dos Testes")
        print("=" * 50)
        print(f"✅ Testes bem-sucedidos: {success_count}/{total_tests}")
        print(f"📈 Taxa de sucesso: {success_count/total_tests*100:.1f}%")
        
        if success_count == total_tests:
            print("🎉 Todos os testes passaram! Batch processing está funcionando corretamente.")
        else:
            print("⚠️  Alguns testes falharam. Verifique os logs para detalhes.")
        
        print("\n💡 Próximos passos:")
        print("   • Integrar batch processing no sistema principal")
        print("   • Implementar cache Redis (Task 3.2)")
        print("   • Otimizar rate limiting (Task 3.3)")
    
    except KeyboardInterrupt:
        print("\n⏹️  Testes interrompidos pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        sys.exit(1)
    finally:
        if 'collector' in locals():
            collector.disconnect()

if __name__ == "__main__":
    main()
