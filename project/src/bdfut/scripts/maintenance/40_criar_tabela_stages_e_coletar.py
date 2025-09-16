#!/usr/bin/env python3
"""
Script para criar tabela stages e coletar TODOS os dados da Sportmonks API com paginação completa
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

def create_stages_table():
    """Criar tabela stages no banco de dados"""
    
    logger.info("🔧 Criando tabela stages...")
    
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
        
        # SQL para criar a tabela stages
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS stages (
            id SERIAL PRIMARY KEY,
            sportmonks_id INTEGER UNIQUE NOT NULL,
            sport_id INTEGER,
            country_id INTEGER,
            league_id INTEGER,
            season_id INTEGER,
            type_id INTEGER,
            name VARCHAR(255),
            short_code VARCHAR(10),
            sort_order INTEGER,
            finished BOOLEAN DEFAULT FALSE,
            is_current BOOLEAN DEFAULT FALSE,
            starting_at TIMESTAMP,
            ending_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Executar SQL via RPC (se disponível) ou usar método alternativo
        try:
            result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
            logger.info("✅ Tabela stages criada via RPC")
        except Exception as e:
            logger.warning(f"⚠️ RPC não disponível: {e}")
            logger.info("📋 SQL para criar tabela stages:")
            logger.info(create_table_sql)
            logger.info("💡 Execute este SQL manualmente no Supabase Dashboard")
        
        # Verificar se a tabela foi criada
        try:
            result = supabase.table('stages').select('*').limit(1).execute()
            logger.info("✅ Tabela stages existe e está acessível")
        except Exception as e:
            logger.warning(f"⚠️ Tabela stages pode não existir ainda: {e}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabela stages: {e}")

def get_all_stages_with_pagination():
    """Buscar TODOS os stages da API Sportmonks com paginação completa"""
    
    # Token válido fornecido pelo usuário
    api_token = "teW8DGJoAC7Gc6r4u0RrCMB4IR4iy8s22BF9mgOTtoNUu3UBMc58wulgveYB"
    
    all_stages = []
    page = 1
    per_page = 25  # Máximo por página
    
    logger.info("🌐 Iniciando coleta COMPLETA de stages com paginação...")
    logger.info(f"🔑 Usando token válido: {api_token[:10]}...")
    
    while True:
        # URL da API Sportmonks para stages com paginação
        url = f"https://api.sportmonks.com/v3/football/stages?api_token={api_token}&include=&page={page}&per_page={per_page}"
        
        logger.info(f"📄 Página {page} - Fazendo requisição...")
        
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extrair dados da página atual
                stages = data.get('data', [])
                pagination = data.get('pagination', {})
                
                logger.info(f"✅ Página {page}: {len(stages)} stages encontrados")
                
                # Mostrar alguns exemplos da página atual
                if stages:
                    logger.info(f"   📋 Exemplos: {stages[0].get('name')} (ID: {stages[0].get('id')}), {stages[1].get('name') if len(stages) > 1 else 'N/A'}")
                
                # Adicionar stages à lista total
                all_stages.extend(stages)
                
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
        if page > 50:  # Máximo de 50 páginas (1250 stages)
            logger.warning("⚠️ Limite de páginas atingido (50)")
            break
    
    logger.info(f"🎉 Coleta COMPLETA finalizada: {len(all_stages)} stages coletados")
    return all_stages

def save_stages_to_database(stages_data):
    """Salvar stages no banco de dados"""
    
    logger.info("💾 Salvando stages no banco de dados...")
    
    # Inicializar cliente Supabase
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
        return
    
    if not stages_data:
        logger.error("❌ Nenhum stage para salvar")
        return
    
    # Preparar dados para inserção
    stages_to_save = []
    for stage_item in stages_data:
        stage_data = {
            'sportmonks_id': stage_item.get('id'),
            'sport_id': stage_item.get('sport_id'),
            'country_id': stage_item.get('country_id'),
            'league_id': stage_item.get('league_id'),
            'season_id': stage_item.get('season_id'),
            'type_id': stage_item.get('type_id'),
            'name': stage_item.get('name'),
            'short_code': stage_item.get('short_code'),
            'sort_order': stage_item.get('sort_order'),
            'finished': stage_item.get('finished'),
            'is_current': stage_item.get('is_current'),
            'starting_at': stage_item.get('starting_at'),
            'ending_at': stage_item.get('ending_at'),
            'created_at': datetime.utcnow().isoformat()
        }
        stages_to_save.append(stage_data)
    
    logger.info(f"📊 {len(stages_to_save)} stages preparados para inserção")
    
    # Salvar stages em lotes para melhor performance
    batch_size = 50
    saved_count = 0
    skipped_count = 0
    error_count = 0
    
    for i in range(0, len(stages_to_save), batch_size):
        batch = stages_to_save[i:i + batch_size]
        
        try:
            # Tentar inserir lote completo
            supabase.table('stages').insert(batch).execute()
            saved_count += len(batch)
            logger.info(f"✅ Lote {i//batch_size + 1}: {len(batch)} stages salvos")
            
        except Exception as e:
            if 'duplicate key' in str(e).lower() or 'unique constraint' in str(e).lower():
                # Se houver conflito, salvar um por vez
                logger.info(f"⚠️ Conflito no lote {i//batch_size + 1}, salvando individualmente...")
                for stage_data in batch:
                    try:
                        supabase.table('stages').insert(stage_data).execute()
                        saved_count += 1
                        logger.info(f"✅ Stage salvo: {stage_data['name']} (ID: {stage_data['sportmonks_id']})")
                    except Exception as e2:
                        if 'duplicate key' in str(e2).lower() or 'unique constraint' in str(e2).lower():
                            skipped_count += 1
                            logger.info(f"⏭️ Stage já existe: {stage_data['name']} (ID: {stage_data['sportmonks_id']})")
                        else:
                            error_count += 1
                            logger.warning(f"⚠️ Erro ao salvar stage '{stage_data['name']}': {e2}")
            else:
                error_count += len(batch)
                logger.warning(f"⚠️ Erro no lote {i//batch_size + 1}: {e}")
        
        # Aguardar entre lotes para evitar rate limiting
        time.sleep(0.2)
    
    logger.info(f"✅ {saved_count} stages novos salvos")
    logger.info(f"⏭️ {skipped_count} stages já existiam")
    logger.info(f"❌ {error_count} stages com erro")
    
    return saved_count, skipped_count, error_count

def generate_final_report():
    """Gerar relatório final da tabela stages"""
    
    logger.info("📊 Gerando relatório final...")
    
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        
        # Contagem total
        response = supabase.table('stages').select('*', count='exact').execute()
        total_count = response.count
        logger.info(f"📊 Total de stages na tabela: {total_count}")
        
        # Estatísticas por liga
        logger.info("\n📈 Estatísticas por liga:")
        league_stats = supabase.table('stages').select('league_id').not_.is_('league_id', 'null').execute()
        league_counts = {}
        for stage in league_stats.data:
            lid = stage['league_id']
            league_counts[lid] = league_counts.get(lid, 0) + 1
        
        # Top 10 ligas com mais stages
        top_leagues = sorted(league_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for league_id, count in top_leagues:
            logger.info(f"   • Liga ID {league_id}: {count} stages")
        
        # Stages finalizados vs ativos
        finished_stages = supabase.table('stages').select('sportmonks_id,name,finished').eq('finished', True).execute()
        current_stages = supabase.table('stages').select('sportmonks_id,name,is_current').eq('is_current', True).execute()
        logger.info(f"\n✅ Stages finalizados: {len(finished_stages.data)}")
        logger.info(f"🔄 Stages atuais: {len(current_stages.data)}")
        
        # Stages com datas
        with_dates = supabase.table('stages').select('sportmonks_id,name,starting_at,ending_at').not_.is_('starting_at', 'null').execute()
        logger.info(f"📅 Stages com datas: {len(with_dates.data)}")
        
        # Exemplos de stages
        logger.info("\n📋 Exemplos de stages:")
        examples = supabase.table('stages').select('sportmonks_id,name,league_id,finished,is_current').limit(10).execute()
        for stage in examples.data:
            status = "✅ Finalizado" if stage['finished'] else "🔄 Ativo"
            current = "⭐ Atual" if stage['is_current'] else ""
            logger.info(f"   • ID {stage['sportmonks_id']}: {stage['name']} - Liga {stage['league_id']} - {status} {current}")
        
        # Top 10 stages mais populares (por ID mais baixo)
        logger.info("\n🏆 Top 10 stages (IDs mais baixos):")
        top_stages = supabase.table('stages').select('sportmonks_id,name,league_id,finished').order('sportmonks_id').limit(10).execute()
        for stage in top_stages.data:
            status = "✅ Finalizado" if stage['finished'] else "🔄 Ativo"
            logger.info(f"   • ID {stage['sportmonks_id']}: {stage['name']} - Liga {stage['league_id']} - {status}")
                
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 CRIANDO TABELA STAGES E COLETANDO DADOS DA SPORTMONKS API")
    logger.info("=" * 80)
    
    # Criar tabela stages
    create_stages_table()
    
    # Coletar todos os stages com paginação completa
    stages_data = get_all_stages_with_pagination()
    
    if stages_data:
        # Salvar no banco de dados
        saved, skipped, errors = save_stages_to_database(stages_data)
        
        # Gerar relatório final
        generate_final_report()
        
        logger.info("=" * 80)
        logger.info("✅ CRIAÇÃO DE TABELA E COLETA DE STAGES FINALIZADA!")
        logger.info(f"📊 Salvos: {saved}, Já existiam: {skipped}, Erros: {errors}")
        logger.info("=" * 80)
    else:
        logger.error("❌ Falha na coleta de stages")

if __name__ == "__main__":
    main()
