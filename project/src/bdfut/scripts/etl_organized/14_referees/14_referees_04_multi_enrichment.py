#!/usr/bin/env python3
"""
Task 2.8 - Enriquecimento Multi-Include (Referees + Dados Adicionais)
====================================================================

Objetivo: Coletar referees + dados adicionais em uma única chamada API
Includes: referees,venue,league,season,state,round,stage,participants
Situação atual: 2.71% de cobertura de referees
Meta: Maximizar coleta de dados por chamada API
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

import requests
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bdfut.core.supabase_client import SupabaseClient
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiEnrichmentCollector:
    def __init__(self):
        Config.validate()
        self.api_key = Config.SPORTMONKS_API_KEY
        self.base_url = Config.SPORTMONKS_BASE_URL
        self.supabase = SupabaseClient()
        self.batch_size = 10  # Limite da API multi
        
        # Includes prioritários baseados na documentação Sportmonks
        self.includes = [
            'referees',      # Árbitros (objetivo principal)
            'venue',         # Estádio/local
            'league',        # Liga
            'season',        # Temporada
            'state',         # Estado da partida
            'round',         # Rodada
            'stage',         # Fase
            'participants'   # Times participantes
        ]
        
        self.delay_between_batches = 1.0  # Respeitar rate limits
        
    def get_fixtures_without_referee(self, limit: int = None) -> List[Dict]:
        """Buscar fixtures sem referee para enriquecer"""
        logger.info("🔍 Buscando fixtures sem referee...")
        
        query = self.supabase.client.table('fixtures').select('id,sportmonks_id')
        query = query.or_('referee.is.null,referee.eq.')
        
        if limit:
            query = query.limit(limit)
            
        result = query.execute()
        fixtures = result.data
        
        logger.info(f"📋 Encontradas {len(fixtures)} fixtures sem referee")
        return fixtures
    
    def fetch_multi_data_batch(self, fixture_ids: List[str]) -> Dict:
        """Buscar múltiplos dados para um lote de fixtures via API multi"""
        fixture_ids_str = ','.join(fixture_ids)
        
        url = f'{self.base_url}/fixtures/multi/{fixture_ids_str}'
        params = {
            'api_token': self.api_key,
            'include': ';'.join(self.includes)  # Usar ; como separador
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na API para lote {fixture_ids_str}: {e}")
            return []
    
    def process_multi_data_batch(self, fixtures_batch: List[Dict]) -> Dict:
        """Processar um lote de fixtures e extrair múltiplos dados"""
        sportmonks_ids = [str(f['sportmonks_id']) for f in fixtures_batch]
        
        # Buscar dados da API
        api_fixtures = self.fetch_multi_data_batch(sportmonks_ids)
        
        if not api_fixtures:
            return {'referees': 0, 'venues': 0, 'leagues': 0, 'seasons': 0}
        
        # Criar mapeamento sportmonks_id -> db_id
        id_mapping = {f['sportmonks_id']: f['id'] for f in fixtures_batch}
        
        updates = {
            'referees': 0,
            'venues': 0,
            'leagues': 0,
            'seasons': 0,
            'states': 0,
            'rounds': 0,
            'stages': 0
        }
        
        for api_fixture in api_fixtures:
            sportmonks_id = api_fixture.get('id')
            
            if sportmonks_id not in id_mapping:
                continue
                
            db_fixture_id = id_mapping[sportmonks_id]
            
            try:
                # 1. PROCESSAR REFEREES (objetivo principal)
                referees = api_fixture.get('referees', [])
                main_referees = [r for r in referees if r.get('type_id') == 6]
                
                if main_referees:
                    main_referee = main_referees[0]
                    referee_id = main_referee.get('id')
                    
                    if referee_id:
                        self.supabase.client.table('fixtures').update({
                            'referee': str(referee_id)
                        }).eq('id', db_fixture_id).execute()
                        updates['referees'] += 1
                
                # 2. PROCESSAR VENUE (estádio)
                venue = api_fixture.get('venue')
                if venue and venue.get('id'):
                    # Verificar se venue já existe
                    existing_venue = self.supabase.client.table('venues').select('id').eq('sportmonks_id', venue['id']).execute().data
                    
                    if not existing_venue:
                        venue_data = {
                            'sportmonks_id': venue['id'],
                            'name': venue.get('name'),
                            'city': venue.get('city'),
                            'capacity': venue.get('capacity'),
                            'image_path': venue.get('image_path'),
                            'coordinates': venue.get('coordinates'),
                            'created_at': datetime.now().isoformat()
                        }
                        
                        self.supabase.client.table('venues').insert(venue_data).execute()
                        updates['venues'] += 1
                
                # 3. PROCESSAR LEAGUE (liga)
                league = api_fixture.get('league')
                if league and league.get('id'):
                    existing_league = self.supabase.client.table('leagues').select('id').eq('sportmonks_id', league['id']).execute().data
                    
                    if not existing_league:
                        league_data = {
                            'sportmonks_id': league['id'],
                            'name': league.get('name'),
                            'country': str(league.get('country_id', '')),
                            'logo_url': league.get('image_path'),
                            'active': True,
                            'created_at': datetime.now().isoformat()
                        }
                        
                        self.supabase.client.table('leagues').insert(league_data).execute()
                        updates['leagues'] += 1
                
                # 4. PROCESSAR SEASON (temporada)
                season = api_fixture.get('season')
                if season and season.get('id'):
                    existing_season = self.supabase.client.table('seasons').select('id').eq('sportmonks_id', season['id']).execute().data
                    
                    if not existing_season:
                        season_data = {
                            'sportmonks_id': season['id'],
                            'name': season.get('name'),
                            'league_id': league['id'] if league else None,
                            'is_current': season.get('is_current', False),
                            'starting_at': season.get('starting_at'),
                            'ending_at': season.get('ending_at'),
                            'created_at': datetime.now().isoformat()
                        }
                        
                        self.supabase.client.table('seasons').insert(season_data).execute()
                        updates['seasons'] += 1
                
                # 5. PROCESSAR STATE (estado da partida)
                state = api_fixture.get('state')
                if state and state.get('id'):
                    # Atualizar fixture com state_id se não existir
                    current_fixture = self.supabase.client.table('fixtures').select('state_id').eq('id', db_fixture_id).execute().data
                    
                    if current_fixture and not current_fixture[0].get('state_id'):
                        self.supabase.client.table('fixtures').update({
                            'state_id': state['id']
                        }).eq('id', db_fixture_id).execute()
                        updates['states'] += 1
                
                # 6. PROCESSAR ROUND (rodada)
                round_data = api_fixture.get('round')
                if round_data and round_data.get('id'):
                    existing_round = self.supabase.client.table('rounds').select('id').eq('sportmonks_id', round_data['id']).execute().data
                    
                    if not existing_round:
                        round_insert_data = {
                            'sportmonks_id': round_data['id'],
                            'name': round_data.get('name'),
                            'stage_id': api_fixture.get('stage', {}).get('id'),
                            'starting_at': round_data.get('starting_at'),
                            'ending_at': round_data.get('ending_at'),
                            'created_at': datetime.now().isoformat()
                        }
                        
                        self.supabase.client.table('rounds').insert(round_insert_data).execute()
                        updates['rounds'] += 1
                
                # 7. PROCESSAR STAGE (fase)
                stage = api_fixture.get('stage')
                if stage and stage.get('id'):
                    existing_stage = self.supabase.client.table('stages').select('id').eq('sportmonks_id', stage['id']).execute().data
                    
                    if not existing_stage:
                        stage_data = {
                            'sportmonks_id': stage['id'],
                            'name': stage.get('name'),
                            'type': stage.get('type'),
                            'starting_at': stage.get('starting_at'),
                            'ending_at': stage.get('ending_at'),
                            'created_at': datetime.now().isoformat()
                        }
                        
                        self.supabase.client.table('stages').insert(stage_data).execute()
                        updates['stages'] += 1
                        
            except Exception as e:
                logger.error(f"❌ Erro ao processar fixture {sportmonks_id}: {e}")
        
        return updates
    
    def collect_multi_enrichment(self, max_fixtures: int = None, progress_interval: int = 50):
        """Coletar múltiplos dados para fixtures sem referee"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO MULTI-INCLUDE...")
        logger.info(f"📊 Includes: {', '.join(self.includes)}")
        
        # Buscar fixtures sem referee
        fixtures_to_process = self.get_fixtures_without_referee(max_fixtures)
        
        if not fixtures_to_process:
            logger.info("✅ Todas as fixtures já têm referee!")
            return True
        
        total_fixtures = len(fixtures_to_process)
        total_batches = (total_fixtures + self.batch_size - 1) // self.batch_size
        
        logger.info(f"📊 Processando {total_fixtures} fixtures em {total_batches} lotes")
        
        # Estimativa de tempo
        estimated_minutes = total_batches * self.delay_between_batches / 60
        eta = datetime.now() + timedelta(minutes=estimated_minutes)
        logger.info(f"⏱️ ETA estimado: {eta.strftime('%H:%M:%S')} ({estimated_minutes:.1f} minutos)")
        
        total_updates = {
            'referees': 0,
            'venues': 0,
            'leagues': 0,
            'seasons': 0,
            'states': 0,
            'rounds': 0,
            'stages': 0
        }
        
        start_time = datetime.now()
        
        # Processar em lotes
        for i in range(0, total_fixtures, self.batch_size):
            batch_num = (i // self.batch_size) + 1
            batch = fixtures_to_process[i:i + self.batch_size]
            
            logger.info(f"📡 Processando lote {batch_num}/{total_batches} ({len(batch)} fixtures)")
            
            try:
                updates = self.process_multi_data_batch(batch)
                
                # Somar atualizações
                for key in total_updates:
                    total_updates[key] += updates[key]
                
                logger.info(f"  ✅ Lote {batch_num}: {updates}")
                
                # Progress report
                if batch_num % progress_interval == 0:
                    elapsed = datetime.now() - start_time
                    rate = batch_num / elapsed.total_seconds() * 60  # batches per minute
                    eta_minutes = (total_batches - batch_num) / rate if rate > 0 else 0
                    eta_time = datetime.now() + timedelta(minutes=eta_minutes)
                    
                    logger.info(f"📈 Progresso: {batch_num}/{total_batches} lotes ({batch_num/total_batches*100:.1f}%)")
                    logger.info(f"⏱️ Taxa: {rate:.1f} lotes/min, ETA: {eta_time.strftime('%H:%M:%S')}")
                    logger.info(f"💾 Total atualizado: {total_updates}")
                
            except Exception as e:
                logger.error(f"❌ Erro no lote {batch_num}: {e}")
            
            # Pausa entre lotes
            time.sleep(self.delay_between_batches)
        
        # Relatório final
        elapsed_total = datetime.now() - start_time
        logger.info(f"\\n📊 RELATÓRIO FINAL:")
        logger.info(f"  - Fixtures processadas: {total_fixtures}")
        logger.info(f"  - Referees: {total_updates['referees']}")
        logger.info(f"  - Venues: {total_updates['venues']}")
        logger.info(f"  - Leagues: {total_updates['leagues']}")
        logger.info(f"  - Seasons: {total_updates['seasons']}")
        logger.info(f"  - States: {total_updates['states']}")
        logger.info(f"  - Rounds: {total_updates['rounds']}")
        logger.info(f"  - Stages: {total_updates['stages']}")
        logger.info(f"  - Tempo total: {elapsed_total}")
        
        return total_updates['referees'] > 0
    
    def get_coverage_report(self):
        """Gerar relatório de cobertura atual"""
        logger.info("📊 Gerando relatório de cobertura...")
        
        result = self.supabase.client.table('fixtures').select('id').execute()
        total_fixtures = len(result.data)
        
        result_with_referee = self.supabase.client.table('fixtures').select('id').is_('referee', 'null').execute()
        fixtures_without_referee = len(result_with_referee.data)
        
        fixtures_with_referee = total_fixtures - fixtures_without_referee
        coverage_percentage = fixtures_with_referee * 100.0 / total_fixtures
        
        logger.info(f"📈 COBERTURA ATUAL:")
        logger.info(f"  - Total fixtures: {total_fixtures}")
        logger.info(f"  - Com referee: {fixtures_with_referee} ({coverage_percentage:.2f}%)")
        logger.info(f"  - Sem referee: {fixtures_without_referee}")
        
        return {
            'total': total_fixtures,
            'with_referee': fixtures_with_referee,
            'without_referee': fixtures_without_referee,
            'coverage_percentage': coverage_percentage
        }

def main():
    """Função principal"""
    collector = MultiEnrichmentCollector()
    
    # Relatório inicial
    initial_coverage = collector.get_coverage_report()
    
    # Confirmar execução
    logger.info(f"\\n🎯 OBJETIVO:")
    logger.info(f"  - Processar {initial_coverage['without_referee']} fixtures sem referee")
    logger.info(f"  - Coletar múltiplos dados por chamada API")
    logger.info(f"  - Maximizar eficiência da coleta")
    
    # Coletar dados para todas as fixtures (começar com 1000 para teste)
    logger.info("\\n🚀 Iniciando enriquecimento multi-include...")
    success = collector.collect_multi_enrichment(max_fixtures=1000, progress_interval=25)
    
    if success:
        # Relatório final
        final_coverage = collector.get_coverage_report()
        
        improvement = final_coverage['coverage_percentage'] - initial_coverage['coverage_percentage']
        logger.info(f"\\n🎉 ENRIQUECIMENTO MULTI-INCLUDE CONCLUÍDO!")
        logger.info(f"📈 Melhoria na cobertura: +{improvement:.2f}%")
        logger.info(f"📊 Cobertura final: {final_coverage['coverage_percentage']:.2f}%")
        
        if improvement > 0:
            logger.info("✅ Enriquecimento multi-include concluído com sucesso!")
        else:
            logger.warning("⚠️ Nenhuma melhoria detectada. Verificar logs.")
    else:
        logger.error("💥 Falha no enriquecimento multi-include!")

if __name__ == "__main__":
    main()
