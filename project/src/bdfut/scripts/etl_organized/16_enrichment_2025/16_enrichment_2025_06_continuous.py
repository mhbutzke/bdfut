#!/usr/bin/env python3
"""
Script para enriquecimento contínuo de TODAS as fixtures restantes
Processa todas as fixtures sem eventos de forma contínua e otimizada
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

class ContinuousEventsEnrichment:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 100  # Processar em lotes de 100
        self.rate_limit_delay = 0.1  # 100ms entre requests
        self.long_pause_interval = 1000  # Pausa longa a cada 1000 fixtures
        self.long_pause_delay = 5  # 5 segundos de pausa longa
        
    def get_fixtures_without_events(self, limit: int = None):
        """Buscar fixtures que não possuem eventos"""
        try:
            # Buscar todas as fixtures finalizadas
            response = self.supabase.client.table('fixtures').select('id, sportmonks_id, match_date, home_team_name, away_team_name').in_('status', ['FT', 'FT_PEN', 'AET']).order('match_date', desc=True).execute()
            
            if not response.data:
                return []
            
            # Filtrar fixtures que não possuem eventos
            fixtures_without_events = []
            for fixture in response.data:
                # Verificar se já existem eventos para esta fixture
                if not self.check_existing_events(fixture['id']):
                    fixtures_without_events.append(fixture)
                    
                    # Limitar se especificado
                    if limit and len(fixtures_without_events) >= limit:
                        break
            
            return fixtures_without_events
            
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures sem eventos: {e}")
            return []
    
    def check_existing_events(self, fixture_id: int):
        """Verificar se já existem eventos para esta fixture"""
        try:
            response = self.supabase.client.table('match_events').select('id').eq('fixture_id', fixture_id).limit(1).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Erro ao verificar eventos existentes: {e}")
            return False
    
    def enrich_fixture_events(self, fixture):
        """Enriquecer uma fixture com eventos"""
        try:
            fixture_id = fixture['id']
            sportmonks_id = fixture['sportmonks_id']
            
            # Verificar se a fixture existe na tabela fixtures
            fixture_check = self.supabase.client.table('fixtures').select('id').eq('id', fixture_id).limit(1).execute()
            if not fixture_check.data:
                return {'status': 'error', 'reason': 'fixture_not_found'}
            
            # Verificar se já existem eventos
            if self.check_existing_events(fixture_id):
                return {'status': 'ignored', 'reason': 'already_has_events'}
            
            # Buscar eventos da API
            events = self.sportmonks.get_events_by_fixture(sportmonks_id)
            
            if not events:
                return {'status': 'no_events', 'reason': 'api_no_events'}
            
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
            
            # Inserir eventos
            if events_data:
                response = self.supabase.client.table('match_events').insert(events_data).execute()
                return {
                    'status': 'success',
                    'events_count': len(events_data),
                    'events': events_data
                }
            
            return {'status': 'no_events', 'reason': 'no_valid_events'}
            
        except Exception as e:
            logger.error(f"Erro ao enriquecer fixture {fixture_id}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def run_continuous_enrichment(self):
        """Executar enriquecimento contínuo"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO CONTÍNUO DE EVENTOS")
        logger.info("=" * 60)
        
        total_processed = 0
        total_events = 0
        total_success = 0
        total_ignored = 0
        total_errors = 0
        total_no_events = 0
        
        start_time = datetime.now()
        
        while True:
            try:
                # Buscar próximo lote de fixtures
                fixtures = self.get_fixtures_without_events(self.batch_size)
                
                if not fixtures:
                    logger.info("✅ Todas as fixtures foram processadas!")
                    break
                
                logger.info(f"📦 Processando lote de {len(fixtures)} fixtures...")
                
                batch_events = 0
                batch_success = 0
                batch_ignored = 0
                batch_errors = 0
                batch_no_events = 0
                
                for i, fixture in enumerate(fixtures):
                    try:
                        # Enriquecer fixture
                        result = self.enrich_fixture_events(fixture)
                        
                        if result['status'] == 'success':
                            batch_success += 1
                            batch_events += result['events_count']
                            logger.info(f"   ✅ Fixture {fixture['id']} ({fixture['home_team_name']} vs {fixture['away_team_name']}): {result['events_count']} eventos")
                        elif result['status'] == 'ignored':
                            batch_ignored += 1
                            logger.info(f"   ⏭️ Fixture {fixture['id']}: {result['reason']}")
                        elif result['status'] == 'no_events':
                            batch_no_events += 1
                            logger.info(f"   📭 Fixture {fixture['id']}: {result['reason']}")
                        else:
                            batch_errors += 1
                            logger.error(f"   ❌ Fixture {fixture['id']}: {result.get('error', 'Erro desconhecido')}")
                        
                        # Rate limiting
                        time.sleep(self.rate_limit_delay)
                        
                        # Pausa longa a cada intervalo
                        if (total_processed + i + 1) % self.long_pause_interval == 0:
                            logger.info(f"⏸️ Pausa longa de {self.long_pause_delay}s após {total_processed + i + 1} fixtures...")
                            time.sleep(self.long_pause_delay)
                        
                    except Exception as e:
                        batch_errors += 1
                        logger.error(f"   ❌ Erro ao processar fixture {fixture['id']}: {e}")
                
                # Atualizar estatísticas
                total_processed += len(fixtures)
                total_events += batch_events
                total_success += batch_success
                total_ignored += batch_ignored
                total_errors += batch_errors
                total_no_events += batch_no_events
                
                # Relatório do lote
                logger.info(f"📊 Lote processado:")
                logger.info(f"   Fixtures: {len(fixtures)}")
                logger.info(f"   Sucessos: {batch_success}")
                logger.info(f"   Ignoradas: {batch_ignored}")
                logger.info(f"   Sem eventos: {batch_no_events}")
                logger.info(f"   Erros: {batch_errors}")
                logger.info(f"   Eventos coletados: {batch_events}")
                
                # Relatório geral
                elapsed = datetime.now() - start_time
                logger.info(f"📈 ESTATÍSTICAS GERAIS:")
                logger.info(f"   Total processadas: {total_processed:,}")
                logger.info(f"   Total de eventos: {total_events:,}")
                logger.info(f"   Sucessos: {total_success:,}")
                logger.info(f"   Ignoradas: {total_ignored:,}")
                logger.info(f"   Sem eventos: {total_no_events:,}")
                logger.info(f"   Erros: {total_errors:,}")
                logger.info(f"   Tempo decorrido: {elapsed}")
                logger.info(f"   Taxa: {total_processed/elapsed.total_seconds():.2f} fixtures/segundo")
                logger.info("-" * 60)
                
            except Exception as e:
                logger.error(f"Erro no lote: {e}")
                time.sleep(5)  # Pausa antes de tentar novamente
        
        # Relatório final
        elapsed = datetime.now() - start_time
        logger.info("🎉 ENRIQUECIMENTO CONTÍNUO CONCLUÍDO!")
        logger.info("=" * 60)
        logger.info(f"📊 ESTATÍSTICAS FINAIS:")
        logger.info(f"   Total processadas: {total_processed:,}")
        logger.info(f"   Total de eventos: {total_events:,}")
        logger.info(f"   Sucessos: {total_success:,}")
        logger.info(f"   Ignoradas: {total_ignored:,}")
        logger.info(f"   Sem eventos: {total_no_events:,}")
        logger.info(f"   Erros: {total_errors:,}")
        logger.info(f"   Tempo total: {elapsed}")
        logger.info(f"   Taxa média: {total_processed/elapsed.total_seconds():.2f} fixtures/segundo")
        
        return {
            'total_processed': total_processed,
            'total_events': total_events,
            'total_success': total_success,
            'total_ignored': total_ignored,
            'total_errors': total_errors,
            'total_no_events': total_no_events,
            'elapsed_time': elapsed
        }

def main():
    """Função principal"""
    try:
        enrichment = ContinuousEventsEnrichment()
        result = enrichment.run_continuous_enrichment()
        
        print(f"\n🎯 RESULTADO FINAL:")
        print(f"   Fixtures processadas: {result['total_processed']:,}")
        print(f"   Eventos coletados: {result['total_events']:,}")
        print(f"   Tempo total: {result['elapsed_time']}")
        
    except Exception as e:
        logger.error(f"Erro na execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
