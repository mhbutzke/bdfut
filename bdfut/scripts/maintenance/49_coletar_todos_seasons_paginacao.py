#!/usr/bin/env python3
"""
Script para coletar TODOS os seasons da Sportmonks API com paginação completa
e enriquecer a tabela seasons no Supabase.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config import Config
from src.sportmonks_client import SportmonksClient
from src.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def collect_all_seasons_with_pagination() -> List[Dict[str, Any]]:
    """
    Coleta todos os seasons da Sportmonks API com paginação completa.
    """
    logger.info("=" * 80)
    logger.info("🚀 COLETANDO TODOS OS SEASONS DA SPORTMONKS API COM PAGINAÇÃO")
    logger.info("=" * 80)
    
    # Inicializar cliente Sportmonks
    sportmonks = SportmonksClient()
    
    all_seasons = []
    page = 1
    total_pages = 1
    
    logger.info("📡 Iniciando coleta com paginação completa...")
    
    while True:
        try:
            logger.info(f"📄 Coletando página {page}...")
            
            # Fazer requisição com paginação
            response = sportmonks._make_request(
                '/seasons',
                {
                    'include': '',
                    'page': page,
                    'per_page': 25
                }
            )
            
            if not response:
                logger.error(f"❌ Resposta vazia na página {page}")
                break
                
            # Extrair dados da resposta
            seasons_data = response.get('data', [])
            pagination = response.get('pagination', {})
            
            logger.info(f"✅ Página {page}: {len(seasons_data)} seasons coletados")
            
            # Adicionar seasons à lista
            all_seasons.extend(seasons_data)
            
            # Verificar se há mais páginas
            has_more = pagination.get('has_more', False)
            next_page = pagination.get('next_page')
            
            logger.info(f"📊 Tem mais páginas: {has_more}")
            if next_page:
                logger.info(f"🔗 Próxima página: {next_page}")
            
            # Se não há mais páginas, parar
            if not has_more:
                logger.info("🏁 Última página alcançada")
                break
                
            page += 1
            
            # Rate limiting - aguardar entre requisições
            import time
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"❌ Erro na página {page}: {str(e)}")
            break
    
    logger.info(f"🎉 Coleta finalizada! Total de seasons: {len(all_seasons)}")
    return all_seasons

def save_seasons_to_json(seasons: List[Dict[str, Any]]) -> str:
    """
    Salva os seasons coletados em um arquivo JSON.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"seasons_data_{timestamp}.json"
    
    logger.info(f"💾 Salvando {len(seasons)} seasons em {filename}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(seasons, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"✅ Seasons salvos em {filename}")
    return filename

def enrich_seasons_table(seasons: List[Dict[str, Any]]) -> None:
    """
    Enriquece a tabela seasons no Supabase com os dados coletados.
    """
    logger.info("=" * 80)
    logger.info("💾 ENRIQUECENDO TABELA SEASONS NO SUPABASE")
    logger.info("=" * 80)
    
    # Inicializar cliente Supabase
    supabase = SupabaseClient()
    
    logger.info("✅ Cliente Supabase inicializado")
    
    # Preparar dados para inserção
    seasons_to_insert = []
    
    for season in seasons:
        try:
            # Mapear dados da API para a estrutura da tabela
            season_data = {
                'sportmonks_id': season.get('id'),
                'sport_id': season.get('sport_id'),
                'country_id': season.get('country_id'),
                'league_id': season.get('league_id'),
                'name': season.get('name'),
                'starting_at': season.get('starting_at'),
                'ending_at': season.get('ending_at'),
                'finished': season.get('finished', False),
                'pending': season.get('pending', False),
                'is_current': season.get('is_current', False),
                'current_round_id': season.get('current_round_id'),
                'current_stage_id': season.get('current_stage_id'),
                'winner_id': season.get('winner_id'),
                'created_at': datetime.utcnow().isoformat()
            }
            
            seasons_to_insert.append(season_data)
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar season {season.get('id', 'unknown')}: {str(e)}")
            continue
    
    logger.info(f"📊 {len(seasons_to_insert)} seasons preparados para inserção")
    
    # Inserir em lotes
    batch_size = 50
    total_inserted = 0
    total_updated = 0
    total_errors = 0
    
    for i in range(0, len(seasons_to_insert), batch_size):
        batch = seasons_to_insert[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        try:
            logger.info(f"📦 Processando lote {batch_num} ({len(batch)} seasons)...")
            
            # Usar upsert para evitar duplicatas
            result = supabase.client.table('seasons').upsert(
                batch, 
                on_conflict='sportmonks_id'
            ).execute()
            
            if result.data:
                inserted_count = len([s for s in batch if s.get('sportmonks_id')])
                total_inserted += inserted_count
                logger.info(f"✅ Lote {batch_num}: {inserted_count} seasons salvos")
            else:
                logger.warning(f"⚠️ Lote {batch_num}: Nenhum season salvo")
                
        except Exception as e:
            logger.error(f"❌ Erro no lote {batch_num}: {str(e)}")
            total_errors += len(batch)
    
    # Relatório final
    logger.info("=" * 80)
    logger.info("📊 RELATÓRIO FINAL DE SEASONS")
    logger.info("=" * 80)
    logger.info(f"✅ Seasons novos salvos: {total_inserted}")
    logger.info(f"⏭️ Seasons já existiam: {total_updated}")
    logger.info(f"❌ Seasons com erro: {total_errors}")
    
    # Estatísticas adicionais
    try:
        # Contar total na tabela
        count_result = supabase.client.table('seasons').select('*', count='exact').execute()
        total_in_table = count_result.count if count_result.count else 0
        logger.info(f"📊 Total de seasons na tabela: {total_in_table}")
        
        # Estatísticas por liga
        leagues_result = supabase.client.table('seasons').select('league_id').execute()
        if leagues_result.data:
            league_counts = {}
            for season in leagues_result.data:
                league_id = season.get('league_id')
                if league_id:
                    league_counts[league_id] = league_counts.get(league_id, 0) + 1
            
            logger.info("\n📈 Estatísticas por liga:")
            sorted_leagues = sorted(league_counts.items(), key=lambda x: x[1], reverse=True)[:15]
            for league_id, count in sorted_leagues:
                logger.info(f"   • Liga ID {league_id}: {count} seasons")
        
        # Seasons ativos vs finalizados
        current_result = supabase.client.table('seasons').select('sportmonks_id,name,is_current').eq('is_current', True).execute()
        finished_result = supabase.client.table('seasons').select('sportmonks_id,name,finished').eq('finished', True).execute()
        
        logger.info(f"\n✅ Seasons ativos: {len(current_result.data) if current_result.data else 0}")
        logger.info(f"🏁 Seasons finalizados: {len(finished_result.data) if finished_result.data else 0}")
        
        # Exemplos de seasons
        examples_result = supabase.client.table('seasons').select('sportmonks_id,name,league_id,finished,is_current').limit(10).execute()
        if examples_result.data:
            logger.info("\n📋 Exemplos de seasons:")
            for season in examples_result.data:
                status = "🔄 Ativo" if season.get('is_current') else ("✅ Finalizado" if season.get('finished') else "⏳ Em andamento")
                logger.info(f"   • ID {season.get('sportmonks_id')}: {season.get('name')} - Liga {season.get('league_id')} - {status}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar estatísticas: {str(e)}")
    
    logger.info("=" * 80)
    logger.info("✅ ENRIQUECIMENTO DE SEASONS FINALIZADO!")
    logger.info("=" * 80)

def main():
    """
    Função principal.
    """
    try:
        # Coletar todos os seasons
        seasons = collect_all_seasons_with_pagination()
        
        if not seasons:
            logger.error("❌ Nenhum season foi coletado!")
            return
        
        # Salvar em JSON
        json_file = save_seasons_to_json(seasons)
        
        # Enriquecer tabela
        enrich_seasons_table(seasons)
        
        logger.info("🎉 Processo completo finalizado com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {str(e)}")
        raise

if __name__ == "__main__":
    main()
