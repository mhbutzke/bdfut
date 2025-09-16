#!/usr/bin/env python3
"""
05_quality_checks_04_automated_validation.py
============================================

Script de verificação automática de qualidade de dados
com relatórios detalhados e sistema de alertas.

DEPENDÊNCIAS:
- Todas as tasks ETL anteriores concluídas
- Sistema de metadados ETL funcionando
- Cache Redis operacional

FUNCIONALIDADE:
- Validações de integridade referencial
- Detecção de dados duplicados
- Validação de campos obrigatórios
- Relatórios automáticos de qualidade
- Sistema de alertas para problemas
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Optional

# Adicionar o diretório bdfut ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from bdfut.core.data_quality import DataQualityManager, QualityAlertsManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'bdfut/logs/data_quality_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_complete_quality_check(tables: Optional[List[str]] = None) -> bool:
    """
    Executa verificação completa de qualidade
    
    Args:
        tables: Lista de tabelas (None = todas)
        
    Returns:
        True se verificação foi bem-sucedida
    """
    logger.info("🔍 VERIFICAÇÃO COMPLETA DE QUALIDADE DE DADOS")
    logger.info("=" * 60)
    
    try:
        # Inicializar gerenciadores
        quality_manager = DataQualityManager()
        alerts_manager = QualityAlertsManager(quality_manager)
        
        logger.info("✅ Gerenciadores inicializados")
        
        # Executar verificações
        logger.info("🔄 Executando verificações de qualidade...")
        results = quality_manager.run_all_quality_checks(tables=tables)
        
        # Gerar relatório
        logger.info("📊 Gerando relatório de qualidade...")
        report_text = quality_manager.generate_quality_report(results)
        
        # Salvar relatório
        report_file = f"bdfut/logs/quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logger.info(f"💾 Relatório salvo: {report_file}")
        
        # Verificar alertas
        logger.info("🚨 Verificando condições de alerta...")
        alerts = alerts_manager.check_alert_conditions(results)
        
        if alerts:
            logger.warning(f"⚠️ {len(alerts)} alertas gerados")
            alerts_manager.send_alerts(alerts)
        else:
            logger.info("✅ Nenhum alerta necessário")
        
        # Mostrar resumo
        print("\n" + "=" * 60)
        print("📊 RESUMO DA VERIFICAÇÃO DE QUALIDADE")
        print("=" * 60)
        print(f"🎯 Score Geral: {results['overall_score']:.1%}")
        print(f"📊 Tabelas: {results['tables_checked']}")
        print(f"✅ Passou: {results['passed_checks']}/{results['total_checks']}")
        print(f"❌ Falhou: {results['failed_checks']}")
        print(f"🚨 Críticos: {results['critical_issues']}")
        print(f"❌ Erros: {results['errors']}")
        print(f"⚠️ Warnings: {results['warnings']}")
        
        if results['recommendations']:
            print(f"\n💡 PRINCIPAIS RECOMENDAÇÕES:")
            for i, rec in enumerate(results['recommendations'][:3], 1):
                print(f"  {i}. {rec}")
        
        print(f"\n📄 Relatório completo: {report_file}")
        
        # Critérios de sucesso
        success = (
            results['overall_score'] >= 0.8 and
            results['critical_issues'] == 0 and
            results['errors'] < 10
        )
        
        if success:
            print("\n🎉 VERIFICAÇÃO DE QUALIDADE APROVADA!")
        else:
            print("\n⚠️ PROBLEMAS DE QUALIDADE DETECTADOS")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erro durante verificação de qualidade: {e}")
        print(f"❌ Erro durante verificação: {e}")
        return False

def run_critical_checks_only() -> bool:
    """
    Executa apenas verificações críticas (mais rápido)
    
    Returns:
        True se verificações críticas passaram
    """
    logger.info("🚨 VERIFICAÇÕES CRÍTICAS DE QUALIDADE")
    logger.info("=" * 50)
    
    try:
        quality_manager = DataQualityManager()
        
        # Executar apenas verificações críticas
        results = quality_manager.run_critical_checks_only()
        
        # Verificar se há problemas críticos
        critical_issues = results.get('critical_issues', 0)
        errors = results.get('errors', 0)
        
        print(f"🎯 Score Crítico: {results['overall_score']:.1%}")
        print(f"🚨 Problemas Críticos: {critical_issues}")
        print(f"❌ Erros: {errors}")
        
        success = critical_issues == 0 and errors < 5
        
        if success:
            print("✅ VERIFICAÇÕES CRÍTICAS APROVADAS")
        else:
            print("❌ PROBLEMAS CRÍTICOS DETECTADOS")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erro durante verificações críticas: {e}")
        return False

def run_quality_trends_analysis() -> bool:
    """
    Executa análise de tendências de qualidade
    
    Returns:
        True se análise foi bem-sucedida
    """
    logger.info("📈 ANÁLISE DE TENDÊNCIAS DE QUALIDADE")
    logger.info("=" * 50)
    
    try:
        quality_manager = DataQualityManager()
        
        # Analisar tendências
        trends = quality_manager.get_quality_trends(days=7)
        
        if 'error' not in trends:
            print(f"📊 Verificações executadas (7 dias): {trends['quality_checks_run']}")
            print(f"📈 Score médio: {trends['average_score']:.1%}")
            print(f"📊 Tendência: {trends['score_trend']}")
            
            if trends['recommendations']:
                print(f"💡 Recomendações:")
                for rec in trends['recommendations']:
                    print(f"  • {rec}")
            
            return True
        else:
            print(f"❌ Erro na análise: {trends['error']}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro durante análise de tendências: {e}")
        return False

def main():
    """Função principal com opções de execução"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de Verificação de Qualidade de Dados")
    parser.add_argument('--mode', choices=['complete', 'critical', 'trends'], 
                       default='complete', help='Modo de verificação')
    parser.add_argument('--tables', nargs='*', 
                       help='Tabelas específicas para verificar')
    
    args = parser.parse_args()
    
    print(f"🔍 SISTEMA DE VERIFICAÇÃO DE QUALIDADE")
    print(f"📋 Modo: {args.mode.upper()}")
    if args.tables:
        print(f"📊 Tabelas: {', '.join(args.tables)}")
    print("=" * 50)
    
    try:
        if args.mode == 'complete':
            # Verificação completa
            success = run_complete_quality_check(tables=args.tables)
        elif args.mode == 'critical':
            # Apenas verificações críticas
            success = run_critical_checks_only()
        elif args.mode == 'trends':
            # Análise de tendências
            success = run_quality_trends_analysis()
        else:
            logger.error(f"❌ Modo inválido: {args.mode}")
            return False
        
        if success:
            print(f"\n🎉 VERIFICAÇÃO DE QUALIDADE CONCLUÍDA COM SUCESSO!")
        else:
            print(f"\n⚠️ VERIFICAÇÃO CONCLUÍDA COM PROBLEMAS")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        print(f"❌ Erro fatal: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {str(e)}")
        sys.exit(1)
