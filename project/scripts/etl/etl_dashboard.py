#!/usr/bin/env python3
"""
Dashboard de Monitoramento ETL
=============================

Script para visualizar métricas, logs e status do sistema ETL.

Autor: ETL Engineer
Data: 17 de Janeiro de 2025
Task: 2.4 - Dashboard de Monitoramento ETL
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
import json

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.monitoring import ETLMonitor, ETLHealthStatus
from etl.config import ETLConfig

def print_header(title: str):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_section(title: str):
    """Imprime seção formatada"""
    print(f"\n📊 {title}")
    print("-" * 40)

def format_duration(seconds: int) -> str:
    """Formata duração em formato legível"""
    if seconds is None:
        return "N/A"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def format_datetime(dt) -> str:
    """Formata datetime em formato legível"""
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def show_health_status(monitor: ETLMonitor):
    """Mostra status de saúde do sistema"""
    print_section("Status de Saúde do Sistema ETL")
    
    health = monitor.get_health_status()
    
    print(f"🔄 Execuções Totais: {health.total_executions}")
    print(f"▶️  Em Execução: {health.running_executions}")
    print(f"✅ Concluídas: {health.completed_executions}")
    print(f"❌ Falhadas: {health.failed_executions}")
    
    if health.avg_duration_seconds:
        print(f"⏱️  Duração Média: {format_duration(int(health.avg_duration_seconds))}")
    
    if health.avg_success_rate:
        print(f"📈 Taxa de Sucesso Média: {health.avg_success_rate:.1f}%")
    
    print(f"🕐 Última Execução: {format_datetime(health.last_execution_at)}")
    print(f"📝 Logs (24h): {health.total_logs_24h}")
    print(f"🚨 Erros (24h): {health.error_logs_24h}")
    
    # Status geral
    if health.running_executions > 0:
        print(f"\n⚠️  ATENÇÃO: {health.running_executions} execução(ões) ainda em execução")
    
    if health.error_logs_24h > 10:
        print(f"\n🚨 ALERTA: Muitos erros nas últimas 24h ({health.error_logs_24h})")

def show_execution_summary(monitor: ETLMonitor, execution_id: str):
    """Mostra resumo de execução específica"""
    print_section(f"Resumo da Execução: {execution_id}")
    
    summary = monitor.get_execution_summary(execution_id)
    if not summary:
        print("❌ Execução não encontrada")
        return
    
    print(f"🆔 ID: {summary.execution_id}")
    print(f"📊 Status: {summary.status}")
    print(f"🕐 Iniciada: {format_datetime(summary.started_at)}")
    print(f"🕐 Finalizada: {format_datetime(summary.finished_at)}")
    print(f"⏱️  Duração: {format_duration(summary.duration_seconds)}")
    
    print(f"\n📈 Estatísticas:")
    print(f"   Total de Fixtures: {summary.total_fixtures:,}")
    print(f"   Processadas: {summary.processed_fixtures:,}")
    print(f"   Sucessos: {summary.successful_fixtures:,}")
    print(f"   Falhas: {summary.failed_fixtures:,}")
    
    if summary.processed_fixtures > 0:
        success_rate = (summary.successful_fixtures / summary.processed_fixtures) * 100
        print(f"   Taxa de Sucesso: {success_rate:.1f}%")
    
    print(f"\n📦 Chunks:")
    print(f"   Total: {summary.total_chunks}")
    print(f"   Processados: {summary.processed_chunks}")
    
    if summary.duration_seconds and summary.duration_seconds > 0:
        rate = summary.processed_fixtures / summary.duration_seconds
        print(f"\n🚀 Performance:")
        print(f"   Taxa: {rate:.1f} fixtures/s")
    
    if summary.error_message:
        print(f"\n❌ Erro: {summary.error_message}")

def show_recent_logs(monitor: ETLMonitor, limit: int = 20):
    """Mostra logs recentes"""
    print_section(f"Logs Recentes (últimos {limit})")
    
    try:
        cursor = monitor.connection.cursor()
        cursor.execute("""
            SELECT timestamp, level, component, message, execution_id, chunk_id
            FROM etl_logs
            ORDER BY timestamp DESC
            LIMIT %s
        """, (limit,))
        
        logs = cursor.fetchall()
        cursor.close()
        
        if not logs:
            print("📝 Nenhum log encontrado")
            return
        
        for log in logs:
            timestamp, level, component, message, execution_id, chunk_id = log
            
            # Ícone baseado no nível
            icon = {
                'DEBUG': '🔍',
                'INFO': 'ℹ️',
                'WARNING': '⚠️',
                'ERROR': '❌',
                'CRITICAL': '🚨'
            }.get(level, '📝')
            
            # Formata timestamp
            ts_str = timestamp.strftime("%H:%M:%S")
            
            # Formata mensagem
            msg_parts = [f"{icon} {ts_str} [{level}] {component}"]
            if execution_id:
                msg_parts.append(f"exec:{execution_id[:8]}")
            if chunk_id:
                msg_parts.append(f"chunk:{chunk_id}")
            msg_parts.append(message)
            
            print(" ".join(msg_parts))
    
    except Exception as e:
        print(f"❌ Erro ao obter logs: {e}")

def show_metrics_summary(monitor: ETLMonitor, hours: int = 24):
    """Mostra resumo de métricas"""
    print_section(f"Métricas das Últimas {hours}h")
    
    try:
        cursor = monitor.connection.cursor()
        cursor.execute("""
            SELECT metric_name, AVG(metric_value) as avg_value, 
                   MAX(metric_value) as max_value, COUNT(*) as count
            FROM etl_metrics
            WHERE timestamp > NOW() - INTERVAL '%s hours'
            GROUP BY metric_name
            ORDER BY metric_name
        """, (hours,))
        
        metrics = cursor.fetchall()
        cursor.close()
        
        if not metrics:
            print("📊 Nenhuma métrica encontrada")
            return
        
        for metric in metrics:
            name, avg_val, max_val, count = metric
            print(f"📊 {name}:")
            print(f"   Média: {avg_val:.2f}")
            print(f"   Máximo: {max_val:.2f}")
            print(f"   Amostras: {count}")
    
    except Exception as e:
        print(f"❌ Erro ao obter métricas: {e}")

def show_alerts(monitor: ETLMonitor):
    """Mostra alertas do sistema"""
    print_section("Alertas do Sistema")
    
    try:
        from etl.monitoring import ETLAlertManager
        alert_manager = ETLAlertManager(monitor)
        
        # Verifica alertas do sistema
        system_alerts = alert_manager.check_system_alerts()
        
        if system_alerts:
            for alert in system_alerts:
                print(f"🚨 {alert}")
        else:
            print("✅ Nenhum alerta encontrado")
    
    except Exception as e:
        print(f"❌ Erro ao verificar alertas: {e}")

def export_data(monitor: ETLMonitor, output_file: str):
    """Exporta dados para arquivo JSON"""
    print_section(f"Exportando dados para {output_file}")
    
    try:
        data = {
            'exported_at': datetime.now().isoformat(),
            'health_status': {},
            'recent_executions': [],
            'recent_logs': []
        }
        
        # Status de saúde
        health = monitor.get_health_status()
        data['health_status'] = {
            'total_executions': health.total_executions,
            'running_executions': health.running_executions,
            'completed_executions': health.completed_executions,
            'failed_executions': health.failed_executions,
            'avg_duration_seconds': health.avg_duration_seconds,
            'avg_success_rate': health.avg_success_rate,
            'last_execution_at': health.last_execution_at.isoformat() if health.last_execution_at else None,
            'total_logs_24h': health.total_logs_24h,
            'error_logs_24h': health.error_logs_24h
        }
        
        # Execuções recentes
        cursor = monitor.connection.cursor()
        cursor.execute("""
            SELECT execution_id, status, started_at, finished_at, 
                   duration_seconds, total_fixtures, processed_fixtures,
                   successful_fixtures, failed_fixtures
            FROM etl_executions
            ORDER BY started_at DESC
            LIMIT 10
        """)
        
        executions = cursor.fetchall()
        for exec_data in executions:
            data['recent_executions'].append({
                'execution_id': exec_data[0],
                'status': exec_data[1],
                'started_at': exec_data[2].isoformat() if exec_data[2] else None,
                'finished_at': exec_data[3].isoformat() if exec_data[3] else None,
                'duration_seconds': exec_data[4],
                'total_fixtures': exec_data[5],
                'processed_fixtures': exec_data[6],
                'successful_fixtures': exec_data[7],
                'failed_fixtures': exec_data[8]
            })
        
        # Logs recentes
        cursor.execute("""
            SELECT timestamp, level, component, message, execution_id, chunk_id
            FROM etl_logs
            ORDER BY timestamp DESC
            LIMIT 100
        """)
        
        logs = cursor.fetchall()
        for log_data in logs:
            data['recent_logs'].append({
                'timestamp': log_data[0].isoformat(),
                'level': log_data[1],
                'component': log_data[2],
                'message': log_data[3],
                'execution_id': log_data[4],
                'chunk_id': log_data[5]
            })
        
        cursor.close()
        
        # Salva arquivo
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dados exportados com sucesso para {output_file}")
        print(f"📊 {len(data['recent_executions'])} execuções")
        print(f"📝 {len(data['recent_logs'])} logs")
    
    except Exception as e:
        print(f"❌ Erro ao exportar dados: {e}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Dashboard de monitoramento ETL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Status geral do sistema
  python etl_dashboard.py

  # Resumo de execução específica
  python etl_dashboard.py --execution-id etl_20250117_143022_abc123

  # Logs recentes
  python etl_dashboard.py --logs --limit 50

  # Métricas das últimas 6 horas
  python etl_dashboard.py --metrics --hours 6

  # Exportar dados
  python etl_dashboard.py --export etl_data.json

  # Verificar alertas
  python etl_dashboard.py --alerts
        """
    )
    
    parser.add_argument(
        '--execution-id',
        help='ID da execução para mostrar resumo detalhado'
    )
    
    parser.add_argument(
        '--logs',
        action='store_true',
        help='Mostrar logs recentes'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Número de logs para mostrar (padrão: 20)'
    )
    
    parser.add_argument(
        '--metrics',
        action='store_true',
        help='Mostrar resumo de métricas'
    )
    
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Horas para métricas (padrão: 24)'
    )
    
    parser.add_argument(
        '--alerts',
        action='store_true',
        help='Verificar alertas do sistema'
    )
    
    parser.add_argument(
        '--export',
        help='Exportar dados para arquivo JSON'
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
    
    # Conecta ao banco
    config = ETLConfig.get_connection_params()
    monitor = ETLMonitor(config['connection_string'])
    monitor.connect()
    
    try:
        print_header("Dashboard de Monitoramento ETL")
        print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Status geral (sempre mostra)
        show_health_status(monitor)
        
        # Resumo de execução específica
        if args.execution_id:
            show_execution_summary(monitor, args.execution_id)
        
        # Logs recentes
        if args.logs:
            show_recent_logs(monitor, args.limit)
        
        # Métricas
        if args.metrics:
            show_metrics_summary(monitor, args.hours)
        
        # Alertas
        if args.alerts:
            show_alerts(monitor)
        
        # Exportar dados
        if args.export:
            export_data(monitor, args.export)
        
        # Se nenhuma opção específica foi escolhida, mostra tudo
        if not any([args.execution_id, args.logs, args.metrics, args.alerts, args.export]):
            show_recent_logs(monitor, 10)
            show_metrics_summary(monitor, 24)
            show_alerts(monitor)
        
        print("\n" + "=" * 60)
        print("✅ Dashboard concluído")
    
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        sys.exit(1)
    finally:
        monitor.disconnect()

if __name__ == "__main__":
    main()
