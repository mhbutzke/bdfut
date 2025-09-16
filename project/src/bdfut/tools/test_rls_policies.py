#!/usr/bin/env python3
"""
Script para testar políticas Row Level Security (RLS)
=====================================================

Responsável: Security Specialist 🔐
Task: SEC-002 - Implementar Row Level Security (RLS)
Data: 15 de Setembro de 2025

Objetivo: Validar que todas as políticas RLS estão funcionando corretamente
"""

import sys
import os
from typing import Dict, List, Any
import logging

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from bdfut.core.supabase_client import SupabaseClient
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RLSPolicyTester:
    """Classe para testar políticas RLS"""
    
    def __init__(self):
        """Inicializar o testador de políticas"""
        try:
            self.client = SupabaseClient()
            logger.info("Cliente Supabase inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Supabase: {e}")
            raise
    
    def get_tables_with_rls(self) -> List[Dict[str, Any]]:
        """Obter lista de tabelas com RLS habilitado"""
        try:
            query = """
            SELECT 
                schemaname,
                tablename,
                rowsecurity as rls_enabled,
                (SELECT COUNT(*) FROM pg_policies p 
                 WHERE p.schemaname = t.schemaname 
                 AND p.tablename = t.tablename) as policies_count
            FROM pg_tables t
            WHERE schemaname = 'public'
            ORDER BY tablename;
            """
            
            result = self.client.client.rpc('sql', {'query': query}).execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Erro ao obter tabelas com RLS: {e}")
            return []
    
    def test_table_access(self, table_name: str) -> Dict[str, Any]:
        """Testar acesso a uma tabela específica"""
        test_result = {
            'table': table_name,
            'select_test': False,
            'select_error': None,
            'row_count': 0
        }
        
        try:
            # Testar SELECT
            result = self.client.client.table(table_name).select('*').limit(1).execute()
            test_result['select_test'] = True
            test_result['row_count'] = len(result.data) if result.data else 0
            logger.info(f"✅ SELECT em {table_name}: OK ({test_result['row_count']} registros)")
            
        except Exception as e:
            test_result['select_error'] = str(e)
            logger.error(f"❌ SELECT em {table_name}: {e}")
        
        return test_result
    
    def test_all_tables(self) -> Dict[str, Any]:
        """Testar acesso a todas as tabelas públicas"""
        # Lista das 17 tabelas identificadas na auditoria
        tables_to_test = [
            'leagues', 'seasons', 'teams', 'fixtures', 'api_cache',
            'match_events', 'match_statistics', 'match_lineups',
            'venues', 'referees', 'players', 'coaches', 'states',
            'types', 'countries', 'stages'
        ]
        
        results = {
            'total_tables': len(tables_to_test),
            'successful_tests': 0,
            'failed_tests': 0,
            'table_results': []
        }
        
        logger.info(f"Iniciando testes RLS em {len(tables_to_test)} tabelas...")
        
        for table in tables_to_test:
            logger.info(f"Testando tabela: {table}")
            test_result = self.test_table_access(table)
            results['table_results'].append(test_result)
            
            if test_result['select_test']:
                results['successful_tests'] += 1
            else:
                results['failed_tests'] += 1
        
        return results
    
    def generate_rls_report(self) -> str:
        """Gerar relatório completo de RLS"""
        logger.info("Gerando relatório de RLS...")
        
        # Obter informações das tabelas
        tables_info = self.get_tables_with_rls()
        
        # Testar acesso
        test_results = self.test_all_tables()
        
        # Gerar relatório
        report = f"""
# RELATÓRIO DE TESTES RLS - BDFUT
**Data:** {logger.handlers[0].formatter.formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}
**Responsável:** Security Specialist 🔐
**Task:** SEC-002 - Implementar Row Level Security

## 📊 RESUMO DOS TESTES

- **Total de tabelas testadas:** {test_results['total_tables']}
- **Testes bem-sucedidos:** {test_results['successful_tests']}
- **Testes falharam:** {test_results['failed_tests']}
- **Taxa de sucesso:** {(test_results['successful_tests'] / test_results['total_tables'] * 100):.1f}%

## 📋 DETALHES POR TABELA

"""
        
        for result in test_results['table_results']:
            status_icon = "✅" if result['select_test'] else "❌"
            report += f"### {status_icon} {result['table'].upper()}\n"
            report += f"- **Acesso SELECT:** {'OK' if result['select_test'] else 'FALHOU'}\n"
            
            if result['select_test']:
                report += f"- **Registros acessíveis:** {result['row_count']}\n"
            else:
                report += f"- **Erro:** {result['select_error']}\n"
            
            report += "\n"
        
        # Informações sobre RLS
        report += "## 🔒 STATUS RLS DAS TABELAS\n\n"
        
        for table_info in tables_info:
            rls_status = "✅ HABILITADO" if table_info.get('rls_enabled') else "❌ DESABILITADO"
            policies_count = table_info.get('policies_count', 0)
            
            report += f"- **{table_info['tablename']}:** {rls_status} ({policies_count} políticas)\n"
        
        report += f"""
## 🎯 PRÓXIMAS AÇÕES

{'✅ RLS implementado com sucesso!' if test_results['failed_tests'] == 0 else '⚠️ Correções necessárias encontradas'}

### Para aplicar as políticas RLS:
```sql
-- Executar migração
psql -h <host> -U <user> -d <database> -f supabase/migrations/20250915_enable_rls_all_tables.sql
```

### Para verificar status:
```sql
SELECT * FROM public.check_rls_status();
```

---
**Gerado por:** test_rls_policies.py  
**Security Specialist:** 🔐
"""
        
        return report

def main():
    """Função principal"""
    try:
        logger.info("🔐 Iniciando testes de políticas RLS...")
        
        # Criar testador
        tester = RLSPolicyTester()
        
        # Gerar relatório
        report = tester.generate_rls_report()
        
        # Salvar relatório
        report_file = f"logs/RLS_TEST_REPORT_{logger.handlers[0].formatter.formatTime(logging.LogRecord('', 0, '', 0, '', (), None)).replace(':', '').replace(' ', '_').replace('-', '')[:15]}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✅ Relatório salvo em: {report_file}")
        
        # Exibir resumo no terminal
        test_results = tester.test_all_tables()
        print("\n" + "="*50)
        print("🔐 RESUMO DOS TESTES RLS")
        print("="*50)
        print(f"Total de tabelas: {test_results['total_tables']}")
        print(f"Testes OK: {test_results['successful_tests']}")
        print(f"Testes FALHOU: {test_results['failed_tests']}")
        print(f"Taxa de sucesso: {(test_results['successful_tests'] / test_results['total_tables'] * 100):.1f}%")
        print("="*50)
        
        if test_results['failed_tests'] == 0:
            print("✅ TODOS OS TESTES PASSARAM!")
            return 0
        else:
            print("⚠️ ALGUNS TESTES FALHARAM - Verifique o relatório")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
