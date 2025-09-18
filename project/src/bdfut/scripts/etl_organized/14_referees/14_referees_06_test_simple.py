#!/usr/bin/env python3
"""
Teste Simples - Verificar Estrutura da API Multi-Include
========================================================

Objetivo: Testar a estrutura da API com múltiplos includes
Includes: referees,venue,league,season,state,round,stage
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

import requests
import logging
import json
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_multi_include_structure():
    """Testar estrutura da API com múltiplos includes"""
    Config.validate()
    api_key = Config.SPORTMONKS_API_KEY
    base_url = Config.SPORTMONKS_BASE_URL
    
    # Teste com 2 fixtures
    test_fixture_ids = "16475287,11865351"
    
    # Includes que queremos testar
    includes = [
        'referees',      # Árbitros
        'venue',         # Estádio
        'league',        # Liga
        'season',        # Temporada
        'state',         # Estado da partida
        'round',         # Rodada
        'stage',         # Fase
        'participants'   # Times participantes
    ]
    
    url = f'{base_url}/fixtures/multi/{test_fixture_ids}'
    params = {
        'api_token': api_key,
        'include': ';'.join(includes)  # Usar ; como separador
    }
    
    logger.info(f"🔍 Testando API multi com includes: {', '.join(includes)}")
    logger.info(f"📡 URL: {url}")
    logger.info(f"📋 Params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        fixtures = data.get('data', [])
        
        logger.info(f"✅ {len(fixtures)} fixtures retornadas")
        
        for i, fixture in enumerate(fixtures):
            logger.info(f"\n📊 FIXTURE {i+1} (ID: {fixture.get('id')}):")
            
            # Verificar cada include
            for include_name in includes:
                include_data = fixture.get(include_name)
                if include_data:
                    if isinstance(include_data, list):
                        logger.info(f"  {include_name}: {len(include_data)} itens")
                        if include_name == 'referees':
                            for ref in include_data:
                                logger.info(f"    - Referee ID: {ref.get('id')}, Type: {ref.get('type_id')}")
                    else:
                        logger.info(f"  {include_name}: {include_data.get('id')} - {include_data.get('name', 'N/A')}")
                else:
                    logger.info(f"  {include_name}: ❌ Não encontrado")
        
        # Salvar resposta completa para análise
        with open('test_multi_include_response.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"\n💾 Resposta salva em: test_multi_include_response.json")
        
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro na API: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        return False

if __name__ == "__main__":
    test_multi_include_structure()
