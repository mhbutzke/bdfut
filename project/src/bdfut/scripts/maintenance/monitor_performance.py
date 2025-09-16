#!/usr/bin/env python3
"""
Script de Monitoramento de Performance - TASK-DB-003
Agente: Database Specialist 🗄️
Data: 2025-01-13

Monitora performance dos índices e queries após otimizações.
"""

import os
import sys
import logging
import time
from datetime import datetime
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
        logging.FileHandler(f'logs/monitor_performance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor de performance do banco de dados."""
    
    def __init__(self):
        """Inicializar cliente Supabase."""
        try:
            self.config = Config()
            self.supabase = SupabaseClient(self.config)
            logger.info("✅ Cliente Supabase inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
            raise
    
    def analyze_index_usage(self):
        """Analisar uso dos índices após otimizações."""
        logger.info("🔍 Analisando uso dos índices otimizados...")
        
        try:
            result = self.supabase.execute_sql("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_tup_read,
                    idx_tup_fetch,
                    CASE 
                        WHEN idx_tup_read = 0 THEN 'NUNCA USADO'
                        WHEN idx_tup_fetch = 0 THEN 'NUNCA RETORNOU DADOS'
                        ELSE 'ATIVO'
                    END as status_uso,
                    CASE 
                        WHEN idx_tup_read > 0 THEN ROUND((idx_tup_fetch::numeric / idx_tup_read::numeric) * 100, 2)
                        ELSE 0
                    END as eficiencia_percentual
                FROM pg_stat_user_indexes 
                WHERE schemaname = 'public'
                AND indexname LIKE 'idx_%'
                ORDER BY idx_tup_read DESC;
            """)
            
            logger.info(f"📊 {len(result)} índices analisados")
            
            # Categorizar índices
            ativos = [idx for idx in result if idx['status_uso'] == 'ATIVO']
            nao_utilizados = [idx for idx in result if idx['status_uso'] == 'NUNCA USADO']
            baixa_eficiencia = [idx for idx in result if idx['eficiencia_percentual'] < 50 and idx['status_uso'] == 'ATIVO']
            
            logger.info(f"✅ Índices ativos: {len(ativos)}")
            logger.info(f"⚠️ Índices não utilizados: {len(nao_utilizados)}")
            logger.info(f"🔴 Índices com baixa eficiência: {len(baixa_eficiencia)}")
            
            # Mostrar top 10 mais utilizados
            logger.info("🏆 Top 10 índices mais utilizados:")
            for i, idx in enumerate(result[:10], 1):
                logger.info(f"  {i}. {idx['indexname']} - {idx['idx_tup_read']} leituras ({idx['eficiencia_percentual']}% eficiência)")
            
            return {
                'total_indices': len(result),
                'ativos': len(ativos),
                'nao_utilizados': len(nao_utilizados),
                'baixa_eficiencia': len(baixa_eficiencia)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar índices: {e}")
            return None
    
    def test_query_performance(self):
        """Testar performance de queries críticas."""
        logger.info("⚡ Testando performance de queries críticas...")
        
        queries = [
            {
                'name': 'Fixtures por temporada e data',
                'sql': """
                    SELECT f.*, h.name as home_team, a.name as away_team 
                    FROM fixtures f
                    JOIN teams h ON f.home_team_id = h.sportmonks_id
                    JOIN teams a ON f.away_team_id = a.sportmonks_id
                    WHERE f.season_id = 20534
                    ORDER BY f.match_date DESC
                    LIMIT 100;
                """
            },
            {
                'name': 'Eventos por fixture e tipo',
                'sql': """
                    SELECT me.*, f.match_date, h.name as home_team, a.name as away_team
                    FROM match_events me
                    JOIN fixtures f ON me.fixture_id = f.sportmonks_id
                    JOIN teams h ON f.home_team_id = h.sportmonks_id
                    JOIN teams a ON f.away_team_id = a.sportmonks_id
                    WHERE me.event_type = 'goal'
                    ORDER BY f.match_date DESC
                    LIMIT 50;
                """
            },
            {
                'name': 'Estatísticas por fixture',
                'sql': """
                    SELECT ms.*, f.match_date, t.name as team_name
                    FROM match_statistics ms
                    JOIN fixtures f ON ms.fixture_id = f.sportmonks_id
                    JOIN teams t ON ms.team_id = t.sportmonks_id
                    WHERE ms.shots_total > 10
                    ORDER BY f.match_date DESC
                    LIMIT 50;
                """
            },
            {
                'name': 'Lineups por fixture',
                'sql': """
                    SELECT ml.*, f.match_date, t.name as team_name, p.name as player_name
                    FROM match_lineups ml
                    JOIN fixtures f ON ml.fixture_id = f.sportmonks_id
                    JOIN teams t ON ml.team_id = t.sportmonks_id
                    LEFT JOIN players p ON ml.player_id = p.sportmonks_id
                    WHERE ml.minutes_played > 60
                    ORDER BY f.match_date DESC
                    LIMIT 50;
                """
            }
        ]
        
        results = []
        
        for query in queries:
            try:
                start_time = time.time()
                result = self.supabase.execute_sql(query['sql'])
                end_time = time.time()
                
                execution_time = (end_time - start_time) * 1000  # em ms
                rows_returned = len(result) if result else 0
                
                logger.info(f"✅ {query['name']}: {execution_time:.2f}ms ({rows_returned} rows)")
                
                results.append({
                    'name': query['name'],
                    'execution_time_ms': execution_time,
                    'rows_returned': rows_returned,
                    'status': 'SUCCESS'
                })
                
            except Exception as e:
                logger.error(f"❌ {query['name']}: Erro - {e}")
                results.append({
                    'name': query['name'],
                    'execution_time_ms': 0,
                    'rows_returned': 0,
                    'status': 'ERROR',
                    'error': str(e)
                })
        
        return results
    
    def analyze_table_sizes(self):
        """Analisar tamanhos das tabelas."""
        logger.info("📏 Analisando tamanhos das tabelas...")
        
        try:
            result = self.supabase.execute_sql("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """)
            
            logger.info(f"📊 {len(result)} tabelas analisadas")
            
            # Mostrar top 10 maiores tabelas
            logger.info("🏆 Top 10 maiores tabelas:")
            for i, table in enumerate(result[:10], 1):
                logger.info(f"  {i}. {table['tablename']} - {table['size']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar tamanhos: {e}")
            return None
    
    def generate_performance_report(self):
        """Gerar relatório completo de performance."""
        logger.info("📋 Gerando relatório completo de performance...")
        
        # Coletar métricas
        index_analysis = self.analyze_index_usage()
        query_performance = self.test_query_performance()
        table_sizes = self.analyze_table_sizes()
        
        # Calcular métricas de sucesso
        successful_queries = [q for q in query_performance if q['status'] == 'SUCCESS']
        avg_query_time = sum(q['execution_time_ms'] for q in successful_queries) / len(successful_queries) if successful_queries else 0
        
        # Verificar se metas foram atingidas
        queries_under_100ms = [q for q in successful_queries if q['execution_time_ms'] < 100]
        index_usage_rate = (index_analysis['ativos'] / index_analysis['total_indices'] * 100) if index_analysis else 0
        
        logger.info("🎯 RESUMO DE PERFORMANCE:")
        logger.info(f"  📊 Queries executadas: {len(successful_queries)}/{len(query_performance)}")
        logger.info(f"  ⚡ Tempo médio de query: {avg_query_time:.2f}ms")
        logger.info(f"  🎯 Queries < 100ms: {len(queries_under_100ms)}/{len(successful_queries)}")
        logger.info(f"  📈 Uso de índices: {index_usage_rate:.1f}%")
        
        # Verificar metas
        if avg_query_time < 100:
            logger.info("✅ META ATINGIDA: Tempo médio de query < 100ms")
        else:
            logger.warning(f"⚠️ META NÃO ATINGIDA: Tempo médio de query {avg_query_time:.2f}ms > 100ms")
        
        if index_usage_rate > 80:
            logger.info("✅ META ATINGIDA: Uso de índices > 80%")
        else:
            logger.warning(f"⚠️ META NÃO ATINGIDA: Uso de índices {index_usage_rate:.1f}% < 80%")
        
        return {
            'index_analysis': index_analysis,
            'query_performance': query_performance,
            'table_sizes': table_sizes,
            'avg_query_time_ms': avg_query_time,
            'queries_under_100ms': len(queries_under_100ms),
            'index_usage_rate': index_usage_rate,
            'success_rate': len(successful_queries) / len(query_performance) * 100 if query_performance else 0
        }

def main():
    """Função principal."""
    try:
        monitor = PerformanceMonitor()
        report = monitor.generate_performance_report()
        
        print("✅ Monitoramento de performance concluído!")
        print(f"📊 Relatório salvo em: logs/monitor_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # Verificar se todas as metas foram atingidas
        if (report['avg_query_time_ms'] < 100 and 
            report['index_usage_rate'] > 80 and 
            report['success_rate'] > 90):
            print("🎉 TODAS AS METAS DE PERFORMANCE FORAM ATINGIDAS!")
            sys.exit(0)
        else:
            print("⚠️ Algumas metas de performance não foram atingidas. Verifique os logs.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Erro durante monitoramento: {e}")
        print(f"❌ Erro durante monitoramento: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
