#!/usr/bin/env python3
"""
Script para enriquecer tabela referees com dados da API Sportmonks
Endpoint: /v3/football/referees
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
import requests

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RefereesEnricher:
    """Classe para enriquecer tabela referees com dados da API Sportmonks"""
    
    def __init__(self):
        """Inicializar clientes"""
        try:
            self.config = Config()
            self.sportmonks_client = SportmonksClient()
            self.supabase = create_client(self.config.SUPABASE_URL, self.config.SUPABASE_KEY)
            logger.info("✅ Clientes inicializados com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar clientes: {e}")
            sys.exit(1)

    def fetch_referees_from_api(self) -> List[Dict[str, Any]]:
        """Buscar árbitros da API Sportmonks com paginação"""
        all_referees = []
        page = 1
        has_more = True
        
        logger.info("🔍 Buscando árbitros da API Sportmonks com paginação...")

        while has_more:
            try:
                logger.info(f"📄 Buscando página {page}...")
                url = "https://api.sportmonks.com/v3/football/referees"
                params = {
                    'api_token': self.sportmonks_client.api_key,
                    'include': '',
                    'page': page
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data and 'data' in data:
                    referees_on_page = data['data']
                    all_referees.extend(referees_on_page)
                    logger.info(f"✅ Página {page}: {len(referees_on_page)} árbitros encontrados")
                    
                    # Verificar paginação
                    pagination = data.get('pagination', {})
                    has_more = pagination.get('has_more', False)
                    page += 1
                else:
                    logger.warning(f"⚠️ Nenhum dado retornado da API na página {page}")
                    has_more = False
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Erro ao buscar árbitros da API na página {page}: {e}")
                has_more = False
            except Exception as e:
                logger.error(f"❌ Erro inesperado ao buscar árbitros da API na página {page}: {e}")
                has_more = False
                
        logger.info(f"🎉 Total de árbitros encontrados: {len(all_referees)}")
        return all_referees

    def process_referees_data(self, referees_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processar dados dos árbitros para inserção"""
        processed_referees = []
        for referee in referees_data:
            processed_referee = {
                'referee_id': referee.get('id'),
                'sport_id': referee.get('sport_id'),
                'country_id': referee.get('country_id'),
                'city_id': referee.get('city_id'),
                'common_name': referee.get('common_name'),
                'firstname': referee.get('firstname'),
                'lastname': referee.get('lastname'),
                'name': referee.get('name', ''),
                'display_name': referee.get('display_name'),
                'image_path': referee.get('image_path'),
                'height': referee.get('height'),
                'weight': referee.get('weight'),
                'date_of_birth': referee.get('date_of_birth'),
                'gender': referee.get('gender'),
                'nationality': referee.get('nationality')  # Manter para compatibilidade
            }
            # Remover campos None para evitar erros de inserção/atualização
            processed_referee = {k: v for k, v in processed_referee.items() if v is not None}
            processed_referees.append(processed_referee)
        return processed_referees

    def insert_referees_to_database(self, referees: List[Dict[str, Any]]):
        """Inserir ou atualizar árbitros no banco de dados"""
        inserted_count = 0
        updated_count = 0
        
        logger.info(f"💾 Inserindo {len(referees)} árbitros no banco...")

        for referee in referees:
            referee_id = referee.get('referee_id')
            if referee_id is None:
                logger.warning(f"⚠️ Árbitro sem referee_id, pulando: {referee.get('name')}")
                continue

            try:
                # Verificar se o árbitro já existe
                existing = self.supabase.table('referees').select('referee_id').eq('referee_id', referee_id).execute()
                
                if existing.data:
                    # Atualizar árbitro existente
                    update_data = {
                        'name': referee['name'],
                        'sport_id': referee.get('sport_id'),
                        'country_id': referee.get('country_id'),
                        'city_id': referee.get('city_id'),
                        'common_name': referee.get('common_name'),
                        'firstname': referee.get('firstname'),
                        'lastname': referee.get('lastname'),
                        'display_name': referee.get('display_name'),
                        'image_path': referee.get('image_path'),
                        'height': referee.get('height'),
                        'weight': referee.get('weight'),
                        'date_of_birth': referee.get('date_of_birth'),
                        'gender': referee.get('gender'),
                        'nationality': referee.get('nationality')
                    }
                    
                    # Remover campos None
                    update_data = {k: v for k, v in update_data.items() if v is not None}
                    
                    result = self.supabase.table('referees').update(update_data).eq('referee_id', referee_id).execute()
                    if result.data:
                        updated_count += 1
                    else:
                        logger.error(f"❌ Erro ao atualizar árbitro {referee_id}: {result.error}")
                else:
                    # Inserir novo árbitro
                    result = self.supabase.table('referees').insert(referee).execute()
                    if result.data:
                        inserted_count += 1
                    else:
                        logger.error(f"❌ Erro ao inserir árbitro {referee_id}: {result.error}")
            except Exception as e:
                logger.error(f"❌ Erro ao processar árbitro {referee_id} ({referee.get('name')}): {e}")
                
        logger.info(f"✅ Enriquecimento concluído: {inserted_count} inseridos, {updated_count} atualizados")
        return inserted_count, updated_count

    def run(self):
        """Executar o processo de enriquecimento"""
        logger.info("🚀 Iniciando enriquecimento da tabela referees...")
        
        # Obter contagem inicial de árbitros
        initial_count_response = self.supabase.table('referees').select('referee_id', count='exact').execute()
        initial_count = initial_count_response.count if initial_count_response.count is not None else 0
        logger.info(f"📊 Árbitros atuais: {initial_count}")

        referees_data = self.fetch_referees_from_api()
        if referees_data:
            processed_referees = self.process_referees_data(referees_data)
            logger.info(f"✅ {len(processed_referees)} árbitros processados com sucesso")
            inserted, updated = self.insert_referees_to_database(processed_referees)
            
            # Obter contagem final de árbitros
            final_count_response = self.supabase.table('referees').select('referee_id', count='exact').execute()
            final_count = final_count_response.count if final_count_response.count is not None else 0

            logger.info("🎉 Enriquecimento concluído!")
            logger.info(f"📈 Árbitros iniciais: {initial_count}")
            logger.info(f"📈 Árbitros finais: {final_count}")
            logger.info(f"📈 Árbitros adicionados/atualizados: {inserted + updated}")
        else:
            logger.warning("⚠️ Nenhum árbitro para processar.")

if __name__ == "__main__":
    enricher = RefereesEnricher()
    enricher.run()
