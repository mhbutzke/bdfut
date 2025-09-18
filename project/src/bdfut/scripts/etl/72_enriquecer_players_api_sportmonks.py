#!/usr/bin/env python3
"""
Script para enriquecer tabela players com dados da API Sportmonks
Endpoint: /v3/football/players
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

class PlayersEnricher:
    """Classe para enriquecer tabela players com dados da API Sportmonks"""
    
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

    def fetch_players_from_api(self) -> List[Dict[str, Any]]:
        """Buscar jogadores da API Sportmonks com paginação"""
        all_players = []
        page = 1
        has_more = True
        
        logger.info("🔍 Buscando jogadores da API Sportmonks com paginação...")

        while has_more:
            try:
                logger.info(f"📄 Buscando página {page}...")
                url = "https://api.sportmonks.com/v3/football/players"
                params = {
                    'api_token': self.sportmonks_client.api_key,
                    'include': '',
                    'page': page
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data and 'data' in data:
                    players_on_page = data['data']
                    all_players.extend(players_on_page)
                    logger.info(f"✅ Página {page}: {len(players_on_page)} jogadores encontrados")
                    
                    # Verificar paginação
                    pagination = data.get('pagination', {})
                    has_more = pagination.get('has_more', False)
                    page += 1
                else:
                    logger.warning(f"⚠️ Nenhum dado retornado da API na página {page}")
                    has_more = False
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Erro ao buscar jogadores da API na página {page}: {e}")
                has_more = False
            except Exception as e:
                logger.error(f"❌ Erro inesperado ao buscar jogadores da API na página {page}: {e}")
                has_more = False
                
        logger.info(f"🎉 Total de jogadores encontrados: {len(all_players)}")
        return all_players

    def process_players_data(self, players_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processar dados dos jogadores para inserção"""
        processed_players = []
        for player in players_data:
            processed_player = {
                'player_id': player.get('id'),
                'sport_id': player.get('sport_id'),
                'country_id': player.get('country_id'),
                'city_id': player.get('city_id'),
                'common_name': player.get('common_name'),
                'firstname': player.get('firstname'),
                'lastname': player.get('lastname'),
                'name': player.get('name'),
                'display_name': player.get('display_name'),
                'nationality': player.get('nationality'),
                'position_id': player.get('position_id'),
                'position_name': player.get('position_name'),
                'date_of_birth': player.get('date_of_birth'),
                'height': player.get('height'),
                'weight': player.get('weight'),
                'image_path': player.get('image_path'),
                'gender': player.get('gender'),
                'shirt_number': player.get('shirt_number'),
                'preferred_foot': player.get('preferred_foot'),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            # Remover campos None para evitar erros de inserção/atualização
            processed_player = {k: v for k, v in processed_player.items() if v is not None}
            processed_players.append(processed_player)
        return processed_players

    def insert_players_to_database(self, players: List[Dict[str, Any]]):
        """Inserir ou atualizar jogadores no banco de dados"""
        inserted_count = 0
        updated_count = 0
        
        logger.info(f"💾 Inserindo {len(players)} jogadores no banco...")

        for player in players:
            player_id = player.get('player_id')
            if player_id is None:
                logger.warning(f"⚠️ Jogador sem player_id, pulando: {player.get('name')}")
                continue

            try:
                # Verificar se o jogador já existe
                existing = self.supabase.table('players').select('player_id').eq('player_id', player_id).execute()
                
                if existing.data:
                    # Atualizar jogador existente
                    result = self.supabase.table('players').update(player).eq('player_id', player_id).execute()
                    if result.data:
                        updated_count += 1
                    else:
                        logger.error(f"❌ Erro ao atualizar jogador {player_id}: {result.error}")
                else:
                    # Inserir novo jogador
                    result = self.supabase.table('players').insert(player).execute()
                    if result.data:
                        inserted_count += 1
                    else:
                        logger.error(f"❌ Erro ao inserir jogador {player_id}: {result.error}")
            except Exception as e:
                logger.error(f"❌ Erro ao processar jogador {player_id} ({player.get('name')}): {e}")
                
        logger.info(f"✅ Enriquecimento concluído: {inserted_count} inseridos, {updated_count} atualizados")
        return inserted_count, updated_count

    def run(self):
        """Executar o processo de enriquecimento"""
        logger.info("🚀 Iniciando enriquecimento da tabela players...")
        
        # Obter contagem inicial de jogadores
        initial_count_response = self.supabase.table('players').select('player_id', count='exact').execute()
        initial_count = initial_count_response.count if initial_count_response.count is not None else 0
        logger.info(f"📊 Jogadores atuais: {initial_count}")

        players_data = self.fetch_players_from_api()
        if players_data:
            processed_players = self.process_players_data(players_data)
            logger.info(f"✅ {len(processed_players)} jogadores processados com sucesso")
            inserted, updated = self.insert_players_to_database(processed_players)
            
            # Obter contagem final de jogadores
            final_count_response = self.supabase.table('players').select('player_id', count='exact').execute()
            final_count = final_count_response.count if final_count_response.count is not None else 0

            logger.info("🎉 Enriquecimento concluído!")
            logger.info(f"📈 Jogadores iniciais: {initial_count}")
            logger.info(f"📈 Jogadores finais: {final_count}")
            logger.info(f"📈 Jogadores adicionados/atualizados: {inserted + updated}")
        else:
            logger.warning("⚠️ Nenhum jogador para processar.")

if __name__ == "__main__":
    enricher = PlayersEnricher()
    enricher.run()
