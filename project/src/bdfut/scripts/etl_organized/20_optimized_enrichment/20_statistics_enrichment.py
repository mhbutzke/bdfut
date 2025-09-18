#!/usr/bin/env python3
"""
Script otimizado para enriquecimento de MATCH_STATISTICS
Baseado no planejamento detalhado e mapeamento correto da API
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import time
import logging

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StatisticsEnrichment:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 100
        self.request_delay = 1
        
        # Contadores
        self.total_processed = 0
        self.total_statistics = 0
        self.total_errors = 0
        self.start_time = None
        
        # Mapeamento de type_id para campos específicos
        self.statistics_mapping = {
            41: 'shots_total',
            42: 'shots_on_target',
            43: 'shots_inside_box',
            44: 'shots_outside_box',
            45: 'blocked_shots',
            46: 'corners',
            47: 'ball_possession',
            48: 'yellow_cards',
            49: 'red_cards',
            50: 'passes_total',
            51: 'passes_accurate',
            52: 'pass_percentage',
            53: 'saves',
            54: 'interceptions'
        }
        
    def get_fixtures_without_statistics(self, limit: int = None):
        """Buscar fixtures finalizadas que não possuem estatísticas"""
        try:
            # Buscar fixtures finalizadas
            response = self.supabase.client.from_('fixtures').select(
                'fixture_id, match_date, home_team_name, away_team_name, status'
            ).in_('status', ['FT', 'FT_PEN', 'AET']).order('match_date', desc=True)
            
            if limit:
                response = response.limit(limit)
            
            result = response.execute()
            
            if result.data:
                # Filtrar fixtures que não têm estatísticas
                fixtures_without_stats = []
                for fixture in result.data:
                    fixture_id = fixture['fixture_id']
                    
                    # Verificar se já tem estatísticas
                    stats_check = self.supabase.client.table('match_statistics').select('id').eq('fixture_id', fixture_id).limit(1).execute()
                    
                    if len(stats_check.data) == 0:
                        fixtures_without_stats.append(fixture)
                
                return fixtures_without_stats
            
            return []
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures sem estatísticas: {e}")
            return []
    
    def map_statistics_data(self, statistics: list, fixture_id: int) -> list:
        """Mapear estatísticas da API para estrutura do banco"""
        # Agrupar estatísticas por team_id
        stats_by_team = {}
        
        for stat in statistics:
            team_id = stat.get('participant_id')
            if team_id not in stats_by_team:
                stats_by_team[team_id] = {}
            
            type_id = stat.get('type_id')
            data_value = stat.get('data', {}).get('value', 0)
            
            # Mapear type_id para campo específico
            if type_id in self.statistics_mapping:
                field_name = self.statistics_mapping[type_id]
                stats_by_team[team_id][field_name] = data_value
        
        # Criar registros de estatísticas agrupadas
        stats_data = []
        for team_id, team_stats in stats_by_team.items():
            stat_data = {
                'id': f"{fixture_id}_{team_id}",
                'fixture_id': fixture_id,
                'team_id': team_id,
                'created_at': datetime.now().isoformat()
            }
            
            # Adicionar todas as estatísticas disponíveis
            stat_data.update(team_stats)
            stats_data.append(stat_data)
        
        return stats_data
    
    def enrich_fixture_statistics(self, fixture):
        """Enriquecer uma fixture com estatísticas"""
        try:
            fixture_id = fixture['fixture_id']
            
            logger.info(f"🔍 Processando fixture {fixture_id} ({fixture['home_team_name']} vs {fixture['away_team_name']})")
            
            # Buscar estatísticas da API
            statistics = self.sportmonks.get_statistics_by_fixture(fixture_id)
            
            if not statistics:
                logger.info(f"   📭 Nenhuma estatística encontrada na API")
                return {'status': 'no_statistics', 'count': 0}
            
            logger.info(f"   📊 {len(statistics)} estatísticas encontradas na API")
            
            # Mapear dados para inserção
            stats_data = self.map_statistics_data(statistics, fixture_id)
            
            # Inserir estatísticas no Supabase
            if stats_data:
                response = self.supabase.client.table('match_statistics').upsert(stats_data, on_conflict='id').execute()
                
                if response.data:
                    logger.info(f"   ✅ {len(response.data)} estatísticas inseridas/atualizadas")
                    return {'status': 'success', 'count': len(response.data)}
                else:
                    logger.warning(f"   ⚠️ Nenhuma estatística inserida, resposta vazia")
                    return {'status': 'no_insert', 'count': 0}
            
            return {'status': 'no_data', 'count': 0}
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer fixture {fixture_id}: {e}")
            return {'status': 'error', 'count': 0, 'error': str(e)}
    
    def print_progress_report(self, current: int, total: int):
        """Imprimir relatório de progresso"""
        if current % 50 == 0 or current == total:
            elapsed = time.time() - self.start_time
            rate = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / rate if rate > 0 else 0
            
            logger.info(f"\\n📊 PROGRESSO: {current:,}/{total:,} ({current/total*100:.1f}%)")
            logger.info(f"⏱️ Tempo decorrido: {elapsed/60:.1f} minutos")
            logger.info(f"🚀 Taxa: {rate:.1f} fixtures/minuto")
            logger.info(f"⏳ ETA: {eta/60:.1f} minutos")
            logger.info(f"📈 Estatísticas inseridas: {self.total_statistics:,}")
            logger.info(f"❌ Erros: {self.total_errors:,}")
    
    def run_enrichment(self, limit: int = None):
        """Executar enriquecimento de estatísticas"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO DE ESTATÍSTICAS")
        logger.info("=" * 50)
        
        self.start_time = time.time()
        
        # Buscar fixtures para enriquecer
        fixtures = self.get_fixtures_without_statistics(limit)
        
        if not fixtures:
            logger.warning("⚠️ Nenhuma fixture encontrada para enriquecimento")
            return
        
        logger.info(f"📊 {len(fixtures):,} fixtures encontradas para processamento")
        
        # Processar fixtures
        for i, fixture in enumerate(fixtures):
            try:
                result = self.enrich_fixture_statistics(fixture)
                
                if result['status'] == 'success':
                    self.total_processed += 1
                    self.total_statistics += result['count']
                elif result['status'] == 'error':
                    self.total_errors += 1
                
                # Delay entre requisições
                time.sleep(self.request_delay)
                
                # Relatório de progresso
                self.print_progress_report(i + 1, len(fixtures))
                
            except Exception as e:
                logger.error(f"❌ Erro crítico ao processar fixture {fixture['fixture_id']}: {e}")
                self.total_errors += 1
        
        # Relatório final
        total_time = time.time() - self.start_time
        logger.info("\\n🎉 ENRIQUECIMENTO DE ESTATÍSTICAS CONCLUÍDO!")
        logger.info("=" * 50)
        logger.info(f"⏱️ Tempo total: {total_time/60:.1f} minutos")
        logger.info(f"📊 Fixtures processadas: {self.total_processed:,}")
        logger.info(f"📈 Estatísticas inseridas: {self.total_statistics:,}")
        logger.info(f"❌ Erros encontrados: {self.total_errors:,}")
        logger.info(f"🚀 Taxa média: {self.total_processed/(total_time/60):.1f} fixtures/minuto")

def main():
    """Função principal"""
    enrichment = StatisticsEnrichment()
    
    # Testar com 100 fixtures primeiro
    enrichment.run_enrichment(limit=100)

if __name__ == "__main__":
    main()
