#!/usr/bin/env python3
"""
Task 2.8 - Coleta Massiva de Referees (Todas as Fixtures)
==========================================================

Objetivo: Coletar referee IDs (type=6) para TODAS as fixtures sem referee
Situação atual: 0.05% de cobertura (31/67.085 fixtures)
Meta: Processar todas as 67.054 fixtures sem referee
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

import requests
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional
from bdfut.core.supabase_client import SupabaseClient
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RefereeMassCollector:
    def __init__(self):
        Config.validate()
        self.api_key = Config.SPORTMONKS_API_KEY
        self.base_url = Config.SPORTMONKS_BASE_URL
        self.supabase = SupabaseClient()
        self.batch_size = 10  # Limite da API multi
        self.delay_between_batches = 1.0  # Respeitar rate limits
        
    def get_fixtures_without_referee(self, limit: int = None) -> List[Dict]:
        """Buscar fixtures sem referee"""
        logger.info("🔍 Buscando fixtures sem referee...")
        
        query = self.supabase.client.table('fixtures').select('id,sportmonks_id')
        query = query.or_('referee.is.null,referee.eq.')
        
        if limit:
            query = query.limit(limit)
            
        result = query.execute()
        fixtures = result.data
        
        logger.info(f"📋 Encontradas {len(fixtures)} fixtures sem referee")
        return fixtures
    
    def fetch_referees_batch(self, fixture_ids: List[str]) -> Dict:
        """Buscar referees para um lote de fixtures via API multi"""
        fixture_ids_str = ','.join(fixture_ids)
        
        url = f'{self.base_url}/fixtures/multi/{fixture_ids_str}'
        params = {
            'api_token': self.api_key,
            'include': 'referees'
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na API para lote {fixture_ids_str}: {e}")
            return []
    
    def process_referees_batch(self, fixtures_batch: List[Dict]) -> int:
        """Processar um lote de fixtures e extrair referee IDs"""
        sportmonks_ids = [str(f['sportmonks_id']) for f in fixtures_batch]
        
        # Buscar dados da API
        api_fixtures = self.fetch_referees_batch(sportmonks_ids)
        
        if not api_fixtures:
            return 0
        
        # Criar mapeamento sportmonks_id -> db_id
        id_mapping = {f['sportmonks_id']: f['id'] for f in fixtures_batch}
        
        updates_count = 0
        
        for api_fixture in api_fixtures:
            sportmonks_id = api_fixture.get('id')
            referees = api_fixture.get('referees', [])
            
            # Filtrar apenas referees principais (type=6)
            main_referees = [r for r in referees if r.get('type_id') == 6]
            
            if main_referees and sportmonks_id in id_mapping:
                main_referee = main_referees[0]
                referee_id = main_referee.get('id')
                
                if referee_id:
                    db_fixture_id = id_mapping[sportmonks_id]
                    
                    try:
                        # Atualizar fixture com referee ID
                        self.supabase.client.table('fixtures').update({
                            'referee': str(referee_id)
                        }).eq('id', db_fixture_id).execute()
                        
                        updates_count += 1
                        logger.debug(f"✅ Fixture {sportmonks_id}: referee ID {referee_id}")
                        
                    except Exception as e:
                        logger.error(f"❌ Erro ao atualizar fixture {sportmonks_id}: {e}")
        
        return updates_count
    
    def collect_all_referees(self, max_fixtures: int = None, progress_interval: int = 100):
        """Coletar referees para todas as fixtures sem referee"""
        logger.info("🚀 INICIANDO COLETA MASSIVA DE REFEREES...")
        
        # Buscar fixtures sem referee
        fixtures_to_process = self.get_fixtures_without_referee(max_fixtures)
        
        if not fixtures_to_process:
            logger.info("✅ Todas as fixtures já têm referee!")
            return True
        
        total_fixtures = len(fixtures_to_process)
        total_batches = (total_fixtures + self.batch_size - 1) // self.batch_size
        
        logger.info(f"📊 Processando {total_fixtures} fixtures em {total_batches} lotes")
        
        total_updates = 0
        start_time = datetime.now()
        
        # Processar em lotes
        for i in range(0, total_fixtures, self.batch_size):
            batch_num = (i // self.batch_size) + 1
            batch = fixtures_to_process[i:i + self.batch_size]
            
            logger.info(f"📡 Processando lote {batch_num}/{total_batches} ({len(batch)} fixtures)")
            
            try:
                updates = self.process_referees_batch(batch)
                total_updates += updates
                
                logger.info(f"  ✅ {updates} fixtures atualizadas no lote {batch_num}")
                
                # Progress report
                if batch_num % progress_interval == 0:
                    elapsed = datetime.now() - start_time
                    rate = batch_num / elapsed.total_seconds() * 60  # batches per minute
                    eta_minutes = (total_batches - batch_num) / rate if rate > 0 else 0
                    
                    logger.info(f"📈 Progresso: {batch_num}/{total_batches} lotes ({batch_num/total_batches*100:.1f}%)")
                    logger.info(f"⏱️ Taxa: {rate:.1f} lotes/min, ETA: {eta_minutes:.1f} min")
                    logger.info(f"💾 Total atualizado: {total_updates} fixtures")
                
            except Exception as e:
                logger.error(f"❌ Erro no lote {batch_num}: {e}")
            
            # Pausa entre lotes
            time.sleep(self.delay_between_batches)
        
        # Relatório final
        elapsed_total = datetime.now() - start_time
        logger.info(f"\\n📊 RELATÓRIO FINAL:")
        logger.info(f"  - Fixtures processadas: {total_fixtures}")
        logger.info(f"  - Fixtures atualizadas: {total_updates}")
        logger.info(f"  - Taxa de sucesso: {total_updates/total_fixtures*100:.2f}%")
        logger.info(f"  - Tempo total: {elapsed_total}")
        
        return total_updates > 0
    
    def get_coverage_report(self):
        """Gerar relatório de cobertura atual"""
        logger.info("📊 Gerando relatório de cobertura...")
        
        result = self.supabase.client.table('fixtures').select('id').execute()
        total_fixtures = len(result.data)
        
        result_with_referee = self.supabase.client.table('fixtures').select('id').is_('referee', 'null').execute()
        fixtures_without_referee = len(result_with_referee.data)
        
        fixtures_with_referee = total_fixtures - fixtures_without_referee
        coverage_percentage = fixtures_with_referee * 100.0 / total_fixtures
        
        logger.info(f"📈 COBERTURA ATUAL:")
        logger.info(f"  - Total fixtures: {total_fixtures}")
        logger.info(f"  - Com referee: {fixtures_with_referee} ({coverage_percentage:.2f}%)")
        logger.info(f"  - Sem referee: {fixtures_without_referee}")
        
        return {
            'total': total_fixtures,
            'with_referee': fixtures_with_referee,
            'without_referee': fixtures_without_referee,
            'coverage_percentage': coverage_percentage
        }

def main():
    """Função principal"""
    collector = RefereeMassCollector()
    
    # Relatório inicial
    initial_coverage = collector.get_coverage_report()
    
    # Coletar referees (começar com 1000 fixtures para teste)
    logger.info("🧪 Iniciando com 1000 fixtures para teste...")
    success = collector.collect_all_referees(max_fixtures=1000, progress_interval=10)
    
    if success:
        # Relatório final
        final_coverage = collector.get_coverage_report()
        
        improvement = final_coverage['coverage_percentage'] - initial_coverage['coverage_percentage']
        logger.info(f"\\n🎉 COLETA CONCLUÍDA!")
        logger.info(f"📈 Melhoria na cobertura: +{improvement:.2f}%")
        
        if improvement > 0:
            logger.info("✅ Pronto para processar todas as fixtures restantes!")
        else:
            logger.warning("⚠️ Nenhuma melhoria detectada. Verificar logs.")
    else:
        logger.error("💥 Falha na coleta de referees!")

if __name__ == "__main__":
    main()
