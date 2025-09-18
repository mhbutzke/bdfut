#!/usr/bin/env python3
"""
Script para criar scripts de teste baseados nos resultados dos testes da API
"""

import os
import sys
import json
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
# from bdfut.core.config import Config
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestScriptGenerator:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def create_events_test_script(self):
        """Criar script de teste para eventos"""
        script_content = '''#!/usr/bin/env python3
"""
Script de teste para eventos - baseado nos resultados dos testes da API
"""

import os
import sys
import json
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EventsTestScript:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def test_events_for_fixture(self, fixture_id: int):
        """Testar eventos para uma fixture específica"""
        try:
            # Buscar eventos da API
            events_data = self.sportmonks.get_fixture_events(fixture_id)
            
            if not events_data:
                logger.warning(f"❌ Nenhum evento encontrado para fixture {fixture_id}")
                return None
                
            logger.info(f"📊 {len(events_data)} eventos encontrados para fixture {fixture_id}")
            
            # Analisar eventos
            analysis = self.analyze_events(events_data)
            
            # Salvar resposta para análise
            with open(f"fixture_{fixture_id}_events_response.json", "w") as f:
                json.dump(events_data, f, indent=2)
                
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar eventos para fixture {fixture_id}: {e}")
            return None
            
    def analyze_events(self, events_data):
        """Analisar eventos coletados"""
        analysis = {
            'total_events': len(events_data),
            'event_types': {},
            'cards': {'yellow': 0, 'red': 0},
            'fouls': 0,
            'goals': 0,
            'substitutions': 0,
            'var_events': 0
        }
        
        for event in events_data:
            # Contar tipos de eventos
            event_type = event.get('type', 'unknown')
            analysis['event_types'][event_type] = analysis['event_types'].get(event_type, 0) + 1
            
            # Analisar cartões
            if event_type in ['yellow_card', 'red_card']:
                if event_type == 'yellow_card':
                    analysis['cards']['yellow'] += 1
                else:
                    analysis['cards']['red'] += 1
                    
            # Analisar faltas
            if event_type == 'foul':
                analysis['fouls'] += 1
                
            # Analisar gols
            if event_type in ['goal', 'own_goal']:
                analysis['goals'] += 1
                
            # Analisar substituições
            if event_type == 'substitution':
                analysis['substitutions'] += 1
                
            # Analisar VAR
            if event.get('var', False):
                analysis['var_events'] += 1
                
        return analysis
        
    def run_test(self, fixture_id: int):
        """Executar teste completo"""
        logger.info(f"🚀 TESTANDO EVENTOS PARA FIXTURE {fixture_id}")
        
        analysis = self.test_events_for_fixture(fixture_id)
        
        if analysis:
            logger.info(f"📊 Análise dos eventos:")
            logger.info(f"   Total: {analysis['total_events']}")
            logger.info(f"   Cartões amarelos: {analysis['cards']['yellow']}")
            logger.info(f"   Cartões vermelhos: {analysis['cards']['red']}")
            logger.info(f"   Faltas: {analysis['fouls']}")
            logger.info(f"   Gols: {analysis['goals']}")
            logger.info(f"   Substituições: {analysis['substitutions']}")
            logger.info(f"   Eventos VAR: {analysis['var_events']}")
            
        return analysis

if __name__ == "__main__":
    # Testar com uma fixture específica
    test_script = EventsTestScript()
    fixture_id = 19429228  # Fixture de teste
    
    analysis = test_script.run_test(fixture_id)
    
    if analysis:
        logger.info("✅ Teste de eventos concluído com sucesso!")
    else:
        logger.error("❌ Teste de eventos falhou!")
'''
        
        # Salvar script
        script_path = Path(__file__).parent / "15_planning_08_test_events_script.py"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
            
        logger.info(f"✅ Script de teste para eventos criado: {script_path}")
        
    def create_lineups_test_script(self):
        """Criar script de teste para escalações"""
        script_content = '''#!/usr/bin/env python3
"""
Script de teste para escalações - baseado nos resultados dos testes da API
"""

import os
import sys
import json
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LineupsTestScript:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def test_lineups_for_fixture(self, fixture_id: int):
        """Testar escalações para uma fixture específica"""
        try:
            # Buscar escalações da API
            lineups_data = self.sportmonks.get_fixture_lineups(fixture_id)
            
            if not lineups_data:
                logger.warning(f"❌ Nenhuma escalação encontrada para fixture {fixture_id}")
                return None
                
            logger.info(f"📊 {len(lineups_data)} escalações encontradas para fixture {fixture_id}")
            
            # Analisar escalações
            analysis = self.analyze_lineups(lineups_data)
            
            # Salvar resposta para análise
            with open(f"fixture_{fixture_id}_lineups_response.json", "w") as f:
                json.dump(lineups_data, f, indent=2)
                
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar escalações para fixture {fixture_id}: {e}")
            return None
            
    def analyze_lineups(self, lineups_data):
        """Analisar escalações coletadas"""
        analysis = {
            'total_lineups': len(lineups_data),
            'teams': {},
            'players': {'total': 0, 'with_positions': 0, 'captains': 0},
            'formations': {},
            'substitutions': 0
        }
        
        for lineup in lineups_data:
            team_id = lineup.get('team_id')
            team_name = lineup.get('team_name', 'Unknown')
            
            if team_id not in analysis['teams']:
                analysis['teams'][team_id] = {
                    'name': team_name,
                    'players': 0,
                    'formation': lineup.get('formation'),
                    'captain': None
                }
                
            # Contar jogadores
            analysis['teams'][team_id]['players'] += 1
            analysis['players']['total'] += 1
            
            # Analisar posições
            if lineup.get('position_name'):
                analysis['players']['with_positions'] += 1
                
            # Analisar capitão
            if lineup.get('captain'):
                analysis['players']['captains'] += 1
                analysis['teams'][team_id]['captain'] = lineup.get('player_name')
                
            # Analisar formação
            formation = lineup.get('formation')
            if formation:
                analysis['formations'][formation] = analysis['formations'].get(formation, 0) + 1
                
            # Analisar substituições
            if lineup.get('substitution'):
                analysis['substitutions'] += 1
                
        return analysis
        
    def run_test(self, fixture_id: int):
        """Executar teste completo"""
        logger.info(f"🚀 TESTANDO ESCALAÇÕES PARA FIXTURE {fixture_id}")
        
        analysis = self.test_lineups_for_fixture(fixture_id)
        
        if analysis:
            logger.info(f"📊 Análise das escalações:")
            logger.info(f"   Total: {analysis['total_lineups']}")
            logger.info(f"   Times: {len(analysis['teams'])}")
            logger.info(f"   Jogadores: {analysis['players']['total']}")
            logger.info(f"   Com posições: {analysis['players']['with_positions']}")
            logger.info(f"   Capitães: {analysis['players']['captains']}")
            logger.info(f"   Substituições: {analysis['substitutions']}")
            
        return analysis

if __name__ == "__main__":
    # Testar com uma fixture específica
    test_script = LineupsTestScript()
    fixture_id = 19429228  # Fixture de teste
    
    analysis = test_script.run_test(fixture_id)
    
    if analysis:
        logger.info("✅ Teste de escalações concluído com sucesso!")
    else:
        logger.error("❌ Teste de escalações falhou!")
'''
        
        # Salvar script
        script_path = Path(__file__).parent / "15_planning_09_test_lineups_script.py"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
            
        logger.info(f"✅ Script de teste para escalações criado: {script_path}")
        
    def create_statistics_test_script(self):
        """Criar script de teste para estatísticas"""
        script_content = '''#!/usr/bin/env python3
"""
Script de teste para estatísticas - baseado nos resultados dos testes da API
"""

import os
import sys
import json
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StatisticsTestScript:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def test_statistics_for_fixture(self, fixture_id: int):
        """Testar estatísticas para uma fixture específica"""
        try:
            # Buscar estatísticas da API
            statistics_data = self.sportmonks.get_fixture_statistics(fixture_id)
            
            if not statistics_data:
                logger.warning(f"❌ Nenhuma estatística encontrada para fixture {fixture_id}")
                return None
                
            logger.info(f"📊 {len(statistics_data)} estatísticas encontradas para fixture {fixture_id}")
            
            # Analisar estatísticas
            analysis = self.analyze_statistics(statistics_data)
            
            # Salvar resposta para análise
            with open(f"fixture_{fixture_id}_statistics_response.json", "w") as f:
                json.dump(statistics_data, f, indent=2)
                
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar estatísticas para fixture {fixture_id}: {e}")
            return None
            
    def analyze_statistics(self, statistics_data):
        """Analisar estatísticas coletadas"""
        analysis = {
            'total_statistics': len(statistics_data),
            'teams': {},
            'card_stats': {'yellow_cards': 0, 'red_cards': 0, 'fouls': 0},
            'possession': {},
            'shots': {'total': 0, 'on_target': 0},
            'passes': {'total': 0, 'accurate': 0},
            'goals': {'scored': 0, 'conceded': 0}
        }
        
        for stat in statistics_data:
            team_id = stat.get('team_id')
            team_name = stat.get('team_name', 'Unknown')
            
            if team_id not in analysis['teams']:
                analysis['teams'][team_id] = {
                    'name': team_name,
                    'stats': {}
                }
                
            # Analisar cartões
            if stat.get('type') == 'yellow_cards':
                analysis['card_stats']['yellow_cards'] += stat.get('value', 0)
            elif stat.get('type') == 'red_cards':
                analysis['card_stats']['red_cards'] += stat.get('value', 0)
            elif stat.get('type') == 'fouls':
                analysis['card_stats']['fouls'] += stat.get('value', 0)
                
            # Analisar posse de bola
            if stat.get('type') == 'ball_possession':
                analysis['possession'][team_id] = stat.get('value', 0)
                
            # Analisar chutes
            if stat.get('type') == 'shots_total':
                analysis['shots']['total'] += stat.get('value', 0)
            elif stat.get('type') == 'shots_on_target':
                analysis['shots']['on_target'] += stat.get('value', 0)
                
            # Analisar passes
            if stat.get('type') == 'passes_total':
                analysis['passes']['total'] += stat.get('value', 0)
            elif stat.get('type') == 'passes_accurate':
                analysis['passes']['accurate'] += stat.get('value', 0)
                
            # Analisar gols
            if stat.get('type') == 'goals':
                analysis['goals']['scored'] += stat.get('value', 0)
            elif stat.get('type') == 'goals_conceded':
                analysis['goals']['conceded'] += stat.get('value', 0)
                
        return analysis
        
    def run_test(self, fixture_id: int):
        """Executar teste completo"""
        logger.info(f"🚀 TESTANDO ESTATÍSTICAS PARA FIXTURE {fixture_id}")
        
        analysis = self.test_statistics_for_fixture(fixture_id)
        
        if analysis:
            logger.info(f"📊 Análise das estatísticas:")
            logger.info(f"   Total: {analysis['total_statistics']}")
            logger.info(f"   Times: {len(analysis['teams'])}")
            logger.info(f"   Cartões amarelos: {analysis['card_stats']['yellow_cards']}")
            logger.info(f"   Cartões vermelhos: {analysis['card_stats']['red_cards']}")
            logger.info(f"   Faltas: {analysis['card_stats']['fouls']}")
            logger.info(f"   Chutes: {analysis['shots']['total']}")
            logger.info(f"   Passes: {analysis['passes']['total']}")
            logger.info(f"   Gols: {analysis['goals']['scored']}")
            
        return analysis

if __name__ == "__main__":
    # Testar com uma fixture específica
    test_script = StatisticsTestScript()
    fixture_id = 19429228  # Fixture de teste
    
    analysis = test_script.run_test(fixture_id)
    
    if analysis:
        logger.info("✅ Teste de estatísticas concluído com sucesso!")
    else:
        logger.error("❌ Teste de estatísticas falhou!")
'''
        
        # Salvar script
        script_path = Path(__file__).parent / "15_planning_10_test_statistics_script.py"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
            
        logger.info(f"✅ Script de teste para estatísticas criado: {script_path}")
        
    def create_comprehensive_test_script(self):
        """Criar script de teste abrangente"""
        script_content = '''#!/usr/bin/env python3
"""
Script de teste abrangente para eventos, escalações e estatísticas
"""

import os
import sys
import json
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveTestScript:
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        
    def get_test_fixtures(self, limit: int = 5):
        """Obter fixtures para teste"""
        try:
            response = self.supabase.client.table('fixtures').select(
                'id, sportmonks_id, match_date, home_score, away_score, status'
            ).not_.is_('match_date', 'null').in_(
                'status', ['FT', 'FT_PEN', 'AET']
            ).order('match_date', desc=True).limit(limit).execute()
            
            return response.data
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixtures: {e}")
            return []
            
    def test_all_data_types(self, fixture_id: int):
        """Testar todos os tipos de dados para uma fixture"""
        results = {
            'fixture_id': fixture_id,
            'events': None,
            'lineups': None,
            'statistics': None,
            'success': False
        }
        
        try:
            # Testar eventos
            logger.info(f"📡 Testando eventos para fixture {fixture_id}")
            events_data = self.sportmonks.get_fixture_events(fixture_id)
            if events_data:
                results['events'] = {
                    'count': len(events_data),
                    'cards': sum(1 for e in events_data if e.get('type') in ['yellow_card', 'red_card']),
                    'fouls': sum(1 for e in events_data if e.get('type') == 'foul')
                }
                
            # Testar escalações
            logger.info(f"📡 Testando escalações para fixture {fixture_id}")
            lineups_data = self.sportmonks.get_fixture_lineups(fixture_id)
            if lineups_data:
                results['lineups'] = {
                    'count': len(lineups_data),
                    'teams': len(set(l.get('team_id') for l in lineups_data if l.get('team_id'))),
                    'players': len(lineups_data)
                }
                
            # Testar estatísticas
            logger.info(f"📡 Testando estatísticas para fixture {fixture_id}")
            statistics_data = self.sportmonks.get_fixture_statistics(fixture_id)
            if statistics_data:
                results['statistics'] = {
                    'count': len(statistics_data),
                    'teams': len(set(s.get('team_id') for s in statistics_data if s.get('team_id'))),
                    'card_stats': sum(1 for s in statistics_data if s.get('type') in ['yellow_cards', 'red_cards'])
                }
                
            results['success'] = True
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar fixture {fixture_id}: {e}")
            
        return results
        
    def run_comprehensive_test(self, limit: int = 5):
        """Executar teste abrangente"""
        logger.info(f"🚀 INICIANDO TESTE ABRANGENTE COM {limit} FIXTURES")
        
        fixtures = self.get_test_fixtures(limit)
        
        if not fixtures:
            logger.error("❌ Nenhuma fixture encontrada para teste")
            return
            
        results = []
        
        for fixture in fixtures:
            fixture_id = fixture['sportmonks_id']
            logger.info(f"\\n📡 Testando fixture {fixture_id}")
            
            result = self.test_all_data_types(fixture_id)
            results.append(result)
            
        # Resumo dos resultados
        logger.info(f"\\n📊 RESUMO DOS TESTES:")
        logger.info(f"   Fixtures testadas: {len(results)}")
        logger.info(f"   Sucessos: {sum(1 for r in results if r['success'])}")
        
        events_count = sum(1 for r in results if r['events'])
        lineups_count = sum(1 for r in results if r['lineups'])
        statistics_count = sum(1 for r in results if r['statistics'])
        
        logger.info(f"   Com eventos: {events_count}")
        logger.info(f"   Com escalações: {lineups_count}")
        logger.info(f"   Com estatísticas: {statistics_count}")
        
        # Salvar resultados
        with open("comprehensive_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        logger.info("💾 Resultados salvos em: comprehensive_test_results.json")
        
        return results

if __name__ == "__main__":
    test_script = ComprehensiveTestScript()
    results = test_script.run_comprehensive_test(5)
    
    if results:
        logger.info("✅ Teste abrangente concluído com sucesso!")
    else:
        logger.error("❌ Teste abrangente falhou!")
'''
        
        # Salvar script
        script_path = Path(__file__).parent / "15_planning_11_comprehensive_test_script.py"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
            
        logger.info(f"✅ Script de teste abrangente criado: {script_path}")
        
    def run(self):
        """Executar geração de todos os scripts"""
        logger.info("🚀 INICIANDO GERAÇÃO DE SCRIPTS DE TESTE")
        
        # Criar scripts individuais
        self.create_events_test_script()
        self.create_lineups_test_script()
        self.create_statistics_test_script()
        
        # Criar script abrangente
        self.create_comprehensive_test_script()
        
        logger.info("✅ Todos os scripts de teste foram criados com sucesso!")
        logger.info("\\n📋 Scripts criados:")
        logger.info("   - 15_planning_08_test_events_script.py")
        logger.info("   - 15_planning_09_test_lineups_script.py")
        logger.info("   - 15_planning_10_test_statistics_script.py")
        logger.info("   - 15_planning_11_comprehensive_test_script.py")

if __name__ == "__main__":
    generator = TestScriptGenerator()
    generator.run()
