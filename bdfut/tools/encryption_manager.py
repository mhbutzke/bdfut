#!/usr/bin/env python3
"""
Gerenciador do Sistema de Criptografia BDFut
===========================================

Responsável: Security Specialist 🔐
Task: SEC-004 - Implementar Criptografia de Dados
Data: 15 de Setembro de 2025

Funcionalidades:
- Gerenciar criptografia de dados pessoais
- Migrar dados existentes para formato criptografado
- Monitorar status da criptografia
- Integrar com sistema de auditoria
- Compliance LGPD/GDPR
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

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

class EncryptionManager:
    """Gerenciador do sistema de criptografia"""
    
    def __init__(self):
        """Inicializar o gerenciador de criptografia"""
        try:
            self.client = SupabaseClient()
            logger.info("Gerenciador de criptografia inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar gerenciador: {e}")
            raise
    
    def check_vault_status(self) -> Dict[str, Any]:
        """Verificar status do Supabase Vault"""
        try:
            # Verificar se Vault está instalado
            query = """
            SELECT 
                extname,
                extversion,
                CASE WHEN extname IS NOT NULL THEN true ELSE false END as installed
            FROM pg_extension 
            WHERE extname = 'vault'
            UNION ALL
            SELECT 'vault', 'not_installed', false
            WHERE NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vault')
            LIMIT 1;
            """
            
            result = self.client.client.rpc('sql', {'query': query}).execute()
            vault_info = result.data[0] if result.data else {'installed': False}
            
            # Verificar se schema crypto existe
            schema_query = """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'crypto';
            """
            
            schema_result = self.client.client.rpc('sql', {'query': schema_query}).execute()
            crypto_schema_exists = len(schema_result.data) > 0 if schema_result.data else False
            
            return {
                'vault_installed': vault_info.get('installed', False),
                'vault_version': vault_info.get('extversion'),
                'crypto_schema_exists': crypto_schema_exists,
                'status': 'ready' if vault_info.get('installed') and crypto_schema_exists else 'needs_setup'
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar status do Vault: {e}")
            return {'error': str(e)}
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """Obter status da criptografia"""
        try:
            # Verificar se a função existe
            function_check = """
            SELECT EXISTS (
                SELECT 1 FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'crypto' AND p.proname = 'get_encryption_status'
            ) as function_exists;
            """
            
            function_result = self.client.client.rpc('sql', {'query': function_check}).execute()
            
            if not function_result.data or not function_result.data[0]['function_exists']:
                return {
                    'encryption_system_exists': False,
                    'message': 'Sistema de criptografia não encontrado. Execute a migração primeiro.'
                }
            
            # Obter status da criptografia
            status_query = """
            SELECT * FROM crypto.get_encryption_status();
            """
            
            result = self.client.client.rpc('sql', {'query': status_query}).execute()
            
            if result.data:
                status_data = result.data
                
                # Calcular estatísticas gerais
                total_records = sum(row['total_records'] for row in status_data)
                total_encrypted = sum(row['encrypted_records'] for row in status_data)
                overall_percentage = (total_encrypted / total_records * 100) if total_records > 0 else 0
                
                return {
                    'encryption_system_exists': True,
                    'tables_status': status_data,
                    'overall_statistics': {
                        'total_records': total_records,
                        'total_encrypted': total_encrypted,
                        'encryption_percentage': round(overall_percentage, 2),
                        'last_encrypted': max(row['last_encrypted'] for row in status_data if row['last_encrypted'])
                    },
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'encryption_system_exists': True,
                    'tables_status': [],
                    'overall_statistics': {
                        'total_records': 0,
                        'total_encrypted': 0,
                        'encryption_percentage': 0
                    }
                }
            
        except Exception as e:
            logger.error(f"Erro ao obter status da criptografia: {e}")
            return {'error': str(e)}
    
    def execute_migration(self) -> Dict[str, Any]:
        """Executar migração completa de dados"""
        try:
            # Verificar se a função existe
            function_check = """
            SELECT EXISTS (
                SELECT 1 FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'crypto' AND p.proname = 'execute_full_migration'
            ) as function_exists;
            """
            
            function_result = self.client.client.rpc('sql', {'query': function_check}).execute()
            
            if not function_result.data or not function_result.data[0]['function_exists']:
                return {
                    'migration_available': False,
                    'message': 'Função de migração não encontrada. Execute a migração primeiro.'
                }
            
            logger.info("Iniciando migração completa de dados para formato criptografado...")
            
            # Executar migração
            migration_query = """
            SELECT * FROM crypto.execute_full_migration();
            """
            
            result = self.client.client.rpc('sql', {'query': migration_query}).execute()
            
            if result.data:
                migration_results = result.data
                
                # Calcular estatísticas da migração
                total_migrated = sum(row['migrated_count'] for row in migration_results)
                
                return {
                    'migration_available': True,
                    'migration_completed': True,
                    'results': migration_results,
                    'statistics': {
                        'total_migrated': total_migrated,
                        'tables_processed': len(migration_results),
                        'migration_time': datetime.now().isoformat()
                    }
                }
            else:
                return {
                    'migration_available': True,
                    'migration_completed': False,
                    'message': 'Migração executada mas sem resultados'
                }
            
        except Exception as e:
            logger.error(f"Erro durante migração: {e}")
            return {'error': str(e)}
    
    def test_encryption_access(self) -> Dict[str, Any]:
        """Testar acesso aos dados criptografados"""
        try:
            # Verificar se as views descriptografadas existem
            views_to_test = [
                'crypto.players_decrypted',
                'crypto.coaches_decrypted', 
                'crypto.referees_decrypted'
            ]
            
            test_results = {}
            
            for view in views_to_test:
                try:
                    # Tentar acessar a view
                    query = f"SELECT COUNT(*) as count FROM {view} LIMIT 1;"
                    result = self.client.client.rpc('sql', {'query': query}).execute()
                    
                    if result.data:
                        test_results[view] = {
                            'accessible': True,
                            'record_count': result.data[0]['count']
                        }
                    else:
                        test_results[view] = {
                            'accessible': False,
                            'error': 'No data returned'
                        }
                        
                except Exception as e:
                    test_results[view] = {
                        'accessible': False,
                        'error': str(e)
                    }
            
            return {
                'test_results': test_results,
                'overall_status': 'success' if all(r['accessible'] for r in test_results.values()) else 'partial',
                'tested_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao testar acesso: {e}")
            return {'error': str(e)}
    
    def get_personal_data_summary(self) -> Dict[str, Any]:
        """Obter resumo dos dados pessoais protegidos"""
        try:
            # Contar dados pessoais por tabela
            tables_info = {
                'players': {
                    'table': 'crypto.players_encrypted',
                    'personal_fields': ['firstname_encrypted', 'lastname_encrypted', 'date_of_birth_encrypted', 'nationality_encrypted', 'height_encrypted', 'weight_encrypted'],
                    'description': 'Dados pessoais de jogadores (nome, sobrenome, data nascimento, nacionalidade, dados biométricos)'
                },
                'coaches': {
                    'table': 'crypto.coaches_encrypted',
                    'personal_fields': ['firstname_encrypted', 'lastname_encrypted', 'nationality_encrypted'],
                    'description': 'Dados pessoais de treinadores (nome, sobrenome, nacionalidade)'
                },
                'referees': {
                    'table': 'crypto.referees_encrypted',
                    'personal_fields': ['firstname_encrypted', 'lastname_encrypted', 'nationality_encrypted'],
                    'description': 'Dados pessoais de árbitros (nome, sobrenome, nacionalidade)'
                }
            }
            
            summary = {}
            
            for table_name, info in tables_info.items():
                try:
                    # Contar registros com dados pessoais criptografados
                    query = f"""
                    SELECT 
                        COUNT(*) as total_records,
                        COUNT(CASE WHEN {info['personal_fields'][0]} IS NOT NULL THEN 1 END) as encrypted_records
                    FROM {info['table']};
                    """
                    
                    result = self.client.client.rpc('sql', {'query': query}).execute()
                    
                    if result.data:
                        data = result.data[0]
                        summary[table_name] = {
                            'description': info['description'],
                            'total_records': data['total_records'],
                            'encrypted_records': data['encrypted_records'],
                            'encryption_percentage': round((data['encrypted_records'] / data['total_records'] * 100), 2) if data['total_records'] > 0 else 0,
                            'personal_fields_count': len(info['personal_fields']),
                            'lgpd_compliance': 'ENHANCED' if data['encrypted_records'] > 0 else 'PENDING'
                        }
                    else:
                        summary[table_name] = {
                            'error': 'No data available'
                        }
                        
                except Exception as e:
                    summary[table_name] = {
                        'error': str(e)
                    }
            
            return {
                'personal_data_summary': summary,
                'lgpd_compliance_status': 'ENHANCED' if any(
                    'lgpd_compliance' in info and info['lgpd_compliance'] == 'ENHANCED' 
                    for info in summary.values()
                ) else 'PENDING',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo de dados pessoais: {e}")
            return {'error': str(e)}
    
    def generate_encryption_report(self) -> Dict[str, Any]:
        """Gerar relatório completo de criptografia"""
        logger.info("Gerando relatório completo de criptografia...")
        
        report = {
            'report_generated_at': datetime.now().isoformat(),
            'vault_status': self.check_vault_status(),
            'encryption_status': self.get_encryption_status(),
            'personal_data_summary': self.get_personal_data_summary(),
            'access_test': self.test_encryption_access(),
            'recommendations': []
        }
        
        # Adicionar recomendações baseadas nos dados
        recommendations = []
        
        # Verificar se Vault está instalado
        vault_status = report['vault_status']
        if not vault_status.get('vault_installed', False):
            recommendations.append({
                'type': 'CRITICAL',
                'message': 'Supabase Vault não está instalado. Execute a migração de criptografia.',
                'action': 'Aplicar migração 20250915_implement_data_encryption.sql'
            })
        
        # Verificar status da criptografia
        encryption_status = report['encryption_status']
        if encryption_status.get('encryption_system_exists', False):
            overall_stats = encryption_status.get('overall_statistics', {})
            encryption_percentage = overall_stats.get('encryption_percentage', 0)
            
            if encryption_percentage == 0:
                recommendations.append({
                    'type': 'WARNING',
                    'message': 'Nenhum dado foi criptografado ainda',
                    'action': 'Executar migração de dados: python3 bdfut/tools/encryption_manager.py --migrate'
                })
            elif encryption_percentage < 100:
                recommendations.append({
                    'type': 'INFO',
                    'message': f'Apenas {encryption_percentage}% dos dados estão criptografados',
                    'action': 'Considerar completar a migração dos dados restantes'
                })
            else:
                recommendations.append({
                    'type': 'SUCCESS',
                    'message': 'Todos os dados pessoais estão criptografados',
                    'action': 'Sistema de criptografia funcionando perfeitamente'
                })
        
        # Verificar compliance LGPD
        personal_data = report['personal_data_summary']
        lgpd_status = personal_data.get('lgpd_compliance_status', 'PENDING')
        
        if lgpd_status == 'ENHANCED':
            recommendations.append({
                'type': 'SUCCESS',
                'message': 'Compliance LGPD/GDPR aprimorado com criptografia',
                'action': 'Sistema em conformidade com proteção de dados pessoais'
            })
        else:
            recommendations.append({
                'type': 'WARNING',
                'message': 'Compliance LGPD/GDPR pendente',
                'action': 'Implementar criptografia completa para dados pessoais'
            })
        
        report['recommendations'] = recommendations
        
        return report

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciador do Sistema de Criptografia BDFut')
    parser.add_argument('--status', action='store_true', help='Verificar status do Vault e criptografia')
    parser.add_argument('--encryption-status', action='store_true', help='Obter status da criptografia')
    parser.add_argument('--migrate', action='store_true', help='Executar migração completa de dados')
    parser.add_argument('--test-access', action='store_true', help='Testar acesso aos dados criptografados')
    parser.add_argument('--personal-data', action='store_true', help='Obter resumo dos dados pessoais')
    parser.add_argument('--report', action='store_true', help='Gerar relatório completo de criptografia')
    
    args = parser.parse_args()
    
    try:
        manager = EncryptionManager()
        
        if args.status:
            print("🔐 Status do Vault e Criptografia:")
            status = manager.check_vault_status()
            print(json.dumps(status, indent=2, default=str))
        
        elif args.encryption_status:
            print("📊 Status da Criptografia:")
            status = manager.get_encryption_status()
            print(json.dumps(status, indent=2, default=str))
        
        elif args.migrate:
            print("🔄 Executando migração completa...")
            result = manager.execute_migration()
            print(json.dumps(result, indent=2, default=str))
        
        elif args.test_access:
            print("🔍 Testando acesso aos dados criptografados:")
            result = manager.test_encryption_access()
            print(json.dumps(result, indent=2, default=str))
        
        elif args.personal_data:
            print("👤 Resumo dos dados pessoais:")
            result = manager.get_personal_data_summary()
            print(json.dumps(result, indent=2, default=str))
        
        else:
            print("📊 Relatório completo de criptografia:")
            report = manager.generate_encryption_report()
            
            # Salvar relatório
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"logs/ENCRYPTION_REPORT_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📄 Relatório salvo em: {report_file}")
            
            # Mostrar resumo
            print("\n📊 RESUMO:")
            vault_status = report['vault_status']
            print(f"- Vault instalado: {vault_status.get('vault_installed', False)}")
            print(f"- Schema crypto existe: {vault_status.get('crypto_schema_exists', False)}")
            
            encryption_status = report['encryption_status']
            if encryption_status.get('encryption_system_exists', False):
                stats = encryption_status.get('overall_statistics', {})
                print(f"- Total de registros: {stats.get('total_records', 0)}")
                print(f"- Registros criptografados: {stats.get('total_encrypted', 0)}")
                print(f"- Percentual de criptografia: {stats.get('encryption_percentage', 0)}%")
            
            personal_data = report['personal_data_summary']
            print(f"- Compliance LGPD: {personal_data.get('lgpd_compliance_status', 'PENDING')}")
            print(f"- Recomendações: {len(report['recommendations'])}")
            
            # Mostrar recomendações críticas
            critical_recs = [r for r in report['recommendations'] if r['type'] == 'CRITICAL']
            if critical_recs:
                print("\n🚨 RECOMENDAÇÕES CRÍTICAS:")
                for rec in critical_recs:
                    print(f"- {rec['message']}")
                    print(f"  Ação: {rec['action']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
