#!/usr/bin/env python3
"""
Teste com Fixtures Futuras (2026)
=================================

Objetivo: Testar a API com fixtures futuras para verificar se têm referees
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

def test_future_fixtures():
    """Testar fixtures futuras"""
    Config.validate()
    api_key = Config.SPORTMONKS_API_KEY
    base_url = Config.SPORTMONKS_BASE_URL
    
    # Fixtures futuras (2026) sem referee
    test_fixtures = [
        {"id": 78612, "sportmonks_id": 19441528},
        {"id": 78614, "sportmonks_id": 19441533},
        {"id": 78381, "sportmonks_id": 19441527},
        {"id": 78399, "sportmonks_id": 19441524},
        {"id": 78560, "sportmonks_id": 19441532}
    ]
    
    logger.info("🔍 Testando fixtures futuras (2026)...")
    
    # Teste com chamada multi
    sportmonks_ids = [str(f['sportmonks_id']) for f in test_fixtures]
    multi_ids = ','.join(sportmonks_ids)
    
    url = f'{base_url}/fixtures/multi/{multi_ids}'
    params = {
        'api_token': api_key,
        'include': 'referees'
    }
    
    logger.info(f"📡 Chamando API: {url}")
    logger.info(f"📋 Parâmetros: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        fixtures_data = data.get('data', [])
        
        logger.info(f"📋 Resposta multi: {len(fixtures_data)} fixtures")
        
        for fixture_data in fixtures_data:
            sportmonks_id = fixture_data.get('id')
            referees = fixture_data.get('referees', [])
            
            logger.info(f"  Fixture {sportmonks_id}: {len(referees)} referees")
            for ref in referees:
                logger.info(f"    - referee_id: {ref.get('referee_id')}, type_id: {ref.get('type_id')}")
        
        # Salvar resposta para análise
        with open("test_future_fixtures_response.json", "w") as f:
            json.dump(fixtures_data, f, indent=2, default=str)
        logger.info("💾 Resposta salva em: test_future_fixtures_response.json")
        
    except Exception as e:
        logger.error(f"❌ Erro na chamada multi: {e}")

def main():
    """Função principal"""
    logger.info("🚀 INICIANDO TESTE COM FIXTURES FUTURAS")
    test_future_fixtures()
    logger.info("✅ Teste concluído!")

if __name__ == "__main__":
    main()
