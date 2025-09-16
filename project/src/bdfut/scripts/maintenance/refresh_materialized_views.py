#!/usr/bin/env python3
"""
Script de Refresh de Materialized Views - TASK-DB-004
Agente: Database Specialist 🗄️
Data: 2025-01-13

Configura e executa refresh automático das materialized views.
"""

import os
import sys
import logging
import schedule
import time
from datetime import datetime, timedelta
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
        logging.FileHandler(f'logs/refresh_views_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MaterializedViewManager:
    """Gerenciador de Materialized Views."""
    
    def __init__(self):
        """Inicializar cliente Supabase."""
        try:
            self.config = Config()
            self.supabase = SupabaseClient(self.config)
            logger.info("✅ Cliente Supabase inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
            raise
    
    def refresh_all_views(self):
        """Refresh de todas as materialized views."""
        logger.info("🔄 Iniciando refresh de todas as materialized views...")
        
        views = [
            'player_season_stats',
            'team_season_stats', 
            'fixture_timeline_expanded',
            'league_season_summary'
        ]
        
        results = []
        
        for view in views:
            try:
                start_time = datetime.now()
                logger.info(f"🔄 Refreshing {view}...")
                
                # Executar refresh
                self.supabase.execute_sql(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view};")
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                logger.info(f"✅ {view} refreshed em {duration:.2f}s")
                
                results.append({
                    'view': view,
                    'status': 'SUCCESS',
                    'duration_seconds': duration,
                    'timestamp': start_time
                })
                
            except Exception as e:
                logger.error(f"❌ Erro ao refresh {view}: {e}")
                results.append({
                    'view': view,
                    'status': 'ERROR',
                    'error': str(e),
                    'timestamp': datetime.now()
                })
        
        # Log do refresh completo
        self.log_refresh_operation(results)
        
        return results
    
    def refresh_single_view(self, view_name):
        """Refresh de uma materialized view específica."""
        logger.info(f"🔄 Refreshing {view_name}...")
        
        try:
            start_time = datetime.now()
            self.supabase.execute_sql(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view_name};")
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ {view_name} refreshed em {duration:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao refresh {view_name}: {e}")
            return False
    
    def log_refresh_operation(self, results):
        """Log da operação de refresh."""
        try:
            successful = [r for r in results if r['status'] == 'SUCCESS']
            failed = [r for r in results if r['status'] == 'ERROR']
            
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'total_views': len(results),
                'successful': len(successful),
                'failed': len(failed),
                'results': results
            }
            
            # Salvar log no cache
            cache_key = f"materialized_views_refresh_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.supabase.execute_sql(f"""
                INSERT INTO api_cache (cache_key, data, expires_at) 
                VALUES ('{cache_key}', '{str(log_data).replace("'", "''")}', 
                        '{datetime.now() + timedelta(days=7)}');
            """)
            
            logger.info(f"📊 Refresh completo: {len(successful)}/{len(results)} views atualizadas")
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao salvar log: {e}")
    
    def get_view_statistics(self):
        """Obter estatísticas das materialized views."""
        logger.info("📊 Coletando estatísticas das materialized views...")
        
        try:
            result = self.supabase.execute_sql("""
                SELECT 
                    schemaname,
                    matviewname as view_name,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size,
                    pg_total_relation_size(schemaname||'.'||matviewname) as size_bytes
                FROM pg_matviews 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||matviewname) DESC;
            """)
            
            logger.info(f"📊 {len(result)} materialized views encontradas")
            
            for view in result:
                logger.info(f"  📋 {view['view_name']} - {view['size']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar estatísticas: {e}")
            return None
    
    def check_view_freshness(self):
        """Verificar frescor das materialized views."""
        logger.info("🔍 Verificando frescor das materialized views...")
        
        try:
            result = self.supabase.execute_sql("""
                SELECT 
                    schemaname,
                    matviewname as view_name,
                    pg_stat_get_last_analyze_time(oid) as last_analyze,
                    pg_stat_get_last_autoanalyze_time(oid) as last_autoanalyze
                FROM pg_matviews 
                JOIN pg_class ON pg_class.relname = pg_matviews.matviewname
                WHERE schemaname = 'public';
            """)
            
            logger.info(f"🔍 {len(result)} views analisadas")
            
            for view in result:
                logger.info(f"  📋 {view['view_name']} - Última análise: {view['last_analyze']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar frescor: {e}")
            return None
    
    def setup_automatic_refresh(self):
        """Configurar refresh automático."""
        logger.info("⏰ Configurando refresh automático das materialized views...")
        
        try:
            # Criar função de refresh se não existir
            self.supabase.execute_sql("""
                CREATE OR REPLACE FUNCTION refresh_materialized_views()
                RETURNS void AS $$
                BEGIN
                    REFRESH MATERIALIZED VIEW CONCURRENTLY player_season_stats;
                    REFRESH MATERIALIZED VIEW CONCURRENTLY team_season_stats;
                    REFRESH MATERIALIZED VIEW CONCURRENTLY fixture_timeline_expanded;
                    REFRESH MATERIALIZED VIEW CONCURRENTLY league_season_summary;
                END;
                $$ LANGUAGE plpgsql;
            """)
            
            logger.info("✅ Função de refresh automático criada")
            
            # Configurar schedule para refresh diário às 2h da manhã
            schedule.every().day.at("02:00").do(self.refresh_all_views)
            logger.info("⏰ Refresh automático configurado para 02:00 diariamente")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar refresh automático: {e}")
            return False
    
    def run_scheduler(self):
        """Executar scheduler de refresh automático."""
        logger.info("🚀 Iniciando scheduler de refresh automático...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
            except KeyboardInterrupt:
                logger.info("⏹️ Scheduler interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no scheduler: {e}")
                time.sleep(60)

def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciador de Materialized Views')
    parser.add_argument('--refresh-all', action='store_true', help='Refresh todas as views')
    parser.add_argument('--refresh-view', type=str, help='Refresh uma view específica')
    parser.add_argument('--stats', action='store_true', help='Mostrar estatísticas das views')
    parser.add_argument('--freshness', action='store_true', help='Verificar frescor das views')
    parser.add_argument('--setup-auto', action='store_true', help='Configurar refresh automático')
    parser.add_argument('--run-scheduler', action='store_true', help='Executar scheduler')
    
    args = parser.parse_args()
    
    try:
        manager = MaterializedViewManager()
        
        if args.refresh_all:
            results = manager.refresh_all_views()
            successful = len([r for r in results if r['status'] == 'SUCCESS'])
            print(f"✅ Refresh completo: {successful}/{len(results)} views atualizadas")
            
        elif args.refresh_view:
            success = manager.refresh_single_view(args.refresh_view)
            if success:
                print(f"✅ {args.refresh_view} refreshed com sucesso")
            else:
                print(f"❌ Erro ao refresh {args.refresh_view}")
                
        elif args.stats:
            stats = manager.get_view_statistics()
            if stats:
                print("📊 Estatísticas das Materialized Views:")
                for stat in stats:
                    print(f"  📋 {stat['view_name']} - {stat['size']}")
                    
        elif args.freshness:
            freshness = manager.check_view_freshness()
            if freshness:
                print("🔍 Frescor das Materialized Views:")
                for view in freshness:
                    print(f"  📋 {view['view_name']} - Última análise: {view['last_analyze']}")
                    
        elif args.setup_auto:
            success = manager.setup_automatic_refresh()
            if success:
                print("✅ Refresh automático configurado com sucesso")
            else:
                print("❌ Erro ao configurar refresh automático")
                
        elif args.run_scheduler:
            print("🚀 Executando scheduler de refresh automático...")
            manager.run_scheduler()
            
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {e}")
        print(f"❌ Erro durante execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
