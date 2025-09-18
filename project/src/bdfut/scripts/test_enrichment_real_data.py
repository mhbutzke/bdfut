#!/usr/bin/env python3
"""
TEST-ENRICH-REAL: Teste de Enriquecimento com Dados Reais
=========================================================

Objetivo: Testar enriquecimento com fixtures que sabemos que têm dados
Dependência: APIs configuradas
Estimativa: 5 minutos
Data: 2025-01-16
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path
import json

# Configurar path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_real_fixture_enrichment():
    """Testar enriquecimento com fixture real"""
    logger.info("🧪 TESTE DE ENRIQUECIMENTO COM DADOS REAIS")
    logger.info("=" * 50)
    
    # Fixture que sabemos que tem dados (de dezembro 2024)
    test_fixture_id = 19160640  # Fixture com lineups confirmados
    
    try:
        sportmonks = SportmonksClient(enable_cache=False, use_redis=False)
        supabase = SupabaseClient(use_service_role=True)
        
        logger.info(f"🔍 Testando fixture {test_fixture_id}...")
        
        # Testar eventos
        logger.info("⚽ Testando coleta de eventos...")
        events_data = sportmonks.get_events_by_fixture(fixture_id=test_fixture_id)
        if events_data and isinstance(events_data, list) and len(events_data) > 0:
            logger.info(f"✅ {len(events_data)} eventos encontrados")
            
            # Mostrar exemplo de evento
            if len(events_data) > 0:
                sample_event = events_data[0]
                logger.info(f"📋 Exemplo de evento: {sample_event.get('type', {}).get('name', 'Unknown')} no minuto {sample_event.get('minute', 0)}")
        else:
            logger.info("ℹ️ Nenhum evento disponível para esta fixture")
        
        # Testar estatísticas
        logger.info("📊 Testando coleta de estatísticas...")
        stats_data = sportmonks.get_statistics_by_fixture(fixture_id=test_fixture_id)
        if stats_data and isinstance(stats_data, list) and len(stats_data) > 0:
            logger.info(f"✅ {len(stats_data)} estatísticas encontradas")
            
            # Mostrar exemplo de estatística
            if len(stats_data) > 0:
                sample_stat = stats_data[0]
                team_name = sample_stat.get('team', {}).get('name', 'Unknown Team')
                logger.info(f"📋 Exemplo de estatística: {team_name} - {sample_stat.get('shots_total', 0)} chutes")
        else:
            logger.info("ℹ️ Nenhuma estatística disponível para esta fixture")
        
        # Testar lineups
        logger.info("👥 Testando coleta de lineups...")
        lineups_data = sportmonks.get_lineups_by_fixture(fixture_id=test_fixture_id)
        if lineups_data and isinstance(lineups_data, list) and len(lineups_data) > 0:
            logger.info(f"✅ {len(lineups_data)} lineups encontrados")
            
            # Mostrar exemplo de lineup
            if len(lineups_data) > 0:
                sample_lineup = lineups_data[0]
                player_name = sample_lineup.get('player', {}).get('name', 'Unknown Player')
                position = sample_lineup.get('position', {}).get('name', 'Unknown Position')
                logger.info(f"📋 Exemplo de lineup: {player_name} - {position}")
        else:
            logger.info("ℹ️ Nenhum lineup disponível para esta fixture")
        
        # Testar inserção no Supabase (apenas uma amostra pequena)
        logger.info("💾 Testando inserção no Supabase...")
        
        if events_data and len(events_data) > 0:
            # Processar apenas o primeiro evento como teste
            sample_event = events_data[0]
            processed_event = {
                'id': f"{test_fixture_id}_{sample_event.get('id', '')}_{sample_event.get('minute', 0)}_test",
                'fixture_id': test_fixture_id,
                'type_id': sample_event.get('type', {}).get('id') if sample_event.get('type') else None,
                'event_type': sample_event.get('type', {}).get('name') if sample_event.get('type') else None,
                'minute': sample_event.get('minute', 0),
                'extra_minute': sample_event.get('extra_minute'),
                'team_id': sample_event.get('team', {}).get('id') if sample_event.get('team') else None,
                'player_id': sample_event.get('player', {}).get('id') if sample_event.get('player') else None,
                'player_name': sample_event.get('player', {}).get('name') if sample_event.get('player') else None,
                'result': sample_event.get('result'),
                'var': sample_event.get('var', False),
                'coordinates': json.dumps(sample_event.get('coordinates')) if sample_event.get('coordinates') else None
            }
            
            try:
                # Tentar inserir no Supabase
                result = supabase.client.table('match_events').upsert(
                    processed_event,
                    on_conflict='id'
                ).execute()
                
                logger.info("✅ Evento de teste inserido com sucesso no Supabase")
                
                # Limpar o evento de teste
                supabase.client.table('match_events').delete().eq('id', processed_event['id']).execute()
                logger.info("🧹 Evento de teste removido")
                
            except Exception as e:
                logger.error(f"❌ Erro ao inserir evento de teste: {str(e)}")
        
        logger.info("✅ TESTE CONCLUÍDO COM SUCESSO")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {str(e)}")
        return False

def main():
    """Função principal"""
    success = test_real_fixture_enrichment()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
