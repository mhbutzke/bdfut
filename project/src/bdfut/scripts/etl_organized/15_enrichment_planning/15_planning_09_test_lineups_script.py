#!/usr/bin/env python3
"""
Script de teste para escalações - baseado nos resultados dos testes da API
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

class LineupsTestScript:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def test_lineups_for_fixture(self, fixture_id: int):
        """Testar escalações para uma fixture específica"""
        try:
            # Buscar escalações da API
            lineups_data = self.sportmonks.get_fixture_lineups(fixture_id)
            
            if not lineups_data:
                logger.warning(f"❌ Nenhuma escalação encontrada para fixture {fixture_id}")
                return None
                
            logger.info(f"📊 {len(lineups_data)} escalações encontradas para fixture {fixture_id}")
            
            # Analisar escalações
            analysis = self.analyze_lineups(lineups_data)
            
            # Salvar resposta para análise
            with open(f"fixture_{fixture_id}_lineups_response.json", "w") as f:
                json.dump(lineups_data, f, indent=2)
                
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar escalações para fixture {fixture_id}: {e}")
            return None
            
    def analyze_lineups(self, lineups_data):
        """Analisar escalações coletadas"""
        analysis = {
            'total_lineups': len(lineups_data),
            'teams': {},
            'players': {'total': 0, 'with_positions': 0, 'captains': 0},
            'formations': {},
            'substitutions': 0
        }
        
        for lineup in lineups_data:
            team_id = lineup.get('team_id')
            team_name = lineup.get('team_name', 'Unknown')
            
            if team_id not in analysis['teams']:
                analysis['teams'][team_id] = {
                    'name': team_name,
                    'players': 0,
                    'formation': lineup.get('formation'),
                    'captain': None
                }
                
            # Contar jogadores
            analysis['teams'][team_id]['players'] += 1
            analysis['players']['total'] += 1
            
            # Analisar posições
            if lineup.get('position_name'):
                analysis['players']['with_positions'] += 1
                
            # Analisar capitão
            if lineup.get('captain'):
                analysis['players']['captains'] += 1
                analysis['teams'][team_id]['captain'] = lineup.get('player_name')
                
            # Analisar formação
            formation = lineup.get('formation')
            if formation:
                analysis['formations'][formation] = analysis['formations'].get(formation, 0) + 1
                
            # Analisar substituições
            if lineup.get('substitution'):
                analysis['substitutions'] += 1
                
        return analysis
        
    def run_test(self, fixture_id: int):
        """Executar teste completo"""
        logger.info(f"🚀 TESTANDO ESCALAÇÕES PARA FIXTURE {fixture_id}")
        
        analysis = self.test_lineups_for_fixture(fixture_id)
        
        if analysis:
            logger.info(f"📊 Análise das escalações:")
            logger.info(f"   Total: {analysis['total_lineups']}")
            logger.info(f"   Times: {len(analysis['teams'])}")
            logger.info(f"   Jogadores: {analysis['players']['total']}")
            logger.info(f"   Com posições: {analysis['players']['with_positions']}")
            logger.info(f"   Capitães: {analysis['players']['captains']}")
            logger.info(f"   Substituições: {analysis['substitutions']}")
            
        return analysis

if __name__ == "__main__":
    # Testar com uma fixture específica
    test_script = LineupsTestScript()
    fixture_id = 19429228  # Fixture de teste
    
    analysis = test_script.run_test(fixture_id)
    
    if analysis:
        logger.info("✅ Teste de escalações concluído com sucesso!")
    else:
        logger.error("❌ Teste de escalações falhou!")
