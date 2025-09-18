#!/usr/bin/env python3
"""
Script completo de enriquecimento usando todos os includes solicitados
statistics;events;lineups;referees;participants;periods
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

class CompleteEnrichmentWithAllIncludes:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 10  # Processar 10 fixtures por vez
        self.request_delay = 2  # 2 segundos entre requests
        
        # Contadores para IDs sequenciais
        self.next_event_id = self._get_next_available_id('match_events')
        self.next_lineup_id = self._get_next_available_id('match_lineups')
        self.next_stat_id = self._get_next_available_id('match_statistics')
        self.next_referee_id = self._get_next_available_id('match_referees')
        self.next_period_id = self._get_next_available_id('match_periods')
        self.next_participant_id = self._get_next_available_id('match_participants')
        
    def _get_next_available_id(self, table_name):
        """Obter o próximo ID disponível para uma tabela"""
        try:
            response = self.supabase.client.table(table_name).select('id').order('id', desc=True).limit(1).execute()
            if response.data:
                max_id = max([int(row['id']) for row in response.data if str(row['id']).isdigit()])
                return max_id + 1
            return 1
        except Exception as e:
            logger.error(f"Erro ao obter próximo ID para {table_name}: {e}")
            return 1
    
    def get_fixtures_batch(self, limit: int = None):
        """Buscar fixtures finalizadas em lotes"""
        try:
            response = self.supabase.client.table('fixtures').select(
                'fixture_id, match_date, home_team_name, away_team_name'
            ).in_('status', ['FT', 'FT_PEN', 'AET']).order('match_date', desc=True)
            
            if limit:
                response = response.limit(limit)
            
            result = response.execute()
            
            if result.data:
                logger.info(f"📊 {len(result.data)} fixtures encontradas para processamento")
                return result.data
            return []
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures: {e}")
            return []
    
    def check_existing_data(self, fixture_id: int):
        """Verificar se já existem dados para uma fixture"""
        try:
            events_count = self.supabase.client.table('match_events').select('id', count='exact').eq('fixture_id', fixture_id).execute().count
            lineups_count = self.supabase.client.table('match_lineups').select('id', count='exact').eq('fixture_id', fixture_id).execute().count
            stats_count = self.supabase.client.table('match_statistics').select('id', count='exact').eq('fixture_id', fixture_id).execute().count
            referees_count = self.supabase.client.table('match_referees').select('id', count='exact').eq('fixture_id', fixture_id).execute().count
            periods_count = self.supabase.client.table('match_periods').select('id', count='exact').eq('fixture_id', fixture_id).execute().count
            
            return {
                'has_events': events_count > 0,
                'has_lineups': lineups_count > 0,
                'has_stats': stats_count > 0,
                'has_referees': referees_count > 0,
                'has_periods': periods_count > 0,
                'events_count': events_count,
                'lineups_count': lineups_count,
                'stats_count': stats_count,
                'referees_count': referees_count,
                'periods_count': periods_count
            }
        except Exception as e:
            logger.error(f"Erro ao verificar dados existentes para fixture {fixture_id}: {e}")
            return {'has_events': False, 'has_lineups': False, 'has_stats': False, 'has_referees': False, 'has_periods': False}
    
    def enrich_fixtures_batch(self, fixtures_batch):
        """Enriquecer um lote de fixtures usando endpoint multi com todos os includes"""
        try:
            fixture_ids = [str(f['fixture_id']) for f in fixtures_batch]
            ids_string = ','.join(fixture_ids)
            
            logger.info(f"🔍 Processando lote de {len(fixture_ids)} fixtures: {ids_string}")
            
            # Chamada multi com TODOS os includes solicitados
            includes = "statistics;events;lineups;referees;participants;periods"
            response = self.sportmonks.get_fixtures_multi(ids_string, includes)
            
            if not response or not response.get('data'):
                logger.warning(f"   ⚠️ Nenhuma resposta da API para lote {ids_string}")
                return {'status': 'no_response', 'processed': 0}
            
            processed_count = 0
            events_inserted = 0
            lineups_inserted = 0
            stats_inserted = 0
            referees_inserted = 0
            periods_inserted = 0
            participants_inserted = 0
            
            # Processar cada fixture da resposta
            for fixture_data in response['data']:
                fixture_id = fixture_data.get('id')
                if not fixture_id:
                    continue
                
                logger.info(f"   📊 Processando fixture {fixture_id}")
                
                # Verificar dados existentes
                existing = self.check_existing_data(fixture_id)
                
                # Processar participantes primeiro (necessário para outras tabelas)
                if fixture_data.get('participants'):
                    participants_count = self.process_participants(fixture_data['participants'])
                    participants_inserted += participants_count
                    logger.info(f"      👥 Participantes: +{participants_count}")
                
                # Processar períodos
                if not existing['has_periods'] and fixture_data.get('periods'):
                    periods_count = self.process_periods(fixture_id, fixture_data['periods'])
                    periods_inserted += periods_count
                    logger.info(f"      ⏱️ Períodos: +{periods_count}")
                
                # Processar árbitros
                if not existing['has_referees'] and fixture_data.get('referees'):
                    referees_count = self.process_referees(fixture_id, fixture_data['referees'])
                    referees_inserted += referees_count
                    logger.info(f"      🏟️ Árbitros: +{referees_count}")
                
                # Processar eventos
                if not existing['has_events'] and fixture_data.get('events'):
                    events_count = self.process_events(fixture_id, fixture_data['events'])
                    events_inserted += events_count
                    logger.info(f"      📈 Eventos: +{events_count}")
                
                # Processar lineups
                if not existing['has_lineups'] and fixture_data.get('lineups'):
                    lineups_count = self.process_lineups(fixture_id, fixture_data['lineups'])
                    lineups_inserted += lineups_count
                    logger.info(f"      👥 Lineups: +{lineups_count}")
                
                # Processar estatísticas
                if not existing['has_stats'] and fixture_data.get('statistics'):
                    stats_count = self.process_statistics(fixture_id, fixture_data['statistics'])
                    stats_inserted += stats_count
                    logger.info(f"      📊 Estatísticas: +{stats_count}")
                
                processed_count += 1
            
            logger.info(f"   ✅ Lote processado: {processed_count} fixtures")
            logger.info(f"   📊 Total inserido: Eventos: +{events_inserted}, Lineups: +{lineups_inserted}, Stats: +{stats_inserted}")
            logger.info(f"   📊 Total inserido: Árbitros: +{referees_inserted}, Períodos: +{periods_inserted}, Participantes: +{participants_inserted}")
            
            return {
                'status': 'success',
                'processed': processed_count,
                'events_inserted': events_inserted,
                'lineups_inserted': lineups_inserted,
                'stats_inserted': stats_inserted,
                'referees_inserted': referees_inserted,
                'periods_inserted': periods_inserted,
                'participants_inserted': participants_inserted
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar lote: {e}")
            return {'status': 'error', 'error': str(e), 'processed': 0}
    
    def process_participants(self, participants_data: list):
        """Processar e inserir participantes (times)"""
        if not participants_data:
            return 0
        
        try:
            participants_to_insert = []
            for participant in participants_data:
                participant_data = {
                    'id': participant.get('id'),
                    'sport_id': participant.get('sport_id'),
                    'country_id': participant.get('country_id'),
                    'venue_id': participant.get('venue_id'),
                    'gender': participant.get('gender'),
                    'name': participant.get('name'),
                    'short_code': participant.get('short_code'),
                    'image_path': participant.get('image_path'),
                    'founded': participant.get('founded'),
                    'type': participant.get('type'),
                    'placeholder': participant.get('placeholder', False),
                    'last_played_at': participant.get('last_played_at'),
                    'meta': participant.get('meta'),
                    'created_at': datetime.now().isoformat()
                }
                participants_to_insert.append(participant_data)
            
            if participants_to_insert:
                response = self.supabase.client.table('match_participants').upsert(participants_to_insert, on_conflict='id').execute()
                return len(response.data) if response.data else 0
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao processar participantes: {e}")
            return 0
    
    def process_periods(self, fixture_id: int, periods_data: list):
        """Processar e inserir períodos"""
        if not periods_data:
            return 0
        
        try:
            periods_to_insert = []
            for period in periods_data:
                period_data = {
                    'id': period.get('id'),
                    'fixture_id': fixture_id,
                    'type_id': period.get('type_id'),
                    'started': period.get('started'),
                    'ended': period.get('ended'),
                    'counts_from': period.get('counts_from'),
                    'ticking': period.get('ticking'),
                    'sort_order': period.get('sort_order'),
                    'description': period.get('description'),
                    'time_added': period.get('time_added'),
                    'period_length': period.get('period_length'),
                    'minutes': period.get('minutes'),
                    'seconds': period.get('seconds'),
                    'has_timer': period.get('has_timer'),
                    'created_at': datetime.now().isoformat()
                }
                periods_to_insert.append(period_data)
            
            if periods_to_insert:
                response = self.supabase.client.table('match_periods').upsert(periods_to_insert, on_conflict='id').execute()
                return len(response.data) if response.data else 0
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao processar períodos para fixture {fixture_id}: {e}")
            return 0
    
    def process_referees(self, fixture_id: int, referees_data: list):
        """Processar e inserir árbitros"""
        if not referees_data:
            return 0
        
        try:
            referees_to_insert = []
            for referee in referees_data:
                referee_data = {
                    'id': referee.get('id'),
                    'fixture_id': fixture_id,
                    'referee_id': referee.get('referee_id'),
                    'type_id': referee.get('type_id'),
                    'created_at': datetime.now().isoformat()
                }
                referees_to_insert.append(referee_data)
            
            if referees_to_insert:
                response = self.supabase.client.table('match_referees').upsert(referees_to_insert, on_conflict='id').execute()
                return len(response.data) if response.data else 0
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao processar árbitros para fixture {fixture_id}: {e}")
            return 0
    
    def process_events(self, fixture_id: int, events_data: list):
        """Processar e inserir eventos com todos os campos"""
        if not events_data:
            return 0
        
        try:
            events_to_insert = []
            for event in events_data:
                event_data = {
                    'id': event.get('id'),
                    'fixture_id': fixture_id,
                    'period_id': event.get('period_id'),
                    'participant_id': event.get('participant_id'),
                    'type_id': event.get('type_id'),
                    'event_type': event.get('type', {}).get('name') if event.get('type') else None,
                    'section': event.get('section'),
                    'player_id': event.get('player_id'),
                    'related_player_id': event.get('related_player_id'),
                    'player_name': event.get('player_name'),
                    'related_player_name': event.get('related_player_name'),
                    'result': event.get('result'),
                    'info': event.get('info'),
                    'addition': event.get('addition'),
                    'minute': event.get('minute'),
                    'extra_minute': event.get('extra_minute'),
                    'injured': event.get('injured', False),
                    'on_bench': event.get('on_bench', False),
                    'coach_id': event.get('coach_id'),
                    'sub_type_id': event.get('sub_type_id'),
                    'detailed_period_id': event.get('detailed_period_id'),
                    'rescinded': event.get('rescinded', False),
                    'sort_order': event.get('sort_order'),
                    'created_at': datetime.now().isoformat()
                }
                events_to_insert.append(event_data)
            
            if events_to_insert:
                response = self.supabase.client.table('match_events').upsert(events_to_insert, on_conflict='id').execute()
                return len(response.data) if response.data else 0
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao processar eventos para fixture {fixture_id}: {e}")
            return 0
    
    def process_lineups(self, fixture_id: int, lineups_data: list):
        """Processar e inserir lineups com todos os campos"""
        if not lineups_data:
            return 0
        
        try:
            lineups_to_insert = []
            for lineup in lineups_data:
                lineup_data = {
                    'id': lineup.get('id'),
                    'fixture_id': fixture_id,
                    'team_id': lineup.get('team_id'),
                    'player_id': lineup.get('player_id'),
                    'position_id': lineup.get('position_id'),
                    'formation_field': lineup.get('formation_field'),
                    'type_id': lineup.get('type_id'),
                    'formation_position': lineup.get('formation_position'),
                    'player_name': lineup.get('player_name'),
                    'jersey_number': lineup.get('jersey_number'),
                    'sport_id': lineup.get('sport_id'),
                    'created_at': datetime.now().isoformat()
                }
                lineups_to_insert.append(lineup_data)
            
            if lineups_to_insert:
                response = self.supabase.client.table('match_lineups').upsert(lineups_to_insert, on_conflict='id').execute()
                return len(response.data) if response.data else 0
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao processar lineups para fixture {fixture_id}: {e}")
            return 0
    
    def process_statistics(self, fixture_id: int, statistics_data: list):
        """Processar e inserir estatísticas com todos os campos"""
        if not statistics_data:
            return 0
        
        try:
            # Agrupar estatísticas por team_id (participant_id)
            stats_by_team = {}
            for stat in statistics_data:
                team_id = stat.get('participant_id')
                if team_id not in stats_by_team:
                    stats_by_team[team_id] = {}
                
                # Mapear type_id para campos específicos
                type_id = stat.get('type_id')
                data_value = stat.get('data')
                location = stat.get('location')
                
                if type_id == 41:  # shots_total
                    stats_by_team[team_id]['shots_total'] = data_value
                elif type_id == 42:  # shots_on_goal
                    stats_by_team[team_id]['shots_on_goal'] = data_value
                elif type_id == 43:  # shots_off_goal
                    stats_by_team[team_id]['shots_off_goal'] = data_value
                elif type_id == 44:  # shots_insidebox
                    stats_by_team[team_id]['shots_insidebox'] = data_value
                elif type_id == 45:  # shots_outsidebox
                    stats_by_team[team_id]['shots_outsidebox'] = data_value
                elif type_id == 46:  # shots_blocked
                    stats_by_team[team_id]['shots_blocked'] = data_value
                elif type_id == 47:  # possession
                    stats_by_team[team_id]['possession'] = data_value
                elif type_id == 48:  # corners
                    stats_by_team[team_id]['corners'] = data_value
                elif type_id == 49:  # offsides
                    stats_by_team[team_id]['offsides'] = data_value
                elif type_id == 50:  # fouls
                    stats_by_team[team_id]['fouls'] = data_value
                elif type_id == 51:  # yellow_cards
                    stats_by_team[team_id]['yellow_cards'] = data_value
                elif type_id == 52:  # red_cards
                    stats_by_team[team_id]['red_cards'] = data_value
                elif type_id == 53:  # goalkeeper_saves
                    stats_by_team[team_id]['goalkeeper_saves'] = data_value
                elif type_id == 54:  # passes_total
                    stats_by_team[team_id]['passes_total'] = data_value
                
                # Salvar location se disponível
                if location:
                    stats_by_team[team_id]['location'] = location
            
            # Inserir estatísticas agrupadas por time
            stats_to_insert = []
            for team_id, team_stats in stats_by_team.items():
                stat_data = {
                    'id': self.next_stat_id,
                    'fixture_id': fixture_id,
                    'team_id': team_id,
                    'shots_total': team_stats.get('shots_total'),
                    'shots_on_goal': team_stats.get('shots_on_goal'),
                    'shots_off_goal': team_stats.get('shots_off_goal'),
                    'shots_insidebox': team_stats.get('shots_insidebox'),
                    'shots_outsidebox': team_stats.get('shots_outsidebox'),
                    'shots_blocked': team_stats.get('shots_blocked'),
                    'possession': team_stats.get('possession'),
                    'corners': team_stats.get('corners'),
                    'offsides': team_stats.get('offsides'),
                    'fouls': team_stats.get('fouls'),
                    'yellow_cards': team_stats.get('yellow_cards'),
                    'red_cards': team_stats.get('red_cards'),
                    'goalkeeper_saves': team_stats.get('goalkeeper_saves'),
                    'passes_total': team_stats.get('passes_total'),
                    'location': team_stats.get('location'),
                    'created_at': datetime.now().isoformat()
                }
                stats_to_insert.append(stat_data)
                self.next_stat_id += 1
            
            if stats_to_insert:
                response = self.supabase.client.table('match_statistics').upsert(stats_to_insert, on_conflict='id').execute()
                return len(response.data) if response.data else 0
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao processar estatísticas para fixture {fixture_id}: {e}")
            return 0
    
    def run_enrichment(self, limit: int = None):
        """Executar enriquecimento completo com todos os includes"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO COMPLETO COM TODOS OS INCLUDES")
        logger.info("=" * 70)
        logger.info("📋 Includes: statistics;events;lineups;referees;participants;periods")
        
        fixtures = self.get_fixtures_batch(limit)
        
        if not fixtures:
            logger.warning("⚠️ Nenhuma fixture encontrada para enriquecimento")
            return
        
        logger.info(f"📊 {len(fixtures)} fixtures para processar em lotes de {self.batch_size}")
        
        total_processed = 0
        total_events = 0
        total_lineups = 0
        total_stats = 0
        total_referees = 0
        total_periods = 0
        total_participants = 0
        total_errors = 0
        
        start_time = time.time()
        
        # Processar em lotes
        for i in range(0, len(fixtures), self.batch_size):
            batch = fixtures[i:i + self.batch_size]
            
            try:
                result = self.enrich_fixtures_batch(batch)
                
                if result['status'] == 'success':
                    total_processed += result['processed']
                    total_events += result.get('events_inserted', 0)
                    total_lineups += result.get('lineups_inserted', 0)
                    total_stats += result.get('stats_inserted', 0)
                    total_referees += result.get('referees_inserted', 0)
                    total_periods += result.get('periods_inserted', 0)
                    total_participants += result.get('participants_inserted', 0)
                else:
                    total_errors += len(batch)
                
                # Rate limiting
                if i + self.batch_size < len(fixtures):
                    time.sleep(self.request_delay)
                
                # Log de progresso
                progress = min(i + self.batch_size, len(fixtures))
                elapsed = time.time() - start_time
                rate = progress / (elapsed / 60) if elapsed > 0 else 0
                eta = (len(fixtures) - progress) / rate if rate > 0 else 0
                
                logger.info(f"\n📊 PROGRESSO: {progress}/{len(fixtures)} ({progress/len(fixtures)*100:.1f}%)")
                logger.info(f"⏱️ Tempo decorrido: {elapsed/60:.1f} minutos")
                logger.info(f"🚀 Taxa: {rate:.1f} fixtures/minuto")
                logger.info(f"⏳ ETA: {eta:.1f} minutos")
                logger.info(f"📈 Eventos: +{total_events}, Lineups: +{total_lineups}, Stats: +{total_stats}")
                logger.info(f"🏟️ Árbitros: +{total_referees}, Períodos: +{total_periods}, Participantes: +{total_participants}")
                logger.info(f"❌ Erros: {total_errors}")
                
            except Exception as e:
                logger.error(f"❌ Erro inesperado no lote {i//self.batch_size + 1}: {e}")
                total_errors += len(batch)
                continue
        
        # Relatório final
        total_time = time.time() - start_time
        logger.info(f"\n🎉 ENRIQUECIMENTO COMPLETO CONCLUÍDO!")
        logger.info("=" * 70)
        logger.info(f"⏱️ Tempo total: {total_time/60:.1f} minutos")
        logger.info(f"📊 Fixtures processadas: {total_processed}")
        logger.info(f"📈 Eventos inseridos: {total_events}")
        logger.info(f"👥 Lineups inseridos: {total_lineups}")
        logger.info(f"📊 Estatísticas inseridas: {total_stats}")
        logger.info(f"🏟️ Árbitros inseridos: {total_referees}")
        logger.info(f"⏱️ Períodos inseridos: {total_periods}")
        logger.info(f"👥 Participantes inseridos: {total_participants}")
        logger.info(f"❌ Erros encontrados: {total_errors}")
        logger.info(f"🚀 Taxa média: {total_processed/(total_time/60):.1f} fixtures/minuto")

def main():
    """Função principal"""
    enrichment = CompleteEnrichmentWithAllIncludes()
    
    # Executar enriquecimento com limite de 20 fixtures para teste
    enrichment.run_enrichment(limit=20)

if __name__ == "__main__":
    main()
