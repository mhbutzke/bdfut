#!/usr/bin/env python3
"""
Script de teste para enriquecer a tabela fixtures com home_team_id e away_team_id
usando o include participants da API Sportmonks
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
        
    def get_test_fixtures(self, limit: int = 5) -> List[Dict]:
        """Buscar fixtures de teste que não possuem home_team_id ou away_team_id"""
        try:
            response = self.supabase.client.from_('fixtures').select(
                'fixture_id, match_date, home_team_name, away_team_name, home_team_id, away_team_id'
            ).or_('home_team_id.is.null,away_team_id.is.null').order('match_date', desc=True).limit(limit).execute()
            
            if response.data:
                logger.info(f"📊 {len(response.data)} fixtures encontradas para teste")
                return response.data
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures de teste: {e}")
            return []
    
    def test_api_response(self, fixture_ids: List[int]) -> Dict:
        """Testar resposta da API com participants"""
        fixture_ids_str = ','.join(map(str, fixture_ids))
        
        logger.info(f"🔍 Testando API para fixtures: {fixture_ids_str}")
        
        try:
            # Chamar API com múltiplos IDs e include participants
            api_response = self.sportmonks.get_fixtures_multi(
                fixture_ids_str, 
                include='participants'
            )
            
            if not api_response or 'data' not in api_response:
                logger.warning(f"Nenhum dado retornado para fixtures {fixture_ids_str}")
                return {}
            
            logger.info(f"✅ API retornou {len(api_response['data'])} fixtures")
            
            # Analisar estrutura dos participants
            for fixture_data in api_response['data']:
                fixture_id = fixture_data.get('id')
                participants = fixture_data.get('participants', [])
                
                logger.info(f"    📊 Fixture {fixture_id}: {len(participants)} participants")
                
                # Analisar cada participant
                for participant in participants:
                    location = participant.get('location')
                    participant_id = participant.get('id')
                    name = participant.get('name')
                    
                    logger.info(f"       🏠 Location: {location}, ID: {participant_id}, Name: {name}")
            
            return api_response
            
        except Exception as e:
            logger.error(f"Erro ao testar API: {e}")
            return {}
    
    def process_participants_for_fixture(self, fixture_data: Dict) -> Dict:
        """Processar participants de uma fixture e extrair home_team_id e away_team_id"""
        participants = fixture_data.get('participants', [])
        
        home_team_id = None
        away_team_id = None
        
        for participant in participants:
            location = participant.get('location')
            participant_id = participant.get('id')
            
            if location == 'Home':
                home_team_id = participant_id
            elif location == 'Away':
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
    
    def run_test(self):
        """Executar teste completo"""
        logger.info("🚀 Iniciando teste de enriquecimento de fixtures com team IDs...")
        logger.info("=" * 70)
        
        # 1. Buscar fixtures de teste
        test_fixtures = self.get_test_fixtures(5)
        
        if not test_fixtures:
            logger.info("✅ Todas as fixtures já possuem team IDs!")
            return
        
        # 2. Testar API response
        fixture_ids = [f['fixture_id'] for f in test_fixtures]
        api_response = self.test_api_response(fixture_ids)
        
        if not api_response:
            logger.error("❌ Falha ao obter dados da API")
            return
        
        # 3. Processar e atualizar fixtures
        updated_count = 0
        
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
        
        # 4. Relatório final
        logger.info(f"""
🎉 TESTE CONCLUÍDO!
======================================================================
📊 Fixtures testadas: {len(test_fixtures)}
✅ Fixtures atualizadas: {updated_count}
❌ Fixtures com problemas: {len(test_fixtures) - updated_count}
""")

def main():
    """Função principal"""
    try:
        enrichment = FixturesTeamsEnrichment()
        enrichment.run_test()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()
