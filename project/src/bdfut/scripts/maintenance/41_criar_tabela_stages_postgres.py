#!/usr/bin/env python3
"""
Script para criar tabela stages usando PostgreSQL direto
"""

import os
import sys
import psycopg2
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_stages_table_postgres():
    """Criar tabela stages usando PostgreSQL direto"""
    
    # Credenciais do PostgreSQL (Supabase) - usando Session pooler conforme SUPABASE.md
    DB_CONFIG = {
        'host': 'aws-0-us-west-1.pooler.supabase.com',
        'port': 6543,
        'database': 'postgres',
        'user': 'postgres.qoqeshyuwmxfrjdkhwii',
        'password': 'HRX*rht.htq7ufx@hpz'
    }
    
    logger.info("🔧 Criando tabela stages via PostgreSQL...")
    
    try:
        # Conectar ao PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        logger.info("✅ Conectado ao PostgreSQL com sucesso")
        
        # SQL para criar a tabela stages
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS stages (
            id SERIAL PRIMARY KEY,
            sportmonks_id INTEGER UNIQUE NOT NULL,
            sport_id INTEGER,
            country_id INTEGER,
            league_id INTEGER,
            season_id INTEGER,
            type_id INTEGER,
            name VARCHAR(255),
            short_code VARCHAR(10),
            sort_order INTEGER,
            finished BOOLEAN DEFAULT FALSE,
            is_current BOOLEAN DEFAULT FALSE,
            starting_at TIMESTAMP,
            ending_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Executar SQL
        cursor.execute(create_table_sql)
        logger.info("✅ Tabela stages criada com sucesso")
        
        # Verificar se a tabela foi criada
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'stages' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        logger.info("📋 Estrutura da tabela stages:")
        for col in columns:
            logger.info(f"   • {col[0]} ({col[1]})")
        
        # Verificar se há dados na tabela
        cursor.execute("SELECT COUNT(*) FROM stages;")
        count = cursor.fetchone()[0]
        logger.info(f"📊 Total de registros na tabela stages: {count}")
        
        cursor.close()
        conn.close()
        logger.info("✅ Tabela stages criada e verificada com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabela stages: {e}")

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🔧 CRIANDO TABELA STAGES VIA POSTGRESQL")
    logger.info("=" * 80)
    
    try:
        create_stages_table_postgres()
        
        logger.info("=" * 80)
        logger.info("✅ CRIAÇÃO DE TABELA FINALIZADA!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Falha na criação da tabela: {e}")

if __name__ == "__main__":
    main()
