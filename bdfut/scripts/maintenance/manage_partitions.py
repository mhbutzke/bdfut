#!/usr/bin/env python3
"""
Script de Gerenciamento de Partições - TASK-DB-005
Agente: Database Specialist 🗄️
Data: 2025-01-13

Gerencia partições automaticamente, criando novas e removendo antigas.
"""

import os
import sys
import logging
import schedule
import time
from datetime import datetime, timedelta, date
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
        logging.FileHandler(f'logs/manage_partitions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PartitionManager:
    """Gerenciador de partições."""
    
    def __init__(self):
        """Inicializar cliente Supabase."""
        try:
            self.config = Config()
            self.supabase = SupabaseClient(self.config)
            logger.info("✅ Cliente Supabase inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
            raise
    
    def list_partitions(self):
        """Listar todas as partições existentes."""
        logger.info("📋 Listando partições existentes...")
        
        try:
            result = self.supabase.execute_sql("""
                SELECT 
                    schemaname,
                    tablename as partition_name,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND (tablename LIKE 'fixtures_20%' OR tablename = 'fixtures_default')
                ORDER BY tablename;
            """)
            
            logger.info(f"📊 {len(result)} partições encontradas:")
            for partition in result:
                logger.info(f"  📋 {partition['partition_name']} - {partition['size']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar partições: {e}")
            return []
    
    def get_partition_statistics(self):
        """Obter estatísticas das partições."""
        logger.info("📊 Coletando estatísticas das partições...")
        
        try:
            result = self.supabase.execute_sql("""
                SELECT 
                    schemaname,
                    tablename as partition_name,
                    n_tup_ins as total_inserts,
                    n_tup_upd as total_updates,
                    n_tup_del as total_deletes,
                    n_live_tup as live_rows,
                    n_dead_tup as dead_rows,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_stat_user_tables 
                WHERE schemaname = 'public' 
                AND (relname LIKE 'fixtures_20%' OR relname = 'fixtures_default')
                ORDER BY relname;
            """)
            
            logger.info(f"📊 Estatísticas de {len(result)} partições:")
            for stat in result:
                logger.info(f"  📋 {stat['partition_name']}: {stat['live_rows']} registros, {stat['size']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar estatísticas: {e}")
            return []
    
    def create_future_partitions(self, months_ahead=6):
        """Criar partições para os próximos meses."""
        logger.info(f"🔮 Criando partições para os próximos {months_ahead} meses...")
        
        created_partitions = []
        
        for i in range(months_ahead):
            try:
                target_date = date.today() + timedelta(days=30 * i)
                
                logger.info(f"🔄 Criando partição para {target_date.strftime('%Y-%m')}...")
                
                # Executar função de criação de partição
                self.supabase.execute_sql(f"SELECT create_monthly_partition('{target_date}');")
                
                partition_name = f"fixtures_{target_date.strftime('%Y_%m')}"
                created_partitions.append(partition_name)
                
                logger.info(f"✅ Partição {partition_name} criada com sucesso")
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao criar partição para {target_date}: {e}")
        
        logger.info(f"🎉 {len(created_partitions)} partições criadas: {created_partitions}")
        return created_partitions
    
    def cleanup_old_partitions(self, retention_months=24):
        """Limpar partições antigas."""
        logger.info(f"🧹 Limpando partições com mais de {retention_months} meses...")
        
        try:
            # Executar função de limpeza
            self.supabase.execute_sql(f"SELECT drop_old_partitions({retention_months});")
            
            logger.info("✅ Limpeza de partições antigas concluída")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar partições antigas: {e}")
            return False
    
    def analyze_partition_performance(self):
        """Analisar performance das partições."""
        logger.info("⚡ Analisando performance das partições...")
        
        try:
            # Testar query com partition pruning
            start_time = time.time()
            result = self.supabase.execute_sql("""
                EXPLAIN ANALYZE
                SELECT COUNT(*) 
                FROM fixtures 
                WHERE match_date >= '2025-01-01' AND match_date < '2025-02-01';
            """)
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000
            
            logger.info(f"⚡ Query com partition pruning executada em {execution_time:.2f}ms")
            
            # Verificar se partition pruning está funcionando
            plan_text = '\n'.join([row['QUERY PLAN'] for row in result])
            if 'Seq Scan on fixtures_2025' in plan_text:
                logger.info("✅ Partition pruning funcionando corretamente")
            else:
                logger.warning("⚠️ Partition pruning pode não estar otimizado")
            
            return {
                'execution_time_ms': execution_time,
                'partition_pruning_active': 'fixtures_2025' in plan_text,
                'query_plan': plan_text
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar performance: {e}")
            return None
    
    def validate_partition_constraints(self):
        """Validar constraints das partições."""
        logger.info("🔍 Validando constraints das partições...")
        
        try:
            # Verificar se todas as partições têm os índices necessários
            result = self.supabase.execute_sql("""
                SELECT 
                    t.tablename as partition_name,
                    COUNT(i.indexname) as index_count
                FROM pg_tables t
                LEFT JOIN pg_indexes i ON t.tablename = i.tablename
                WHERE t.schemaname = 'public' 
                AND t.tablename LIKE 'fixtures_20%'
                GROUP BY t.tablename
                ORDER BY t.tablename;
            """)
            
            issues = []
            for partition in result:
                if partition['index_count'] < 4:  # Esperamos pelo menos 4 índices por partição
                    issues.append(f"Partição {partition['partition_name']} tem apenas {partition['index_count']} índices")
            
            if issues:
                logger.warning(f"⚠️ {len(issues)} problemas encontrados:")
                for issue in issues:
                    logger.warning(f"  - {issue}")
            else:
                logger.info("✅ Todas as partições têm os índices necessários")
            
            return len(issues) == 0
            
        except Exception as e:
            logger.error(f"❌ Erro ao validar constraints: {e}")
            return False
    
    def setup_automatic_maintenance(self):
        """Configurar manutenção automática das partições."""
        logger.info("⏰ Configurando manutenção automática das partições...")
        
        try:
            # Configurar schedule para criar partições futuras mensalmente
            schedule.every().month.do(self.create_future_partitions, months_ahead=6)
            
            # Configurar schedule para limpeza trimestral
            schedule.every(3).months.do(self.cleanup_old_partitions, retention_months=24)
            
            logger.info("✅ Manutenção automática configurada:")
            logger.info("  📅 Criação de partições: Mensalmente")
            logger.info("  🧹 Limpeza de partições: Trimestralmente")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar manutenção automática: {e}")
            return False
    
    def run_maintenance_scheduler(self):
        """Executar scheduler de manutenção."""
        logger.info("🚀 Iniciando scheduler de manutenção de partições...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(3600)  # Verificar a cada hora
            except KeyboardInterrupt:
                logger.info("⏹️ Scheduler interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no scheduler: {e}")
                time.sleep(3600)
    
    def generate_partition_report(self):
        """Gerar relatório completo das partições."""
        logger.info("📋 Gerando relatório completo das partições...")
        
        # Coletar informações
        partitions = self.list_partitions()
        statistics = self.get_partition_statistics()
        performance = self.analyze_partition_performance()
        constraints_valid = self.validate_partition_constraints()
        
        # Calcular métricas
        total_size = sum(p['size_bytes'] for p in partitions if p['size_bytes'])
        total_rows = sum(s['live_rows'] for s in statistics if s['live_rows'])
        
        logger.info("📊 RESUMO DAS PARTIÇÕES:")
        logger.info(f"  📋 Total de partições: {len(partitions)}")
        logger.info(f"  💾 Tamanho total: {self._format_bytes(total_size)}")
        logger.info(f"  📊 Total de registros: {total_rows:,}")
        logger.info(f"  ⚡ Performance: {performance['execution_time_ms']:.2f}ms" if performance else "  ⚡ Performance: N/A")
        logger.info(f"  ✅ Constraints válidas: {'Sim' if constraints_valid else 'Não'}")
        
        return {
            'partitions': partitions,
            'statistics': statistics,
            'performance': performance,
            'constraints_valid': constraints_valid,
            'total_size_bytes': total_size,
            'total_rows': total_rows
        }
    
    def _format_bytes(self, bytes_value):
        """Formatar bytes em formato legível."""
        if not bytes_value:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"

def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciador de Partições')
    parser.add_argument('--list', action='store_true', help='Listar partições existentes')
    parser.add_argument('--stats', action='store_true', help='Mostrar estatísticas das partições')
    parser.add_argument('--create-future', type=int, default=6, help='Criar partições futuras (meses)')
    parser.add_argument('--cleanup', type=int, default=24, help='Limpar partições antigas (meses de retenção)')
    parser.add_argument('--analyze', action='store_true', help='Analisar performance das partições')
    parser.add_argument('--validate', action='store_true', help='Validar constraints das partições')
    parser.add_argument('--report', action='store_true', help='Gerar relatório completo')
    parser.add_argument('--setup-auto', action='store_true', help='Configurar manutenção automática')
    parser.add_argument('--run-scheduler', action='store_true', help='Executar scheduler de manutenção')
    
    args = parser.parse_args()
    
    try:
        manager = PartitionManager()
        
        if args.list:
            partitions = manager.list_partitions()
            print(f"📋 {len(partitions)} partições encontradas")
            
        elif args.stats:
            stats = manager.get_partition_statistics()
            print(f"📊 Estatísticas de {len(stats)} partições coletadas")
            
        elif args.create_future:
            created = manager.create_future_partitions(args.create_future)
            print(f"🔮 {len(created)} partições futuras criadas")
            
        elif args.cleanup:
            success = manager.cleanup_old_partitions(args.cleanup)
            if success:
                print("🧹 Limpeza de partições antigas concluída")
            else:
                print("❌ Erro na limpeza de partições antigas")
                
        elif args.analyze:
            performance = manager.analyze_partition_performance()
            if performance:
                print(f"⚡ Performance analisada: {performance['execution_time_ms']:.2f}ms")
            else:
                print("❌ Erro na análise de performance")
                
        elif args.validate:
            valid = manager.validate_partition_constraints()
            if valid:
                print("✅ Todas as constraints das partições são válidas")
            else:
                print("⚠️ Algumas constraints das partições precisam de atenção")
                
        elif args.report:
            report = manager.generate_partition_report()
            print("📋 Relatório completo das partições gerado")
            
        elif args.setup_auto:
            success = manager.setup_automatic_maintenance()
            if success:
                print("✅ Manutenção automática configurada")
            else:
                print("❌ Erro ao configurar manutenção automática")
                
        elif args.run_scheduler:
            print("🚀 Executando scheduler de manutenção...")
            manager.run_maintenance_scheduler()
            
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {e}")
        print(f"❌ Erro durante execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
