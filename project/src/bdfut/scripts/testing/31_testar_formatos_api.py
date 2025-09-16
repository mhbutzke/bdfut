#!/usr/bin/env python3
"""
Script para testar diferentes formatos de URL da Sportmonks API
"""

import requests
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_different_formats():
    """Testar diferentes formatos de URL da API"""
    
    # Token fornecido pelo usuário
    api_token = "eCvQGYBfNOTVYCGJYYYqJNWBZCGvnGJJMZOYhJZJ"
    
    logger.info("🔑 Testando diferentes formatos de URL da Sportmonks API...")
    logger.info(f"Token: {api_token}")
    
    # Diferentes formatos de URL para testar
    test_urls = [
        # Formato 1: api_token como parâmetro
        f"https://api.sportmonks.com/v3/core/countries?api_token={api_token}&include=",
        
        # Formato 2: api_token como parâmetro sem include
        f"https://api.sportmonks.com/v3/core/countries?api_token={api_token}",
        
        # Formato 3: api_token como parâmetro com include específico
        f"https://api.sportmonks.com/v3/core/countries?api_token={api_token}&include=continent",
        
        # Formato 4: api_token como header
        "https://api.sportmonks.com/v3/core/countries?include=",
        
        # Formato 5: api_token como parâmetro com paginação
        f"https://api.sportmonks.com/v3/core/countries?api_token={api_token}&include=&page=1&per_page=10",
        
        # Formato 6: endpoint diferente
        f"https://api.sportmonks.com/v3/football/countries?api_token={api_token}&include=",
        
        # Formato 7: sem v3
        f"https://api.sportmonks.com/core/countries?api_token={api_token}&include=",
    ]
    
    headers_with_token = {
        'Authorization': f'Bearer {api_token}',
        'X-API-Key': api_token,
        'api_token': api_token
    }
    
    for i, url in enumerate(test_urls, 1):
        logger.info(f"\n📄 Teste {i}: {url}")
        
        try:
            if i == 4:  # Teste com header
                response = requests.get(url, headers=headers_with_token, timeout=30)
            else:
                response = requests.get(url, timeout=30)
            
            logger.info(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("✅ SUCESSO!")
                data = response.json()
                logger.info(f"📊 Resposta: {data}")
                return url, data
            elif response.status_code == 401:
                logger.error("❌ Token inválido - Erro 401 Unauthorized")
            elif response.status_code == 404:
                logger.warning("⚠️ Endpoint não encontrado - Erro 404")
            elif response.status_code == 429:
                logger.warning("⚠️ Rate limit atingido")
            else:
                logger.error(f"❌ Erro: {response.status_code}")
                logger.error(f"Resposta: {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na requisição: {e}")
        except Exception as e:
            logger.error(f"❌ Erro geral: {e}")
        
        # Aguardar entre testes
        import time
        time.sleep(1)
    
    logger.error("❌ Nenhum formato funcionou")
    return None, None

def test_simple_endpoint():
    """Testar endpoint mais simples"""
    
    api_token = "eCvQGYBfNOTVYCGJYYYqJNWBZCGvnGJJMZOYhJZJ"
    
    logger.info("\n🔍 Testando endpoint mais simples...")
    
    # Testar endpoint básico
    simple_urls = [
        f"https://api.sportmonks.com/v3/core/countries?api_token={api_token}",
        f"https://api.sportmonks.com/v3/football/countries?api_token={api_token}",
        f"https://api.sportmonks.com/v3/core/continents?api_token={api_token}",
        f"https://api.sportmonks.com/v3/football/continents?api_token={api_token}",
    ]
    
    for url in simple_urls:
        logger.info(f"🌐 Testando: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            logger.info(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("✅ FUNCIONOU!")
                data = response.json()
                logger.info(f"📊 Dados: {data}")
                return url, data
            else:
                logger.error(f"❌ Erro {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
    
    return None, None

def main():
    """Função principal"""
    
    logger.info("=" * 60)
    logger.info("🔑 TESTANDO DIFERENTES FORMATOS DA SPORTMONKS API")
    logger.info("=" * 60)
    
    # Testar diferentes formatos
    working_url, data = test_different_formats()
    
    if not working_url:
        # Testar endpoints mais simples
        working_url, data = test_simple_endpoint()
    
    if working_url:
        logger.info(f"\n🎉 FORMATO QUE FUNCIONOU: {working_url}")
        logger.info("✅ Token está válido!")
    else:
        logger.error("\n❌ NENHUM FORMATO FUNCIONOU")
        logger.error("❌ Token pode estar inválido ou expirado")

if __name__ == "__main__":
    main()
