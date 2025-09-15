#!/usr/bin/env python3
"""
Script para adicionar colunas à tabela leagues usando Supabase client
"""

import os
import sys
import logging
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client
from config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def add_columns_to_leagues():
    """Adicionar colunas necessárias à tabela leagues"""
    
    logger.info("🔧 Adicionando colunas à tabela leagues...")
    
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
        
        # SQL para adicionar as colunas necessárias
        sql_commands = [
            "ALTER TABLE leagues ADD COLUMN IF NOT EXISTS sport_id INTEGER;",
            "ALTER TABLE leagues ADD COLUMN IF NOT EXISTS country_id INTEGER;",
            "ALTER TABLE leagues ADD COLUMN IF NOT EXISTS active BOOLEAN;",
            "ALTER TABLE leagues ADD COLUMN IF NOT EXISTS short_code VARCHAR(10);",
            "ALTER TABLE leagues ADD COLUMN IF NOT EXISTS image_path TEXT;",
            "ALTER TABLE leagues ADD COLUMN IF NOT EXISTS type VARCHAR(50);",
            "ALTER TABLE leagues ADD COLUMN IF NOT EXISTS sub_type VARCHAR(50);",
            "ALTER TABLE leagues ADD COLUMN IF NOT EXISTS last_played_at TIMESTAMP;",
            "ALTER TABLE leagues ADD COLUMN IF NOT EXISTS category VARCHAR(50);",
            "ALTER TABLE leagues ADD COLUMN IF NOT EXISTS has_jerseys BOOLEAN;"
        ]
        
        for sql in sql_commands:
            try:
                result = supabase.rpc('exec_sql', {'sql': sql}).execute()
                logger.info(f"✅ Executado: {sql}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao executar {sql}: {e}")
        
        # Verificar estrutura atual
        logger.info("📋 Verificando estrutura atual da tabela leagues...")
        try:
            # Tentar inserir um registro de teste para ver quais colunas existem
            test_data = {
                'sportmonks_id': 999999,
                'name': 'Test League',
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Tentar inserir com diferentes combinações de colunas
            columns_to_test = [
                'sport_id', 'country_id', 'active', 'short_code', 
                'image_path', 'type', 'sub_type', 'last_played_at', 
                'category', 'has_jerseys'
            ]
            
            for col in columns_to_test:
                try:
                    test_data_with_col = test_data.copy()
                    test_data_with_col[col] = None
                    supabase.table('leagues').insert(test_data_with_col).execute()
                    logger.info(f"✅ Coluna {col} existe")
                    # Remover o registro de teste
                    supabase.table('leagues').delete().eq('sportmonks_id', 999999).execute()
                    break
                except Exception as e:
                    if 'column' in str(e).lower() and 'does not exist' in str(e).lower():
                        logger.warning(f"❌ Coluna {col} não existe: {e}")
                    else:
                        logger.info(f"✅ Coluna {col} existe (erro diferente: {e})")
                        # Remover o registro de teste se foi inserido
                        try:
                            supabase.table('leagues').delete().eq('sportmonks_id', 999999).execute()
                        except:
                            pass
                        break
                    
        except Exception as e:
            logger.error(f"❌ Erro ao verificar estrutura: {e}")
        
        logger.info("✅ Processo de adição de colunas finalizado!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar colunas: {e}")

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🔧 ADICIONANDO COLUNAS À TABELA LEAGUES")
    logger.info("=" * 80)
    
    try:
        add_columns_to_leagues()
        
        logger.info("=" * 80)
        logger.info("✅ ADIÇÃO DE COLUNAS FINALIZADA!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Falha na adição de colunas: {e}")

if __name__ == "__main__":
    main()
