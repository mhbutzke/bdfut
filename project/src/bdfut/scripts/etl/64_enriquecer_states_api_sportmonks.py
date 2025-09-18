#!/usr/bin/env python3
"""
Script para enriquecer tabela states com dados da API Sportmonks
Endpoint: /v3/football/states
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

class StatesEnricher:
    """Classe para enriquecer tabela states com dados da API Sportmonks"""
    
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
    
    def fetch_states_from_api(self) -> List[Dict[str, Any]]:
        """Buscar estados da API Sportmonks"""
        try:
            logger.info("🔍 Buscando estados da API Sportmonks...")
            
            # Fazer chamada para o endpoint states
            url = f"{self.sportmonks_client.base_url}/v3/football/states"
            params = {
                'api_token': self.sportmonks_client.api_key,
                'include': ''
            }
            
            response = self.sportmonks_client._make_request('/states', params=params)
            
            if response and 'data' in response:
                states = response['data']
                logger.info(f"✅ Encontrados {len(states)} estados na API")
                return states
            else:
                logger.warning("⚠️ Nenhum dado retornado da API")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar estados da API: {e}")
            return []
    
    def process_states_data(self, states_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processar dados dos estados para inserção"""
        processed_states = []
        
        for state in states_data:
            try:
                processed_state = {
                    'state_id': state.get('id'),
                    'name': state.get('name', ''),
                    'short_name': state.get('short_name', ''),
                    'developer_name': state.get('developer_name', ''),
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Validar dados obrigatórios
                if processed_state['state_id'] and processed_state['name']:
                    processed_states.append(processed_state)
                else:
                    logger.warning(f"⚠️ Estado inválido ignorado: {state}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao processar estado {state}: {e}")
                continue
        
        logger.info(f"✅ {len(processed_states)} estados processados com sucesso")
        return processed_states
    
    def insert_states_to_database(self, states_data: List[Dict[str, Any]]) -> int:
        """Inserir estados no banco de dados"""
        try:
            logger.info(f"💾 Inserindo {len(states_data)} estados no banco...")
            
            inserted_count = 0
            updated_count = 0
            
            for state in states_data:
                try:
                    # Verificar se o estado já existe
                    existing = self.supabase.table('states').select('state_id').eq('state_id', state['state_id']).execute()
                    
                    if existing.data:
                        # Atualizar estado existente
                        result = self.supabase.table('states').update({
                            'name': state['name'],
                            'short_name': state['short_name'],
                            'developer_name': state['developer_name'],
                            'updated_at': state['updated_at']
                        }).eq('state_id', state['state_id']).execute()
                        
                        if result.data:
                            updated_count += 1
                            logger.debug(f"✅ Estado atualizado: {state['name']} (ID: {state['state_id']})")
                    else:
                        # Inserir novo estado
                        result = self.supabase.table('states').insert(state).execute()
                        
                        if result.data:
                            inserted_count += 1
                            logger.debug(f"✅ Estado inserido: {state['name']} (ID: {state['state_id']})")
                
                except Exception as e:
                    logger.error(f"❌ Erro ao inserir/atualizar estado {state['name']}: {e}")
                    continue
            
            logger.info(f"✅ Enriquecimento concluído: {inserted_count} inseridos, {updated_count} atualizados")
            return inserted_count + updated_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao inserir estados no banco: {e}")
            return 0
    
    def get_current_states_count(self) -> int:
        """Obter contagem atual de estados"""
        try:
            result = self.supabase.table('states').select('state_id', count='exact').execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"❌ Erro ao contar estados: {e}")
            return 0
    
    def run_enrichment(self):
        """Executar processo completo de enriquecimento"""
        try:
            logger.info("🚀 Iniciando enriquecimento da tabela states...")
            
            # Contar estados atuais
            initial_count = self.get_current_states_count()
            logger.info(f"📊 Estados atuais: {initial_count}")
            
            # Buscar dados da API
            states_data = self.fetch_states_from_api()
            
            if not states_data:
                logger.warning("⚠️ Nenhum dado obtido da API")
                return
            
            # Processar dados
            processed_states = self.process_states_data(states_data)
            
            if not processed_states:
                logger.warning("⚠️ Nenhum estado processado")
                return
            
            # Inserir no banco
            enriched_count = self.insert_states_to_database(processed_states)
            
            # Contar estados finais
            final_count = self.get_current_states_count()
            
            logger.info("🎉 Enriquecimento concluído!")
            logger.info(f"📈 Estados iniciais: {initial_count}")
            logger.info(f"📈 Estados finais: {final_count}")
            logger.info(f"📈 Estados adicionados/atualizados: {enriched_count}")
            
        except Exception as e:
            logger.error(f"❌ Erro no processo de enriquecimento: {e}")
            raise

def main():
    """Função principal"""
    try:
        enricher = StatesEnricher()
        enricher.run_enrichment()
        
    except Exception as e:
        logger.error(f"❌ Erro na execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
