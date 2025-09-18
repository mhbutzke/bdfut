#!/usr/bin/env python3
"""
Script para enriquecer tabela teams com dados da API Sportmonks
Endpoint: /v3/football/teams
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

class TeamsEnricher:
    """Classe para enriquecer tabela teams com dados da API Sportmonks"""
    
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

    def fetch_teams_from_api(self) -> List[Dict[str, Any]]:
        """Buscar times da API Sportmonks com paginação"""
        all_teams = []
        page = 1
        has_more = True
        
        logger.info("🔍 Buscando times da API Sportmonks com paginação...")

        while has_more:
            try:
                logger.info(f"📄 Buscando página {page}...")
                url = "https://api.sportmonks.com/v3/football/teams"
                params = {
                    'api_token': self.sportmonks_client.api_key,
                    'include': '',
                    'page': page
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data and 'data' in data:
                    teams_on_page = data['data']
                    all_teams.extend(teams_on_page)
                    logger.info(f"✅ Página {page}: {len(teams_on_page)} times encontrados")
                    
                    # Verificar paginação
                    pagination = data.get('pagination', {})
                    has_more = pagination.get('has_more', False)
                    page += 1
                else:
                    logger.warning(f"⚠️ Nenhum dado retornado da API na página {page}")
                    has_more = False
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Erro ao buscar times da API na página {page}: {e}")
                has_more = False
            except Exception as e:
                logger.error(f"❌ Erro inesperado ao buscar times da API na página {page}: {e}")
                has_more = False
                
        logger.info(f"🎉 Total de times encontrados: {len(all_teams)}")
        return all_teams

    def process_teams_data(self, teams_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processar dados dos times para inserção"""
        processed_teams = []
        for team in teams_data:
            processed_team = {
                'team_id': team.get('id'),
                'sport_id': team.get('sport_id'),
                'country_id': team.get('country_id'),
                'venue_id': team.get('venue_id'),
                'gender': team.get('gender'),
                'name': team.get('name', ''),
                'short_code': team.get('short_code'),
                'image_path': team.get('image_path'),
                'founded': team.get('founded'),
                'type': team.get('type'),
                'placeholder': team.get('placeholder', False),
                'last_played_at': team.get('last_played_at'),
                'venue_name': team.get('venue_name')  # Manter para compatibilidade
            }
            # Remover campos None para evitar erros de inserção/atualização
            processed_team = {k: v for k, v in processed_team.items() if v is not None}
            processed_teams.append(processed_team)
        return processed_teams

    def insert_teams_to_database(self, teams: List[Dict[str, Any]]):
        """Inserir ou atualizar times no banco de dados"""
        inserted_count = 0
        updated_count = 0
        
        logger.info(f"💾 Inserindo {len(teams)} times no banco...")

        for team in teams:
            team_id = team.get('team_id')
            if team_id is None:
                logger.warning(f"⚠️ Time sem team_id, pulando: {team.get('name')}")
                continue

            try:
                # Verificar se o time já existe
                existing = self.supabase.table('teams').select('team_id').eq('team_id', team_id).execute()
                
                if existing.data:
                    # Atualizar time existente
                    update_data = {
                        'name': team['name'],
                        'sport_id': team.get('sport_id'),
                        'country_id': team.get('country_id'),
                        'venue_id': team.get('venue_id'),
                        'gender': team.get('gender'),
                        'short_code': team.get('short_code'),
                        'image_path': team.get('image_path'),
                        'founded': team.get('founded'),
                        'type': team.get('type'),
                        'placeholder': team.get('placeholder', False),
                        'last_played_at': team.get('last_played_at'),
                        'venue_name': team.get('venue_name')
                    }
                    
                    # Remover campos None
                    update_data = {k: v for k, v in update_data.items() if v is not None}
                    
                    result = self.supabase.table('teams').update(update_data).eq('team_id', team_id).execute()
                    if result.data:
                        updated_count += 1
                    else:
                        logger.error(f"❌ Erro ao atualizar time {team_id}: {result.error}")
                else:
                    # Inserir novo time
                    result = self.supabase.table('teams').insert(team).execute()
                    if result.data:
                        inserted_count += 1
                    else:
                        logger.error(f"❌ Erro ao inserir time {team_id}: {result.error}")
            except Exception as e:
                logger.error(f"❌ Erro ao processar time {team_id} ({team.get('name')}): {e}")
                
        logger.info(f"✅ Enriquecimento concluído: {inserted_count} inseridos, {updated_count} atualizados")
        return inserted_count, updated_count

    def run(self):
        """Executar o processo de enriquecimento"""
        logger.info("🚀 Iniciando enriquecimento da tabela teams...")
        
        # Obter contagem inicial de times
        initial_count_response = self.supabase.table('teams').select('team_id', count='exact').execute()
        initial_count = initial_count_response.count if initial_count_response.count is not None else 0
        logger.info(f"📊 Times atuais: {initial_count}")

        teams_data = self.fetch_teams_from_api()
        if teams_data:
            processed_teams = self.process_teams_data(teams_data)
            logger.info(f"✅ {len(processed_teams)} times processados com sucesso")
            inserted, updated = self.insert_teams_to_database(processed_teams)
            
            # Obter contagem final de times
            final_count_response = self.supabase.table('teams').select('team_id', count='exact').execute()
            final_count = final_count_response.count if final_count_response.count is not None else 0

            logger.info("🎉 Enriquecimento concluído!")
            logger.info(f"📈 Times iniciais: {initial_count}")
            logger.info(f"📈 Times finais: {final_count}")
            logger.info(f"📈 Times adicionados/atualizados: {inserted + updated}")
        else:
            logger.warning("⚠️ Nenhum time para processar.")

if __name__ == "__main__":
    enricher = TeamsEnricher()
    enricher.run()
