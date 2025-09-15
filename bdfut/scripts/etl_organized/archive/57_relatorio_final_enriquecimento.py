#!/usr/bin/env python3
"""
Script para gerar relatório final consolidado do enriquecimento das tabelas
"""

import os
import sys
import logging
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/Users/mhbutzke/Documents/BDFut/bdfut/bdfut/logs/relatorio_final_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_supabase_client():
    """Obter cliente Supabase"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar configurados no .env")
    
    return create_client(supabase_url, supabase_key)

def gerar_relatorio_completo(supabase):
    """Gerar relatório completo do estado atual das tabelas"""
    logger.info("=" * 100)
    logger.info("📊 RELATÓRIO FINAL CONSOLIDADO - ENRIQUECIMENTO DAS TABELAS SUPABASE")
    logger.info("=" * 100)
    
    try:
        # Contar registros em todas as tabelas
        all_tables = [
            'leagues', 'seasons', 'teams', 'fixtures', 
            'match_events', 'match_statistics', 'match_lineups',
            'countries', 'states', 'types', 'venues', 
            'referees', 'players', 'coaches', 'stages'
        ]
        
        total_records = 0
        logger.info("\n📋 CONTAGEM FINAL DE REGISTROS POR TABELA:")
        logger.info("=" * 80)
        
        table_stats = {}
        for table in all_tables:
            try:
                response = supabase.table(table).select('*', count='exact').execute()
                count = response.count
                total_records += count
                table_stats[table] = count
                status = "✅" if count > 0 else "❌"
                logger.info(f"{status} {table:20}: {count:>8,} registros")
            except Exception as e:
                logger.warning(f"⚠️ {table:20}: erro ao contar - {e}")
                table_stats[table] = 0
        
        logger.info("=" * 80)
        logger.info(f"📊 TOTAL GERAL: {total_records:>8,} registros")
        
        # Análise por categoria
        logger.info("\n📈 ANÁLISE POR CATEGORIA:")
        logger.info("=" * 80)
        
        # Dados principais
        main_data = table_stats.get('leagues', 0) + table_stats.get('seasons', 0) + table_stats.get('teams', 0)
        logger.info(f"🏆 Dados Principais (leagues + seasons + teams): {main_data:,}")
        
        # Partidas e eventos
        match_data = table_stats.get('fixtures', 0) + table_stats.get('match_events', 0) + table_stats.get('match_statistics', 0) + table_stats.get('match_lineups', 0)
        logger.info(f"⚽ Partidas e Eventos (fixtures + events + stats + lineups): {match_data:,}")
        
        # Dados de referência
        reference_data = table_stats.get('countries', 0) + table_stats.get('states', 0) + table_stats.get('types', 0) + table_stats.get('venues', 0) + table_stats.get('referees', 0) + table_stats.get('players', 0) + table_stats.get('coaches', 0)
        logger.info(f"📚 Dados de Referência (countries + states + types + venues + referees + players + coaches): {reference_data:,}")
        
        # Estatísticas específicas
        logger.info("\n📊 ESTATÍSTICAS ESPECÍFICAS:")
        logger.info("=" * 80)
        
        # Fixtures por status
        try:
            fixtures_status = supabase.table('fixtures').select('status').execute()
            status_counts = {}
            for fixture in fixtures_status.data:
                status = fixture.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            logger.info("⚽ Fixtures por status:")
            for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   • {status:15}: {count:>6,} partidas")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao analisar status das fixtures: {e}")
        
        # Players por posição
        try:
            players_pos = supabase.table('players').select('position_name').not_.is_('position_name', 'null').execute()
            pos_counts = {}
            for player in players_pos.data:
                pos = player.get('position_name', 'unknown')
                pos_counts[pos] = pos_counts.get(pos, 0) + 1
            
            logger.info("\n⚽ Players por posição:")
            for pos, count in sorted(pos_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   • {pos:15}: {count:>6,} jogadores")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao analisar posições dos jogadores: {e}")
        
        # Countries por continente
        try:
            countries_continent = supabase.table('countries').select('continent_id').not_.is_('continent_id', 'null').execute()
            continent_counts = {}
            continent_names = {1: "Europa", 2: "América do Norte", 4: "América do Sul", 3: "Ásia", 5: "África", 6: "Oceania"}
            
            for country in countries_continent.data:
                cid = country.get('continent_id')
                continent_counts[cid] = continent_counts.get(cid, 0) + 1
            
            logger.info("\n🌍 Countries por continente:")
            for cid, count in sorted(continent_counts.items(), key=lambda x: x[1], reverse=True):
                continent_name = continent_names.get(cid, f"Continente {cid}")
                logger.info(f"   • {continent_name:15}: {count:>6,} países")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao analisar continentes: {e}")
        
        # Types por categoria
        try:
            types_model = supabase.table('types').select('model_type').not_.is_('model_type', 'null').execute()
            model_counts = {}
            for type_item in types_model.data:
                model = type_item.get('model_type', 'unknown')
                model_counts[model] = model_counts.get(model, 0) + 1
            
            logger.info("\n📊 Types por categoria:")
            for model, count in sorted(model_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   • {model:15}: {count:>6,} tipos")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao analisar tipos: {e}")
        
        # Venues por capacidade
        try:
            venues_capacity = supabase.table('venues').select('capacity').not_.is_('capacity', 'null').execute()
            capacity_ranges = {
                'Pequeno (< 20k)': 0,
                'Médio (20k-50k)': 0,
                'Grande (50k-80k)': 0,
                'Muito Grande (> 80k)': 0
            }
            
            for venue in venues_capacity.data:
                capacity = venue.get('capacity', 0)
                if capacity < 20000:
                    capacity_ranges['Pequeno (< 20k)'] += 1
                elif capacity < 50000:
                    capacity_ranges['Médio (20k-50k)'] += 1
                elif capacity < 80000:
                    capacity_ranges['Grande (50k-80k)'] += 1
                else:
                    capacity_ranges['Muito Grande (> 80k)'] += 1
            
            logger.info("\n🏟️ Venues por capacidade:")
            for range_name, count in capacity_ranges.items():
                logger.info(f"   • {range_name:15}: {count:>6,} estádios")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao analisar capacidades dos estádios: {e}")
        
        # Resumo de qualidade dos dados
        logger.info("\n🎯 RESUMO DE QUALIDADE DOS DADOS:")
        logger.info("=" * 80)
        
        # Tabelas completamente populadas
        populated_tables = [table for table, count in table_stats.items() if count > 0]
        empty_tables = [table for table, count in table_stats.items() if count == 0]
        
        logger.info(f"✅ Tabelas populadas: {len(populated_tables)}/{len(all_tables)}")
        logger.info(f"❌ Tabelas vazias: {len(empty_tables)}/{len(all_tables)}")
        
        if empty_tables:
            logger.info(f"   Tabelas vazias: {', '.join(empty_tables)}")
        
        # Tabelas com muitos dados
        large_tables = [table for table, count in table_stats.items() if count > 1000]
        logger.info(f"📊 Tabelas com muitos dados (>1000): {len(large_tables)}")
        for table in large_tables:
            logger.info(f"   • {table}: {table_stats[table]:,} registros")
        
        # Recomendações
        logger.info("\n💡 RECOMENDAÇÕES:")
        logger.info("=" * 80)
        
        if table_stats.get('referees', 0) < 50:
            logger.info("🟨 Considerar enriquecer mais árbitros da API")
        
        if table_stats.get('coaches', 0) < 50:
            logger.info("👨‍💼 Considerar enriquecer mais técnicos da API")
        
        if table_stats.get('venues', 0) < 200:
            logger.info("🏟️ Considerar enriquecer mais estádios da API")
        
        if table_stats.get('players', 0) < 1000:
            logger.info("⚽ Considerar enriquecer mais jogadores da API")
        
        logger.info("\n🚀 PRÓXIMOS PASSOS SUGERIDOS:")
        logger.info("=" * 80)
        logger.info("1. Executar sincronização incremental diária")
        logger.info("2. Implementar monitoramento de qualidade dos dados")
        logger.info("3. Criar dashboards para visualização dos dados")
        logger.info("4. Implementar alertas para dados faltantes")
        logger.info("5. Considerar enriquecimento com dados históricos")
        
        logger.info("\n" + "=" * 100)
        logger.info("🎉 RELATÓRIO FINAL CONCLUÍDO!")
        logger.info("=" * 100)
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {str(e)}")

def main():
    """Função principal"""
    
    logger.info("🚀 Gerando relatório final consolidado...")
    
    try:
        # Obter cliente Supabase
        supabase = get_supabase_client()
        logger.info("✅ Cliente Supabase inicializado com sucesso")
        
        # Gerar relatório completo
        gerar_relatorio_completo(supabase)
        
    except Exception as e:
        logger.error(f"❌ Erro no processo principal: {str(e)}")
        raise

if __name__ == "__main__":
    main()
