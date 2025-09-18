#!/usr/bin/env python3
"""
Script para enriquecimento completo de stages
Busca todas as páginas da API Sportmonks e enriquece a tabela
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

class FullStagesEnrichment:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 50  # Processar em lotes de 50
        
    def get_all_stages_from_api(self):
        """Buscar todas as páginas de stages da API Sportmonks"""
        all_stages = []
        page = 1
        per_page = 25  # API retorna 25 por página
        
        try:
            logger.info("📡 Buscando todas as páginas de stages da API...")
            
            while True:
                logger.info(f"   📄 Buscando página {page}...")
                
                params = {
                    'page': page,
                    'per_page': per_page
                }
                
                response = self.sportmonks._make_request('/stages', params, 'stages')
                
                if response and response.get('data'):
                    stages = response['data']
                    all_stages.extend(stages)
                    logger.info(f"   ✅ Página {page}: {len(stages)} stages recebidos")
                    
                    # Se recebemos menos que per_page, é a última página
                    if len(stages) < per_page:
                        logger.info(f"   📄 Última página alcançada (página {page})")
                        break
                    
                    page += 1
                    
                    # Rate limiting
                    time.sleep(0.5)
                else:
                    logger.warning(f"   ⚠️ Nenhum dado recebido na página {page}")
                    break
            
            logger.info(f"✅ Total de stages coletados: {len(all_stages)}")
            return all_stages
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar stages da API: {e}")
            return all_stages
    
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
    
    def upsert_stages_batch(self, stages_data):
        """Inserir ou atualizar um lote de stages no banco"""
        try:
            if not stages_data:
                return {'success': 0, 'errors': 0}
            
            logger.info(f"💾 Inserindo/atualizando lote de {len(stages_data)} stages...")
            
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
    
    def process_all_stages(self, api_stages):
        """Processar todos os stages coletados"""
        results = {'success': 0, 'errors': 0, 'processed': 0}
        
        # Processar em lotes
        for i in range(0, len(api_stages), self.batch_size):
            batch = api_stages[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(api_stages) + self.batch_size - 1) // self.batch_size
            
            logger.info(f"📦 Processando lote {batch_num}/{total_batches} ({len(batch)} stages)")
            
            # Preparar dados do lote
            batch_data = []
            for api_stage in batch:
                stage_data = self.prepare_stage_data(api_stage)
                if stage_data:
                    batch_data.append(stage_data)
            
            # Inserir/atualizar lote
            if batch_data:
                batch_result = self.upsert_stages_batch(batch_data)
                results['success'] += batch_result['success']
                results['errors'] += batch_result['errors']
                results['processed'] += len(batch_data)
                
                # Log do progresso
                logger.info(f"   ✅ Sucessos: {batch_result['success']}")
                logger.info(f"   ❌ Erros: {batch_result['errors']}")
                logger.info(f"   📊 Processados: {len(batch_data)}")
            else:
                logger.warning(f"   ⚠️ Nenhum dado válido no lote {batch_num}")
                results['errors'] += len(batch)
            
            # Pausa entre lotes
            if i + self.batch_size < len(api_stages):
                logger.info("⏸️ Pausa de 1 segundo entre lotes...")
                time.sleep(1)
        
        return results
    
    def run_full_enrichment(self):
        """Executar enriquecimento completo de stages"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO COMPLETO DE STAGES")
        logger.info("=" * 70)
        
        # Buscar todos os stages da API
        api_stages = self.get_all_stages_from_api()
        
        if not api_stages:
            logger.warning("⚠️ Nenhum stage encontrado para processar")
            return
        
        logger.info(f"📊 Processando {len(api_stages)} stages")
        
        # Processar todos os stages
        total_results = self.process_all_stages(api_stages)
        
        # Relatório final
        logger.info("=" * 70)
        logger.info("📊 RELATÓRIO FINAL - ENRIQUECIMENTO COMPLETO DE STAGES")
        logger.info("=" * 70)
        logger.info(f"📈 Stages processados: {total_results['processed']}")
        logger.info(f"✅ Sucessos: {total_results['success']}")
        logger.info(f"❌ Erros: {total_results['errors']}")
        
        success_rate = (total_results['success'] / total_results['processed']) * 100 if total_results['processed'] > 0 else 0
        logger.info(f"🎯 Taxa de sucesso: {success_rate:.1f}%")
        
        # Verificar total no banco
        try:
            response = self.supabase.client.table('stages').select('stage_id', count='exact').execute()
            logger.info(f"📊 Total de stages no banco após enriquecimento: {response.count}")
        except Exception as e:
            logger.error(f"❌ Erro ao verificar total no banco: {e}")
        
        logger.info("🎉 ENRIQUECIMENTO COMPLETO DE STAGES CONCLUÍDO!")

def main():
    """Função principal"""
    enrichment = FullStagesEnrichment()
    enrichment.run_full_enrichment()

if __name__ == "__main__":
    main()
