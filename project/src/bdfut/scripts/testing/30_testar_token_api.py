#!/usr/bin/env python3
"""
Script para testar o token da Sportmonks API
"""

import requests
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_api_token():
    """Testar token da API Sportmonks"""
    
    # Token fornecido pelo usuário
    api_token = "eCvQGYBfNOTVYCGJYYYqJNWBZCGvnGJJMZOYhJZJ"
    
    logger.info("🔑 Testando token da Sportmonks API...")
    logger.info(f"Token: {api_token}")
    
    # URL de teste simples
    url = f"https://api.sportmonks.com/v3/core/countries?api_token={api_token}&include="
    
    logger.info(f"🌐 Fazendo requisição para: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        
        logger.info(f"📊 Status Code: {response.status_code}")
        logger.info(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Token válido!")
            logger.info(f"📊 Resposta: {data}")
            
            # Verificar estrutura da resposta
            if 'data' in data:
                countries = data['data']
                logger.info(f"📊 Countries encontrados: {len(countries)}")
                
                if countries:
                    logger.info("📋 Primeiros countries:")
                    for i, country in enumerate(countries[:5]):
                        logger.info(f"   {i+1}. ID {country.get('id')} - {country.get('name')} ({country.get('iso2')})")
                
                # Verificar paginação
                pagination = data.get('pagination', {})
                if pagination:
                    logger.info(f"📊 Paginação: {pagination}")
            
        elif response.status_code == 401:
            logger.error("❌ Token inválido - Erro 401 Unauthorized")
            logger.error(f"Resposta: {response.text}")
            
        elif response.status_code == 429:
            logger.warning("⚠️ Rate limit atingido")
            logger.error(f"Resposta: {response.text}")
            
        else:
            logger.error(f"❌ Erro na API: {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro na requisição: {e}")
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")

def main():
    """Função principal"""
    
    logger.info("=" * 60)
    logger.info("🔑 TESTANDO TOKEN DA SPORTMONKS API")
    logger.info("=" * 60)
    
    test_api_token()

if __name__ == "__main__":
    main()
