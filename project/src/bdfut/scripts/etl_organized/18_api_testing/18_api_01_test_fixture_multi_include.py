#!/usr/bin/env python3
"""
Script para testar a API Sportmonks com múltiplos includes
Testar endpoint específico fornecido pelo usuário
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import time
import logging

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultiIncludeAPITest:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def test_fixture_multi_include(self, fixture_id: int = 11865351):
        """Testar fixture específica com múltiplos includes"""
        logger.info("🔍 TESTANDO FIXTURE COM MÚLTIPLOS INCLUDES")
        logger.info("=" * 60)
        
        try:
            # Definir includes conforme solicitado pelo usuário
            includes = "scores;sport;round;stage;group;aggregate;league;season;referees;coaches;tvStations;venue;state;weatherReport;lineups;events;timeline;comments;trends;statistics;participants;periods;odds"
            
            logger.info(f"📡 Testando fixture {fixture_id}")
            logger.info(f"📋 Includes: {includes}")
            
            # Fazer a requisição
            endpoint = f'/fixtures/{fixture_id}'
            params = {'include': includes}
            
            response = self.sportmonks._make_request(endpoint, params, 'fixtures')
            
            if response and response.get('data'):
                fixture_data = response['data']
                logger.info("✅ Resposta recebida com sucesso!")
                
                # Analisar estrutura principal
                logger.info("📊 ESTRUTURA PRINCIPAL DA FIXTURE:")
                for key, value in fixture_data.items():
                    if isinstance(value, (dict, list)):
                        logger.info(f"   {key}: {type(value).__name__} com {len(value) if isinstance(value, (list, dict)) else 'N/A'} itens")
                    else:
                        logger.info(f"   {key}: {value}")
                
                # Analisar includes recebidos
                if 'includes' in response:
                    logger.info("\\n📋 INCLUDES RECEBIDOS:")
                    for include_key, include_data in response['includes'].items():
                        if isinstance(include_data, list):
                            logger.info(f"   {include_key}: {len(include_data)} itens")
                            if include_data:
                                logger.info(f"      Exemplo: {list(include_data[0].keys()) if isinstance(include_data[0], dict) else include_data[0]}")
                        elif isinstance(include_data, dict):
                            logger.info(f"   {include_key}: objeto com {len(include_data)} campos")
                            logger.info(f"      Campos: {list(include_data.keys())}")
                        else:
                            logger.info(f"   {include_key}: {include_data}")
                
                # Salvar resposta completa em arquivo para análise
                output_file = f"fixture_{fixture_id}_multi_include_response.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(response, f, indent=2, ensure_ascii=False, default=str)
                
                logger.info(f"💾 Resposta completa salva em: {output_file}")
                
                return response
            else:
                logger.warning("⚠️ Nenhum dado recebido da API")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar API: {e}")
            return None
    
    def analyze_response_structure(self, response):
        """Analisar estrutura detalhada da resposta"""
        if not response:
            return
            
        logger.info("\\n🔍 ANÁLISE DETALHADA DA RESPOSTA")
        logger.info("=" * 60)
        
        try:
            # Analisar dados principais
            if 'data' in response:
                data = response['data']
                logger.info("📊 DADOS PRINCIPAIS:")
                for key, value in data.items():
                    if key in ['lineups', 'events', 'statistics', 'participants']:
                        if isinstance(value, list):
                            logger.info(f"   {key}: {len(value)} itens")
                            if value:
                                logger.info(f"      Primeiro item: {list(value[0].keys()) if isinstance(value[0], dict) else value[0]}")
                        else:
                            logger.info(f"   {key}: {value}")
            
            # Analisar includes específicos importantes
            if 'includes' in response:
                important_includes = ['lineups', 'events', 'statistics', 'participants', 'referees', 'coaches']
                
                logger.info("\\n🎯 INCLUDES IMPORTANTES PARA ENRIQUECIMENTO:")
                for include_key in important_includes:
                    if include_key in response['includes']:
                        include_data = response['includes'][include_key]
                        if isinstance(include_data, list):
                            logger.info(f"   {include_key}: {len(include_data)} itens")
                            if include_data:
                                sample = include_data[0]
                                logger.info(f"      Campos disponíveis: {list(sample.keys()) if isinstance(sample, dict) else 'N/A'}")
                        else:
                            logger.info(f"   {include_key}: {include_data}")
                    else:
                        logger.info(f"   {include_key}: ❌ Não encontrado")
                        
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
    
    def run_test(self):
        """Executar teste completo"""
        logger.info("🚀 INICIANDO TESTE DE FIXTURE COM MÚLTIPLOS INCLUDES")
        logger.info("=" * 70)
        
        # Teste principal
        response = self.test_fixture_multi_include(11865351)
        
        # Análise detalhada
        if response:
            self.analyze_response_structure(response)
        
        logger.info("🎉 TESTE CONCLUÍDO!")

def main():
    """Função principal"""
    test = MultiIncludeAPITest()
    test.run_test()

if __name__ == "__main__":
    main()
