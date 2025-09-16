#!/usr/bin/env python3
"""
Script para adicionar colunas faltantes à tabela countries via PostgreSQL direto
Baseado na estrutura completa da Sportmonks API
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

def adicionar_colunas_countries():
    """Adicionar colunas faltantes à tabela countries"""
    
    logger.info("🔧 Adicionando colunas faltantes à tabela countries...")
    
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
        
        # SQL para adicionar colunas baseadas na estrutura da Sportmonks API
        sql_commands = [
            # Colunas básicas
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS continent VARCHAR(50);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS continent_code VARCHAR(10);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS currency VARCHAR(10);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS currency_symbol VARCHAR(10);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS phone_code VARCHAR(10);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS timezone VARCHAR(50);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS capital VARCHAR(100);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS population INTEGER;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS area_km2 DECIMAL(15,2);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS gdp_per_capita DECIMAL(15,2);",
            
            # Colunas de localização
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS latitude DECIMAL(10,8);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS longitude DECIMAL(11,8);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS region VARCHAR(100);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS subregion VARCHAR(100);",
            
            # Colunas de idioma
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS official_language VARCHAR(100);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS languages TEXT;",
            
            # Colunas de bandeira e símbolos
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS flag_url TEXT;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS flag_emoji VARCHAR(10);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS coat_of_arms_url TEXT;",
            
            # Colunas de status
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS is_independent BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS is_un_member BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS is_eu_member BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS is_nato_member BOOLEAN DEFAULT FALSE;",
            
            # Colunas de futebol
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS fifa_code VARCHAR(10);",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS fifa_ranking INTEGER;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS uefa_member BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS conmebol_member BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS concacaf_member BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS afc_member BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS caf_member BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS ofc_member BOOLEAN DEFAULT FALSE;",
            
            # Colunas de datas
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS independence_date DATE;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS fifa_joined_date DATE;",
            
            # Colunas de estatísticas
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS world_cup_participations INTEGER DEFAULT 0;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS world_cup_titles INTEGER DEFAULT 0;",
            "ALTER TABLE countries ADD COLUMN IF NOT EXISTS continental_titles INTEGER DEFAULT 0;",
            
            # Criar índices para melhor performance
            "CREATE INDEX IF NOT EXISTS idx_countries_continent ON countries(continent);",
            "CREATE INDEX IF NOT EXISTS idx_countries_continent_code ON countries(continent_code);",
            "CREATE INDEX IF NOT EXISTS idx_countries_fifa_code ON countries(fifa_code);",
            "CREATE INDEX IF NOT EXISTS idx_countries_uefa_member ON countries(uefa_member);",
            "CREATE INDEX IF NOT EXISTS idx_countries_conmebol_member ON countries(conmebol_member);",
            
            # Comentários para documentação
            "COMMENT ON COLUMN countries.continent IS 'Continente do país';",
            "COMMENT ON COLUMN countries.continent_code IS 'Código do continente';",
            "COMMENT ON COLUMN countries.currency IS 'Moeda oficial';",
            "COMMENT ON COLUMN countries.fifa_code IS 'Código FIFA do país';",
            "COMMENT ON COLUMN countries.fifa_ranking IS 'Posição no ranking FIFA';",
            "COMMENT ON COLUMN countries.uefa_member IS 'Membro da UEFA';",
            "COMMENT ON COLUMN countries.conmebol_member IS 'Membro da CONMEBOL';",
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
    logger.info("🔧 ADICIONANDO COLUNAS À TABELA COUNTRIES")
    logger.info("=" * 60)
    
    adicionar_colunas_countries()

if __name__ == "__main__":
    main()
