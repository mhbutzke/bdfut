#!/usr/bin/env python3
"""
PASSO 4: Popular tabelas venues e referees
Coleta dados de venues e referees das fixtures já salvas
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Any

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.sportmonks_client import SportmonksClient
from supabase import create_client
from config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Função principal para popular venues e referees"""
    
    logger.info("=" * 80)
    logger.info("🚀 PASSO 4: POPULANDO VENUES E REFEREES")
    logger.info("=" * 80)
    
    # Inicializar clientes
    try:
        config = Config()
        sportmonks = SportmonksClient()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Clientes inicializados com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar clientes: {e}")
        return
    
    # Buscar fixtures que têm venues/referees
    logger.info("🔍 Buscando fixtures com venues e referees...")
    
    try:
        # Buscar fixtures que têm venues/referees
        fixtures_response = supabase.table('fixtures').select(
            'sportmonks_id,venue,referee'
        ).not_.is_('venue', 'null').execute()
        
        fixtures = fixtures_response.data
        logger.info(f"📊 Total de fixtures com venues/referees: {len(fixtures)}")
        
        if not fixtures:
            logger.warning("⚠️ Nenhuma fixture com venues/referees encontrada")
            return
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar fixtures: {e}")
        return
    
    # Coletar venues únicos
    venues_collected = set()
    referees_collected = set()
    
    for fixture in fixtures:
        venue = fixture.get('venue')
        referee = fixture.get('referee')
        
        if venue and venue not in venues_collected:
            venues_collected.add(venue)
        
        if referee and referee not in referees_collected:
            referees_collected.add(referee)
    
    logger.info(f"📊 Venues únicos encontrados: {len(venues_collected)}")
    logger.info(f"📊 Referees únicos encontrados: {len(referees_collected)}")
    
    # Salvar venues
    if venues_collected:
        logger.info("💾 Salvando venues...")
        venues_to_save = []
        
        for venue_name in venues_collected:
            venue_data = {
                'name': venue_name,
                'created_at': datetime.utcnow().isoformat()
            }
            venues_to_save.append(venue_data)
        
        try:
            supabase.table('venues').upsert(venues_to_save, on_conflict='name').execute()
            logger.info(f"✅ {len(venues_to_save)} venues salvos")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar venues: {e}")
    
    # Salvar referees
    if referees_collected:
        logger.info("💾 Salvando referees...")
        referees_to_save = []
        
        for referee_name in referees_collected:
            referee_data = {
                'name': referee_name,
                'created_at': datetime.utcnow().isoformat()
            }
            referees_to_save.append(referee_data)
        
        try:
            supabase.table('referees').upsert(referees_to_save, on_conflict='name').execute()
            logger.info(f"✅ {len(referees_to_save)} referees salvos")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar referees: {e}")
    
    # Relatório final
    logger.info("=" * 80)
    logger.info("📊 STATUS FINAL")
    logger.info("=" * 80)
    logger.info(f"   • Venues coletados: {len(venues_collected)}")
    logger.info(f"   • Referees coletados: {len(referees_collected)}")
    
    logger.info("=" * 80)
    logger.info("✅ POPULAÇÃO DE VENUES E REFEREES CONCLUÍDA!")
    logger.info("=" * 80)
    logger.info("🎯 PRÓXIMO PASSO:")
    logger.info("   → Execute: python3 05_auditoria_final.py")
    logger.info("   Para auditoria final e relatório completo")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()
