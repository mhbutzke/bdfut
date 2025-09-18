#!/usr/bin/env python3
"""
Script para enriquecer a tabela stages com dados da API Sportmonks
Baseado na estrutura correta fornecida pelo usuário
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import time
import logging

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StagesEnrichment:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 50  # Processar em lotes de 50
        
    def get_stages_from_api(self, limit: int = None):
        """Buscar stages da API Sportmonks"""
        try:
            logger.info("📡 Buscando stages da API Sportmonks...")
            
            params = {}
            if limit:
                params['per_page'] = limit
                
            response = self.sportmonks._make_request('/stages', params, 'stages')
            
            if response and response.get('data'):
                stages = response['data']
                logger.info(f"✅ {len(stages)} stages recebidos da API")
                return stages
            else:
                logger.warning("⚠️ Nenhum stage recebido da API")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar stages da API: {e}")
            return []
    
    def prepare_stage_data(self, api_stage):
        """Preparar dados do stage para inserção no banco"""
        try:
            # Mapear dados da API para nossa estrutura
            stage_data = {
                'stage_id': api_stage.get('id'),  # Usar stage_id como chave primária
                'sport_id': api_stage.get('sport_id'),
                'league_id': api_stage.get('league_id'),
                'season_id': api_stage.get('season_id'),
                'type_id': api_stage.get('type_id'),
                'name': api_stage.get('name'),
                'sort_order': api_stage.get('sort_order'),
                'finished': api_stage.get('finished'),
                'is_current': api_stage.get('is_current'),
                'starting_at': api_stage.get('starting_at'),
                'ending_at': api_stage.get('ending_at'),
                'games_in_current_week': api_stage.get('games_in_current_week'),
                'tie_breaker_rule_id': api_stage.get('tie_breaker_rule_id'),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            return stage_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao preparar dados do stage: {e}")
            return None
    
    def upsert_stages(self, stages_data):
        """Inserir ou atualizar stages no banco"""
        try:
            if not stages_data:
                return {'success': 0, 'errors': 0}
            
            logger.info(f"💾 Inserindo/atualizando {len(stages_data)} stages...")
            
            response = self.supabase.client.table('stages').upsert(
                stages_data, 
                on_conflict='stage_id'
            ).execute()
            
            if response.data:
                logger.info(f"✅ {len(response.data)} stages inseridos/atualizados com sucesso")
                return {'success': len(response.data), 'errors': 0}
            else:
                logger.error("❌ Erro ao inserir stages")
                return {'success': 0, 'errors': len(stages_data)}
                
        except Exception as e:
            logger.error(f"❌ Erro ao inserir stages: {e}")
            return {'success': 0, 'errors': len(stages_data)}
    
    def process_batch(self, api_stages):
        """Processar um lote de stages"""
        results = {'success': 0, 'errors': 0, 'processed': 0}
        
        for api_stage in api_stages:
            try:
                # Preparar dados
                stage_data = self.prepare_stage_data(api_stage)
                
                if stage_data:
                    # Inserir/atualizar
                    result = self.upsert_stages([stage_data])
                    results['success'] += result['success']
                    results['errors'] += result['errors']
                    results['processed'] += 1
                    
                    logger.info(f"   📊 Stage {stage_data['stage_id']}: {stage_data['name']}")
                else:
                    results['errors'] += 1
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar stage: {e}")
                results['errors'] += 1
        
        return results
    
    def run_enrichment(self, limit: int = 100):
        """Executar enriquecimento de stages"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO DE STAGES")
        logger.info("=" * 60)
        
        # Buscar stages da API
        api_stages = self.get_stages_from_api(limit)
        
        if not api_stages:
            logger.warning("⚠️ Nenhum stage encontrado para processar")
            return
        
        logger.info(f"📊 Processando {len(api_stages)} stages")
        
        # Processar em lotes
        total_results = {'success': 0, 'errors': 0, 'processed': 0}
        
        for i in range(0, len(api_stages), self.batch_size):
            batch = api_stages[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(api_stages) + self.batch_size - 1) // self.batch_size
            
            logger.info(f"📦 Processando lote {batch_num}/{total_batches} ({len(batch)} stages)")
            
            batch_results = self.process_batch(batch)
            
            # Atualizar resultados totais
            for key in total_results:
                total_results[key] += batch_results[key]
            
            # Log do progresso
            logger.info(f"   ✅ Sucessos: {batch_results['success']}")
            logger.info(f"   ❌ Erros: {batch_results['errors']}")
            logger.info(f"   📊 Processados: {batch_results['processed']}")
            
            # Pausa entre lotes
            if i + self.batch_size < len(api_stages):
                logger.info("⏸️ Pausa de 1 segundo entre lotes...")
                time.sleep(1)
        
        # Relatório final
        logger.info("=" * 60)
        logger.info("📊 RELATÓRIO FINAL - ENRIQUECIMENTO STAGES")
        logger.info("=" * 60)
        logger.info(f"📈 Stages processados: {total_results['processed']}")
        logger.info(f"✅ Sucessos: {total_results['success']}")
        logger.info(f"❌ Erros: {total_results['errors']}")
        
        success_rate = (total_results['success'] / total_results['processed']) * 100 if total_results['processed'] > 0 else 0
        logger.info(f"🎯 Taxa de sucesso: {success_rate:.1f}%")
        
        logger.info("🎉 ENRIQUECIMENTO DE STAGES CONCLUÍDO!")

def main():
    """Função principal"""
    enrichment = StagesEnrichment()
    enrichment.run_enrichment(limit=100)  # Processar 100 stages

if __name__ == "__main__":
    main()
