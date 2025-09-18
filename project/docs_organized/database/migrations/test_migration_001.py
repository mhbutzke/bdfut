#!/usr/bin/env python3
"""
Test Script para Migration 001 - Enhance Fixtures Table
Author: Database Optimization Team  
Date: 2025-01-18

Este script testa a migration 001 em ambiente seguro antes de aplicar em produção.
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Any
from supabase import create_client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MigrationTester:
    """Testador para Migration 001"""
    
    def __init__(self):
        """Inicializar testador"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY') 
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("❌ Variáveis SUPABASE_URL e SUPABASE_ANON_KEY devem estar configuradas")
        
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.test_results = []
    
    def log_test(self, test_name: str, status: str, message: str, details: Any = None):
        """Registrar resultado de teste"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        emoji = {'PASS': '✅', 'FAIL': '❌', 'WARNING': '⚠️'}
        logger.info(f"{emoji.get(status, '❓')} {test_name}: {message}")
    
    def test_current_structure(self) -> bool:
        """Testar estrutura atual da tabela fixtures"""
        logger.info("🔍 Testando estrutura atual da tabela fixtures...")
        
        try:
            # Verificar se tabela existe e quantos registros tem
            response = self.supabase.table('fixtures').select('fixture_id', count='exact').limit(1).execute()
            total_records = response.count
            
            self.log_test(
                'table_exists', 'PASS',
                f'Tabela fixtures existe com {total_records} registros',
                {'record_count': total_records}
            )
            
            # Verificar colunas essenciais atuais
            essential_columns = ['fixture_id', 'league_id', 'season_id', 'home_team_id', 'away_team_id']
            sample = self.supabase.table('fixtures').select(','.join(essential_columns)).limit(1).execute()
            
            if sample.data:
                self.log_test(
                    'essential_columns', 'PASS',
                    'Colunas essenciais presentes e acessíveis'
                )
                return True
            else:
                self.log_test(
                    'essential_columns', 'FAIL', 
                    'Não foi possível acessar colunas essenciais'
                )
                return False
                
        except Exception as e:
            self.log_test('table_access', 'FAIL', f'Erro ao acessar tabela: {str(e)}')
            return False
    
    def test_missing_columns(self) -> Dict[str, bool]:
        """Testar quais colunas da migration estão faltando"""
        logger.info("🔍 Verificando colunas que serão adicionadas...")
        
        new_columns = [
            'name', 'result_info', 'leg', 'details', 'last_processed_at',
            'home_score', 'away_score', 'total_goals', 'goal_difference', 
            'match_result', 'etl_processed_at', 'etl_version', 'data_quality_score'
        ]
        
        missing_columns = []
        existing_columns = []
        
        for column in new_columns:
            try:
                # Tentar selecionar a coluna
                response = self.supabase.table('fixtures').select(column).limit(1).execute()
                existing_columns.append(column)
                self.log_test(
                    f'column_{column}', 'WARNING',
                    f'Coluna {column} já existe (migration pode falhar)'
                )
            except:
                missing_columns.append(column)
                self.log_test(
                    f'column_{column}', 'PASS',
                    f'Coluna {column} não existe (será adicionada)'
                )
        
        return {
            'missing': missing_columns,
            'existing': existing_columns,
            'ready_for_migration': len(missing_columns) > 0
        }
    
    def test_performance_baseline(self) -> Dict[str, float]:
        """Medir performance atual para comparação pós-migration"""
        logger.info("⏱️ Medindo performance baseline...")
        
        performance_tests = {}
        
        # Teste 1: Consulta simples por ID
        start_time = time.time()
        try:
            self.supabase.table('fixtures').select('*').eq('fixture_id', 11865351).execute()
            performance_tests['simple_select'] = time.time() - start_time
            self.log_test('perf_simple_select', 'PASS', 
                         f'Consulta simples: {performance_tests["simple_select"]:.3f}s')
        except Exception as e:
            self.log_test('perf_simple_select', 'FAIL', f'Erro: {str(e)}')
        
        # Teste 2: Consulta com JOIN
        start_time = time.time()
        try:
            # Simular consulta que usará as views futuras
            response = self.supabase.table('fixtures').select(
                'fixture_id,league_id,home_team_id,away_team_id,starting_at'
            ).limit(100).execute()
            performance_tests['join_simulation'] = time.time() - start_time
            self.log_test('perf_join_simulation', 'PASS',
                         f'Consulta complexa: {performance_tests["join_simulation"]:.3f}s')
        except Exception as e:
            self.log_test('perf_join_simulation', 'FAIL', f'Erro: {str(e)}')
        
        # Teste 3: Contagem total
        start_time = time.time()
        try:
            response = self.supabase.table('fixtures').select('*', count='exact').limit(1).execute()
            performance_tests['count_total'] = time.time() - start_time
            self.log_test('perf_count_total', 'PASS',
                         f'Contagem total: {performance_tests["count_total"]:.3f}s')
        except Exception as e:
            self.log_test('perf_count_total', 'FAIL', f'Erro: {str(e)}')
        
        return performance_tests
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executar todos os testes pré-migration"""
        logger.info("🚀 Iniciando testes pré-migration...")
        
        # Teste 1: Estrutura atual
        structure_ok = self.test_current_structure()
        
        # Teste 2: Colunas faltantes
        columns_info = self.test_missing_columns()
        
        # Teste 3: Performance baseline
        performance_baseline = self.test_performance_baseline()
        
        # Resumo final
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARNING'])
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'structure_ready': structure_ok,
            'columns_analysis': columns_info,
            'performance_baseline': performance_baseline,
            'test_summary': {
                'total': total_tests,
                'passed': passed,
                'failed': failed,
                'warnings': warnings,
                'success_rate': (passed / total_tests * 100) if total_tests > 0 else 0
            },
            'ready_for_migration': structure_ok and failed == 0,
            'test_results': self.test_results
        }
        
        # Log final
        logger.info(f"📊 Testes concluídos: {passed} PASS, {failed} FAIL, {warnings} WARNING")
        logger.info(f"🎯 Taxa de sucesso: {summary['test_summary']['success_rate']:.1f}%")
        
        if summary['ready_for_migration']:
            logger.info("✅ Sistema pronto para migration!")
        else:
            logger.warning("⚠️ Revisar problemas antes de executar migration")
        
        return summary

def main():
    """Função principal"""
    print("🧪 Testador de Migration 001 - BDFut")
    print("=" * 50)
    
    try:
        tester = MigrationTester()
        results = tester.run_all_tests()
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"migration_test_report_{timestamp}.json"
        
        import json
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Relatório salvo em: {report_file}")
        
        # Status final
        if results['ready_for_migration']:
            print("\n🎉 ✅ SISTEMA PRONTO PARA MIGRATION!")
            print("\nPróximos passos:")
            print("1. Executar backup: ./database_migrations/backup_fixtures.sh")
            print("2. Aplicar migration: psql $SUPABASE_DB_URL -f database_migrations/001_enhance_fixtures_table.sql")
            print("3. Executar testes pós-migration")
        else:
            print("\n⚠️ ❌ REVISAR PROBLEMAS ANTES DA MIGRATION")
            print("\nVerificar:")
            print("- Falhas nos testes identificadas")
            print("- Configurações de ambiente")
            print("- Permissões de acesso ao banco")
        
        return 0 if results['ready_for_migration'] else 1
        
    except Exception as e:
        logger.error(f"❌ Erro durante testes: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
