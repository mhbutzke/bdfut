#!/usr/bin/env python3
"""
Task 2 - Teste da API Sportmonks para Eventos
=============================================

Objetivo: Testar endpoint da API para eventos de fixtures e validar estrutura de resposta
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
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EventsApiTester:
    def __init__(self):
        self.supabase = SupabaseClient()
        self.api_token = os.getenv("SPORTMONKS_API_KEY")
        self.base_url = "https://api.sportmonks.com/v3/football"
        self.includes = "events"
        
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
    
    def test_single_fixture_events(self, fixture_data: Dict) -> Optional[Dict]:
        """Testar eventos de uma única fixture"""
        fixture_id = fixture_data['sportmonks_id']
        db_id = fixture_data['id']
        
        logger.info(f"\\n📡 Testando fixture {db_id} (sportmonks: {fixture_id})")
        logger.info(f"📅 Data: {fixture_data['match_date']}")
        logger.info(f"🏆 Status: {fixture_data['status']}")
        logger.info(f"⚽ Placar: {fixture_data['home_score']} x {fixture_data['away_score']}")
        
        # Buscar eventos da API
        events_data = self.get_api_data(f"fixtures/{fixture_id}", {"include": self.includes})
        
        if not events_data:
            logger.warning(f"⚠️ Nenhum dado retornado para fixture {fixture_id}")
            return None
        
        # Analisar estrutura dos eventos
        events = events_data.get('events', [])
        logger.info(f"📊 Eventos encontrados: {len(events)}")
        
        if events:
            logger.info("\\n🎯 ANÁLISE DOS EVENTOS:")
            
            # Contar tipos de eventos
            event_types = {}
            for event in events:
                event_type = event.get('type_id')
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            logger.info("📋 Tipos de eventos encontrados:")
            for event_type, count in event_types.items():
                logger.info(f"  - Tipo {event_type}: {count} eventos")
            
            # Analisar campos críticos para cartões
            critical_fields = [
                'type_id', 'event_type', 'minute', 'extra_minute',
                'team_id', 'player_id', 'related_player_id', 'player_name',
                'period_id', 'result', 'var', 'var_reason', 'coordinates'
            ]
            
            logger.info("\\n🔍 CAMPOS CRÍTICOS PARA CARTÕES:")
            sample_event = events[0]
            for field in critical_fields:
                value = sample_event.get(field)
                status = "✅" if value is not None else "❌"
                logger.info(f"  {status} {field}: {value}")
            
            # Salvar resposta para análise detalhada
            filename = f"fixture_{fixture_id}_events_response.json"
            with open(filename, 'w') as f:
                json.dump(events_data, f, indent=2)
            logger.info(f"💾 Resposta salva em: {filename}")
            
            return events_data
        else:
            logger.info("📭 Nenhum evento encontrado para esta fixture")
            return None
    
    def test_multiple_fixtures(self, fixtures: List[Dict]) -> Dict:
        """Testar múltiplas fixtures"""
        logger.info(f"\\n🚀 TESTANDO {len(fixtures)} FIXTURES PARA EVENTOS")
        
        results = {
            'total_tested': len(fixtures),
            'successful': 0,
            'with_events': 0,
            'total_events': 0,
            'event_types': {},
            'fixtures_with_cards': 0,
            'fixtures_with_var': 0
        }
        
        for fixture_data in fixtures:
            try:
                events_data = self.test_single_fixture_events(fixture_data)
                
                if events_data:
                    results['successful'] += 1
                    
                    events = events_data.get('events', [])
                    if events:
                        results['with_events'] += 1
                        results['total_events'] += len(events)
                        
                        # Contar tipos de eventos
                        for event in events:
                            event_type = event.get('type_id')
                            results['event_types'][event_type] = results['event_types'].get(event_type, 0) + 1
                            
                            # Verificar cartões
                            if event_type in [18, 19]:  # Cartão amarelo/vermelho
                                results['fixtures_with_cards'] += 1
                            
                            # Verificar VAR
                            if event.get('var'):
                                results['fixtures_with_var'] += 1
                
            except Exception as e:
                logger.error(f"❌ Erro ao testar fixture {fixture_data['id']}: {e}")
        
        return results
    
    def analyze_event_types(self, event_types: Dict) -> None:
        """Analisar tipos de eventos encontrados"""
        logger.info("\\n📊 ANÁLISE DOS TIPOS DE EVENTOS:")
        
        # Mapear tipos conhecidos (baseado na documentação Sportmonks)
        known_types = {
            1: "Goal",
            2: "Own Goal", 
            3: "Penalty",
            4: "Missed Penalty",
            5: "Substitution",
            6: "Yellow Card",
            7: "Red Card",
            8: "Second Yellow Card",
            9: "VAR",
            10: "Offside",
            11: "Corner",
            12: "Foul",
            13: "Free Kick",
            14: "Throw In",
            15: "Goal Kick",
            16: "Kick Off",
            17: "Half Time",
            18: "Yellow Card",  # Duplicado
            19: "Red Card",     # Duplicado
            20: "VAR Decision"
        }
        
        for event_type, count in sorted(event_types.items()):
            type_name = known_types.get(event_type, f"Tipo {event_type}")
            logger.info(f"  📋 {event_type}: {type_name} - {count} eventos")
    
    def generate_recommendations(self, results: Dict) -> None:
        """Gerar recomendações baseadas nos testes"""
        logger.info("\\n💡 RECOMENDAÇÕES BASEADAS NOS TESTES:")
        
        success_rate = (results['successful'] / results['total_tested']) * 100
        events_rate = (results['with_events'] / results['successful']) * 100 if results['successful'] > 0 else 0
        
        logger.info(f"📈 Taxa de sucesso da API: {success_rate:.1f}%")
        logger.info(f"📊 Taxa de fixtures com eventos: {events_rate:.1f}%")
        logger.info(f"🎯 Total de eventos coletados: {results['total_events']}")
        logger.info(f"🟨 Fixtures com cartões: {results['fixtures_with_cards']}")
        logger.info(f"📺 Fixtures com VAR: {results['fixtures_with_var']}")
        
        logger.info("\\n🔧 PRÓXIMOS PASSOS:")
        logger.info("  1. Mapear campos da API para estrutura da tabela match_events")
        logger.info("  2. Implementar validação de dados antes de inserir")
        logger.info("  3. Criar script de enriquecimento com rate limiting")
        logger.info("  4. Testar com fixtures de diferentes ligas e anos")
    
    def run_test(self):
        """Executar teste completo"""
        logger.info("🚀 INICIANDO TESTE DA API SPORTMONKS PARA EVENTOS")
        
        # Obter fixtures para teste
        test_fixtures = self.get_test_fixtures(10)
        
        if not test_fixtures:
            logger.error("❌ Nenhuma fixture encontrada para teste")
            return {
                'total_tested': 0,
                'successful': 0,
                'with_events': 0,
                'total_events': 0,
                'event_types': {},
                'fixtures_with_cards': 0,
                'fixtures_with_var': 0
            }
        
        # Testar múltiplas fixtures
        results = self.test_multiple_fixtures(test_fixtures)
        
        # Analisar tipos de eventos
        self.analyze_event_types(results['event_types'])
        
        # Gerar recomendações
        self.generate_recommendations(results)
        
        logger.info("\\n✅ TESTE CONCLUÍDO!")
        
        return results

def main():
    """Função principal"""
    tester = EventsApiTester()
    results = tester.run_test()
    
    logger.info("\\n📋 RESUMO DO TESTE:")
    logger.info(f"  📊 Fixtures testadas: {results['total_tested']}")
    logger.info(f"  ✅ Sucessos: {results['successful']}")
    logger.info(f"  📈 Com eventos: {results['with_events']}")
    logger.info(f"  🎯 Total eventos: {results['total_events']}")

if __name__ == "__main__":
    main()
