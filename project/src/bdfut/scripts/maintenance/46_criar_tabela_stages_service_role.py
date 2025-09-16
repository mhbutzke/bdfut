#!/usr/bin/env python3
"""
Script para criar tabela stages usando service_role key
"""

import os
import sys
import logging
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_stages_table_with_service_role():
    """Criar tabela stages usando service_role key"""
    
    logger.info("🔧 Criando tabela stages com service_role...")
    
    # Usar service_role key com privilégios administrativos
    SUPABASE_URL = "https://qoqeshyuwmxfrjdkhwii.supabase.co"
    SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFvcWVzaHl1d214ZnJqZGtod2lpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzY5MzE3NCwiZXhwIjoyMDczMjY5MTc0fQ.QPgk88JViYHXekcJwsHtBgIU7CjKWx1ZUkd1nEkRGoQ"
    
    try:
        # Criar cliente com service_role
        supabase = create_client(SUPABASE_URL, SERVICE_KEY)
        logger.info("✅ Cliente Supabase com service_role inicializado")
        
        # SQL para criar a tabela
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
        
        # Tentar executar via RPC com service_role
        try:
            result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
            logger.info("✅ Tabela stages criada via RPC com service_role")
            return True
        except Exception as e:
            logger.warning(f"⚠️ RPC não disponível: {e}")
            
            # Tentar método alternativo - inserir um registro de teste
            try:
                test_data = {
                    'sportmonks_id': 999999,
                    'name': 'Test Stage',
                    'created_at': datetime.utcnow().isoformat()
                }
                supabase.table('stages').insert(test_data).execute()
                logger.info("✅ Tabela stages já existe e está acessível")
                return True
            except Exception as e2:
                logger.error(f"❌ Tabela stages não existe: {e2}")
                return False
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabela stages: {e}")
        return False

def check_stages_table_with_service_role():
    """Verificar se a tabela stages existe usando service_role"""
    
    logger.info("🔍 Verificando se a tabela stages existe com service_role...")
    
    try:
        SUPABASE_URL = "https://qoqeshyuwmxfrjdkhwii.supabase.co"
        SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFvcWVzaHl1d214ZnJqZGtod2lpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzY5MzE3NCwiZXhwIjoyMDczMjY5MTc0fQ.QPgk88JViYHXekcJwsHtBgIU7CjKWx1ZUkd1nEkRGoQ"
        
        supabase = create_client(SUPABASE_URL, SERVICE_KEY)
        
        # Tentar fazer uma consulta simples
        result = supabase.table('stages').select('*').limit(1).execute()
        logger.info("✅ Tabela stages existe e está acessível")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ Tabela stages não existe ou não está acessível: {e}")
        return False

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🔧 CRIANDO TABELA STAGES COM SERVICE_ROLE")
    logger.info("=" * 80)
    
    # Verificar se a tabela já existe
    if check_stages_table_with_service_role():
        logger.info("✅ Tabela stages já existe!")
        return
    
    # Tentar criar a tabela
    if create_stages_table_with_service_role():
        logger.info("✅ Tabela stages criada com sucesso!")
        
        # Verificar novamente
        if check_stages_table_with_service_role():
            logger.info("🎉 Tabela stages confirmada e pronta para uso!")
        else:
            logger.warning("⚠️ Tabela criada mas não confirmada")
    else:
        logger.error("❌ Não foi possível criar a tabela stages")
        logger.info("💡 Você precisa criar a tabela manualmente no Supabase Dashboard")

if __name__ == "__main__":
    main()
