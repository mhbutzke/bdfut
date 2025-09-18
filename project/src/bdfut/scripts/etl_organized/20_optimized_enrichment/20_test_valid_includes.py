#!/usr/bin/env python3
"""
Teste com includes válidos para o endpoint multi
Baseado na documentação da Sportmonks
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

def test_valid_includes():
    """Testar includes válidos conforme documentação"""
    
    # IDs das fixtures para teste
    fixture_ids = "18863344,19154589,19154599"
    
    logger.info("🔍 TESTANDO INCLUDES VÁLIDOS PARA ENDPOINT MULTI")
    logger.info("=" * 60)
    logger.info(f"📋 Fixtures para teste: {fixture_ids}")
    
    # Inicializar cliente
    sportmonks = SportmonksClient()
    
    # Includes válidos conforme documentação
    valid_includes = [
        "participants",  # Informações dos times
        "league",        # Informações da liga
        "season",        # Informações da temporada
        "venue",         # Informações do estádio
        "state",         # Estado da partida
        "round",         # Rodada
        "stage",         # Fase
        "referees",      # Árbitros
        "coaches",       # Técnicos
        "lineups",       # Escalações
        "events",        # Eventos da partida
        "statistics",    # Estatísticas
        "odds",          # Odds
        "scores"         # Placar
    ]
    
    for include in valid_includes:
        try:
            logger.info(f"\n🧪 TESTANDO INCLUDE: {include}")
            logger.info("-" * 40)
            
            response = sportmonks.get_fixtures_multi(fixture_ids, include)
            
            if response:
                logger.info(f"✅ Include '{include}' funcionou!")
                
                if 'data' in response and response['data']:
                    fixture = response['data'][0]
                    include_data = fixture.get(include, [])
                    
                    if isinstance(include_data, list):
                        logger.info(f"   📊 {include}: {len(include_data)} itens")
                        if include_data:
                            logger.info(f"      Primeiro item: {list(include_data[0].keys())}")
                    elif isinstance(include_data, dict):
                        logger.info(f"   📊 {include}: objeto com {len(include_data)} campos")
                        logger.info(f"      Campos: {list(include_data.keys())}")
                    else:
                        logger.info(f"   📊 {include}: {include_data}")
                else:
                    logger.warning(f"   ⚠️ Include '{include}' retornou dados vazios")
            else:
                logger.error(f"❌ Include '{include}' falhou")
                
        except Exception as e:
            logger.error(f"❌ Erro com include '{include}': {e}")
    
    # Teste com múltiplos includes válidos
    logger.info(f"\n🧪 TESTANDO MÚLTIPLOS INCLUDES VÁLIDOS")
    logger.info("-" * 40)
    
    try:
        multiple_includes = "participants;league;season;venue;state"
        response = sportmonks.get_fixtures_multi(fixture_ids, multiple_includes)
        
        if response:
            logger.info("✅ Múltiplos includes funcionaram!")
            
            if 'data' in response and response['data']:
                fixture = response['data'][0]
                logger.info(f"📊 Fixture {fixture.get('id')}:")
                
                for include in multiple_includes.split(';'):
                    include_data = fixture.get(include)
                    if include_data:
                        if isinstance(include_data, list):
                            logger.info(f"   {include}: {len(include_data)} itens")
                        elif isinstance(include_data, dict):
                            logger.info(f"   {include}: objeto com {len(include_data)} campos")
                        else:
                            logger.info(f"   {include}: {include_data}")
                    else:
                        logger.info(f"   {include}: não encontrado")
        else:
            logger.error("❌ Múltiplos includes falharam")
            
    except Exception as e:
        logger.error(f"❌ Erro com múltiplos includes: {e}")

def test_individual_fixture_includes():
    """Testar includes em fixture individual para comparação"""
    
    logger.info(f"\n🧪 TESTANDO INCLUDES EM FIXTURE INDIVIDUAL")
    logger.info("-" * 40)
    
    sportmonks = SportmonksClient()
    fixture_id = 18863344
    
    try:
        # Testar includes que funcionaram no multi
        includes = "participants;league;season;venue;state;lineups;events;statistics"
        response = sportmonks.get_fixture_with_includes(fixture_id, includes)
        
        if response:
            logger.info("✅ Includes individuais funcionaram!")
            
            if 'data' in response:
                fixture_data = response['data']
                logger.info(f"📊 Fixture {fixture_id}:")
                
                for include in includes.split(';'):
                    include_data = fixture_data.get(include)
                    if include_data:
                        if isinstance(include_data, list):
                            logger.info(f"   {include}: {len(include_data)} itens")
                        elif isinstance(include_data, dict):
                            logger.info(f"   {include}: objeto com {len(include_data)} campos")
                        else:
                            logger.info(f"   {include}: {include_data}")
                    else:
                        logger.info(f"   {include}: não encontrado")
        else:
            logger.error("❌ Includes individuais falharam")
            
    except Exception as e:
        logger.error(f"❌ Erro com includes individuais: {e}")

def main():
    """Função principal"""
    test_valid_includes()
    test_individual_fixture_includes()
    
    logger.info("\n🎉 TESTES DE INCLUDES CONCLUÍDOS!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
