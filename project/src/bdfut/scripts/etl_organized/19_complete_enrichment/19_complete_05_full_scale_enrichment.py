#!/usr/bin/env python3
"""
Script para enriquecimento completo em escala de todas as fixtures
Versão otimizada para processar 11k+ fixtures
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

class FullScaleEnrichment:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 100  # Processar em lotes maiores
        self.request_delay = 0.5  # Delay reduzido para acelerar
        
        # Includes para enriquecimento completo
        self.includes = "scores;sport;round;stage;group;aggregate;league;season;referees;coaches;tvStations;venue;state;weatherReport;lineups;events;timeline;comments;trends;statistics;participants;periods;odds"
        
        # Contadores para relatório
        self.total_processed = 0
        self.total_events = 0
        self.total_lineups = 0
        self.total_stats = 0
        self.total_errors = 0
        self.start_time = None
        
    def get_fixtures_to_enrich(self, limit: int = None):
        """Buscar fixtures que precisam de enriquecimento completo"""
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
            
            # Verificar status atual
            status = self.check_fixture_enrichment_status(fixture_id)
            if status['is_complete']:
                return {'status': 'already_complete'}
            
            # Buscar dados da API
            endpoint = f'/fixtures/{fixture_id}'
            params = {'include': self.includes}
            
            response = self.sportmonks._make_request(endpoint, params, 'fixtures')
            
            if not response or not response.get('data'):
                return {'status': 'no_data'}
            
            fixture_data = response['data']
            
            # Processar eventos
            events_result = self.process_events_optimized(fixture_data, fixture_id)
            
            # Processar lineups
            lineups_result = self.process_lineups_optimized(fixture_data, fixture_id)
            
            # Processar estatísticas
            stats_result = self.process_statistics_optimized(fixture_data, fixture_id)
            
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
    
    def process_events_optimized(self, fixture_data, fixture_id):
        """Processar eventos da fixture - mapeamento otimizado"""
        try:
            events = fixture_data.get('events', [])
            if not events:
                return {'count': 0, 'status': 'no_events'}
            
            events_data = []
            for i, event in enumerate(events):
                # Mapear campos da API para campos do banco
                event_data = {
                    'id': f"{fixture_id}_{i+1}",
                    'fixture_id': fixture_id,
                    'type_id': event.get('type_id'),
                    'event_type': event.get('info'),
                    'minute': event.get('minute'),
                    'extra_minute': event.get('extra_minute'),
                    'team_id': event.get('participant_id'),
                    'player_id': event.get('player_id'),
                    'related_player_id': event.get('related_player_id'),
                    'player_name': event.get('player_name'),
                    'period_id': event.get('period_id'),
                    'result': event.get('result'),
                    'var': None,
                    'var_reason': None,
                    'coordinates': None,
                    'assist_id': None,
                    'assist_name': None,
                    'injured': event.get('injured'),
                    'on_bench': event.get('on_bench'),
                    'created_at': datetime.now().isoformat()
                }
                events_data.append(event_data)
            
            # Inserir eventos
            if events_data:
                response = self.supabase.client.table('match_events').upsert(events_data, on_conflict='id').execute()
                return {'count': len(events_data), 'status': 'success'}
            
            return {'count': 0, 'status': 'no_data'}
            
        except Exception as e:
            logger.error(f"Erro ao processar eventos: {e}")
            return {'count': 0, 'status': 'error', 'error': str(e)}
    
    def process_lineups_optimized(self, fixture_data, fixture_id):
        """Processar lineups da fixture - mapeamento otimizado"""
        try:
            lineups = fixture_data.get('lineups', [])
            if not lineups:
                return {'count': 0, 'status': 'no_lineups'}
            
            lineups_data = []
            for i, lineup in enumerate(lineups):
                # Mapear campos da API para campos do banco
                lineup_data = {
                    'id': f"{fixture_id}_{i+1}",
                    'fixture_id': fixture_id,
                    'team_id': lineup.get('team_id'),
                    'player_id': lineup.get('player_id'),
                    'player_name': lineup.get('player_name'),
                    'type': 'lineup' if lineup.get('type_id') == 11 else 'substitute',
                    'position_id': lineup.get('position_id'),
                    'position_name': None,
                    'jersey_number': lineup.get('jersey_number'),
                    'captain': False,
                    'minutes_played': None,
                    'rating': None,
                    'formation': None,
                    'formation_position': lineup.get('formation_position'),
                    'formation_number': None,
                    'formation_row': None,
                    'formation_position_x': None,
                    'formation_position_y': None,
                    'substitute': lineup.get('type_id') == 12,
                    'substitute_in': None,
                    'substitute_out': None,
                    'substitute_minute': None,
                    'substitute_extra_minute': None,
                    'substitute_reason': None,
                    'substitute_type': None,
                    'substitute_player_id': None,
                    'substitute_player_name': None,
                    'created_at': datetime.now().isoformat()
                }
                lineups_data.append(lineup_data)
            
            # Inserir lineups
            if lineups_data:
                response = self.supabase.client.table('match_lineups').upsert(lineups_data, on_conflict='id').execute()
                return {'count': len(lineups_data), 'status': 'success'}
            
            return {'count': 0, 'status': 'no_data'}
            
        except Exception as e:
            logger.error(f"Erro ao processar lineups: {e}")
            return {'count': 0, 'status': 'error', 'error': str(e)}
    
    def process_statistics_optimized(self, fixture_data, fixture_id):
        """Processar estatísticas da fixture - mapeamento otimizado"""
        try:
            statistics = fixture_data.get('statistics', [])
            if not statistics:
                return {'count': 0, 'status': 'no_statistics'}
            
            # Agrupar estatísticas por team_id
            stats_by_team = {}
            
            for stat in statistics:
                team_id = stat.get('participant_id')
                if team_id not in stats_by_team:
                    stats_by_team[team_id] = {}
                
                type_id = stat.get('type_id')
                data_value = stat.get('data', {}).get('value', 0)
                
                # Mapear type_id para campos específicos
                if type_id == 41:  # Shots Total
                    stats_by_team[team_id]['shots_total'] = data_value
                elif type_id == 42:  # Shots On Target
                    stats_by_team[team_id]['shots_on_target'] = data_value
                elif type_id == 43:  # Shots Inside Box
                    stats_by_team[team_id]['shots_inside_box'] = data_value
                elif type_id == 44:  # Shots Outside Box
                    stats_by_team[team_id]['shots_outside_box'] = data_value
                elif type_id == 45:  # Blocked Shots
                    stats_by_team[team_id]['blocked_shots'] = data_value
                elif type_id == 46:  # Corners
                    stats_by_team[team_id]['corners'] = data_value
                elif type_id == 47:  # Ball Possession
                    stats_by_team[team_id]['ball_possession'] = data_value
                elif type_id == 48:  # Yellow Cards
                    stats_by_team[team_id]['yellow_cards'] = data_value
                elif type_id == 49:  # Red Cards
                    stats_by_team[team_id]['red_cards'] = data_value
                elif type_id == 50:  # Passes Total
                    stats_by_team[team_id]['passes_total'] = data_value
                elif type_id == 51:  # Passes Accurate
                    stats_by_team[team_id]['passes_accurate'] = data_value
                elif type_id == 52:  # Pass Percentage
                    stats_by_team[team_id]['pass_percentage'] = data_value
                elif type_id == 53:  # Saves
                    stats_by_team[team_id]['saves'] = data_value
                elif type_id == 54:  # Interceptions
                    stats_by_team[team_id]['interceptions'] = data_value
            
            # Inserir estatísticas agrupadas
            stats_data = []
            for team_id, team_stats in stats_by_team.items():
                stat_data = {
                    'id': f"{fixture_id}_{team_id}",
                    'fixture_id': fixture_id,
                    'team_id': team_id,
                    'created_at': datetime.now().isoformat()
                }
                
                # Adicionar todas as estatísticas disponíveis
                stat_data.update(team_stats)
                stats_data.append(stat_data)
            
            # Inserir estatísticas
            if stats_data:
                response = self.supabase.client.table('match_statistics').upsert(stats_data, on_conflict='id').execute()
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
            
        except Exception as e:
            logger.error(f"Erro ao atualizar fixture: {e}")
    
    def print_progress_report(self, current: int, total: int):
        """Imprimir relatório de progresso"""
        if current % 100 == 0 or current == total:
            elapsed = time.time() - self.start_time
            rate = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / rate if rate > 0 else 0
            
            logger.info(f"\\n📊 PROGRESSO: {current:,}/{total:,} ({current/total*100:.1f}%)")
            logger.info(f"⏱️ Tempo decorrido: {elapsed/60:.1f} minutos")
            logger.info(f"🚀 Taxa: {rate:.1f} fixtures/minuto")
            logger.info(f"⏳ ETA: {eta/60:.1f} minutos")
            logger.info(f"📈 Eventos: {self.total_events:,}")
            logger.info(f"👥 Lineups: {self.total_lineups:,}")
            logger.info(f"📊 Estatísticas: {self.total_stats:,}")
            logger.info(f"❌ Erros: {self.total_errors:,}")
    
    def run_enrichment(self, limit: int = None):
        """Executar enriquecimento completo"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO COMPLETO EM ESCALA")
        logger.info("=" * 70)
        
        self.start_time = time.time()
        
        # Buscar fixtures para enriquecer
        fixtures = self.get_fixtures_to_enrich(limit)
        
        if not fixtures:
            logger.warning("⚠️ Nenhuma fixture encontrada para enriquecimento")
            return
        
        logger.info(f"📊 {len(fixtures):,} fixtures encontradas para processamento")
        
        # Processar em lotes
        for i in range(0, len(fixtures), self.batch_size):
            batch = fixtures[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(fixtures) + self.batch_size - 1) // self.batch_size
            
            logger.info(f"\\n🔄 Processando lote {batch_num}/{total_batches} ({len(batch)} fixtures)")
            
            for j, fixture in enumerate(batch):
                try:
                    result = self.enrich_fixture_complete(fixture)
                    
                    if result['status'] == 'success':
                        self.total_processed += 1
                        self.total_events += result['events']['count']
                        self.total_lineups += result['lineups']['count']
                        self.total_stats += result['statistics']['count']
                    elif result['status'] == 'error':
                        self.total_errors += 1
                    
                    # Delay entre requisições
                    time.sleep(self.request_delay)
                    
                    # Relatório de progresso
                    current_fixture = i + j + 1
                    self.print_progress_report(current_fixture, len(fixtures))
                    
                except Exception as e:
                    logger.error(f"❌ Erro crítico ao processar fixture {fixture['fixture_id']}: {e}")
                    self.total_errors += 1
            
            # Pausa entre lotes
            if i + self.batch_size < len(fixtures):
                logger.info(f"⏸️ Pausa de 10 segundos antes do próximo lote...")
                time.sleep(10)
        
        # Relatório final
        total_time = time.time() - self.start_time
        logger.info("\\n🎉 ENRIQUECIMENTO CONCLUÍDO!")
        logger.info("=" * 50)
        logger.info(f"⏱️ Tempo total: {total_time/60:.1f} minutos")
        logger.info(f"📊 Fixtures processadas: {self.total_processed:,}")
        logger.info(f"📊 Eventos inseridos: {self.total_events:,}")
        logger.info(f"📊 Lineups inseridos: {self.total_lineups:,}")
        logger.info(f"📊 Estatísticas inseridas: {self.total_stats:,}")
        logger.info(f"❌ Erros encontrados: {self.total_errors:,}")
        logger.info(f"🚀 Taxa média: {self.total_processed/(total_time/60):.1f} fixtures/minuto")

def main():
    """Função principal"""
    enrichment = FullScaleEnrichment()
    
    # Executar enriquecimento completo (sem limite)
    enrichment.run_enrichment()

if __name__ == "__main__":
    main()
