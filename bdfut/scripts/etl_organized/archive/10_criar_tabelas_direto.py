#!/usr/bin/env python3
"""
Script para criar tabelas usando conexão direta ao PostgreSQL
"""

import os
import sys
import logging
from datetime import datetime
import requests
import json

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_tables_via_rest_api():
    """Criar tabelas usando REST API diretamente com service role"""
    
    logger.info("🔨 Criando tabelas via REST API com Service Role...")
    
    try:
        config = Config()
        
        # Headers com service role key
        headers = {
            'apikey': config.SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {config.SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        # URL base
        base_url = config.SUPABASE_URL.rstrip('/')
        
        # SQL para criar as tabelas
        sql_commands = [
            """CREATE TABLE IF NOT EXISTS venues (
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
            )""",
            
            """CREATE TABLE IF NOT EXISTS referees (
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
            )""",
            
            """CREATE TABLE IF NOT EXISTS players (
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
            )""",
            
            """CREATE TABLE IF NOT EXISTS coaches (
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
            )""",
            
            """CREATE TABLE IF NOT EXISTS states (
                id SERIAL PRIMARY KEY,
                sportmonks_id INTEGER UNIQUE,
                name VARCHAR(255) NOT NULL,
                short_name VARCHAR(10),
                developer_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS types (
                id SERIAL PRIMARY KEY,
                sportmonks_id INTEGER UNIQUE,
                name VARCHAR(255) NOT NULL,
                developer_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS countries (
                id SERIAL PRIMARY KEY,
                sportmonks_id INTEGER UNIQUE,
                name VARCHAR(255) NOT NULL,
                code VARCHAR(10),
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        ]
        
        # Tentar executar cada comando
        for i, sql in enumerate(sql_commands, 1):
            table_name = sql.split('CREATE TABLE IF NOT EXISTS ')[1].split(' ')[0]
            logger.info(f"📝 Criando tabela {table_name} ({i}/{len(sql_commands)})...")
            
            # Tentar via RPC (se existir)
            try:
                rpc_url = f"{base_url}/rest/v1/rpc/exec_sql"
                rpc_data = {'sql': sql}
                
                response = requests.post(rpc_url, headers=headers, json=rpc_data, timeout=30)
                
                if response.status_code == 200:
                    logger.info(f"✅ Tabela {table_name} criada via RPC")
                    continue
                else:
                    logger.warning(f"⚠️ RPC falhou para {table_name}: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ RPC não disponível para {table_name}: {e}")
            
            # Tentar via SQL direto (provavelmente não funcionará)
            try:
                sql_url = f"{base_url}/rest/v1/rpc/query"
                sql_data = {'query': sql}
                
                response = requests.post(sql_url, headers=headers, json=sql_data, timeout=30)
                
                if response.status_code == 200:
                    logger.info(f"✅ Tabela {table_name} criada via SQL direto")
                    continue
                else:
                    logger.warning(f"⚠️ SQL direto falhou para {table_name}: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ SQL direto não disponível para {table_name}: {e}")
        
        logger.warning("⚠️ Não foi possível criar tabelas automaticamente")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return False

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 TENTANDO CRIAR TABELAS VIA REST API")
    logger.info("=" * 80)
    
    success = create_tables_via_rest_api()
    
    if not success:
        logger.info("=" * 80)
        logger.info("📝 SOLUÇÃO MANUAL NECESSÁRIA")
        logger.info("=" * 80)
        logger.info("🔗 Acesse: https://supabase.com/dashboard/project/qoqeshyuwmxfrjdkhwii/sql")
        logger.info("📋 Cole e execute o conteúdo do arquivo: create_tables.sql")
        logger.info("")
        logger.info("🎯 APÓS EXECUTAR O SQL MANUALMENTE:")
        logger.info("   → Execute: python3 08_coletar_dados_finais.py")
        logger.info("   Para popular as novas tabelas com dados")
        logger.info("=" * 80)

if __name__ == "__main__":
    main()
