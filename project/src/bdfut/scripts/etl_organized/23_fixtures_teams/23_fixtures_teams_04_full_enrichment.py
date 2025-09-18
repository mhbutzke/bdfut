#!/usr/bin/env python3
"""
Script para enriquecimento completo da tabela fixtures com home_team_id e away_team_id
Processa TODAS as fixtures usando chamadas de múltiplos IDs (10 por vez)
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

class FullFixturesTeamsEnrichment:
    """Classe para enriquecimento completo de fixtures com IDs dos times"""
    
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.total_processed = 0
        self.total_updated = 0
        self.start_time = datetime.now()
        
    def get_fixtures_without_teams(self, limit: int = 10) -> List[Dict]:
        """Buscar fixtures que não possuem home_team_id ou away_team_id"""
        try:
            response = self.supabase.client.from_('fixtures').select(
                'fixture_id, match_date, home_team_name, away_team_name, home_team_id, away_team_id'
            ).or_('home_team_id.is.null,away_team_id.is.null').order('match_date', desc=True).limit(limit).execute()
            
            if response.data:
                return response.data
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures sem team IDs: {e}")
            return []
    
    def get_total_fixtures_count(self) -> int:
        """Obter total de fixtures que precisam ser enriquecidas"""
        try:
            response = self.supabase.client.from_('fixtures').select(
                'fixture_id', count='exact'
            ).or_('home_team_id.is.null,away_team_id.is.null').execute()
            
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
    
    def update_fixture_teams(self, fixture_id: int, home_team_id: int, away_team_id: int) -> bool:
        """Atualizar fixture com os IDs dos times"""
        try:
            update_data = {
                'home_team_id': home_team_id,
                'away_team_id': away_team_id
            }
            
            response = self.supabase.client.from_('fixtures').update(update_data).eq('fixture_id', fixture_id).execute()
            
            if response.data:
                return True
            else:
                logger.warning(f"⚠️ Nenhuma linha atualizada para fixture {fixture_id}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao atualizar fixture {fixture_id}: {e}")
            return False
    
    def process_fixtures_batch(self, fixtures: List[Dict]) -> int:
        """Processar um lote de fixtures"""
        if not fixtures:
            return 0
            
        fixture_ids = [str(f['fixture_id']) for f in fixtures]
        fixture_ids_str = ','.join(fixture_ids)
        
        try:
            # Chamar API com múltiplos IDs e include participants
            api_response = self.sportmonks.get_fixtures_multi(
                fixture_ids_str, 
                include='participants'
            )
            
            if not api_response or 'data' not in api_response:
                logger.warning(f"Nenhum dado retornado para fixtures {fixture_ids_str}")
                return 0
            
            updated_count = 0
            
            # Processar cada fixture na resposta
            for fixture_data in api_response['data']:
                fixture_id = fixture_data.get('id')
                
                # Processar participants
                team_ids = self.process_participants_for_fixture(fixture_data)
                
                if team_ids['home_team_id'] and team_ids['away_team_id']:
                    # Atualizar fixture
                    if self.update_fixture_teams(
                        fixture_id, 
                        team_ids['home_team_id'], 
                        team_ids['away_team_id']
                    ):
                        updated_count += 1
                else:
                    logger.warning(f"⚠️ Fixture {fixture_id} não possui team IDs completos")
            
            return updated_count
            
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
📊 RELATÓRIO DE PROGRESSO
======================================================================
⏱️  Tempo decorrido: {elapsed_minutes:.1f} minutos
📈 Fixtures processadas: {self.total_processed:,}
✅ Fixtures atualizadas: {self.total_updated:,}
🚀 Taxa de processamento: {rate:.1f} fixtures/minuto
⏳ ETA: {eta_minutes:.1f} minutos
📊 Progresso: {(self.total_processed/self.total_fixtures)*100:.1f}%
""")
    
    def run_full_enrichment(self):
        """Executar enriquecimento completo"""
        logger.info("🚀 Iniciando ENRIQUECIMENTO COMPLETO de fixtures com team IDs...")
        logger.info("=" * 80)
        
        # Obter total de fixtures
        self.total_fixtures = self.get_total_fixtures_count()
        
        if self.total_fixtures == 0:
            logger.info("✅ Todas as fixtures já possuem team IDs!")
            return
        
        logger.info(f"📊 Total de fixtures para processar: {self.total_fixtures:,}")
        
        batch_size = 10
        report_interval = 100  # Relatório a cada 100 fixtures processadas
        
        while True:
            # Buscar lote de fixtures
            fixtures = self.get_fixtures_without_teams(batch_size)
            
            if not fixtures:
                logger.info("✅ Todas as fixtures já possuem team IDs!")
                break
            
            # Processar lote
            updated = self.process_fixtures_batch(fixtures)
            self.total_processed += len(fixtures)
            self.total_updated += updated
            
            # Relatório de progresso
            if self.total_processed % report_interval == 0:
                self.print_progress_report()
            
            # Rate limiting (1 segundo entre lotes)
            time.sleep(1)
        
        # Relatório final
        elapsed_time = datetime.now() - self.start_time
        elapsed_minutes = elapsed_time.total_seconds() / 60
        
        logger.info(f"""
🎉 ENRIQUECIMENTO COMPLETO CONCLUÍDO!
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
        enrichment = FullFixturesTeamsEnrichment()
        enrichment.run_full_enrichment()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Enriquecimento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()
