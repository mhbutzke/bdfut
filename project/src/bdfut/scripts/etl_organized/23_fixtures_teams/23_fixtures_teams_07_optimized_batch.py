#!/usr/bin/env python3
"""
Script OTIMIZADO para enriquecimento de fixtures usando chamada multi com até 10 fixture_ids
Usa a chamada: https://api.sportmonks.com/v3/football/fixtures/multi/ID1,ID2,ID3?api_token=TOKEN&include=participants;
"""

import sys
import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizedBatchEnrichment:
    """Classe para enriquecimento otimizado usando chamada multi com até 10 fixture_ids"""
    
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.total_processed = 0
        self.total_updated = 0
        self.start_time = datetime.now()
        
    def get_all_fixtures(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Buscar fixtures para processamento"""
        try:
            response = self.supabase.client.from_('fixtures').select(
                'fixture_id, match_date, home_team_name, away_team_name, home_team_id, away_team_id'
            ).order('match_date', desc=True).range(offset, offset + limit - 1).execute()
            
            if response.data:
                return response.data
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures: {e}")
            return []
    
    def get_total_fixtures_count(self) -> int:
        """Obter total de fixtures na tabela"""
        try:
            response = self.supabase.client.from_('fixtures').select('fixture_id', count='exact').execute()
            return response.count if response.count else 0
            
        except Exception as e:
            logger.error(f"Erro ao contar fixtures: {e}")
            return 0
    
    def process_participants_for_fixture(self, fixture_data: Dict) -> Dict:
        """Processar participants de uma fixture e extrair home_team_id e away_team_id"""
        participants = fixture_data.get('participants', [])
        
        home_team_id = None
        away_team_id = None
        
        for participant in participants:
            participant_id = participant.get('id')
            meta = participant.get('meta', {})
            location = meta.get('location')
            
            if location == 'home':
                home_team_id = participant_id
            elif location == 'away':
                away_team_id = participant_id
        
        return {
            'home_team_id': home_team_id,
            'away_team_id': away_team_id
        }
    
    def batch_update_fixtures(self, updates: List[Dict]) -> int:
        """Atualizar múltiplas fixtures em lote usando upsert"""
        if not updates:
            return 0
            
        try:
            # Preparar dados para upsert
            upsert_data = []
            for update in updates:
                upsert_data.append({
                    'fixture_id': update['fixture_id'],
                    'home_team_id': update['home_team_id'],
                    'away_team_id': update['away_team_id']
                })
            
            # Executar upsert em lote
            response = self.supabase.client.from_('fixtures').upsert(
                upsert_data, 
                on_conflict='fixture_id'
            ).execute()
            
            if response.data:
                return len(response.data)
            else:
                logger.warning(f"⚠️ Nenhuma fixture atualizada no lote")
                return 0
                
        except Exception as e:
            logger.error(f"Erro ao atualizar lote de fixtures: {e}")
            return 0
    
    def process_fixtures_batch(self, fixtures: List[Dict]) -> int:
        """Processar um lote de até 10 fixtures usando chamada multi"""
        if not fixtures:
            return 0
            
        # Limitar a 10 fixtures por lote
        fixtures_batch = fixtures[:10]
        fixture_ids = [str(f['fixture_id']) for f in fixtures_batch]
        fixture_ids_str = ','.join(fixture_ids)
        
        logger.info(f"🔍 Processando lote de {len(fixtures_batch)} fixtures: {fixture_ids_str}")
        
        try:
            # Chamar API com múltiplos IDs e include participants (exatamente como solicitado)
            api_response = self.sportmonks.get_fixtures_multi(
                fixture_ids_str, 
                include='participants'
            )
            
            if not api_response or 'data' not in api_response:
                logger.warning(f"Nenhum dado retornado para fixtures {fixture_ids_str}")
                return 0
            
            # Preparar atualizações em lote
            batch_updates = []
            
            # Processar cada fixture na resposta
            for fixture_data in api_response['data']:
                fixture_id = fixture_data.get('id')
                
                # Processar participants
                team_ids = self.process_participants_for_fixture(fixture_data)
                
                if team_ids['home_team_id'] and team_ids['away_team_id']:
                    batch_updates.append({
                        'fixture_id': fixture_id,
                        'home_team_id': team_ids['home_team_id'],
                        'away_team_id': team_ids['away_team_id']
                    })
                    logger.info(f"✅ Fixture {fixture_id}: home={team_ids['home_team_id']}, away={team_ids['away_team_id']}")
                else:
                    logger.warning(f"⚠️ Fixture {fixture_id} não possui team IDs completos")
            
            # Executar atualização em lote
            if batch_updates:
                updated_count = self.batch_update_fixtures(batch_updates)
                logger.info(f"📊 Lote processado: {len(fixtures_batch)} fixtures, {updated_count} atualizadas")
                return updated_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao processar lote de fixtures {fixture_ids_str}: {e}")
            return 0
    
    def print_progress_report(self):
        """Imprimir relatório de progresso"""
        elapsed_time = datetime.now() - self.start_time
        elapsed_minutes = elapsed_time.total_seconds() / 60
        
        if elapsed_minutes > 0:
            rate = self.total_processed / elapsed_minutes
            eta_minutes = (self.total_fixtures - self.total_processed) / rate if rate > 0 else 0
            
            logger.info(f"""
📊 RELATÓRIO DE PROGRESSO OTIMIZADO
======================================================================
⏱️  Tempo decorrido: {elapsed_minutes:.1f} minutos
📈 Fixtures processadas: {self.total_processed:,}
✅ Fixtures atualizadas: {self.total_updated:,}
🚀 Taxa de processamento: {rate:.1f} fixtures/minuto
⏳ ETA: {eta_minutes:.1f} minutos
📊 Progresso: {(self.total_processed/self.total_fixtures)*100:.1f}%
""")
    
    def run_optimized_enrichment(self, max_fixtures: Optional[int] = None):
        """Executar enriquecimento OTIMIZADO"""
        logger.info("🚀 Iniciando ENRIQUECIMENTO OTIMIZADO com chamada multi (até 10 fixture_ids)...")
        logger.info("=" * 80)
        
        # Obter total de fixtures
        self.total_fixtures = self.get_total_fixtures_count()
        
        if self.total_fixtures == 0:
            logger.info("❌ Nenhuma fixture encontrada!")
            return
        
        logger.info(f"📊 Total de fixtures para processar: {self.total_fixtures:,}")
        
        batch_size = 10  # Exatamente 10 fixtures por lote
        report_interval = 100  # Relatório a cada 100 fixtures processadas
        offset = 0
        
        while offset < self.total_fixtures:
            # Verificar limite máximo se especificado
            if max_fixtures and self.total_processed >= max_fixtures:
                logger.info(f"✅ Limite de {max_fixtures} fixtures atingido!")
                break
            
            # Buscar lote de fixtures
            fixtures = self.get_all_fixtures(batch_size, offset)
            
            if not fixtures:
                logger.info("✅ Todas as fixtures foram processadas!")
                break
            
            # Processar lote
            updated = self.process_fixtures_batch(fixtures)
            self.total_processed += len(fixtures)
            self.total_updated += updated
            
            # Relatório de progresso
            if self.total_processed % report_interval == 0:
                self.print_progress_report()
            
            # Rate limiting (0.5 segundo entre lotes)
            time.sleep(0.5)
            
            # Atualizar offset
            offset += batch_size
        
        # Relatório final
        elapsed_time = datetime.now() - self.start_time
        elapsed_minutes = elapsed_time.total_seconds() / 60
        
        logger.info(f"""
🎉 ENRIQUECIMENTO OTIMIZADO CONCLUÍDO!
======================================================================
⏱️  Tempo total: {elapsed_minutes:.1f} minutos
📈 Fixtures processadas: {self.total_processed:,}
✅ Fixtures atualizadas: {self.total_updated:,}
🚀 Taxa média: {self.total_processed/elapsed_minutes:.1f} fixtures/minuto
📊 Taxa de sucesso: {(self.total_updated/self.total_processed)*100:.1f}%
""")

def main():
    """Função principal"""
    try:
        enrichment = OptimizedBatchEnrichment()
        
        # Executar enriquecimento com limite de 100 fixtures para teste
        enrichment.run_optimized_enrichment(max_fixtures=100)
        
    except KeyboardInterrupt:
        logger.info("⏹️ Enriquecimento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()
