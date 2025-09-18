#!/usr/bin/env python3
"""
Script de teste abrangente para eventos, escalações e estatísticas
"""

import os
import sys
import json
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveTestScript:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def get_test_fixtures(self, limit: int = 5):
        """Obter fixtures para teste"""
        try:
            response = self.supabase.client.table('fixtures').select(
                'id, sportmonks_id, match_date, home_score, away_score, status'
            ).not_.is_('match_date', 'null').in_(
                'status', ['FT', 'FT_PEN', 'AET']
            ).order('match_date', desc=True).limit(limit).execute()
            
            return response.data
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixtures: {e}")
            return []
            
    def test_all_data_types(self, fixture_id: int):
        """Testar todos os tipos de dados para uma fixture"""
        results = {
            'fixture_id': fixture_id,
            'events': None,
            'lineups': None,
            'statistics': None,
            'success': False
        }
        
        try:
            # Testar eventos
            logger.info(f"📡 Testando eventos para fixture {fixture_id}")
            events_data = self.sportmonks.get_fixture_events(fixture_id)
            if events_data:
                results['events'] = {
                    'count': len(events_data),
                    'cards': sum(1 for e in events_data if e.get('type') in ['yellow_card', 'red_card']),
                    'fouls': sum(1 for e in events_data if e.get('type') == 'foul')
                }
                
            # Testar escalações
            logger.info(f"📡 Testando escalações para fixture {fixture_id}")
            lineups_data = self.sportmonks.get_fixture_lineups(fixture_id)
            if lineups_data:
                results['lineups'] = {
                    'count': len(lineups_data),
                    'teams': len(set(l.get('team_id') for l in lineups_data if l.get('team_id'))),
                    'players': len(lineups_data)
                }
                
            # Testar estatísticas
            logger.info(f"📡 Testando estatísticas para fixture {fixture_id}")
            statistics_data = self.sportmonks.get_fixture_statistics(fixture_id)
            if statistics_data:
                results['statistics'] = {
                    'count': len(statistics_data),
                    'teams': len(set(s.get('team_id') for s in statistics_data if s.get('team_id'))),
                    'card_stats': sum(1 for s in statistics_data if s.get('type') in ['yellow_cards', 'red_cards'])
                }
                
            results['success'] = True
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar fixture {fixture_id}: {e}")
            
        return results
        
    def run_comprehensive_test(self, limit: int = 5):
        """Executar teste abrangente"""
        logger.info(f"🚀 INICIANDO TESTE ABRANGENTE COM {limit} FIXTURES")
        
        fixtures = self.get_test_fixtures(limit)
        
        if not fixtures:
            logger.error("❌ Nenhuma fixture encontrada para teste")
            return
            
        results = []
        
        for fixture in fixtures:
            fixture_id = fixture['sportmonks_id']
            logger.info(f"\n📡 Testando fixture {fixture_id}")
            
            result = self.test_all_data_types(fixture_id)
            results.append(result)
            
        # Resumo dos resultados
        logger.info(f"\n📊 RESUMO DOS TESTES:")
        logger.info(f"   Fixtures testadas: {len(results)}")
        logger.info(f"   Sucessos: {sum(1 for r in results if r['success'])}")
        
        events_count = sum(1 for r in results if r['events'])
        lineups_count = sum(1 for r in results if r['lineups'])
        statistics_count = sum(1 for r in results if r['statistics'])
        
        logger.info(f"   Com eventos: {events_count}")
        logger.info(f"   Com escalações: {lineups_count}")
        logger.info(f"   Com estatísticas: {statistics_count}")
        
        # Salvar resultados
        with open("comprehensive_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        logger.info("💾 Resultados salvos em: comprehensive_test_results.json")
        
        return results

if __name__ == "__main__":
    test_script = ComprehensiveTestScript()
    results = test_script.run_comprehensive_test(5)
    
    if results:
        logger.info("✅ Teste abrangente concluído com sucesso!")
    else:
        logger.error("❌ Teste abrangente falhou!")
