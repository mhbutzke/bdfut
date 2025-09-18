#!/usr/bin/env python3
"""
Task 4 - Teste da API Sportmonks para Estatísticas
==================================================

Objetivo: Testar endpoint da API para estatísticas de fixtures e validar estrutura de resposta
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

class StatisticsApiTester:
    def __init__(self):
        self.supabase = SupabaseClient()
        self.api_token = os.getenv("SPORTMONKS_API_KEY")
        self.base_url = "https://api.sportmonks.com/v3/football"
        self.includes = "statistics"
        
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
    
    def test_single_fixture_statistics(self, fixture_data: Dict) -> Optional[Dict]:
        """Testar estatísticas de uma única fixture"""
        fixture_id = fixture_data['sportmonks_id']
        db_id = fixture_data['id']
        
        logger.info(f"\\n📡 Testando fixture {db_id} (sportmonks: {fixture_id})")
        logger.info(f"📅 Data: {fixture_data['match_date']}")
        logger.info(f"🏆 Status: {fixture_data['status']}")
        logger.info(f"⚽ Placar: {fixture_data['home_score']} x {fixture_data['away_score']}")
        
        # Buscar estatísticas da API
        statistics_data = self.get_api_data(f"fixtures/{fixture_id}", {"include": self.includes})
        
        if not statistics_data:
            logger.warning(f"⚠️ Nenhum dado retornado para fixture {fixture_id}")
            return None
        
        # Analisar estrutura das estatísticas
        statistics = statistics_data.get('statistics', [])
        logger.info(f"📊 Estatísticas encontradas: {len(statistics)}")
        
        if statistics:
            logger.info("\\n🎯 ANÁLISE DAS ESTATÍSTICAS:")
            
            # Contar times
            teams = {}
            for stat in statistics:
                team_id = stat.get('team_id')
                teams[team_id] = teams.get(team_id, 0) + 1
            
            logger.info("\\n🏟️ Times encontrados:")
            for team_id, count in teams.items():
                logger.info(f"  - Time {team_id}: {count} estatísticas")
            
            # Analisar campos críticos para estatísticas de cartões
            critical_fields = [
                'fixture_id', 'team_id', 'yellow_cards', 'red_cards', 'fouls',
                'shots_total', 'shots_on_target', 'corners', 'offsides',
                'ball_possession', 'passes_total', 'passes_accurate', 'pass_percentage',
                'goals', 'goals_conceded', 'saves', 'tackles', 'interceptions'
            ]
            
            logger.info("\\n🔍 CAMPOS CRÍTICOS PARA ESTATÍSTICAS DE CARTÕES:")
            sample_stat = statistics[0]
            for field in critical_fields:
                value = sample_stat.get(field)
                status = "✅" if value is not None else "❌"
                logger.info(f"  {status} {field}: {value}")
            
            # Analisar estatísticas específicas de cartões
            logger.info("\\n🟨 ESTATÍSTICAS DE CARTÕES:")
            total_yellow_cards = sum(stat.get('yellow_cards', 0) for stat in statistics)
            total_red_cards = sum(stat.get('red_cards', 0) for stat in statistics)
            total_fouls = sum(stat.get('fouls', 0) for stat in statistics)
            
            logger.info(f"  🟨 Cartões amarelos: {total_yellow_cards}")
            logger.info(f"  🔴 Cartões vermelhos: {total_red_cards}")
            logger.info(f"  ⚠️ Faltas: {total_fouls}")
            
            # Salvar resposta para análise detalhada
            filename = f"fixture_{fixture_id}_statistics_response.json"
            with open(filename, 'w') as f:
                json.dump(statistics_data, f, indent=2)
            logger.info(f"💾 Resposta salva em: {filename}")
            
            return statistics_data
        else:
            logger.info("📭 Nenhuma estatística encontrada para esta fixture")
            return None
    
    def test_multiple_fixtures(self, fixtures: List[Dict]) -> Dict:
        """Testar múltiplas fixtures"""
        logger.info(f"\\n🚀 TESTANDO {len(fixtures)} FIXTURES PARA ESTATÍSTICAS")
        
        results = {
            'total_tested': len(fixtures),
            'successful': 0,
            'with_statistics': 0,
            'total_statistics': 0,
            'teams_count': 0,
            'total_yellow_cards': 0,
            'total_red_cards': 0,
            'total_fouls': 0,
            'fixtures_with_cards': 0
        }
        
        for fixture_data in fixtures:
            try:
                statistics_data = self.test_single_fixture_statistics(fixture_data)
                
                if statistics_data:
                    results['successful'] += 1
                    
                    statistics = statistics_data.get('statistics', [])
                    if statistics:
                        results['with_statistics'] += 1
                        results['total_statistics'] += len(statistics)
                        
                        # Contar times únicos
                        unique_teams = set(stat.get('team_id') for stat in statistics)
                        results['teams_count'] = len(unique_teams)
                        
                        # Somar estatísticas de cartões
                        fixture_yellow_cards = sum(stat.get('yellow_cards', 0) for stat in statistics)
                        fixture_red_cards = sum(stat.get('red_cards', 0) for stat in statistics)
                        fixture_fouls = sum(stat.get('fouls', 0) for stat in statistics)
                        
                        results['total_yellow_cards'] += fixture_yellow_cards
                        results['total_red_cards'] += fixture_red_cards
                        results['total_fouls'] += fixture_fouls
                        
                        # Verificar se tem cartões
                        if fixture_yellow_cards > 0 or fixture_red_cards > 0:
                            results['fixtures_with_cards'] += 1
                
            except Exception as e:
                logger.error(f"❌ Erro ao testar fixture {fixture_data['id']}: {e}")
        
        return results
    
    def generate_recommendations(self, results: Dict) -> None:
        """Gerar recomendações baseadas nos testes"""
        logger.info("\\n💡 RECOMENDAÇÕES BASEADAS NOS TESTES:")
        
        success_rate = (results['successful'] / results['total_tested']) * 100
        statistics_rate = (results['with_statistics'] / results['successful']) * 100 if results['successful'] > 0 else 0
        
        logger.info(f"📈 Taxa de sucesso da API: {success_rate:.1f}%")
        logger.info(f"📊 Taxa de fixtures com estatísticas: {statistics_rate:.1f}%")
        logger.info(f"🎯 Total de estatísticas coletadas: {results['total_statistics']}")
        logger.info(f"🟨 Cartões amarelos totais: {results['total_yellow_cards']}")
        logger.info(f"🔴 Cartões vermelhos totais: {results['total_red_cards']}")
        logger.info(f"⚠️ Faltas totais: {results['total_fouls']}")
        logger.info(f"🏟️ Times únicos: {results['teams_count']}")
        logger.info(f"📊 Fixtures com cartões: {results['fixtures_with_cards']}")
        
        logger.info("\\n🔧 PRÓXIMOS PASSOS:")
        logger.info("  1. Mapear campos da API para estrutura da tabela match_statistics")
        logger.info("  2. Implementar validação de dados antes de inserir")
        logger.info("  3. Criar script de enriquecimento com rate limiting")
        logger.info("  4. Testar com fixtures de diferentes ligas e anos")
        logger.info("  5. Focar em dados de cartões, faltas e posse de bola")
    
    def run_test(self):
        """Executar teste completo"""
        logger.info("🚀 INICIANDO TESTE DA API SPORTMONKS PARA ESTATÍSTICAS")
        
        # Obter fixtures para teste
        test_fixtures = self.get_test_fixtures(10)
        
        if not test_fixtures:
            logger.error("❌ Nenhuma fixture encontrada para teste")
            return {
                'total_tested': 0,
                'successful': 0,
                'with_statistics': 0,
                'total_statistics': 0,
                'teams_count': 0,
                'total_yellow_cards': 0,
                'total_red_cards': 0,
                'total_fouls': 0,
                'fixtures_with_cards': 0
            }
        
        # Testar múltiplas fixtures
        results = self.test_multiple_fixtures(test_fixtures)
        
        # Gerar recomendações
        self.generate_recommendations(results)
        
        logger.info("\\n✅ TESTE CONCLUÍDO!")
        
        return results

def main():
    """Função principal"""
    tester = StatisticsApiTester()
    results = tester.run_test()
    
    logger.info("\\n📋 RESUMO DO TESTE:")
    logger.info(f"  📊 Fixtures testadas: {results['total_tested']}")
    logger.info(f"  ✅ Sucessos: {results['successful']}")
    logger.info(f"  📈 Com estatísticas: {results['with_statistics']}")
    logger.info(f"  🎯 Total estatísticas: {results['total_statistics']}")

if __name__ == "__main__":
    main()
