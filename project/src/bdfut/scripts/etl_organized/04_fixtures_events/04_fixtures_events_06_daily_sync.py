#!/usr/bin/env python3
"""
04_fixtures_events_06_daily_sync.py
===================================

Script de sincronização diária incremental para manter dados atualizados.

DEPENDÊNCIAS:
- Sistema de cache Redis funcionando
- Tabelas de metadados ETL criadas
- Dados base populados

FUNCIONALIDADE:
- Sincronização incremental inteligente
- Detecção automática de mudanças
- Otimização com cache Redis
- Monitoramento com metadados ETL
- Sistema de agendamento automático
"""

import os
import sys
import time
import logging
import schedule
from datetime import datetime, timedelta
from typing import Dict, Any

# Adicionar o diretório bdfut ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from bdfut.core.incremental_sync import IncrementalSyncManager, ScheduledSyncRunner

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'bdfut/logs/daily_sync_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_daily_sync_once():
    """Executa uma sincronização diária única"""
    logger.info("🌅 SINCRONIZAÇÃO DIÁRIA INICIADA")
    logger.info("=" * 50)
    
    try:
        # Inicializar gerenciador
        sync_manager = IncrementalSyncManager(use_redis=True)
        
        # Executar sincronização diária
        results = sync_manager.run_daily_sync(include_standings=True)
        
        # Log dos resultados
        logger.info("📊 RESULTADOS DA SINCRONIZAÇÃO:")
        
        if results['fixtures_sync']:
            fixtures_stats = results['fixtures_sync']
            if not fixtures_stats.get('skipped', False):
                logger.info(f"  🏆 Fixtures: {fixtures_stats.get('fixtures_processed', 0)} processadas")
            else:
                logger.info(f"  🏆 Fixtures: Pulada - {fixtures_stats.get('reason', 'N/A')}")
        
        if results['standings_sync']:
            standings_stats = results['standings_sync']
            logger.info(f"  📊 Classificações: {standings_stats.get('standings_synced', 0)} entradas")
        
        if results['base_data_sync']:
            base_stats = results['base_data_sync']
            total_base = (base_stats.get('countries_synced', 0) + 
                         base_stats.get('states_synced', 0) + 
                         base_stats.get('types_synced', 0))
            logger.info(f"  📋 Dados base: {total_base} registros")
        
        success = results.get('overall_success', False)
        duration = results.get('duration_seconds', 0)
        
        logger.info(f"✅ Status: {'SUCESSO' if success else 'FALHA'}")
        logger.info(f"⏱️ Duração: {duration}s ({duration//60}min)")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erro durante sincronização diária: {e}")
        return False

def run_continuous_sync():
    """Executa sincronização contínua com agendamento"""
    logger.info("🔄 MODO SINCRONIZAÇÃO CONTÍNUA")
    logger.info("=" * 50)
    
    try:
        # Inicializar componentes
        sync_manager = IncrementalSyncManager(use_redis=True)
        scheduler = ScheduledSyncRunner(sync_manager)
        
        # Configurar agendamentos
        logger.info("⏰ Configurando agendamentos...")
        
        # Sincronização crítica (fixtures de hoje) - a cada 15 minutos
        schedule.every(15).minutes.do(
            lambda: sync_manager.sync_today_fixtures()
        ).tag('critical')
        
        # Sincronização de fixtures recentes - a cada hora
        schedule.every().hour.do(
            lambda: sync_manager.sync_recent_fixtures()
        ).tag('hourly')
        
        # Sincronização diária completa - todo dia às 06:00
        schedule.every().day.at("06:00").do(
            lambda: sync_manager.run_daily_sync(include_standings=True)
        ).tag('daily')
        
        # Sincronização de dados base - toda segunda às 02:00
        schedule.every().monday.at("02:00").do(
            lambda: sync_manager.sync_base_data_incremental()
        ).tag('weekly')
        
        logger.info("✅ Agendamentos configurados:")
        logger.info("  • Fixtures críticas: A cada 15 minutos")
        logger.info("  • Fixtures recentes: A cada hora")
        logger.info("  • Sincronização completa: Diário às 06:00")
        logger.info("  • Dados base: Segunda às 02:00")
        
        # Loop principal
        logger.info("🔄 Iniciando loop de sincronização...")
        
        while True:
            try:
                # Executar jobs agendados
                schedule.run_pending()
                
                # Verificar status a cada 5 minutos
                time.sleep(300)  # 5 minutos
                
                # Log de status (opcional)
                now = datetime.now()
                if now.minute % 30 == 0:  # A cada 30 minutos
                    status = sync_manager.get_sync_status()
                    logger.info(f"💓 Heartbeat - {now.strftime('%H:%M')} - Sistema ativo")
                
            except KeyboardInterrupt:
                logger.info("⏹️ Sincronização interrompida pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop de sincronização: {e}")
                time.sleep(60)  # Pausa de 1 minuto antes de tentar novamente
        
        logger.info("🛑 Sincronização contínua finalizada")
        
    except Exception as e:
        logger.error(f"❌ Erro fatal na sincronização contínua: {e}")

def run_smart_sync():
    """Executa sincronização inteligente baseada na necessidade"""
    logger.info("🧠 SINCRONIZAÇÃO INTELIGENTE")
    logger.info("=" * 50)
    
    try:
        # Inicializar componentes
        sync_manager = IncrementalSyncManager(use_redis=True)
        scheduler = ScheduledSyncRunner(sync_manager)
        
        # Verificar status atual
        status = sync_manager.get_sync_status()
        
        logger.info("📊 Status atual das sincronizações:")
        for sync_type, health in status['sync_health'].items():
            needs_sync = "✅ NECESSÁRIA" if health['needs_sync'] else "⏭️ OK"
            logger.info(f"  • {sync_type}: {needs_sync} - {health['reason']}")
        
        # Executar apenas sincronizações necessárias
        results = scheduler.run_scheduled_syncs()
        
        if results:
            logger.info(f"📊 {len(results)} sincronizações executadas")
            for sync_type, result in results.items():
                success = "✅" if result.get('success', False) else "❌"
                logger.info(f"  {success} {sync_type}")
        else:
            logger.info("⏭️ Nenhuma sincronização necessária no momento")
        
        return len(results) > 0
        
    except Exception as e:
        logger.error(f"❌ Erro durante sincronização inteligente: {e}")
        return False

def main():
    """Função principal com opções de execução"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de Sincronização Incremental")
    parser.add_argument('--mode', choices=['once', 'continuous', 'smart'], 
                       default='once', help='Modo de execução')
    parser.add_argument('--force', action='store_true', 
                       help='Forçar sincronização mesmo se não necessária')
    
    args = parser.parse_args()
    
    print(f"🚀 SISTEMA DE SINCRONIZAÇÃO INCREMENTAL")
    print(f"📋 Modo: {args.mode.upper()}")
    print("=" * 50)
    
    try:
        if args.mode == 'once':
            # Execução única
            success = run_daily_sync_once()
        elif args.mode == 'continuous':
            # Execução contínua
            run_continuous_sync()
            success = True
        elif args.mode == 'smart':
            # Execução inteligente
            success = run_smart_sync()
        else:
            logger.error(f"❌ Modo inválido: {args.mode}")
            return False
        
        if success:
            print("\n🎉 SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!")
        else:
            print("\n⚠️ SINCRONIZAÇÃO CONCLUÍDA COM PROBLEMAS")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        print(f"❌ Erro fatal: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {str(e)}")
        sys.exit(1)
