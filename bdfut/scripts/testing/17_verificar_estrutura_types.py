#!/usr/bin/env python3
"""
Script para verificar a estrutura atual da tabela types
"""

import os
import sys
import logging

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from supabase import create_client
from config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verificar_estrutura_types():
    """Verificar estrutura atual da tabela types"""
    
    logger.info("🔍 Verificando estrutura atual da tabela types...")
    
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente: {e}")
        return
    
    try:
        # Buscar alguns registros para ver a estrutura
        response = supabase.table('types').select('*').limit(5).execute()
        
        if response.data:
            logger.info("📊 Estrutura atual da tabela types:")
            logger.info("=" * 50)
            
            # Mostrar as colunas disponíveis
            columns = list(response.data[0].keys())
            logger.info(f"📋 Colunas disponíveis: {columns}")
            
            # Mostrar exemplo de dados
            logger.info("\n📄 Exemplo de dados:")
            for i, record in enumerate(response.data[:3]):
                logger.info(f"   Registro {i+1}:")
                for key, value in record.items():
                    logger.info(f"     {key}: {value}")
                logger.info("")
                
        else:
            logger.warning("⚠️ Nenhum registro encontrado na tabela types")
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar estrutura: {e}")

def main():
    """Função principal"""
    
    logger.info("=" * 60)
    logger.info("🔍 VERIFICANDO ESTRUTURA DA TABELA TYPES")
    logger.info("=" * 60)
    
    verificar_estrutura_types()

if __name__ == "__main__":
    main()
