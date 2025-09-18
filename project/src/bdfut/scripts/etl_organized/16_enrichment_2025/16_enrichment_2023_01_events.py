#!/usr/bin/env python3
"""
Script para enriquecer fixtures de 2023 com eventos
Baseado no padrão testado e validado para 2024 e 2025
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

class Events2023Enrichment:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 100  # Processar em lotes de 100
        
    def get_fixtures_2023(self, limit: int = None):
        """Buscar fixtures de 2023 que não possuem eventos"""
        try:
            # Buscar fixtures de 2023 finalizadas
            query = self.supabase.client.table('fixtures').select(
                'fixture_id, match_date, home_team_name, away_team_name'
            ).gte('match_date', '2023-01-01').lt('match_date', '2024-01-01').in_(
                'status', ['FT', 'FT_PEN', 'AET']
            ).order('match_date', desc=True)
            
            if limit:
                query = query.limit(limit)
                
            response = query.execute()
            
            if response.data:
                logger.info(f"📊 Encontradas {len(response.data)} fixtures de 2023")
                return response.data
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixtures de 2023: {e}")
            return []
    
    def check_existing_events(self, fixture_id):
        """Verificar se já existem eventos para uma fixture"""
        try:
            response = self.supabase.client.table('match_events').select(
                'id'
            ).eq('fixture_id', fixture_id).limit(1).execute()
            
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
            if self.check_existing_events(fixture_id):
                logger.info(f"   ⏭️ Fixture já possui eventos - ignorando")
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
                    'id': f"{fixture_id}_{i+1}",
                    'fixture_id': fixture_id,
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
                response = self.supabase.client.table('match_events').upsert(
                    events_data, 
                    on_conflict='id'
                ).execute()
                
                if response.data:
                    logger.info(f"   ✅ {len(response.data)} eventos inseridos com sucesso")
                    return {
                        'status': 'success', 
                        'events_count': len(response.data),
                        'fixture_id': fixture_id
                    }
                else:
                    logger.error(f"   ❌ Erro ao inserir eventos")
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
            'error': 0,
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
                results['error'] += 1
            
            # Rate limiting - pausa entre requests
            time.sleep(0.1)
        
        return results
    
    def run_enrichment(self, limit: int = 1000):
        """Executar enriquecimento de eventos para fixtures de 2023"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO DE EVENTOS - FIXTURES 2023")
        logger.info("=" * 60)
        
        # Buscar fixtures de 2023
        fixtures = self.get_fixtures_2023(limit)
        
        if not fixtures:
            logger.warning("⚠️ Nenhuma fixture de 2023 encontrada")
            return
        
        logger.info(f"📊 Processando {len(fixtures)} fixtures de 2023")
        
        # Processar em lotes
        total_results = {
            'success': 0,
            'ignored': 0,
            'no_events': 0,
            'error': 0,
            'total_events': 0
        }
        
        for i in range(0, len(fixtures), self.batch_size):
            batch = fixtures[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(fixtures) + self.batch_size - 1) // self.batch_size
            
            logger.info(f"📦 Processando lote {batch_num}/{total_batches} ({len(batch)} fixtures)")
            
            batch_results = self.process_batch(batch)
            
            # Atualizar resultados totais
            for key in total_results:
                total_results[key] += batch_results[key]
            
            # Log do progresso
            logger.info(f"   ✅ Sucesso: {batch_results['success']}")
            logger.info(f"   ⏭️ Ignoradas: {batch_results['ignored']}")
            logger.info(f"   📭 Sem eventos: {batch_results['no_events']}")
            logger.info(f"   ❌ Erros: {batch_results['error']}")
            logger.info(f"   📊 Eventos coletados: {batch_results['total_events']}")
            
            # Pausa entre lotes
            if i + self.batch_size < len(fixtures):
                logger.info("⏸️ Pausa de 2 segundos entre lotes...")
                time.sleep(2)
        
        # Relatório final
        logger.info("=" * 60)
        logger.info("📊 RELATÓRIO FINAL - ENRIQUECIMENTO 2023")
        logger.info("=" * 60)
        logger.info(f"📈 Fixtures processadas: {len(fixtures)}")
        logger.info(f"✅ Sucessos: {total_results['success']}")
        logger.info(f"⏭️ Ignoradas: {total_results['ignored']}")
        logger.info(f"📭 Sem eventos: {total_results['no_events']}")
        logger.info(f"❌ Erros: {total_results['error']}")
        logger.info(f"📊 Total de eventos coletados: {total_results['total_events']}")
        
        success_rate = (total_results['success'] / len(fixtures)) * 100 if fixtures else 0
        logger.info(f"🎯 Taxa de sucesso: {success_rate:.1f}%")
        
        logger.info("🎉 ENRIQUECIMENTO DE EVENTOS 2023 CONCLUÍDO!")

def main():
    """Função principal"""
    enrichment = Events2023Enrichment()
    enrichment.run_enrichment(limit=1000)  # Processar 1000 fixtures de 2023

if __name__ == "__main__":
    main()
