#!/usr/bin/env python3
"""
Script para coletar TODOS os leagues da Sportmonks API com paginação completa
e ajustar a estrutura da tabela conforme especificado
"""

import os
import sys
import requests
import logging
import time
from datetime import datetime
from typing import List, Dict, Any

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client
from config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_all_leagues_with_pagination():
    """Buscar TODOS os leagues da API Sportmonks com paginação completa"""
    
    # Token válido fornecido pelo usuário
    api_token = "teW8DGJoAC7Gc6r4u0RrCMB4IR4iy8s22BF9mgOTtoNUu3UBMc58wulgveYB"
    
    all_leagues = []
    page = 1
    per_page = 25  # Máximo por página
    total_pages = None
    total_count = None
    
    logger.info("🌐 Iniciando coleta COMPLETA de leagues com paginação...")
    logger.info(f"🔑 Usando token válido: {api_token[:10]}...")
    
    while True:
        # URL da API Sportmonks para leagues com paginação
        url = f"https://api.sportmonks.com/v3/football/leagues?api_token={api_token}&include=&page={page}&per_page={per_page}"
        
        logger.info(f"📄 Página {page} - Fazendo requisição...")
        
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extrair dados da página atual
                leagues = data.get('data', [])
                pagination = data.get('pagination', {})
                
                logger.info(f"✅ Página {page}: {len(leagues)} leagues encontrados")
                
                # Mostrar alguns exemplos da página atual
                if leagues:
                    logger.info(f"   📋 Exemplos: {leagues[0].get('name')} (ID: {leagues[0].get('id')}), {leagues[1].get('name') if len(leagues) > 1 else 'N/A'}")
                
                # Adicionar leagues à lista total
                all_leagues.extend(leagues)
                
                # Verificar informações de paginação
                if total_pages is None:
                    # Tentar obter informações de paginação
                    current_page = pagination.get('current_page', page)
                    has_more = pagination.get('has_more', False)
                    next_page = pagination.get('next_page')
                    
                    logger.info(f"📊 Página atual: {current_page}")
                    logger.info(f"📊 Tem próxima página: {has_more}")
                    logger.info(f"📊 Próxima URL: {next_page}")
                
                # Verificar se há próxima página
                has_more = pagination.get('has_more', False)
                next_page = pagination.get('next_page')
                
                # Se não há próxima página ou next_page é None, parar
                if not has_more or not next_page:
                    logger.info("🏁 Última página alcançada")
                    break
                
                page += 1
                
                # Rate limiting - aguardar entre requisições
                time.sleep(0.5)
                
            elif response.status_code == 401:
                logger.error("❌ Token inválido - Erro 401 Unauthorized")
                logger.error(f"Resposta: {response.text}")
                return []
                
            elif response.status_code == 429:
                logger.warning("⚠️ Rate limit atingido - aguardando 60 segundos...")
                time.sleep(60)
                continue
                
            else:
                logger.error(f"❌ Erro na API: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na requisição: {e}")
            return []
        
        # Proteção contra loop infinito
        if page > 50:  # Máximo de 50 páginas (1250 leagues)
            logger.warning("⚠️ Limite de páginas atingido (50)")
            break
    
    logger.info(f"🎉 Coleta COMPLETA finalizada: {len(all_leagues)} leagues coletados")
    return all_leagues

def save_leagues_to_database(leagues_data):
    """Salvar leagues no banco de dados com estrutura ajustada"""
    
    logger.info("💾 Salvando leagues no banco de dados...")
    
    # Inicializar cliente Supabase
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
        return
    
    if not leagues_data:
        logger.error("❌ Nenhum league para salvar")
        return
    
    # Preparar dados para inserção com estrutura especificada
    leagues_to_save = []
    for league_item in leagues_data:
        league_data = {
            'sportmonks_id': league_item.get('id'),
            'sport_id': league_item.get('sport_id'),
            'country_id': league_item.get('country_id'),
            'name': league_item.get('name'),
            'active': league_item.get('active'),
            'short_code': league_item.get('short_code'),
            'image_path': league_item.get('image_path'),
            'type': league_item.get('type'),
            'sub_type': league_item.get('sub_type'),
            'last_played_at': league_item.get('last_played_at'),
            'category': league_item.get('category'),
            'has_jerseys': league_item.get('has_jerseys'),
            'created_at': datetime.utcnow().isoformat()
        }
        leagues_to_save.append(league_data)
    
    logger.info(f"📊 {len(leagues_to_save)} leagues preparados para inserção")
    
    # Salvar leagues em lotes para melhor performance
    batch_size = 50
    saved_count = 0
    skipped_count = 0
    error_count = 0
    
    for i in range(0, len(leagues_to_save), batch_size):
        batch = leagues_to_save[i:i + batch_size]
        
        try:
            # Tentar inserir lote completo
            supabase.table('leagues').insert(batch).execute()
            saved_count += len(batch)
            logger.info(f"✅ Lote {i//batch_size + 1}: {len(batch)} leagues salvos")
            
        except Exception as e:
            if 'duplicate key' in str(e).lower() or 'unique constraint' in str(e).lower():
                # Se houver conflito, salvar um por vez
                logger.info(f"⚠️ Conflito no lote {i//batch_size + 1}, salvando individualmente...")
                for league_data in batch:
                    try:
                        supabase.table('leagues').insert(league_data).execute()
                        saved_count += 1
                        logger.info(f"✅ League salvo: {league_data['name']} (ID: {league_data['sportmonks_id']})")
                    except Exception as e2:
                        if 'duplicate key' in str(e2).lower() or 'unique constraint' in str(e2).lower():
                            skipped_count += 1
                            logger.info(f"⏭️ League já existe: {league_data['name']} (ID: {league_data['sportmonks_id']})")
                        else:
                            error_count += 1
                            logger.warning(f"⚠️ Erro ao salvar league '{league_data['name']}': {e2}")
            else:
                error_count += len(batch)
                logger.warning(f"⚠️ Erro no lote {i//batch_size + 1}: {e}")
        
        # Aguardar entre lotes para evitar rate limiting
        time.sleep(0.2)
    
    logger.info(f"✅ {saved_count} leagues novos salvos")
    logger.info(f"⏭️ {skipped_count} leagues já existiam")
    logger.info(f"❌ {error_count} leagues com erro")
    
    return saved_count, skipped_count, error_count

def generate_final_report():
    """Gerar relatório final da tabela leagues"""
    
    logger.info("📊 Gerando relatório final...")
    
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        
        # Contagem total
        response = supabase.table('leagues').select('*', count='exact').execute()
        total_count = response.count
        logger.info(f"📊 Total de leagues na tabela: {total_count}")
        
        # Estatísticas por país
        logger.info("\n📈 Estatísticas por país:")
        country_stats = supabase.table('leagues').select('country_id').not_.is_('country_id', 'null').execute()
        country_counts = {}
        for league in country_stats.data:
            cid = league['country_id']
            country_counts[cid] = country_counts.get(cid, 0) + 1
        
        # Top 10 países com mais ligas
        top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for country_id, count in top_countries:
            logger.info(f"   • País ID {country_id}: {count} ligas")
        
        # Leagues ativos vs inativos
        active_leagues = supabase.table('leagues').select('sportmonks_id,name,active').eq('active', True).execute()
        inactive_leagues = supabase.table('leagues').select('sportmonks_id,name,active').eq('active', False).execute()
        logger.info(f"\n✅ Leagues ativos: {len(active_leagues.data)}")
        logger.info(f"❌ Leagues inativos: {len(inactive_leagues.data)}")
        
        # Leagues com imagens
        with_images = supabase.table('leagues').select('sportmonks_id,name,image_path').not_.is_('image_path', 'null').execute()
        logger.info(f"🖼️ Leagues com imagens: {len(with_images.data)}")
        
        # Leagues com códigos curtos
        with_short_codes = supabase.table('leagues').select('sportmonks_id,name,short_code').not_.is_('short_code', 'null').execute()
        logger.info(f"🔢 Leagues com códigos curtos: {len(with_short_codes.data)}")
        
        # Exemplos de leagues por tipo
        logger.info("\n📋 Exemplos de leagues:")
        examples = supabase.table('leagues').select('sportmonks_id,name,short_code,type,category,active').limit(10).execute()
        for league in examples.data:
            status = "✅ Ativo" if league['active'] else "❌ Inativo"
            logger.info(f"   • ID {league['sportmonks_id']}: {league['name']} ({league['short_code']}) - {league['type']} - {league['category']} - {status}")
        
        # Top 10 leagues mais populares (por ID mais baixo)
        logger.info("\n🏆 Top 10 leagues (IDs mais baixos):")
        top_leagues = supabase.table('leagues').select('sportmonks_id,name,short_code,type,category').order('sportmonks_id').limit(10).execute()
        for league in top_leagues.data:
            logger.info(f"   • ID {league['sportmonks_id']}: {league['name']} ({league['short_code']}) - {league['type']} - {league['category']}")
                
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 COLETANDO TODOS OS LEAGUES DA SPORTMONKS API COM PAGINAÇÃO COMPLETA")
    logger.info("=" * 80)
    
    # Coletar todos os leagues com paginação completa
    leagues_data = get_all_leagues_with_pagination()
    
    if leagues_data:
        # Salvar no banco de dados
        saved, skipped, errors = save_leagues_to_database(leagues_data)
        
        # Gerar relatório final
        generate_final_report()
        
        logger.info("=" * 80)
        logger.info("✅ COLETA COMPLETA DE LEAGUES FINALIZADA!")
        logger.info(f"📊 Salvos: {saved}, Já existiam: {skipped}, Erros: {errors}")
        logger.info("=" * 80)
    else:
        logger.error("❌ Falha na coleta completa de leagues")

if __name__ == "__main__":
    main()
