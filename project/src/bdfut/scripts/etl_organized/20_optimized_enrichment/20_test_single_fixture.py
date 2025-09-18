#!/usr/bin/env python3
"""
Script de teste para uma fixture específica
Validar mapeamento antes do enriquecimento em escala
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
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

class SingleFixtureTest:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def test_fixture_enrichment(self, fixture_id: int):
        """Testar enriquecimento de uma fixture específica"""
        logger.info(f"🔍 TESTANDO FIXTURE {fixture_id}")
        logger.info("=" * 50)
        
        try:
            # Verificar status atual
            self.check_current_status(fixture_id)
            
            # Testar eventos
            self.test_events(fixture_id)
            
            # Testar lineups
            self.test_lineups(fixture_id)
            
            # Testar estatísticas
            self.test_statistics(fixture_id)
            
        except Exception as e:
            logger.error(f"❌ Erro no teste: {e}")
            import traceback
            traceback.print_exc()
    
    def check_current_status(self, fixture_id: int):
        """Verificar status atual da fixture"""
        logger.info("📊 STATUS ATUAL:")
        
        # Verificar eventos
        events_check = self.supabase.client.table('match_events').select('id').eq('fixture_id', fixture_id).limit(1).execute()
        has_events = len(events_check.data) > 0
        
        # Verificar lineups
        lineups_check = self.supabase.client.table('match_lineups').select('id').eq('fixture_id', fixture_id).limit(1).execute()
        has_lineups = len(lineups_check.data) > 0
        
        # Verificar estatísticas
        stats_check = self.supabase.client.table('match_statistics').select('id').eq('fixture_id', fixture_id).limit(1).execute()
        has_stats = len(stats_check.data) > 0
        
        logger.info(f"   Eventos: {'✅' if has_events else '❌'}")
        logger.info(f"   Lineups: {'✅' if has_lineups else '❌'}")
        logger.info(f"   Estatísticas: {'✅' if has_stats else '❌'}")
    
    def test_events(self, fixture_id: int):
        """Testar enriquecimento de eventos"""
        logger.info("\\n🎯 TESTANDO EVENTOS:")
        
        try:
            # Buscar eventos da API
            events = self.sportmonks.get_events_by_fixture(fixture_id)
            
            if not events:
                logger.info("   📭 Nenhum evento encontrado na API")
                return
            
            logger.info(f"   📊 {len(events)} eventos encontrados na API")
            
            # Mostrar estrutura do primeiro evento
            if events:
                sample_event = events[0]
                logger.info("   📋 Estrutura do evento:")
                for key, value in sample_event.items():
                    logger.info(f"     {key}: {type(value).__name__} = {value}")
            
            # Mapear dados para inserção
            events_data = []
            for i, event in enumerate(events):
                event_data = {
                    'id': f"{fixture_id}_{event.get('id', i)}",
                    'fixture_id': fixture_id,
                    'type_id': event.get('type_id'),
                    'event_type': event.get('addition'),
                    'minute': event.get('minute'),
                    'extra_minute': event.get('extra_minute'),
                    'team_id': event.get('participant_id'),
                    'player_id': event.get('player_id'),
                    'related_player_id': event.get('related_player_id'),
                    'player_name': event.get('player_name'),
                    'related_player_name': event.get('related_player_name'),
                    'period_id': event.get('period_id'),
                    'result': event.get('result'),
                    'injured': event.get('injured'),
                    'on_bench': event.get('on_bench'),
                    'sort_order': event.get('sort_order'),
                    'created_at': datetime.now().isoformat()
                }
                events_data.append(event_data)
            
            logger.info(f"   📝 {len(events_data)} eventos mapeados para inserção")
            
            # Mostrar exemplo de mapeamento
            if events_data:
                logger.info("   📋 Exemplo de mapeamento:")
                sample_mapped = events_data[0]
                for key, value in sample_mapped.items():
                    logger.info(f"     {key}: {value}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar eventos: {e}")
    
    def test_lineups(self, fixture_id: int):
        """Testar enriquecimento de lineups"""
        logger.info("\\n👥 TESTANDO LINEUPS:")
        
        try:
            # Buscar lineups da API
            lineups = self.sportmonks.get_lineups_by_fixture(fixture_id)
            
            if not lineups:
                logger.info("   📭 Nenhum lineup encontrado na API")
                return
            
            logger.info(f"   📊 {len(lineups)} lineups encontrados na API")
            
            # Mostrar estrutura do primeiro lineup
            if lineups:
                sample_lineup = lineups[0]
                logger.info("   📋 Estrutura do lineup:")
                for key, value in sample_lineup.items():
                    logger.info(f"     {key}: {type(value).__name__} = {value}")
            
            # Mapear dados para inserção
            lineups_data = []
            for i, lineup in enumerate(lineups):
                lineup_type = "lineup" if lineup.get('type_id') == 11 else "substitute"
                
                lineup_data = {
                    'id': f"{fixture_id}_{lineup.get('id', i)}",
                    'fixture_id': fixture_id,
                    'team_id': lineup.get('team_id'),
                    'player_id': lineup.get('player_id'),
                    'player_name': lineup.get('player_name'),
                    'type': lineup_type,
                    'position_id': lineup.get('position_id'),
                    'jersey_number': lineup.get('jersey_number'),
                    'formation_position': lineup.get('formation_position'),
                    'created_at': datetime.now().isoformat()
                }
                lineups_data.append(lineup_data)
            
            logger.info(f"   📝 {len(lineups_data)} lineups mapeados para inserção")
            
            # Mostrar exemplo de mapeamento
            if lineups_data:
                logger.info("   📋 Exemplo de mapeamento:")
                sample_mapped = lineups_data[0]
                for key, value in sample_mapped.items():
                    logger.info(f"     {key}: {value}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar lineups: {e}")
    
    def test_statistics(self, fixture_id: int):
        """Testar enriquecimento de estatísticas"""
        logger.info("\\n📈 TESTANDO ESTATÍSTICAS:")
        
        try:
            # Buscar estatísticas da API
            statistics = self.sportmonks.get_statistics_by_fixture(fixture_id)
            
            if not statistics:
                logger.info("   📭 Nenhuma estatística encontrada na API")
                return
            
            logger.info(f"   📊 {len(statistics)} estatísticas encontradas na API")
            
            # Mostrar estrutura da primeira estatística
            if statistics:
                sample_stat = statistics[0]
                logger.info("   📋 Estrutura da estatística:")
                for key, value in sample_stat.items():
                    logger.info(f"     {key}: {type(value).__name__} = {value}")
            
            # Mapear dados para inserção
            stats_by_team = {}
            
            for stat in statistics:
                team_id = stat.get('participant_id')
                if team_id not in stats_by_team:
                    stats_by_team[team_id] = {}
                
                type_id = stat.get('type_id')
                data_value = stat.get('data', {}).get('value', 0)
                
                # Mapear type_id para campo específico
                statistics_mapping = {
                    41: 'shots_total',
                    42: 'shots_on_target',
                    43: 'shots_inside_box',
                    44: 'shots_outside_box',
                    45: 'blocked_shots',
                    46: 'corners',
                    47: 'ball_possession',
                    48: 'yellow_cards',
                    49: 'red_cards',
                    50: 'passes_total',
                    51: 'passes_accurate',
                    52: 'pass_percentage',
                    53: 'saves',
                    54: 'interceptions'
                }
                
                if type_id in statistics_mapping:
                    field_name = statistics_mapping[type_id]
                    stats_by_team[team_id][field_name] = data_value
            
            # Criar registros de estatísticas agrupadas
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
            
            logger.info(f"   📝 {len(stats_data)} estatísticas mapeadas para inserção")
            
            # Mostrar exemplo de mapeamento
            if stats_data:
                logger.info("   📋 Exemplo de mapeamento:")
                sample_mapped = stats_data[0]
                for key, value in sample_mapped.items():
                    logger.info(f"     {key}: {value}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar estatísticas: {e}")

def main():
    """Função principal"""
    test = SingleFixtureTest()
    
    # Testar com uma fixture específica que não tem eventos
    fixture_id = 18863344  # RB Leipzig vs Bayer 04 Leverkusen
    test.test_fixture_enrichment(fixture_id)

if __name__ == "__main__":
    main()
