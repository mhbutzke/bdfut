#!/usr/bin/env python3
"""
Script de teste para estatísticas - baseado nos resultados dos testes da API
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

class StatisticsTestScript:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def test_statistics_for_fixture(self, fixture_id: int):
        """Testar estatísticas para uma fixture específica"""
        try:
            # Buscar estatísticas da API
            statistics_data = self.sportmonks.get_fixture_statistics(fixture_id)
            
            if not statistics_data:
                logger.warning(f"❌ Nenhuma estatística encontrada para fixture {fixture_id}")
                return None
                
            logger.info(f"📊 {len(statistics_data)} estatísticas encontradas para fixture {fixture_id}")
            
            # Analisar estatísticas
            analysis = self.analyze_statistics(statistics_data)
            
            # Salvar resposta para análise
            with open(f"fixture_{fixture_id}_statistics_response.json", "w") as f:
                json.dump(statistics_data, f, indent=2)
                
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar estatísticas para fixture {fixture_id}: {e}")
            return None
            
    def analyze_statistics(self, statistics_data):
        """Analisar estatísticas coletadas"""
        analysis = {
            'total_statistics': len(statistics_data),
            'teams': {},
            'card_stats': {'yellow_cards': 0, 'red_cards': 0, 'fouls': 0},
            'possession': {},
            'shots': {'total': 0, 'on_target': 0},
            'passes': {'total': 0, 'accurate': 0},
            'goals': {'scored': 0, 'conceded': 0}
        }
        
        for stat in statistics_data:
            team_id = stat.get('team_id')
            team_name = stat.get('team_name', 'Unknown')
            
            if team_id not in analysis['teams']:
                analysis['teams'][team_id] = {
                    'name': team_name,
                    'stats': {}
                }
                
            # Analisar cartões
            if stat.get('type') == 'yellow_cards':
                analysis['card_stats']['yellow_cards'] += stat.get('value', 0)
            elif stat.get('type') == 'red_cards':
                analysis['card_stats']['red_cards'] += stat.get('value', 0)
            elif stat.get('type') == 'fouls':
                analysis['card_stats']['fouls'] += stat.get('value', 0)
                
            # Analisar posse de bola
            if stat.get('type') == 'ball_possession':
                analysis['possession'][team_id] = stat.get('value', 0)
                
            # Analisar chutes
            if stat.get('type') == 'shots_total':
                analysis['shots']['total'] += stat.get('value', 0)
            elif stat.get('type') == 'shots_on_target':
                analysis['shots']['on_target'] += stat.get('value', 0)
                
            # Analisar passes
            if stat.get('type') == 'passes_total':
                analysis['passes']['total'] += stat.get('value', 0)
            elif stat.get('type') == 'passes_accurate':
                analysis['passes']['accurate'] += stat.get('value', 0)
                
            # Analisar gols
            if stat.get('type') == 'goals':
                analysis['goals']['scored'] += stat.get('value', 0)
            elif stat.get('type') == 'goals_conceded':
                analysis['goals']['conceded'] += stat.get('value', 0)
                
        return analysis
        
    def run_test(self, fixture_id: int):
        """Executar teste completo"""
        logger.info(f"🚀 TESTANDO ESTATÍSTICAS PARA FIXTURE {fixture_id}")
        
        analysis = self.test_statistics_for_fixture(fixture_id)
        
        if analysis:
            logger.info(f"📊 Análise das estatísticas:")
            logger.info(f"   Total: {analysis['total_statistics']}")
            logger.info(f"   Times: {len(analysis['teams'])}")
            logger.info(f"   Cartões amarelos: {analysis['card_stats']['yellow_cards']}")
            logger.info(f"   Cartões vermelhos: {analysis['card_stats']['red_cards']}")
            logger.info(f"   Faltas: {analysis['card_stats']['fouls']}")
            logger.info(f"   Chutes: {analysis['shots']['total']}")
            logger.info(f"   Passes: {analysis['passes']['total']}")
            logger.info(f"   Gols: {analysis['goals']['scored']}")
            
        return analysis

if __name__ == "__main__":
    # Testar com uma fixture específica
    test_script = StatisticsTestScript()
    fixture_id = 19429228  # Fixture de teste
    
    analysis = test_script.run_test(fixture_id)
    
    if analysis:
        logger.info("✅ Teste de estatísticas concluído com sucesso!")
    else:
        logger.error("❌ Teste de estatísticas falhou!")
