#!/usr/bin/env python3
"""
Script otimizado para enriquecimento de MATCH_EVENTS
Baseado no planejamento detalhado e mapeamento correto da API
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

class EventsEnrichment:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 100
        self.request_delay = 1
        
        # Contadores
        self.total_processed = 0
        self.total_events = 0
        self.total_errors = 0
        self.start_time = None
        
    def get_fixtures_without_events(self, limit: int = None):
        """Buscar fixtures finalizadas que não possuem eventos"""
        try:
            # Buscar fixtures finalizadas
            response = self.supabase.client.from_('fixtures').select(
                'fixture_id, match_date, home_team_name, away_team_name, status'
            ).in_('status', ['FT', 'FT_PEN', 'AET']).order('match_date', desc=True)
            
            if limit:
                response = response.limit(limit)
            
            result = response.execute()
            
            if result.data:
                # Filtrar fixtures que não têm eventos
                fixtures_without_events = []
                for fixture in result.data:
                    fixture_id = fixture['fixture_id']
                    
                    # Verificar se já tem eventos
                    events_check = self.supabase.client.table('match_events').select('id').eq('fixture_id', fixture_id).limit(1).execute()
                    
                    if len(events_check.data) == 0:
                        fixtures_without_events.append(fixture)
                
                return fixtures_without_events
            
            return []
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures sem eventos: {e}")
            return []
    
    def map_event_data(self, event: dict, fixture_id: int, index: int) -> dict:
        """Mapear dados do evento da API para estrutura do banco"""
        return {
            'id': f"{fixture_id}_{event.get('id', index)}",
            'fixture_id': fixture_id,
            'type_id': event.get('type_id'),
            'event_type': event.get('addition'),  # Usar 'addition' como event_type
            'minute': event.get('minute'),
            'extra_minute': event.get('extra_minute'),
            'team_id': event.get('participant_id'),  # participant_id = team_id
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
    
    def enrich_fixture_events(self, fixture):
        """Enriquecer uma fixture com eventos"""
        try:
            fixture_id = fixture['fixture_id']
            
            logger.info(f"🔍 Processando fixture {fixture_id} ({fixture['home_team_name']} vs {fixture['away_team_name']})")
            
            # Buscar eventos da API
            events = self.sportmonks.get_events_by_fixture(fixture_id)
            
            if not events:
                logger.info(f"   📭 Nenhum evento encontrado na API")
                return {'status': 'no_events', 'count': 0}
            
            logger.info(f"   📊 {len(events)} eventos encontrados na API")
            
            # Mapear dados para inserção
            events_data = []
            for i, event in enumerate(events):
                event_data = self.map_event_data(event, fixture_id, i)
                events_data.append(event_data)
            
            # Inserir eventos no Supabase
            if events_data:
                response = self.supabase.client.table('match_events').upsert(events_data, on_conflict='id').execute()
                
                if response.data:
                    logger.info(f"   ✅ {len(response.data)} eventos inseridos/atualizados")
                    return {'status': 'success', 'count': len(response.data)}
                else:
                    logger.warning(f"   ⚠️ Nenhum evento inserido, resposta vazia")
                    return {'status': 'no_insert', 'count': 0}
            
            return {'status': 'no_data', 'count': 0}
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer fixture {fixture_id}: {e}")
            return {'status': 'error', 'count': 0, 'error': str(e)}
    
    def print_progress_report(self, current: int, total: int):
        """Imprimir relatório de progresso"""
        if current % 50 == 0 or current == total:
            elapsed = time.time() - self.start_time
            rate = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / rate if rate > 0 else 0
            
            logger.info(f"\\n📊 PROGRESSO: {current:,}/{total:,} ({current/total*100:.1f}%)")
            logger.info(f"⏱️ Tempo decorrido: {elapsed/60:.1f} minutos")
            logger.info(f"🚀 Taxa: {rate:.1f} fixtures/minuto")
            logger.info(f"⏳ ETA: {eta/60:.1f} minutos")
            logger.info(f"📈 Eventos inseridos: {self.total_events:,}")
            logger.info(f"❌ Erros: {self.total_errors:,}")
    
    def run_enrichment(self, limit: int = None):
        """Executar enriquecimento de eventos"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO DE EVENTOS")
        logger.info("=" * 50)
        
        self.start_time = time.time()
        
        # Buscar fixtures para enriquecer
        fixtures = self.get_fixtures_without_events(limit)
        
        if not fixtures:
            logger.warning("⚠️ Nenhuma fixture encontrada para enriquecimento")
            return
        
        logger.info(f"📊 {len(fixtures):,} fixtures encontradas para processamento")
        
        # Processar fixtures
        for i, fixture in enumerate(fixtures):
            try:
                result = self.enrich_fixture_events(fixture)
                
                if result['status'] == 'success':
                    self.total_processed += 1
                    self.total_events += result['count']
                elif result['status'] == 'error':
                    self.total_errors += 1
                
                # Delay entre requisições
                time.sleep(self.request_delay)
                
                # Relatório de progresso
                self.print_progress_report(i + 1, len(fixtures))
                
            except Exception as e:
                logger.error(f"❌ Erro crítico ao processar fixture {fixture['fixture_id']}: {e}")
                self.total_errors += 1
        
        # Relatório final
        total_time = time.time() - self.start_time
        logger.info("\\n🎉 ENRIQUECIMENTO DE EVENTOS CONCLUÍDO!")
        logger.info("=" * 50)
        logger.info(f"⏱️ Tempo total: {total_time/60:.1f} minutos")
        logger.info(f"📊 Fixtures processadas: {self.total_processed:,}")
        logger.info(f"📈 Eventos inseridos: {self.total_events:,}")
        logger.info(f"❌ Erros encontrados: {self.total_errors:,}")
        logger.info(f"🚀 Taxa média: {self.total_processed/(total_time/60):.1f} fixtures/minuto")

def main():
    """Função principal"""
    enrichment = EventsEnrichment()
    
    # Testar com 100 fixtures primeiro
    enrichment.run_enrichment(limit=100)

if __name__ == "__main__":
    main()
