#!/usr/bin/env python3
"""
Script para alinhar tabelas com estrutura da API Sportmonks
Executa alterações diretamente no Supabase
"""

import os
import sys
from pathlib import Path
import logging

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TableAligner:
    def __init__(self):
        self.supabase = SupabaseClient()
        
    def add_column_if_not_exists(self, table_name: str, column_name: str, column_type: str, default_value=None):
        """Adicionar coluna se não existir"""
        try:
            # Verificar se a coluna já existe
            response = self.supabase.client.table('information_schema.columns').select('column_name').eq('table_name', table_name).eq('column_name', column_name).execute()
            
            if response.data:
                logger.info(f"   ✅ Coluna {column_name} já existe em {table_name}")
                return True
            else:
                logger.info(f"   ➕ Adicionando coluna {column_name} em {table_name}")
                # Como não podemos executar ALTER TABLE diretamente, vamos usar uma abordagem diferente
                # Vamos apenas documentar as colunas que precisam ser adicionadas
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Erro ao verificar coluna {column_name}: {e}")
            return False
    
    def check_table_structure(self, table_name: str):
        """Verificar estrutura atual da tabela"""
        try:
            response = self.supabase.client.table('information_schema.columns').select('column_name, data_type, is_nullable').eq('table_name', table_name).execute()
            
            if response.data:
                logger.info(f"\\n📊 ESTRUTURA ATUAL DA TABELA {table_name.upper()}:")
                logger.info("=" * 50)
                for col in response.data:
                    nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
                    logger.info(f"   {col['column_name']}: {col['data_type']} ({nullable})")
                return response.data
            else:
                logger.warning(f"   ❌ Tabela {table_name} não encontrada")
                return []
                
        except Exception as e:
            logger.error(f"   ❌ Erro ao verificar estrutura da tabela {table_name}: {e}")
            return []
    
    def align_match_events_table(self):
        """Alinhar tabela match_events com API"""
        logger.info("\\n🔧 ALINHANDO TABELA MATCH_EVENTS")
        logger.info("=" * 40)
        
        # Verificar estrutura atual
        current_structure = self.check_table_structure('match_events')
        current_columns = {col['column_name'] for col in current_structure}
        
        # Colunas que precisam ser adicionadas da API
        api_columns = {
            'section': 'VARCHAR(50)',
            'sub_type_id': 'INTEGER',
            'info': 'TEXT',
            'rescinded': 'BOOLEAN',
            'coach_id': 'INTEGER',
            'participant_id': 'INTEGER',
            'related_player_name': 'VARCHAR(255)',
            'sort_order': 'INTEGER',
            'addition': 'TEXT',
            'detailed_period_id': 'INTEGER'
        }
        
        missing_columns = []
        for col_name, col_type in api_columns.items():
            if col_name not in current_columns:
                missing_columns.append((col_name, col_type))
                logger.info(f"   ❌ FALTANDO: {col_name} ({col_type})")
            else:
                logger.info(f"   ✅ EXISTE: {col_name}")
        
        return missing_columns
    
    def align_match_lineups_table(self):
        """Alinhar tabela match_lineups com API"""
        logger.info("\\n🔧 ALINHANDO TABELA MATCH_LINEUPS")
        logger.info("=" * 40)
        
        # Verificar estrutura atual
        current_structure = self.check_table_structure('match_lineups')
        current_columns = {col['column_name'] for col in current_structure}
        
        # Colunas que precisam ser adicionadas da API
        api_columns = {
            'formation_field': 'VARCHAR(50)',
            'sport_id': 'INTEGER',
            'type_id': 'INTEGER'
        }
        
        missing_columns = []
        for col_name, col_type in api_columns.items():
            if col_name not in current_columns:
                missing_columns.append((col_name, col_type))
                logger.info(f"   ❌ FALTANDO: {col_name} ({col_type})")
            else:
                logger.info(f"   ✅ EXISTE: {col_name}")
        
        return missing_columns
    
    def align_match_statistics_table(self):
        """Alinhar tabela match_statistics com API"""
        logger.info("\\n🔧 ALINHANDO TABELA MATCH_STATISTICS")
        logger.info("=" * 40)
        
        # Verificar estrutura atual
        current_structure = self.check_table_structure('match_statistics')
        current_columns = {col['column_name'] for col in current_structure}
        
        # Colunas que precisam ser adicionadas da API
        api_columns = {
            'data': 'JSONB',
            'participant_id': 'INTEGER',
            'type_id': 'INTEGER',
            'location': 'VARCHAR(50)'
        }
        
        missing_columns = []
        for col_name, col_type in api_columns.items():
            if col_name not in current_columns:
                missing_columns.append((col_name, col_type))
                logger.info(f"   ❌ FALTANDO: {col_name} ({col_type})")
            else:
                logger.info(f"   ✅ EXISTE: {col_name}")
        
        return missing_columns
    
    def generate_migration_sql(self, missing_columns_dict):
        """Gerar SQL de migration para as colunas faltantes"""
        logger.info("\\n📋 GERANDO SQL DE MIGRATION")
        logger.info("=" * 40)
        
        migration_sql = "-- Migration para adicionar colunas faltantes da API\\n"
        migration_sql += "-- Gerado automaticamente em " + str(Path(__file__).name) + "\\n\\n"
        
        for table_name, missing_columns in missing_columns_dict.items():
            if missing_columns:
                migration_sql += f"-- Adicionar colunas em {table_name}\\n"
                migration_sql += f"ALTER TABLE {table_name}\\n"
                
                for i, (col_name, col_type) in enumerate(missing_columns):
                    comma = "," if i < len(missing_columns) - 1 else ""
                    migration_sql += f"ADD COLUMN IF NOT EXISTS {col_name} {col_type}{comma}\\n"
                
                migration_sql += ";\\n\\n"
        
        return migration_sql
    
    def run_alignment_check(self):
        """Executar verificação de alinhamento"""
        logger.info("🚀 INICIANDO VERIFICAÇÃO DE ALINHAMENTO DAS TABELAS")
        logger.info("=" * 70)
        
        # Verificar cada tabela
        events_missing = self.align_match_events_table()
        lineups_missing = self.align_match_lineups_table()
        stats_missing = self.align_match_statistics_table()
        
        # Resumo
        logger.info("\\n📊 RESUMO DA VERIFICAÇÃO")
        logger.info("=" * 30)
        
        missing_columns_dict = {
            'match_events': events_missing,
            'match_lineups': lineups_missing,
            'match_statistics': stats_missing
        }
        
        total_missing = sum(len(cols) for cols in missing_columns_dict.values())
        
        if total_missing == 0:
            logger.info("✅ TODAS AS TABELAS ESTÃO ALINHADAS COM A API!")
            logger.info("🎯 As tabelas já possuem todas as colunas necessárias")
        else:
            logger.info(f"⚠️ {total_missing} colunas precisam ser adicionadas:")
            for table_name, missing_cols in missing_columns_dict.items():
                if missing_cols:
                    logger.info(f"   📋 {table_name}: {len(missing_cols)} colunas")
                    for col_name, col_type in missing_cols:
                        logger.info(f"      - {col_name} ({col_type})")
            
            # Gerar SQL de migration
            migration_sql = self.generate_migration_sql(missing_columns_dict)
            
            # Salvar SQL
            migration_file = Path(__file__).parent / "migration_add_missing_columns.sql"
            with open(migration_file, 'w', encoding='utf-8') as f:
                f.write(migration_sql)
            
            logger.info(f"\\n💾 SQL de migration salvo em: {migration_file}")
            logger.info("\\n📋 Para executar a migration, use o SQL gerado no Supabase Dashboard")
        
        return missing_columns_dict

def main():
    """Função principal"""
    aligner = TableAligner()
    aligner.run_alignment_check()

if __name__ == "__main__":
    main()
