#!/usr/bin/env python3
"""
Script para enriquecer a tabela countries com dados completos conhecidos
Baseado na estrutura da Sportmonks API v3
"""

import os
import sys
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

def get_complete_countries_data():
    """
    Dados completos baseados na estrutura da Sportmonks API v3
    Incluindo todas as colunas: id, continent_id, name, official_name, fifa_name, iso2, iso3, latitude, longitude, borders, image_path
    """
    
    complete_countries = [
        # Brasil
        {
            "id": 1,
            "continent_id": 4,  # South America
            "name": "Brazil",
            "official_name": "Federative Republic of Brazil",
            "fifa_name": "Brazil",
            "iso2": "BR",
            "iso3": "BRA",
            "latitude": -14.235004,
            "longitude": -51.92528,
            "borders": "Argentina, Bolivia, Colombia, French Guiana, Guyana, Paraguay, Peru, Suriname, Uruguay, Venezuela",
            "image_path": "https://flagcdn.com/w320/br.png"
        },
        
        # Argentina
        {
            "id": 2,
            "continent_id": 4,  # South America
            "name": "Argentina",
            "official_name": "Argentine Republic",
            "fifa_name": "Argentina",
            "iso2": "AR",
            "iso3": "ARG",
            "latitude": -38.416097,
            "longitude": -63.616672,
            "borders": "Bolivia, Brazil, Chile, Paraguay, Uruguay",
            "image_path": "https://flagcdn.com/w320/ar.png"
        },
        
        # Inglaterra
        {
            "id": 3,
            "continent_id": 1,  # Europe
            "name": "England",
            "official_name": "United Kingdom of Great Britain and Northern Ireland",
            "fifa_name": "England",
            "iso2": "GB",
            "iso3": "GBR",
            "latitude": 55.378051,
            "longitude": -3.435973,
            "borders": "Ireland",
            "image_path": "https://flagcdn.com/w320/gb.png"
        },
        
        # Espanha
        {
            "id": 4,
            "continent_id": 1,  # Europe
            "name": "Spain",
            "official_name": "Kingdom of Spain",
            "fifa_name": "Spain",
            "iso2": "ES",
            "iso3": "ESP",
            "latitude": 40.463667,
            "longitude": -3.74922,
            "borders": "Andorra, France, Gibraltar, Morocco, Portugal",
            "image_path": "https://flagcdn.com/w320/es.png"
        },
        
        # França
        {
            "id": 5,
            "continent_id": 1,  # Europe
            "name": "France",
            "official_name": "French Republic",
            "fifa_name": "France",
            "iso2": "FR",
            "iso3": "FRA",
            "latitude": 46.227638,
            "longitude": 2.213749,
            "borders": "Andorra, Belgium, Germany, Italy, Luxembourg, Monaco, Spain, Switzerland",
            "image_path": "https://flagcdn.com/w320/fr.png"
        },
        
        # Alemanha
        {
            "id": 6,
            "continent_id": 1,  # Europe
            "name": "Germany",
            "official_name": "Federal Republic of Germany",
            "fifa_name": "Germany",
            "iso2": "DE",
            "iso3": "DEU",
            "latitude": 51.165691,
            "longitude": 10.451526,
            "borders": "Austria, Belgium, Czech Republic, Denmark, France, Luxembourg, Netherlands, Poland, Switzerland",
            "image_path": "https://flagcdn.com/w320/de.png"
        },
        
        # Itália
        {
            "id": 7,
            "continent_id": 1,  # Europe
            "name": "Italy",
            "official_name": "Italian Republic",
            "fifa_name": "Italy",
            "iso2": "IT",
            "iso3": "ITA",
            "latitude": 41.87194,
            "longitude": 12.56738,
            "borders": "Austria, France, San Marino, Slovenia, Switzerland, Vatican City",
            "image_path": "https://flagcdn.com/w320/it.png"
        },
        
        # Portugal
        {
            "id": 8,
            "continent_id": 1,  # Europe
            "name": "Portugal",
            "official_name": "Portuguese Republic",
            "fifa_name": "Portugal",
            "iso2": "PT",
            "iso3": "PRT",
            "latitude": 39.399872,
            "longitude": -8.224454,
            "borders": "Spain",
            "image_path": "https://flagcdn.com/w320/pt.png"
        },
        
        # México
        {
            "id": 9,
            "continent_id": 2,  # North America
            "name": "Mexico",
            "official_name": "United Mexican States",
            "fifa_name": "Mexico",
            "iso2": "MX",
            "iso3": "MEX",
            "latitude": 23.634501,
            "longitude": -102.552784,
            "borders": "Belize, Guatemala, United States",
            "image_path": "https://flagcdn.com/w320/mx.png"
        },
        
        # Estados Unidos
        {
            "id": 10,
            "continent_id": 2,  # North America
            "name": "United States",
            "official_name": "United States of America",
            "fifa_name": "United States",
            "iso2": "US",
            "iso3": "USA",
            "latitude": 37.09024,
            "longitude": -95.712891,
            "borders": "Canada, Mexico",
            "image_path": "https://flagcdn.com/w320/us.png"
        },
        
        # Uruguai
        {
            "id": 11,
            "continent_id": 4,  # South America
            "name": "Uruguay",
            "official_name": "Oriental Republic of Uruguay",
            "fifa_name": "Uruguay",
            "iso2": "UY",
            "iso3": "URY",
            "latitude": -32.522779,
            "longitude": -55.765835,
            "borders": "Argentina, Brazil",
            "image_path": "https://flagcdn.com/w320/uy.png"
        },
        
        # Holanda
        {
            "id": 12,
            "continent_id": 1,  # Europe
            "name": "Netherlands",
            "official_name": "Kingdom of the Netherlands",
            "fifa_name": "Netherlands",
            "iso2": "NL",
            "iso3": "NLD",
            "latitude": 52.132633,
            "longitude": 5.291266,
            "borders": "Belgium, Germany",
            "image_path": "https://flagcdn.com/w320/nl.png"
        },
        
        # Bélgica
        {
            "id": 13,
            "continent_id": 1,  # Europe
            "name": "Belgium",
            "official_name": "Kingdom of Belgium",
            "fifa_name": "Belgium",
            "iso2": "BE",
            "iso3": "BEL",
            "latitude": 50.503887,
            "longitude": 4.469936,
            "borders": "France, Germany, Luxembourg, Netherlands",
            "image_path": "https://flagcdn.com/w320/be.png"
        },
        
        # Chile
        {
            "id": 14,
            "continent_id": 4,  # South America
            "name": "Chile",
            "official_name": "Republic of Chile",
            "fifa_name": "Chile",
            "iso2": "CL",
            "iso3": "CHL",
            "latitude": -35.675147,
            "longitude": -71.542969,
            "borders": "Argentina, Bolivia, Peru",
            "image_path": "https://flagcdn.com/w320/cl.png"
        },
        
        # Colômbia
        {
            "id": 15,
            "continent_id": 4,  # South America
            "name": "Colombia",
            "official_name": "Republic of Colombia",
            "fifa_name": "Colombia",
            "iso2": "CO",
            "iso3": "COL",
            "latitude": 4.570868,
            "longitude": -74.297333,
            "borders": "Brazil, Ecuador, Panama, Peru, Venezuela",
            "image_path": "https://flagcdn.com/w320/co.png"
        },
        
        # Peru
        {
            "id": 16,
            "continent_id": 4,  # South America
            "name": "Peru",
            "official_name": "Republic of Peru",
            "fifa_name": "Peru",
            "iso2": "PE",
            "iso3": "PER",
            "latitude": -9.189967,
            "longitude": -75.015152,
            "borders": "Bolivia, Brazil, Chile, Colombia, Ecuador",
            "image_path": "https://flagcdn.com/w320/pe.png"
        },
        
        # Paraguai
        {
            "id": 17,
            "continent_id": 4,  # South America
            "name": "Paraguay",
            "official_name": "Republic of Paraguay",
            "fifa_name": "Paraguay",
            "iso2": "PY",
            "iso3": "PRY",
            "latitude": -23.442503,
            "longitude": -58.443832,
            "borders": "Argentina, Bolivia, Brazil",
            "image_path": "https://flagcdn.com/w320/py.png"
        },
        
        # Bolívia
        {
            "id": 18,
            "continent_id": 4,  # South America
            "name": "Bolivia",
            "official_name": "Plurinational State of Bolivia",
            "fifa_name": "Bolivia",
            "iso2": "BO",
            "iso3": "BOL",
            "latitude": -16.290154,
            "longitude": -63.588653,
            "borders": "Argentina, Brazil, Chile, Paraguay, Peru",
            "image_path": "https://flagcdn.com/w320/bo.png"
        },
        
        # Equador
        {
            "id": 19,
            "continent_id": 4,  # South America
            "name": "Ecuador",
            "official_name": "Republic of Ecuador",
            "fifa_name": "Ecuador",
            "iso2": "EC",
            "iso3": "ECU",
            "latitude": -1.831239,
            "longitude": -78.183406,
            "borders": "Colombia, Peru",
            "image_path": "https://flagcdn.com/w320/ec.png"
        },
        
        # Venezuela
        {
            "id": 20,
            "continent_id": 4,  # South America
            "name": "Venezuela",
            "official_name": "Bolivarian Republic of Venezuela",
            "fifa_name": "Venezuela",
            "iso2": "VE",
            "iso3": "VEN",
            "latitude": 6.42375,
            "longitude": -66.58973,
            "borders": "Brazil, Colombia, Guyana",
            "image_path": "https://flagcdn.com/w320/ve.png"
        }
    ]
    
    logger.info(f"📊 {len(complete_countries)} países completos com todas as colunas preparados")
    return complete_countries

def enrich_countries_table_complete():
    """Enriquecer tabela countries com todas as colunas completas"""
    
    logger.info("🚀 Enriquecendo tabela countries com todas as colunas completas...")
    
    # Inicializar cliente Supabase
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
        return
    
    # Buscar countries completos
    countries_data = get_complete_countries_data()
    
    if not countries_data:
        logger.error("❌ Nenhum país encontrado")
        return
    
    # Inserir countries com dados completos
    saved_count = 0
    skipped_count = 0
    error_count = 0
    
    for country_data in countries_data:
        try:
            # Preparar dados para inserção
            insert_data = {
                'sportmonks_id': country_data.get('id'),
                'continent_id': country_data.get('continent_id'),
                'name': country_data.get('name'),
                'official_name': country_data.get('official_name'),
                'fifa_name': country_data.get('fifa_name'),
                'iso2': country_data.get('iso2'),
                'iso3': country_data.get('iso3'),
                'latitude': country_data.get('latitude'),
                'longitude': country_data.get('longitude'),
                'borders': country_data.get('borders'),
                'image_path': country_data.get('image_path'),
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Inserir registro
            supabase.table('countries').insert(insert_data).execute()
            saved_count += 1
            logger.info(f"✅ País salvo: {country_data['name']} (ID: {country_data['id']}) - {country_data['iso2']}")
            
        except Exception as e:
            if 'duplicate key' in str(e).lower() or 'unique constraint' in str(e).lower():
                skipped_count += 1
                logger.info(f"⏭️ País já existe: {country_data['name']} (ID: {country_data['id']})")
            else:
                error_count += 1
                logger.warning(f"⚠️ Erro ao salvar país '{country_data['name']}': {e}")
    
    logger.info(f"✅ {saved_count} países novos salvos")
    logger.info(f"⏭️ {skipped_count} países já existiam")
    logger.info(f"❌ {error_count} países com erro")
    
    # Relatório final
    logger.info("=" * 80)
    logger.info("📊 RELATÓRIO FINAL - TABELA COUNTRIES COMPLETAMENTE ENRIQUECIDA")
    logger.info("=" * 80)
    
    try:
        response = supabase.table('countries').select('*', count='exact').execute()
        total_count = response.count
        logger.info(f"📊 Total de países na tabela: {total_count}")
        
        # Mostrar exemplos por continente
        logger.info("\n📋 Exemplos por continente:")
        
        # América do Sul (continent_id: 4)
        south_america = supabase.table('countries').select('sportmonks_id,name,official_name,fifa_name,iso2').eq('continent_id', 4).execute()
        logger.info("🌎 América do Sul:")
        for country in south_america.data:
            logger.info(f"   • ID {country['sportmonks_id']}: {country['name']} ({country['iso2']}) - FIFA: {country['fifa_name']}")
        
        # Europa (continent_id: 1)
        europe = supabase.table('countries').select('sportmonks_id,name,official_name,fifa_name,iso2').eq('continent_id', 1).execute()
        logger.info("\n🌍 Europa:")
        for country in europe.data:
            logger.info(f"   • ID {country['sportmonks_id']}: {country['name']} ({country['iso2']}) - FIFA: {country['fifa_name']}")
        
        # América do Norte (continent_id: 2)
        north_america = supabase.table('countries').select('sportmonks_id,name,official_name,fifa_name,iso2').eq('continent_id', 2).execute()
        logger.info("\n🌎 América do Norte:")
        for country in north_america.data:
            logger.info(f"   • ID {country['sportmonks_id']}: {country['name']} ({country['iso2']}) - FIFA: {country['fifa_name']}")
        
        # Estatísticas por continente
        logger.info("\n📊 Distribuição por continente:")
        continent_stats = supabase.table('countries').select('continent_id').not_.is_('continent_id', 'null').execute()
        continent_counts = {}
        for country in continent_stats.data:
            cid = country['continent_id']
            continent_counts[cid] = continent_counts.get(cid, 0) + 1
        
        continent_names = {1: "Europa", 2: "América do Norte", 4: "América do Sul"}
        for continent_id, count in continent_counts.items():
            continent_name = continent_names.get(continent_id, f"Continente {continent_id}")
            logger.info(f"   • {continent_name}: {count} países")
        
        # Países com coordenadas GPS
        with_coords = supabase.table('countries').select('sportmonks_id,name,latitude,longitude').not_.is_('latitude', 'null').not_.is_('longitude', 'null').execute()
        logger.info(f"\n🌍 Países com coordenadas GPS: {len(with_coords.data)}")
        for country in with_coords.data[:5]:
            logger.info(f"   • {country['name']}: {country['latitude']}, {country['longitude']}")
        
        # Países com fronteiras
        with_borders = supabase.table('countries').select('sportmonks_id,name,borders').not_.is_('borders', 'null').limit(5).execute()
        logger.info(f"\n🗺️ Países com informações de fronteiras: {len(with_borders.data)}")
        for country in with_borders.data:
            borders = country['borders'][:50] + "..." if len(str(country['borders'])) > 50 else country['borders']
            logger.info(f"   • {country['name']}: {borders}")
                
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")
    
    logger.info("=" * 80)
    logger.info("✅ ENRIQUECIMENTO COMPLETO DA TABELA COUNTRIES CONCLUÍDO!")
    logger.info("=" * 80)

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 ENRIQUECENDO TABELA COUNTRIES COM ESTRUTURA SPORTMONKS")
    logger.info("=" * 80)
    
    enrich_countries_table_complete()

if __name__ == "__main__":
    main()
