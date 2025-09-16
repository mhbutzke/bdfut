#!/usr/bin/env python3
"""
Script para aplicar políticas Row Level Security (RLS)
====================================================

Responsável: Security Specialist 🔐
Task: SEC-002 - Implementar Row Level Security (RLS)
Data: 15 de Setembro de 2025

CRÍTICO: Este script aplica RLS em 17 tabelas para corrigir vulnerabilidades
"""

import sys
import os
import logging
from typing import List, Dict, Any

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

class RLSPolicyApplier:
    """Classe para aplicar políticas RLS"""
    
    def __init__(self):
        """Inicializar o aplicador de políticas"""
        try:
            self.client = SupabaseClient()
            logger.info("Cliente Supabase inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente: {e}")
            raise
    
    def get_rls_policies(self) -> List[Dict[str, str]]:
        """Definir políticas RLS para todas as tabelas"""
        
        # Lista das 17 tabelas identificadas na auditoria SEC-001
        tables = [
            'leagues', 'seasons', 'teams', 'fixtures', 'match_events',
            'match_statistics', 'match_lineups', 'venues', 'referees',
            'players', 'coaches', 'states', 'types', 'countries', 'stages'
        ]
        
        policies = []
        
        for table in tables:
            # Habilitar RLS na tabela
            policies.append({
                'name': f'enable_rls_{table}',
                'sql': f'ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;',
                'table': table,
                'type': 'enable_rls'
            })
            
            # Política de SELECT (leitura pública para dados esportivos)
            policies.append({
                'name': f'{table}_select_policy',
                'sql': f'''
                CREATE POLICY "{table}_select_policy" ON public.{table}
                    FOR SELECT USING (true);
                ''',
                'table': table,
                'type': 'select_policy'
            })
            
            # Políticas de escrita (apenas service_role)
            for operation in ['INSERT', 'UPDATE', 'DELETE']:
                policy_name = f'{table}_{operation.lower()}_policy'
                
                if operation == 'INSERT':
                    condition = 'WITH CHECK (auth.role() = \'service_role\')'
                else:
                    condition = 'USING (auth.role() = \'service_role\')'
                
                policies.append({
                    'name': policy_name,
                    'sql': f'''
                    CREATE POLICY "{policy_name}" ON public.{table}
                        FOR {operation} {condition};
                    ''',
                    'table': table,
                    'type': f'{operation.lower()}_policy'
                })
        
        # Política especial para API_CACHE (mais restritiva)
        if 'api_cache' not in tables:
            # API Cache deve ser completamente privado
            policies.extend([
                {
                    'name': 'enable_rls_api_cache',
                    'sql': 'ALTER TABLE public.api_cache ENABLE ROW LEVEL SECURITY;',
                    'table': 'api_cache',
                    'type': 'enable_rls'
                },
                {
                    'name': 'api_cache_select_policy',
                    'sql': '''
                    CREATE POLICY "api_cache_select_policy" ON public.api_cache
                        FOR SELECT USING (auth.role() = 'service_role');
                    ''',
                    'table': 'api_cache',
                    'type': 'select_policy'
                }
            ])
            
            for operation in ['INSERT', 'UPDATE', 'DELETE']:
                policy_name = f'api_cache_{operation.lower()}_policy'
                condition = 'WITH CHECK (auth.role() = \'service_role\')' if operation == 'INSERT' else 'USING (auth.role() = \'service_role\')'
                
                policies.append({
                    'name': policy_name,
                    'sql': f'''
                    CREATE POLICY "{policy_name}" ON public.api_cache
                        FOR {operation} {condition};
                    ''',
                    'table': 'api_cache',
                    'type': f'{operation.lower()}_policy'
                })
        
        return policies
    
    def apply_policy(self, policy: Dict[str, str]) -> bool:
        """Aplicar uma política específica"""
        try:
            logger.info(f"Aplicando {policy['type']} para {policy['table']}: {policy['name']}")
            
            # Executar SQL usando RPC (se disponível) ou client direto
            try:
                result = self.client.client.rpc('exec_sql', {'sql': policy['sql']}).execute()
                logger.info(f"✅ Política {policy['name']} aplicada com sucesso")
                return True
                
            except Exception as e:
                # Tentar método alternativo se RPC não funcionar
                logger.warning(f"RPC falhou, tentando método alternativo: {e}")
                
                # Para RLS, podemos tentar usar o método direto do Supabase
                if policy['type'] == 'enable_rls':
                    # Método direto não disponível, registrar como pendente
                    logger.warning(f"⚠️ RLS deve ser habilitado manualmente para {policy['table']}")
                    return False
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao aplicar política {policy['name']}: {e}")
            return False
    
    def check_rls_status(self) -> Dict[str, Any]:
        """Verificar status atual do RLS"""
        try:
            # Verificar quais tabelas têm RLS habilitado
            query = """
            SELECT 
                schemaname,
                tablename,
                rowsecurity as rls_enabled
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
            """
            
            # Tentar executar query
            try:
                result = self.client.client.rpc('exec_sql', {'sql': query}).execute()
                return {'success': True, 'data': result.data}
            except:
                logger.warning("Não foi possível verificar status RLS via RPC")
                return {'success': False, 'data': []}
                
        except Exception as e:
            logger.error(f"Erro ao verificar status RLS: {e}")
            return {'success': False, 'data': []}
    
    def generate_migration_script(self) -> str:
        """Gerar script de migração completo"""
        policies = self.get_rls_policies()
        
        script = """-- ================================================================
-- SCRIPT DE APLICAÇÃO RLS - GERADO AUTOMATICAMENTE
-- ================================================================
-- Responsável: Security Specialist 🔐
-- Task: SEC-002 - Implementar Row Level Security (RLS)
-- Gerado em: """ + str(logging.LogRecord('', 0, '', 0, '', (), None).__dict__.get('created', 'N/A')) + """

BEGIN;

"""
        
        current_table = None
        for policy in policies:
            if policy['table'] != current_table:
                script += f"\n-- ================================================================\n"
                script += f"-- TABELA: {policy['table'].upper()}\n"
                script += f"-- ================================================================\n"
                current_table = policy['table']
            
            script += f"-- {policy['type']}: {policy['name']}\n"
            script += policy['sql'].strip() + "\n\n"
        
        script += """
-- Verificar aplicação
SELECT 
    tablename,
    rowsecurity as rls_enabled,
    (SELECT COUNT(*) FROM pg_policies p WHERE p.tablename = t.tablename AND p.schemaname = 'public') as policies_count
FROM pg_tables t
WHERE schemaname = 'public'
ORDER BY tablename;

COMMIT;

-- ================================================================
-- FIM DO SCRIPT
-- ================================================================
"""
        
        return script
    
    def apply_all_policies(self) -> Dict[str, Any]:
        """Aplicar todas as políticas RLS"""
        logger.info("🔐 Iniciando aplicação de políticas RLS...")
        
        policies = self.get_rls_policies()
        
        results = {
            'total_policies': len(policies),
            'applied_successfully': 0,
            'failed': 0,
            'failed_policies': [],
            'tables_affected': set()
        }
        
        for policy in policies:
            results['tables_affected'].add(policy['table'])
            
            if self.apply_policy(policy):
                results['applied_successfully'] += 1
            else:
                results['failed'] += 1
                results['failed_policies'].append(policy['name'])
        
        results['tables_affected'] = len(results['tables_affected'])
        
        # Verificar status final
        status = self.check_rls_status()
        results['final_status'] = status
        
        return results

def main():
    """Função principal"""
    try:
        logger.info("🔐 Iniciando aplicação de políticas RLS...")
        
        # Criar aplicador
        applier = RLSPolicyApplier()
        
        # Verificar status atual
        logger.info("Verificando status atual do RLS...")
        current_status = applier.check_rls_status()
        
        if current_status['success']:
            logger.info("✅ Status atual obtido com sucesso")
        else:
            logger.warning("⚠️ Não foi possível obter status atual")
        
        # Gerar script de migração
        logger.info("Gerando script de migração...")
        migration_script = applier.generate_migration_script()
        
        # Salvar script
        script_file = "supabase/migrations/generated_rls_policies.sql"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(migration_script)
        
        logger.info(f"✅ Script de migração salvo em: {script_file}")
        
        # Tentar aplicar políticas
        logger.info("Tentando aplicar políticas RLS...")
        results = applier.apply_all_policies()
        
        # Exibir resultados
        print("\n" + "="*60)
        print("🔐 RESULTADOS DA APLICAÇÃO RLS")
        print("="*60)
        print(f"Total de políticas: {results['total_policies']}")
        print(f"Aplicadas com sucesso: {results['applied_successfully']}")
        print(f"Falharam: {results['failed']}")
        print(f"Tabelas afetadas: {results['tables_affected']}")
        
        if results['failed'] > 0:
            print(f"\n⚠️ Políticas que falharam:")
            for policy in results['failed_policies']:
                print(f"  - {policy}")
            
            print(f"\n📋 Para aplicar manualmente:")
            print(f"  psql -f {script_file}")
        
        print("="*60)
        
        # Salvar relatório
        report_file = f"logs/RLS_APPLICATION_REPORT_{str(logging.LogRecord('', 0, '', 0, '', (), None).__dict__.get('created', 'N/A')).replace('.', '')[:15]}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"""# RELATÓRIO DE APLICAÇÃO RLS

## Resultados
- **Total de políticas:** {results['total_policies']}
- **Aplicadas com sucesso:** {results['applied_successfully']}
- **Falharam:** {results['failed']}
- **Tabelas afetadas:** {results['tables_affected']}

## Script gerado
{script_file}

## Status
{'✅ Aplicação completa' if results['failed'] == 0 else '⚠️ Aplicação parcial - requer intervenção manual'}
""")
        
        logger.info(f"📄 Relatório salvo em: {report_file}")
        
        return 0 if results['failed'] == 0 else 1
        
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
