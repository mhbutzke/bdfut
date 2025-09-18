#!/usr/bin/env python3
"""
Script corrigido para enriquecimento de lineups
Usando IDs sequenciais simples para evitar overflow de integer
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
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

class LineupsEnrichmentFixed:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 100
        self.request_delay = 1
        
        # Contador para IDs sequenciais
        self.next_id = self._get_next_available_id()
        
    def _get_next_available_id(self):
        """Obter o próximo ID disponível para lineups"""
        try:
            response = self.supabase.client.table('match_lineups').select('id').order('id', desc=True).limit(1).execute()
            if response.data:
                # Pegar o maior ID existente e adicionar 1
                max_id = max([int(row['id']) for row in response.data if str(row['id']).isdigit()])
                return max_id + 1
            return 1
        except Exception as e:
            logger.error(f"Erro ao obter próximo ID: {e}")
            return 1
    
    def get_fixtures_without_lineups(self, limit: int = None):
        """Buscar fixtures finalizadas que não possuem lineups"""
        try:
            # Primeiro, buscar IDs de fixtures que já têm lineups
            lineups_response = self.supabase.client.from_('match_lineups').select('fixture_id').execute()
            existing_fixture_ids = {row['fixture_id'] for row in lineups_response.data} if lineups_response.data else set()
            
            # Buscar todas as fixtures finalizadas
            all_fixtures_response = self.supabase.client.from_('fixtures').select(
                'fixture_id, match_date, home_team_name, away_team_name'
            ).in_('status', ['FT', 'FT_PEN', 'AET']).order('match_date', desc=True).execute()
            
            if not all_fixtures_response.data:
                return []
            
            # Filtrar fixtures que não têm lineups
            fixtures_without_lineups = []
            for fixture in all_fixtures_response.data:
                if fixture['fixture_id'] not in existing_fixture_ids:
                    fixtures_without_lineups.append(fixture)
                    if limit and len(fixtures_without_lineups) >= limit:
                        break
            
            logger.info(f"📊 {len(fixtures_without_lineups)} fixtures encontradas para processamento")
            return fixtures_without_lineups
            
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures sem lineups: {e}")
            return []
    
    def check_existing_lineups(self, fixture_id: int) -> bool:
        """Verificar se já existem lineups para uma fixture"""
        try:
            response = self.supabase.client.table('match_lineups').select('id').eq('fixture_id', fixture_id).limit(1).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Erro ao verificar lineups existentes para fixture {fixture_id}: {e}")
            return False
    
    def enrich_fixture_lineups(self, fixture):
        """Enriquecer uma fixture com lineups"""
        try:
            fixture_id = fixture['fixture_id']
            
            logger.info(f"🔍 Processando fixture {fixture_id} ({fixture['home_team_name']} vs {fixture['away_team_name']})")
            
            # Buscar lineups da API
            lineups = self.sportmonks.get_lineups_by_fixture(fixture_id)
            
            if not lineups:
                logger.info(f"   📭 Nenhum lineup encontrado na API")
                return {'status': 'no_lineups', 'reason': 'api_no_lineups'}
            
            logger.info(f"   📊 {len(lineups)} lineups encontrados na API")
            
            # Preparar dados para inserção
            lineups_data = []
            for i, lineup in enumerate(lineups):
                lineup_data = {
                    'id': self.next_id,  # Usar ID sequencial simples
                    'fixture_id': fixture_id,
                    'team_id': lineup.get('team_id'),
                    'player_id': lineup.get('player_id'),
                    'position_id': lineup.get('position_id'),
                    'formation_field': lineup.get('formation_field'),
                    'type_id': lineup.get('type_id'),
                    'formation_position': lineup.get('formation_position'),
                    'player_name': lineup.get('player_name'),
                    'jersey_number': lineup.get('jersey_number'),
                    'created_at': datetime.now().isoformat()
                }
                lineups_data.append(lineup_data)
                self.next_id += 1  # Incrementar para próximo registro
            
            # Inserir/Atualizar lineups no Supabase
            if lineups_data:
                response = self.supabase.client.table('match_lineups').upsert(lineups_data, on_conflict='id').execute()
                if response.data:
                    logger.info(f"   ✅ {len(response.data)} lineups inseridos/atualizados")
                    return {'status': 'success', 'lineups_count': len(response.data)}
                else:
                    logger.warning(f"   ⚠️ Nenhum lineup inserido/atualizado, resposta vazia")
                    return {'status': 'no_insert', 'reason': 'empty_response'}
            
            return {'status': 'no_data', 'reason': 'no_lineups_data'}
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer fixture {fixture_id}: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    def run_enrichment(self, limit: int = None):
        """Executar enriquecimento de lineups"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO DE LINEUPS")
        logger.info("=" * 50)
        
        fixtures_to_process = self.get_fixtures_without_lineups(limit)
        
        if not fixtures_to_process:
            logger.warning("⚠️ Nenhuma fixture encontrada para enriquecimento")
            return
        
        logger.info(f"📊 {len(fixtures_to_process)} fixtures para processar")
        
        processed_count = 0
        successful_count = 0
        error_count = 0
        lineups_inserted = 0
        
        start_time = time.time()
        
        for i, fixture in enumerate(fixtures_to_process):
            try:
                # Verificar se já tem lineups
                if self.check_existing_lineups(fixture['fixture_id']):
                    logger.info(f"⏭️ Fixture {fixture['fixture_id']} já possui lineups, pulando...")
                    continue
                
                # Enriquecer fixture
                result = self.enrich_fixture_lineups(fixture)
                
                processed_count += 1
                
                if result['status'] == 'success':
                    successful_count += 1
                    lineups_inserted += result.get('lineups_count', 0)
                elif result['status'] == 'error':
                    error_count += 1
                
                # Rate limiting
                if i < len(fixtures_to_process) - 1:  # Não aguardar na última iteração
                    time.sleep(self.request_delay)
                
                # Log de progresso a cada 10 fixtures
                if processed_count % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = processed_count / (elapsed / 60) if elapsed > 0 else 0
                    eta = (len(fixtures_to_process) - processed_count) / rate if rate > 0 else 0
                    
                    logger.info(f"\n📊 PROGRESSO: {processed_count}/{len(fixtures_to_process)} ({processed_count/len(fixtures_to_process)*100:.1f}%)")
                    logger.info(f"⏱️ Tempo decorrido: {elapsed/60:.1f} minutos")
                    logger.info(f"🚀 Taxa: {rate:.1f} fixtures/minuto")
                    logger.info(f"⏳ ETA: {eta:.1f} minutos")
                    logger.info(f"👥 Lineups inseridos: {lineups_inserted}")
                    logger.info(f"❌ Erros: {error_count}")
                
            except Exception as e:
                logger.error(f"❌ Erro inesperado ao processar fixture {fixture['fixture_id']}: {e}")
                error_count += 1
                continue
        
        # Relatório final
        total_time = time.time() - start_time
        logger.info(f"\n🎉 ENRIQUECIMENTO DE LINEUPS CONCLUÍDO!")
        logger.info("=" * 50)
        logger.info(f"⏱️ Tempo total: {total_time/60:.1f} minutos")
        logger.info(f"📊 Fixtures processadas: {processed_count}")
        logger.info(f"👥 Lineups inseridos: {lineups_inserted}")
        logger.info(f"❌ Erros encontrados: {error_count}")
        logger.info(f"🚀 Taxa média: {processed_count/(total_time/60):.1f} fixtures/minuto")

def main():
    """Função principal"""
    enrichment = LineupsEnrichmentFixed()
    
    # Executar enriquecimento com limite de 1000 fixtures para teste
    enrichment.run_enrichment(limit=1000)

if __name__ == "__main__":
    main()
