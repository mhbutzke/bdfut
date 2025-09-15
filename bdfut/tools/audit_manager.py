#!/usr/bin/env python3
"""
Gerenciador do Sistema de Auditoria BDFut
==========================================

Responsável: Security Specialist 🔐
Task: SEC-003 - Implementar Logs de Auditoria
Data: 15 de Setembro de 2025

Funcionalidades:
- Configurar e gerenciar pgaudit
- Monitorar logs de auditoria
- Detectar atividades suspeitas
- Gerar relatórios de auditoria
- Gerenciar alertas de segurança
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

class AuditManager:
    """Gerenciador do sistema de auditoria"""
    
    def __init__(self):
        """Inicializar o gerenciador de auditoria"""
        try:
            self.client = SupabaseClient()
            logger.info("Gerenciador de auditoria inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar gerenciador: {e}")
            raise
    
    def check_pgaudit_status(self) -> Dict[str, Any]:
        """Verificar status do pgaudit"""
        try:
            # Verificar se pgaudit está instalado
            query = """
            SELECT 
                extname,
                extversion,
                CASE WHEN extname IS NOT NULL THEN true ELSE false END as installed
            FROM pg_extension 
            WHERE extname = 'pgaudit'
            UNION ALL
            SELECT 'pgaudit', 'not_installed', false
            WHERE NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgaudit')
            LIMIT 1;
            """
            
            result = self.client.client.rpc('sql', {'query': query}).execute()
            extension_info = result.data[0] if result.data else {'installed': False}
            
            # Verificar configurações de auditoria
            config_query = """
            SELECT 
                rolname,
                rolconfig
            FROM pg_roles 
            WHERE rolconfig IS NOT NULL
            AND EXISTS (
                SELECT 1 FROM unnest(rolconfig) as c 
                WHERE c LIKE '%pgaudit%'
            );
            """
            
            config_result = self.client.client.rpc('sql', {'query': config_query}).execute()
            audit_configs = config_result.data if config_result.data else []
            
            return {
                'pgaudit_installed': extension_info.get('installed', False),
                'pgaudit_version': extension_info.get('extversion'),
                'audit_configurations': audit_configs,
                'total_configured_roles': len(audit_configs)
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar status do pgaudit: {e}")
            return {'error': str(e)}
    
    def get_audit_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Obter estatísticas de auditoria"""
        try:
            # Verificar se o schema de auditoria existe
            schema_check = """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'audit';
            """
            
            schema_result = self.client.client.rpc('sql', {'query': schema_check}).execute()
            
            if not schema_result.data:
                return {
                    'audit_schema_exists': False,
                    'message': 'Schema de auditoria não encontrado. Execute a migração primeiro.'
                }
            
            # Estatísticas dos últimos dias
            stats_query = f"""
            SELECT 
                COUNT(*) as total_activities,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT client_ip) as unique_ips,
                COUNT(DISTINCT operation_type) as operation_types,
                MIN(timestamp) as earliest_activity,
                MAX(timestamp) as latest_activity
            FROM audit.activity_log
            WHERE timestamp > NOW() - INTERVAL '{days} days';
            """
            
            stats_result = self.client.client.rpc('sql', {'query': stats_query}).execute()
            stats = stats_result.data[0] if stats_result.data else {}
            
            # Operações por tipo
            ops_query = f"""
            SELECT 
                operation_type,
                COUNT(*) as count,
                COUNT(DISTINCT user_id) as unique_users
            FROM audit.activity_log
            WHERE timestamp > NOW() - INTERVAL '{days} days'
            GROUP BY operation_type
            ORDER BY count DESC;
            """
            
            ops_result = self.client.client.rpc('sql', {'query': ops_query}).execute()
            operations = ops_result.data if ops_result.data else []
            
            return {
                'audit_schema_exists': True,
                'period_days': days,
                'statistics': stats,
                'operations_breakdown': operations,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {'error': str(e)}
    
    def detect_suspicious_activities(self) -> List[Dict[str, Any]]:
        """Detectar atividades suspeitas"""
        try:
            # Verificar se a função existe
            function_check = """
            SELECT EXISTS (
                SELECT 1 FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'audit' AND p.proname = 'detect_suspicious_activity'
            ) as function_exists;
            """
            
            function_result = self.client.client.rpc('sql', {'query': function_check}).execute()
            
            if not function_result.data or not function_result.data[0]['function_exists']:
                return [{
                    'alert_type': 'SYSTEM_ERROR',
                    'message': 'Função de detecção não encontrada. Sistema de auditoria pode não estar instalado.'
                }]
            
            # Executar detecção
            detection_query = """
            SELECT * FROM audit.detect_suspicious_activity();
            """
            
            result = self.client.client.rpc('sql', {'query': detection_query}).execute()
            suspicious_activities = result.data if result.data else []
            
            # Adicionar análises adicionais
            additional_checks = self._additional_security_checks()
            
            return suspicious_activities + additional_checks
            
        except Exception as e:
            logger.error(f"Erro ao detectar atividades suspeitas: {e}")
            return [{'alert_type': 'DETECTION_ERROR', 'error': str(e)}]
    
    def _additional_security_checks(self) -> List[Dict[str, Any]]:
        """Verificações adicionais de segurança"""
        alerts = []
        
        try:
            # Verificar atividade de DELETE em massa
            mass_delete_query = """
            SELECT 
                user_id,
                client_ip,
                COUNT(*) as delete_count,
                array_agg(DISTINCT table_name) as affected_tables
            FROM audit.activity_log
            WHERE operation_type = 'DELETE'
              AND timestamp > NOW() - INTERVAL '1 hour'
            GROUP BY user_id, client_ip
            HAVING COUNT(*) > 10;
            """
            
            result = self.client.client.rpc('sql', {'query': mass_delete_query}).execute()
            
            for activity in result.data or []:
                alerts.append({
                    'alert_type': 'MASS_DELETE_ACTIVITY',
                    'user_id': activity['user_id'],
                    'client_ip': activity['client_ip'],
                    'delete_count': activity['delete_count'],
                    'affected_tables': activity['affected_tables'],
                    'severity': 'CRITICAL'
                })
            
            # Verificar tentativas de acesso a tabelas sensíveis
            sensitive_access_query = """
            SELECT 
                user_id,
                client_ip,
                COUNT(*) as access_count,
                array_agg(DISTINCT table_name) as accessed_tables
            FROM audit.activity_log
            WHERE table_name IN ('users', 'auth', 'passwords', 'tokens')
              AND operation_type IN ('SELECT', 'UPDATE', 'DELETE')
              AND timestamp > NOW() - INTERVAL '24 hours'
            GROUP BY user_id, client_ip
            HAVING COUNT(*) > 5;
            """
            
            result = self.client.client.rpc('sql', {'query': sensitive_access_query}).execute()
            
            for activity in result.data or []:
                alerts.append({
                    'alert_type': 'SENSITIVE_DATA_ACCESS',
                    'user_id': activity['user_id'],
                    'client_ip': activity['client_ip'],
                    'access_count': activity['access_count'],
                    'accessed_tables': activity['accessed_tables'],
                    'severity': 'WARNING'
                })
            
        except Exception as e:
            logger.error(f"Erro nas verificações adicionais: {e}")
            alerts.append({
                'alert_type': 'CHECK_ERROR',
                'error': str(e),
                'severity': 'WARNING'
            })
        
        return alerts
    
    def create_security_alert(self, alert_type: str, alert_level: str, 
                            description: str, details: Dict = None) -> Optional[int]:
        """Criar alerta de segurança"""
        try:
            # Verificar se a função existe
            function_check = """
            SELECT EXISTS (
                SELECT 1 FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'audit' AND p.proname = 'create_security_alert'
            ) as function_exists;
            """
            
            function_result = self.client.client.rpc('sql', {'query': function_check}).execute()
            
            if not function_result.data or not function_result.data[0]['function_exists']:
                logger.error("Função create_security_alert não encontrada")
                return None
            
            # Criar alerta
            alert_query = f"""
            SELECT audit.create_security_alert(
                '{alert_type}',
                '{alert_level}',
                '{description}',
                NULL,
                NULL,
                '{json.dumps(details or {})}'::jsonb
            ) as alert_id;
            """
            
            result = self.client.client.rpc('sql', {'query': alert_query}).execute()
            
            if result.data:
                alert_id = result.data[0]['alert_id']
                logger.info(f"Alerta de segurança criado: {alert_id}")
                return alert_id
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta: {e}")
            return None
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Obter alertas recentes"""
        try:
            query = f"""
            SELECT 
                id,
                alert_time,
                alert_type,
                alert_level,
                description,
                user_id,
                client_ip,
                status,
                details
            FROM audit.security_alerts
            WHERE alert_time > NOW() - INTERVAL '{hours} hours'
            ORDER BY alert_time DESC;
            """
            
            result = self.client.client.rpc('sql', {'query': query}).execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Erro ao obter alertas: {e}")
            return []
    
    def cleanup_old_logs(self, retention_days: int = 90) -> int:
        """Limpar logs antigos"""
        try:
            # Verificar se a função existe
            function_check = """
            SELECT EXISTS (
                SELECT 1 FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'audit' AND p.proname = 'cleanup_old_logs'
            ) as function_exists;
            """
            
            function_result = self.client.client.rpc('sql', {'query': function_check}).execute()
            
            if not function_result.data or not function_result.data[0]['function_exists']:
                logger.error("Função cleanup_old_logs não encontrada")
                return 0
            
            # Executar limpeza
            cleanup_query = f"""
            SELECT audit.cleanup_old_logs({retention_days}) as deleted_count;
            """
            
            result = self.client.client.rpc('sql', {'query': cleanup_query}).execute()
            
            if result.data:
                deleted_count = result.data[0]['deleted_count']
                logger.info(f"Logs limpos: {deleted_count} registros removidos")
                return deleted_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao limpar logs: {e}")
            return 0
    
    def generate_audit_report(self, days: int = 30) -> Dict[str, Any]:
        """Gerar relatório completo de auditoria"""
        logger.info(f"Gerando relatório de auditoria para {days} dias...")
        
        report = {
            'report_generated_at': datetime.now().isoformat(),
            'period_days': days,
            'pgaudit_status': self.check_pgaudit_status(),
            'audit_statistics': self.get_audit_statistics(days),
            'suspicious_activities': self.detect_suspicious_activities(),
            'recent_alerts': self.get_recent_alerts(days * 24),
            'recommendations': []
        }
        
        # Adicionar recomendações baseadas nos dados
        recommendations = []
        
        # Verificar se pgaudit está instalado
        if not report['pgaudit_status'].get('pgaudit_installed', False):
            recommendations.append({
                'type': 'CRITICAL',
                'message': 'pgaudit não está instalado. Execute a migração de auditoria.',
                'action': 'Aplicar migração 20250915_implement_audit_logging.sql'
            })
        
        # Verificar atividade suspeita
        if report['suspicious_activities']:
            recommendations.append({
                'type': 'WARNING',
                'message': f"Detectadas {len(report['suspicious_activities'])} atividades suspeitas",
                'action': 'Investigar atividades suspeitas e criar alertas se necessário'
            })
        
        # Verificar volume de logs
        stats = report['audit_statistics'].get('statistics', {})
        total_activities = stats.get('total_activities', 0)
        
        if total_activities == 0:
            recommendations.append({
                'type': 'INFO',
                'message': 'Nenhuma atividade auditada encontrada',
                'action': 'Verificar se a configuração de auditoria está funcionando'
            })
        elif total_activities > 100000:
            recommendations.append({
                'type': 'WARNING',
                'message': f'Alto volume de logs: {total_activities} atividades',
                'action': 'Considerar ajustar configurações de auditoria ou limpeza automática'
            })
        
        report['recommendations'] = recommendations
        
        return report

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciador do Sistema de Auditoria BDFut')
    parser.add_argument('--status', action='store_true', help='Verificar status do pgaudit')
    parser.add_argument('--stats', type=int, default=7, help='Obter estatísticas (dias)')
    parser.add_argument('--suspicious', action='store_true', help='Detectar atividades suspeitas')
    parser.add_argument('--alerts', type=int, default=24, help='Obter alertas recentes (horas)')
    parser.add_argument('--cleanup', type=int, help='Limpar logs antigos (dias de retenção)')
    parser.add_argument('--report', type=int, default=30, help='Gerar relatório completo (dias)')
    parser.add_argument('--create-alert', nargs=3, metavar=('TYPE', 'LEVEL', 'DESCRIPTION'),
                        help='Criar alerta: tipo nível descrição')
    
    args = parser.parse_args()
    
    try:
        manager = AuditManager()
        
        if args.status:
            print("🔍 Status do pgaudit:")
            status = manager.check_pgaudit_status()
            print(json.dumps(status, indent=2, default=str))
        
        elif args.suspicious:
            print("🚨 Atividades suspeitas:")
            activities = manager.detect_suspicious_activities()
            for activity in activities:
                print(f"- {activity}")
        
        elif args.alerts:
            print(f"📢 Alertas das últimas {args.alerts} horas:")
            alerts = manager.get_recent_alerts(args.alerts)
            for alert in alerts:
                print(f"- [{alert['alert_level']}] {alert['alert_type']}: {alert['description']}")
        
        elif args.cleanup:
            print(f"🧹 Limpando logs antigos (retenção: {args.cleanup} dias)...")
            deleted = manager.cleanup_old_logs(args.cleanup)
            print(f"✅ {deleted} registros removidos")
        
        elif args.create_alert:
            alert_type, alert_level, description = args.create_alert
            print(f"📢 Criando alerta: {alert_type}")
            alert_id = manager.create_security_alert(alert_type, alert_level, description)
            if alert_id:
                print(f"✅ Alerta criado com ID: {alert_id}")
            else:
                print("❌ Erro ao criar alerta")
        
        else:
            print(f"📊 Relatório de auditoria ({args.report} dias):")
            report = manager.generate_audit_report(args.report)
            
            # Salvar relatório
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"logs/AUDIT_REPORT_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📄 Relatório salvo em: {report_file}")
            
            # Mostrar resumo
            print("\n📊 RESUMO:")
            print(f"- pgaudit instalado: {report['pgaudit_status'].get('pgaudit_installed', False)}")
            
            stats = report['audit_statistics'].get('statistics', {})
            print(f"- Total de atividades: {stats.get('total_activities', 0)}")
            print(f"- Usuários únicos: {stats.get('unique_users', 0)}")
            print(f"- IPs únicos: {stats.get('unique_ips', 0)}")
            print(f"- Atividades suspeitas: {len(report['suspicious_activities'])}")
            print(f"- Alertas recentes: {len(report['recent_alerts'])}")
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
