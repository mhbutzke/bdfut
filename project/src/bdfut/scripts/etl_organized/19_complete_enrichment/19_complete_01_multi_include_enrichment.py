#!/usr/bin/env python3
"""
Script otimizado para enriquecimento completo de fixtures
Baseado na análise da API Sportmonks com múltiplos includes
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

class CompleteEnrichment:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 50  # Processar em lotes de 50 fixtures
        self.request_delay = 1  # 1 segundo entre as requisições
        
        # Includes para enriquecimento completo
        self.includes = "scores;sport;round;stage;group;aggregate;league;season;referees;coaches;tvStations;venue;state;weatherReport;lineups;events;timeline;comments;trends;statistics;participants;periods;odds"
        
    def get_fixtures_to_enrich(self, limit: int = None):
        """Buscar fixtures que precisam de enriquecimento"""
        try:
            # Buscar fixtures finalizadas que não possuem eventos completos
            response = self.supabase.client.from_('fixtures').select(
                'fixture_id, match_date, home_team_name, away_team_name, status'
            ).in_('status', ['FT', 'FT_PEN', 'AET']).order('match_date', desc=True)
            
            if limit:
                response = response.limit(limit)
            
            result = response.execute()
            
            if result.data:
                return result.data
            return []
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures: {e}")
            return []
    
    def check_fixture_enrichment_status(self, fixture_id: int):
        """Verificar status de enriquecimento de uma fixture"""
        try:
            # Verificar se já tem eventos
            events_response = self.supabase.client.table('match_events').select('id').eq('fixture_id', fixture_id).limit(1).execute()
            has_events = len(events_response.data) > 0
            
            # Verificar se já tem lineups
            lineups_response = self.supabase.client.table('match_lineups').select('id').eq('fixture_id', fixture_id).limit(1).execute()
            has_lineups = len(lineups_response.data) > 0
            
            # Verificar se já tem estatísticas
            stats_response = self.supabase.client.table('match_statistics').select('id').eq('fixture_id', fixture_id).limit(1).execute()
            has_stats = len(stats_response.data) > 0
            
            return {
                'has_events': has_events,
                'has_lineups': has_lineups,
                'has_stats': has_stats,
                'is_complete': has_events and has_lineups and has_stats
            }
        except Exception as e:
            logger.error(f"Erro ao verificar status da fixture {fixture_id}: {e}")
            return {'has_events': False, 'has_lineups': False, 'has_stats': False, 'is_complete': False}
    
    def enrich_fixture_complete(self, fixture):
        """Enriquecer uma fixture com todos os dados disponíveis"""
        try:
            fixture_id = fixture['fixture_id']
            
            logger.info(f"🔍 Processando fixture {fixture_id} ({fixture['home_team_name']} vs {fixture['away_team_name']})")
            
            # Verificar status atual
            status = self.check_fixture_enrichment_status(fixture_id)
            if status['is_complete']:
                logger.info(f"   ✅ Fixture já está completa")
                return {'status': 'already_complete'}
            
            # Buscar dados da API
            endpoint = f'/fixtures/{fixture_id}'
            params = {'include': self.includes}
            
            response = self.sportmonks._make_request(endpoint, params, 'fixtures')
            
            if not response or not response.get('data'):
                logger.warning(f"   ⚠️ Nenhum dado recebido da API")
                return {'status': 'no_data'}
            
            fixture_data = response['data']
            
            # Processar eventos
            events_result = self.process_events(fixture_data, fixture_id)
            
            # Processar lineups
            lineups_result = self.process_lineups(fixture_data, fixture_id)
            
            # Processar estatísticas
            stats_result = self.process_statistics(fixture_data, fixture_id)
            
            # Atualizar fixture com dados adicionais
            self.update_fixture_data(fixture_data, fixture_id)
            
            return {
                'status': 'success',
                'events': events_result,
                'lineups': lineups_result,
                'statistics': stats_result
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer fixture {fixture_id}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def process_events(self, fixture_data, fixture_id):
        """Processar eventos da fixture"""
        try:
            events = fixture_data.get('events', [])
            if not events:
                return {'count': 0, 'status': 'no_events'}
            
            events_data = []
            for i, event in enumerate(events):
                event_data = {
                    'id': f"{fixture_id}_{i+1}",
                    'fixture_id': fixture_id,
                    'type_id': event.get('type_id'),
                    'event_type': event.get('type', {}).get('name') if event.get('type') else None,
                    'minute': event.get('minute'),
                    'extra_minute': event.get('extra_minute'),
                    'team_id': event.get('participant_id'),
                    'player_id': event.get('player_id'),
                    'related_player_id': event.get('related_player_id'),
                    'player_name': event.get('player_name'),
                    'related_player_name': event.get('related_player_name'),
                    'period_id': event.get('period_id'),
                    'result': event.get('result'),
                    'info': event.get('info'),
                    'addition': event.get('addition'),
                    'injured': event.get('injured'),
                    'on_bench': event.get('on_bench'),
                    'coach_id': event.get('coach_id'),
                    'sub_type_id': event.get('sub_type_id'),
                    'detailed_period_id': event.get('detailed_period_id'),
                    'rescinded': event.get('rescinded'),
                    'sort_order': event.get('sort_order'),
                    'created_at': datetime.now().isoformat()
                }
                events_data.append(event_data)
            
            # Inserir eventos
            if events_data:
                response = self.supabase.client.table('match_events').upsert(events_data, on_conflict='id').execute()
                logger.info(f"   📊 {len(events_data)} eventos processados")
                return {'count': len(events_data), 'status': 'success'}
            
            return {'count': 0, 'status': 'no_data'}
            
        except Exception as e:
            logger.error(f"Erro ao processar eventos: {e}")
            return {'count': 0, 'status': 'error', 'error': str(e)}
    
    def process_lineups(self, fixture_data, fixture_id):
        """Processar lineups da fixture"""
        try:
            lineups = fixture_data.get('lineups', [])
            if not lineups:
                return {'count': 0, 'status': 'no_lineups'}
            
            lineups_data = []
            for i, lineup in enumerate(lineups):
                lineup_data = {
                    'id': f"{fixture_id}_{i+1}",
                    'fixture_id': fixture_id,
                    'player_id': lineup.get('player_id'),
                    'team_id': lineup.get('team_id'),
                    'position_id': lineup.get('position_id'),
                    'formation_field': lineup.get('formation_field'),
                    'type_id': lineup.get('type_id'),
                    'formation_position': lineup.get('formation_position'),
                    'player_name': lineup.get('player_name'),
                    'jersey_number': lineup.get('jersey_number'),
                    'created_at': datetime.now().isoformat()
                }
                lineups_data.append(lineup_data)
            
            # Inserir lineups
            if lineups_data:
                response = self.supabase.client.table('match_lineups').upsert(lineups_data, on_conflict='id').execute()
                logger.info(f"   👥 {len(lineups_data)} jogadores processados")
                return {'count': len(lineups_data), 'status': 'success'}
            
            return {'count': 0, 'status': 'no_data'}
            
        except Exception as e:
            logger.error(f"Erro ao processar lineups: {e}")
            return {'count': 0, 'status': 'error', 'error': str(e)}
    
    def process_statistics(self, fixture_data, fixture_id):
        """Processar estatísticas da fixture"""
        try:
            statistics = fixture_data.get('statistics', [])
            if not statistics:
                return {'count': 0, 'status': 'no_statistics'}
            
            stats_data = []
            for i, stat in enumerate(statistics):
                stat_data = {
                    'id': f"{fixture_id}_{i+1}",
                    'fixture_id': fixture_id,
                    'type_id': stat.get('type_id'),
                    'team_id': stat.get('participant_id'),
                    'data': stat.get('data'),
                    'location': stat.get('location'),
                    'created_at': datetime.now().isoformat()
                }
                stats_data.append(stat_data)
            
            # Inserir estatísticas
            if stats_data:
                response = self.supabase.client.table('match_statistics').upsert(stats_data, on_conflict='id').execute()
                logger.info(f"   📈 {len(stats_data)} estatísticas processadas")
                return {'count': len(stats_data), 'status': 'success'}
            
            return {'count': 0, 'status': 'no_data'}
            
        except Exception as e:
            logger.error(f"Erro ao processar estatísticas: {e}")
            return {'count': 0, 'status': 'error', 'error': str(e)}
    
    def update_fixture_data(self, fixture_data, fixture_id):
        """Atualizar dados adicionais da fixture"""
        try:
            # Extrair dados importantes
            update_data = {
                'sport_id': fixture_data.get('sport_id'),
                'group_id': fixture_data.get('group_id'),
                'aggregate_id': fixture_data.get('aggregate_id'),
                'has_premium_odds': fixture_data.get('has_premium_odds'),
                'starting_at_timestamp': fixture_data.get('starting_at_timestamp')
            }
            
            # Remover valores None
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            if update_data:
                response = self.supabase.client.table('fixtures').update(update_data).eq('fixture_id', fixture_id).execute()
                logger.info(f"   🔄 Fixture atualizada com dados adicionais")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar fixture: {e}")
    
    def run_enrichment(self, limit: int = None):
        """Executar enriquecimento completo"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO COMPLETO DE FIXTURES")
        logger.info("=" * 70)
        
        # Buscar fixtures para enriquecer
        fixtures = self.get_fixtures_to_enrich(limit)
        
        if not fixtures:
            logger.warning("⚠️ Nenhuma fixture encontrada para enriquecimento")
            return
        
        logger.info(f"📊 {len(fixtures)} fixtures encontradas para processamento")
        
        # Processar em lotes
        total_processed = 0
        total_events = 0
        total_lineups = 0
        total_stats = 0
        
        for i in range(0, len(fixtures), self.batch_size):
            batch = fixtures[i:i + self.batch_size]
            logger.info(f"\\n🔄 Processando lote {i//self.batch_size + 1} ({len(batch)} fixtures)")
            
            for fixture in batch:
                try:
                    result = self.enrich_fixture_complete(fixture)
                    
                    if result['status'] == 'success':
                        total_processed += 1
                        total_events += result['events']['count']
                        total_lineups += result['lineups']['count']
                        total_stats += result['statistics']['count']
                    
                    # Delay entre requisições
                    time.sleep(self.request_delay)
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar fixture {fixture['fixture_id']}: {e}")
            
            # Pausa entre lotes
            if i + self.batch_size < len(fixtures):
                logger.info(f"⏸️ Pausa de 5 segundos antes do próximo lote...")
                time.sleep(5)
        
        # Relatório final
        logger.info("\\n🎉 ENRIQUECIMENTO CONCLUÍDO!")
        logger.info("=" * 50)
        logger.info(f"📊 Fixtures processadas: {total_processed}")
        logger.info(f"📊 Eventos inseridos: {total_events}")
        logger.info(f"📊 Lineups inseridos: {total_lineups}")
        logger.info(f"📊 Estatísticas inseridas: {total_stats}")

def main():
    """Função principal"""
    enrichment = CompleteEnrichment()
    
    # Executar enriquecimento (limitar a 100 fixtures para teste)
    enrichment.run_enrichment(limit=100)

if __name__ == "__main__":
    main()
