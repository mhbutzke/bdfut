#!/usr/bin/env python3
"""
Script para criar tabelas que estão faltando no Supabase
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

def create_tables():
    """Criar tabelas que estão faltando"""
    
    logger.info("🚀 Criando tabelas que estão faltando...")
    
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente: {e}")
        return
    
    # SQL para criar as tabelas
    tables_sql = [
        # Venues
        """
        CREATE TABLE IF NOT EXISTS venues (
            id SERIAL PRIMARY KEY,
            sportmonks_id INTEGER UNIQUE,
            name VARCHAR(255) NOT NULL,
            city VARCHAR(255),
            capacity INTEGER,
            surface VARCHAR(100),
            country VARCHAR(100),
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Referees
        """
        CREATE TABLE IF NOT EXISTS referees (
            id SERIAL PRIMARY KEY,
            sportmonks_id INTEGER UNIQUE,
            name VARCHAR(255) NOT NULL,
            common_name VARCHAR(255),
            firstname VARCHAR(255),
            lastname VARCHAR(255),
            nationality VARCHAR(100),
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Players
        """
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            sportmonks_id INTEGER UNIQUE,
            name VARCHAR(255) NOT NULL,
            common_name VARCHAR(255),
            firstname VARCHAR(255),
            lastname VARCHAR(255),
            nationality VARCHAR(100),
            position_id INTEGER,
            position_name VARCHAR(100),
            date_of_birth DATE,
            height INTEGER,
            weight INTEGER,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Coaches
        """
        CREATE TABLE IF NOT EXISTS coaches (
            id SERIAL PRIMARY KEY,
            sportmonks_id INTEGER UNIQUE,
            name VARCHAR(255) NOT NULL,
            common_name VARCHAR(255),
            firstname VARCHAR(255),
            lastname VARCHAR(255),
            nationality VARCHAR(100),
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # States
        """
        CREATE TABLE IF NOT EXISTS states (
            id SERIAL PRIMARY KEY,
            sportmonks_id INTEGER UNIQUE,
            name VARCHAR(255) NOT NULL,
            short_name VARCHAR(10),
            developer_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Types
        """
        CREATE TABLE IF NOT EXISTS types (
            id SERIAL PRIMARY KEY,
            sportmonks_id INTEGER UNIQUE,
            name VARCHAR(255) NOT NULL,
            developer_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Countries
        """
        CREATE TABLE IF NOT EXISTS countries (
            id SERIAL PRIMARY KEY,
            sportmonks_id INTEGER UNIQUE,
            name VARCHAR(255) NOT NULL,
            code VARCHAR(10),
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]
    
    # Executar cada SQL
    for i, sql in enumerate(tables_sql, 1):
        try:
            logger.info(f"📝 Executando SQL {i}/7...")
            supabase.rpc('exec_sql', {'sql': sql}).execute()
            logger.info(f"✅ Tabela {i} criada com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabela {i}: {e}")
    
    logger.info("🎉 Todas as tabelas foram criadas!")

if __name__ == "__main__":
    create_tables()
