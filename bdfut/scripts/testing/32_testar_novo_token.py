#!/usr/bin/env python3
"""
Script para testar o novo token da Sportmonks API
"""

import requests
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_new_token():
    """Testar novo token da API Sportmonks"""
    
    # Novo token fornecido pelo usuário
    api_token = "teW8DGJoAC7Gc6r4u0RrCMB4IR4iy8s22BF9mgOTtoNUu3UBMc58wulgveYB"
    
    logger.info("🔑 Testando NOVO token da Sportmonks API...")
    logger.info(f"Token: {api_token}")
    
    # URL de teste
    url = f"https://api.sportmonks.com/v3/core/countries?api_token={api_token}&include="
    
    logger.info(f"🌐 Fazendo requisição para: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        
        logger.info(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("✅ Token VÁLIDO!")
            data = response.json()
            
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
                    total_pages = pagination.get('total_pages', 1)
                    total_count = pagination.get('total', 0)
                    logger.info(f"📊 Total de páginas: {total_pages}, Total de countries: {total_count}")
            
            return True, data
            
        elif response.status_code == 401:
            logger.error("❌ Token inválido - Erro 401 Unauthorized")
            logger.error(f"Resposta: {response.text}")
            return False, None
            
        elif response.status_code == 429:
            logger.warning("⚠️ Rate limit atingido")
            logger.error(f"Resposta: {response.text}")
            return False, None
            
        else:
            logger.error(f"❌ Erro na API: {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro na requisição: {e}")
        return False, None
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return False, None

def test_pagination():
    """Testar paginação com o novo token"""
    
    api_token = "teW8DGJoAC7Gc6r4u0RrCMB4IR4iy8s22BF9mgOTtoNUu3UBMc58wulgveYB"
    
    logger.info("\n📄 Testando paginação...")
    
    # Testar primeira página
    url = f"https://api.sportmonks.com/v3/core/countries?api_token={api_token}&include=&page=1&per_page=10"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            countries = data.get('data', [])
            pagination = data.get('pagination', {})
            
            logger.info(f"✅ Paginação funcionando!")
            logger.info(f"📊 Página 1: {len(countries)} countries")
            logger.info(f"📊 Paginação: {pagination}")
            
            return True
        else:
            logger.error(f"❌ Erro na paginação: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro na paginação: {e}")
        return False

def main():
    """Função principal"""
    
    logger.info("=" * 60)
    logger.info("🔑 TESTANDO NOVO TOKEN DA SPORTMONKS API")
    logger.info("=" * 60)
    
    # Testar token
    success, data = test_new_token()
    
    if success:
        logger.info("🎉 TOKEN FUNCIONANDO!")
        
        # Testar paginação
        if test_pagination():
            logger.info("🎉 PAGINAÇÃO FUNCIONANDO!")
            logger.info("✅ Pronto para coletar todos os countries!")
        else:
            logger.warning("⚠️ Problema com paginação")
    else:
        logger.error("❌ Token não funcionou")

if __name__ == "__main__":
    main()
