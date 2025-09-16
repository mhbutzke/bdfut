#!/usr/bin/env python3
"""
Gerenciador do Sistema de Compliance LGPD/GDPR BDFut
==================================================

Responsável: Security Specialist 🔐
Task: SEC-005 - Implementar Compliance LGPD/GDPR
Data: 15 de Setembro de 2025

Funcionalidades:
- Gerenciar compliance LGPD/GDPR
- Mapear dados pessoais
- Controlar consentimentos
- Processar direitos dos titulares
- Gerar relatórios de compliance
- Integrar com auditoria e criptografia
"""

import sys
import os
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
import json
import uuid

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

class LGPDComplianceManager:
    """Gerenciador do sistema de compliance LGPD/GDPR"""
    
    def __init__(self):
        """Inicializar o gerenciador de compliance"""
        try:
            self.client = SupabaseClient()
            logger.info("Gerenciador de compliance LGPD/GDPR inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar gerenciador: {e}")
            raise
    
    def check_compliance_status(self) -> Dict[str, Any]:
        """Verificar status do sistema de compliance"""
        try:
            # Verificar se schema lgpd existe
            schema_check = """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'lgpd';
            """
            
            schema_result = self.client.client.rpc('sql', {'query': schema_check}).execute()
            lgpd_schema_exists = len(schema_result.data) > 0 if schema_result.data else False
            
            if not lgpd_schema_exists:
                return {
                    'compliance_system_exists': False,
                    'message': 'Sistema de compliance LGPD/GDPR não encontrado. Execute a migração primeiro.'
                }
            
            # Verificar componentes do sistema
            components_check = """
            SELECT 
                COUNT(*) as total_tables,
                COUNT(CASE WHEN table_name = 'personal_data_mapping' THEN 1 END) as mapping_table,
                COUNT(CASE WHEN table_name = 'consent_records' THEN 1 END) as consent_table,
                COUNT(CASE WHEN table_name = 'data_subject_rights' THEN 1 END) as rights_table,
                COUNT(CASE WHEN table_name = 'retention_policies' THEN 1 END) as retention_table,
                COUNT(CASE WHEN table_name = 'compliance_reports' THEN 1 END) as reports_table
            FROM information_schema.tables 
            WHERE table_schema = 'lgpd';
            """
            
            components_result = self.client.client.rpc('sql', {'query': components_check}).execute()
            
            if components_result.data:
                components = components_result.data[0]
                
                return {
                    'compliance_system_exists': True,
                    'components_status': {
                        'total_tables': components['total_tables'],
                        'personal_data_mapping': components['mapping_table'] > 0,
                        'consent_records': components['consent_table'] > 0,
                        'data_subject_rights': components['rights_table'] > 0,
                        'retention_policies': components['retention_table'] > 0,
                        'compliance_reports': components['reports_table'] > 0
                    },
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'compliance_system_exists': True,
                    'components_status': {
                        'total_tables': 0,
                        'personal_data_mapping': False,
                        'consent_records': False,
                        'data_subject_rights': False,
                        'retention_policies': False,
                        'compliance_reports': False
                    }
                }
            
        except Exception as e:
            logger.error(f"Erro ao verificar status de compliance: {e}")
            return {'error': str(e)}
    
    def get_personal_data_mapping(self) -> Dict[str, Any]:
        """Obter mapeamento de dados pessoais"""
        try:
            # Verificar se a função existe
            function_check = """
            SELECT EXISTS (
                SELECT 1 FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'lgpd' AND p.proname = 'map_personal_data'
            ) as function_exists;
            """
            
            function_result = self.client.client.rpc('sql', {'query': function_check}).execute()
            
            if not function_result.data or not function_result.data[0]['function_exists']:
                return {
                    'mapping_available': False,
                    'message': 'Função de mapeamento não encontrada. Execute a migração primeiro.'
                }
            
            # Obter mapeamento de dados pessoais
            mapping_query = """
            SELECT 
                table_name,
                schema_name,
                column_name,
                data_type,
                data_category,
                sensitivity_level,
                legal_basis,
                retention_period,
                purpose,
                is_encrypted
            FROM lgpd.personal_data_mapping
            ORDER BY table_name, column_name;
            """
            
            result = self.client.client.rpc('sql', {'query': mapping_query}).execute()
            
            if result.data:
                mapping_data = result.data
                
                # Calcular estatísticas
                total_fields = len(mapping_data)
                encrypted_fields = len([f for f in mapping_data if f['is_encrypted']])
                critical_fields = len([f for f in mapping_data if f['sensitivity_level'] == 'crítica'])
                high_sensitivity_fields = len([f for f in mapping_data if f['sensitivity_level'] == 'alta'])
                
                # Agrupar por categoria
                categories = {}
                for field in mapping_data:
                    category = field['data_category']
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(field)
                
                return {
                    'mapping_available': True,
                    'total_fields': total_fields,
                    'encrypted_fields': encrypted_fields,
                    'critical_fields': critical_fields,
                    'high_sensitivity_fields': high_sensitivity_fields,
                    'encryption_percentage': round((encrypted_fields / total_fields * 100), 2) if total_fields > 0 else 0,
                    'categories': categories,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'mapping_available': True,
                    'total_fields': 0,
                    'encrypted_fields': 0,
                    'critical_fields': 0,
                    'high_sensitivity_fields': 0,
                    'encryption_percentage': 0,
                    'categories': {},
                    'message': 'Nenhum dado pessoal mapeado ainda'
                }
            
        except Exception as e:
            logger.error(f"Erro ao obter mapeamento de dados pessoais: {e}")
            return {'error': str(e)}
    
    def get_consent_status(self) -> Dict[str, Any]:
        """Obter status de consentimentos"""
        try:
            # Verificar se a view existe
            view_check = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.views 
                WHERE table_schema = 'lgpd' AND table_name = 'consent_status'
            ) as view_exists;
            """
            
            view_result = self.client.client.rpc('sql', {'query': view_check}).execute()
            
            if not view_result.data or not view_result.data[0]['view_exists']:
                return {
                    'consent_status_available': False,
                    'message': 'View de status de consentimentos não encontrada. Execute a migração primeiro.'
                }
            
            # Obter status de consentimentos
            consent_query = """
            SELECT * FROM lgpd.consent_status;
            """
            
            result = self.client.client.rpc('sql', {'query': consent_query}).execute()
            
            if result.data:
                consent_data = result.data
                
                # Calcular estatísticas gerais
                total_consents = sum(row['total_consents'] for row in consent_data)
                consents_given = sum(row['consents_given'] for row in consent_data)
                consents_withdrawn = sum(row['consents_withdrawn'] for row in consent_data)
                overall_consent_rate = (consents_given / total_consents * 100) if total_consents > 0 else 0
                
                return {
                    'consent_status_available': True,
                    'consent_types': consent_data,
                    'overall_statistics': {
                        'total_consents': total_consents,
                        'consents_given': consents_given,
                        'consents_withdrawn': consents_withdrawn,
                        'overall_consent_rate': round(overall_consent_rate, 2)
                    },
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'consent_status_available': True,
                    'consent_types': [],
                    'overall_statistics': {
                        'total_consents': 0,
                        'consents_given': 0,
                        'consents_withdrawn': 0,
                        'overall_consent_rate': 0
                    },
                    'message': 'Nenhum consentimento registrado ainda'
                }
            
        except Exception as e:
            logger.error(f"Erro ao obter status de consentimentos: {e}")
            return {'error': str(e)}
    
    def get_rights_summary(self) -> Dict[str, Any]:
        """Obter resumo de direitos dos titulares"""
        try:
            # Verificar se a view existe
            view_check = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.views 
                WHERE table_schema = 'lgpd' AND table_name = 'rights_summary'
            ) as view_exists;
            """
            
            view_result = self.client.client.rpc('sql', {'query': view_check}).execute()
            
            if not view_result.data or not view_result.data[0]['view_exists']:
                return {
                    'rights_summary_available': False,
                    'message': 'View de resumo de direitos não encontrada. Execute a migração primeiro.'
                }
            
            # Obter resumo de direitos
            rights_query = """
            SELECT * FROM lgpd.rights_summary;
            """
            
            result = self.client.client.rpc('sql', {'query': rights_query}).execute()
            
            if result.data:
                rights_data = result.data
                
                # Calcular estatísticas gerais
                total_requests = sum(row['total_requests'] for row in rights_data)
                completed_requests = sum(row['completed_requests'] for row in rights_data)
                pending_requests = sum(row['pending_requests'] for row in rights_data)
                overall_completion_rate = (completed_requests / total_requests * 100) if total_requests > 0 else 0
                avg_processing_hours = sum(row['avg_processing_hours'] or 0 for row in rights_data) / len(rights_data) if rights_data else 0
                
                return {
                    'rights_summary_available': True,
                    'rights_types': rights_data,
                    'overall_statistics': {
                        'total_requests': total_requests,
                        'completed_requests': completed_requests,
                        'pending_requests': pending_requests,
                        'overall_completion_rate': round(overall_completion_rate, 2),
                        'avg_processing_hours': round(avg_processing_hours, 2)
                    },
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'rights_summary_available': True,
                    'rights_types': [],
                    'overall_statistics': {
                        'total_requests': 0,
                        'completed_requests': 0,
                        'pending_requests': 0,
                        'overall_completion_rate': 0,
                        'avg_processing_hours': 0
                    },
                    'message': 'Nenhum direito exercido ainda'
                }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo de direitos: {e}")
            return {'error': str(e)}
    
    def calculate_compliance_score(self) -> Dict[str, Any]:
        """Calcular score de compliance"""
        try:
            # Verificar se a função existe
            function_check = """
            SELECT EXISTS (
                SELECT 1 FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'lgpd' AND p.proname = 'calculate_compliance_score'
            ) as function_exists;
            """
            
            function_result = self.client.client.rpc('sql', {'query': function_check}).execute()
            
            if not function_result.data or not function_result.data[0]['function_exists']:
                return {
                    'score_calculation_available': False,
                    'message': 'Função de cálculo de score não encontrada. Execute a migração primeiro.'
                }
            
            # Calcular score de compliance
            score_query = """
            SELECT lgpd.calculate_compliance_score() as compliance_score;
            """
            
            result = self.client.client.rpc('sql', {'query': score_query}).execute()
            
            if result.data:
                score = result.data[0]['compliance_score']
                
                # Determinar nível de compliance
                if score >= 90:
                    compliance_level = 'EXCELENTE'
                elif score >= 80:
                    compliance_level = 'BOM'
                elif score >= 70:
                    compliance_level = 'ADEQUADO'
                elif score >= 60:
                    compliance_level = 'PARCIAL'
                else:
                    compliance_level = 'INSUFICIENTE'
                
                return {
                    'score_calculation_available': True,
                    'compliance_score': score,
                    'compliance_level': compliance_level,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'score_calculation_available': True,
                    'compliance_score': 0,
                    'compliance_level': 'INSUFICIENTE',
                    'message': 'Não foi possível calcular o score'
                }
            
        except Exception as e:
            logger.error(f"Erro ao calcular score de compliance: {e}")
            return {'error': str(e)}
    
    def generate_compliance_report(self, report_type: str = 'mensal') -> Dict[str, Any]:
        """Gerar relatório de compliance"""
        try:
            # Verificar se a função existe
            function_check = """
            SELECT EXISTS (
                SELECT 1 FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'lgpd' AND p.proname = 'generate_compliance_report'
            ) as function_exists;
            """
            
            function_result = self.client.client.rpc('sql', {'query': function_check}).execute()
            
            if not function_result.data or not function_result.data[0]['function_exists']:
                return {
                    'report_generation_available': False,
                    'message': 'Função de geração de relatório não encontrada. Execute a migração primeiro.'
                }
            
            # Calcular período baseado no tipo de relatório
            end_date = date.today()
            if report_type == 'mensal':
                start_date = end_date - timedelta(days=30)
            elif report_type == 'trimestral':
                start_date = end_date - timedelta(days=90)
            elif report_type == 'anual':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Gerar relatório
            report_query = f"""
            SELECT lgpd.generate_compliance_report('{report_type}', '{start_date}', '{end_date}') as report_id;
            """
            
            result = self.client.client.rpc('sql', {'query': report_query}).execute()
            
            if result.data:
                report_id = result.data[0]['report_id']
                
                # Obter detalhes do relatório
                details_query = f"""
                SELECT * FROM lgpd.compliance_reports WHERE id = '{report_id}';
                """
                
                details_result = self.client.client.rpc('sql', {'query': details_query}).execute()
                
                if details_result.data:
                    report_details = details_result.data[0]
                    
                    return {
                        'report_generation_available': True,
                        'report_id': report_id,
                        'report_type': report_type,
                        'period_start': str(start_date),
                        'period_end': str(end_date),
                        'report_details': report_details,
                        'generated_at': datetime.now().isoformat()
                    }
                else:
                    return {
                        'report_generation_available': True,
                        'report_id': report_id,
                        'message': 'Relatório gerado mas detalhes não encontrados'
                    }
            else:
                return {
                    'report_generation_available': True,
                    'message': 'Não foi possível gerar o relatório'
                }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de compliance: {e}")
            return {'error': str(e)}
    
    def generate_full_compliance_report(self) -> Dict[str, Any]:
        """Gerar relatório completo de compliance"""
        logger.info("Gerando relatório completo de compliance LGPD/GDPR...")
        
        report = {
            'report_generated_at': datetime.now().isoformat(),
            'compliance_status': self.check_compliance_status(),
            'personal_data_mapping': self.get_personal_data_mapping(),
            'consent_status': self.get_consent_status(),
            'rights_summary': self.get_rights_summary(),
            'compliance_score': self.calculate_compliance_score(),
            'recommendations': []
        }
        
        # Adicionar recomendações baseadas nos dados
        recommendations = []
        
        # Verificar se sistema de compliance existe
        compliance_status = report['compliance_status']
        if not compliance_status.get('compliance_system_exists', False):
            recommendations.append({
                'type': 'CRITICAL',
                'message': 'Sistema de compliance LGPD/GDPR não está instalado',
                'action': 'Aplicar migração 20250915_implement_lgpd_compliance.sql'
            })
        else:
            # Verificar componentes
            components = compliance_status.get('components_status', {})
            missing_components = []
            for component, exists in components.items():
                if component != 'total_tables' and not exists:
                    missing_components.append(component)
            
            if missing_components:
                recommendations.append({
                    'type': 'WARNING',
                    'message': f'Componentes faltando: {", ".join(missing_components)}',
                    'action': 'Verificar aplicação da migração de compliance'
                })
            
            # Verificar mapeamento de dados pessoais
            mapping = report['personal_data_mapping']
            if mapping.get('mapping_available', False):
                total_fields = mapping.get('total_fields', 0)
                if total_fields == 0:
                    recommendations.append({
                        'type': 'WARNING',
                        'message': 'Nenhum dado pessoal foi mapeado ainda',
                        'action': 'Executar mapeamento de dados pessoais'
                    })
                else:
                    encryption_percentage = mapping.get('encryption_percentage', 0)
                    if encryption_percentage < 100:
                        recommendations.append({
                            'type': 'INFO',
                            'message': f'Apenas {encryption_percentage}% dos dados pessoais estão criptografados',
                            'action': 'Considerar aumentar a cobertura de criptografia'
                        })
                    else:
                        recommendations.append({
                            'type': 'SUCCESS',
                            'message': 'Todos os dados pessoais estão criptografados',
                            'action': 'Excelente proteção de dados pessoais'
                        })
            
            # Verificar score de compliance
            score_data = report['compliance_score']
            if score_data.get('score_calculation_available', False):
                score = score_data.get('compliance_score', 0)
                level = score_data.get('compliance_level', 'INSUFICIENTE')
                
                if score < 60:
                    recommendations.append({
                        'type': 'CRITICAL',
                        'message': f'Score de compliance baixo: {score}% ({level})',
                        'action': 'Implementar controles de compliance urgentemente'
                    })
                elif score < 80:
                    recommendations.append({
                        'type': 'WARNING',
                        'message': f'Score de compliance moderado: {score}% ({level})',
                        'action': 'Melhorar controles de compliance'
                    })
                else:
                    recommendations.append({
                        'type': 'SUCCESS',
                        'message': f'Score de compliance excelente: {score}% ({level})',
                        'action': 'Sistema de compliance funcionando bem'
                    })
        
        report['recommendations'] = recommendations
        
        return report

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciador do Sistema de Compliance LGPD/GDPR BDFut')
    parser.add_argument('--status', action='store_true', help='Verificar status do sistema de compliance')
    parser.add_argument('--mapping', action='store_true', help='Obter mapeamento de dados pessoais')
    parser.add_argument('--consent', action='store_true', help='Obter status de consentimentos')
    parser.add_argument('--rights', action='store_true', help='Obter resumo de direitos dos titulares')
    parser.add_argument('--score', action='store_true', help='Calcular score de compliance')
    parser.add_argument('--report', action='store_true', help='Gerar relatório completo de compliance')
    parser.add_argument('--generate-report', type=str, choices=['mensal', 'trimestral', 'anual'], 
                       help='Gerar relatório específico de compliance')
    
    args = parser.parse_args()
    
    try:
        manager = LGPDComplianceManager()
        
        if args.status:
            print("🔐 Status do Sistema de Compliance LGPD/GDPR:")
            status = manager.check_compliance_status()
            print(json.dumps(status, indent=2, default=str))
        
        elif args.mapping:
            print("📊 Mapeamento de Dados Pessoais:")
            mapping = manager.get_personal_data_mapping()
            print(json.dumps(mapping, indent=2, default=str))
        
        elif args.consent:
            print("✅ Status de Consentimentos:")
            consent = manager.get_consent_status()
            print(json.dumps(consent, indent=2, default=str))
        
        elif args.rights:
            print("⚖️ Resumo de Direitos dos Titulares:")
            rights = manager.get_rights_summary()
            print(json.dumps(rights, indent=2, default=str))
        
        elif args.score:
            print("📈 Score de Compliance:")
            score = manager.calculate_compliance_score()
            print(json.dumps(score, indent=2, default=str))
        
        elif args.generate_report:
            print(f"📋 Gerando Relatório {args.generate_report}...")
            report = manager.generate_compliance_report(args.generate_report)
            print(json.dumps(report, indent=2, default=str))
        
        else:
            print("📊 Relatório completo de compliance LGPD/GDPR:")
            report = manager.generate_full_compliance_report()
            
            # Salvar relatório
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"logs/LGPD_COMPLIANCE_REPORT_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📄 Relatório salvo em: {report_file}")
            
            # Mostrar resumo
            print("\n📊 RESUMO:")
            compliance_status = report['compliance_status']
            print(f"- Sistema de compliance existe: {compliance_status.get('compliance_system_exists', False)}")
            
            if compliance_status.get('compliance_system_exists', False):
                components = compliance_status.get('components_status', {})
                print(f"- Total de tabelas: {components.get('total_tables', 0)}")
                print(f"- Mapeamento de dados: {components.get('personal_data_mapping', False)}")
                print(f"- Registros de consentimento: {components.get('consent_records', False)}")
                print(f"- Direitos dos titulares: {components.get('data_subject_rights', False)}")
            
            mapping = report['personal_data_mapping']
            if mapping.get('mapping_available', False):
                print(f"- Dados pessoais mapeados: {mapping.get('total_fields', 0)}")
                print(f"- Percentual de criptografia: {mapping.get('encryption_percentage', 0)}%")
            
            score_data = report['compliance_score']
            if score_data.get('score_calculation_available', False):
                print(f"- Score de compliance: {score_data.get('compliance_score', 0)}%")
                print(f"- Nível de compliance: {score_data.get('compliance_level', 'INSUFICIENTE')}")
            
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
