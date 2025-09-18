#!/usr/bin/env python3
"""
Script otimizado para enriquecer TODAS as fixtures com eventos
Baseado no padrão testado e validado
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

class OptimizedEventsEnrichment:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 100  # Processar em lotes de 100
        self.rate_limit_delay = 0.5  # 500ms entre requests
        
    def get_all_fixtures(self, year: int = None, limit: int = None):
        """Obter todas as fixtures finalizadas"""
        try:
            query = self.supabase.client.table('fixtures').select(
                'id, sportmonks_id, match_date, home_score, away_score, status'
            ).in_('status', ['FT', 'FT_PEN', 'AET']).order('match_date', desc=True)
            
            if year:
                query = query.gte('match_date', f'{year}-01-01').lt('match_date', f'{year+1}-01-01')
                
            if limit:
                query = query.limit(limit)
                
            response = query.execute()
            fixtures = response.data
            
            logger.info(f"📋 Encontradas {len(fixtures):,} fixtures para processamento")
            return fixtures
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixtures: {e}")
            return []
            
    def check_existing_events(self, fixture_id: int):
        """Verificar se já existem eventos para a fixture e se estão completos"""
        try:
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
                return True, 'skipped'
            elif existing_count > 0:
                logger.warning(f"⚠️ Fixture {fixture_id} possui eventos incompletos ({existing_count} eventos). "
                              f"Atualizando com dados da API...")
                # Deletar eventos existentes incompletos
                self.supabase.client.table('match_events').delete().eq('fixture_id', fixture_id).execute()
                
            # Buscar eventos da API
            events_data = self.sportmonks.get_events_by_fixture(fixture_id)
            
            if not events_data:
                logger.warning(f"❌ Nenhum evento encontrado para fixture {fixture_id}")
                return False, 'no_events'
                
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
                return True, 'success'
                
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer eventos para fixture {fixture_id}: {e}")
            return False, 'error'
            
    def run_enrichment(self, year: int = None, limit: int = None, start_from: int = 0):
        """Executar enriquecimento otimizado de eventos"""
        logger.info(f"🚀 INICIANDO ENRIQUECIMENTO OTIMIZADO DE EVENTOS")
        if year:
            logger.info(f"📅 Processando fixtures de {year}")
        if limit:
            logger.info(f"🔢 Limitado a {limit:,} fixtures")
        if start_from > 0:
            logger.info(f"📍 Iniciando da fixture {start_from}")
            
        fixtures = self.get_all_fixtures(year, limit)
        
        if not fixtures:
            logger.error("❌ Nenhuma fixture encontrada para enriquecimento")
            return
            
        # Aplicar offset se especificado
        if start_from > 0:
            fixtures = fixtures[start_from:]
            
        results = {
            'total_fixtures': len(fixtures),
            'successful': 0,
            'skipped': 0,
            'no_events': 0,
            'errors': 0,
            'total_events': 0,
            'start_time': datetime.now()
        }
        
        # Processar em lotes
        for batch_start in range(0, len(fixtures), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(fixtures))
            batch_fixtures = fixtures[batch_start:batch_end]
            
            logger.info(f"\\n📦 Processando lote {batch_start//self.batch_size + 1}: "
                       f"fixtures {batch_start + 1} a {batch_end}")
            
            for i, fixture in enumerate(batch_fixtures, batch_start + 1):
                fixture_id = fixture['sportmonks_id']
                
                try:
                    success, status = self.enrich_fixture_events(fixture)
                    
                    if success:
                        if status == 'success':
                            results['successful'] += 1
                        elif status == 'skipped':
                            results['skipped'] += 1
                    else:
                        if status == 'no_events':
                            results['no_events'] += 1
                        else:
                            results['errors'] += 1
                            
                    # Rate limiting
                    time.sleep(self.rate_limit_delay)
                    
                    # Log de progresso a cada 50 fixtures
                    if i % 50 == 0:
                        elapsed = datetime.now() - results['start_time']
                        rate = i / elapsed.total_seconds() * 60  # fixtures por minuto
                        eta_minutes = (len(fixtures) - i) / rate if rate > 0 else 0
                        
                        logger.info(f"📊 Progresso: {i}/{len(fixtures)} "
                                   f"({i/len(fixtures)*100:.1f}%) - "
                                   f"Taxa: {rate:.1f} fixtures/min - "
                                   f"ETA: {eta_minutes:.0f}min")
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao processar fixture {fixture_id}: {e}")
                    results['errors'] += 1
                    
        # Resumo dos resultados
        elapsed_total = datetime.now() - results['start_time']
        logger.info(f"\\n📊 RESUMO DO ENRIQUECIMENTO:")
        logger.info(f"   Fixtures processadas: {results['total_fixtures']:,}")
        logger.info(f"   Sucessos: {results['successful']:,}")
        logger.info(f"   Puladas (já completas): {results['skipped']:,}")
        logger.info(f"   Sem eventos: {results['no_events']:,}")
        logger.info(f"   Erros: {results['errors']:,}")
        logger.info(f"   Tempo total: {elapsed_total}")
        
        total_processed = results['successful'] + results['skipped'] + results['no_events'] + results['errors']
        if total_processed > 0:
            success_rate = (results['successful'] + results['skipped']) / total_processed * 100
            logger.info(f"   Taxa de sucesso: {success_rate:.1f}%")
        
        return results

if __name__ == "__main__":
    enrichment = OptimizedEventsEnrichment()
    
    # Testar com 500 fixtures primeiro
    logger.info("🧪 TESTANDO COM 500 FIXTURES PRIMEIRO")
    results = enrichment.run_enrichment(limit=500)
    
    if results and (results['successful'] + results['skipped']) > 0:
        logger.info("\\n✅ Teste bem-sucedido! Executando enriquecimento completo...")
        
        # Executar enriquecimento completo
        results = enrichment.run_enrichment()
        
        if results:
            logger.info("✅ Enriquecimento completo de eventos concluído!")
        else:
            logger.error("❌ Enriquecimento completo de eventos falhou!")
    else:
        logger.error("❌ Teste falhou! Verifique os logs antes de continuar.")
