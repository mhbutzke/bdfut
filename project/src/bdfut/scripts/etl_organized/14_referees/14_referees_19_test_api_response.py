#!/usr/bin/env python3
"""
Teste da API para Verificar Resposta de Referees
================================================

Objetivo: Testar a API com fixtures que sabemos que têm referees
para verificar se a resposta está correta
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

def test_api_response():
    """Testar resposta da API com fixtures conhecidas"""
    Config.validate()
    api_key = Config.SPORTMONKS_API_KEY
    base_url = Config.SPORTMONKS_BASE_URL
    
    # Fixtures que sabemos que têm referees
    test_fixtures = [
        {"id": 12886, "sportmonks_id": 18863322},
        {"id": 12887, "sportmonks_id": 18863344},
        {"id": 12889, "sportmonks_id": 18863381},
        {"id": 12892, "sportmonks_id": 18863414},
        {"id": 12894, "sportmonks_id": 18863425}
    ]
    
    logger.info("🔍 Testando API com fixtures que têm referees...")
    
    for fixture in test_fixtures:
        sportmonks_id = fixture['sportmonks_id']
        db_id = fixture['id']
        
        logger.info(f"\\n📡 Testando fixture {db_id} (sportmonks: {sportmonks_id})")
        
        # Teste 1: Chamada individual
        url = f'{base_url}/fixtures/{sportmonks_id}'
        params = {
            'api_token': api_key,
            'include': 'referees'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            fixture_data = data.get('data')
            
            if fixture_data:
                referees = fixture_data.get('referees', [])
                logger.info(f"  📋 Referees encontrados: {len(referees)}")
                
                for ref in referees:
                    logger.info(f"    - referee_id: {ref.get('referee_id')}, type_id: {ref.get('type_id')}")
                
                # Salvar resposta para análise
                with open(f"test_fixture_{sportmonks_id}_response.json", "w") as f:
                    json.dump(fixture_data, f, indent=2, default=str)
                logger.info(f"  💾 Resposta salva em: test_fixture_{sportmonks_id}_response.json")
            else:
                logger.warning(f"  ⚠️ Nenhum dado retornado para fixture {sportmonks_id}")
                
        except Exception as e:
            logger.error(f"  ❌ Erro ao buscar fixture {sportmonks_id}: {e}")
    
    # Teste 2: Chamada multi
    logger.info("\\n📡 Testando chamada multi...")
    
    sportmonks_ids = [str(f['sportmonks_id']) for f in test_fixtures]
    multi_ids = ','.join(sportmonks_ids)
    
    url = f'{base_url}/fixtures/multi/{multi_ids}'
    params = {
        'api_token': api_key,
        'include': 'referees'
    }
    
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
        
        # Salvar resposta multi para análise
        with open("test_multi_response.json", "w") as f:
            json.dump(fixtures_data, f, indent=2, default=str)
        logger.info("💾 Resposta multi salva em: test_multi_response.json")
        
    except Exception as e:
        logger.error(f"❌ Erro na chamada multi: {e}")

def main():
    """Função principal"""
    logger.info("🚀 INICIANDO TESTE DA API DE REFEREES")
    test_api_response()
    logger.info("✅ Teste concluído!")

if __name__ == "__main__":
    main()
