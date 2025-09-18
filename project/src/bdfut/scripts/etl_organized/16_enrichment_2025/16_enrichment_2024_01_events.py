#!/usr/bin/env python3
"""
Script para enriquecer fixtures de 2024 com eventos
Baseado no padrão testado e validado para 2025
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

class Events2024Enrichment:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 100  # Processar em lotes de 100
        self.delay_between_batches = 1  # 1 segundo entre lotes
        
    def get_fixtures_2024(self, limit: int = None):
        """Buscar fixtures de 2024 que não possuem eventos"""
        try:
            # Buscar fixtures de 2024 finalizadas
            query = self.supabase.client.table('fixtures').select(
                'fixture_id, match_date, home_team_name, away_team_name'
            ).gte('match_date', '2024-01-01').lt('match_date', '2025-01-01').in_(
                'status', ['FT', 'FT_PEN', 'AET']
            ).order('match_date', desc=True)
            
            if limit:
                query = query.limit(limit)
                
            response = query.execute()
            
            if response.data:
                logger.info(f"📊 Encontradas {len(response.data)} fixtures de 2024")
                return response.data
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixtures de 2024: {e}")
            return []
    
    def check_existing_events(self, sportmonks_id: int):
        """Verificar se já existem eventos para esta fixture"""
        try:
            response = self.supabase.client.table('match_events').select(
                'id'
            ).eq('fixture_id', sportmonks_id).limit(1).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar eventos existentes: {e}")
            return False
    
    def enrich_fixture_events(self, fixture):
        """Enriquecer uma fixture com eventos"""
        try:
            fixture_id = fixture['fixture_id']
            sportmonks_id = fixture['fixture_id']  # fixture_id é o sportmonks_id
            
            logger.info(f"🔍 Processando fixture {fixture_id} ({fixture['home_team_name']} vs {fixture['away_team_name']})")
            
            # Verificar se já existem eventos
            if self.check_existing_events(sportmonks_id):
                logger.info(f"   ⏭️  Eventos já existem, pulando")
                return {'status': 'ignored', 'reason': 'already_has_events'}
            
            # Buscar eventos da API
            events = self.sportmonks.get_events_by_fixture(sportmonks_id)
            
            if not events:
                logger.info(f"   📭 Nenhum evento encontrado na API")
                return {'status': 'no_events', 'reason': 'api_no_events'}
            
            logger.info(f"   📊 {len(events)} eventos encontrados na API")
            
            # Preparar dados para inserção
            events_data = []
            for i, event in enumerate(events):
                event_data = {
                    'id': f"{sportmonks_id}_{i+1}",
                    'fixture_id': sportmonks_id,  # Usar sportmonks_id como fixture_id
                    'type_id': event.get('type_id'),
                    'event_type': event.get('type', {}).get('name') if event.get('type') else None,
                    'minute': event.get('minute'),
                    'extra_minute': event.get('extra_minute'),
                    'team_id': event.get('team_id'),
                    'player_id': event.get('player_id'),
                    'related_player_id': event.get('related_player_id'),
                    'player_name': event.get('player', {}).get('name') if event.get('player') else None,
                    'period_id': event.get('period_id'),
                    'result': event.get('result'),
                    'var': event.get('var'),
                    'var_reason': event.get('var_reason'),
                    'coordinates': json.dumps(event.get('coordinates')) if event.get('coordinates') else None,
                    'assist_id': event.get('assist_id'),
                    'assist_name': event.get('assist', {}).get('name') if event.get('assist') else None,
                    'injured': event.get('injured'),
                    'on_bench': event.get('on_bench'),
                    'created_at': datetime.now().isoformat()
                }
                events_data.append(event_data)
            
            # Inserir eventos no banco
            if events_data:
                response = self.supabase.client.table('match_events').insert(events_data).execute()
                
                if response.data:
                    logger.info(f"   ✅ {len(response.data)} eventos inseridos com sucesso")
                    return {
                        'status': 'success',
                        'events_count': len(response.data),
                        'fixture_id': fixture_id,
                        'sportmonks_id': sportmonks_id
                    }
                else:
                    logger.error(f"   ❌ Erro ao inserir eventos: {response}")
                    return {'status': 'error', 'reason': 'insert_failed'}
            
            return {'status': 'no_events', 'reason': 'no_data_to_insert'}
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer fixture {fixture_id}: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    def process_batch(self, fixtures):
        """Processar um lote de fixtures"""
        results = {
            'success': 0,
            'ignored': 0,
            'no_events': 0,
            'errors': 0,
            'total_events': 0
        }
        
        for fixture in fixtures:
            result = self.enrich_fixture_events(fixture)
            
            if result['status'] == 'success':
                results['success'] += 1
                results['total_events'] += result.get('events_count', 0)
            elif result['status'] == 'ignored':
                results['ignored'] += 1
            elif result['status'] == 'no_events':
                results['no_events'] += 1
            else:
                results['errors'] += 1
        
        return results
    
    def run_enrichment(self, max_fixtures: int = 1000):
        """Executar enriquecimento de fixtures de 2024"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO DE EVENTOS - 2024")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Buscar fixtures de 2024
        fixtures = self.get_fixtures_2024(max_fixtures)
        
        if not fixtures:
            logger.warning("⚠️  Nenhuma fixture de 2024 encontrada")
            return
        
        logger.info(f"📊 Total de fixtures a processar: {len(fixtures)}")
        
        # Processar em lotes
        total_results = {
            'success': 0,
            'ignored': 0,
            'no_events': 0,
            'errors': 0,
            'total_events': 0
        }
        
        for i in range(0, len(fixtures), self.batch_size):
            batch = fixtures[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(fixtures) + self.batch_size - 1) // self.batch_size
            
            logger.info(f"📦 Processando lote {batch_num}/{total_batches} ({len(batch)} fixtures)")
            
            batch_results = self.process_batch(batch)
            
            # Atualizar totais
            for key in total_results:
                total_results[key] += batch_results[key]
            
            # Log do progresso
            logger.info(f"   ✅ Sucessos: {batch_results['success']}")
            logger.info(f"   ⏭️  Ignorados: {batch_results['ignored']}")
            logger.info(f"   📭 Sem eventos: {batch_results['no_events']}")
            logger.info(f"   ❌ Erros: {batch_results['errors']}")
            logger.info(f"   📊 Eventos coletados: {batch_results['total_events']}")
            
            # Delay entre lotes
            if i + self.batch_size < len(fixtures):
                logger.info(f"⏳ Aguardando {self.delay_between_batches}s antes do próximo lote...")
                time.sleep(self.delay_between_batches)
        
        # Relatório final
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("🎉 ENRIQUECIMENTO CONCLUÍDO - 2024")
        logger.info("=" * 60)
        logger.info(f"⏱️  Duração total: {duration}")
        logger.info(f"📊 Fixtures processadas: {len(fixtures)}")
        logger.info(f"✅ Sucessos: {total_results['success']}")
        logger.info(f"⏭️  Ignorados: {total_results['ignored']}")
        logger.info(f"📭 Sem eventos: {total_results['no_events']}")
        logger.info(f"❌ Erros: {total_results['errors']}")
        logger.info(f"📊 Total de eventos coletados: {total_results['total_events']}")
        
        if total_results['success'] > 0:
            avg_events = total_results['total_events'] / total_results['success']
            logger.info(f"📈 Média de eventos por fixture: {avg_events:.1f}")

def main():
    """Função principal"""
    try:
        enrichment = Events2024Enrichment()
        enrichment.run_enrichment(max_fixtures=1000)  # Processar até 1000 fixtures
        
    except Exception as e:
        logger.error(f"❌ Erro na execução principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
