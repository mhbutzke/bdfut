#!/usr/bin/env python3
"""
Script para enriquecimento em massa de TODAS as fixtures restantes
Processa todas as 11.754 fixtures sem eventos de forma otimizada
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

class MassiveScaleEventsEnrichment:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 50  # Lotes menores para melhor controle
        self.rate_limit_delay = 0.5  # 0.5 segundos entre requests
        self.long_pause_interval = 500  # Pausa a cada 500 fixtures
        self.long_pause_delay = 10  # 10 segundos de pausa
        
    def get_fixtures_without_events(self):
        """Buscar fixtures que não possuem eventos"""
        try:
            logger.info("🔍 Buscando fixtures sem eventos...")
            
            # Buscar todas as fixtures finalizadas
            response = self.supabase.client.table('fixtures').select(
                'id, sportmonks_id, match_date, home_team_name, away_team_name, status'
            ).gte('match_date', '2023-01-01').lt('match_date', '2026-01-01').in_(
                'status', ['FT', 'FT_PEN', 'AET']
            ).order('match_date', desc=True).execute()
            
            all_fixtures = response.data
            logger.info(f"📊 Encontradas {len(all_fixtures):,} fixtures finalizadas")
            
            # Buscar fixtures que já possuem eventos
            response = self.supabase.client.table('match_events').select('fixture_id').execute()
            fixtures_with_events = set([event['fixture_id'] for event in response.data])
            logger.info(f"📊 {len(fixtures_with_events):,} fixtures já possuem eventos")
            
            # Filtrar fixtures sem eventos
            fixtures_without_events = [
                fixture for fixture in all_fixtures 
                if fixture['sportmonks_id'] not in fixtures_with_events
            ]
            
            logger.info(f"📊 {len(fixtures_without_events):,} fixtures precisam de enriquecimento")
            
            return fixtures_without_events
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixtures: {e}")
            return []
    
    def enrich_fixture_events(self, fixture):
        """Enriquecer eventos para uma fixture"""
        fixture_id = fixture['sportmonks_id']
        
        try:
            # Buscar eventos da API
            events_data = self.sportmonks.get_events_by_fixture(fixture_id)
            
            if not events_data:
                return True, 0, "sem_eventos"
            
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
                
                return True, len(events_to_insert), "inserido"
            
            return True, 0, "sem_eventos"
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer eventos para fixture {fixture_id}: {e}")
            return False, 0, "erro"
    
    def process_batch(self, fixtures_batch, batch_num, total_batches):
        """Processar um lote de fixtures"""
        logger.info(f"🔄 Processando lote {batch_num}/{total_batches} ({len(fixtures_batch)} fixtures)")
        
        results = {
            'total': len(fixtures_batch),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_events': 0
        }
        
        for i, fixture in enumerate(fixtures_batch):
            fixture_id = fixture['sportmonks_id']
            match_date = fixture['match_date']
            home_team = fixture['home_team_name']
            away_team = fixture['away_team_name']
            
            try:
                success, event_count, status = self.enrich_fixture_events(fixture)
                
                if success:
                    if status == "inserido":
                        results['successful'] += 1
                        results['total_events'] += event_count
                        logger.info(f"✅ {fixture_id}: {event_count} eventos ({home_team} vs {away_team})")
                    else:  # sem_eventos
                        results['skipped'] += 1
                        logger.info(f"⚠️ {fixture_id}: Sem eventos ({home_team} vs {away_team})")
                else:
                    results['failed'] += 1
                    logger.error(f"❌ {fixture_id}: Falha no enriquecimento")
                
                # Log de progresso a cada 10 fixtures
                if (i + 1) % 10 == 0:
                    logger.info(f"   Progresso: {i+1}/{len(fixtures_batch)} fixtures processadas")
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar fixture {fixture_id}: {e}")
                results['failed'] += 1
        
        return results
    
    def run_massive_enrichment(self):
        """Executar enriquecimento em massa"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO EM MASSA DE EVENTOS")
        logger.info("=" * 60)
        
        # Buscar fixtures sem eventos
        fixtures = self.get_fixtures_without_events()
        
        if not fixtures:
            logger.info("✅ Todas as fixtures já possuem eventos!")
            return
        
        # Dividir em lotes
        total_batches = (len(fixtures) + self.batch_size - 1) // self.batch_size
        logger.info(f"📊 Processando {len(fixtures):,} fixtures em {total_batches} lotes")
        
        # Resultados globais
        global_results = {
            'total_fixtures': len(fixtures),
            'total_batches': total_batches,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_events': 0,
            'start_time': datetime.now()
        }
        
        # Processar lotes
        for batch_num in range(total_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(fixtures))
            fixtures_batch = fixtures[start_idx:end_idx]
            
            # Processar lote
            batch_results = self.process_batch(fixtures_batch, batch_num + 1, total_batches)
            
            # Atualizar resultados globais
            global_results['successful'] += batch_results['successful']
            global_results['failed'] += batch_results['failed']
            global_results['skipped'] += batch_results['skipped']
            global_results['total_events'] += batch_results['total_events']
            
            # Log do lote
            logger.info(f"📊 Lote {batch_num + 1}/{total_batches} concluído:")
            logger.info(f"   Sucessos: {batch_results['successful']}")
            logger.info(f"   Falhas: {batch_results['failed']}")
            logger.info(f"   Ignorados: {batch_results['skipped']}")
            logger.info(f"   Eventos coletados: {batch_results['total_events']}")
            
            # Pausa entre lotes (exceto no último)
            if batch_num < total_batches - 1:
                time.sleep(self.rate_limit_delay)
                
                # Pausa longa a cada 500 fixtures
                if (batch_num + 1) % 10 == 0:  # A cada 10 lotes (500 fixtures)
                    logger.info(f"⏸️ Pausa de {self.long_pause_delay}s após {batch_num + 1} lotes...")
                    time.sleep(self.long_pause_delay)
        
        # Calcular tempo total
        end_time = datetime.now()
        total_time = end_time - global_results['start_time']
        
        # Resumo final
        logger.info("\\n" + "=" * 60)
        logger.info("📊 RESUMO FINAL DO ENRIQUECIMENTO EM MASSA:")
        logger.info(f"   Fixtures processadas: {global_results['total_fixtures']:,}")
        logger.info(f"   Lotes processados: {global_results['total_batches']}")
        logger.info(f"   Sucessos: {global_results['successful']:,}")
        logger.info(f"   Ignorados: {global_results['skipped']:,}")
        logger.info(f"   Falhas: {global_results['failed']:,}")
        logger.info(f"   Total de eventos coletados: {global_results['total_events']:,}")
        logger.info(f"   Tempo total: {total_time}")
        
        success_rate = (global_results['successful'] / global_results['total_fixtures'] * 100) if global_results['total_fixtures'] > 0 else 0
        logger.info(f"   Taxa de sucesso: {success_rate:.1f}%")
        
        logger.info("\\n🎉 ENRIQUECIMENTO EM MASSA FINALIZADO!")

def main():
    """Função principal"""
    try:
        enrichment = MassiveScaleEventsEnrichment()
        enrichment.run_massive_enrichment()
        
    except KeyboardInterrupt:
        logger.info("\\n⏹️ Enriquecimento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()
