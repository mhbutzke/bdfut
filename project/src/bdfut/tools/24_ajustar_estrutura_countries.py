#!/usr/bin/env python3
"""
Script para ajustar a estrutura da tabela countries para corresponder exatamente à Sportmonks API
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

def ajustar_estrutura_countries():
    """Ajustar estrutura da tabela countries para corresponder à Sportmonks API"""
    
    logger.info("🔧 Ajustando estrutura da tabela countries para corresponder à Sportmonks API...")
    
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
        
        # SQL para ajustar a estrutura da tabela countries
        sql_commands = [
            # Primeiro, vamos limpar a tabela existente e recriar com a estrutura correta
            "DROP TABLE IF EXISTS countries_backup;",
            "CREATE TABLE countries_backup AS SELECT * FROM countries;",
            
            # Dropar a tabela atual
            "DROP TABLE countries;",
            
            # Criar nova tabela com estrutura exata da Sportmonks API
            """
            CREATE TABLE countries (
                id SERIAL PRIMARY KEY,
                sportmonks_id INTEGER UNIQUE,
                continent_id INTEGER,
                name VARCHAR(255) NOT NULL,
                official_name VARCHAR(255),
                fifa_name VARCHAR(255),
                iso2 VARCHAR(2),
                iso3 VARCHAR(3),
                latitude DECIMAL(10,8),
                longitude DECIMAL(11,8),
                borders TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Criar índices para melhor performance
            "CREATE INDEX idx_countries_sportmonks_id ON countries(sportmonks_id);",
            "CREATE INDEX idx_countries_continent_id ON countries(continent_id);",
            "CREATE INDEX idx_countries_iso2 ON countries(iso2);",
            "CREATE INDEX idx_countries_iso3 ON countries(iso3);",
            "CREATE INDEX idx_countries_fifa_name ON countries(fifa_name);",
            
            # Comentários para documentação
            "COMMENT ON COLUMN countries.sportmonks_id IS 'ID único da Sportmonks API';",
            "COMMENT ON COLUMN countries.continent_id IS 'ID do continente';",
            "COMMENT ON COLUMN countries.name IS 'Nome do país';",
            "COMMENT ON COLUMN countries.official_name IS 'Nome oficial do país';",
            "COMMENT ON COLUMN countries.fifa_name IS 'Nome usado pela FIFA';",
            "COMMENT ON COLUMN countries.iso2 IS 'Código ISO 3166-1 alpha-2';",
            "COMMENT ON COLUMN countries.iso3 IS 'Código ISO 3166-1 alpha-3';",
            "COMMENT ON COLUMN countries.latitude IS 'Latitude do país';",
            "COMMENT ON COLUMN countries.longitude IS 'Longitude do país';",
            "COMMENT ON COLUMN countries.borders IS 'Países que fazem fronteira';",
            "COMMENT ON COLUMN countries.image_path IS 'Caminho da imagem da bandeira';",
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
            WHERE table_name = 'countries' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        logger.info("📊 Estrutura final da tabela countries:")
        logger.info("=" * 60)
        for col in columns:
            logger.info(f"   • {col[0]} ({col[1]}) - Nullable: {col[2]}")
        
        logger.info("=" * 60)
        logger.info("✅ ESTRUTURA DA TABELA COUNTRIES AJUSTADA COM SUCESSO!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Erro ao ajustar estrutura: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("🔌 Conexão fechada")

def main():
    """Função principal"""
    
    logger.info("=" * 60)
    logger.info("🔧 AJUSTANDO ESTRUTURA DA TABELA COUNTRIES")
    logger.info("=" * 60)
    
    ajustar_estrutura_countries()

if __name__ == "__main__":
    main()
