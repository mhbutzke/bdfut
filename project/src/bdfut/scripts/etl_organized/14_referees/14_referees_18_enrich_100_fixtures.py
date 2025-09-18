#!/usr/bin/env python3
"""
Enriquecimento de 100 Fixtures com Referee ID
============================================

Objetivo: Enriquecer 100 fixtures específicas com referee_id usando API multi
Fixtures: IDs específicos encontrados na query
API: fixtures/multi/{ids}?include=referees
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

import requests
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional
from bdfut.core.supabase_client import SupabaseClient
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RefereeEnrichmentCollector:
    def __init__(self):
        Config.validate()
        self.api_key = Config.SPORTMONKS_API_KEY
        self.base_url = Config.SPORTMONKS_BASE_URL
        self.supabase = SupabaseClient()
        self.batch_size = 10  # Limite da API multi
        
    def get_fixtures_to_enrich(self) -> List[Dict]:
        """Buscar as 100 fixtures específicas para enriquecer"""
        logger.info("🔍 Buscando 100 fixtures com referee_id NULL...")
        
        # IDs específicos encontrados na query
        fixture_data = [
            {"id": 1728, "sportmonks_id": 19391123}, {"id": 1729, "sportmonks_id": 19391136}, 
            {"id": 1730, "sportmonks_id": 19391145}, {"id": 1731, "sportmonks_id": 19391164}, 
            {"id": 1732, "sportmonks_id": 19391168}, {"id": 1733, "sportmonks_id": 19391175}, 
            {"id": 1734, "sportmonks_id": 19391179}, {"id": 1735, "sportmonks_id": 19391188}, 
            {"id": 67343, "sportmonks_id": 19322050}, {"id": 52407, "sportmonks_id": 19081362}, 
            {"id": 1737, "sportmonks_id": 19391199}, {"id": 28321, "sportmonks_id": 18839829}, 
            {"id": 14212, "sportmonks_id": 19352879}, {"id": 52412, "sportmonks_id": 19112202}, 
            {"id": 1738, "sportmonks_id": 19391203}, {"id": 28324, "sportmonks_id": 18840081}, 
            {"id": 28326, "sportmonks_id": 18842172}, {"id": 1740, "sportmonks_id": 19391207}, 
            {"id": 1742, "sportmonks_id": 19391216}, {"id": 28319, "sportmonks_id": 18839825}, 
            {"id": 23924, "sportmonks_id": 18789761}, {"id": 28322, "sportmonks_id": 18839832}, 
            {"id": 1741, "sportmonks_id": 19391214}, {"id": 1743, "sportmonks_id": 19391219}, 
            {"id": 28327, "sportmonks_id": 18842173}, {"id": 1752, "sportmonks_id": 19391137}, 
            {"id": 28349, "sportmonks_id": 18840084}, {"id": 712, "sportmonks_id": 19387274}, 
            {"id": 1751, "sportmonks_id": 19391135}, {"id": 52429, "sportmonks_id": 19112203}, 
            {"id": 695, "sportmonks_id": 19387264}, {"id": 715, "sportmonks_id": 19387279}, 
            {"id": 1763, "sportmonks_id": 19391167}, {"id": 13217, "sportmonks_id": 19425979}, 
            {"id": 13227, "sportmonks_id": 19426018}, {"id": 1793, "sportmonks_id": 19391218}, 
            {"id": 13221, "sportmonks_id": 19425987}, {"id": 13213, "sportmonks_id": 19425964}, 
            {"id": 13211, "sportmonks_id": 19425958}, {"id": 13224, "sportmonks_id": 19426004}, 
            {"id": 13203, "sportmonks_id": 19425954}, {"id": 13253, "sportmonks_id": 19426021}, 
            {"id": 13249, "sportmonks_id": 19425982}, {"id": 13247, "sportmonks_id": 19425956}, 
            {"id": 13223, "sportmonks_id": 19425996}, {"id": 13250, "sportmonks_id": 19425990}, 
            {"id": 13215, "sportmonks_id": 19425974}, {"id": 13245, "sportmonks_id": 19425951}, 
            {"id": 13295, "sportmonks_id": 19426002}, {"id": 28332, "sportmonks_id": 18844282}, 
            {"id": 13310, "sportmonks_id": 19425943}, {"id": 13283, "sportmonks_id": 19425957}, 
            {"id": 13274, "sportmonks_id": 19425965}, {"id": 13285, "sportmonks_id": 19425967}, 
            {"id": 13318, "sportmonks_id": 19425971}, {"id": 13293, "sportmonks_id": 19426000}, 
            {"id": 13209, "sportmonks_id": 19425950}, {"id": 13278, "sportmonks_id": 19426008}, 
            {"id": 13324, "sportmonks_id": 19425998}, {"id": 13298, "sportmonks_id": 19426009}, 
            {"id": 13326, "sportmonks_id": 19426012}, {"id": 13312, "sportmonks_id": 19425946}, 
            {"id": 28329, "sportmonks_id": 18842767}, {"id": 13276, "sportmonks_id": 19425976}, 
            {"id": 13314, "sportmonks_id": 19425961}, {"id": 13322, "sportmonks_id": 19425995}, 
            {"id": 13297, "sportmonks_id": 19426007}, {"id": 13302, "sportmonks_id": 19426019}, 
            {"id": 13300, "sportmonks_id": 19426014}, {"id": 28330, "sportmonks_id": 18842774}, 
            {"id": 67398, "sportmonks_id": 19318133}, {"id": 67400, "sportmonks_id": 19318135}, 
            {"id": 28333, "sportmonks_id": 18844283}, {"id": 28335, "sportmonks_id": 18865212}, 
            {"id": 3103, "sportmonks_id": 18788765}, {"id": 28307, "sportmonks_id": 18865210}, 
            {"id": 28336, "sportmonks_id": 18865213}, {"id": 3291, "sportmonks_id": 19362276}, 
            {"id": 3317, "sportmonks_id": 19362320}, {"id": 3309, "sportmonks_id": 19362301}, 
            {"id": 67417, "sportmonks_id": 19265613}, {"id": 3304, "sportmonks_id": 19362265}, 
            {"id": 3307, "sportmonks_id": 19362289}, {"id": 3312, "sportmonks_id": 19362305}, 
            {"id": 3314, "sportmonks_id": 19362315}, {"id": 3290, "sportmonks_id": 19362262}, 
            {"id": 67406, "sportmonks_id": 19318203}, {"id": 3288, "sportmonks_id": 19362234}, 
            {"id": 3515, "sportmonks_id": 19362260}, {"id": 3517, "sportmonks_id": 19422348}, 
            {"id": 3492, "sportmonks_id": 19362316}, {"id": 3489, "sportmonks_id": 19362255}, 
            {"id": 3530, "sportmonks_id": 19362256}, {"id": 3535, "sportmonks_id": 19362300}, 
            {"id": 3586, "sportmonks_id": 19362270}, {"id": 3591, "sportmonks_id": 19362325}, 
            {"id": 3240, "sportmonks_id": 19362236}, {"id": 3540, "sportmonks_id": 19362312}, 
            {"id": 3537, "sportmonks_id": 19362307}, {"id": 3589, "sportmonks_id": 19362299}
        ]
        
        logger.info(f"📋 Encontradas {len(fixture_data)} fixtures para enriquecer")
        return fixture_data
    
    def fetch_referees_batch(self, fixture_ids: List[str]) -> Dict:
        """Buscar referees para um lote de fixtures via API multi"""
        fixture_ids_str = ','.join(fixture_ids)
        
        url = f'{self.base_url}/fixtures/multi/{fixture_ids_str}'
        params = {
            'api_token': self.api_key,
            'include': 'referees'
        }
        
        logger.info(f"📡 Chamando API: {url}")
        logger.info(f"📋 Parâmetros: {params}")
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            fixtures_data = data.get('data', [])
            
            logger.info(f"✅ Resposta recebida: {len(fixtures_data)} fixtures")
            return fixtures_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na API para lote {fixture_ids_str}: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return []
    
    def process_referees_batch(self, fixtures_batch: List[Dict]) -> int:
        """Processar um lote de fixtures e extrair referee_id"""
        sportmonks_ids = [str(f['sportmonks_id']) for f in fixtures_batch]
        
        # Buscar dados da API
        api_fixtures = self.fetch_referees_batch(sportmonks_ids)
        
        if not api_fixtures:
            return 0
        
        # Criar mapeamento sportmonks_id -> db_id
        id_mapping = {f['sportmonks_id']: f['id'] for f in fixtures_batch}
        
        updated_count = 0
        
        for api_fixture in api_fixtures:
            sportmonks_id = api_fixture.get('id')
            
            if sportmonks_id not in id_mapping:
                continue
                
            db_fixture_id = id_mapping[sportmonks_id]
            
            try:
                # Extrair referee principal (type_id = 6)
                referees = api_fixture.get('referees', [])
                main_referees = [r for r in referees if r.get('type_id') == 6]
                
                if main_referees:
                    main_referee = main_referees[0]
                    referee_id = main_referee.get('referee_id')
                    
                    if referee_id:
                        # Atualizar fixture com referee_id
                        self.supabase.client.table('fixtures').update({
                            'referee_id': referee_id
                        }).eq('id', db_fixture_id).execute()
                        
                        updated_count += 1
                        logger.info(f"✅ Fixture {db_fixture_id} (sportmonks: {sportmonks_id}) atualizada com referee_id: {referee_id}")
                    else:
                        logger.warning(f"⚠️ Fixture {db_fixture_id} (sportmonks: {sportmonks_id}) - referee_id vazio")
                else:
                    logger.warning(f"⚠️ Fixture {db_fixture_id} (sportmonks: {sportmonks_id}) - nenhum referee principal encontrado")
                        
            except Exception as e:
                logger.error(f"❌ Erro ao processar fixture {sportmonks_id}: {e}")
        
        return updated_count
    
    def enrich_100_fixtures(self):
        """Enriquecer as 100 fixtures específicas com referee_id"""
        logger.info("🚀 INICIANDO ENRIQUECIMENTO DE 100 FIXTURES COM REFEREE_ID!")
        
        # Obter fixtures para enriquecer
        fixtures_to_process = self.get_fixtures_to_enrich()
        
        total_fixtures = len(fixtures_to_process)
        total_batches = (total_fixtures + self.batch_size - 1) // self.batch_size
        
        logger.info(f"📊 Processando {total_fixtures} fixtures em {total_batches} lotes")
        
        total_updated = 0
        start_time = datetime.now()
        
        # Processar em lotes
        for i in range(0, total_fixtures, self.batch_size):
            batch_num = (i // self.batch_size) + 1
            batch = fixtures_to_process[i:i + self.batch_size]
            
            logger.info(f"\\n📡 Processando lote {batch_num}/{total_batches} ({len(batch)} fixtures)")
            
            try:
                updated_count = self.process_referees_batch(batch)
                total_updated += updated_count
                
                logger.info(f"✅ Lote {batch_num}: {updated_count} fixtures atualizadas")
                
            except Exception as e:
                logger.error(f"❌ Erro no lote {batch_num}: {e}")
            
            # Rate limiting - 1 segundo entre lotes
            if batch_num < total_batches:
                time.sleep(1)
        
        # Relatório final
        elapsed_time = datetime.now() - start_time
        logger.info(f"\\n🎉 ENRIQUECIMENTO CONCLUÍDO!")
        logger.info(f"📊 Fixtures processadas: {total_fixtures}")
        logger.info(f"✅ Fixtures atualizadas: {total_updated}")
        logger.info(f"⏱️ Tempo total: {elapsed_time}")
        logger.info(f"📈 Taxa de sucesso: {total_updated/total_fixtures*100:.1f}%")
        
        return total_updated > 0

def main():
    """Função principal"""
    collector = RefereeEnrichmentCollector()
    
    # Enriquecer as 100 fixtures específicas
    logger.info("\\n🚀 Iniciando enriquecimento de 100 fixtures com referee_id...")
    success = collector.enrich_100_fixtures()
    
    if success:
        logger.info("✅ Enriquecimento concluído com sucesso!")
    else:
        logger.error("💥 Falha no enriquecimento!")

if __name__ == "__main__":
    main()
