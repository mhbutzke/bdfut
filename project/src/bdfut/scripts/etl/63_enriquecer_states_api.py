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
            self.config = Config()
            self.sportmonks = SportmonksClient()
            self.supabase = create_client(self.config.SUPABASE_URL, self.config.SUPABASE_KEY)
            logger.info("✅ Clientes inicializados com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar clientes: {e}")
            raise
    
    def get_states_from_api(self) -> List[Dict]:
        """Buscar todos os states da API Sportmonks"""
        try:
            logger.info("🔍 Buscando states da API Sportmonks...")
            
            response = self.sportmonks._make_request(
                '/states',
                {'include': ''}
            )
            
            states_data = response.get('data', [])
            logger.info(f"📊 {len(states_data)} states encontrados na API")
            
            return states_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar states da API: {e}")
            return []
    
    def process_state_data(self, state_data: Dict) -> Dict:
        """Processar dados de um state para inserção no banco"""
        try:
            processed_state = {
                'sportmonks_id': state_data.get('id'),
                'name': state_data.get('name'),
                'short_name': state_data.get('short_name'),
                'developer_name': state_data.get('developer_name'),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            return processed_state
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar state {state_data.get('id', 'unknown')}: {e}")
            return {}
    
    def save_states_to_database(self, states: List[Dict]) -> Dict[str, int]:
        """Salvar states no banco de dados"""
        stats = {
            'total': len(states),
            'saved': 0,
            'updated': 0,
            'errors': 0
        }
        
        try:
            logger.info(f"💾 Salvando {len(states)} states no banco...")
            
            # Processar cada state
            processed_states = []
            for state_data in states:
                processed_state = self.process_state_data(state_data)
                if processed_state:
                    processed_states.append(processed_state)
            
            if not processed_states:
                logger.warning("⚠️ Nenhum state válido para salvar")
                return stats
            
            # Salvar em lotes para evitar timeout
            batch_size = 50
            for i in range(0, len(processed_states), batch_size):
                batch = processed_states[i:i + batch_size]
                
                try:
                    # Usar upsert para evitar duplicatas
                    result = self.supabase.table('states').upsert(
                        batch, 
                        on_conflict='sportmonks_id'
                    ).execute()
                    
                    stats['saved'] += len(batch)
                    logger.info(f"✅ Lote {i//batch_size + 1} salvo: {len(batch)} states")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao salvar lote {i//batch_size + 1}: {e}")
                    stats['errors'] += len(batch)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erro geral ao salvar states: {e}")
            stats['errors'] = stats['total']
            return stats
    
    def get_current_states_count(self) -> int:
        """Obter contagem atual de states no banco"""
        try:
            response = self.supabase.table('states').select('id', count='exact').execute()
            return response.count
        except Exception as e:
            logger.error(f"❌ Erro ao contar states: {e}")
            return 0
    
    def get_enrichment_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de enriquecimento"""
        try:
            # Contagem atual
            current_count = self.get_current_states_count()
            
            # Buscar states da API
            api_states = self.get_states_from_api()
            api_count = len(api_states)
            
            return {
                'current_count': current_count,
                'api_count': api_count,
                'potential_new': max(0, api_count - current_count),
                'coverage_percentage': round((current_count / api_count) * 100, 2) if api_count > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 ENRIQUECENDO TABELA STATES COM API SPORTMONKS")
    logger.info("=" * 80)
    
    try:
        # Inicializar enricher
        enricher = StatesEnricher()
        
        # Obter estatísticas iniciais
        logger.info("📊 Estatísticas iniciais:")
        initial_stats = enricher.get_enrichment_stats()
        for key, value in initial_stats.items():
            logger.info(f"   • {key}: {value}")
        
        # Buscar states da API
        api_states = enricher.get_states_from_api()
        if not api_states:
            logger.error("❌ Nenhum state encontrado na API")
            return
        
        logger.info(f"🔍 {len(api_states)} states encontrados na API")
        
        # Salvar states no banco
        logger.info("💾 Salvando states no banco...")
        save_stats = enricher.save_states_to_database(api_states)
        
        # Relatório final
        logger.info("=" * 80)
        logger.info("📊 RELATÓRIO FINAL")
        logger.info("=" * 80)
        logger.info(f"   • States processados: {save_stats['total']}")
        logger.info(f"   • States salvos: {save_stats['saved']}")
        logger.info(f"   • Erros: {save_stats['errors']}")
        
        # Estatísticas finais
        final_stats = enricher.get_enrichment_stats()
        logger.info("📊 Estatísticas finais:")
        for key, value in final_stats.items():
            logger.info(f"   • {key}: {value}")
        
        logger.info("=" * 80)
        logger.info("✅ ENRIQUECIMENTO DE STATES CONCLUÍDO!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return

if __name__ == "__main__":
    main()
