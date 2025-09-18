#!/usr/bin/env python3
"""
Script para debugar a estrutura da resposta da API Sportmonks
e entender como identificar home/away teams nos participants
"""

import sys
import os
import json
import logging
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from bdfut.core.sportmonks_client import SportmonksClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_api_response():
    """Debugar resposta da API para entender estrutura dos participants"""
    
    sportmonks = SportmonksClient()
    
    # Testar com uma fixture específica
    test_fixture_id = "19441523"
    
    logger.info(f"🔍 Testando fixture {test_fixture_id} com includes: participants")
    
    try:
        # Chamar API com participants
        response = sportmonks.get_fixtures_multi(
            test_fixture_id, 
            include='participants'
        )
        
        if not response or 'data' not in response:
            logger.error("❌ Nenhuma resposta da API")
            return
        
        # Salvar resposta completa em arquivo para análise
        with open('debug_participants_response.json', 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        
        logger.info("💾 Resposta salva em debug_participants_response.json")
        
        # Analisar estrutura
        fixture_data = response['data'][0]
        logger.info(f"📊 Fixture ID: {fixture_data.get('id')}")
        
        # Analisar participants
        participants = fixture_data.get('participants', [])
        logger.info(f"👥 Número de participants: {len(participants)}")
        
        for i, participant in enumerate(participants):
            logger.info(f"   Participant {i+1}:")
            logger.info(f"      ID: {participant.get('id')}")
            logger.info(f"      Name: {participant.get('name')}")
            logger.info(f"      Location: {participant.get('location')}")
            logger.info(f"      Type: {participant.get('type')}")
            logger.info(f"      Sport ID: {participant.get('sport_id')}")
            logger.info(f"      Country ID: {participant.get('country_id')}")
            logger.info(f"      Venue ID: {participant.get('venue_id')}")
            logger.info(f"      Meta: {participant.get('meta')}")
            logger.info("      ---")
        
        # Verificar se há outros campos na fixture que possam indicar home/away
        logger.info("🔍 Outros campos da fixture:")
        for key, value in fixture_data.items():
            if key != 'participants':
                logger.info(f"   {key}: {value}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao debugar API: {e}")

def test_different_includes():
    """Testar diferentes includes para ver se há informação de home/away"""
    
    sportmonks = SportmonksClient()
    test_fixture_id = "19441523"
    
    includes_to_test = [
        'participants',
        'participants;lineups',
        'participants;statistics',
        'lineups',
        'statistics'
    ]
    
    for include in includes_to_test:
        logger.info(f"🔍 Testando include: {include}")
        
        try:
            response = sportmonks.get_fixtures_multi(test_fixture_id, include=include)
            
            if response and 'data' in response:
                fixture_data = response['data'][0]
                
                # Verificar se há informação de home/away em diferentes seções
                for section in ['participants', 'lineups', 'statistics']:
                    if section in fixture_data:
                        data = fixture_data[section]
                        logger.info(f"   📊 {section}: {len(data) if isinstance(data, list) else 'N/A'} items")
                        
                        if isinstance(data, list) and data:
                            first_item = data[0]
                            logger.info(f"      Primeiro item: {list(first_item.keys())}")
                            
                            # Procurar por campos que possam indicar home/away
                            for key, value in first_item.items():
                                if 'home' in key.lower() or 'away' in key.lower() or 'location' in key.lower():
                                    logger.info(f"         {key}: {value}")
            
        except Exception as e:
            logger.error(f"   ❌ Erro com include {include}: {e}")
        
        logger.info("   ---")

if __name__ == "__main__":
    logger.info("🚀 Iniciando debug da API Sportmonks...")
    logger.info("=" * 60)
    
    # Debug principal
    debug_api_response()
    
    logger.info("\n" + "=" * 60)
    
    # Testar diferentes includes
    test_different_includes()
    
    logger.info("\n🎉 Debug concluído!")
