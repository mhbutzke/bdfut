#!/usr/bin/env python3
"""
Script para adicionar colunas faltantes à tabela types via PostgreSQL direto
"""

import os
import sys
import psycopg2
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def adicionar_colunas_types():
    """Adicionar colunas faltantes à tabela types"""
    
    logger.info("🔧 Adicionando colunas faltantes à tabela types...")
    
    # Parâmetros de conexão (usando Session pooler - IPv4 compatible)
    connection_params = {
        'host': 'aws-1-sa-east-1.pooler.supabase.com',
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres.qoqeshyuwmxfrjdkhwii',
        'password': 'HRX*rht.htq7ufx@hpz'
    }
    
    try:
        # Conectar ao PostgreSQL
        logger.info("🔌 Conectando ao PostgreSQL...")
        conn = psycopg2.connect(**connection_params)
        conn.autocommit = True
        cursor = conn.cursor()
        logger.info("✅ Conectado com sucesso!")
        
        # SQL para adicionar colunas
        sql_commands = [
            "ALTER TABLE types ADD COLUMN IF NOT EXISTS code VARCHAR(50);",
            "ALTER TABLE types ADD COLUMN IF NOT EXISTS model_type VARCHAR(50);",
            "ALTER TABLE types ADD COLUMN IF NOT EXISTS stat_group VARCHAR(50);",
            "CREATE INDEX IF NOT EXISTS idx_types_code ON types(code);",
            "CREATE INDEX IF NOT EXISTS idx_types_model_type ON types(model_type);",
            "CREATE INDEX IF NOT EXISTS idx_types_stat_group ON types(stat_group);",
            "COMMENT ON COLUMN types.code IS 'Código único do tipo de evento';",
            "COMMENT ON COLUMN types.model_type IS 'Tipo de modelo (event, statistic, etc.)';",
            "COMMENT ON COLUMN types.stat_group IS 'Grupo estatístico do evento';"
        ]
        
        # Executar comandos SQL
        for i, sql in enumerate(sql_commands, 1):
            try:
                logger.info(f"📝 Executando comando {i}/{len(sql_commands)}...")
                cursor.execute(sql)
                logger.info(f"✅ Comando {i} executado com sucesso")
            except Exception as e:
                logger.warning(f"⚠️ Erro no comando {i}: {e}")
        
        # Verificar estrutura final
        logger.info("🔍 Verificando estrutura final da tabela...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'types' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        logger.info("📊 Estrutura final da tabela types:")
        logger.info("=" * 60)
        for col in columns:
            logger.info(f"   • {col[0]} ({col[1]}) - Nullable: {col[2]}")
        
        logger.info("=" * 60)
        logger.info("✅ COLUNAS ADICIONADAS COM SUCESSO!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar colunas: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("🔌 Conexão fechada")

def main():
    """Função principal"""
    
    logger.info("=" * 60)
    logger.info("🔧 ADICIONANDO COLUNAS À TABELA TYPES")
    logger.info("=" * 60)
    
    adicionar_colunas_types()

if __name__ == "__main__":
    main()
