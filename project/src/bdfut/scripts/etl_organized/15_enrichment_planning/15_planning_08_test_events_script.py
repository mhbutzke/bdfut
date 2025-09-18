#!/usr/bin/env python3
"""
Script de teste para eventos - baseado nos resultados dos testes da API
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

class EventsTestScript:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def test_events_for_fixture(self, fixture_id: int):
        """Testar eventos para uma fixture específica"""
        try:
            # Buscar eventos da API
            events_data = self.sportmonks.get_fixture_events(fixture_id)
            
            if not events_data:
                logger.warning(f"❌ Nenhum evento encontrado para fixture {fixture_id}")
                return None
                
            logger.info(f"📊 {len(events_data)} eventos encontrados para fixture {fixture_id}")
            
            # Analisar eventos
            analysis = self.analyze_events(events_data)
            
            # Salvar resposta para análise
            with open(f"fixture_{fixture_id}_events_response.json", "w") as f:
                json.dump(events_data, f, indent=2)
                
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar eventos para fixture {fixture_id}: {e}")
            return None
            
    def analyze_events(self, events_data):
        """Analisar eventos coletados"""
        analysis = {
            'total_events': len(events_data),
            'event_types': {},
            'cards': {'yellow': 0, 'red': 0},
            'fouls': 0,
            'goals': 0,
            'substitutions': 0,
            'var_events': 0
        }
        
        for event in events_data:
            # Contar tipos de eventos
            event_type = event.get('type', 'unknown')
            analysis['event_types'][event_type] = analysis['event_types'].get(event_type, 0) + 1
            
            # Analisar cartões
            if event_type in ['yellow_card', 'red_card']:
                if event_type == 'yellow_card':
                    analysis['cards']['yellow'] += 1
                else:
                    analysis['cards']['red'] += 1
                    
            # Analisar faltas
            if event_type == 'foul':
                analysis['fouls'] += 1
                
            # Analisar gols
            if event_type in ['goal', 'own_goal']:
                analysis['goals'] += 1
                
            # Analisar substituições
            if event_type == 'substitution':
                analysis['substitutions'] += 1
                
            # Analisar VAR
            if event.get('var', False):
                analysis['var_events'] += 1
                
        return analysis
        
    def run_test(self, fixture_id: int):
        """Executar teste completo"""
        logger.info(f"🚀 TESTANDO EVENTOS PARA FIXTURE {fixture_id}")
        
        analysis = self.test_events_for_fixture(fixture_id)
        
        if analysis:
            logger.info(f"📊 Análise dos eventos:")
            logger.info(f"   Total: {analysis['total_events']}")
            logger.info(f"   Cartões amarelos: {analysis['cards']['yellow']}")
            logger.info(f"   Cartões vermelhos: {analysis['cards']['red']}")
            logger.info(f"   Faltas: {analysis['fouls']}")
            logger.info(f"   Gols: {analysis['goals']}")
            logger.info(f"   Substituições: {analysis['substitutions']}")
            logger.info(f"   Eventos VAR: {analysis['var_events']}")
            
        return analysis

if __name__ == "__main__":
    # Testar com uma fixture específica
    test_script = EventsTestScript()
    fixture_id = 19429228  # Fixture de teste
    
    analysis = test_script.run_test(fixture_id)
    
    if analysis:
        logger.info("✅ Teste de eventos concluído com sucesso!")
    else:
        logger.error("❌ Teste de eventos falhou!")
