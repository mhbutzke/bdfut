#!/usr/bin/env python3
"""
Script para enriquecer fixtures de 2025 com eventos
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import time

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EventsEnrichment2025:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def get_2025_fixtures(self, limit: int = None):
        """Obter fixtures de 2025"""
        try:
            # Buscar fixtures de 2025
            query = self.supabase.client.table('fixtures').select(
                'id, sportmonks_id, match_date, home_score, away_score, status'
            ).gte('match_date', '2025-01-01').lt('match_date', '2026-01-01').in_(
                'status', ['FT', 'FT_PEN', 'AET']
            ).order('match_date', desc=True)
            
            if limit:
                query = query.limit(limit)
                
            response = query.execute()
            fixtures = response.data
            
            logger.info(f"📋 Encontradas {len(fixtures)} fixtures de 2025")
            return fixtures
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixtures de 2025: {e}")
            return []
            
    def check_existing_events(self, fixture_id: int):
        """Verificar se já existem eventos para a fixture e se estão completos"""
        try:
            # Buscar eventos existentes
            response = self.supabase.client.table('match_events').select(
                'id, type_id, event_type, minute, team_id, player_id'
            ).eq('fixture_id', fixture_id).execute()
            
            existing_events = response.data
            
            if not existing_events:
                return False, 0
                
            # Verificar se os eventos têm dados importantes preenchidos
            complete_events = 0
            for event in existing_events:
                # Verificar se tem pelo menos os campos essenciais
                # type_id e minute são os campos mais importantes para análise de cartões
                if (event.get('type_id') is not None and 
                    event.get('minute') is not None):
                    complete_events += 1
                    
            # Considerar completo se pelo menos 80% dos eventos têm dados essenciais
            completion_rate = complete_events / len(existing_events) if existing_events else 0
            is_complete = completion_rate >= 0.8
            
            logger.info(f"📊 Fixture {fixture_id}: {len(existing_events)} eventos existentes, "
                       f"{complete_events} completos ({completion_rate:.1%})")
            
            return is_complete, len(existing_events)
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar eventos existentes para fixture {fixture_id}: {e}")
            return False, 0
            
    def enrich_fixture_events(self, fixture):
        """Enriquecer eventos para uma fixture"""
        fixture_id = fixture['sportmonks_id']
        
        try:
            # Verificar se já existem eventos e se estão completos
            is_complete, existing_count = self.check_existing_events(fixture_id)
            
            if is_complete:
                logger.info(f"⏭️ Fixture {fixture_id} já possui eventos completos ({existing_count} eventos)")
                return True
            elif existing_count > 0:
                logger.warning(f"⚠️ Fixture {fixture_id} possui eventos incompletos ({existing_count} eventos). "
                              f"Vamos atualizar com dados da API...")
                # Deletar eventos existentes incompletos
                self.supabase.client.table('match_events').delete().eq('fixture_id', fixture_id).execute()
                logger.info(f"🗑️ Eventos incompletos removidos para fixture {fixture_id}")
                
            # Buscar eventos da API
            events_data = self.sportmonks.get_events_by_fixture(fixture_id)
            
            if not events_data:
                logger.warning(f"❌ Nenhum evento encontrado para fixture {fixture_id}")
                return False
                
            logger.info(f"📊 {len(events_data)} eventos encontrados para fixture {fixture_id}")
            
            # Preparar dados para inserção
            events_to_insert = []
            
            for i, event in enumerate(events_data):
                event_data = {
                    'id': f"{fixture_id}_{i+1}",  # Gerar ID único
                    'fixture_id': fixture_id,
                    'type_id': event.get('type_id'),
                    'event_type': event.get('type'),
                    'minute': event.get('minute'),
                    'extra_minute': event.get('extra_minute'),
                    'team_id': event.get('team_id'),
                    'player_id': event.get('player_id'),
                    'related_player_id': event.get('related_player_id'),
                    'player_name': event.get('player_name'),
                    'period_id': event.get('period_id'),
                    'result': event.get('result'),
                    'var': event.get('var', False),
                    'var_reason': event.get('var_reason'),
                    'coordinates': event.get('coordinates'),
                    'assist_id': event.get('assist_id'),
                    'assist_name': event.get('assist_name'),
                    'injured': event.get('injured', False),
                    'on_bench': event.get('on_bench', False),
                    'created_at': datetime.now().isoformat()
                }
                
                # Remover campos None
                event_data = {k: v for k, v in event_data.items() if v is not None}
                
                events_to_insert.append(event_data)
                
            # Inserir eventos
            if events_to_insert:
                response = self.supabase.client.table('match_events').insert(
                    events_to_insert
                ).execute()
                
                logger.info(f"✅ {len(events_to_insert)} eventos inseridos para fixture {fixture_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer eventos para fixture {fixture_id}: {e}")
            return False
            
    def run_enrichment(self, limit: int = None):
        """Executar enriquecimento de eventos para 2025"""
        logger.info(f"🚀 INICIANDO ENRIQUECIMENTO DE EVENTOS PARA 2025")
        
        fixtures = self.get_2025_fixtures(limit)
        
        if not fixtures:
            logger.error("❌ Nenhuma fixture encontrada para enriquecimento")
            return
            
        results = {
            'total_fixtures': len(fixtures),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'updated_incomplete': 0,
            'total_events': 0
        }
        
        for i, fixture in enumerate(fixtures, 1):
            fixture_id = fixture['sportmonks_id']
            logger.info(f"\\n📡 Processando fixture {i}/{len(fixtures)}: {fixture_id}")
            
            try:
                success = self.enrich_fixture_events(fixture)
                
                if success:
                    # Verificar se foi uma atualização de dados incompletos
                    is_complete, existing_count = self.check_existing_events(fixture_id)
                    if existing_count > 0 and not is_complete:
                        results['updated_incomplete'] += 1
                    else:
                        results['successful'] += 1
                else:
                    results['failed'] += 1
                    
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar fixture {fixture_id}: {e}")
                results['failed'] += 1
                
        # Resumo dos resultados
        logger.info(f"\\n📊 RESUMO DO ENRIQUECIMENTO:")
        logger.info(f"   Fixtures processadas: {results['total_fixtures']}")
        logger.info(f"   Sucessos: {results['successful']}")
        logger.info(f"   Atualizações de dados incompletos: {results['updated_incomplete']}")
        logger.info(f"   Falhas: {results['failed']}")
        total_successful = results['successful'] + results['updated_incomplete']
        logger.info(f"   Taxa de sucesso: {(total_successful / results['total_fixtures'] * 100):.1f}%")
        
        return results

if __name__ == "__main__":
    enrichment = EventsEnrichment2025()
    
    # Testar com 10 fixtures primeiro
    logger.info("🧪 TESTANDO COM 10 FIXTURES PRIMEIRO")
    results = enrichment.run_enrichment(limit=10)
    
    if results and results['successful'] > 0:
        logger.info("\\n✅ Teste bem-sucedido! Executando enriquecimento completo...")
        
        # Executar enriquecimento completo
        results = enrichment.run_enrichment()
        
        if results:
            logger.info("✅ Enriquecimento de eventos para 2025 concluído!")
        else:
            logger.error("❌ Enriquecimento de eventos para 2025 falhou!")
    else:
        logger.error("❌ Teste falhou! Verifique os logs antes de continuar.")
