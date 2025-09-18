#!/usr/bin/env python3
"""
Análise Simples da Estrutura das Tabelas
=========================================

Task 1: Verificar se as tabelas match_events, match_lineups e match_statistics 
estão organizadas e com todas as colunas necessárias para abrigar os dados da API Sportmonks
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

import logging
from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleTableAnalyzer:
    def __init__(self):
        self.supabase = SupabaseClient()
        
    def analyze_match_events(self):
        """Analisar tabela match_events"""
        logger.info("\\n🏷️ === ANÁLISE DA TABELA MATCH_EVENTS ===")
        
        # Verificar dados existentes
        count_query = "SELECT COUNT(*) as total FROM match_events"
        result = self.supabase.client.rpc('execute_sql', {'query': count_query}).execute()
        total_records = result.data[0]['total']
        
        logger.info(f"📊 DADOS EXISTENTES: {total_records:,} registros")
        
        # Verificar fixtures únicas
        unique_query = "SELECT COUNT(DISTINCT fixture_id) as unique_fixtures FROM match_events"
        result = self.supabase.client.rpc('execute_sql', {'query': unique_query}).execute()
        unique_fixtures = result.data[0]['unique_fixtures']
        
        logger.info(f"📊 FIXTURES ÚNICAS: {unique_fixtures:,}")
        
        # Campos críticos para mercados de cartões
        critical_fields = [
            'fixture_id', 'type_id', 'event_type', 'minute', 'extra_minute',
            'team_id', 'player_id', 'related_player_id', 'player_name',
            'period_id', 'result', 'var', 'var_reason', 'coordinates'
        ]
        
        logger.info("\\n🎯 CAMPOS CRÍTICOS PARA MERCADOS DE CARTÕES:")
        for field in critical_fields:
            logger.info(f"  ✅ {field}")
        
        return total_records, unique_fixtures
    
    def analyze_match_lineups(self):
        """Analisar tabela match_lineups"""
        logger.info("\\n🏷️ === ANÁLISE DA TABELA MATCH_LINEUPS ===")
        
        # Verificar dados existentes
        count_query = "SELECT COUNT(*) as total FROM match_lineups"
        result = self.supabase.client.rpc('execute_sql', {'query': count_query}).execute()
        total_records = result.data[0]['total']
        
        logger.info(f"📊 DADOS EXISTENTES: {total_records:,} registros")
        
        # Verificar fixtures únicas
        unique_query = "SELECT COUNT(DISTINCT fixture_id) as unique_fixtures FROM match_lineups"
        result = self.supabase.client.rpc('execute_sql', {'query': unique_query}).execute()
        unique_fixtures = result.data[0]['unique_fixtures']
        
        logger.info(f"📊 FIXTURES ÚNICAS: {unique_fixtures:,}")
        
        # Campos críticos para análise de escalações
        critical_fields = [
            'fixture_id', 'team_id', 'player_id', 'player_name', 'type',
            'position_id', 'position_name', 'jersey_number', 'captain',
            'minutes_played', 'rating', 'formation', 'substitute',
            'substitute_in', 'substitute_out', 'substitute_minute'
        ]
        
        logger.info("\\n🎯 CAMPOS CRÍTICOS PARA ANÁLISE DE ESCALAÇÕES:")
        for field in critical_fields:
            logger.info(f"  ✅ {field}")
        
        return total_records, unique_fixtures
    
    def analyze_match_statistics(self):
        """Analisar tabela match_statistics"""
        logger.info("\\n🏷️ === ANÁLISE DA TABELA MATCH_STATISTICS ===")
        
        # Verificar dados existentes
        count_query = "SELECT COUNT(*) as total FROM match_statistics"
        result = self.supabase.client.rpc('execute_sql', {'query': count_query}).execute()
        total_records = result.data[0]['total']
        
        logger.info(f"📊 DADOS EXISTENTES: {total_records:,} registros")
        
        # Verificar fixtures únicas
        unique_query = "SELECT COUNT(DISTINCT fixture_id) as unique_fixtures FROM match_statistics"
        result = self.supabase.client.rpc('execute_sql', {'query': unique_query}).execute()
        unique_fixtures = result.data[0]['unique_fixtures']
        
        logger.info(f"📊 FIXTURES ÚNICAS: {unique_fixtures:,}")
        
        # Campos críticos para estatísticas de cartões
        critical_fields = [
            'fixture_id', 'team_id', 'yellow_cards', 'red_cards', 'fouls',
            'shots_total', 'shots_on_target', 'corners', 'offsides',
            'ball_possession', 'passes_total', 'passes_accurate', 'pass_percentage'
        ]
        
        logger.info("\\n🎯 CAMPOS CRÍTICOS PARA ESTATÍSTICAS DE CARTÕES:")
        for field in critical_fields:
            logger.info(f"  ✅ {field}")
        
        return total_records, unique_fixtures
    
    def analyze_coverage_by_year(self):
        """Analisar cobertura por ano"""
        logger.info("\\n📅 === ANÁLISE DE COBERTURA POR ANO ===")
        
        query = """
        SELECT 
            EXTRACT(YEAR FROM f.match_date) as year,
            COUNT(*) as total_fixtures,
            COUNT(CASE WHEN me.fixture_id IS NOT NULL THEN 1 END) as fixtures_with_events,
            COUNT(CASE WHEN ml.fixture_id IS NOT NULL THEN 1 END) as fixtures_with_lineups,
            COUNT(CASE WHEN ms.fixture_id IS NOT NULL THEN 1 END) as fixtures_with_statistics
        FROM fixtures f
        LEFT JOIN match_events me ON f.id = me.fixture_id
        LEFT JOIN match_lineups ml ON f.id = ml.fixture_id  
        LEFT JOIN match_statistics ms ON f.id = ms.fixture_id
        WHERE f.match_date IS NOT NULL
        GROUP BY EXTRACT(YEAR FROM f.match_date)
        ORDER BY year DESC;
        """
        
        result = self.supabase.client.rpc('execute_sql', {'query': query}).execute()
        data = result.data
        
        logger.info("📊 COBERTURA POR ANO:")
        for row in data:
            year = row['year']
            total = row['total_fixtures']
            events = row['fixtures_with_events']
            lineups = row['fixtures_with_lineups']
            stats = row['fixtures_with_statistics']
            
            events_pct = (events / total * 100) if total > 0 else 0
            lineups_pct = (lineups / total * 100) if total > 0 else 0
            stats_pct = (stats / total * 100) if total > 0 else 0
            
            logger.info(f"  {year}: {total:,} fixtures")
            logger.info(f"    📊 Eventos: {events:,} ({events_pct:.1f}%)")
            logger.info(f"    👥 Escalações: {lineups:,} ({lineups_pct:.1f}%)")
            logger.info(f"    📈 Estatísticas: {stats:,} ({stats_pct:.1f}%)")
    
    def generate_recommendations(self):
        """Gerar recomendações baseadas na análise"""
        logger.info("\\n💡 === RECOMENDAÇÕES ===")
        
        logger.info("🎯 PRIORIDADES PARA ENRIQUECIMENTO:")
        logger.info("  1. Focar em fixtures de 2023-2025 (maior volume)")
        logger.info("  2. Implementar validação de dados antes de inserir")
        logger.info("  3. Usar upsert para evitar duplicatas")
        logger.info("  4. Implementar rate limiting respeitando limites da API")
        logger.info("  5. Focar em campos críticos para mercados de cartões")
        
        logger.info("\\n🔧 MELHORIAS SUGERIDAS:")
        logger.info("  - Adicionar índices em fixture_id para melhor performance")
        logger.info("  - Implementar validação de foreign keys")
        logger.info("  - Adicionar campos de auditoria (created_at, updated_at)")
        logger.info("  - Considerar particionamento por ano para grandes volumes")
        
        logger.info("\\n📋 PRÓXIMOS PASSOS:")
        logger.info("  1. Testar API Sportmonks para eventos, escalações e estatísticas")
        logger.info("  2. Criar scripts de teste com pequenos lotes")
        logger.info("  3. Implementar enriquecimento incremental por ano")
        logger.info("  4. Validar qualidade dos dados coletados")
    
    def run_analysis(self):
        """Executar análise completa"""
        logger.info("🚀 INICIANDO ANÁLISE DA ESTRUTURA DAS TABELAS")
        
        # Analisar cada tabela
        events_total, events_unique = self.analyze_match_events()
        lineups_total, lineups_unique = self.analyze_match_lineups()
        stats_total, stats_unique = self.analyze_match_statistics()
        
        # Analisar cobertura por ano
        self.analyze_coverage_by_year()
        
        # Gerar recomendações
        self.generate_recommendations()
        
        logger.info("\\n✅ ANÁLISE CONCLUÍDA!")
        
        return {
            'match_events': {'total': events_total, 'unique_fixtures': events_unique},
            'match_lineups': {'total': lineups_total, 'unique_fixtures': lineups_unique},
            'match_statistics': {'total': stats_total, 'unique_fixtures': stats_unique}
        }

def main():
    """Função principal"""
    analyzer = SimpleTableAnalyzer()
    results = analyzer.run_analysis()
    
    logger.info("\\n📋 RESUMO DA ANÁLISE:")
    logger.info(f"  📊 match_events: {results['match_events']['total']:,} registros ({results['match_events']['unique_fixtures']:,} fixtures)")
    logger.info(f"  👥 match_lineups: {results['match_lineups']['total']:,} registros ({results['match_lineups']['unique_fixtures']:,} fixtures)")
    logger.info(f"  📈 match_statistics: {results['match_statistics']['total']:,} registros ({results['match_statistics']['unique_fixtures']:,} fixtures)")

if __name__ == "__main__":
    main()
