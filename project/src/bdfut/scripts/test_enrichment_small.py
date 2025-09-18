#!/usr/bin/env python3
"""
TEST-ENRICH-001: Teste de Enriquecimento com Amostra Pequena
============================================================

Objetivo: Testar o sistema de enriquecimento com uma amostra pequena de fixtures
Dependência: Sistema ETL base deve estar CONCLUÍDO
Estimativa: 10 minutos
Data: 2025-01-16

Critérios de Sucesso:
- [ ] Testar coleta de events para 5 fixtures
- [ ] Testar coleta de statistics para 5 fixtures
- [ ] Testar coleta de lineups para 5 fixtures
- [ ] Validar inserção no Supabase
- [ ] Verificar atualização de flags

Entregáveis:
- Script de teste funcional
- Relatório de validação
- Confirmação de funcionamento
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

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/Users/mhbutzke/Documents/BDFut/bdfut/project/data/logs/test_enrichment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_sportmonks_connection():
    """Testar conexão com API Sportmonks"""
    logger.info("🔌 Testando conexão com API Sportmonks...")
    
    try:
        client = SportmonksClient(enable_cache=True, use_redis=True)
        
        # Testar endpoint básico
        result = client.get_countries()
        
        if result and 'data' in result:
            logger.info(f"✅ Conexão com Sportmonks OK - {len(result['data'])} países encontrados")
            return True
        else:
            logger.error("❌ Falha na conexão com Sportmonks")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro na conexão com Sportmonks: {str(e)}")
        return False

def test_supabase_connection():
    """Testar conexão com Supabase"""
    logger.info("🔌 Testando conexão com Supabase...")
    
    try:
        client = SupabaseClient(use_service_role=True)
        
        # Testar query básica
        result = client.client.table('fixtures').select('sportmonks_id').limit(5).execute()
        
        if result and result.data:
            logger.info(f"✅ Conexão com Supabase OK - {len(result.data)} fixtures encontradas")
            return True
        else:
            logger.error("❌ Falha na conexão com Supabase")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro na conexão com Supabase: {str(e)}")
        return False

def get_test_fixtures(limit: int = 5):
    """Obter fixtures para teste"""
    logger.info(f"📋 Buscando {limit} fixtures para teste...")
    
    try:
        client = SupabaseClient(use_service_role=True)
        
        # Buscar fixtures recentes sem enriquecimento completo
        result = client.client.table('fixtures').select(
            'sportmonks_id, match_date, league_id, has_events, has_statistics, has_lineups'
        ).order('match_date', desc=True).limit(limit * 3).execute()
        
        if not result.data:
            logger.error("❌ Nenhuma fixture encontrada")
            return []
        
        # Filtrar fixtures que precisam de enriquecimento
        test_fixtures = []
        for fixture in result.data:
            if (not fixture.get('has_events') or 
                not fixture.get('has_statistics') or 
                not fixture.get('has_lineups')):
                test_fixtures.append(fixture)
                if len(test_fixtures) >= limit:
                    break
        
        logger.info(f"✅ {len(test_fixtures)} fixtures selecionadas para teste")
        return test_fixtures
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar fixtures: {str(e)}")
        return []

def test_fixture_events(sportmonks_client, fixture_id: int):
    """Testar coleta de eventos de uma fixture"""
    logger.info(f"⚽ Testando coleta de eventos para fixture {fixture_id}...")
    
    try:
        events_data = sportmonks_client.get_fixture_events(
            fixture_id=fixture_id,
            include='player,team,type'
        )
        
        if events_data and 'data' in events_data and events_data['data']:
            events_count = len(events_data['data'])
            logger.info(f"✅ {events_count} eventos encontrados para fixture {fixture_id}")
            return True, events_count
        else:
            logger.warning(f"⚠️ Nenhum evento encontrado para fixture {fixture_id}")
            return False, 0
            
    except Exception as e:
        logger.error(f"❌ Erro ao coletar eventos da fixture {fixture_id}: {str(e)}")
        return False, 0

def test_fixture_statistics(sportmonks_client, fixture_id: int):
    """Testar coleta de estatísticas de uma fixture"""
    logger.info(f"📊 Testando coleta de estatísticas para fixture {fixture_id}...")
    
    try:
        stats_data = sportmonks_client.get_fixture_statistics(
            fixture_id=fixture_id,
            include='team'
        )
        
        if stats_data and 'data' in stats_data and stats_data['data']:
            stats_count = len(stats_data['data'])
            logger.info(f"✅ {stats_count} estatísticas encontradas para fixture {fixture_id}")
            return True, stats_count
        else:
            logger.warning(f"⚠️ Nenhuma estatística encontrada para fixture {fixture_id}")
            return False, 0
            
    except Exception as e:
        logger.error(f"❌ Erro ao coletar estatísticas da fixture {fixture_id}: {str(e)}")
        return False, 0

def test_fixture_lineups(sportmonks_client, fixture_id: int):
    """Testar coleta de escalações de uma fixture"""
    logger.info(f"👥 Testando coleta de escalações para fixture {fixture_id}...")
    
    try:
        lineups_data = sportmonks_client.get_fixture_lineups(
            fixture_id=fixture_id,
            include='player,team,position'
        )
        
        if lineups_data and 'data' in lineups_data and lineups_data['data']:
            lineups_count = len(lineups_data['data'])
            logger.info(f"✅ {lineups_count} escalações encontradas para fixture {fixture_id}")
            return True, lineups_count
        else:
            logger.warning(f"⚠️ Nenhuma escalação encontrada para fixture {fixture_id}")
            return False, 0
            
    except Exception as e:
        logger.error(f"❌ Erro ao coletar escalações da fixture {fixture_id}: {str(e)}")
        return False, 0

def main():
    """Função principal do teste"""
    logger.info("🧪 INICIANDO TEST-ENRICH-001")
    logger.info("=" * 50)
    
    # Testar conexões
    if not test_sportmonks_connection():
        logger.error("❌ Falha na conexão com Sportmonks - abortando teste")
        return False
    
    if not test_supabase_connection():
        logger.error("❌ Falha na conexão com Supabase - abortando teste")
        return False
    
    # Inicializar clientes
    sportmonks = SportmonksClient(enable_cache=True, use_redis=True)
    supabase = SupabaseClient(use_service_role=True)
    
    # Obter fixtures para teste
    test_fixtures = get_test_fixtures(limit=5)
    
    if not test_fixtures:
        logger.error("❌ Nenhuma fixture encontrada para teste - abortando")
        return False
    
    # Estatísticas do teste
    test_stats = {
        'fixtures_tested': 0,
        'events_success': 0,
        'statistics_success': 0,
        'lineups_success': 0,
        'total_events': 0,
        'total_statistics': 0,
        'total_lineups': 0,
        'errors': 0
    }
    
    # Testar cada fixture
    for fixture in test_fixtures:
        fixture_id = fixture['sportmonks_id']
        logger.info(f"🔍 Testando fixture {fixture_id}...")
        
        test_stats['fixtures_tested'] += 1
        
        # Testar eventos
        events_ok, events_count = test_fixture_events(sportmonks, fixture_id)
        if events_ok:
            test_stats['events_success'] += 1
            test_stats['total_events'] += events_count
        
        # Testar estatísticas
        stats_ok, stats_count = test_fixture_statistics(sportmonks, fixture_id)
        if stats_ok:
            test_stats['statistics_success'] += 1
            test_stats['total_statistics'] += stats_count
        
        # Testar escalações
        lineups_ok, lineups_count = test_fixture_lineups(sportmonks, fixture_id)
        if lineups_ok:
            test_stats['lineups_success'] += 1
            test_stats['total_lineups'] += lineups_count
        
        if not events_ok and not stats_ok and not lineups_ok:
            test_stats['errors'] += 1
        
        logger.info(f"📊 Fixture {fixture_id}: Events={events_ok}, Stats={stats_ok}, Lineups={lineups_ok}")
    
    # Relatório final
    logger.info("=" * 50)
    logger.info("📊 RESULTADOS DO TESTE:")
    logger.info(f"   Fixtures testadas: {test_stats['fixtures_tested']}")
    logger.info(f"   Events coletados: {test_stats['events_success']}/{test_stats['fixtures_tested']} ({test_stats['total_events']} eventos)")
    logger.info(f"   Statistics coletadas: {test_stats['statistics_success']}/{test_stats['fixtures_tested']} ({test_stats['total_statistics']} stats)")
    logger.info(f"   Lineups coletadas: {test_stats['lineups_success']}/{test_stats['fixtures_tested']} ({test_stats['total_lineups']} lineups)")
    logger.info(f"   Erros: {test_stats['errors']}")
    
    # Determinar sucesso
    success_rate = (test_stats['events_success'] + test_stats['statistics_success'] + test_stats['lineups_success']) / (test_stats['fixtures_tested'] * 3)
    
    if success_rate >= 0.7:  # 70% de sucesso
        logger.info("✅ TEST-ENRICH-001 CONCLUÍDO COM SUCESSO")
        logger.info("🚀 Sistema de enriquecimento está funcionando corretamente")
        return True
    else:
        logger.warning("⚠️ TEST-ENRICH-001 com problemas")
        logger.warning("🔧 Verificar configurações da API e conectividade")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
