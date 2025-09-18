#!/usr/bin/env python3
"""
TEST-SIMPLE-ENRICH: Teste Simples de Enriquecimento
===================================================

Objetivo: Teste básico de conectividade e funcionalidade de enriquecimento
Dependência: APIs configuradas
Estimativa: 5 minutos
Data: 2025-01-16
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient

# Configurar logging simples
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_connections():
    """Testar conexões básicas sem cache"""
    logger.info("🔌 Testando conexões básicas...")
    
    # Testar Sportmonks sem cache
    try:
        client = SportmonksClient(enable_cache=False, use_redis=False)
        result = client.get_countries()
        
        if result and isinstance(result, list) and len(result) > 0:
            logger.info(f"✅ Sportmonks OK - {len(result)} países encontrados")
            return True
        else:
            logger.error("❌ Sportmonks retornou dados inválidos")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no Sportmonks: {str(e)}")
        return False

def test_supabase_basic():
    """Testar Supabase básico"""
    logger.info("🔌 Testando Supabase...")
    
    try:
        client = SupabaseClient(use_service_role=True)
        
        # Testar query simples
        result = client.client.table('fixtures').select('sportmonks_id').limit(3).execute()
        
        if result and result.data and len(result.data) > 0:
            logger.info(f"✅ Supabase OK - {len(result.data)} fixtures encontradas")
            return True
        else:
            logger.error("❌ Supabase retornou dados inválidos")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no Supabase: {str(e)}")
        return False

def test_fixture_data_sample():
    """Testar amostra de dados de fixtures"""
    logger.info("📋 Testando amostra de fixtures...")
    
    try:
        supabase = SupabaseClient(use_service_role=True)
        sportmonks = SportmonksClient(enable_cache=False, use_redis=False)
        
        # Buscar uma fixture recente
        result = supabase.client.table('fixtures').select(
            'sportmonks_id, match_date, league_id'
        ).order('match_date', desc=True).limit(1).execute()
        
        if not result.data:
            logger.error("❌ Nenhuma fixture encontrada")
            return False
        
        fixture = result.data[0]
        fixture_id = fixture['sportmonks_id']
        
        logger.info(f"🔍 Testando fixture {fixture_id}...")
        
        # Testar coleta de eventos (sem inserir)
        try:
            events_data = sportmonks.get_events_by_fixture(fixture_id=fixture_id)
            if events_data and isinstance(events_data, list):
                events_count = len(events_data)
                logger.info(f"⚽ {events_count} eventos disponíveis para fixture {fixture_id}")
            else:
                logger.info(f"⚽ Nenhum evento disponível para fixture {fixture_id}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao buscar eventos: {str(e)}")
        
        # Testar coleta de estatísticas (sem inserir)
        try:
            stats_data = sportmonks.get_statistics_by_fixture(fixture_id=fixture_id)
            if stats_data and isinstance(stats_data, list):
                stats_count = len(stats_data)
                logger.info(f"📊 {stats_count} estatísticas disponíveis para fixture {fixture_id}")
            else:
                logger.info(f"📊 Nenhuma estatística disponível para fixture {fixture_id}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao buscar estatísticas: {str(e)}")
        
        # Testar coleta de lineups (sem inserir)
        try:
            lineups_data = sportmonks.get_lineups_by_fixture(fixture_id=fixture_id)
            if lineups_data and isinstance(lineups_data, list):
                lineups_count = len(lineups_data)
                logger.info(f"👥 {lineups_count} lineups disponíveis para fixture {fixture_id}")
            else:
                logger.info(f"👥 Nenhum lineup disponível para fixture {fixture_id}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao buscar lineups: {str(e)}")
        
        logger.info("✅ Teste de amostra concluído")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de amostra: {str(e)}")
        return False

def main():
    """Função principal"""
    logger.info("🧪 INICIANDO TEST-SIMPLE-ENRICH")
    logger.info("=" * 40)
    
    # Testar conexões básicas
    sportmonks_ok = test_basic_connections()
    supabase_ok = test_supabase_basic()
    
    if not sportmonks_ok or not supabase_ok:
        logger.error("❌ Falha nas conexões básicas - abortando")
        return False
    
    # Testar dados de amostra
    sample_ok = test_fixture_data_sample()
    
    if sample_ok:
        logger.info("✅ TEST-SIMPLE-ENRICH CONCLUÍDO COM SUCESSO")
        logger.info("🚀 Sistema básico está funcionando")
        return True
    else:
        logger.warning("⚠️ TEST-SIMPLE-ENRICH com problemas")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
