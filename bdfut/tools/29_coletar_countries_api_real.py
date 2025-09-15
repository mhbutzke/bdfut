#!/usr/bin/env python3
"""
Script para coletar todos os countries da Sportmonks API REAL com paginação completa
"""

import os
import sys
import requests
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

def get_all_countries_with_pagination():
    """Buscar todos os countries da API Sportmonks REAL com paginação completa"""
    
    try:
        config = Config()
        api_token = config.SPORTMONKS_API_KEY
        
        if not api_token:
            logger.error("❌ Token da Sportmonks API não encontrado no .env")
            return []
        
        all_countries = []
        page = 1
        per_page = 25  # Máximo por página
        total_pages = None
        
        logger.info("🌐 Iniciando coleta REAL com paginação completa...")
        logger.info(f"🔑 Usando token: {api_token[:10]}...")
        
        while True:
            # URL da API Sportmonks para countries com paginação
            url = f"https://api.sportmonks.com/v3/core/countries?api_token={api_token}&include=&page={page}&per_page={per_page}"
            
            logger.info(f"📄 Fazendo requisição REAL - Página {page} (per_page={per_page})")
            logger.info(f"🔗 URL: {url}")
            
            try:
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extrair dados da página atual
                    countries = data.get('data', [])
                    pagination = data.get('pagination', {})
                    
                    logger.info(f"✅ Página {page}: {len(countries)} countries encontrados")
                    
                    # Mostrar alguns exemplos da página atual
                    for i, country in enumerate(countries[:3]):
                        logger.info(f"   📋 Exemplo {i+1}: ID {country.get('id')} - {country.get('name')} ({country.get('iso2')})")
                    
                    # Adicionar countries à lista total
                    all_countries.extend(countries)
                    
                    # Verificar informações de paginação
                    if total_pages is None:
                        total_pages = pagination.get('total_pages', 1)
                        total_count = pagination.get('total', 0)
                        logger.info(f"📊 Total de páginas: {total_pages}, Total de countries: {total_count}")
                    
                    # Verificar se há próxima página
                    current_page = pagination.get('current_page', page)
                    has_next = pagination.get('has_more', False)
                    
                    logger.info(f"📋 Página atual: {current_page}, Tem próxima: {has_next}")
                    
                    # Se não há próxima página, parar
                    if not has_next or current_page >= total_pages:
                        logger.info("🏁 Última página alcançada")
                        break
                    
                    page += 1
                    
                    # Rate limiting - aguardar entre requisições
                    time.sleep(0.5)
                    
                elif response.status_code == 401:
                    logger.error("❌ Token inválido - Erro 401 Unauthorized")
                    logger.error(f"Resposta: {response.text}")
                    return []
                    
                elif response.status_code == 429:
                    logger.warning("⚠️ Rate limit atingido - aguardando 60 segundos...")
                    time.sleep(60)
                    continue
                    
                else:
                    logger.error(f"❌ Erro na API: {response.status_code} - {response.text}")
                    return []
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Erro na requisição: {e}")
                return []
            
            # Proteção contra loop infinito
            if page > 100:  # Máximo de 100 páginas (2500 countries)
                logger.warning("⚠️ Limite de páginas atingido (100)")
                break
        
        logger.info(f"🎉 Coleta REAL finalizada: {len(all_countries)} countries coletados")
        return all_countries
        
    except Exception as e:
        logger.error(f"❌ Erro geral na coleta: {e}")
        return []

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
    batch_size = 50
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
    logger.info("🚀 COLETANDO TODOS OS COUNTRIES DA SPORTMONKS API REAL COM PAGINAÇÃO")
    logger.info("=" * 80)
    
    # Coletar todos os countries com paginação REAL
    countries_data = get_all_countries_with_pagination()
    
    if countries_data:
        # Salvar no banco de dados
        saved, skipped, errors = save_countries_to_database(countries_data)
        
        # Gerar relatório final
        generate_final_report()
        
        logger.info("=" * 80)
        logger.info("✅ COLETA REAL DE COUNTRIES FINALIZADA!")
        logger.info(f"📊 Salvos: {saved}, Já existiam: {skipped}, Erros: {errors}")
        logger.info("=" * 80)
    else:
        logger.error("❌ Falha na coleta REAL de countries")

if __name__ == "__main__":
    main()
