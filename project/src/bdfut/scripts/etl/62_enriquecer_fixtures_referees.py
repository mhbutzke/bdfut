#!/usr/bin/env python3
"""
Script para enriquecer fixtures com nomes dos referees
Coleta dados de referees da API Sportmonks e popula o campo referee na tabela fixtures
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from bdfut.core.sportmonks_client import SportmonksClient
from supabase import create_client
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FixturesRefereesEnricher:
    """Classe para enriquecer fixtures com dados de referees"""
    
    def __init__(self):
        """Inicializar clientes"""
        try:
            self.config = Config()
            self.sportmonks = SportmonksClient()
            self.supabase = create_client(self.config.SUPABASE_URL, self.config.SUPABASE_KEY)
            logger.info("✅ Clientes inicializados com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar clientes: {e}")
            raise
    
    def get_fixtures_without_referees(self, limit: int = 1000) -> List[Dict]:
        """Buscar fixtures que não têm referee preenchido"""
        try:
            response = self.supabase.table('fixtures').select(
                'id,sportmonks_id,league_id,season_id,match_date,status'
            ).is_('referee', 'null').limit(limit).execute()
            
            fixtures = response.data
            logger.info(f"📊 {len(fixtures)} fixtures sem referee encontradas")
            return fixtures
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixtures: {e}")
            return []
    
    def get_fixture_details_from_api(self, fixture_id: int) -> Optional[Dict]:
        """Buscar detalhes de uma fixture específica da API Sportmonks"""
        try:
            response = self.sportmonks._make_request(
                f'/fixtures/{fixture_id}',
                {'include': 'referees'}
            )
            
            return response.get('data', {})
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixture {fixture_id}: {e}")
            return None
    
    def extract_referee_names(self, fixture_data: Dict) -> Optional[str]:
        """Extrair nomes dos referees dos dados da fixture"""
        referees = fixture_data.get('referees', [])
        if not referees:
            return None
        
        referee_names = []
        for referee in referees:
            name = referee.get('name')
            if name:
                referee_names.append(name)
        
        return ', '.join(referee_names) if referee_names else None
    
    def update_fixture_referee(self, fixture_id: int, referee_names: str) -> bool:
        """Atualizar o campo referee de uma fixture"""
        try:
            self.supabase.table('fixtures').update({
                'referee': referee_names,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', fixture_id).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar fixture {fixture_id}: {e}")
            return False
    
    def enrich_fixtures_batch(self, fixtures: List[Dict], batch_size: int = 50) -> Dict[str, int]:
        """Enriquecer um lote de fixtures com dados de referees"""
        stats = {
            'processed': 0,
            'enriched': 0,
            'errors': 0,
            'skipped': 0
        }
        
        for i, fixture in enumerate(fixtures):
            try:
                fixture_id = fixture['id']
                sportmonks_id = fixture['sportmonks_id']
                
                logger.info(f"🔍 Processando fixture {i+1}/{len(fixtures)} (ID: {fixture_id})")
                
                # Buscar detalhes da fixture da API
                fixture_data = self.get_fixture_details_from_api(sportmonks_id)
                if not fixture_data:
                    stats['skipped'] += 1
                    continue
                
                # Extrair nomes dos referees
                referee_names = self.extract_referee_names(fixture_data)
                if not referee_names:
                    stats['skipped'] += 1
                    continue
                
                # Atualizar fixture
                if self.update_fixture_referee(fixture_id, referee_names):
                    stats['enriched'] += 1
                    logger.info(f"✅ Fixture {fixture_id} enriquecida com referee: {referee_names}")
                else:
                    stats['errors'] += 1
                
                stats['processed'] += 1
                
                # Rate limit
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar fixture {fixture.get('id', 'unknown')}: {e}")
                stats['errors'] += 1
        
        return stats
    
    def get_enrichment_stats(self) -> Dict[str, int]:
        """Obter estatísticas de enriquecimento"""
        try:
            # Total de fixtures
            total_response = self.supabase.table('fixtures').select('id', count='exact').execute()
            total_fixtures = total_response.count
            
            # Fixtures com referee
            with_referee_response = self.supabase.table('fixtures').select('id', count='exact').not_.is_('referee', 'null').execute()
            with_referee = with_referee_response.count
            
            # Fixtures sem referee
            without_referee = total_fixtures - with_referee
            
            return {
                'total_fixtures': total_fixtures,
                'with_referee': with_referee,
                'without_referee': without_referee,
                'percentage_enriched': round((with_referee / total_fixtures) * 100, 2) if total_fixtures > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 ENRIQUECENDO FIXTURES COM REFEREES")
    logger.info("=" * 80)
    
    try:
        # Inicializar enricher
        enricher = FixturesRefereesEnricher()
        
        # Obter estatísticas iniciais
        logger.info("📊 Estatísticas iniciais:")
        initial_stats = enricher.get_enrichment_stats()
        for key, value in initial_stats.items():
            logger.info(f"   • {key}: {value}")
        
        # Buscar fixtures sem referee
        fixtures = enricher.get_fixtures_without_referees(limit=1000)
        if not fixtures:
            logger.info("✅ Todas as fixtures já têm referee preenchido!")
            return
        
        logger.info(f"🔍 Encontradas {len(fixtures)} fixtures para enriquecer")
        
        # Enriquecer fixtures
        logger.info("🚀 Iniciando enriquecimento...")
        stats = enricher.enrich_fixtures_batch(fixtures)
        
        # Relatório final
        logger.info("=" * 80)
        logger.info("📊 RELATÓRIO FINAL")
        logger.info("=" * 80)
        logger.info(f"   • Fixtures processadas: {stats['processed']}")
        logger.info(f"   • Fixtures enriquecidas: {stats['enriched']}")
        logger.info(f"   • Fixtures ignoradas: {stats['skipped']}")
        logger.info(f"   • Erros: {stats['errors']}")
        
        # Estatísticas finais
        final_stats = enricher.get_enrichment_stats()
        logger.info("📊 Estatísticas finais:")
        for key, value in final_stats.items():
            logger.info(f"   • {key}: {value}")
        
        logger.info("=" * 80)
        logger.info("✅ ENRIQUECIMENTO CONCLUÍDO!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return

if __name__ == "__main__":
    main()
