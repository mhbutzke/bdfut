#!/usr/bin/env python3
"""
Script para debugar a paginação da API de seasons.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config import Config
from src.sportmonks_client import SportmonksClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_pagination():
    """
    Debug da paginação da API de seasons.
    """
    logger.info("=" * 80)
    logger.info("🔍 DEBUGANDO PAGINAÇÃO DA API SEASONS")
    logger.info("=" * 80)
    
    # Inicializar cliente Sportmonks
    sportmonks = SportmonksClient()
    
    # Testar primeira página
    logger.info("📄 Testando página 1...")
    response = sportmonks._make_request(
        '/seasons',
        {
            'include': '',
            'page': 1,
            'per_page': 25
        }
    )
    
    if response:
        logger.info("✅ Resposta recebida!")
        logger.info(f"📊 Dados: {len(response.get('data', []))} seasons")
        
        pagination = response.get('pagination', {})
        logger.info(f"📋 Paginação completa: {json.dumps(pagination, indent=2)}")
        
        # Salvar resposta completa para análise
        with open('debug_seasons_page1.json', 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, ensure_ascii=False, default=str)
        logger.info("💾 Resposta salva em debug_seasons_page1.json")
        
        # Testar página 2 se houver
        if pagination.get('has_more', False):
            logger.info("📄 Testando página 2...")
            response2 = sportmonks._make_request(
                '/seasons',
                {
                    'include': '',
                    'page': 2,
                    'per_page': 25
                }
            )
            
            if response2:
                logger.info("✅ Resposta página 2 recebida!")
                logger.info(f"📊 Dados página 2: {len(response2.get('data', []))} seasons")
                
                pagination2 = response2.get('pagination', {})
                logger.info(f"📋 Paginação página 2: {json.dumps(pagination2, indent=2)}")
                
                # Salvar resposta página 2
                with open('debug_seasons_page2.json', 'w', encoding='utf-8') as f:
                    json.dump(response2, f, indent=2, ensure_ascii=False, default=str)
                logger.info("💾 Resposta página 2 salva em debug_seasons_page2.json")
            else:
                logger.error("❌ Sem resposta na página 2")
        else:
            logger.info("ℹ️ Não há mais páginas (has_more = False)")
    else:
        logger.error("❌ Sem resposta na página 1")

if __name__ == "__main__":
    debug_pagination()
