#!/usr/bin/env python3
"""
Script simples para testar enriquecimento de eventos
Processa apenas 10 fixtures para validar o funcionamento
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

class SimpleEventsTest:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def get_test_fixtures(self, limit: int = 10):
        """Buscar fixtures de teste que não possuem eventos"""
        try:
            # Buscar fixtures finalizadas
            response = self.supabase.client.table('fixtures').select('id, sportmonks_id, match_date, home_team_name, away_team_name').in_('status', ['FT', 'FT_PEN', 'AET']).order('match_date', desc=True).limit(limit * 2).execute()
            
            if not response.data:
                return []
            
            # Filtrar fixtures que não possuem eventos
            fixtures_without_events = []
            for fixture in response.data:
                # Verificar se já existem eventos para esta fixture
                events_check = self.supabase.client.table('match_events').select('id').eq('fixture_id', fixture['id']).limit(1).execute()
                if not events_check.data:
                    fixtures_without_events.append(fixture)
                    if len(fixtures_without_events) >= limit:
                        break
            
            return fixtures_without_events
            
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures de teste: {e}")
            return []
    
    def enrich_fixture_events(self, fixture):
        """Enriquecer uma fixture com eventos"""
        try:
            fixture_id = fixture['id']
            sportmonks_id = fixture['sportmonks_id']
            
            logger.info(f"🔍 Processando fixture {fixture_id} (Sportmonks: {sportmonks_id})")
            
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
                    'id': f"{sportmonks_id}_{i+1}",  # Usar sportmonks_id como base
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
            
            # Inserir eventos
            if events_data:
                response = self.supabase.client.table('match_events').insert(events_data).execute()
                logger.info(f"   ✅ {len(events_data)} eventos inseridos com sucesso")
                return {
                    'status': 'success',
                    'events_count': len(events_data),
                    'events': events_data
                }
            
            return {'status': 'no_events', 'reason': 'no_valid_events'}
            
        except Exception as e:
            logger.error(f"   ❌ Erro ao enriquecer fixture {fixture_id}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def run_test(self):
        """Executar teste simples"""
        logger.info("🧪 INICIANDO TESTE SIMPLES DE ENRIQUECIMENTO")
        logger.info("=" * 50)
        
        # Buscar fixtures de teste
        fixtures = self.get_test_fixtures(10)
        
        if not fixtures:
            logger.info("❌ Nenhuma fixture encontrada para teste")
            return
        
        logger.info(f"📦 Encontradas {len(fixtures)} fixtures para teste")
        
        total_events = 0
        total_success = 0
        total_errors = 0
        total_no_events = 0
        
        for i, fixture in enumerate(fixtures, 1):
            logger.info(f"\n📋 Fixture {i}/{len(fixtures)}")
            
            # Enriquecer fixture
            result = self.enrich_fixture_events(fixture)
            
            if result['status'] == 'success':
                total_success += 1
                total_events += result['events_count']
            elif result['status'] == 'no_events':
                total_no_events += 1
            else:
                total_errors += 1
            
            # Rate limiting
            time.sleep(0.1)
        
        # Relatório final
        logger.info("\n🎯 RESULTADO DO TESTE:")
        logger.info("=" * 50)
        logger.info(f"   Fixtures processadas: {len(fixtures)}")
        logger.info(f"   Sucessos: {total_success}")
        logger.info(f"   Sem eventos: {total_no_events}")
        logger.info(f"   Erros: {total_errors}")
        logger.info(f"   Total de eventos: {total_events}")
        
        return {
            'fixtures_processed': len(fixtures),
            'total_success': total_success,
            'total_errors': total_errors,
            'total_no_events': total_no_events,
            'total_events': total_events
        }

def main():
    """Função principal"""
    try:
        test = SimpleEventsTest()
        result = test.run_test()
        
        print(f"\n🎯 RESULTADO FINAL:")
        print(f"   Fixtures processadas: {result['fixtures_processed']}")
        print(f"   Eventos coletados: {result['total_events']}")
        print(f"   Taxa de sucesso: {result['total_success']}/{result['fixtures_processed']} ({result['total_success']/result['fixtures_processed']*100:.1f}%)")
        
    except Exception as e:
        logger.error(f"Erro na execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
