#!/usr/bin/env python3
"""
Script corrigido para enriquecer a tabela fixtures com home_team_id e away_team_id
usando o include participants da API Sportmonks
A informação de location está no campo meta dos participants
"""

import sys
import os
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

class FixturesTeamsEnrichment:
    """Classe para enriquecer fixtures com IDs dos times usando participants"""
    
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def get_fixtures_without_teams(self, limit: int = 10) -> List[Dict]:
        """Buscar fixtures que não possuem home_team_id ou away_team_id"""
        try:
            response = self.supabase.client.from_('fixtures').select(
                'fixture_id, match_date, home_team_name, away_team_name, home_team_id, away_team_id'
            ).or_('home_team_id.is.null,away_team_id.is.null').order('match_date', desc=True).limit(limit).execute()
            
            if response.data:
                logger.info(f"📊 {len(response.data)} fixtures encontradas sem team IDs")
                return response.data
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures sem team IDs: {e}")
            return []
    
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
                logger.info(f"✅ Fixture {fixture_id} atualizada: home_team_id={home_team_id}, away_team_id={away_team_id}")
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
        
        logger.info(f"🔍 Processando lote de {len(fixtures)} fixtures: {fixture_ids_str}")
        
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
    
    def run_enrichment(self, max_fixtures: Optional[int] = None):
        """Executar enriquecimento completo"""
        logger.info("🚀 Iniciando enriquecimento de fixtures com team IDs...")
        logger.info("=" * 70)
        
        batch_size = 10
        offset = 0
        total_updated = 0
        
        while True:
            # Buscar lote de fixtures
            fixtures = self.get_fixtures_without_teams(batch_size)
            
            if not fixtures:
                logger.info("✅ Todas as fixtures já possuem team IDs!")
                break
            
            # Processar lote
            updated = self.process_fixtures_batch(fixtures)
            total_updated += updated
            
            # Verificar limite máximo
            if max_fixtures and total_updated >= max_fixtures:
                logger.info(f"✅ Limite de {max_fixtures} fixtures atingido!")
                break
            
            # Rate limiting
            import time
            time.sleep(1)
            
            # Atualizar offset (simulado)
            offset += batch_size
            
            # Relatório de progresso
            logger.info(f"📊 Total atualizado: {total_updated}")
        
        # Relatório final
        logger.info(f"""
🎉 ENRIQUECIMENTO CONCLUÍDO!
======================================================================
✅ Fixtures atualizadas: {total_updated}
""")

def main():
    """Função principal"""
    try:
        enrichment = FixturesTeamsEnrichment()
        
        # Executar enriquecimento com limite de 50 fixtures para teste
        enrichment.run_enrichment(max_fixtures=50)
        
    except KeyboardInterrupt:
        logger.info("⏹️ Enriquecimento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()
