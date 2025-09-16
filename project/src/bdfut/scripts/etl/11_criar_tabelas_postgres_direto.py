#!/usr/bin/env python3
"""
Script para criar tabelas conectando diretamente ao PostgreSQL
"""

import os
import sys
import logging
from datetime import datetime
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_tables_direct_postgres():
    """Criar tabelas conectando diretamente ao PostgreSQL"""
    
    logger.info("🔨 Conectando diretamente ao PostgreSQL...")
    
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
        conn = psycopg2.connect(**connection_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        logger.info("✅ Conectado ao PostgreSQL com sucesso!")
        
        # SQL para criar as tabelas
        create_tables_sql = """
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
        
        # Executar SQL
        logger.info("📝 Executando SQL para criar tabelas...")
        cursor.execute(create_tables_sql)
        
        logger.info("✅ Todas as tabelas foram criadas com sucesso!")
        
        # Verificar se as tabelas foram criadas
        logger.info("🔍 Verificando tabelas criadas...")
        
        tables_to_check = ['venues', 'referees', 'players', 'coaches', 'states', 'types', 'countries']
        
        for table in tables_to_check:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table}'
                );
            """)
            exists = cursor.fetchone()[0]
            if exists:
                logger.info(f"✅ Tabela {table} criada com sucesso")
            else:
                logger.error(f"❌ Tabela {table} não foi criada")
        
        # Fechar conexão
        cursor.close()
        conn.close()
        
        logger.info("🎉 Processo concluído com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao conectar/criar tabelas: {e}")
        return False

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 CRIANDO TABELAS VIA CONEXÃO DIRETA POSTGRESQL")
    logger.info("=" * 80)
    
    success = create_tables_direct_postgres()
    
    if success:
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
