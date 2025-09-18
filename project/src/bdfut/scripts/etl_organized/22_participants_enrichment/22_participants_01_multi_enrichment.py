#!/usr/bin/env python3
"""
Script para enriquecer a tabela match_participants usando chamadas de múltiplos IDs
Processa fixtures em lotes de 10 usando o endpoint multi da API Sportmonks
"""

import sys
import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ParticipantsEnrichment:
    """Classe para enriquecimento de participantes usando endpoint multi"""
    
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.batch_size = 10
        self.processed_count = 0
        self.total_inserted = 0
        self.errors = 0
        
    def get_fixtures_batch(self, offset: int, limit: int) -> List[Dict]:
        """Buscar lote de fixtures para processamento"""
        try:
            response = self.supabase.client.from_('fixtures').select(
                'fixture_id, match_date, home_team_name, away_team_name'
            ).order('match_date', desc=True).range(offset, offset + limit - 1).execute()
            
            if response.data:
                logger.info(f"📊 Buscando fixtures {offset+1}-{offset+len(response.data)}")
                return response.data
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures: {e}")
            return []
    
    def get_existing_participants(self, fixture_ids: List[int]) -> set:
        """Buscar participantes já existentes para evitar duplicatas"""
        try:
            response = self.supabase.client.from_('match_participants').select('id').in_('id', fixture_ids).execute()
            return {row['id'] for row in response.data} if response.data else set()
        except Exception as e:
            logger.error(f"Erro ao buscar participantes existentes: {e}")
            return set()
    
    def process_participants_batch(self, fixtures: List[Dict]) -> int:
        """Processar um lote de fixtures para participantes"""
        if not fixtures:
            return 0
            
        fixture_ids = [str(f['fixture_id']) for f in fixtures]
        fixture_ids_str = ','.join(fixture_ids)
        
        logger.info(f"🔍 Processando lote de {len(fixtures)} fixtures: {fixture_ids_str}")
        
        try:
            # Chamar API com múltiplos IDs
            api_response = self.sportmonks.get_fixtures_multi(
                fixture_ids_str, 
                include='participants'
            )
            
            if not api_response or 'data' not in api_response:
                logger.warning(f"Nenhum dado retornado para fixtures {fixture_ids_str}")
                return 0
            
            total_inserted = 0
            
            # Processar cada fixture na resposta
            for fixture_data in api_response['data']:
                fixture_id = fixture_data.get('id')
                participants_data = fixture_data.get('participants', [])
                
                if not participants_data:
                    continue
                
                logger.info(f"    📊 Processando fixture {fixture_id}")
                
                # Verificar participantes existentes
                existing_ids = self.get_existing_participants([p.get('id') for p in participants_data])
                
                # Preparar dados para inserção
                participants_to_insert = []
                for participant in participants_data:
                    participant_id = participant.get('id')
                    
                    if participant_id in existing_ids:
                        continue
                    
                    mapped_participant = {
                        'id': participant_id,
                        'sport_id': participant.get('sport_id'),
                        'country_id': participant.get('country_id'),
                        'venue_id': participant.get('venue_id'),
                        'gender': participant.get('gender'),
                        'name': participant.get('name'),
                        'short_code': participant.get('short_code'),
                        'image_path': participant.get('image_path'),
                        'founded': participant.get('founded'),
                        'type': participant.get('type'),
                        'placeholder': participant.get('placeholder'),
                        'last_played_at': participant.get('last_played_at'),
                        'meta': participant.get('meta'),
                        'created_at': datetime.now().isoformat()
                    }
                    
                    participants_to_insert.append(mapped_participant)
                
                # Inserir participantes
                if participants_to_insert:
                    try:
                        response = self.supabase.client.from_('match_participants').upsert(
                            participants_to_insert, 
                            on_conflict='id'
                        ).execute()
                        
                        if response.data:
                            inserted_count = len(response.data)
                            logger.info(f"       👥 Participantes: +{inserted_count}")
                            total_inserted += inserted_count
                        else:
                            logger.warning(f"       👥 Participantes: Nenhum participante inserido para fixture {fixture_id}")
                            
                    except Exception as e:
                        logger.error(f"Erro ao inserir participantes para fixture {fixture_id}: {e}")
                        self.errors += 1
                
                self.processed_count += 1
            
            return total_inserted
            
        except Exception as e:
            logger.error(f"Erro ao processar lote de fixtures {fixture_ids_str}: {e}")
            self.errors += 1
            return 0
    
    def run_enrichment(self, max_fixtures: Optional[int] = None):
        """Executar enriquecimento completo"""
        logger.info("🚀 Iniciando enriquecimento de participantes...")
        logger.info("=" * 60)
        
        start_time = time.time()
        offset = 0
        
        while True:
            # Buscar lote de fixtures
            fixtures = self.get_fixtures_batch(offset, self.batch_size)
            
            if not fixtures:
                logger.info("✅ Todas as fixtures foram processadas!")
                break
            
            # Processar lote
            inserted = self.process_participants_batch(fixtures)
            self.total_inserted += inserted
            
            # Verificar limite máximo
            if max_fixtures and self.processed_count >= max_fixtures:
                logger.info(f"✅ Limite de {max_fixtures} fixtures atingido!")
                break
            
            # Rate limiting
            time.sleep(1)
            
            # Atualizar offset
            offset += self.batch_size
            
            # Relatório de progresso a cada 100 fixtures
            if self.processed_count % 100 == 0:
                elapsed_time = time.time() - start_time
                rate = self.processed_count / (elapsed_time / 60) if elapsed_time > 0 else 0
                eta = (max_fixtures - self.processed_count) / rate if max_fixtures and rate > 0 else 0
                
                logger.info(f"""
📊 PROGRESSO: {self.processed_count}/{max_fixtures or '∞'} ({self.processed_count/(max_fixtures or 1)*100:.1f}%)
⏱️ Tempo decorrido: {elapsed_time/60:.1f} minutos
🚀 Taxa: {rate:.1f} fixtures/minuto
⏳ ETA: {eta:.1f} minutos
👥 Participantes inseridos: +{self.total_inserted}
❌ Erros: {self.errors}
""")
        
        # Relatório final
        total_time = time.time() - start_time
        final_rate = self.processed_count / (total_time / 60) if total_time > 0 else 0
        
        logger.info(f"""
🎉 ENRIQUECIMENTO DE PARTICIPANTES CONCLUÍDO!
======================================================================
⏱️ Tempo total: {total_time/60:.1f} minutos
📊 Fixtures processadas: {self.processed_count}
👥 Participantes inseridos: {self.total_inserted}
❌ Erros encontrados: {self.errors}
🚀 Taxa média: {final_rate:.1f} fixtures/minuto
""")

def main():
    """Função principal"""
    try:
        enrichment = ParticipantsEnrichment()
        
        # Executar enriquecimento com limite de 1000 fixtures para teste
        enrichment.run_enrichment(max_fixtures=1000)
        
    except KeyboardInterrupt:
        logger.info("⏹️ Enriquecimento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()
