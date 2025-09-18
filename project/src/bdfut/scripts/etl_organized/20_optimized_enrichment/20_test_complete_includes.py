#!/usr/bin/env python3
"""
Teste com todos os includes solicitados
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

def test_complete_includes():
    """Testar com todos os includes solicitados"""
    
    # IDs específicos solicitados
    fixture_ids = "16475287,11865351"
    
    logger.info("🔍 TESTANDO TODOS OS INCLUDES SOLICITADOS")
    logger.info("=" * 60)
    logger.info(f"📋 Fixtures: {fixture_ids}")
    
    # Inicializar cliente
    sportmonks = SportmonksClient()
    
    # Todos os includes solicitados
    includes = "statistics;events;lineups;referees;participants;periods"
    
    try:
        logger.info(f"🧪 Testando includes: {includes}")
        logger.info("-" * 40)
        
        response = sportmonks.get_fixtures_multi(fixture_ids, includes)
        
        if response:
            logger.info("✅ Resposta recebida com sucesso!")
            
            if 'data' in response and response['data']:
                logger.info(f"📈 Número de fixtures retornadas: {len(response['data'])}")
                
                # Analisar cada fixture
                for i, fixture in enumerate(response['data']):
                    fixture_id = fixture.get('id')
                    logger.info(f"\n📊 FIXTURE {fixture_id}:")
                    logger.info("-" * 30)
                    
                    # Analisar cada include
                    for include in includes.split(';'):
                        include_data = fixture.get(include)
                        if include_data:
                            if isinstance(include_data, list):
                                logger.info(f"   {include}: {len(include_data)} itens")
                                if include_data:
                                    logger.info(f"      Primeiro item: {list(include_data[0].keys())}")
                                    # Mostrar alguns campos importantes
                                    first_item = include_data[0]
                                    for key, value in first_item.items():
                                        if key in ['id', 'name', 'type_id', 'participant_id', 'team_id', 'player_id']:
                                            logger.info(f"         {key}: {value}")
                            elif isinstance(include_data, dict):
                                logger.info(f"   {include}: objeto com {len(include_data)} campos")
                                logger.info(f"      Campos: {list(include_data.keys())}")
                                # Mostrar alguns valores importantes
                                for key, value in include_data.items():
                                    if key in ['id', 'name', 'type_id', 'participant_id', 'team_id']:
                                        logger.info(f"         {key}: {value}")
                            else:
                                logger.info(f"   {include}: {include_data}")
                        else:
                            logger.info(f"   {include}: não encontrado")
                
                # Salvar resposta completa para análise
                logger.info(f"\n💾 Salvando resposta completa...")
                with open('complete_includes_response.json', 'w', encoding='utf-8') as f:
                    json.dump(response, f, ensure_ascii=False, indent=2)
                logger.info("✅ Resposta salva em: complete_includes_response.json")
                
            else:
                logger.warning("⚠️ Campo 'data' não encontrado na resposta")
        else:
            logger.error("❌ Nenhuma resposta recebida")
            
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

def analyze_data_structure():
    """Analisar estrutura dos dados para criar tabelas"""
    
    logger.info(f"\n🔍 ANALISANDO ESTRUTURA PARA CRIAÇÃO DE TABELAS")
    logger.info("=" * 60)
    
    try:
        # Carregar resposta salva
        with open('complete_includes_response.json', 'r', encoding='utf-8') as f:
            response = json.load(f)
        
        if 'data' in response and response['data']:
            fixture = response['data'][0]  # Primeira fixture
            
            logger.info("📋 ESTRUTURA DOS DADOS:")
            
            # Analisar cada include
            for include in ['statistics', 'events', 'lineups', 'referees', 'participants', 'periods']:
                include_data = fixture.get(include)
                if include_data:
                    logger.info(f"\n🔍 {include.upper()}:")
                    
                    if isinstance(include_data, list) and include_data:
                        first_item = include_data[0]
                        logger.info(f"   Campos disponíveis: {list(first_item.keys())}")
                        
                        # Identificar campos importantes
                        important_fields = []
                        for key, value in first_item.items():
                            if value is not None and value != "":
                                important_fields.append(f"{key} ({type(value).__name__})")
                        
                        logger.info(f"   Campos com dados: {important_fields}")
                        
                    elif isinstance(include_data, dict):
                        logger.info(f"   Campos: {list(include_data.keys())}")
                        important_fields = []
                        for key, value in include_data.items():
                            if value is not None and value != "":
                                important_fields.append(f"{key} ({type(value).__name__})")
                        logger.info(f"   Campos com dados: {important_fields}")
        
    except Exception as e:
        logger.error(f"❌ Erro na análise: {e}")

def main():
    """Função principal"""
    test_complete_includes()
    analyze_data_structure()
    
    logger.info("\n🎉 ANÁLISE CONCLUÍDA!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
