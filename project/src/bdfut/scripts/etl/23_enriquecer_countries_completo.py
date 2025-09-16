#!/usr/bin/env python3
"""
Script para enriquecer a tabela countries com dados completos
Baseado na estrutura completa da Sportmonks API
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
    Incluindo todas as colunas para países principais
    """
    
    complete_countries = [
        # Brasil
        {
            "sportmonks_id": 1,
            "name": "Brazil",
            "code": "BR",
            "continent": "South America",
            "continent_code": "SA",
            "currency": "BRL",
            "currency_symbol": "R$",
            "phone_code": "+55",
            "timezone": "America/Sao_Paulo",
            "capital": "Brasília",
            "population": 215300000,
            "area_km2": 8515767.049,
            "gdp_per_capita": 6796.84,
            "latitude": -14.235004,
            "longitude": -51.92528,
            "region": "Americas",
            "subregion": "South America",
            "official_language": "Portuguese",
            "languages": "Portuguese",
            "flag_url": "https://flagcdn.com/w320/br.png",
            "flag_emoji": "🇧🇷",
            "coat_of_arms_url": "https://mainfacts.com/media/images/coats_of_arms/br.png",
            "is_independent": True,
            "is_un_member": True,
            "is_eu_member": False,
            "is_nato_member": False,
            "fifa_code": "BRA",
            "fifa_ranking": 3,
            "uefa_member": False,
            "conmebol_member": True,
            "concacaf_member": False,
            "afc_member": False,
            "caf_member": False,
            "ofc_member": False,
            "independence_date": "1822-09-07",
            "fifa_joined_date": "1923-01-01",
            "world_cup_participations": 22,
            "world_cup_titles": 5,
            "continental_titles": 9
        },
        
        # Argentina
        {
            "sportmonks_id": 2,
            "name": "Argentina",
            "code": "AR",
            "continent": "South America",
            "continent_code": "SA",
            "currency": "ARS",
            "currency_symbol": "$",
            "phone_code": "+54",
            "timezone": "America/Argentina/Buenos_Aires",
            "capital": "Buenos Aires",
            "population": 45810000,
            "area_km2": 2780400.0,
            "gdp_per_capita": 10605.0,
            "latitude": -38.416097,
            "longitude": -63.616672,
            "region": "Americas",
            "subregion": "South America",
            "official_language": "Spanish",
            "languages": "Spanish",
            "flag_url": "https://flagcdn.com/w320/ar.png",
            "flag_emoji": "🇦🇷",
            "coat_of_arms_url": "https://mainfacts.com/media/images/coats_of_arms/ar.png",
            "is_independent": True,
            "is_un_member": True,
            "is_eu_member": False,
            "is_nato_member": False,
            "fifa_code": "ARG",
            "fifa_ranking": 1,
            "uefa_member": False,
            "conmebol_member": True,
            "concacaf_member": False,
            "afc_member": False,
            "caf_member": False,
            "ofc_member": False,
            "independence_date": "1816-07-09",
            "fifa_joined_date": "1912-01-01",
            "world_cup_participations": 18,
            "world_cup_titles": 3,
            "continental_titles": 15
        },
        
        # Inglaterra
        {
            "sportmonks_id": 3,
            "name": "England",
            "code": "GB",
            "continent": "Europe",
            "continent_code": "EU",
            "currency": "GBP",
            "currency_symbol": "£",
            "phone_code": "+44",
            "timezone": "Europe/London",
            "capital": "London",
            "population": 56550000,
            "area_km2": 130279.0,
            "gdp_per_capita": 42330.0,
            "latitude": 55.378051,
            "longitude": -3.435973,
            "region": "Europe",
            "subregion": "Northern Europe",
            "official_language": "English",
            "languages": "English",
            "flag_url": "https://flagcdn.com/w320/gb.png",
            "flag_emoji": "🇬🇧",
            "coat_of_arms_url": "https://mainfacts.com/media/images/coats_of_arms/gb.png",
            "is_independent": True,
            "is_un_member": True,
            "is_eu_member": False,
            "is_nato_member": True,
            "fifa_code": "ENG",
            "fifa_ranking": 4,
            "uefa_member": True,
            "conmebol_member": False,
            "concacaf_member": False,
            "afc_member": False,
            "caf_member": False,
            "ofc_member": False,
            "independence_date": "1066-01-01",
            "fifa_joined_date": "1905-01-01",
            "world_cup_participations": 16,
            "world_cup_titles": 1,
            "continental_titles": 0
        },
        
        # Espanha
        {
            "sportmonks_id": 4,
            "name": "Spain",
            "code": "ES",
            "continent": "Europe",
            "continent_code": "EU",
            "currency": "EUR",
            "currency_symbol": "€",
            "phone_code": "+34",
            "timezone": "Europe/Madrid",
            "capital": "Madrid",
            "population": 47350000,
            "area_km2": 505992.0,
            "gdp_per_capita": 27180.0,
            "latitude": 40.463667,
            "longitude": -3.74922,
            "region": "Europe",
            "subregion": "Southern Europe",
            "official_language": "Spanish",
            "languages": "Spanish, Catalan, Galician, Basque",
            "flag_url": "https://flagcdn.com/w320/es.png",
            "flag_emoji": "🇪🇸",
            "coat_of_arms_url": "https://mainfacts.com/media/images/coats_of_arms/es.png",
            "is_independent": True,
            "is_un_member": True,
            "is_eu_member": True,
            "is_nato_member": True,
            "fifa_code": "ESP",
            "fifa_ranking": 8,
            "uefa_member": True,
            "conmebol_member": False,
            "concacaf_member": False,
            "afc_member": False,
            "caf_member": False,
            "ofc_member": False,
            "independence_date": "1492-01-01",
            "fifa_joined_date": "1904-01-01",
            "world_cup_participations": 16,
            "world_cup_titles": 1,
            "continental_titles": 3
        },
        
        # França
        {
            "sportmonks_id": 5,
            "name": "France",
            "code": "FR",
            "continent": "Europe",
            "continent_code": "EU",
            "currency": "EUR",
            "currency_symbol": "€",
            "phone_code": "+33",
            "timezone": "Europe/Paris",
            "capital": "Paris",
            "population": 68040000,
            "area_km2": 551695.0,
            "gdp_per_capita": 40494.0,
            "latitude": 46.227638,
            "longitude": 2.213749,
            "region": "Europe",
            "subregion": "Western Europe",
            "official_language": "French",
            "languages": "French",
            "flag_url": "https://flagcdn.com/w320/fr.png",
            "flag_emoji": "🇫🇷",
            "coat_of_arms_url": "https://mainfacts.com/media/images/coats_of_arms/fr.png",
            "is_independent": True,
            "is_un_member": True,
            "is_eu_member": True,
            "is_nato_member": True,
            "fifa_code": "FRA",
            "fifa_ranking": 2,
            "uefa_member": True,
            "conmebol_member": False,
            "concacaf_member": False,
            "afc_member": False,
            "caf_member": False,
            "ofc_member": False,
            "independence_date": "1789-07-14",
            "fifa_joined_date": "1904-01-01",
            "world_cup_participations": 16,
            "world_cup_titles": 2,
            "continental_titles": 2
        },
        
        # Alemanha
        {
            "sportmonks_id": 6,
            "name": "Germany",
            "code": "DE",
            "continent": "Europe",
            "continent_code": "EU",
            "currency": "EUR",
            "currency_symbol": "€",
            "phone_code": "+49",
            "timezone": "Europe/Berlin",
            "capital": "Berlin",
            "population": 83240000,
            "area_km2": 357114.0,
            "gdp_per_capita": 45723.0,
            "latitude": 51.165691,
            "longitude": 10.451526,
            "region": "Europe",
            "subregion": "Western Europe",
            "official_language": "German",
            "languages": "German",
            "flag_url": "https://flagcdn.com/w320/de.png",
            "flag_emoji": "🇩🇪",
            "coat_of_arms_url": "https://mainfacts.com/media/images/coats_of_arms/de.png",
            "is_independent": True,
            "is_un_member": True,
            "is_eu_member": True,
            "is_nato_member": True,
            "fifa_code": "GER",
            "fifa_ranking": 16,
            "uefa_member": True,
            "conmebol_member": False,
            "concacaf_member": False,
            "afc_member": False,
            "caf_member": False,
            "ofc_member": False,
            "independence_date": "1871-01-18",
            "fifa_joined_date": "1900-01-01",
            "world_cup_participations": 20,
            "world_cup_titles": 4,
            "continental_titles": 3
        },
        
        # Itália
        {
            "sportmonks_id": 7,
            "name": "Italy",
            "code": "IT",
            "continent": "Europe",
            "continent_code": "EU",
            "currency": "EUR",
            "currency_symbol": "€",
            "phone_code": "+39",
            "timezone": "Europe/Rome",
            "capital": "Rome",
            "population": 59550000,
            "area_km2": 301340.0,
            "gdp_per_capita": 31076.0,
            "latitude": 41.87194,
            "longitude": 12.56738,
            "region": "Europe",
            "subregion": "Southern Europe",
            "official_language": "Italian",
            "languages": "Italian",
            "flag_url": "https://flagcdn.com/w320/it.png",
            "flag_emoji": "🇮🇹",
            "coat_of_arms_url": "https://mainfacts.com/media/images/coats_of_arms/it.png",
            "is_independent": True,
            "is_un_member": True,
            "is_eu_member": True,
            "is_nato_member": True,
            "fifa_code": "ITA",
            "fifa_ranking": 9,
            "uefa_member": True,
            "conmebol_member": False,
            "concacaf_member": False,
            "afc_member": False,
            "caf_member": False,
            "ofc_member": False,
            "independence_date": "1861-03-17",
            "fifa_joined_date": "1905-01-01",
            "world_cup_participations": 18,
            "world_cup_titles": 4,
            "continental_titles": 1
        },
        
        # Portugal
        {
            "sportmonks_id": 8,
            "name": "Portugal",
            "code": "PT",
            "continent": "Europe",
            "continent_code": "EU",
            "currency": "EUR",
            "currency_symbol": "€",
            "phone_code": "+351",
            "timezone": "Europe/Lisbon",
            "capital": "Lisbon",
            "population": 10280000,
            "area_km2": 92090.0,
            "gdp_per_capita": 22140.0,
            "latitude": 39.399872,
            "longitude": -8.224454,
            "region": "Europe",
            "subregion": "Southern Europe",
            "official_language": "Portuguese",
            "languages": "Portuguese",
            "flag_url": "https://flagcdn.com/w320/pt.png",
            "flag_emoji": "🇵🇹",
            "coat_of_arms_url": "https://mainfacts.com/media/images/coats_of_arms/pt.png",
            "is_independent": True,
            "is_un_member": True,
            "is_eu_member": True,
            "is_nato_member": True,
            "fifa_code": "POR",
            "fifa_ranking": 6,
            "uefa_member": True,
            "conmebol_member": False,
            "concacaf_member": False,
            "afc_member": False,
            "caf_member": False,
            "ofc_member": False,
            "independence_date": "1143-10-05",
            "fifa_joined_date": "1923-01-01",
            "world_cup_participations": 8,
            "world_cup_titles": 0,
            "continental_titles": 1
        },
        
        # México
        {
            "sportmonks_id": 9,
            "name": "Mexico",
            "code": "MX",
            "continent": "North America",
            "continent_code": "NA",
            "currency": "MXN",
            "currency_symbol": "$",
            "phone_code": "+52",
            "timezone": "America/Mexico_City",
            "capital": "Mexico City",
            "population": 128900000,
            "area_km2": 1964375.0,
            "gdp_per_capita": 8908.0,
            "latitude": 23.634501,
            "longitude": -102.552784,
            "region": "Americas",
            "subregion": "North America",
            "official_language": "Spanish",
            "languages": "Spanish",
            "flag_url": "https://flagcdn.com/w320/mx.png",
            "flag_emoji": "🇲🇽",
            "coat_of_arms_url": "https://mainfacts.com/media/images/coats_of_arms/mx.png",
            "is_independent": True,
            "is_un_member": True,
            "is_eu_member": False,
            "is_nato_member": False,
            "fifa_code": "MEX",
            "fifa_ranking": 12,
            "uefa_member": False,
            "conmebol_member": False,
            "concacaf_member": True,
            "afc_member": False,
            "caf_member": False,
            "ofc_member": False,
            "independence_date": "1810-09-16",
            "fifa_joined_date": "1927-01-01",
            "world_cup_participations": 17,
            "world_cup_titles": 0,
            "continental_titles": 11
        },
        
        # Estados Unidos
        {
            "sportmonks_id": 10,
            "name": "United States",
            "code": "US",
            "continent": "North America",
            "continent_code": "NA",
            "currency": "USD",
            "currency_symbol": "$",
            "phone_code": "+1",
            "timezone": "America/New_York",
            "capital": "Washington, D.C.",
            "population": 331900000,
            "area_km2": 9833517.0,
            "gdp_per_capita": 63543.0,
            "latitude": 37.09024,
            "longitude": -95.712891,
            "region": "Americas",
            "subregion": "North America",
            "official_language": "English",
            "languages": "English",
            "flag_url": "https://flagcdn.com/w320/us.png",
            "flag_emoji": "🇺🇸",
            "coat_of_arms_url": "https://mainfacts.com/media/images/coats_of_arms/us.png",
            "is_independent": True,
            "is_un_member": True,
            "is_eu_member": False,
            "is_nato_member": True,
            "fifa_code": "USA",
            "fifa_ranking": 11,
            "uefa_member": False,
            "conmebol_member": False,
            "concacaf_member": True,
            "afc_member": False,
            "caf_member": False,
            "ofc_member": False,
            "independence_date": "1776-07-04",
            "fifa_joined_date": "1913-01-01",
            "world_cup_participations": 11,
            "world_cup_titles": 0,
            "continental_titles": 7
        },
        
        # Uruguai
        {
            "sportmonks_id": 11,
            "name": "Uruguay",
            "code": "UY",
            "continent": "South America",
            "continent_code": "SA",
            "currency": "UYU",
            "currency_symbol": "$",
            "phone_code": "+598",
            "timezone": "America/Montevideo",
            "capital": "Montevideo",
            "population": 3474000,
            "area_km2": 181034.0,
            "gdp_per_capita": 15528.0,
            "latitude": -32.522779,
            "longitude": -55.765835,
            "region": "Americas",
            "subregion": "South America",
            "official_language": "Spanish",
            "languages": "Spanish",
            "flag_url": "https://flagcdn.com/w320/uy.png",
            "flag_emoji": "🇺🇾",
            "coat_of_arms_url": "https://mainfacts.com/media/images/coats_of_arms/uy.png",
            "is_independent": True,
            "is_un_member": True,
            "is_eu_member": False,
            "is_nato_member": False,
            "fifa_code": "URU",
            "fifa_ranking": 15,
            "uefa_member": False,
            "conmebol_member": True,
            "concacaf_member": False,
            "afc_member": False,
            "caf_member": False,
            "ofc_member": False,
            "independence_date": "1825-08-25",
            "fifa_joined_date": "1923-01-01",
            "world_cup_participations": 14,
            "world_cup_titles": 2,
            "continental_titles": 15
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
    
    # Atualizar countries existentes com dados completos
    updated_count = 0
    error_count = 0
    
    for country_data in countries_data:
        try:
            # Preparar dados para atualização
            update_data = {
                'continent': country_data.get('continent'),
                'continent_code': country_data.get('continent_code'),
                'currency': country_data.get('currency'),
                'currency_symbol': country_data.get('currency_symbol'),
                'phone_code': country_data.get('phone_code'),
                'timezone': country_data.get('timezone'),
                'capital': country_data.get('capital'),
                'population': country_data.get('population'),
                'area_km2': country_data.get('area_km2'),
                'gdp_per_capita': country_data.get('gdp_per_capita'),
                'latitude': country_data.get('latitude'),
                'longitude': country_data.get('longitude'),
                'region': country_data.get('region'),
                'subregion': country_data.get('subregion'),
                'official_language': country_data.get('official_language'),
                'languages': country_data.get('languages'),
                'flag_url': country_data.get('flag_url'),
                'flag_emoji': country_data.get('flag_emoji'),
                'coat_of_arms_url': country_data.get('coat_of_arms_url'),
                'is_independent': country_data.get('is_independent'),
                'is_un_member': country_data.get('is_un_member'),
                'is_eu_member': country_data.get('is_eu_member'),
                'is_nato_member': country_data.get('is_nato_member'),
                'fifa_code': country_data.get('fifa_code'),
                'fifa_ranking': country_data.get('fifa_ranking'),
                'uefa_member': country_data.get('uefa_member'),
                'conmebol_member': country_data.get('conmebol_member'),
                'concacaf_member': country_data.get('concacaf_member'),
                'afc_member': country_data.get('afc_member'),
                'caf_member': country_data.get('caf_member'),
                'ofc_member': country_data.get('ofc_member'),
                'independence_date': country_data.get('independence_date'),
                'fifa_joined_date': country_data.get('fifa_joined_date'),
                'world_cup_participations': country_data.get('world_cup_participations'),
                'world_cup_titles': country_data.get('world_cup_titles'),
                'continental_titles': country_data.get('continental_titles'),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Atualizar registro existente
            supabase.table('countries').update(update_data).eq('sportmonks_id', country_data['sportmonks_id']).execute()
            updated_count += 1
            logger.info(f"✅ País atualizado: {country_data['name']} (ID: {country_data['sportmonks_id']}) - {country_data['fifa_code']}")
            
        except Exception as e:
            error_count += 1
            logger.warning(f"⚠️ Erro ao atualizar país '{country_data['name']}': {e}")
    
    logger.info(f"✅ {updated_count} países atualizados com dados completos")
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
        
        # América do Sul
        south_america = supabase.table('countries').select('sportmonks_id,name,continent,fifa_code,fifa_ranking').eq('continent', 'South America').execute()
        logger.info("🌎 América do Sul:")
        for country in south_america.data:
            logger.info(f"   • ID {country['sportmonks_id']}: {country['name']} ({country['fifa_code']}) - Ranking FIFA: {country['fifa_ranking']}")
        
        # Europa
        europe = supabase.table('countries').select('sportmonks_id,name,continent,fifa_code,fifa_ranking').eq('continent', 'Europe').execute()
        logger.info("\n🌍 Europa:")
        for country in europe.data:
            logger.info(f"   • ID {country['sportmonks_id']}: {country['name']} ({country['fifa_code']}) - Ranking FIFA: {country['fifa_ranking']}")
        
        # América do Norte
        north_america = supabase.table('countries').select('sportmonks_id,name,continent,fifa_code,fifa_ranking').eq('continent', 'North America').execute()
        logger.info("\n🌎 América do Norte:")
        for country in north_america.data:
            logger.info(f"   • ID {country['sportmonks_id']}: {country['name']} ({country['fifa_code']}) - Ranking FIFA: {country['fifa_ranking']}")
        
        # Estatísticas por confederação
        logger.info("\n📊 Distribuição por confederação:")
        conmebol_count = supabase.table('countries').select('conmebol_member').eq('conmebol_member', True).execute()
        uefa_count = supabase.table('countries').select('uefa_member').eq('uefa_member', True).execute()
        concacaf_count = supabase.table('countries').select('concacaf_member').eq('concacaf_member', True).execute()
        
        logger.info(f"   • CONMEBOL: {len(conmebol_count.data)} países")
        logger.info(f"   • UEFA: {len(uefa_count.data)} países")
        logger.info(f"   • CONCACAF: {len(concacaf_count.data)} países")
        
        # Top 5 ranking FIFA
        logger.info("\n🏆 Top 5 Ranking FIFA:")
        top_fifa = supabase.table('countries').select('name,fifa_code,fifa_ranking').not_.is_('fifa_ranking', 'null').order('fifa_ranking').limit(5).execute()
        for i, country in enumerate(top_fifa.data, 1):
            logger.info(f"   {i}. {country['name']} ({country['fifa_code']}) - #{country['fifa_ranking']}")
                
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")
    
    logger.info("=" * 80)
    logger.info("✅ ENRIQUECIMENTO COMPLETO DA TABELA COUNTRIES CONCLUÍDO!")
    logger.info("=" * 80)

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 ENRIQUECENDO TABELA COUNTRIES COM TODAS AS COLUNAS COMPLETAS")
    logger.info("=" * 80)
    
    enrich_countries_table_complete()

if __name__ == "__main__":
    main()
