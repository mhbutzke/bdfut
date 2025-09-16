#!/usr/bin/env python3
"""
Script para criar tabelas usando Service Role Key (privilégios completos)
"""

import os
import sys
import logging
from datetime import datetime

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

def create_tables_with_service_role():
    """Criar tabelas usando Service Role Key"""
    
    logger.info("🔨 Criando tabelas com Service Role Key...")
    
    try:
        config = Config()
        # Usar service_role key que tem privilégios completos
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
        logger.info("✅ Cliente Supabase com Service Role inicializado")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente: {e}")
        return False
    
    # SQL para criar as tabelas
    create_sql = """
    -- Criar tabela venues
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

    -- Criar tabela referees
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

    -- Criar tabela players
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

    -- Criar tabela coaches
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

    -- Criar tabela states
    CREATE TABLE IF NOT EXISTS states (
        id SERIAL PRIMARY KEY,
        sportmonks_id INTEGER UNIQUE,
        name VARCHAR(255) NOT NULL,
        short_name VARCHAR(10),
        developer_name VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Criar tabela types
    CREATE TABLE IF NOT EXISTS types (
        id SERIAL PRIMARY KEY,
        sportmonks_id INTEGER UNIQUE,
        name VARCHAR(255) NOT NULL,
        developer_name VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Criar tabela countries
    CREATE TABLE IF NOT EXISTS countries (
        id SERIAL PRIMARY KEY,
        sportmonks_id INTEGER UNIQUE,
        name VARCHAR(255) NOT NULL,
        code VARCHAR(10),
        image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Adicionar índices para melhor performance
    CREATE INDEX IF NOT EXISTS idx_venues_name ON venues(name);
    CREATE INDEX IF NOT EXISTS idx_referees_name ON referees(name);
    CREATE INDEX IF NOT EXISTS idx_players_name ON players(name);
    CREATE INDEX IF NOT EXISTS idx_coaches_name ON coaches(name);
    CREATE INDEX IF NOT EXISTS idx_states_name ON states(name);
    CREATE INDEX IF NOT EXISTS idx_types_name ON types(name);
    CREATE INDEX IF NOT EXISTS idx_countries_name ON countries(name);
    """
    
    try:
        # Executar SQL via RPC
        result = supabase.rpc('exec_sql', {'sql': create_sql}).execute()
        logger.info("✅ Tabelas criadas com sucesso!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao executar SQL: {e}")
        
        # Tentar método alternativo
        try:
            # Dividir em comandos menores
            sql_commands = create_sql.split(';')
            for i, cmd in enumerate(sql_commands):
                cmd = cmd.strip()
                if cmd and not cmd.startswith('--'):
                    logger.info(f"📝 Executando comando {i+1}/{len(sql_commands)}...")
                    supabase.rpc('exec_sql', {'sql': cmd}).execute()
            
            logger.info("✅ Tabelas criadas com sucesso (método alternativo)!")
            return True
        except Exception as e2:
            logger.error(f"❌ Erro no método alternativo: {e2}")
            return False

def verify_tables_created():
    """Verificar se as tabelas foram criadas"""
    
    logger.info("🔍 Verificando se as tabelas foram criadas...")
    
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
        
        required_tables = ['venues', 'referees', 'players', 'coaches', 'states', 'types', 'countries']
        
        for table in required_tables:
            try:
                response = supabase.table(table).select('*', count='exact').limit(1).execute()
                logger.info(f"✅ Tabela {table} criada com sucesso")
            except Exception as e:
                logger.error(f"❌ Tabela {table} não foi criada: {e}")
                return False
        
        logger.info("🎉 Todas as tabelas foram criadas com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar tabelas: {e}")
        return False

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 CRIANDO TABELAS COM SERVICE ROLE KEY")
    logger.info("=" * 80)
    
    # Criar tabelas
    success = create_tables_with_service_role()
    
    if success:
        # Verificar se foram criadas
        verify_tables_created()
        
        logger.info("=" * 80)
        logger.info("🎯 PRÓXIMO PASSO:")
        logger.info("   → Execute: python3 08_coletar_dados_finais.py")
        logger.info("   Para popular as novas tabelas com dados")
        logger.info("=" * 80)
    else:
        logger.error("❌ Falha ao criar tabelas")
        logger.info("📝 Execute manualmente o SQL no Supabase SQL Editor:")
        logger.info("🔗 https://supabase.com/dashboard/project/qoqeshyuwmxfrjdkhwii/sql")

if __name__ == "__main__":
    main()
