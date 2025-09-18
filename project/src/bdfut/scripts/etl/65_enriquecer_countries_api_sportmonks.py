#!/usr/bin/env python3
"""
Script para enriquecer tabela countries com dados da API Sportmonks
Endpoint: /v3/core/countries
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from bdfut.core.sportmonks_client import SportmonksClient
from supabase import create_client
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CountriesEnricher:
    """Classe para enriquecer tabela countries com dados da API Sportmonks"""
    
    def __init__(self):
        """Inicializar clientes"""
        try:
            # Inicializar cliente Sportmonks
            self.sportmonks_client = SportmonksClient(
                enable_cache=True,
                cache_ttl_hours=24,
                use_redis=True
            )
            
            # Inicializar cliente Supabase
            self.supabase = create_client(
                Config.SUPABASE_URL,
                Config.SUPABASE_SERVICE_KEY
            )
            
            logger.info("✅ Clientes inicializados com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar clientes: {e}")
            raise
    
    def fetch_countries_from_api(self) -> List[Dict[str, Any]]:
        """Buscar países da API Sportmonks com paginação"""
        try:
            logger.info("🔍 Buscando países da API Sportmonks com paginação...")
            
            import requests
            url = "https://api.sportmonks.com/v3/core/countries"
            all_countries = []
            page = 1
            per_page = 25  # Limite padrão da API
            
            while True:
                params = {
                    'api_token': self.sportmonks_client.api_key,
                    'include': '',
                    'page': page,
                    'per_page': per_page
                }
                
                logger.info(f"📄 Buscando página {page}...")
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if not data or 'data' not in data:
                    logger.warning(f"⚠️ Nenhum dado retornado na página {page}")
                    break
                
                countries = data['data']
                if not countries:
                    logger.info(f"✅ Página {page} vazia - fim da paginação")
                    break
                
                all_countries.extend(countries)
                logger.info(f"✅ Página {page}: {len(countries)} países encontrados")
                
                # Verificar se há mais páginas
                pagination = data.get('pagination', {})
                if not pagination.get('has_more', False):
                    logger.info("✅ Última página alcançada")
                    break
                
                page += 1
                
                # Pequena pausa para respeitar rate limits
                time.sleep(0.1)
            
            logger.info(f"🎉 Total de países encontrados: {len(all_countries)}")
            return all_countries
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar países da API: {e}")
            return []
    
    def process_countries_data(self, countries_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processar dados dos países para inserção"""
        processed_countries = []
        
        for country in countries_data:
            try:
                processed_country = {
                    'country_id': country.get('id'),
                    'continent_id': country.get('continent_id'),
                    'name': country.get('name', ''),
                    'official_name': country.get('official_name', ''),
                    'fifa_name': country.get('fifa_name', ''),
                    'iso2': country.get('iso2', ''),
                    'iso3': country.get('iso3', ''),
                    'latitude': country.get('latitude'),
                    'longitude': country.get('longitude'),
                    'borders': country.get('borders', ''),
                    'image_path': country.get('image_path', ''),
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Validar dados obrigatórios
                if processed_country['country_id'] and processed_country['name']:
                    processed_countries.append(processed_country)
                else:
                    logger.warning(f"⚠️ País inválido ignorado: {country}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao processar país {country}: {e}")
                continue
        
        logger.info(f"✅ {len(processed_countries)} países processados com sucesso")
        return processed_countries
    
    def insert_countries_to_database(self, countries_data: List[Dict[str, Any]]) -> int:
        """Inserir países no banco de dados"""
        try:
            logger.info(f"💾 Inserindo {len(countries_data)} países no banco...")
            
            inserted_count = 0
            updated_count = 0
            
            for country in countries_data:
                try:
                    # Verificar se o país já existe
                    existing = self.supabase.table('countries').select('country_id').eq('country_id', country['country_id']).execute()
                    
                    if existing.data:
                        # Atualizar país existente
                        result = self.supabase.table('countries').update({
                            'continent_id': country['continent_id'],
                            'name': country['name'],
                            'official_name': country['official_name'],
                            'fifa_name': country['fifa_name'],
                            'iso2': country['iso2'],
                            'iso3': country['iso3'],
                            'latitude': country['latitude'],
                            'longitude': country['longitude'],
                            'borders': country['borders'],
                            'image_path': country['image_path'],
                            'updated_at': country['updated_at']
                        }).eq('country_id', country['country_id']).execute()
                        
                        if result.data:
                            updated_count += 1
                            logger.debug(f"✅ País atualizado: {country['name']} (ID: {country['country_id']})")
                    else:
                        # Inserir novo país
                        result = self.supabase.table('countries').insert(country).execute()
                        
                        if result.data:
                            inserted_count += 1
                            logger.debug(f"✅ País inserido: {country['name']} (ID: {country['country_id']})")
                
                except Exception as e:
                    logger.error(f"❌ Erro ao inserir/atualizar país {country['name']}: {e}")
                    continue
            
            logger.info(f"✅ Enriquecimento concluído: {inserted_count} inseridos, {updated_count} atualizados")
            return inserted_count + updated_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao inserir países no banco: {e}")
            return 0
    
    def get_current_countries_count(self) -> int:
        """Obter contagem atual de países"""
        try:
            result = self.supabase.table('countries').select('country_id', count='exact').execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"❌ Erro ao contar países: {e}")
            return 0
    
    def run_enrichment(self):
        """Executar processo completo de enriquecimento"""
        try:
            logger.info("🚀 Iniciando enriquecimento da tabela countries...")
            
            # Contar países atuais
            initial_count = self.get_current_countries_count()
            logger.info(f"📊 Países atuais: {initial_count}")
            
            # Buscar dados da API
            countries_data = self.fetch_countries_from_api()
            
            if not countries_data:
                logger.warning("⚠️ Nenhum dado obtido da API")
                return
            
            # Processar dados
            processed_countries = self.process_countries_data(countries_data)
            
            if not processed_countries:
                logger.warning("⚠️ Nenhum país processado")
                return
            
            # Inserir no banco
            enriched_count = self.insert_countries_to_database(processed_countries)
            
            # Contar países finais
            final_count = self.get_current_countries_count()
            
            logger.info("🎉 Enriquecimento concluído!")
            logger.info(f"📈 Países iniciais: {initial_count}")
            logger.info(f"📈 Países finais: {final_count}")
            logger.info(f"📈 Países adicionados/atualizados: {enriched_count}")
            
        except Exception as e:
            logger.error(f"❌ Erro no processo de enriquecimento: {e}")
            raise

def main():
    """Função principal"""
    try:
        enricher = CountriesEnricher()
        enricher.run_enrichment()
        
    except Exception as e:
        logger.error(f"❌ Erro na execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
