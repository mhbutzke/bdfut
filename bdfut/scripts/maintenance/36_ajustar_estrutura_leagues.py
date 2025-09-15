#!/usr/bin/env python3
"""
Script para ajustar a estrutura da tabela leagues conforme especificado pelo usuário
"""

import os
import sys
import psycopg2
import logging
from typing import Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def adjust_leagues_structure():
    """Ajustar estrutura da tabela leagues conforme especificado"""
    
    # Credenciais do PostgreSQL (Supabase) - usando Session pooler
    DB_CONFIG = {
        'host': 'aws-0-us-west-1.pooler.supabase.com',
        'port': 6543,
        'database': 'postgres',
        'user': 'postgres.qoqeshyuwmxfrjdkhwii',
        'password': 'HRX*rht.htq7ufx@hpz'
    }
    
    logger.info("🔧 Ajustando estrutura da tabela leagues...")
    
    try:
        # Conectar ao PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        logger.info("✅ Conectado ao PostgreSQL com sucesso")
        
        # Verificar estrutura atual
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'leagues' 
            ORDER BY ordinal_position;
        """)
        
        current_columns = cursor.fetchall()
        logger.info("📋 Estrutura atual da tabela leagues:")
        for col in current_columns:
            logger.info(f"   • {col[0]} ({col[1]})")
        
        # Remover colunas desnecessárias (manter apenas as especificadas)
        columns_to_keep = [
            'id', 'sportmonks_id', 'created_at', 'updated_at',  # Colunas básicas
            'sport_id', 'country_id', 'name', 'active', 'short_code', 
            'image_path', 'type', 'sub_type', 'last_played_at', 
            'category', 'has_jerseys'
        ]
        
        # Obter todas as colunas atuais
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'leagues';
        """)
        
        all_columns = [row[0] for row in cursor.fetchall()]
        
        # Remover colunas que não estão na lista de manter
        columns_to_drop = [col for col in all_columns if col not in columns_to_keep]
        
        if columns_to_drop:
            logger.info(f"🗑️ Removendo colunas desnecessárias: {columns_to_drop}")
            for col in columns_to_drop:
                try:
                    cursor.execute(f"ALTER TABLE leagues DROP COLUMN IF EXISTS {col};")
                    logger.info(f"   ✅ Coluna {col} removida")
                except Exception as e:
                    logger.warning(f"   ⚠️ Erro ao remover coluna {col}: {e}")
        
        # Adicionar colunas especificadas se não existirem
        new_columns = {
            'sport_id': 'INTEGER',
            'country_id': 'INTEGER', 
            'name': 'VARCHAR(255)',
            'active': 'BOOLEAN',
            'short_code': 'VARCHAR(10)',
            'image_path': 'TEXT',
            'type': 'VARCHAR(50)',
            'sub_type': 'VARCHAR(50)',
            'last_played_at': 'TIMESTAMP',
            'category': 'VARCHAR(50)',
            'has_jerseys': 'BOOLEAN'
        }
        
        logger.info("➕ Adicionando/verificando colunas especificadas...")
        for col_name, col_type in new_columns.items():
            try:
                cursor.execute(f"""
                    DO $$ BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                     WHERE table_name = 'leagues' AND column_name = '{col_name}') THEN
                            ALTER TABLE leagues ADD COLUMN {col_name} {col_type};
                        END IF;
                    END $$;
                """)
                logger.info(f"   ✅ Coluna {col_name} ({col_type}) verificada/adicionada")
            except Exception as e:
                logger.warning(f"   ⚠️ Erro ao verificar/adicionar coluna {col_name}: {e}")
        
        # Verificar estrutura final
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'leagues' 
            ORDER BY ordinal_position;
        """)
        
        final_columns = cursor.fetchall()
        logger.info("📋 Estrutura final da tabela leagues:")
        for col in final_columns:
            logger.info(f"   • {col[0]} ({col[1]})")
        
        # Verificar se todas as colunas especificadas estão presentes
        final_column_names = [col[0] for col in final_columns]
        required_columns = ['sport_id', 'country_id', 'name', 'active', 'short_code', 
                           'image_path', 'type', 'sub_type', 'last_played_at', 
                           'category', 'has_jerseys']
        
        missing_columns = [col for col in required_columns if col not in final_column_names]
        if missing_columns:
            logger.error(f"❌ Colunas faltando: {missing_columns}")
        else:
            logger.info("✅ Todas as colunas especificadas estão presentes!")
        
        cursor.close()
        conn.close()
        logger.info("✅ Estrutura da tabela leagues ajustada com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao ajustar estrutura: {e}")
        raise

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🔧 AJUSTANDO ESTRUTURA DA TABELA LEAGUES")
    logger.info("=" * 80)
    
    try:
        adjust_leagues_structure()
        
        logger.info("=" * 80)
        logger.info("✅ AJUSTE DE ESTRUTURA FINALIZADO!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Falha no ajuste de estrutura: {e}")

if __name__ == "__main__":
    main()
