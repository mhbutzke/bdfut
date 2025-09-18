#!/usr/bin/env python3
"""
Database Validator - Ferramenta para validar integridade dos dados BDFut
Author: Database Optimization Team
Date: 2025-01-18
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from supabase import create_client
import pandas as pd
from ..config.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Resultado de uma validação"""
    table_name: str
    validation_type: str
    status: str  # 'PASS', 'FAIL', 'WARNING'
    message: str
    count: Optional[int] = None
    details: Optional[Dict] = None

class DatabaseValidator:
    """Validador de integridade da base de dados BDFut"""
    
    def __init__(self):
        """Inicializar validador"""
        Config.validate()
        self.supabase = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )
        self.results: List[ValidationResult] = []
    
    def log_result(self, result: ValidationResult):
        """Registrar resultado de validação"""
        self.results.append(result)
        status_emoji = {
            'PASS': '✅',
            'FAIL': '❌', 
            'WARNING': '⚠️'
        }
        logger.info(f"{status_emoji.get(result.status, '❓')} {result.table_name}: {result.message}")
    
    async def validate_fixtures_integrity(self) -> List[ValidationResult]:
        """Validar integridade da tabela fixtures"""
        logger.info("🔍 Validando integridade da tabela fixtures...")
        
        # 1. Verificar registros órfãos (sem liga)
        response = self.supabase.table('fixtures').select('fixture_id').is_('league_id', 'null').execute()
        orphan_count = len(response.data)
        
        if orphan_count == 0:
            self.log_result(ValidationResult(
                'fixtures', 'orphan_leagues', 'PASS', 
                'Nenhuma fixture órfã sem liga encontrada'
            ))
        else:
            self.log_result(ValidationResult(
                'fixtures', 'orphan_leagues', 'FAIL',
                f'Encontradas {orphan_count} fixtures sem liga associada',
                count=orphan_count
            ))
        
        # 2. Verificar fixtures sem times
        response = self.supabase.table('fixtures').select('fixture_id').or_('home_team_id.is.null,away_team_id.is.null').execute()
        no_teams_count = len(response.data)
        
        if no_teams_count == 0:
            self.log_result(ValidationResult(
                'fixtures', 'missing_teams', 'PASS',
                'Todas as fixtures têm times associados'
            ))
        else:
            self.log_result(ValidationResult(
                'fixtures', 'missing_teams', 'WARNING',
                f'Encontradas {no_teams_count} fixtures sem times completos',
                count=no_teams_count
            ))
        
        # 3. Verificar fixtures com datas inconsistentes
        response = self.supabase.rpc('validate_fixture_dates').execute()
        if hasattr(response, 'data') and response.data:
            invalid_dates = response.data[0].get('count', 0)
            if invalid_dates == 0:
                self.log_result(ValidationResult(
                    'fixtures', 'date_consistency', 'PASS',
                    'Todas as datas de fixtures são consistentes'
                ))
            else:
                self.log_result(ValidationResult(
                    'fixtures', 'date_consistency', 'WARNING',
                    f'Encontradas {invalid_dates} fixtures com datas inconsistentes',
                    count=invalid_dates
                ))
        
        # 4. Verificar placares negativos
        response = self.supabase.table('fixtures').select('fixture_id').or_('home_score.lt.0,away_score.lt.0').execute()
        negative_scores = len(response.data)
        
        if negative_scores == 0:
            self.log_result(ValidationResult(
                'fixtures', 'negative_scores', 'PASS',
                'Nenhum placar negativo encontrado'
            ))
        else:
            self.log_result(ValidationResult(
                'fixtures', 'negative_scores', 'FAIL',
                f'Encontrados {negative_scores} placares negativos',
                count=negative_scores
            ))
        
        return self.results
    
    async def validate_referential_integrity(self) -> List[ValidationResult]:
        """Validar integridade referencial entre tabelas"""
        logger.info("🔗 Validando integridade referencial...")
        
        # 1. Fixtures → Leagues
        query = """
        SELECT COUNT(*) as count
        FROM fixtures f
        LEFT JOIN leagues l ON f.league_id = l.league_id
        WHERE f.league_id IS NOT NULL AND l.league_id IS NULL
        """
        response = self.supabase.rpc('execute_sql', {'query': query}).execute()
        
        if response.data and response.data[0]['count'] > 0:
            self.log_result(ValidationResult(
                'fixtures→leagues', 'foreign_key', 'FAIL',
                f"Encontradas {response.data[0]['count']} fixtures com league_id inválido",
                count=response.data[0]['count']
            ))
        else:
            self.log_result(ValidationResult(
                'fixtures→leagues', 'foreign_key', 'PASS',
                'Integridade referencial fixtures→leagues OK'
            ))
        
        # 2. Fixtures → Teams (Home)
        query = """
        SELECT COUNT(*) as count
        FROM fixtures f
        LEFT JOIN teams t ON f.home_team_id = t.team_id
        WHERE f.home_team_id IS NOT NULL AND t.team_id IS NULL
        """
        response = self.supabase.rpc('execute_sql', {'query': query}).execute()
        
        if response.data and response.data[0]['count'] > 0:
            self.log_result(ValidationResult(
                'fixtures→teams(home)', 'foreign_key', 'FAIL',
                f"Encontradas {response.data[0]['count']} fixtures com home_team_id inválido",
                count=response.data[0]['count']
            ))
        else:
            self.log_result(ValidationResult(
                'fixtures→teams(home)', 'foreign_key', 'PASS',
                'Integridade referencial fixtures→teams(home) OK'
            ))
        
        # 3. Match Events → Fixtures
        query = """
        SELECT COUNT(*) as count
        FROM match_events me
        LEFT JOIN fixtures f ON me.fixture_id = f.fixture_id
        WHERE f.fixture_id IS NULL
        """
        response = self.supabase.rpc('execute_sql', {'query': query}).execute()
        
        if response.data and response.data[0]['count'] > 0:
            self.log_result(ValidationResult(
                'match_events→fixtures', 'foreign_key', 'FAIL',
                f"Encontrados {response.data[0]['count']} eventos órfãos sem fixture",
                count=response.data[0]['count']
            ))
        else:
            self.log_result(ValidationResult(
                'match_events→fixtures', 'foreign_key', 'PASS',
                'Integridade referencial match_events→fixtures OK'
            ))
        
        return self.results
    
    async def validate_data_completeness(self) -> List[ValidationResult]:
        """Validar completude dos dados principais"""
        logger.info("📊 Validando completude dos dados...")
        
        # 1. Fixtures com dados completos
        query = """
        SELECT 
            COUNT(*) as total_fixtures,
            COUNT(CASE WHEN name IS NOT NULL THEN 1 END) as with_name,
            COUNT(CASE WHEN home_score IS NOT NULL AND away_score IS NOT NULL THEN 1 END) as with_scores,
            COUNT(CASE WHEN has_events = true THEN 1 END) as with_events,
            COUNT(CASE WHEN has_lineups = true THEN 1 END) as with_lineups,
            COUNT(CASE WHEN has_statistics = true THEN 1 END) as with_statistics
        FROM fixtures 
        WHERE state_id = 5 AND is_deleted = false
        """
        response = self.supabase.rpc('execute_sql', {'query': query}).execute()
        
        if response.data:
            data = response.data[0]
            total = data['total_fixtures']
            
            # Calcular percentuais de completude
            name_pct = (data['with_name'] / total * 100) if total > 0 else 0
            scores_pct = (data['with_scores'] / total * 100) if total > 0 else 0
            events_pct = (data['with_events'] / total * 100) if total > 0 else 0
            
            self.log_result(ValidationResult(
                'fixtures', 'data_completeness', 'PASS' if name_pct > 90 else 'WARNING',
                f'Completude dos dados: Names {name_pct:.1f}%, Scores {scores_pct:.1f}%, Events {events_pct:.1f}%',
                details=data
            ))
        
        return self.results
    
    async def validate_api_consistency(self) -> List[ValidationResult]:
        """Validar consistência com estrutura da API"""
        logger.info("🔄 Validando consistência com API Sportmonks...")
        
        # Verificar se temos todas as colunas essenciais da API
        required_fixture_columns = [
            'fixture_id', 'sport_id', 'league_id', 'season_id', 'stage_id',
            'round_id', 'state_id', 'venue_id', 'starting_at', 'starting_at_timestamp',
            'length', 'placeholder', 'has_odds', 'name', 'result_info', 'leg'
        ]
        
        # Verificar quais colunas existem
        query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'fixtures' AND table_schema = 'public'
        """
        response = self.supabase.rpc('execute_sql', {'query': query}).execute()
        
        if response.data:
            existing_columns = [row['column_name'] for row in response.data]
            missing_columns = [col for col in required_fixture_columns if col not in existing_columns]
            
            if not missing_columns:
                self.log_result(ValidationResult(
                    'fixtures', 'api_consistency', 'PASS',
                    'Todas as colunas essenciais da API estão presentes'
                ))
            else:
                self.log_result(ValidationResult(
                    'fixtures', 'api_consistency', 'WARNING',
                    f'Colunas faltantes da API: {", ".join(missing_columns)}',
                    details={'missing_columns': missing_columns}
                ))
        
        return self.results
    
    async def run_all_validations(self) -> Dict[str, Any]:
        """Executar todas as validações"""
        logger.info("🚀 Iniciando validação completa da base de dados...")
        start_time = datetime.now()
        
        # Limpar resultados anteriores
        self.results = []
        
        # Executar validações
        await self.validate_fixtures_integrity()
        await self.validate_referential_integrity()
        await self.validate_data_completeness()
        await self.validate_api_consistency()
        
        # Calcular estatísticas finais
        end_time = datetime.now()
        duration = end_time - start_time
        
        total_validations = len(self.results)
        passed = len([r for r in self.results if r.status == 'PASS'])
        failed = len([r for r in self.results if r.status == 'FAIL'])
        warnings = len([r for r in self.results if r.status == 'WARNING'])
        
        summary = {
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'total_validations': total_validations,
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'success_rate': (passed / total_validations * 100) if total_validations > 0 else 0,
            'results': [
                {
                    'table': r.table_name,
                    'type': r.validation_type,
                    'status': r.status,
                    'message': r.message,
                    'count': r.count,
                    'details': r.details
                }
                for r in self.results
            ]
        }
        
        # Log do resumo
        logger.info(f"✅ Validação concluída em {duration.total_seconds():.2f}s")
        logger.info(f"📊 Resultados: {passed} PASS, {failed} FAIL, {warnings} WARNING")
        logger.info(f"🎯 Taxa de sucesso: {summary['success_rate']:.1f}%")
        
        return summary
    
    def generate_report(self, output_file: str = None) -> str:
        """Gerar relatório de validação em markdown"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"validation_report_{timestamp}.md"
        
        # Calcular estatísticas
        total = len(self.results)
        passed = len([r for r in self.results if r.status == 'PASS'])
        failed = len([r for r in self.results if r.status == 'FAIL'])
        warnings = len([r for r in self.results if r.status == 'WARNING'])
        
        # Gerar conteúdo do relatório
        report = f"""# Relatório de Validação da Base de Dados BDFut

**Data:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Total de Validações:** {total}  
**Taxa de Sucesso:** {(passed/total*100):.1f}%

## 📊 Resumo dos Resultados

- ✅ **PASS:** {passed} validações
- ❌ **FAIL:** {failed} validações  
- ⚠️ **WARNING:** {warnings} validações

## 📋 Detalhes das Validações

"""
        
        # Agrupar por status
        for status in ['FAIL', 'WARNING', 'PASS']:
            status_results = [r for r in self.results if r.status == status]
            if status_results:
                emoji = {'FAIL': '❌', 'WARNING': '⚠️', 'PASS': '✅'}[status]
                report += f"\n### {emoji} {status}\n\n"
                
                for result in status_results:
                    report += f"**{result.table_name}** - {result.validation_type}\n"
                    report += f"- {result.message}\n"
                    if result.count is not None:
                        report += f"- Contagem: {result.count}\n"
                    if result.details:
                        report += f"- Detalhes: {result.details}\n"
                    report += "\n"
        
        # Recomendações
        if failed > 0:
            report += """
## 🚨 Ações Recomendadas

### Falhas Críticas
- Executar scripts de correção para problemas de integridade
- Verificar processo ETL para evitar dados inconsistentes
- Implementar validações no pipeline de dados

"""
        
        if warnings > 0:
            report += """
### Avisos
- Revisar dados com avisos para possíveis melhorias
- Considerar implementar validações adicionais
- Monitorar tendências de qualidade dos dados

"""
        
        report += """
## 📈 Próximos Passos

1. Corrigir todas as falhas críticas identificadas
2. Implementar monitoramento contínuo de qualidade
3. Automatizar validações no pipeline ETL
4. Criar alertas para problemas de integridade

---
*Relatório gerado automaticamente pelo DatabaseValidator*
"""
        
        # Salvar relatório
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"📄 Relatório salvo em: {output_file}")
        
        return report

async def main():
    """Função principal para executar validações"""
    validator = DatabaseValidator()
    
    try:
        # Executar todas as validações
        summary = await validator.run_all_validations()
        
        # Gerar relatório
        report_file = f"docs/management/reports/database_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        validator.generate_report(report_file)
        
        # Retornar resumo
        return summary
        
    except Exception as e:
        logger.error(f"❌ Erro durante validação: {e}")
        raise

if __name__ == "__main__":
    # Executar validações
    asyncio.run(main())
