#!/usr/bin/env python3
"""
Gerenciador do Sistema de Monitoramento de Segurança BDFut
=========================================================

Responsável: Security Specialist 🔐
Task: SEC-006 - Configurar Monitoramento de Segurança
Data: 15 de Setembro de 2025

Funcionalidades:
- Gerenciar alertas de segurança
- Detectar anomalias
- Monitorar métricas de segurança
- Gerenciar incidentes
- Dashboard de segurança
- Integração com compliance, auditoria e criptografia
"""

import sys
import os
import logging
from datetime import datetime, timedelta
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

class SecurityMonitoringManager:
    """Gerenciador do sistema de monitoramento de segurança"""
    
    def __init__(self):
        """Inicializar o gerenciador de monitoramento"""
        try:
            self.client = SupabaseClient()
            logger.info("Gerenciador de monitoramento de segurança inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar gerenciador: {e}")
            raise
    
    def check_monitoring_status(self) -> Dict[str, Any]:
        """Verificar status do sistema de monitoramento"""
        try:
            # Verificar se schema security_monitoring existe
            schema_check = """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'security_monitoring';
            """
            
            schema_result = self.client.client.rpc('sql', {'query': schema_check}).execute()
            monitoring_schema_exists = len(schema_result.data) > 0 if schema_result.data else False
            
            if not monitoring_schema_exists:
                return {
                    'monitoring_system_exists': False,
                    'message': 'Sistema de monitoramento de segurança não encontrado. Execute a migração primeiro.'
                }
            
            # Verificar componentes do sistema
            components_check = """
            SELECT 
                COUNT(*) as total_tables,
                COUNT(CASE WHEN table_name = 'security_alerts_config' THEN 1 END) as alerts_config_table,
                COUNT(CASE WHEN table_name = 'security_alerts_history' THEN 1 END) as alerts_history_table,
                COUNT(CASE WHEN table_name = 'security_metrics' THEN 1 END) as metrics_table,
                COUNT(CASE WHEN table_name = 'security_incidents' THEN 1 END) as incidents_table,
                COUNT(CASE WHEN table_name = 'security_dashboards' THEN 1 END) as dashboards_table
            FROM information_schema.tables 
            WHERE table_schema = 'security_monitoring';
            """
            
            components_result = self.client.client.rpc('sql', {'query': components_check}).execute()
            
            if components_result.data:
                components = components_result.data[0]
                
                return {
                    'monitoring_system_exists': True,
                    'components_status': {
                        'total_tables': components['total_tables'],
                        'security_alerts_config': components['alerts_config_table'] > 0,
                        'security_alerts_history': components['alerts_history_table'] > 0,
                        'security_metrics': components['metrics_table'] > 0,
                        'security_incidents': components['incidents_table'] > 0,
                        'security_dashboards': components['dashboards_table'] > 0
                    },
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'monitoring_system_exists': True,
                    'components_status': {
                        'total_tables': 0,
                        'security_alerts_config': False,
                        'security_alerts_history': False,
                        'security_metrics': False,
                        'security_incidents': False,
                        'security_dashboards': False
                    }
                }
            
        except Exception as e:
            logger.error(f"Erro ao verificar status de monitoramento: {e}")
            return {'error': str(e)}
    
    def get_active_alerts(self) -> Dict[str, Any]:
        """Obter alertas ativos de segurança"""
        try:
            # Verificar se a view existe
            view_check = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.views 
                WHERE table_schema = 'security_monitoring' AND table_name = 'alerts_summary'
            ) as view_exists;
            """
            
            view_result = self.client.client.rpc('sql', {'query': view_check}).execute()
            
            if not view_result.data or not view_result.data[0]['view_exists']:
                return {
                    'alerts_summary_available': False,
                    'message': 'View de resumo de alertas não encontrada. Execute a migração primeiro.'
                }
            
            # Obter resumo de alertas
            alerts_query = """
            SELECT * FROM security_monitoring.alerts_summary;
            """
            
            result = self.client.client.rpc('sql', {'query': alerts_query}).execute()
            
            if result.data:
                alerts_data = result.data
                
                # Calcular estatísticas gerais
                total_alerts = sum(row['total_alerts'] for row in alerts_data)
                active_alerts = sum(row['active_alerts'] for row in alerts_data)
                resolved_alerts = sum(row['resolved_alerts'] for row in alerts_data)
                critical_alerts = len([a for a in alerts_data if a['severity_level'] == 'critical'])
                high_alerts = len([a for a in alerts_data if a['severity_level'] == 'high'])
                
                return {
                    'alerts_summary_available': True,
                    'alerts_summary': alerts_data,
                    'overall_statistics': {
                        'total_alerts': total_alerts,
                        'active_alerts': active_alerts,
                        'resolved_alerts': resolved_alerts,
                        'critical_alerts': critical_alerts,
                        'high_alerts': high_alerts,
                        'resolution_rate': round((resolved_alerts / total_alerts * 100), 2) if total_alerts > 0 else 0
                    },
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'alerts_summary_available': True,
                    'alerts_summary': [],
                    'overall_statistics': {
                        'total_alerts': 0,
                        'active_alerts': 0,
                        'resolved_alerts': 0,
                        'critical_alerts': 0,
                        'high_alerts': 0,
                        'resolution_rate': 0
                    },
                    'message': 'Nenhum alerta registrado ainda'
                }
            
        except Exception as e:
            logger.error(f"Erro ao obter alertas ativos: {e}")
            return {'error': str(e)}
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Obter métricas de segurança"""
        try:
            # Verificar se a view existe
            view_check = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.views 
                WHERE table_schema = 'security_monitoring' AND table_name = 'security_metrics_summary'
            ) as view_exists;
            """
            
            view_result = self.client.client.rpc('sql', {'query': view_check}).execute()
            
            if not view_result.data or not view_result.data[0]['view_exists']:
                return {
                    'metrics_summary_available': False,
                    'message': 'View de resumo de métricas não encontrada. Execute a migração primeiro.'
                }
            
            # Obter resumo de métricas
            metrics_query = """
            SELECT * FROM security_monitoring.security_metrics_summary;
            """
            
            result = self.client.client.rpc('sql', {'query': metrics_query}).execute()
            
            if result.data:
                metrics_data = result.data
                
                # Calcular estatísticas gerais
                total_metrics = len(metrics_data)
                avg_values = [m['avg_value'] for m in metrics_data if m['avg_value'] is not None]
                max_values = [m['max_value'] for m in metrics_data if m['max_value'] is not None]
                
                return {
                    'metrics_summary_available': True,
                    'metrics_summary': metrics_data,
                    'overall_statistics': {
                        'total_metrics': total_metrics,
                        'avg_metric_value': round(sum(avg_values) / len(avg_values), 2) if avg_values else 0,
                        'max_metric_value': max(max_values) if max_values else 0,
                        'last_updated': max([m['last_updated'] for m in metrics_data if m['last_updated']])
                    },
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'metrics_summary_available': True,
                    'metrics_summary': [],
                    'overall_statistics': {
                        'total_metrics': 0,
                        'avg_metric_value': 0,
                        'max_metric_value': 0,
                        'last_updated': None
                    },
                    'message': 'Nenhuma métrica registrada ainda'
                }
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas de segurança: {e}")
            return {'error': str(e)}
    
    def get_incidents_summary(self) -> Dict[str, Any]:
        """Obter resumo de incidentes de segurança"""
        try:
            # Verificar se a view existe
            view_check = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.views 
                WHERE table_schema = 'security_monitoring' AND table_name = 'incidents_summary'
            ) as view_exists;
            """
            
            view_result = self.client.client.rpc('sql', {'query': view_check}).execute()
            
            if not view_result.data or not view_result.data[0]['view_exists']:
                return {
                    'incidents_summary_available': False,
                    'message': 'View de resumo de incidentes não encontrada. Execute a migração primeiro.'
                }
            
            # Obter resumo de incidentes
            incidents_query = """
            SELECT * FROM security_monitoring.incidents_summary;
            """
            
            result = self.client.client.rpc('sql', {'query': incidents_query}).execute()
            
            if result.data:
                incidents_data = result.data
                
                # Calcular estatísticas gerais
                total_incidents = sum(row['total_incidents'] for row in incidents_data)
                open_incidents = sum(row['open_incidents'] for row in incidents_data)
                resolved_incidents = sum(row['resolved_incidents'] for row in incidents_data)
                incidents_with_data_compromise = sum(row['incidents_with_data_compromise'] for row in incidents_data)
                critical_incidents = len([i for i in incidents_data if i['severity_level'] == 'critical'])
                
                return {
                    'incidents_summary_available': True,
                    'incidents_summary': incidents_data,
                    'overall_statistics': {
                        'total_incidents': total_incidents,
                        'open_incidents': open_incidents,
                        'resolved_incidents': resolved_incidents,
                        'incidents_with_data_compromise': incidents_with_data_compromise,
                        'critical_incidents': critical_incidents,
                        'resolution_rate': round((resolved_incidents / total_incidents * 100), 2) if total_incidents > 0 else 0
                    },
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'incidents_summary_available': True,
                    'incidents_summary': [],
                    'overall_statistics': {
                        'total_incidents': 0,
                        'open_incidents': 0,
                        'resolved_incidents': 0,
                        'incidents_with_data_compromise': 0,
                        'critical_incidents': 0,
                        'resolution_rate': 0
                    },
                    'message': 'Nenhum incidente registrado ainda'
                }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo de incidentes: {e}")
            return {'error': str(e)}
    
    def check_security_alerts(self) -> Dict[str, Any]:
        """Verificar alertas de segurança"""
        try:
            # Verificar se a função existe
            function_check = """
            SELECT EXISTS (
                SELECT 1 FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'security_monitoring' AND p.proname = 'check_security_alerts'
            ) as function_exists;
            """
            
            function_result = self.client.client.rpc('sql', {'query': function_check}).execute()
            
            if not function_result.data or not function_result.data[0]['function_exists']:
                return {
                    'alert_checking_available': False,
                    'message': 'Função de verificação de alertas não encontrada. Execute a migração primeiro.'
                }
            
            # Verificar alertas de segurança
            alerts_query = """
            SELECT security_monitoring.check_security_alerts() as alerts_triggered;
            """
            
            result = self.client.client.rpc('sql', {'query': alerts_query}).execute()
            
            if result.data:
                alerts_triggered = result.data[0]['alerts_triggered']
                
                return {
                    'alert_checking_available': True,
                    'alerts_triggered': alerts_triggered,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'alert_checking_available': True,
                    'alerts_triggered': 0,
                    'message': 'Não foi possível verificar alertas'
                }
            
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de segurança: {e}")
            return {'error': str(e)}
    
    def calculate_security_metrics(self) -> Dict[str, Any]:
        """Calcular métricas de segurança"""
        try:
            # Verificar se a função existe
            function_check = """
            SELECT EXISTS (
                SELECT 1 FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'security_monitoring' AND p.proname = 'calculate_security_metrics'
            ) as function_exists;
            """
            
            function_result = self.client.client.rpc('sql', {'query': function_check}).execute()
            
            if not function_result.data or not function_result.data[0]['function_exists']:
                return {
                    'metrics_calculation_available': False,
                    'message': 'Função de cálculo de métricas não encontrada. Execute a migração primeiro.'
                }
            
            # Calcular métricas de segurança
            metrics_query = """
            SELECT security_monitoring.calculate_security_metrics() as metrics_calculated;
            """
            
            result = self.client.client.rpc('sql', {'query': metrics_query}).execute()
            
            if result.data:
                metrics_calculated = result.data[0]['metrics_calculated']
                
                return {
                    'metrics_calculation_available': True,
                    'metrics_calculated': metrics_calculated,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'metrics_calculation_available': True,
                    'metrics_calculated': 0,
                    'message': 'Não foi possível calcular métricas'
                }
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de segurança: {e}")
            return {'error': str(e)}
    
    def get_dashboards(self) -> Dict[str, Any]:
        """Obter dashboards de segurança"""
        try:
            # Verificar se a tabela existe
            table_check = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'security_monitoring' AND table_name = 'security_dashboards'
            ) as table_exists;
            """
            
            table_result = self.client.client.rpc('sql', {'query': table_check}).execute()
            
            if not table_result.data or not table_result.data[0]['table_exists']:
                return {
                    'dashboards_available': False,
                    'message': 'Tabela de dashboards não encontrada. Execute a migração primeiro.'
                }
            
            # Obter dashboards
            dashboards_query = """
            SELECT 
                dashboard_name, 
                dashboard_type, 
                description, 
                refresh_interval_seconds,
                is_public,
                created_by,
                created_at
            FROM security_monitoring.security_dashboards
            ORDER BY created_at DESC;
            """
            
            result = self.client.client.rpc('sql', {'query': dashboards_query}).execute()
            
            if result.data:
                dashboards_data = result.data
                
                return {
                    'dashboards_available': True,
                    'dashboards': dashboards_data,
                    'total_dashboards': len(dashboards_data),
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'dashboards_available': True,
                    'dashboards': [],
                    'total_dashboards': 0,
                    'message': 'Nenhum dashboard encontrado'
                }
            
        except Exception as e:
            logger.error(f"Erro ao obter dashboards: {e}")
            return {'error': str(e)}
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Gerar relatório completo de segurança"""
        logger.info("Gerando relatório completo de monitoramento de segurança...")
        
        report = {
            'report_generated_at': datetime.now().isoformat(),
            'monitoring_status': self.check_monitoring_status(),
            'active_alerts': self.get_active_alerts(),
            'security_metrics': self.get_security_metrics(),
            'incidents_summary': self.get_incidents_summary(),
            'dashboards': self.get_dashboards(),
            'recommendations': []
        }
        
        # Adicionar recomendações baseadas nos dados
        recommendations = []
        
        # Verificar se sistema de monitoramento existe
        monitoring_status = report['monitoring_status']
        if not monitoring_status.get('monitoring_system_exists', False):
            recommendations.append({
                'type': 'CRITICAL',
                'message': 'Sistema de monitoramento de segurança não está instalado',
                'action': 'Aplicar migração 20250915_implement_security_monitoring.sql'
            })
        else:
            # Verificar componentes
            components = monitoring_status.get('components_status', {})
            missing_components = []
            for component, exists in components.items():
                if component != 'total_tables' and not exists:
                    missing_components.append(component)
            
            if missing_components:
                recommendations.append({
                    'type': 'WARNING',
                    'message': f'Componentes faltando: {", ".join(missing_components)}',
                    'action': 'Verificar aplicação da migração de monitoramento'
                })
            
            # Verificar alertas ativos
            alerts = report['active_alerts']
            if alerts.get('alerts_summary_available', False):
                active_alerts = alerts.get('overall_statistics', {}).get('active_alerts', 0)
                critical_alerts = alerts.get('overall_statistics', {}).get('critical_alerts', 0)
                
                if critical_alerts > 0:
                    recommendations.append({
                        'type': 'CRITICAL',
                        'message': f'{critical_alerts} alertas críticos ativos',
                        'action': 'Investigar e resolver alertas críticos imediatamente'
                    })
                elif active_alerts > 0:
                    recommendations.append({
                        'type': 'WARNING',
                        'message': f'{active_alerts} alertas ativos',
                        'action': 'Revisar e resolver alertas pendentes'
                    })
                else:
                    recommendations.append({
                        'type': 'SUCCESS',
                        'message': 'Nenhum alerta ativo',
                        'action': 'Sistema de monitoramento funcionando adequadamente'
                    })
            
            # Verificar incidentes
            incidents = report['incidents_summary']
            if incidents.get('incidents_summary_available', False):
                open_incidents = incidents.get('overall_statistics', {}).get('open_incidents', 0)
                incidents_with_data_compromise = incidents.get('overall_statistics', {}).get('incidents_with_data_compromise', 0)
                
                if incidents_with_data_compromise > 0:
                    recommendations.append({
                        'type': 'CRITICAL',
                        'message': f'{incidents_with_data_compromise} incidentes com comprometimento de dados',
                        'action': 'Investigar incidentes de comprometimento de dados urgentemente'
                    })
                elif open_incidents > 0:
                    recommendations.append({
                        'type': 'WARNING',
                        'message': f'{open_incidents} incidentes abertos',
                        'action': 'Resolver incidentes pendentes'
                    })
            
            # Verificar métricas
            metrics = report['security_metrics']
            if metrics.get('metrics_summary_available', False):
                total_metrics = metrics.get('overall_statistics', {}).get('total_metrics', 0)
                if total_metrics == 0:
                    recommendations.append({
                        'type': 'INFO',
                        'message': 'Nenhuma métrica de segurança coletada',
                        'action': 'Executar cálculo de métricas de segurança'
                    })
                else:
                    recommendations.append({
                        'type': 'SUCCESS',
                        'message': f'{total_metrics} métricas de segurança coletadas',
                        'action': 'Sistema de métricas funcionando adequadamente'
                    })
        
        report['recommendations'] = recommendations
        
        return report

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciador do Sistema de Monitoramento de Segurança BDFut')
    parser.add_argument('--status', action='store_true', help='Verificar status do sistema de monitoramento')
    parser.add_argument('--alerts', action='store_true', help='Obter alertas ativos de segurança')
    parser.add_argument('--metrics', action='store_true', help='Obter métricas de segurança')
    parser.add_argument('--incidents', action='store_true', help='Obter resumo de incidentes')
    parser.add_argument('--check-alerts', action='store_true', help='Verificar alertas de segurança')
    parser.add_argument('--calculate-metrics', action='store_true', help='Calcular métricas de segurança')
    parser.add_argument('--dashboards', action='store_true', help='Obter dashboards de segurança')
    parser.add_argument('--report', action='store_true', help='Gerar relatório completo de monitoramento')
    
    args = parser.parse_args()
    
    try:
        manager = SecurityMonitoringManager()
        
        if args.status:
            print("🔐 Status do Sistema de Monitoramento de Segurança:")
            status = manager.check_monitoring_status()
            print(json.dumps(status, indent=2, default=str))
        
        elif args.alerts:
            print("🚨 Alertas Ativos de Segurança:")
            alerts = manager.get_active_alerts()
            print(json.dumps(alerts, indent=2, default=str))
        
        elif args.metrics:
            print("📊 Métricas de Segurança:")
            metrics = manager.get_security_metrics()
            print(json.dumps(metrics, indent=2, default=str))
        
        elif args.incidents:
            print("🔍 Resumo de Incidentes:")
            incidents = manager.get_incidents_summary()
            print(json.dumps(incidents, indent=2, default=str))
        
        elif args.check_alerts:
            print("🔍 Verificando Alertas de Segurança:")
            alerts_check = manager.check_security_alerts()
            print(json.dumps(alerts_check, indent=2, default=str))
        
        elif args.calculate_metrics:
            print("📈 Calculando Métricas de Segurança:")
            metrics_calc = manager.calculate_security_metrics()
            print(json.dumps(metrics_calc, indent=2, default=str))
        
        elif args.dashboards:
            print("📊 Dashboards de Segurança:")
            dashboards = manager.get_dashboards()
            print(json.dumps(dashboards, indent=2, default=str))
        
        else:
            print("📊 Relatório completo de monitoramento de segurança:")
            report = manager.generate_security_report()
            
            # Salvar relatório
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"logs/SECURITY_MONITORING_REPORT_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📄 Relatório salvo em: {report_file}")
            
            # Mostrar resumo
            print("\n📊 RESUMO:")
            monitoring_status = report['monitoring_status']
            print(f"- Sistema de monitoramento existe: {monitoring_status.get('monitoring_system_exists', False)}")
            
            if monitoring_status.get('monitoring_system_exists', False):
                components = monitoring_status.get('components_status', {})
                print(f"- Total de tabelas: {components.get('total_tables', 0)}")
                print(f"- Configuração de alertas: {components.get('security_alerts_config', False)}")
                print(f"- Histórico de alertas: {components.get('security_alerts_history', False)}")
                print(f"- Métricas de segurança: {components.get('security_metrics', False)}")
                print(f"- Incidentes de segurança: {components.get('security_incidents', False)}")
                print(f"- Dashboards de segurança: {components.get('security_dashboards', False)}")
            
            alerts = report['active_alerts']
            if alerts.get('alerts_summary_available', False):
                stats = alerts.get('overall_statistics', {})
                print(f"- Alertas ativos: {stats.get('active_alerts', 0)}")
                print(f"- Alertas críticos: {stats.get('critical_alerts', 0)}")
                print(f"- Taxa de resolução: {stats.get('resolution_rate', 0)}%")
            
            incidents = report['incidents_summary']
            if incidents.get('incidents_summary_available', False):
                stats = incidents.get('overall_statistics', {})
                print(f"- Incidentes abertos: {stats.get('open_incidents', 0)}")
                print(f"- Incidentes com comprometimento: {stats.get('incidents_with_data_compromise', 0)}")
            
            metrics = report['security_metrics']
            if metrics.get('metrics_summary_available', False):
                stats = metrics.get('overall_statistics', {})
                print(f"- Métricas coletadas: {stats.get('total_metrics', 0)}")
            
            dashboards = report['dashboards']
            if dashboards.get('dashboards_available', False):
                print(f"- Dashboards disponíveis: {dashboards.get('total_dashboards', 0)}")
            
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
