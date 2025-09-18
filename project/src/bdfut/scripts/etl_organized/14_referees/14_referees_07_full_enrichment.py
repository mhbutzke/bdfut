#!/usr/bin/env python3
"""
Task 2.8 - Enriquecimento Completo de Fixtures
==============================================

Objetivo: Enriquecer fixtures com múltiplos dados da API Sportmonks
Includes: referees,venue,league,season,state,round,stage,participants
Situação atual: 2.71% de cobertura de referees
Meta: Maximizar cobertura e enriquecer com dados adicionais
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

class FullEnrichmentCollector:
    def __init__(self):
        Config.validate()
        self.api_key = Config.SPORTMONKS_API_KEY
        self.base_url = Config.SPORTMONKS_BASE_URL
        self.supabase = SupabaseClient()
        self.batch_size = 10  # Limite da API multi
        
        # Includes prioritários baseados na documentação Sportmonks
        self.includes = [
            'referees',      # Árbitros
            'venue',         # Estádio/local
            'league',        # Liga
            'season',        # Temporada
            'state',         # Estado da partida
            'round',         # Rodada
            'stage',         # Fase
            'participants'   # Times participantes
        ]
        
        self.delay_between_batches = 1.0  # Respeitar rate limits
        
    def get_fixtures_to_enrich(self, limit: int = None) -> List[Dict]:
        """Buscar fixtures que precisam ser enriquecidas"""
        logger.info("🔍 Buscando fixtures para enriquecer...")
        
        # Buscar fixtures que não têm referee OU que não têm dados de enriquecimento
        query = self.supabase.client.table('fixtures').select('id,sportmonks_id')
        query = query.or_('referee.is.null,venue_id.is.null,league_id.is.null')
        
        if limit:
            query = query.limit(limit)
            
        result = query.execute()
        fixtures = result.data
        
        logger.info(f"📋 Encontradas {len(fixtures)} fixtures para enriquecer")
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
            return {'referees': 0, 'venues': 0, 'leagues': 0, 'seasons': 0, 'states': 0, 'rounds': 0, 'stages': 0, 'participants': 0}
        
        # Criar mapeamento sportmonks_id -> db_id
        id_mapping = {f['sportmonks_id']: f['id'] for f in fixtures_batch}
        
        updates = {
            'referees': 0,
            'venues': 0,
            'leagues': 0,
            'seasons': 0,
            'states': 0,
            'rounds': 0,
            'stages': 0,
            'participants': 0
        }
        
        for api_fixture in api_fixtures:
            sportmonks_id = api_fixture.get('id')
            
            if sportmonks_id not in id_mapping:
                continue
                
            db_fixture_id = id_mapping[sportmonks_id]
            
            try:
                # Preparar dados de enriquecimento
                enrichment_data = {}
                
                # 1. PROCESSAR REFEREES (objetivo principal)
                referees = api_fixture.get('referees', [])
                main_referees = [r for r in referees if r.get('type_id') == 6]
                
                if main_referees:
                    main_referee = main_referees[0]
                    referee_id = main_referee.get('referee_id')  # Usar referee_id, não id
                    enrichment_data['referee'] = str(referee_id) if referee_id else None
                    enrichment_data['referee_id'] = referee_id
                    updates['referees'] += 1
                
                # 2. PROCESSAR VENUE (estádio)
                venue = api_fixture.get('venue')
                if venue and venue.get('id'):
                    enrichment_data['venue_id'] = venue['id']
                    enrichment_data['venue_name'] = venue.get('name')
                    updates['venues'] += 1
                
                # 3. PROCESSAR LEAGUE (liga)
                league = api_fixture.get('league')
                if league and league.get('id'):
                    enrichment_data['league_id'] = league['id']
                    enrichment_data['league_name'] = league.get('name')
                    updates['leagues'] += 1
                
                # 4. PROCESSAR SEASON (temporada)
                season = api_fixture.get('season')
                if season and season.get('id'):
                    enrichment_data['season_id'] = season['id']
                    enrichment_data['season_name'] = season.get('name')
                    updates['seasons'] += 1
                
                # 5. PROCESSAR STATE (estado da partida)
                state = api_fixture.get('state')
                if state and state.get('id'):
                    enrichment_data['state_id'] = state['id']
                    enrichment_data['state_name'] = state.get('name')
                    updates['states'] += 1
                
                # 6. PROCESSAR ROUND (rodada)
                round_data = api_fixture.get('round')
                if round_data and round_data.get('id'):
                    enrichment_data['round_id'] = round_data['id']
                    enrichment_data['round_name'] = round_data.get('name')
                    updates['rounds'] += 1
                
                # 7. PROCESSAR STAGE (fase)
                stage = api_fixture.get('stage')
                if stage and stage.get('id'):
                    enrichment_data['stage_id'] = stage['id']
                    enrichment_data['stage_name'] = stage.get('name')
                    updates['stages'] += 1
                
                # 8. PROCESSAR PARTICIPANTS (times)
                participants = api_fixture.get('participants', [])
                if participants:
                    home_team = None
                    away_team = None
                    
                    for participant in participants:
                        meta = participant.get('meta', {})
                        if meta.get('location') == 'home':
                            home_team = participant
                        elif meta.get('location') == 'away':
                            away_team = participant
                    
                    if home_team:
                        enrichment_data['home_team_id'] = home_team.get('id')
                        enrichment_data['home_team_name'] = home_team.get('name')
                    
                    if away_team:
                        enrichment_data['away_team_id'] = away_team.get('id')
                        enrichment_data['away_team_name'] = away_team.get('name')
                    
                    if home_team or away_team:
                        updates['participants'] += 1
                
                # Atualizar fixture com todos os dados
                if enrichment_data:
                    self.supabase.client.table('fixtures').update(enrichment_data).eq('id', db_fixture_id).execute()
                        
            except Exception as e:
                logger.error(f"❌ Erro ao processar fixture {sportmonks_id}: {e}")
        
        return updates
    
    def collect_full_enrichment(self, max_fixtures: int = None, progress_interval: int = 50):
        """Coletar múltiplos dados para fixtures"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO COMPLETO DE FIXTURES...")
        logger.info(f"📊 Includes: {', '.join(self.includes)}")
        
        # Buscar fixtures para enriquecer
        fixtures_to_process = self.get_fixtures_to_enrich(max_fixtures)
        
        if not fixtures_to_process:
            logger.info("✅ Todas as fixtures já estão enriquecidas!")
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
            'stages': 0,
            'participants': 0
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
        logger.info(f"  - Participants: {total_updates['participants']}")
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
    collector = FullEnrichmentCollector()
    
    # Relatório inicial
    initial_coverage = collector.get_coverage_report()
    
    # Confirmar execução
    logger.info(f"\\n🎯 OBJETIVO:")
    logger.info(f"  - Processar {initial_coverage['without_referee']} fixtures sem referee")
    logger.info(f"  - Enriquecer com múltiplos dados da API")
    logger.info(f"  - Maximizar cobertura e qualidade dos dados")
    
    # Coletar dados para todas as fixtures (começar com 1000 para teste)
    logger.info("\\n🚀 Iniciando enriquecimento completo...")
    success = collector.collect_full_enrichment(max_fixtures=1000, progress_interval=25)
    
    if success:
        # Relatório final
        final_coverage = collector.get_coverage_report()
        
        improvement = final_coverage['coverage_percentage'] - initial_coverage['coverage_percentage']
        logger.info(f"\\n🎉 ENRIQUECIMENTO COMPLETO CONCLUÍDO!")
        logger.info(f"📈 Melhoria na cobertura: +{improvement:.2f}%")
        logger.info(f"📊 Cobertura final: {final_coverage['coverage_percentage']:.2f}%")
        
        if improvement > 0:
            logger.info("✅ Enriquecimento completo concluído com sucesso!")
        else:
            logger.warning("⚠️ Nenhuma melhoria detectada. Verificar logs.")
    else:
        logger.error("💥 Falha no enriquecimento completo!")

if __name__ == "__main__":
    main()
