#!/usr/bin/env python3
"""
Teste simples do endpoint multi da API Sportmonks
Testando com 10 fixtures específicas
"""

import os
import sys
import json
from pathlib import Path
import logging

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_multi_endpoint():
    """Testar endpoint multi com 10 fixtures"""
    
    # IDs das fixtures para teste
    fixture_ids = "18863344,19154589,19154599,19154662,19154664,19154670,19431796,19431806,19362205,19431797"
    
    logger.info("🔍 TESTANDO ENDPOINT MULTI DA SPORTMONKS")
    logger.info("=" * 50)
    logger.info(f"📋 Fixtures para teste: {fixture_ids}")
    
    # Inicializar cliente
    sportmonks = SportmonksClient()
    
    try:
        # Teste 1: Sem includes
        logger.info("\n🧪 TESTE 1: Endpoint multi sem includes")
        logger.info("-" * 40)
        
        response1 = sportmonks.get_fixtures_multi(fixture_ids)
        
        if response1:
            logger.info("✅ Resposta recebida!")
            logger.info(f"📊 Estrutura da resposta: {list(response1.keys())}")
            
            if 'data' in response1:
                logger.info(f"📈 Número de fixtures retornadas: {len(response1['data'])}")
                
                # Mostrar estrutura da primeira fixture
                if response1['data']:
                    first_fixture = response1['data'][0]
                    logger.info(f"📋 Campos da primeira fixture: {list(first_fixture.keys())}")
            else:
                logger.warning("⚠️ Campo 'data' não encontrado na resposta")
        else:
            logger.error("❌ Nenhuma resposta recebida")
        
        # Teste 2: Com includes básicos
        logger.info("\n🧪 TESTE 2: Endpoint multi com includes básicos")
        logger.info("-" * 40)
        
        includes = "events,lineups,statistics"
        response2 = sportmonks.get_fixtures_multi(fixture_ids, includes)
        
        if response2:
            logger.info("✅ Resposta com includes recebida!")
            
            if 'data' in response2:
                logger.info(f"📈 Número de fixtures retornadas: {len(response2['data'])}")
                
                # Analisar dados incluídos
                for i, fixture in enumerate(response2['data'][:3]):  # Primeiras 3 fixtures
                    fixture_id = fixture.get('id')
                    logger.info(f"\n📊 Fixture {fixture_id}:")
                    
                    # Verificar eventos
                    events = fixture.get('events', [])
                    logger.info(f"   📈 Eventos: {len(events)}")
                    if events:
                        logger.info(f"      Primeiro evento: {list(events[0].keys())}")
                    
                    # Verificar lineups
                    lineups = fixture.get('lineups', [])
                    logger.info(f"   👥 Lineups: {len(lineups)}")
                    if lineups:
                        logger.info(f"      Primeiro lineup: {list(lineups[0].keys())}")
                    
                    # Verificar estatísticas
                    statistics = fixture.get('statistics', [])
                    logger.info(f"   📊 Estatísticas: {len(statistics)}")
                    if statistics:
                        logger.info(f"      Primeira estatística: {list(statistics[0].keys())}")
        else:
            logger.error("❌ Nenhuma resposta com includes recebida")
        
        # Salvar resposta completa para análise
        logger.info("\n💾 Salvando resposta completa para análise...")
        with open('multi_endpoint_test_response.json', 'w', encoding='utf-8') as f:
            json.dump(response2, f, ensure_ascii=False, indent=2)
        logger.info("✅ Resposta salva em: multi_endpoint_test_response.json")
        
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

def test_single_fixture_for_comparison():
    """Testar uma fixture individual para comparação"""
    
    logger.info("\n🧪 TESTE 3: Fixture individual para comparação")
    logger.info("-" * 40)
    
    sportmonks = SportmonksClient()
    fixture_id = 18863344  # RB Leipzig vs Bayer 04 Leverkusen
    
    try:
        # Testar fixture individual com includes
        includes = "events,lineups,statistics"
        response = sportmonks.get_fixture_with_includes(fixture_id, includes)
        
        if response:
            logger.info("✅ Resposta individual recebida!")
            
            if 'data' in response:
                fixture_data = response['data']
                logger.info(f"📊 Fixture {fixture_id}:")
                
                # Verificar eventos
                events = fixture_data.get('events', [])
                logger.info(f"   📈 Eventos: {len(events)}")
                
                # Verificar lineups
                lineups = fixture_data.get('lineups', [])
                logger.info(f"   👥 Lineups: {len(lineups)}")
                
                # Verificar estatísticas
                statistics = fixture_data.get('statistics', [])
                logger.info(f"   📊 Estatísticas: {len(statistics)}")
        else:
            logger.error("❌ Nenhuma resposta individual recebida")
            
    except Exception as e:
        logger.error(f"❌ Erro no teste individual: {e}")

def main():
    """Função principal"""
    test_multi_endpoint()
    test_single_fixture_for_comparison()
    
    logger.info("\n🎉 TESTES CONCLUÍDOS!")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
