#!/usr/bin/env python3
"""
Script simples para verificar a estrutura da tabela fixtures.
"""

import os
import json
import logging
from supabase import create_client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verificar_fixtures():
    """
    Verifica a estrutura da tabela fixtures usando credenciais diretas.
    """
    logger.info("=" * 80)
    logger.info("🔍 VERIFICANDO ESTRUTURA DA TABELA FIXTURES")
    logger.info("=" * 80)
    
    # Credenciais do Supabase (do .env ou hardcoded temporariamente)
    SUPABASE_URL = "https://qoqeshyuwmxfrjdkhwii.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFvcWVzaHl1d214ZnJqZGtod2lpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc2OTMxNzQsImV4cCI6MjA3MzI2OTE3NH0.4nj58uQ6FeKXAlJn4H2Qe13lws8JK9jrk7r8RwoP_10"
    
    try:
        # Inicializar cliente Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado")
        
        # Tentar uma consulta simples para ver se a tabela existe
        logger.info("📊 Testando consulta simples...")
        test_result = supabase.table('fixtures').select('*').limit(1).execute()
        
        if test_result.data is not None:
            logger.info(f"✅ Tabela fixtures existe")
            
            # Contar total de registros
            count_result = supabase.table('fixtures').select('*', count='exact').execute()
            total_count = count_result.count if count_result.count else 0
            logger.info(f"📊 Total de registros na tabela: {total_count}")
            
            if test_result.data:
                logger.info("📋 Exemplo de registro:")
                for key, value in test_result.data[0].items():
                    logger.info(f"  • {key}: {value}")
                    
                logger.info("\n📋 Colunas da tabela fixtures:")
                logger.info("-" * 40)
                for key in test_result.data[0].keys():
                    logger.info(f"  • {key}")
            else:
                logger.info("ℹ️ Tabela está vazia")
        else:
            logger.error("❌ Tabela fixtures não existe ou não é acessível")
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar tabela: {str(e)}")

if __name__ == "__main__":
    verificar_fixtures()
