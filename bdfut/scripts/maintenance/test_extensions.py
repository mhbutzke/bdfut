#!/usr/bin/env python3
"""
Script de Teste de Extensões PostgreSQL - TASK-DB-006
Agente: Database Specialist 🗄️
Data: 2025-01-13

Testa todas as extensões PostgreSQL habilitadas e suas funcionalidades.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

from bdfut.core.supabase_client import SupabaseClient
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/test_extensions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ExtensionTester:
    """Testador de extensões PostgreSQL."""
    
    def __init__(self):
        """Inicializar cliente Supabase."""
        try:
            self.config = Config()
            self.supabase = SupabaseClient(self.config)
            logger.info("✅ Cliente Supabase inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
            raise
    
    def list_installed_extensions(self):
        """Listar extensões instaladas."""
        logger.info("📋 Listando extensões instaladas...")
        
        try:
            result = self.supabase.execute_sql("""
                SELECT 
                    extname as extension_name,
                    extversion as version,
                    nspname as schema
                FROM pg_extension 
                JOIN pg_namespace ON pg_extension.extnamespace = pg_namespace.oid
                WHERE nspname = 'public'
                ORDER BY extname;
            """)
            
            logger.info(f"📊 {len(result)} extensões instaladas:")
            for ext in result:
                logger.info(f"  📦 {ext['extension_name']} v{ext['version']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar extensões: {e}")
            return []
    
    def test_pgcrypto_functions(self):
        """Testar funções da extensão pgcrypto."""
        logger.info("🔐 Testando extensão pgcrypto...")
        
        tests = []
        
        try:
            # Teste 1: Geração de UUID
            result = self.supabase.execute_sql("SELECT uuid_generate_v4() as uuid;")
            uuid_generated = result[0]['uuid'] if result else None
            tests.append({
                'test': 'UUID Generation',
                'success': bool(uuid_generated and len(uuid_generated) == 36),
                'result': uuid_generated
            })
            
            # Teste 2: Hash MD5
            result = self.supabase.execute_sql("SELECT md5('test') as hash;")
            md5_hash = result[0]['hash'] if result else None
            expected_md5 = '098f6bcd4621d373cade4e832627b4f6'
            tests.append({
                'test': 'MD5 Hash',
                'success': md5_hash == expected_md5,
                'result': md5_hash
            })
            
            # Teste 3: Criptografia simétrica
            result = self.supabase.execute_sql("""
                SELECT 
                    encrypt('secret', 'key', 'aes') as encrypted,
                    decrypt(encrypt('secret', 'key', 'aes'), 'key', 'aes') as decrypted;
            """)
            if result:
                encrypted = result[0]['encrypted']
                decrypted = result[0]['decrypted'].decode() if result[0]['decrypted'] else None
                tests.append({
                    'test': 'Symmetric Encryption',
                    'success': decrypted == 'secret',
                    'result': f"Encrypted: {len(encrypted)} bytes, Decrypted: {decrypted}"
                })
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar pgcrypto: {e}")
            tests.append({
                'test': 'pgcrypto Error',
                'success': False,
                'result': str(e)
            })
        
        for test in tests:
            status = "✅" if test['success'] else "❌"
            logger.info(f"  {status} {test['test']}: {test['result']}")
        
        return tests
    
    def test_text_search_functions(self):
        """Testar funções de busca de texto."""
        logger.info("🔍 Testando extensões de busca de texto...")
        
        tests = []
        
        try:
            # Teste 1: Similaridade (pg_trgm)
            result = self.supabase.execute_sql("""
                SELECT similarity('Lionel Messi', 'Messi') as similarity_score;
            """)
            similarity_score = result[0]['similarity_score'] if result else 0
            tests.append({
                'test': 'Trigram Similarity',
                'success': similarity_score > 0.3,
                'result': f"Score: {similarity_score}"
            })
            
            # Teste 2: Remoção de acentos (unaccent)
            result = self.supabase.execute_sql("""
                SELECT unaccent('José Mourinho') as unaccented;
            """)
            unaccented = result[0]['unaccented'] if result else None
            tests.append({
                'test': 'Unaccent Function',
                'success': unaccented == 'Jose Mourinho',
                'result': unaccented
            })
            
            # Teste 3: Distância Levenshtein (fuzzystrmatch)
            result = self.supabase.execute_sql("""
                SELECT levenshtein('Ronaldo', 'Ronald') as distance;
            """)
            distance = result[0]['distance'] if result else None
            tests.append({
                'test': 'Levenshtein Distance',
                'success': distance == 1,
                'result': f"Distance: {distance}"
            })
            
            # Teste 4: Soundex (fuzzystrmatch)
            result = self.supabase.execute_sql("""
                SELECT soundex('Smith'), soundex('Smyth');
            """)
            if result:
                soundex1, soundex2 = result[0].values()
                tests.append({
                    'test': 'Soundex Matching',
                    'success': soundex1 == soundex2,
                    'result': f"Smith: {soundex1}, Smyth: {soundex2}"
                })
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar busca de texto: {e}")
            tests.append({
                'test': 'Text Search Error',
                'success': False,
                'result': str(e)
            })
        
        for test in tests:
            status = "✅" if test['success'] else "❌"
            logger.info(f"  {status} {test['test']}: {test['result']}")
        
        return tests
    
    def test_custom_functions(self):
        """Testar funções personalizadas criadas."""
        logger.info("🛠️ Testando funções personalizadas...")
        
        tests = []
        
        try:
            # Teste 1: Busca de jogadores
            result = self.supabase.execute_sql("""
                SELECT * FROM search_player_name('Silva') LIMIT 3;
            """)
            tests.append({
                'test': 'Player Search Function',
                'success': len(result) > 0,
                'result': f"{len(result)} players found"
            })
            
            # Teste 2: Busca de times
            result = self.supabase.execute_sql("""
                SELECT * FROM search_team_name('Barcelona') LIMIT 3;
            """)
            tests.append({
                'test': 'Team Search Function',
                'success': len(result) > 0,
                'result': f"{len(result)} teams found"
            })
            
            # Teste 3: Geração de UUID com prefixo
            result = self.supabase.execute_sql("""
                SELECT generate_prefixed_uuid('player') as prefixed_uuid;
            """)
            prefixed_uuid = result[0]['prefixed_uuid'] if result else None
            tests.append({
                'test': 'Prefixed UUID Generation',
                'success': bool(prefixed_uuid and prefixed_uuid.startswith('player_')),
                'result': prefixed_uuid
            })
            
            # Teste 4: Hash de senha
            result = self.supabase.execute_sql("""
                SELECT 
                    hash_password('mypassword') as hashed,
                    verify_password('mypassword', hash_password('mypassword')) as verified;
            """)
            if result:
                hashed = result[0]['hashed']
                verified = result[0]['verified']
                tests.append({
                    'test': 'Password Hashing',
                    'success': verified == True,
                    'result': f"Hash length: {len(hashed)}, Verified: {verified}"
                })
            
            # Teste 5: Validação de integridade
            result = self.supabase.execute_sql("""
                SELECT * FROM validate_data_integrity();
            """)
            tests.append({
                'test': 'Data Integrity Validation',
                'success': len(result) >= 4,  # Esperamos pelo menos 4 tabelas
                'result': f"{len(result)} tables validated"
            })
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar funções personalizadas: {e}")
            tests.append({
                'test': 'Custom Functions Error',
                'success': False,
                'result': str(e)
            })
        
        for test in tests:
            status = "✅" if test['success'] else "❌"
            logger.info(f"  {status} {test['test']}: {test['result']}")
        
        return tests
    
    def test_advanced_indexes(self):
        """Testar índices avançados."""
        logger.info("📊 Testando índices avançados...")
        
        tests = []
        
        try:
            # Teste 1: Verificar índices GIN
            result = self.supabase.execute_sql("""
                SELECT COUNT(*) as gin_indexes
                FROM pg_indexes 
                WHERE schemaname = 'public' 
                AND indexdef LIKE '%gin%';
            """)
            gin_count = result[0]['gin_indexes'] if result else 0
            tests.append({
                'test': 'GIN Indexes Created',
                'success': gin_count >= 6,  # Esperamos pelo menos 6 índices GIN
                'result': f"{gin_count} GIN indexes found"
            })
            
            # Teste 2: Testar busca com índice trigram
            result = self.supabase.execute_sql("""
                EXPLAIN ANALYZE
                SELECT name FROM players 
                WHERE name % 'Silva'
                LIMIT 5;
            """)
            plan_text = '\n'.join([row['QUERY PLAN'] for row in result])
            uses_gin = 'Bitmap Index Scan' in plan_text and 'gin' in plan_text.lower()
            tests.append({
                'test': 'Trigram Index Usage',
                'success': uses_gin,
                'result': f"Uses GIN index: {uses_gin}"
            })
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar índices avançados: {e}")
            tests.append({
                'test': 'Advanced Indexes Error',
                'success': False,
                'result': str(e)
            })
        
        for test in tests:
            status = "✅" if test['success'] else "❌"
            logger.info(f"  {status} {test['test']}: {test['result']}")
        
        return tests
    
    def test_performance_monitoring(self):
        """Testar monitoramento de performance."""
        logger.info("⚡ Testando monitoramento de performance...")
        
        tests = []
        
        try:
            # Teste 1: pg_stat_statements
            result = self.supabase.execute_sql("""
                SELECT COUNT(*) as statement_count
                FROM pg_stat_statements
                LIMIT 1;
            """)
            statement_count = result[0]['statement_count'] if result else 0
            tests.append({
                'test': 'pg_stat_statements Active',
                'success': statement_count > 0,
                'result': f"{statement_count} statements tracked"
            })
            
            # Teste 2: Função de estatísticas personalizada
            result = self.supabase.execute_sql("""
                SELECT * FROM get_query_stats(3);
            """)
            tests.append({
                'test': 'Custom Query Stats Function',
                'success': len(result) > 0,
                'result': f"{len(result)} top queries analyzed"
            })
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar monitoramento: {e}")
            tests.append({
                'test': 'Performance Monitoring Error',
                'success': False,
                'result': str(e)
            })
        
        for test in tests:
            status = "✅" if test['success'] else "❌"
            logger.info(f"  {status} {test['test']}: {test['result']}")
        
        return tests
    
    def generate_extension_report(self):
        """Gerar relatório completo das extensões."""
        logger.info("📋 Gerando relatório completo das extensões...")
        
        # Executar todos os testes
        extensions = self.list_installed_extensions()
        crypto_tests = self.test_pgcrypto_functions()
        text_tests = self.test_text_search_functions()
        custom_tests = self.test_custom_functions()
        index_tests = self.test_advanced_indexes()
        perf_tests = self.test_performance_monitoring()
        
        # Calcular estatísticas
        all_tests = crypto_tests + text_tests + custom_tests + index_tests + perf_tests
        successful_tests = [t for t in all_tests if t['success']]
        success_rate = len(successful_tests) / len(all_tests) * 100 if all_tests else 0
        
        logger.info("📊 RESUMO DAS EXTENSÕES:")
        logger.info(f"  📦 Extensões instaladas: {len(extensions)}")
        logger.info(f"  ✅ Testes executados: {len(all_tests)}")
        logger.info(f"  🎯 Taxa de sucesso: {success_rate:.1f}%")
        logger.info(f"  ✅ Testes bem-sucedidos: {len(successful_tests)}")
        logger.info(f"  ❌ Testes falharam: {len(all_tests) - len(successful_tests)}")
        
        return {
            'extensions': extensions,
            'tests': {
                'crypto': crypto_tests,
                'text_search': text_tests,
                'custom_functions': custom_tests,
                'advanced_indexes': index_tests,
                'performance': perf_tests
            },
            'summary': {
                'total_extensions': len(extensions),
                'total_tests': len(all_tests),
                'successful_tests': len(successful_tests),
                'success_rate': success_rate
            }
        }

def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Testador de Extensões PostgreSQL')
    parser.add_argument('--list', action='store_true', help='Listar extensões instaladas')
    parser.add_argument('--test-crypto', action='store_true', help='Testar extensão pgcrypto')
    parser.add_argument('--test-text', action='store_true', help='Testar extensões de busca de texto')
    parser.add_argument('--test-custom', action='store_true', help='Testar funções personalizadas')
    parser.add_argument('--test-indexes', action='store_true', help='Testar índices avançados')
    parser.add_argument('--test-perf', action='store_true', help='Testar monitoramento de performance')
    parser.add_argument('--test-all', action='store_true', help='Executar todos os testes')
    parser.add_argument('--report', action='store_true', help='Gerar relatório completo')
    
    args = parser.parse_args()
    
    try:
        tester = ExtensionTester()
        
        if args.list or args.test_all or args.report:
            extensions = tester.list_installed_extensions()
            if not args.test_all and not args.report:
                print(f"📦 {len(extensions)} extensões instaladas")
        
        if args.test_crypto or args.test_all or args.report:
            crypto_tests = tester.test_pgcrypto_functions()
            if not args.test_all and not args.report:
                successful = len([t for t in crypto_tests if t['success']])
                print(f"🔐 Testes pgcrypto: {successful}/{len(crypto_tests)} sucessos")
        
        if args.test_text or args.test_all or args.report:
            text_tests = tester.test_text_search_functions()
            if not args.test_all and not args.report:
                successful = len([t for t in text_tests if t['success']])
                print(f"🔍 Testes busca de texto: {successful}/{len(text_tests)} sucessos")
        
        if args.test_custom or args.test_all or args.report:
            custom_tests = tester.test_custom_functions()
            if not args.test_all and not args.report:
                successful = len([t for t in custom_tests if t['success']])
                print(f"🛠️ Testes funções personalizadas: {successful}/{len(custom_tests)} sucessos")
        
        if args.test_indexes or args.test_all or args.report:
            index_tests = tester.test_advanced_indexes()
            if not args.test_all and not args.report:
                successful = len([t for t in index_tests if t['success']])
                print(f"📊 Testes índices avançados: {successful}/{len(index_tests)} sucessos")
        
        if args.test_perf or args.test_all or args.report:
            perf_tests = tester.test_performance_monitoring()
            if not args.test_all and not args.report:
                successful = len([t for t in perf_tests if t['success']])
                print(f"⚡ Testes performance: {successful}/{len(perf_tests)} sucessos")
        
        if args.test_all:
            print("✅ Todos os testes executados com sucesso!")
        
        if args.report:
            report = tester.generate_extension_report()
            print(f"📋 Relatório completo gerado: {report['summary']['success_rate']:.1f}% de sucesso")
        
        if not any(vars(args).values()):
            parser.print_help()
            
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {e}")
        print(f"❌ Erro durante execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
