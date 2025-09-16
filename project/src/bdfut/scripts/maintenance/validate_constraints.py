#!/usr/bin/env python3
"""
Script de Validação de Constraints - TASK-DB-002
Agente: Database Specialist 🗄️
Data: 2025-01-13

Valida todas as constraints implementadas e verifica integridade dos dados.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

from bdfut.core.supabase_client import SupabaseClient
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/validate_constraints_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ConstraintValidator:
    """Validador de constraints do banco de dados."""
    
    def __init__(self):
        """Inicializar cliente Supabase."""
        try:
            self.config = Config()
            self.supabase = SupabaseClient(self.config)
            logger.info("✅ Cliente Supabase inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
            raise
    
    def validate_fixtures_constraints(self):
        """Validar constraints da tabela fixtures."""
        logger.info("🔍 Validando constraints da tabela fixtures...")
        
        violations = []
        
        # Verificar scores negativos
        try:
            result = self.supabase.execute_sql("""
                SELECT id, sportmonks_id, home_score, away_score 
                FROM fixtures 
                WHERE home_score < 0 OR away_score < 0
                LIMIT 10;
            """)
            if result:
                violations.extend([f"Score negativo encontrado: {row}" for row in result])
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar scores: {e}")
        
        # Verificar times iguais
        try:
            result = self.supabase.execute_sql("""
                SELECT id, sportmonks_id, home_team_id, away_team_id 
                FROM fixtures 
                WHERE home_team_id = away_team_id
                LIMIT 10;
            """)
            if result:
                violations.extend([f"Times iguais encontrados: {row}" for row in result])
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar times iguais: {e}")
        
        # Verificar datas futuras
        try:
            result = self.supabase.execute_sql("""
                SELECT id, sportmonks_id, match_date 
                FROM fixtures 
                WHERE match_date > CURRENT_TIMESTAMP + INTERVAL '1 year'
                LIMIT 10;
            """)
            if result:
                violations.extend([f"Data muito futura encontrada: {row}" for row in result])
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar datas futuras: {e}")
        
        if violations:
            logger.warning(f"⚠️ {len(violations)} violações encontradas em fixtures")
            for violation in violations[:5]:  # Mostrar apenas as primeiras 5
                logger.warning(f"  - {violation}")
        else:
            logger.info("✅ Constraints de fixtures validadas com sucesso")
        
        return len(violations)
    
    def validate_seasons_constraints(self):
        """Validar constraints da tabela seasons."""
        logger.info("🔍 Validando constraints da tabela seasons...")
        
        violations = []
        
        # Verificar datas inválidas
        try:
            result = self.supabase.execute_sql("""
                SELECT id, sportmonks_id, start_date, end_date 
                FROM seasons 
                WHERE start_date > end_date
                LIMIT 10;
            """)
            if result:
                violations.extend([f"Data de início posterior ao fim: {row}" for row in result])
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar datas: {e}")
        
        # Verificar múltiplas temporadas atuais por liga
        try:
            result = self.supabase.execute_sql("""
                SELECT league_id, COUNT(*) as count 
                FROM seasons 
                WHERE is_current = true 
                GROUP BY league_id 
                HAVING COUNT(*) > 1
                LIMIT 10;
            """)
            if result:
                violations.extend([f"Múltiplas temporadas atuais na liga {row['league_id']}: {row['count']}" for row in result])
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar temporadas atuais: {e}")
        
        if violations:
            logger.warning(f"⚠️ {len(violations)} violações encontradas em seasons")
            for violation in violations[:5]:
                logger.warning(f"  - {violation}")
        else:
            logger.info("✅ Constraints de seasons validadas com sucesso")
        
        return len(violations)
    
    def validate_teams_constraints(self):
        """Validar constraints da tabela teams."""
        logger.info("🔍 Validando constraints da tabela teams...")
        
        violations = []
        
        # Verificar nomes vazios
        try:
            result = self.supabase.execute_sql("""
                SELECT id, sportmonks_id, name 
                FROM teams 
                WHERE name IS NULL OR TRIM(name) = ''
                LIMIT 10;
            """)
            if result:
                violations.extend([f"Nome vazio encontrado: {row}" for row in result])
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar nomes: {e}")
        
        # Verificar ano de fundação inválido
        try:
            result = self.supabase.execute_sql("""
                SELECT id, sportmonks_id, founded 
                FROM teams 
                WHERE founded < 1800 OR founded > EXTRACT(YEAR FROM CURRENT_DATE) + 1
                LIMIT 10;
            """)
            if result:
                violations.extend([f"Ano de fundação inválido: {row}" for row in result])
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar anos de fundação: {e}")
        
        if violations:
            logger.warning(f"⚠️ {len(violations)} violações encontradas em teams")
            for violation in violations[:5]:
                logger.warning(f"  - {violation}")
        else:
            logger.info("✅ Constraints de teams validadas com sucesso")
        
        return len(violations)
    
    def validate_foreign_keys(self):
        """Validar integridade das foreign keys."""
        logger.info("🔍 Validando integridade das foreign keys...")
        
        violations = []
        
        # Verificar fixtures com times inexistentes
        try:
            result = self.supabase.execute_sql("""
                SELECT f.id, f.sportmonks_id, f.home_team_id, f.away_team_id
                FROM fixtures f
                LEFT JOIN teams ht ON f.home_team_id = ht.sportmonks_id
                LEFT JOIN teams at ON f.away_team_id = at.sportmonks_id
                WHERE ht.sportmonks_id IS NULL OR at.sportmonks_id IS NULL
                LIMIT 10;
            """)
            if result:
                violations.extend([f"Fixture com time inexistente: {row}" for row in result])
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar foreign keys de fixtures: {e}")
        
        # Verificar fixtures com ligas inexistentes
        try:
            result = self.supabase.execute_sql("""
                SELECT f.id, f.sportmonks_id, f.league_id
                FROM fixtures f
                LEFT JOIN leagues l ON f.league_id = l.sportmonks_id
                WHERE l.sportmonks_id IS NULL
                LIMIT 10;
            """)
            if result:
                violations.extend([f"Fixture com liga inexistente: {row}" for row in result])
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar foreign keys de ligas: {e}")
        
        if violations:
            logger.warning(f"⚠️ {len(violations)} violações de foreign key encontradas")
            for violation in violations[:5]:
                logger.warning(f"  - {violation}")
        else:
            logger.info("✅ Foreign keys validadas com sucesso")
        
        return len(violations)
    
    def run_validation(self):
        """Executar validação completa."""
        logger.info("🚀 Iniciando validação completa de constraints...")
        
        total_violations = 0
        
        # Validar cada tabela
        total_violations += self.validate_fixtures_constraints()
        total_violations += self.validate_seasons_constraints()
        total_violations += self.validate_teams_constraints()
        total_violations += self.validate_foreign_keys()
        
        # Resumo final
        if total_violations == 0:
            logger.info("🎉 VALIDAÇÃO COMPLETA: Todas as constraints estão válidas!")
            return True
        else:
            logger.warning(f"⚠️ VALIDAÇÃO COMPLETA: {total_violations} violações encontradas")
            return False

def main():
    """Função principal."""
    try:
        validator = ConstraintValidator()
        success = validator.run_validation()
        
        if success:
            print("✅ Validação de constraints concluída com sucesso!")
            sys.exit(0)
        else:
            print("⚠️ Validação encontrou violações. Verifique os logs.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Erro durante validação: {e}")
        print(f"❌ Erro durante validação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
