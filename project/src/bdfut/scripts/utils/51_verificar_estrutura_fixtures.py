#!/usr/bin/env python3
"""
Script para verificar a estrutura atual da tabela fixtures.
"""

import os
import sys
import logging

# Adicionar o diretório bdfut ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from bdfut.config.config import Config
from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verificar_estrutura_fixtures():
    """
    Verifica a estrutura atual da tabela fixtures.
    """
    logger.info("=" * 80)
    logger.info("🔍 VERIFICANDO ESTRUTURA DA TABELA FIXTURES")
    logger.info("=" * 80)
    
    # Inicializar cliente Supabase
    supabase = SupabaseClient()
    
    try:
        # Consultar informações da tabela
        logger.info("📋 Consultando estrutura da tabela fixtures...")
        
        # Usar uma consulta SQL direta para obter informações da tabela
        result = supabase.client.rpc('exec_sql', {
            'sql': """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = 'fixtures' 
                AND table_schema = 'public'
                ORDER BY ordinal_position;
            """
        }).execute()
        
        if result.data:
            logger.info("✅ Estrutura da tabela fixtures:")
            logger.info("-" * 60)
            for col in result.data:
                col_name = col.get('column_name', 'unknown')
                data_type = col.get('data_type', 'unknown')
                nullable = col.get('is_nullable', 'unknown')
                default = col.get('column_default', '')
                max_length = col.get('character_maximum_length', '')
                
                logger.info(f"  • {col_name}: {data_type}" + 
                          (f"({max_length})" if max_length else "") +
                          f" - {'NULL' if nullable == 'YES' else 'NOT NULL'}" +
                          (f" DEFAULT {default}" if default else ""))
        else:
            logger.warning("⚠️ Não foi possível obter a estrutura da tabela")
            
        # Tentar uma consulta simples para ver se a tabela existe
        logger.info("\n📊 Testando consulta simples...")
        test_result = supabase.client.table('fixtures').select('*').limit(1).execute()
        
        if test_result.data is not None:
            logger.info(f"✅ Tabela fixtures existe e tem {len(test_result.data)} registros de teste")
            if test_result.data:
                logger.info("📋 Exemplo de registro:")
                for key, value in test_result.data[0].items():
                    logger.info(f"  • {key}: {value}")
        else:
            logger.error("❌ Tabela fixtures não existe ou não é acessível")
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar estrutura: {str(e)}")
        
        # Tentar método alternativo
        try:
            logger.info("🔄 Tentando método alternativo...")
            result = supabase.client.table('fixtures').select('*').limit(0).execute()
            logger.info("✅ Tabela fixtures existe (método alternativo)")
        except Exception as e2:
            logger.error(f"❌ Método alternativo também falhou: {str(e2)}")

if __name__ == "__main__":
    verificar_estrutura_fixtures()
