#!/usr/bin/env python3
"""
Script para enriquecer a tabela countries usando chamada direta da Sportmonks API
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

def get_countries_from_api():
    """Buscar countries diretamente da API Sportmonks"""
    
    try:
        config = Config()
        api_token = config.SPORTMONKS_API_KEY
        
        if not api_token:
            logger.error("❌ Token da Sportmonks API não encontrado no .env")
            return []
        
        # URL da API Sportmonks para countries
        url = f"https://api.sportmonks.com/v3/core/countries?api_token={api_token}&include="
        
        logger.info(f"🌐 Fazendo requisição para: {url}")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            countries = data.get('data', [])
            logger.info(f"✅ {len(countries)} countries encontrados na API")
            return countries
        else:
            logger.error(f"❌ Erro na API: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar countries da API: {e}")
        return []

def enrich_countries_table():
    """Enriquecer tabela countries com dados reais da Sportmonks API"""
    
    logger.info("🚀 Enriquecendo tabela countries com dados reais da Sportmonks API...")
    
    # Inicializar cliente Supabase
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
        return
    
    # Buscar countries da API
    countries_from_api = get_countries_from_api()
    
    if not countries_from_api:
        logger.error("❌ Nenhum country encontrado na API")
        return
    
    # Preparar dados para inserção
    countries_to_save = []
    for country_item in countries_from_api:
        country_data = {
            'sportmonks_id': country_item.get('id'),
            'continent_id': country_item.get('continent_id'),
            'name': country_item.get('name'),
            'official_name': country_item.get('official_name'),
            'fifa_name': country_item.get('fifa_name'),
            'iso2': country_item.get('iso2'),
            'iso3': country_item.get('iso3'),
            'latitude': country_item.get('latitude'),
            'longitude': country_item.get('longitude'),
            'borders': country_item.get('borders'),
            'image_path': country_item.get('image_path'),
            'created_at': datetime.utcnow().isoformat()
        }
        countries_to_save.append(country_data)
    
    logger.info(f"📊 {len(countries_to_save)} countries preparados para inserção")
    
    # Salvar countries em lotes para melhor performance
    batch_size = 50
    saved_count = 0
    skipped_count = 0
    error_count = 0
    
    for i in range(0, len(countries_to_save), batch_size):
        batch = countries_to_save[i:i + batch_size]
        
        try:
            supabase.table('countries').insert(batch).execute()
            saved_count += len(batch)
            logger.info(f"✅ Lote {i//batch_size + 1}: {len(batch)} countries salvos")
        except Exception as e:
            if 'duplicate key' in str(e).lower() or 'unique constraint' in str(e).lower():
                # Se houver conflito, salvar um por vez
                for country_data in batch:
                    try:
                        supabase.table('countries').insert(country_data).execute()
                        saved_count += 1
                        logger.info(f"✅ Country salvo: {country_data['name']} (ID: {country_data['sportmonks_id']})")
                    except Exception as e2:
                        if 'duplicate key' in str(e2).lower() or 'unique constraint' in str(e2).lower():
                            skipped_count += 1
                            logger.info(f"⏭️ Country já existe: {country_data['name']} (ID: {country_data['sportmonks_id']})")
                        else:
                            error_count += 1
                            logger.warning(f"⚠️ Erro ao salvar country '{country_data['name']}': {e2}")
            else:
                error_count += len(batch)
                logger.warning(f"⚠️ Erro no lote {i//batch_size + 1}: {e}")
    
    logger.info(f"✅ {saved_count} countries novos salvos")
    logger.info(f"⏭️ {skipped_count} countries já existiam")
    logger.info(f"❌ {error_count} countries com erro")
    
    # Relatório final
    logger.info("=" * 80)
    logger.info("📊 RELATÓRIO FINAL - TABELA COUNTRIES ENRIQUECIDA COM API REAL")
    logger.info("=" * 80)
    
    try:
        response = supabase.table('countries').select('*', count='exact').execute()
        total_count = response.count
        logger.info(f"📊 Total de countries na tabela: {total_count}")
        
        # Mostrar alguns examples
        logger.info("📋 Exemplos de countries da API:")
        examples = supabase.table('countries').select('sportmonks_id,name,official_name,fifa_name,iso2,iso3').limit(15).execute()
        for example in examples.data:
            logger.info(f"   • ID {example['sportmonks_id']}: {example['name']} ({example['iso2']}) - FIFA: {example['fifa_name']}")
        
        # Mostrar estatísticas por continente
        logger.info("\n📈 Estatísticas por continente:")
        
        # Buscar países por continent_id
        continent_stats = supabase.table('countries').select('continent_id').not_.is_('continent_id', 'null').execute()
        continent_counts = {}
        for country in continent_stats.data:
            cid = country['continent_id']
            continent_counts[cid] = continent_counts.get(cid, 0) + 1
        
        for continent_id, count in continent_counts.items():
            logger.info(f"   • Continente ID {continent_id}: {count} países")
        
        # Mostrar países com coordenadas
        with_coords = supabase.table('countries').select('sportmonks_id,name,latitude,longitude').not_.is_('latitude', 'null').not_.is_('longitude', 'null').limit(10).execute()
        logger.info(f"\n🌍 Países com coordenadas GPS: {len(with_coords.data)}")
        for country in with_coords.data[:5]:
            logger.info(f"   • {country['name']}: {country['latitude']}, {country['longitude']}")
        
        # Mostrar países com fronteiras
        with_borders = supabase.table('countries').select('sportmonks_id,name,borders').not_.is_('borders', 'null').limit(5).execute()
        logger.info(f"\n🗺️ Países com informações de fronteiras: {len(with_borders.data)}")
        for country in with_borders.data:
            borders = country['borders'][:50] + "..." if len(str(country['borders'])) > 50 else country['borders']
            logger.info(f"   • {country['name']}: {borders}")
                
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")
    
    logger.info("=" * 80)
    logger.info("✅ ENRIQUECIMENTO DA TABELA COUNTRIES COM API REAL CONCLUÍDO!")
    logger.info("=" * 80)

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 ENRIQUECENDO TABELA COUNTRIES COM API SPORTMONKS REAL")
    logger.info("=" * 80)
    
    enrich_countries_table()

if __name__ == "__main__":
    main()
