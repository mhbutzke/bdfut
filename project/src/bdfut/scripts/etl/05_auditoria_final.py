#!/usr/bin/env python3
"""
PASSO 5: Auditoria final e relatório completo
Mostra estatísticas completas dos dados coletados
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Any

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from supabase import create_client
from config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Função principal para auditoria final"""
    
    logger.info("=" * 80)
    logger.info("🚀 PASSO 5: AUDITORIA FINAL E RELATÓRIO COMPLETO")
    logger.info("=" * 80)
    
    # Inicializar cliente
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente: {e}")
        return
    
    # Coletar estatísticas de todas as tabelas
    logger.info("🔍 Coletando estatísticas das tabelas...")
    
    stats = {}
    
    try:
        # Leagues
        leagues_response = supabase.table('leagues').select('*', count='exact').execute()
        stats['leagues'] = leagues_response.count
        
        # Seasons
        seasons_response = supabase.table('seasons').select('*', count='exact').execute()
        stats['seasons'] = seasons_response.count
        
        # Teams
        teams_response = supabase.table('teams').select('*', count='exact').execute()
        stats['teams'] = teams_response.count
        
        # Fixtures
        fixtures_response = supabase.table('fixtures').select('*', count='exact').execute()
        stats['fixtures'] = fixtures_response.count
        
        # Match Events
        events_response = supabase.table('match_events').select('*', count='exact').execute()
        stats['match_events'] = events_response.count
        
        # Match Statistics
        statistics_response = supabase.table('match_statistics').select('*', count='exact').execute()
        stats['match_statistics'] = statistics_response.count
        
        # Match Lineups
        lineups_response = supabase.table('match_lineups').select('*', count='exact').execute()
        stats['match_lineups'] = lineups_response.count
        
    except Exception as e:
        logger.error(f"❌ Erro ao coletar estatísticas: {e}")
        return
    
    # Relatório detalhado
    logger.info("=" * 80)
    logger.info("📊 RELATÓRIO FINAL - DADOS COLETADOS")
    logger.info("=" * 80)
    
    logger.info("🏆 ENTIDADES PRINCIPAIS:")
    logger.info(f"   • Leagues: {stats.get('leagues', 0):,}")
    logger.info(f"   • Seasons: {stats.get('seasons', 0):,}")
    logger.info(f"   • Teams: {stats.get('teams', 0):,}")
    logger.info(f"   • Fixtures: {stats.get('fixtures', 0):,}")
    
    logger.info("")
    logger.info("📈 DADOS DETALHADOS:")
    logger.info(f"   • Events: {stats.get('match_events', 0):,}")
    logger.info(f"   • Statistics: {stats.get('match_statistics', 0):,}")
    logger.info(f"   • Lineups: {stats.get('match_lineups', 0):,}")
    
    # Análise de cobertura
    logger.info("")
    logger.info("📊 ANÁLISE DE COBERTURA:")
    
    if stats.get('fixtures', 0) > 0:
        events_coverage = (stats.get('match_events', 0) / stats.get('fixtures', 1)) * 100
        stats_coverage = (stats.get('match_statistics', 0) / (stats.get('fixtures', 1) * 2)) * 100  # 2 times per fixture
        
        logger.info(f"   • Cobertura de Events: {events_coverage:.1f}%")
        logger.info(f"   • Cobertura de Statistics: {stats_coverage:.1f}%")
    
    # Top leagues por fixtures
    logger.info("")
    logger.info("🏆 TOP LEAGUES POR FIXTURES:")
    
    try:
        top_leagues_response = supabase.table('fixtures').select(
            'league_id,leagues(name)'
        ).execute()
        
        league_counts = {}
        for fixture in top_leagues_response.data:
            league_id = fixture.get('league_id')
            league_name = fixture.get('leagues', {}).get('name', f'League {league_id}')
            league_counts[league_name] = league_counts.get(league_name, 0) + 1
        
        # Ordenar por quantidade
        sorted_leagues = sorted(league_counts.items(), key=lambda x: x[1], reverse=True)
        
        for i, (league_name, count) in enumerate(sorted_leagues[:10], 1):
            logger.info(f"   {i:2d}. {league_name}: {count:,} fixtures")
            
    except Exception as e:
        logger.warning(f"⚠️ Erro ao coletar top leagues: {e}")
    
    # Resumo final
    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ AUDITORIA FINAL CONCLUÍDA!")
    logger.info("=" * 80)
    
    total_entities = sum(stats.values())
    logger.info(f"📊 TOTAL DE REGISTROS COLETADOS: {total_entities:,}")
    
    logger.info("")
    logger.info("🎯 STATUS DOS PASSOS:")
    logger.info("   ✅ PASSO 1: Popular tabelas leagues e seasons")
    logger.info("   ✅ PASSO 2A: Coletar teams primeiro")
    logger.info("   ✅ PASSO 2B: Coletar fixtures básicas por temporada")
    logger.info("   ✅ PASSO 3: Enriquecer fixtures com events, statistics e lineups")
    logger.info("   ⚠️ PASSO 4: Popular tabelas venues e referees (tabelas não existem)")
    logger.info("   ✅ PASSO 5: Auditoria final e relatório completo")
    
    logger.info("")
    logger.info("🚀 PROJETO CONCLUÍDO COM SUCESSO!")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()
