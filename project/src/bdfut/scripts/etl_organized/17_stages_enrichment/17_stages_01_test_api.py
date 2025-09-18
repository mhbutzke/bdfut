#!/usr/bin/env python3
"""
Script para testar a API Sportmonks para stages
Verificar estrutura da resposta e mapear para nossa tabela
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

class StagesAPITest:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def test_stages_api(self):
        """Testar a API de stages"""
        logger.info("🔍 TESTANDO API SPORTMONKS - STAGES")
        logger.info("=" * 50)
        
        try:
            # Testar endpoint básico de stages
            logger.info("📡 Testando endpoint: /stages")
            response = self.sportmonks._make_request('/stages', {}, 'stages')
            
            if response and response.get('data'):
                stages = response['data']
                logger.info(f"✅ Resposta recebida: {len(stages)} stages")
                
                # Analisar estrutura do primeiro stage
                if stages:
                    first_stage = stages[0]
                    logger.info("📊 Estrutura do primeiro stage:")
                    for key, value in first_stage.items():
                        logger.info(f"   {key}: {value}")
                    
                    # Verificar se tem includes
                    if 'includes' in response:
                        logger.info("📋 Includes disponíveis:")
                        for include_key, include_data in response['includes'].items():
                            logger.info(f"   {include_key}: {len(include_data) if isinstance(include_data, list) else 'object'}")
                
                return stages
            else:
                logger.warning("⚠️ Nenhum dado recebido da API")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar API: {e}")
            return []
    
    def test_stages_with_includes(self):
        """Testar stages com includes"""
        logger.info("🔍 TESTANDO STAGES COM INCLUDES")
        logger.info("=" * 50)
        
        try:
            # Testar com includes específicos
            includes = "league,season,sport"
            logger.info(f"📡 Testando com includes: {includes}")
            
            response = self.sportmonks._make_request('/stages', {'include': includes}, 'stages')
            
            if response and response.get('data'):
                stages = response['data']
                logger.info(f"✅ Resposta recebida: {len(stages)} stages com includes")
                
                # Analisar includes
                if 'includes' in response:
                    logger.info("📋 Includes recebidos:")
                    for include_key, include_data in response['includes'].items():
                        logger.info(f"   {include_key}: {len(include_data) if isinstance(include_data, list) else 'object'}")
                        
                        # Mostrar exemplo do include
                        if isinstance(include_data, list) and include_data:
                            logger.info(f"      Exemplo {include_key}:")
                            for key, value in include_data[0].items():
                                logger.info(f"        {key}: {value}")
                
                return stages
            else:
                logger.warning("⚠️ Nenhum dado recebido com includes")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar API com includes: {e}")
            return []
    
    def compare_with_database(self, api_stages):
        """Comparar dados da API com o banco"""
        logger.info("🔍 COMPARANDO COM BANCO DE DADOS")
        logger.info("=" * 50)
        
        try:
            # Buscar alguns stages do banco
            response = self.supabase.client.table('stages').select('*').limit(5).execute()
            
            if response.data:
                logger.info(f"📊 Stages no banco: {len(response.data)}")
                
                # Comparar estrutura
                db_stage = response.data[0]
                api_stage = api_stages[0] if api_stages else {}
                
                logger.info("📋 Comparação de campos:")
                
                # Campos da API
                api_fields = set(api_stage.keys())
                db_fields = set(db_stage.keys())
                
                logger.info("   Campos da API:")
                for field in sorted(api_fields):
                    logger.info(f"     {field}: {api_stage.get(field)}")
                
                logger.info("   Campos do banco:")
                for field in sorted(db_fields):
                    logger.info(f"     {field}: {db_stage.get(field)}")
                
                # Campos em comum
                common_fields = api_fields.intersection(db_fields)
                logger.info(f"   Campos em comum: {len(common_fields)}")
                
                # Campos apenas na API
                api_only = api_fields - db_fields
                if api_only:
                    logger.info(f"   Campos apenas na API: {api_only}")
                
                # Campos apenas no banco
                db_only = db_fields - api_fields
                if db_only:
                    logger.info(f"   Campos apenas no banco: {db_only}")
                
            else:
                logger.warning("⚠️ Nenhum stage encontrado no banco")
                
        except Exception as e:
            logger.error(f"❌ Erro ao comparar com banco: {e}")
    
    def run_test(self):
        """Executar todos os testes"""
        logger.info("🚀 INICIANDO TESTES DA API STAGES")
        logger.info("=" * 60)
        
        # Teste 1: API básica
        api_stages = self.test_stages_api()
        
        # Teste 2: API com includes
        api_stages_with_includes = self.test_stages_with_includes()
        
        # Teste 3: Comparação com banco
        if api_stages:
            self.compare_with_database(api_stages)
        
        logger.info("🎉 TESTES CONCLUÍDOS!")

def main():
    """Função principal"""
    test = StagesAPITest()
    test.run_test()

if __name__ == "__main__":
    main()
