#!/usr/bin/env python3
"""
Task 3 - Teste da API Sportmonks para Escalações
=================================================

Objetivo: Testar endpoint da API para escalações de fixtures e validar estrutura de resposta
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LineupsApiTester:
    def __init__(self):
        self.supabase = SupabaseClient()
        self.api_token = os.getenv("SPORTMONKS_API_KEY")
        self.base_url = "https://api.sportmonks.com/v3/football"
        self.includes = "lineups"
        
    def get_api_data(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Buscar dados da API Sportmonks"""
        full_url = f"{self.base_url}/{endpoint}"
        current_params = {"api_token": self.api_token}
        if params:
            current_params.update(params)
        
        try:
            response = requests.get(full_url, params=current_params, timeout=10)
            response.raise_for_status()
            return response.json().get('data')
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro ao buscar dados da API para {endpoint}: {e}")
            if e.response:
                logger.error(f"Response: {e.response.text}")
            return None
    
    def get_test_fixtures(self, limit: int = 10) -> List[Dict]:
        """Obter fixtures para teste"""
        logger.info(f"🔍 Buscando {limit} fixtures para teste...")
        
        # Buscar fixtures de diferentes anos e ligas (usando status corretos)
        response = self.supabase.client.table('fixtures').select('id, sportmonks_id, match_date, home_score, away_score, status').not_.is_('match_date', 'null').in_('status', ['FT', 'FT_PEN', 'AET']).order('match_date', desc=True).limit(limit).execute()
        fixtures = response.data
        
        logger.info(f"📋 Encontradas {len(fixtures)} fixtures para teste")
        return fixtures
    
    def test_single_fixture_lineups(self, fixture_data: Dict) -> Optional[Dict]:
        """Testar escalações de uma única fixture"""
        fixture_id = fixture_data['sportmonks_id']
        db_id = fixture_data['id']
        
        logger.info(f"\\n📡 Testando fixture {db_id} (sportmonks: {fixture_id})")
        logger.info(f"📅 Data: {fixture_data['match_date']}")
        logger.info(f"🏆 Status: {fixture_data['status']}")
        logger.info(f"⚽ Placar: {fixture_data['home_score']} x {fixture_data['away_score']}")
        
        # Buscar escalações da API
        lineups_data = self.get_api_data(f"fixtures/{fixture_id}", {"include": self.includes})
        
        if not lineups_data:
            logger.warning(f"⚠️ Nenhum dado retornado para fixture {fixture_id}")
            return None
        
        # Analisar estrutura das escalações
        lineups = lineups_data.get('lineups', [])
        logger.info(f"📊 Escalações encontradas: {len(lineups)}")
        
        if lineups:
            logger.info("\\n🎯 ANÁLISE DAS ESCALAÇÕES:")
            
            # Contar tipos de escalações
            lineup_types = {}
            teams = {}
            for lineup in lineups:
                lineup_type = lineup.get('type')
                team_id = lineup.get('team_id')
                lineup_types[lineup_type] = lineup_types.get(lineup_type, 0) + 1
                teams[team_id] = teams.get(team_id, 0) + 1
            
            logger.info("📋 Tipos de escalações encontrados:")
            for lineup_type, count in lineup_types.items():
                logger.info(f"  - {lineup_type}: {count} escalações")
            
            logger.info("\\n🏟️ Times encontrados:")
            for team_id, count in teams.items():
                logger.info(f"  - Time {team_id}: {count} escalações")
            
            # Analisar campos críticos para escalações
            critical_fields = [
                'fixture_id', 'team_id', 'player_id', 'player_name', 'type',
                'position_id', 'position_name', 'jersey_number', 'captain',
                'minutes_played', 'rating', 'formation', 'substitute',
                'substitute_in', 'substitute_out', 'substitute_minute'
            ]
            
            logger.info("\\n🔍 CAMPOS CRÍTICOS PARA ESCALAÇÕES:")
            sample_lineup = lineups[0]
            for field in critical_fields:
                value = sample_lineup.get(field)
                status = "✅" if value is not None else "❌"
                logger.info(f"  {status} {field}: {value}")
            
            # Analisar substituições
            substitutions = [l for l in lineups if l.get('substitute')]
            logger.info(f"\\n🔄 SUBSTITUIÇÕES: {len(substitutions)}")
            
            if substitutions:
                sample_sub = substitutions[0]
                sub_fields = ['substitute_in', 'substitute_out', 'substitute_minute', 'substitute_reason']
                for field in sub_fields:
                    value = sample_sub.get(field)
                    status = "✅" if value is not None else "❌"
                    logger.info(f"  {status} {field}: {value}")
            
            # Salvar resposta para análise detalhada
            filename = f"fixture_{fixture_id}_lineups_response.json"
            with open(filename, 'w') as f:
                json.dump(lineups_data, f, indent=2)
            logger.info(f"💾 Resposta salva em: {filename}")
            
            return lineups_data
        else:
            logger.info("📭 Nenhuma escalação encontrada para esta fixture")
            return None
    
    def test_multiple_fixtures(self, fixtures: List[Dict]) -> Dict:
        """Testar múltiplas fixtures"""
        logger.info(f"\\n🚀 TESTANDO {len(fixtures)} FIXTURES PARA ESCALAÇÕES")
        
        results = {
            'total_tested': len(fixtures),
            'successful': 0,
            'with_lineups': 0,
            'total_lineups': 0,
            'lineup_types': {},
            'teams_count': 0,
            'substitutions_count': 0,
            'captains_count': 0
        }
        
        for fixture_data in fixtures:
            try:
                lineups_data = self.test_single_fixture_lineups(fixture_data)
                
                if lineups_data:
                    results['successful'] += 1
                    
                    lineups = lineups_data.get('lineups', [])
                    if lineups:
                        results['with_lineups'] += 1
                        results['total_lineups'] += len(lineups)
                        
                        # Contar tipos de escalações
                        for lineup in lineups:
                            lineup_type = lineup.get('type')
                            results['lineup_types'][lineup_type] = results['lineup_types'].get(lineup_type, 0) + 1
                            
                            # Verificar substituições
                            if lineup.get('substitute'):
                                results['substitutions_count'] += 1
                            
                            # Verificar capitães
                            if lineup.get('captain'):
                                results['captains_count'] += 1
                        
                        # Contar times únicos
                        unique_teams = set(lineup.get('team_id') for lineup in lineups)
                        results['teams_count'] = len(unique_teams)
                
            except Exception as e:
                logger.error(f"❌ Erro ao testar fixture {fixture_data['id']}: {e}")
        
        return results
    
    def analyze_lineup_types(self, lineup_types: Dict) -> None:
        """Analisar tipos de escalações encontrados"""
        logger.info("\\n📊 ANÁLISE DOS TIPOS DE ESCALAÇÕES:")
        
        # Mapear tipos conhecidos
        known_types = {
            "lineup": "Escalação Titular",
            "bench": "Banco de Reservas",
            "substitution": "Substituição",
            "formation": "Formação"
        }
        
        for lineup_type, count in sorted(lineup_types.items()):
            type_name = known_types.get(lineup_type, f"Tipo {lineup_type}")
            logger.info(f"  📋 {lineup_type}: {type_name} - {count} registros")
    
    def generate_recommendations(self, results: Dict) -> None:
        """Gerar recomendações baseadas nos testes"""
        logger.info("\\n💡 RECOMENDAÇÕES BASEADAS NOS TESTES:")
        
        success_rate = (results['successful'] / results['total_tested']) * 100
        lineups_rate = (results['with_lineups'] / results['successful']) * 100 if results['successful'] > 0 else 0
        
        logger.info(f"📈 Taxa de sucesso da API: {success_rate:.1f}%")
        logger.info(f"📊 Taxa de fixtures com escalações: {lineups_rate:.1f}%")
        logger.info(f"🎯 Total de escalações coletadas: {results['total_lineups']}")
        logger.info(f"🔄 Substituições encontradas: {results['substitutions_count']}")
        logger.info(f"👑 Capitães encontrados: {results['captains_count']}")
        logger.info(f"🏟️ Times únicos: {results['teams_count']}")
        
        logger.info("\\n🔧 PRÓXIMOS PASSOS:")
        logger.info("  1. Mapear campos da API para estrutura da tabela match_lineups")
        logger.info("  2. Implementar validação de dados antes de inserir")
        logger.info("  3. Criar script de enriquecimento com rate limiting")
        logger.info("  4. Testar com fixtures de diferentes ligas e anos")
        logger.info("  5. Focar em dados de substituições e minutos jogados")
    
    def run_test(self):
        """Executar teste completo"""
        logger.info("🚀 INICIANDO TESTE DA API SPORTMONKS PARA ESCALAÇÕES")
        
        # Obter fixtures para teste
        test_fixtures = self.get_test_fixtures(10)
        
        if not test_fixtures:
            logger.error("❌ Nenhuma fixture encontrada para teste")
            return {
                'total_tested': 0,
                'successful': 0,
                'with_lineups': 0,
                'total_lineups': 0,
                'lineup_types': {},
                'teams_count': 0,
                'substitutions_count': 0,
                'captains_count': 0
            }
        
        # Testar múltiplas fixtures
        results = self.test_multiple_fixtures(test_fixtures)
        
        # Analisar tipos de escalações
        self.analyze_lineup_types(results['lineup_types'])
        
        # Gerar recomendações
        self.generate_recommendations(results)
        
        logger.info("\\n✅ TESTE CONCLUÍDO!")
        
        return results

def main():
    """Função principal"""
    tester = LineupsApiTester()
    results = tester.run_test()
    
    logger.info("\\n📋 RESUMO DO TESTE:")
    logger.info(f"  📊 Fixtures testadas: {results['total_tested']}")
    logger.info(f"  ✅ Sucessos: {results['successful']}")
    logger.info(f"  📈 Com escalações: {results['with_lineups']}")
    logger.info(f"  🎯 Total escalações: {results['total_lineups']}")

if __name__ == "__main__":
    main()
