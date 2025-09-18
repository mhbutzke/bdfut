#!/usr/bin/env python3
"""
Análise da Estrutura das Tabelas
=================================

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

class TableStructureAnalyzer:
    def __init__(self):
        self.supabase = SupabaseClient()
        
    def analyze_table_structure(self, table_name):
        """Analisar estrutura de uma tabela específica"""
        logger.info(f"🔍 Analisando estrutura da tabela: {table_name}")
        
        # Obter estrutura da tabela
        query = f"""
        SELECT 
            column_name, 
            data_type, 
            is_nullable, 
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        ORDER BY ordinal_position;
        """
        
        # Usar método direto do Supabase
        response = self.supabase.client.table('information_schema.columns').select('*').eq('table_name', table_name).execute()
        columns = response.data
        
        logger.info(f"📊 Colunas encontradas: {len(columns)}")
        
        # Analisar cada coluna
        for col in columns:
            col_name = col['column_name']
            data_type = col['data_type']
            nullable = col['is_nullable']
            default = col['column_default']
            
            logger.info(f"  📋 {col_name}: {data_type} {'NULL' if nullable == 'YES' else 'NOT NULL'} {f'DEFAULT {default}' if default else ''}")
        
        return columns
    
    def analyze_match_events(self):
        """Analisar tabela match_events"""
        logger.info("\\n🏷️ === ANÁLISE DA TABELA MATCH_EVENTS ===")
        
        columns = self.analyze_table_structure('match_events')
        
        # Campos críticos para mercados de cartões
        critical_fields = [
            'fixture_id', 'type_id', 'event_type', 'minute', 'extra_minute',
            'team_id', 'player_id', 'related_player_id', 'player_name',
            'period_id', 'result', 'var', 'var_reason', 'coordinates'
        ]
        
        logger.info("\\n🎯 CAMPOS CRÍTICOS PARA MERCADOS DE CARTÕES:")
        for field in critical_fields:
            found = any(col['column_name'] == field for col in columns)
            status = "✅" if found else "❌"
            logger.info(f"  {status} {field}")
        
        # Verificar dados existentes
        count_query = "SELECT COUNT(*) as total FROM match_events"
        result = self.supabase.client.rpc('execute_sql', {'query': count_query}).execute()
        total_records = result.data[0]['total']
        
        logger.info(f"\\n📊 DADOS EXISTENTES: {total_records:,} registros")
        
        return columns
    
    def analyze_match_lineups(self):
        """Analisar tabela match_lineups"""
        logger.info("\\n🏷️ === ANÁLISE DA TABELA MATCH_LINEUPS ===")
        
        columns = self.analyze_table_structure('match_lineups')
        
        # Campos críticos para análise de escalações
        critical_fields = [
            'fixture_id', 'team_id', 'player_id', 'player_name', 'type',
            'position_id', 'position_name', 'jersey_number', 'captain',
            'minutes_played', 'rating', 'formation', 'substitute',
            'substitute_in', 'substitute_out', 'substitute_minute'
        ]
        
        logger.info("\\n🎯 CAMPOS CRÍTICOS PARA ANÁLISE DE ESCALAÇÕES:")
        for field in critical_fields:
            found = any(col['column_name'] == field for col in columns)
            status = "✅" if found else "❌"
            logger.info(f"  {status} {field}")
        
        # Verificar dados existentes
        count_query = "SELECT COUNT(*) as total FROM match_lineups"
        result = self.supabase.client.rpc('execute_sql', {'query': count_query}).execute()
        total_records = result.data[0]['total']
        
        logger.info(f"\\n📊 DADOS EXISTENTES: {total_records:,} registros")
        
        return columns
    
    def analyze_match_statistics(self):
        """Analisar tabela match_statistics"""
        logger.info("\\n🏷️ === ANÁLISE DA TABELA MATCH_STATISTICS ===")
        
        columns = self.analyze_table_structure('match_statistics')
        
        # Campos críticos para estatísticas de cartões
        critical_fields = [
            'fixture_id', 'team_id', 'yellow_cards', 'red_cards', 'fouls',
            'shots_total', 'shots_on_target', 'corners', 'offsides',
            'ball_possession', 'passes_total', 'passes_accurate', 'pass_percentage'
        ]
        
        logger.info("\\n🎯 CAMPOS CRÍTICOS PARA ESTATÍSTICAS DE CARTÕES:")
        for field in critical_fields:
            found = any(col['column_name'] == field for col in columns)
            status = "✅" if found else "❌"
            logger.info(f"  {status} {field}")
        
        # Verificar dados existentes
        count_query = "SELECT COUNT(*) as total FROM match_statistics"
        result = self.supabase.client.rpc('execute_sql', {'query': count_query}).execute()
        total_records = result.data[0]['total']
        
        logger.info(f"\\n📊 DADOS EXISTENTES: {total_records:,} registros")
        
        return columns
    
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
    
    def run_analysis(self):
        """Executar análise completa"""
        logger.info("🚀 INICIANDO ANÁLISE DA ESTRUTURA DAS TABELAS")
        
        # Analisar cada tabela
        events_columns = self.analyze_match_events()
        lineups_columns = self.analyze_match_lineups()
        stats_columns = self.analyze_match_statistics()
        
        # Analisar cobertura por ano
        self.analyze_coverage_by_year()
        
        # Gerar recomendações
        self.generate_recommendations()
        
        logger.info("\\n✅ ANÁLISE CONCLUÍDA!")
        
        return {
            'match_events': events_columns,
            'match_lineups': lineups_columns,
            'match_statistics': stats_columns
        }

def main():
    """Função principal"""
    analyzer = TableStructureAnalyzer()
    results = analyzer.run_analysis()
    
    logger.info("\\n📋 RESUMO DA ANÁLISE:")
    logger.info(f"  📊 match_events: {len(results['match_events'])} colunas")
    logger.info(f"  👥 match_lineups: {len(results['match_lineups'])} colunas")
    logger.info(f"  📈 match_statistics: {len(results['match_statistics'])} colunas")

if __name__ == "__main__":
    main()
