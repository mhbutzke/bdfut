#!/usr/bin/env python3
"""
Script otimizado para enriquecimento de MATCH_LINEUPS
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

class LineupsEnrichment:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 100
        self.request_delay = 1
        
        # Contadores
        self.total_processed = 0
        self.total_lineups = 0
        self.total_errors = 0
        self.start_time = None
        
    def get_fixtures_without_lineups(self, limit: int = None):
        """Buscar fixtures finalizadas que não possuem lineups"""
        try:
            # Buscar fixtures finalizadas
            response = self.supabase.client.from_('fixtures').select(
                'fixture_id, match_date, home_team_name, away_team_name, status'
            ).in_('status', ['FT', 'FT_PEN', 'AET']).order('match_date', desc=True)
            
            if limit:
                response = response.limit(limit)
            
            result = response.execute()
            
            if result.data:
                # Filtrar fixtures que não têm lineups
                fixtures_without_lineups = []
                for fixture in result.data:
                    fixture_id = fixture['fixture_id']
                    
                    # Verificar se já tem lineups
                    lineups_check = self.supabase.client.table('match_lineups').select('id').eq('fixture_id', fixture_id).limit(1).execute()
                    
                    if len(lineups_check.data) == 0:
                        fixtures_without_lineups.append(fixture)
                
                return fixtures_without_lineups
            
            return []
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures sem lineups: {e}")
            return []
    
    def map_lineup_data(self, lineup: dict, fixture_id: int, index: int) -> dict:
        """Mapear dados do lineup da API para estrutura do banco"""
        # Determinar tipo baseado no type_id
        lineup_type = "lineup" if lineup.get('type_id') == 11 else "substitute"
        
        return {
            'id': f"{fixture_id}_{lineup.get('id', index)}",
            'fixture_id': fixture_id,
            'team_id': lineup.get('team_id'),
            'player_id': lineup.get('player_id'),
            'player_name': lineup.get('player_name'),
            'type': lineup_type,
            'position_id': lineup.get('position_id'),
            'jersey_number': lineup.get('jersey_number'),
            'formation_position': lineup.get('formation_position'),
            'created_at': datetime.now().isoformat()
        }
    
    def enrich_fixture_lineups(self, fixture):
        """Enriquecer uma fixture com lineups"""
        try:
            fixture_id = fixture['fixture_id']
            
            logger.info(f"🔍 Processando fixture {fixture_id} ({fixture['home_team_name']} vs {fixture['away_team_name']})")
            
            # Buscar lineups da API
            lineups = self.sportmonks.get_lineups_by_fixture(fixture_id)
            
            if not lineups:
                logger.info(f"   📭 Nenhum lineup encontrado na API")
                return {'status': 'no_lineups', 'count': 0}
            
            logger.info(f"   📊 {len(lineups)} lineups encontrados na API")
            
            # Mapear dados para inserção
            lineups_data = []
            for i, lineup in enumerate(lineups):
                lineup_data = self.map_lineup_data(lineup, fixture_id, i)
                lineups_data.append(lineup_data)
            
            # Inserir lineups no Supabase
            if lineups_data:
                response = self.supabase.client.table('match_lineups').upsert(lineups_data, on_conflict='id').execute()
                
                if response.data:
                    logger.info(f"   ✅ {len(response.data)} lineups inseridos/atualizados")
                    return {'status': 'success', 'count': len(response.data)}
                else:
                    logger.warning(f"   ⚠️ Nenhum lineup inserido, resposta vazia")
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
            logger.info(f"👥 Lineups inseridos: {self.total_lineups:,}")
            logger.info(f"❌ Erros: {self.total_errors:,}")
    
    def run_enrichment(self, limit: int = None):
        """Executar enriquecimento de lineups"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO DE LINEUPS")
        logger.info("=" * 50)
        
        self.start_time = time.time()
        
        # Buscar fixtures para enriquecer
        fixtures = self.get_fixtures_without_lineups(limit)
        
        if not fixtures:
            logger.warning("⚠️ Nenhuma fixture encontrada para enriquecimento")
            return
        
        logger.info(f"📊 {len(fixtures):,} fixtures encontradas para processamento")
        
        # Processar fixtures
        for i, fixture in enumerate(fixtures):
            try:
                result = self.enrich_fixture_lineups(fixture)
                
                if result['status'] == 'success':
                    self.total_processed += 1
                    self.total_lineups += result['count']
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
        logger.info("\\n🎉 ENRIQUECIMENTO DE LINEUPS CONCLUÍDO!")
        logger.info("=" * 50)
        logger.info(f"⏱️ Tempo total: {total_time/60:.1f} minutos")
        logger.info(f"📊 Fixtures processadas: {self.total_processed:,}")
        logger.info(f"👥 Lineups inseridos: {self.total_lineups:,}")
        logger.info(f"❌ Erros encontrados: {self.total_errors:,}")
        logger.info(f"🚀 Taxa média: {self.total_processed/(total_time/60):.1f} fixtures/minuto")

def main():
    """Função principal"""
    enrichment = LineupsEnrichment()
    
    # Testar com 100 fixtures primeiro
    enrichment.run_enrichment(limit=100)

if __name__ == "__main__":
    main()
