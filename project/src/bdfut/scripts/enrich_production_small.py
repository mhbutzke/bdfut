#!/usr/bin/env python3
"""
ENRICH-PRODUCTION-001: Enriquecimento em Produção - Amostra Pequena
===================================================================

Objetivo: Executar enriquecimento real em produção com fixtures que tenham dados disponíveis
Dependência: Sistema ETL base deve estar CONCLUÍDO
Estimativa: 30 minutos
Data: 2025-01-16

Critérios de Sucesso:
- [ ] Enriquecer 10 fixtures com dados reais
- [ ] Validar inserção no Supabase
- [ ] Atualizar flags de enriquecimento
- [ ] Gerar relatório de progresso

Entregáveis:
- Script de enriquecimento funcional
- Relatório de execução
- Validação de dados inseridos
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path
import json

# Configurar path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/Users/mhbutzke/Documents/BDFut/bdfut/project/data/logs/enrich_production_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionEnricher:
    """Classe para enriquecimento em produção"""
    
    def __init__(self):
        """Inicializar clientes"""
        self.sportmonks = SportmonksClient(enable_cache=False, use_redis=False)
        self.supabase = SupabaseClient(use_service_role=True)
        
        # Estatísticas
        self.stats = {
            'fixtures_processed': 0,
            'events_inserted': 0,
            'statistics_inserted': 0,
            'lineups_inserted': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        logger.info("🔧 ProductionEnricher inicializado")
    
    def find_fixtures_with_data(self, limit: int = 10) -> list:
        """Encontrar fixtures que provavelmente têm dados disponíveis"""
        logger.info(f"🔍 Buscando {limit} fixtures com dados disponíveis...")
        
        try:
            # Buscar fixtures recentes que precisam de enriquecimento
            result = self.supabase.client.table('fixtures').select(
                'sportmonks_id, match_date, league_id, season_id, home_team_id, away_team_id, has_events, has_statistics, has_lineups'
            ).order('match_date', desc=True).limit(limit * 2).execute()
            
            fixtures = []
            if result.data:
                for fixture in result.data:
                    # Filtrar fixtures que precisam de enriquecimento
                    if (not fixture.get('has_events') or 
                        not fixture.get('has_statistics') or 
                        not fixture.get('has_lineups')):
                        
                        fixture_data = {
                            'sportmonks_id': fixture['sportmonks_id'],
                            'match_date': fixture['match_date'],
                            'league_id': fixture['league_id'],
                            'season_id': fixture['season_id'],
                            'home_team_id': fixture['home_team_id'],
                            'away_team_id': fixture['away_team_id'],
                            'has_events': fixture['has_events'],
                            'has_statistics': fixture['has_statistics'],
                            'has_lineups': fixture['has_lineups'],
                            'league_name': 'Unknown'  # Simplificado por enquanto
                        }
                        fixtures.append(fixture_data)
                        
                        if len(fixtures) >= limit:
                            break
            
            if fixtures:
                logger.info(f"✅ Encontradas {len(fixtures)} fixtures para enriquecimento")
                for fixture in fixtures[:3]:  # Log das primeiras 3
                    logger.info(f"   📋 Fixture {fixture['sportmonks_id']} - {fixture['league_name']} - {fixture['match_date']}")
            else:
                logger.warning("⚠️ Nenhuma fixture recente encontrada")
            
            return fixtures
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixtures: {str(e)}")
            return []
    
    def test_fixture_data_availability(self, fixture_id: int) -> dict:
        """Testar disponibilidade de dados para uma fixture"""
        availability = {
            'events': False,
            'statistics': False,
            'lineups': False,
            'events_count': 0,
            'statistics_count': 0,
            'lineups_count': 0
        }
        
        try:
            # Testar eventos
            events_data = self.sportmonks.get_events_by_fixture(fixture_id=fixture_id)
            if events_data and isinstance(events_data, list) and len(events_data) > 0:
                availability['events'] = True
                availability['events_count'] = len(events_data)
            
            # Testar estatísticas
            stats_data = self.sportmonks.get_statistics_by_fixture(fixture_id=fixture_id)
            if stats_data and isinstance(stats_data, list) and len(stats_data) > 0:
                availability['statistics'] = True
                availability['statistics_count'] = len(stats_data)
            
            # Testar lineups
            lineups_data = self.sportmonks.get_lineups_by_fixture(fixture_id=fixture_id)
            if lineups_data and isinstance(lineups_data, list) and len(lineups_data) > 0:
                availability['lineups'] = True
                availability['lineups_count'] = len(lineups_data)
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao testar disponibilidade da fixture {fixture_id}: {str(e)}")
        
        return availability
    
    def enrich_fixture_events(self, fixture_id: int) -> bool:
        """Enriquecer eventos de uma fixture"""
        try:
            events_data = self.sportmonks.get_events_by_fixture(
                fixture_id=fixture_id,
                include='player,team,type'
            )
            
            if not events_data or not isinstance(events_data, list) or len(events_data) == 0:
                return False
            
            # Processar eventos
            processed_events = []
            for event in events_data:
                processed_event = self._process_event_data(event, fixture_id)
                if processed_event:
                    processed_events.append(processed_event)
            
            if processed_events:
                # Inserir no Supabase
                result = self.supabase.client.table('match_events').upsert(
                    processed_events,
                    on_conflict='id'
                ).execute()
                
                self.stats['events_inserted'] += len(processed_events)
                logger.info(f"✅ {len(processed_events)} eventos inseridos para fixture {fixture_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer eventos da fixture {fixture_id}: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def enrich_fixture_statistics(self, fixture_id: int) -> bool:
        """Enriquecer estatísticas de uma fixture"""
        try:
            stats_data = self.sportmonks.get_statistics_by_fixture(
                fixture_id=fixture_id,
                include='team'
            )
            
            if not stats_data or not isinstance(stats_data, list) or len(stats_data) == 0:
                return False
            
            # Processar estatísticas
            processed_stats = []
            for stat in stats_data:
                processed_stat = self._process_statistics_data(stat, fixture_id)
                if processed_stat:
                    processed_stats.append(processed_stat)
            
            if processed_stats:
                # Inserir no Supabase
                result = self.supabase.client.table('match_statistics').upsert(
                    processed_stats,
                    on_conflict='id'
                ).execute()
                
                self.stats['statistics_inserted'] += len(processed_stats)
                logger.info(f"✅ {len(processed_stats)} estatísticas inseridas para fixture {fixture_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer estatísticas da fixture {fixture_id}: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def enrich_fixture_lineups(self, fixture_id: int) -> bool:
        """Enriquecer lineups de uma fixture"""
        try:
            lineups_data = self.sportmonks.get_lineups_by_fixture(
                fixture_id=fixture_id,
                include='player,team,position'
            )
            
            if not lineups_data or not isinstance(lineups_data, list) or len(lineups_data) == 0:
                return False
            
            # Processar lineups
            processed_lineups = []
            for lineup in lineups_data:
                processed_lineup = self._process_lineup_data(lineup, fixture_id)
                if processed_lineup:
                    processed_lineups.append(processed_lineup)
            
            if processed_lineups:
                # Inserir no Supabase
                result = self.supabase.client.table('match_lineups').upsert(
                    processed_lineups,
                    on_conflict='id'
                ).execute()
                
                self.stats['lineups_inserted'] += len(processed_lineups)
                logger.info(f"✅ {len(processed_lineups)} lineups inseridos para fixture {fixture_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer lineups da fixture {fixture_id}: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def _process_event_data(self, event: dict, fixture_id: int) -> dict:
        """Processar dados de evento"""
        try:
            return {
                'id': f"{fixture_id}_{event.get('id', '')}_{event.get('minute', 0)}",
                'fixture_id': fixture_id,
                'type_id': event.get('type', {}).get('id') if event.get('type') else None,
                'event_type': event.get('type', {}).get('name') if event.get('type') else None,
                'minute': event.get('minute', 0),
                'extra_minute': event.get('extra_minute'),
                'team_id': event.get('team', {}).get('id') if event.get('team') else None,
                'player_id': event.get('player', {}).get('id') if event.get('player') else None,
                'related_player_id': event.get('related_player', {}).get('id') if event.get('related_player') else None,
                'player_name': event.get('player', {}).get('name') if event.get('player') else None,
                'period_id': event.get('period', {}).get('id') if event.get('period') else None,
                'result': event.get('result'),
                'var': event.get('var', False),
                'var_reason': event.get('var_reason'),
                'coordinates': json.dumps(event.get('coordinates')) if event.get('coordinates') else None,
                'assist_id': event.get('assist', {}).get('id') if event.get('assist') else None,
                'assist_name': event.get('assist', {}).get('name') if event.get('assist') else None,
                'injured': event.get('injured', False),
                'on_bench': event.get('on_bench', False)
            }
        except Exception as e:
            logger.error(f"❌ Erro ao processar evento: {str(e)}")
            return None
    
    def _process_statistics_data(self, stat: dict, fixture_id: int) -> dict:
        """Processar dados de estatísticas"""
        try:
            team_id = stat.get('team', {}).get('id') if stat.get('team') else None
            if not team_id:
                return None
            
            return {
                'fixture_id': fixture_id,
                'team_id': team_id,
                'shots_total': stat.get('shots_total'),
                'shots_on_target': stat.get('shots_on_target'),
                'shots_inside_box': stat.get('shots_inside_box'),
                'shots_outside_box': stat.get('shots_outside_box'),
                'blocked_shots': stat.get('blocked_shots'),
                'corners': stat.get('corners'),
                'offsides': stat.get('offsides'),
                'ball_possession': stat.get('ball_possession'),
                'yellow_cards': stat.get('yellow_cards'),
                'red_cards': stat.get('red_cards'),
                'fouls': stat.get('fouls'),
                'passes_total': stat.get('passes_total'),
                'passes_accurate': stat.get('passes_accurate'),
                'pass_percentage': stat.get('pass_percentage'),
                'saves': stat.get('saves'),
                'tackles': stat.get('tackles'),
                'interceptions': stat.get('interceptions'),
                'goals': stat.get('goals'),
                'goals_conceded': stat.get('goals_conceded')
            }
        except Exception as e:
            logger.error(f"❌ Erro ao processar estatística: {str(e)}")
            return None
    
    def _process_lineup_data(self, lineup: dict, fixture_id: int) -> dict:
        """Processar dados de lineup"""
        try:
            return {
                'fixture_id': fixture_id,
                'team_id': lineup.get('team', {}).get('id') if lineup.get('team') else None,
                'player_id': lineup.get('player', {}).get('id') if lineup.get('player') else None,
                'player_name': lineup.get('player', {}).get('name') if lineup.get('player') else None,
                'type': lineup.get('type', 'lineup'),
                'position_id': lineup.get('position', {}).get('id') if lineup.get('position') else None,
                'position_name': lineup.get('position', {}).get('name') if lineup.get('position') else None,
                'jersey_number': lineup.get('jersey_number'),
                'captain': lineup.get('captain', False),
                'minutes_played': lineup.get('minutes_played'),
                'rating': lineup.get('rating'),
                'formation': lineup.get('formation'),
                'formation_position': lineup.get('formation_position'),
                'formation_number': lineup.get('formation_number'),
                'formation_row': lineup.get('formation_row'),
                'formation_position_x': lineup.get('formation_position_x'),
                'formation_position_y': lineup.get('formation_position_y'),
                'substitute': lineup.get('substitute', False),
                'substitute_in': lineup.get('substitute_in'),
                'substitute_out': lineup.get('substitute_out'),
                'substitute_minute': lineup.get('substitute_minute'),
                'substitute_extra_minute': lineup.get('substitute_extra_minute'),
                'substitute_reason': lineup.get('substitute_reason'),
                'substitute_type': lineup.get('substitute_type'),
                'substitute_player_id': lineup.get('substitute_player_id'),
                'substitute_player_name': lineup.get('substitute_player_name')
            }
        except Exception as e:
            logger.error(f"❌ Erro ao processar lineup: {str(e)}")
            return None
    
    def update_fixture_flags(self, fixture_id: int, has_events: bool, has_statistics: bool, has_lineups: bool):
        """Atualizar flags de enriquecimento da fixture"""
        try:
            update_data = {
                'has_events': has_events,
                'has_statistics': has_statistics,
                'has_lineups': has_lineups,
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.client.table('fixtures').update(update_data).eq(
                'sportmonks_id', fixture_id
            ).execute()
            
            logger.info(f"✅ Flags atualizadas para fixture {fixture_id}: Events={has_events}, Stats={has_statistics}, Lineups={has_lineups}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar flags da fixture {fixture_id}: {str(e)}")
    
    def enrich_production_batch(self, fixtures: list) -> dict:
        """Enriquecer lote de fixtures em produção"""
        logger.info(f"🚀 Iniciando enriquecimento em produção de {len(fixtures)} fixtures")
        
        for i, fixture in enumerate(fixtures):
            fixture_id = fixture['sportmonks_id']
            league_name = fixture.get('league_name', 'Unknown')
            
            logger.info(f"🔍 Processando fixture {i+1}/{len(fixtures)}: {fixture_id} ({league_name})")
            
            # Testar disponibilidade de dados
            availability = self.test_fixture_data_availability(fixture_id)
            
            if not any([availability['events'], availability['statistics'], availability['lineups']]):
                logger.warning(f"⚠️ Fixture {fixture_id} não tem dados disponíveis - pulando")
                continue
            
            logger.info(f"📊 Dados disponíveis para fixture {fixture_id}: "
                       f"Events={availability['events_count']}, "
                       f"Stats={availability['statistics_count']}, "
                       f"Lineups={availability['lineups_count']}")
            
            # Enriquecer conforme disponibilidade
            events_added = False
            statistics_added = False
            lineups_added = False
            
            if availability['events'] and not fixture.get('has_events', False):
                events_added = self.enrich_fixture_events(fixture_id)
            
            if availability['statistics'] and not fixture.get('has_statistics', False):
                statistics_added = self.enrich_fixture_statistics(fixture_id)
            
            if availability['lineups'] and not fixture.get('has_lineups', False):
                lineups_added = self.enrich_fixture_lineups(fixture_id)
            
            # Atualizar flags se algum enriquecimento foi feito
            if events_added or statistics_added or lineups_added:
                self.update_fixture_flags(
                    fixture_id,
                    fixture.get('has_events', False) or events_added,
                    fixture.get('has_statistics', False) or statistics_added,
                    fixture.get('has_lineups', False) or lineups_added
                )
            
            self.stats['fixtures_processed'] += 1
            
            # Pausa entre fixtures para respeitar rate limits
            if i < len(fixtures) - 1:
                logger.info("⏳ Pausa de 2 segundos...")
                import time
                time.sleep(2)
        
        return self.stats

def main():
    """Função principal"""
    logger.info("🚀 INICIANDO ENRICH-PRODUCTION-001")
    logger.info("=" * 50)
    
    enricher = ProductionEnricher()
    
    try:
        # Encontrar fixtures para enriquecimento
        fixtures = enricher.find_fixtures_with_data(limit=10)
        
        if not fixtures:
            logger.warning("⚠️ Nenhuma fixture encontrada para enriquecimento")
            return True
        
        # Enriquecer em produção
        stats = enricher.enrich_production_batch(fixtures)
        
        # Relatório final
        elapsed_time = datetime.now() - stats['start_time']
        logger.info("=" * 50)
        logger.info("📊 RESULTADOS DO ENRIQUECIMENTO EM PRODUÇÃO:")
        logger.info(f"   Fixtures processadas: {stats['fixtures_processed']}")
        logger.info(f"   Events inseridos: {stats['events_inserted']}")
        logger.info(f"   Statistics inseridas: {stats['statistics_inserted']}")
        logger.info(f"   Lineups inseridos: {stats['lineups_inserted']}")
        logger.info(f"   Erros: {stats['errors']}")
        logger.info(f"   Tempo total: {elapsed_time}")
        
        if stats['fixtures_processed'] > 0:
            logger.info("✅ ENRICH-PRODUCTION-001 CONCLUÍDO COM SUCESSO")
            logger.info("🚀 Sistema de enriquecimento em produção funcionando")
            return True
        else:
            logger.warning("⚠️ Nenhuma fixture foi processada")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro na ENRICH-PRODUCTION-001: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
