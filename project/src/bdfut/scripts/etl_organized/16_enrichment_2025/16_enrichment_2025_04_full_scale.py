#!/usr/bin/env python3
"""
Script para enriquecimento completo de TODAS as fixtures finalizadas
Processa todas as 11.805 fixtures de 2023-2025 de forma otimizada
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

class FullScaleEventsEnrichment:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 100  # Processar em lotes de 100
        self.rate_limit_delay = 1.0  # 1 segundo entre lotes
        self.long_pause_interval = 1000  # Pausa longa a cada 1000 fixtures
        self.long_pause_delay = 30  # 30 segundos de pausa
        
    def get_all_fixtures(self):
        """Buscar todas as fixtures finalizadas de 2023-2025"""
        try:
            logger.info("🔍 Buscando todas as fixtures finalizadas...")
            
            # Buscar fixtures de 2023-2025 que estão finalizadas
            response = self.supabase.client.table('fixtures').select(
                'id, sportmonks_id, match_date, home_team_name, away_team_name, status'
            ).gte('match_date', '2023-01-01').lt('match_date', '2026-01-01').in_(
                'status', ['FT', 'FT_PEN', 'AET']
            ).order('match_date', desc=True).execute()
            
            fixtures = response.data
            logger.info(f"📊 Encontradas {len(fixtures):,} fixtures finalizadas")
            
            return fixtures
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixtures: {e}")
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
            
            completion_rate = complete_events / len(existing_events) if existing_events else 0
            is_complete = completion_rate >= 0.8  # 80% de completude
            
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
                return True, existing_count, "completo"
            
            # Buscar eventos da API
            events_data = self.sportmonks.get_events_by_fixture(fixture_id)
            
            if not events_data:
                logger.info(f"⚠️ Nenhum evento encontrado para fixture {fixture_id}")
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
            
            # Se já existem eventos incompletos, deletar antes de inserir novos
            if existing_count > 0:
                self.supabase.client.table('match_events').delete().eq('fixture_id', fixture_id).execute()
                logger.info(f"🗑️ Removidos {existing_count} eventos incompletos para fixture {fixture_id}")
            
            # Inserir eventos
            if events_to_insert:
                response = self.supabase.client.table('match_events').insert(
                    events_to_insert
                ).execute()
                
                logger.info(f"✅ Fixture {fixture_id}: {len(events_to_insert)} eventos inseridos")
                return True, len(events_to_insert), "inserido"
            
            return True, 0, "sem_eventos"
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer eventos para fixture {fixture_id}: {e}")
            return False, 0, "erro"
    
    def process_batch(self, fixtures_batch, batch_num):
        """Processar um lote de fixtures"""
        logger.info(f"🔄 Processando lote {batch_num} ({len(fixtures_batch)} fixtures)")
        
        results = {
            'total': len(fixtures_batch),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'updated': 0,
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
                    if status == "completo":
                        results['skipped'] += 1
                    elif status == "inserido":
                        results['successful'] += 1
                        results['total_events'] += event_count
                    elif status == "atualizado":
                        results['updated'] += 1
                        results['total_events'] += event_count
                    else:  # sem_eventos
                        results['skipped'] += 1
                else:
                    results['failed'] += 1
                
                # Log de progresso a cada 10 fixtures
                if (i + 1) % 10 == 0:
                    logger.info(f"   Progresso: {i+1}/{len(fixtures_batch)} fixtures processadas")
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar fixture {fixture_id}: {e}")
                results['failed'] += 1
        
        return results
    
    def run_full_enrichment(self):
        """Executar enriquecimento completo"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO COMPLETO DE EVENTOS")
        logger.info("=" * 60)
        
        # Buscar todas as fixtures
        fixtures = self.get_all_fixtures()
        
        if not fixtures:
            logger.error("❌ Nenhuma fixture encontrada")
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
            'updated': 0,
            'total_events': 0,
            'start_time': datetime.now()
        }
        
        # Processar lotes
        for batch_num in range(total_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(fixtures))
            fixtures_batch = fixtures[start_idx:end_idx]
            
            # Processar lote
            batch_results = self.process_batch(fixtures_batch, batch_num + 1)
            
            # Atualizar resultados globais
            global_results['successful'] += batch_results['successful']
            global_results['failed'] += batch_results['failed']
            global_results['skipped'] += batch_results['skipped']
            global_results['updated'] += batch_results['updated']
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
                
                # Pausa longa a cada 1000 fixtures
                if (batch_num + 1) % 10 == 0:  # A cada 10 lotes (1000 fixtures)
                    logger.info(f"⏸️ Pausa de {self.long_pause_delay}s após {batch_num + 1} lotes...")
                    time.sleep(self.long_pause_delay)
        
        # Calcular tempo total
        end_time = datetime.now()
        total_time = end_time - global_results['start_time']
        
        # Resumo final
        logger.info("\\n" + "=" * 60)
        logger.info("📊 RESUMO FINAL DO ENRIQUECIMENTO COMPLETO:")
        logger.info(f"   Fixtures processadas: {global_results['total_fixtures']:,}")
        logger.info(f"   Lotes processados: {global_results['total_batches']}")
        logger.info(f"   Sucessos: {global_results['successful']:,}")
        logger.info(f"   Atualizações: {global_results['updated']:,}")
        logger.info(f"   Ignorados: {global_results['skipped']:,}")
        logger.info(f"   Falhas: {global_results['failed']:,}")
        logger.info(f"   Total de eventos coletados: {global_results['total_events']:,}")
        logger.info(f"   Tempo total: {total_time}")
        
        total_successful = global_results['successful'] + global_results['updated']
        success_rate = (total_successful / global_results['total_fixtures'] * 100) if global_results['total_fixtures'] > 0 else 0
        logger.info(f"   Taxa de sucesso: {success_rate:.1f}%")
        
        logger.info("\\n🎉 ENRIQUECIMENTO COMPLETO FINALIZADO!")

def main():
    """Função principal"""
    try:
        enrichment = FullScaleEventsEnrichment()
        enrichment.run_full_enrichment()
        
    except KeyboardInterrupt:
        logger.info("\\n⏹️ Enriquecimento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()
