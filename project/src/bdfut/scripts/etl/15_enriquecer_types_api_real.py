#!/usr/bin/env python3
"""
Script para enriquecer a tabela types usando chamada direta da Sportmonks API
com token do .env
"""

import os
import sys
import requests
import logging
from datetime import datetime
from typing import List, Dict, Any

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

def get_types_from_api():
    """Buscar types diretamente da API Sportmonks"""
    
    try:
        config = Config()
        api_token = config.SPORTMONKS_API_KEY
        
        if not api_token:
            logger.error("❌ Token da Sportmonks API não encontrado no .env")
            return []
        
        # URL da API Sportmonks para types
        url = f"https://api.sportmonks.com/v3/core/types?api_token={api_token}&include="
        
        logger.info(f"🌐 Fazendo requisição para: {url}")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            types = data.get('data', [])
            logger.info(f"✅ {len(types)} types encontrados na API")
            return types
        else:
            logger.error(f"❌ Erro na API: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar types da API: {e}")
        return []

def enrich_types_table():
    """Enriquecer tabela types com dados reais da Sportmonks API"""
    
    logger.info("🚀 Enriquecendo tabela types com dados reais da Sportmonks API...")
    
    # Inicializar cliente Supabase
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
        return
    
    # Buscar types da API
    types_from_api = get_types_from_api()
    
    if not types_from_api:
        logger.error("❌ Nenhum type encontrado na API")
        return
    
    # Preparar dados para inserção
    types_to_save = []
    for type_item in types_from_api:
        type_data = {
            'sportmonks_id': type_item.get('id'),
            'name': type_item.get('name'),
            'developer_name': type_item.get('developer_name'),
            'created_at': datetime.utcnow().isoformat()
        }
        types_to_save.append(type_data)
    
    logger.info(f"📊 {len(types_to_save)} types preparados para inserção")
    
    # Salvar types um por vez para evitar conflitos
    saved_count = 0
    skipped_count = 0
    error_count = 0
    
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
                error_count += 1
                logger.warning(f"⚠️ Erro ao salvar type '{type_data['name']}': {e}")
    
    logger.info(f"✅ {saved_count} types novos salvos")
    logger.info(f"⏭️ {skipped_count} types já existiam")
    logger.info(f"❌ {error_count} types com erro")
    
    # Relatório final
    logger.info("=" * 80)
    logger.info("📊 RELATÓRIO FINAL - TABELA TYPES ENRIQUECIDA COM API REAL")
    logger.info("=" * 80)
    
    try:
        response = supabase.table('types').select('*', count='exact').execute()
        total_count = response.count
        logger.info(f"📊 Total de types na tabela: {total_count}")
        
        # Mostrar alguns examples
        logger.info("📋 Exemplos de types da API:")
        examples = supabase.table('types').select('sportmonks_id,name,developer_name').limit(15).execute()
        for example in examples.data:
            logger.info(f"   • ID {example['sportmonks_id']}: {example['name']} ({example['developer_name']})")
        
        # Mostrar estatísticas por categoria
        logger.info("\n📈 Estatísticas por categoria:")
        
        # Eventos de gol
        goal_types = supabase.table('types').select('sportmonks_id,name').in_('sportmonks_id', [14,15,16,17]).execute()
        logger.info(f"⚽ Eventos de Gol: {len(goal_types.data)} types")
        
        # Cartões
        card_types = supabase.table('types').select('sportmonks_id,name').in_('sportmonks_id', [19,20,21]).execute()
        logger.info(f"🟨🟥 Cartões: {len(card_types.data)} types")
        
        # Substituições
        sub_types = supabase.table('types').select('sportmonks_id,name').in_('sportmonks_id', [18,83,84]).execute()
        logger.info(f"🔄 Substituições: {len(sub_types.data)} types")
        
        # Estatísticas avançadas
        advanced_types = supabase.table('types').select('sportmonks_id,name').in_('sportmonks_id', [81,82,85,86]).execute()
        logger.info(f"📈 Estatísticas Avançadas: {len(advanced_types.data)} types")
        
        # Mostrar range de IDs
        min_id = min([t['sportmonks_id'] for t in examples.data])
        max_id = max([t['sportmonks_id'] for t in examples.data])
        logger.info(f"🔢 Range de IDs: {min_id} - {max_id}")
                
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")
    
    logger.info("=" * 80)
    logger.info("✅ ENRIQUECIMENTO DA TABELA TYPES COM API REAL CONCLUÍDO!")
    logger.info("=" * 80)

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 ENRIQUECENDO TABELA TYPES COM API SPORTMONKS REAL")
    logger.info("=" * 80)
    
    enrich_types_table()

if __name__ == "__main__":
    main()
