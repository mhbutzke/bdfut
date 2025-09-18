#!/usr/bin/env python3
"""
Script para enriquecer tabela leagues com dados da API Sportmonks
Endpoint: /v3/football/leagues
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

class LeaguesEnricher:
    """Classe para enriquecer tabela leagues com dados da API Sportmonks"""
    
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
    
    def fetch_leagues_from_api(self) -> List[Dict[str, Any]]:
        """Buscar ligas da API Sportmonks com paginação"""
        try:
            logger.info("🔍 Buscando ligas da API Sportmonks com paginação...")
            
            import requests
            url = "https://api.sportmonks.com/v3/football/leagues"
            all_leagues = []
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
                
                leagues = data['data']
                if not leagues:
                    logger.info(f"✅ Página {page} vazia - fim da paginação")
                    break
                
                all_leagues.extend(leagues)
                logger.info(f"✅ Página {page}: {len(leagues)} ligas encontradas")
                
                # Verificar se há mais páginas
                pagination = data.get('pagination', {})
                if not pagination.get('has_more', False):
                    logger.info("✅ Última página alcançada")
                    break
                
                page += 1
                
                # Pequena pausa para respeitar rate limits
                time.sleep(0.1)
            
            logger.info(f"🎉 Total de ligas encontradas: {len(all_leagues)}")
            return all_leagues
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar ligas da API: {e}")
            return []
    
    def process_leagues_data(self, leagues_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processar dados das ligas para inserção"""
        processed_leagues = []
        
        for league in leagues_data:
            try:
                # Extrair dados do país se disponível
                country_data = league.get('country', {})
                country_name = country_data.get('name', '') if country_data else ''
                country_id = country_data.get('id') if country_data else None
                
                processed_league = {
                    'league_id': league.get('id'),  # A API retorna 'id', não 'league_id'
                    'sport_id': league.get('sport_id'),
                    'country_id': league.get('country_id'),  # Usar diretamente da API
                    'name': league.get('name', ''),
                    'active': league.get('active', True),
                    'short_code': league.get('short_code'),
                    'image_path': league.get('image_path', ''),
                    'type': league.get('type'),
                    'sub_type': league.get('sub_type'),
                    'last_played_at': league.get('last_played_at'),
                    'category': league.get('category'),
                    'has_jerseys': league.get('has_jerseys'),  # Usar diretamente da API
                    'country_name': country_name,  # Nome do país preenchido automaticamente
                    'logo_url': league.get('image_path', ''),  # Manter para compatibilidade
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Remover campos None
                processed_league = {k: v for k, v in processed_league.items() if v is not None}
                
                # Validar dados obrigatórios
                if processed_league['league_id'] and processed_league['name']:
                    processed_leagues.append(processed_league)
                else:
                    logger.warning(f"⚠️ Liga inválida ignorada: {league}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao processar liga {league}: {e}")
                continue
        
        logger.info(f"✅ {len(processed_leagues)} ligas processadas com sucesso")
        return processed_leagues
    
    def insert_leagues_to_database(self, leagues_data: List[Dict[str, Any]]) -> int:
        """Inserir ligas no banco de dados"""
        try:
            logger.info(f"💾 Inserindo {len(leagues_data)} ligas no banco...")
            
            inserted_count = 0
            updated_count = 0
            
            for league in leagues_data:
                try:
                    # Verificar se a liga já existe
                    existing = self.supabase.table('leagues').select('league_id').eq('league_id', league['league_id']).execute()
                    
                    if existing.data:
                        # Atualizar liga existente com todas as novas colunas
                        update_data = {
                            'name': league['name'],
                            'active': league['active'],
                            'updated_at': league['updated_at']
                        }
                        
                        # Adicionar campos opcionais se existirem
                        if 'sport_id' in league:
                            update_data['sport_id'] = league['sport_id']
                        if 'country_id' in league:
                            update_data['country_id'] = league['country_id']
                        if 'short_code' in league:
                            update_data['short_code'] = league['short_code']
                        if 'image_path' in league:
                            update_data['image_path'] = league['image_path']
                        if 'type' in league:
                            update_data['type'] = league['type']
                        if 'sub_type' in league:
                            update_data['sub_type'] = league['sub_type']
                        if 'last_played_at' in league:
                            update_data['last_played_at'] = league['last_played_at']
                        if 'category' in league:
                            update_data['category'] = league['category']
                        if 'has_jerseys' in league:
                            update_data['has_jerseys'] = league['has_jerseys']
                        if 'country_name' in league:
                            update_data['country_name'] = league['country_name']
                        if 'logo_url' in league:
                            update_data['logo_url'] = league['logo_url']
                        
                        result = self.supabase.table('leagues').update(update_data).eq('league_id', league['league_id']).execute()
                        
                        if result.data:
                            updated_count += 1
                            logger.debug(f"✅ Liga atualizada: {league['name']} (ID: {league['league_id']})")
                    else:
                        # Inserir nova liga
                        result = self.supabase.table('leagues').insert(league).execute()
                        
                        if result.data:
                            inserted_count += 1
                            logger.debug(f"✅ Liga inserida: {league['name']} (ID: {league['league_id']})")
                
                except Exception as e:
                    logger.error(f"❌ Erro ao inserir/atualizar liga {league['name']}: {e}")
                    continue
            
            logger.info(f"✅ Enriquecimento concluído: {inserted_count} inseridas, {updated_count} atualizadas")
            return inserted_count + updated_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao inserir ligas no banco: {e}")
            return 0
    
    def get_current_leagues_count(self) -> int:
        """Obter contagem atual de ligas"""
        try:
            result = self.supabase.table('leagues').select('league_id', count='exact').execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"❌ Erro ao contar ligas: {e}")
            return 0
    
    def run_enrichment(self):
        """Executar processo completo de enriquecimento"""
        try:
            logger.info("🚀 Iniciando enriquecimento da tabela leagues...")
            
            # Contar ligas atuais
            initial_count = self.get_current_leagues_count()
            logger.info(f"📊 Ligas atuais: {initial_count}")
            
            # Buscar dados da API
            leagues_data = self.fetch_leagues_from_api()
            
            if not leagues_data:
                logger.warning("⚠️ Nenhum dado obtido da API")
                return
            
            # Processar dados
            processed_leagues = self.process_leagues_data(leagues_data)
            
            if not processed_leagues:
                logger.warning("⚠️ Nenhuma liga processada")
                return
            
            # Inserir no banco
            enriched_count = self.insert_leagues_to_database(processed_leagues)
            
            # Contar ligas finais
            final_count = self.get_current_leagues_count()
            
            logger.info("🎉 Enriquecimento concluído!")
            logger.info(f"📈 Ligas iniciais: {initial_count}")
            logger.info(f"📈 Ligas finais: {final_count}")
            logger.info(f"📈 Ligas adicionadas/atualizadas: {enriched_count}")
            
        except Exception as e:
            logger.error(f"❌ Erro no processo de enriquecimento: {e}")
            raise

def main():
    """Função principal"""
    try:
        enricher = LeaguesEnricher()
        enricher.run_enrichment()
        
    except Exception as e:
        logger.error(f"❌ Erro na execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
