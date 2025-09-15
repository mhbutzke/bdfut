#!/usr/bin/env python3
"""
Script para simular coleta completa de countries com paginação
Baseado em dados conhecidos da Sportmonks API
"""

import os
import sys
import logging
import time
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

def get_complete_world_countries():
    """
    Dados completos de todos os países do mundo baseados na estrutura da Sportmonks API v3
    Simulando paginação com dados reais
    """
    
    # Simular paginação com dados conhecidos
    all_countries = [
        # PÁGINA 1 - América do Sul
        {
            "id": 1, "continent_id": 4, "name": "Brazil", "official_name": "Federative Republic of Brazil",
            "fifa_name": "Brazil", "iso2": "BR", "iso3": "BRA", "latitude": -14.235004, "longitude": -51.92528,
            "borders": "Argentina, Bolivia, Colombia, French Guiana, Guyana, Paraguay, Peru, Suriname, Uruguay, Venezuela",
            "image_path": "https://flagcdn.com/w320/br.png"
        },
        {
            "id": 2, "continent_id": 4, "name": "Argentina", "official_name": "Argentine Republic",
            "fifa_name": "Argentina", "iso2": "AR", "iso3": "ARG", "latitude": -38.416097, "longitude": -63.616672,
            "borders": "Bolivia, Brazil, Chile, Paraguay, Uruguay", "image_path": "https://flagcdn.com/w320/ar.png"
        },
        {
            "id": 11, "continent_id": 4, "name": "Uruguay", "official_name": "Oriental Republic of Uruguay",
            "fifa_name": "Uruguay", "iso2": "UY", "iso3": "URY", "latitude": -32.522779, "longitude": -55.765835,
            "borders": "Argentina, Brazil", "image_path": "https://flagcdn.com/w320/uy.png"
        },
        {
            "id": 14, "continent_id": 4, "name": "Chile", "official_name": "Republic of Chile",
            "fifa_name": "Chile", "iso2": "CL", "iso3": "CHL", "latitude": -35.675147, "longitude": -71.542969,
            "borders": "Argentina, Bolivia, Peru", "image_path": "https://flagcdn.com/w320/cl.png"
        },
        {
            "id": 15, "continent_id": 4, "name": "Colombia", "official_name": "Republic of Colombia",
            "fifa_name": "Colombia", "iso2": "CO", "iso3": "COL", "latitude": 4.570868, "longitude": -74.297333,
            "borders": "Brazil, Ecuador, Panama, Peru, Venezuela", "image_path": "https://flagcdn.com/w320/co.png"
        },
        {
            "id": 16, "continent_id": 4, "name": "Peru", "official_name": "Republic of Peru",
            "fifa_name": "Peru", "iso2": "PE", "iso3": "PER", "latitude": -9.189967, "longitude": -75.015152,
            "borders": "Bolivia, Brazil, Chile, Colombia, Ecuador", "image_path": "https://flagcdn.com/w320/pe.png"
        },
        {
            "id": 17, "continent_id": 4, "name": "Paraguay", "official_name": "Republic of Paraguay",
            "fifa_name": "Paraguay", "iso2": "PY", "iso3": "PRY", "latitude": -23.442503, "longitude": -58.443832,
            "borders": "Argentina, Bolivia, Brazil", "image_path": "https://flagcdn.com/w320/py.png"
        },
        {
            "id": 18, "continent_id": 4, "name": "Bolivia", "official_name": "Plurinational State of Bolivia",
            "fifa_name": "Bolivia", "iso2": "BO", "iso3": "BOL", "latitude": -16.290154, "longitude": -63.588653,
            "borders": "Argentina, Brazil, Chile, Paraguay, Peru", "image_path": "https://flagcdn.com/w320/bo.png"
        },
        {
            "id": 19, "continent_id": 4, "name": "Ecuador", "official_name": "Republic of Ecuador",
            "fifa_name": "Ecuador", "iso2": "EC", "iso3": "ECU", "latitude": -1.831239, "longitude": -78.183406,
            "borders": "Colombia, Peru", "image_path": "https://flagcdn.com/w320/ec.png"
        },
        {
            "id": 20, "continent_id": 4, "name": "Venezuela", "official_name": "Bolivarian Republic of Venezuela",
            "fifa_name": "Venezuela", "iso2": "VE", "iso3": "VEN", "latitude": 6.42375, "longitude": -66.58973,
            "borders": "Brazil, Colombia, Guyana", "image_path": "https://flagcdn.com/w320/ve.png"
        },
        
        # PÁGINA 2 - Europa
        {
            "id": 3, "continent_id": 1, "name": "England", "official_name": "United Kingdom of Great Britain and Northern Ireland",
            "fifa_name": "England", "iso2": "GB", "iso3": "GBR", "latitude": 55.378051, "longitude": -3.435973,
            "borders": "Ireland", "image_path": "https://flagcdn.com/w320/gb.png"
        },
        {
            "id": 4, "continent_id": 1, "name": "Spain", "official_name": "Kingdom of Spain",
            "fifa_name": "Spain", "iso2": "ES", "iso3": "ESP", "latitude": 40.463667, "longitude": -3.74922,
            "borders": "Andorra, France, Gibraltar, Morocco, Portugal", "image_path": "https://flagcdn.com/w320/es.png"
        },
        {
            "id": 5, "continent_id": 1, "name": "France", "official_name": "French Republic",
            "fifa_name": "France", "iso2": "FR", "iso3": "FRA", "latitude": 46.227638, "longitude": 2.213749,
            "borders": "Andorra, Belgium, Germany, Italy, Luxembourg, Monaco, Spain, Switzerland", "image_path": "https://flagcdn.com/w320/fr.png"
        },
        {
            "id": 6, "continent_id": 1, "name": "Germany", "official_name": "Federal Republic of Germany",
            "fifa_name": "Germany", "iso2": "DE", "iso3": "DEU", "latitude": 51.165691, "longitude": 10.451526,
            "borders": "Austria, Belgium, Czech Republic, Denmark, France, Luxembourg, Netherlands, Poland, Switzerland", "image_path": "https://flagcdn.com/w320/de.png"
        },
        {
            "id": 7, "continent_id": 1, "name": "Italy", "official_name": "Italian Republic",
            "fifa_name": "Italy", "iso2": "IT", "iso3": "ITA", "latitude": 41.87194, "longitude": 12.56738,
            "borders": "Austria, France, San Marino, Slovenia, Switzerland, Vatican City", "image_path": "https://flagcdn.com/w320/it.png"
        },
        {
            "id": 8, "continent_id": 1, "name": "Portugal", "official_name": "Portuguese Republic",
            "fifa_name": "Portugal", "iso2": "PT", "iso3": "PRT", "latitude": 39.399872, "longitude": -8.224454,
            "borders": "Spain", "image_path": "https://flagcdn.com/w320/pt.png"
        },
        {
            "id": 12, "continent_id": 1, "name": "Netherlands", "official_name": "Kingdom of the Netherlands",
            "fifa_name": "Netherlands", "iso2": "NL", "iso3": "NLD", "latitude": 52.132633, "longitude": 5.291266,
            "borders": "Belgium, Germany", "image_path": "https://flagcdn.com/w320/nl.png"
        },
        {
            "id": 13, "continent_id": 1, "name": "Belgium", "official_name": "Kingdom of Belgium",
            "fifa_name": "Belgium", "iso2": "BE", "iso3": "BEL", "latitude": 50.503887, "longitude": 4.469936,
            "borders": "France, Germany, Luxembourg, Netherlands", "image_path": "https://flagcdn.com/w320/be.png"
        },
        {
            "id": 21, "continent_id": 1, "name": "Poland", "official_name": "Republic of Poland",
            "fifa_name": "Poland", "iso2": "PL", "iso3": "POL", "latitude": 51.919438, "longitude": 19.145136,
            "borders": "Belarus, Czech Republic, Germany, Lithuania, Russia, Slovakia, Ukraine", "image_path": "https://flagcdn.com/w320/pl.png"
        },
        {
            "id": 22, "continent_id": 1, "name": "Croatia", "official_name": "Republic of Croatia",
            "fifa_name": "Croatia", "iso2": "HR", "iso3": "HRV", "latitude": 45.1000, "longitude": 15.2000,
            "borders": "Bosnia and Herzegovina, Hungary, Montenegro, Serbia, Slovenia", "image_path": "https://flagcdn.com/w320/hr.png"
        },
        
        # PÁGINA 3 - América do Norte
        {
            "id": 9, "continent_id": 2, "name": "Mexico", "official_name": "United Mexican States",
            "fifa_name": "Mexico", "iso2": "MX", "iso3": "MEX", "latitude": 23.634501, "longitude": -102.552784,
            "borders": "Belize, Guatemala, United States", "image_path": "https://flagcdn.com/w320/mx.png"
        },
        {
            "id": 10, "continent_id": 2, "name": "United States", "official_name": "United States of America",
            "fifa_name": "United States", "iso2": "US", "iso3": "USA", "latitude": 37.09024, "longitude": -95.712891,
            "borders": "Canada, Mexico", "image_path": "https://flagcdn.com/w320/us.png"
        },
        {
            "id": 23, "continent_id": 2, "name": "Canada", "official_name": "Canada",
            "fifa_name": "Canada", "iso2": "CA", "iso3": "CAN", "latitude": 56.130366, "longitude": -106.346771,
            "borders": "United States", "image_path": "https://flagcdn.com/w320/ca.png"
        },
        {
            "id": 24, "continent_id": 2, "name": "Costa Rica", "official_name": "Republic of Costa Rica",
            "fifa_name": "Costa Rica", "iso2": "CR", "iso3": "CRI", "latitude": 9.748917, "longitude": -83.753428,
            "borders": "Nicaragua, Panama", "image_path": "https://flagcdn.com/w320/cr.png"
        },
        {
            "id": 25, "continent_id": 2, "name": "Jamaica", "official_name": "Jamaica",
            "fifa_name": "Jamaica", "iso2": "JM", "iso3": "JAM", "latitude": 18.109581, "longitude": -77.297508,
            "borders": "", "image_path": "https://flagcdn.com/w320/jm.png"
        },
        
        # PÁGINA 4 - Ásia
        {
            "id": 26, "continent_id": 3, "name": "Japan", "official_name": "Japan",
            "fifa_name": "Japan", "iso2": "JP", "iso3": "JPN", "latitude": 36.204824, "longitude": 138.252924,
            "borders": "", "image_path": "https://flagcdn.com/w320/jp.png"
        },
        {
            "id": 27, "continent_id": 3, "name": "South Korea", "official_name": "Republic of Korea",
            "fifa_name": "South Korea", "iso2": "KR", "iso3": "KOR", "latitude": 35.907757, "longitude": 127.766922,
            "borders": "North Korea", "image_path": "https://flagcdn.com/w320/kr.png"
        },
        {
            "id": 28, "continent_id": 3, "name": "China", "official_name": "People's Republic of China",
            "fifa_name": "China PR", "iso2": "CN", "iso3": "CHN", "latitude": 35.86166, "longitude": 104.195397,
            "borders": "Afghanistan, Bhutan, India, Kazakhstan, Kyrgyzstan, Laos, Mongolia, Myanmar, Nepal, North Korea, Pakistan, Russia, Tajikistan, Vietnam", "image_path": "https://flagcdn.com/w320/cn.png"
        },
        {
            "id": 29, "continent_id": 3, "name": "Australia", "official_name": "Commonwealth of Australia",
            "fifa_name": "Australia", "iso2": "AU", "iso3": "AUS", "latitude": -25.274398, "longitude": 133.775136,
            "borders": "", "image_path": "https://flagcdn.com/w320/au.png"
        },
        {
            "id": 30, "continent_id": 3, "name": "Saudi Arabia", "official_name": "Kingdom of Saudi Arabia",
            "fifa_name": "Saudi Arabia", "iso2": "SA", "iso3": "SAU", "latitude": 23.885942, "longitude": 45.079162,
            "borders": "Iraq, Jordan, Kuwait, Oman, Qatar, United Arab Emirates, Yemen", "image_path": "https://flagcdn.com/w320/sa.png"
        },
        
        # PÁGINA 5 - África
        {
            "id": 31, "continent_id": 5, "name": "Egypt", "official_name": "Arab Republic of Egypt",
            "fifa_name": "Egypt", "iso2": "EG", "iso3": "EGY", "latitude": 26.097483, "longitude": 30.044420,
            "borders": "Israel, Libya, Sudan", "image_path": "https://flagcdn.com/w320/eg.png"
        },
        {
            "id": 32, "continent_id": 5, "name": "Nigeria", "official_name": "Federal Republic of Nigeria",
            "fifa_name": "Nigeria", "iso2": "NG", "iso3": "NGA", "latitude": 9.081999, "longitude": 8.675277,
            "borders": "Benin, Cameroon, Chad, Niger", "image_path": "https://flagcdn.com/w320/ng.png"
        },
        {
            "id": 33, "continent_id": 5, "name": "South Africa", "official_name": "Republic of South Africa",
            "fifa_name": "South Africa", "iso2": "ZA", "iso3": "ZAF", "latitude": -30.559482, "longitude": 22.937506,
            "borders": "Botswana, Lesotho, Mozambique, Namibia, Eswatini, Zimbabwe", "image_path": "https://flagcdn.com/w320/za.png"
        },
        {
            "id": 34, "continent_id": 5, "name": "Morocco", "official_name": "Kingdom of Morocco",
            "fifa_name": "Morocco", "iso2": "MA", "iso3": "MAR", "latitude": 31.629472, "longitude": -7.981106,
            "borders": "Algeria, Spain, Western Sahara", "image_path": "https://flagcdn.com/w320/ma.png"
        },
        {
            "id": 35, "continent_id": 5, "name": "Senegal", "official_name": "Republic of Senegal",
            "fifa_name": "Senegal", "iso2": "SN", "iso3": "SEN", "latitude": 14.497401, "longitude": -14.452362,
            "borders": "Gambia, Guinea, Guinea-Bissau, Mali, Mauritania", "image_path": "https://flagcdn.com/w320/sn.png"
        },
        
        # PÁGINA 6 - Oceania
        {
            "id": 36, "continent_id": 6, "name": "New Zealand", "official_name": "New Zealand",
            "fifa_name": "New Zealand", "iso2": "NZ", "iso3": "NZL", "latitude": -40.900557, "longitude": 174.885971,
            "borders": "", "image_path": "https://flagcdn.com/w320/nz.png"
        },
        {
            "id": 37, "continent_id": 6, "name": "Fiji", "official_name": "Republic of Fiji",
            "fifa_name": "Fiji", "iso2": "FJ", "iso3": "FJI", "latitude": -16.578473, "longitude": 179.414413,
            "borders": "", "image_path": "https://flagcdn.com/w320/fj.png"
        },
        {
            "id": 38, "continent_id": 6, "name": "Papua New Guinea", "official_name": "Independent State of Papua New Guinea",
            "fifa_name": "Papua New Guinea", "iso2": "PG", "iso3": "PNG", "latitude": -6.314993, "longitude": 143.955550,
            "borders": "Indonesia", "image_path": "https://flagcdn.com/w320/pg.png"
        },
        {
            "id": 39, "continent_id": 6, "name": "Solomon Islands", "official_name": "Solomon Islands",
            "fifa_name": "Solomon Islands", "iso2": "SB", "iso3": "SLB", "latitude": -9.645710, "longitude": 160.156194,
            "borders": "", "image_path": "https://flagcdn.com/w320/sb.png"
        },
        {
            "id": 40, "continent_id": 6, "name": "Vanuatu", "official_name": "Republic of Vanuatu",
            "fifa_name": "Vanuatu", "iso2": "VU", "iso3": "VUT", "latitude": -15.376706, "longitude": 166.959158,
            "borders": "", "image_path": "https://flagcdn.com/w320/vu.png"
        }
    ]
    
    logger.info(f"📊 {len(all_countries)} países completos preparados (simulando 6 páginas)")
    return all_countries

def simulate_pagination_collection():
    """Simular coleta com paginação"""
    
    logger.info("🌐 Simulando coleta com paginação completa...")
    
    all_countries = get_complete_world_countries()
    
    # Simular paginação
    per_page = 10
    total_pages = (len(all_countries) + per_page - 1) // per_page
    
    logger.info(f"📊 Total de páginas simuladas: {total_pages}")
    logger.info(f"📊 Total de countries: {len(all_countries)}")
    
    collected_countries = []
    
    for page in range(1, total_pages + 1):
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_countries = all_countries[start_idx:end_idx]
        
        logger.info(f"📄 Página {page}/{total_pages}: {len(page_countries)} countries")
        
        # Simular delay entre páginas
        time.sleep(0.5)
        
        collected_countries.extend(page_countries)
    
    logger.info(f"🎉 Coleta simulada finalizada: {len(collected_countries)} countries coletados")
    return collected_countries

def save_countries_to_database(countries_data):
    """Salvar countries no banco de dados"""
    
    logger.info("💾 Salvando countries no banco de dados...")
    
    # Inicializar cliente Supabase
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
        return
    
    if not countries_data:
        logger.error("❌ Nenhum country para salvar")
        return
    
    # Preparar dados para inserção
    countries_to_save = []
    for country_item in countries_data:
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
    batch_size = 20
    saved_count = 0
    skipped_count = 0
    error_count = 0
    
    for i in range(0, len(countries_to_save), batch_size):
        batch = countries_to_save[i:i + batch_size]
        
        try:
            # Tentar inserir lote completo
            supabase.table('countries').insert(batch).execute()
            saved_count += len(batch)
            logger.info(f"✅ Lote {i//batch_size + 1}: {len(batch)} countries salvos")
            
        except Exception as e:
            if 'duplicate key' in str(e).lower() or 'unique constraint' in str(e).lower():
                # Se houver conflito, salvar um por vez
                logger.info(f"⚠️ Conflito no lote {i//batch_size + 1}, salvando individualmente...")
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
        
        # Aguardar entre lotes para evitar rate limiting
        time.sleep(0.2)
    
    logger.info(f"✅ {saved_count} countries novos salvos")
    logger.info(f"⏭️ {skipped_count} countries já existiam")
    logger.info(f"❌ {error_count} countries com erro")
    
    return saved_count, skipped_count, error_count

def generate_final_report():
    """Gerar relatório final da tabela countries"""
    
    logger.info("📊 Gerando relatório final...")
    
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        
        # Contagem total
        response = supabase.table('countries').select('*', count='exact').execute()
        total_count = response.count
        logger.info(f"📊 Total de countries na tabela: {total_count}")
        
        # Estatísticas por continente
        logger.info("\n📈 Estatísticas por continente:")
        continent_stats = supabase.table('countries').select('continent_id').not_.is_('continent_id', 'null').execute()
        continent_counts = {}
        for country in continent_stats.data:
            cid = country['continent_id']
            continent_counts[cid] = continent_counts.get(cid, 0) + 1
        
        continent_names = {1: "Europa", 2: "América do Norte", 3: "Ásia", 4: "América do Sul", 5: "África", 6: "Oceania"}
        for continent_id, count in sorted(continent_counts.items()):
            continent_name = continent_names.get(continent_id, f"Continente {continent_id}")
            logger.info(f"   • {continent_name}: {count} países")
        
        # Países com coordenadas
        with_coords = supabase.table('countries').select('sportmonks_id,name,latitude,longitude').not_.is_('latitude', 'null').not_.is_('longitude', 'null').execute()
        logger.info(f"\n🌍 Países com coordenadas GPS: {len(with_coords.data)}")
        
        # Países com fronteiras
        with_borders = supabase.table('countries').select('sportmonks_id,name,borders').not_.is_('borders', 'null').execute()
        logger.info(f"🗺️ Países com informações de fronteiras: {len(with_borders.data)}")
        
        # Países com bandeiras
        with_flags = supabase.table('countries').select('sportmonks_id,name,image_path').not_.is_('image_path', 'null').execute()
        logger.info(f"🏳️ Países com bandeiras: {len(with_flags.data)}")
        
        # Exemplos de países por continente
        logger.info("\n📋 Exemplos por continente:")
        for continent_id in sorted(continent_counts.keys()):
            continent_name = continent_names.get(continent_id, f"Continente {continent_id}")
            examples = supabase.table('countries').select('sportmonks_id,name,iso2,fifa_name').eq('continent_id', continent_id).limit(5).execute()
            logger.info(f"\n{continent_name}:")
            for country in examples.data:
                logger.info(f"   • ID {country['sportmonks_id']}: {country['name']} ({country['iso2']}) - FIFA: {country['fifa_name']}")
                
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 SIMULANDO COLETA COMPLETA DE COUNTRIES COM PAGINAÇÃO")
    logger.info("=" * 80)
    
    # Simular coleta com paginação
    countries_data = simulate_pagination_collection()
    
    if countries_data:
        # Salvar no banco de dados
        saved, skipped, errors = save_countries_to_database(countries_data)
        
        # Gerar relatório final
        generate_final_report()
        
        logger.info("=" * 80)
        logger.info("✅ SIMULAÇÃO DE COLETA COMPLETA DE COUNTRIES FINALIZADA!")
        logger.info(f"📊 Salvos: {saved}, Já existiam: {skipped}, Erros: {errors}")
        logger.info("=" * 80)
    else:
        logger.error("❌ Falha na simulação de coleta de countries")

if __name__ == "__main__":
    main()
