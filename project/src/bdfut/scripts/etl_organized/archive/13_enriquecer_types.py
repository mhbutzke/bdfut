#!/usr/bin/env python3
"""
Script para enriquecer a tabela types com dados completos da Sportmonks API
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Any

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.sportmonks_client import SportmonksClient
from supabase import create_client
from config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def enrich_types_table():
    """Enriquecer tabela types com dados da Sportmonks API"""
    
    logger.info("🚀 Enriquecendo tabela types com dados da Sportmonks API...")
    
    # Inicializar clientes
    try:
        config = Config()
        sportmonks = SportmonksClient()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Clientes inicializados com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar clientes: {e}")
        return
    
    try:
        # Coletar todos os types da API
        logger.info("📊 Coletando types da Sportmonks API...")
        types = sportmonks.get_types()
        
        logger.info(f"📊 {len(types)} types encontrados na API")
        
        # Preparar dados para inserção
        types_to_save = []
        for type_item in types:
            type_data = {
                'sportmonks_id': type_item.get('id'),
                'name': type_item.get('name'),
                'developer_name': type_item.get('developer_name'),
                'created_at': datetime.utcnow().isoformat()
            }
            types_to_save.append(type_data)
        
        # Salvar types um por vez para evitar conflitos
        saved_count = 0
        skipped_count = 0
        
        for type_data in types_to_save:
            try:
                supabase.table('types').insert(type_data).execute()
                saved_count += 1
                logger.info(f"✅ Type salvo: {type_data['name']} (ID: {type_data['sportmonks_id']})")
            except Exception as e:
                if 'duplicate key' in str(e).lower() or 'unique constraint' in str(e).lower():
                    skipped_count += 1
                    logger.info(f"⏭️ Type já existe: {type_data['name']} (ID: {type_data['sportmonks_id']})")
                else:
                    logger.warning(f"⚠️ Erro ao salvar type '{type_data['name']}': {e}")
        
        logger.info(f"✅ {saved_count} types novos salvos")
        logger.info(f"⏭️ {skipped_count} types já existiam")
        
        # Relatório final
        logger.info("=" * 80)
        logger.info("📊 RELATÓRIO FINAL - TABELA TYPES")
        logger.info("=" * 80)
        
        try:
            response = supabase.table('types').select('*', count='exact').execute()
            total_count = response.count
            logger.info(f"📊 Total de types na tabela: {total_count}")
            
            # Mostrar alguns examples
            logger.info("📋 Exemplos de types salvos:")
            examples = supabase.table('types').select('sportmonks_id,name,developer_name').limit(10).execute()
            for example in examples.data:
                logger.info(f"   • ID {example['sportmonks_id']}: {example['name']} ({example['developer_name']})")
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ ENRIQUECIMENTO DA TABELA TYPES CONCLUÍDO!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erro ao enriquecer types: {e}")

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 ENRIQUECENDO TABELA TYPES")
    logger.info("=" * 80)
    
    enrich_types_table()

if __name__ == "__main__":
    main()
