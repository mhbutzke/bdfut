#!/usr/bin/env python3
"""
Script para criar tabela stages usando Supabase Client e inserir dados do JSON
"""

import os
import sys
import json
import logging
from datetime import datetime

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

def create_stages_table_sql():
    """Gerar SQL para criar tabela stages"""
    
    sql = """
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
    
    logger.info("📋 SQL para criar tabela stages:")
    logger.info(sql)
    logger.info("💡 Execute este SQL no Supabase Dashboard > SQL Editor")
    
    return sql

def load_stages_from_json(filename):
    """Carregar stages do arquivo JSON"""
    
    logger.info(f"📁 Carregando stages do arquivo: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            stages_data = json.load(f)
        
        logger.info(f"✅ {len(stages_data)} stages carregados do JSON")
        return stages_data
        
    except FileNotFoundError:
        logger.error(f"❌ Arquivo não encontrado: {filename}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"❌ Erro ao decodificar JSON: {e}")
        return []

def insert_stages_to_supabase(stages_data):
    """Inserir stages no Supabase"""
    
    logger.info("💾 Inserindo stages no Supabase...")
    
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
        return
    
    if not stages_data:
        logger.error("❌ Nenhum stage para inserir")
        return
    
    # Preparar dados para inserção
    stages_to_insert = []
    for stage_item in stages_data:
        stage_data = {
            'sportmonks_id': stage_item.get('sportmonks_id'),
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
            'created_at': stage_item.get('created_at')
        }
        stages_to_insert.append(stage_data)
    
    logger.info(f"📊 {len(stages_to_insert)} stages preparados para inserção")
    
    # Inserir stages em lotes para melhor performance
    batch_size = 50
    saved_count = 0
    skipped_count = 0
    error_count = 0
    
    for i in range(0, len(stages_to_insert), batch_size):
        batch = stages_to_insert[i:i + batch_size]
        
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
        import time
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
        logger.info(f"🔄 Stages ativos: {len(current_stages.data)}")
        
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
    logger.info("🚀 CRIANDO TABELA STAGES E INSERINDO DADOS")
    logger.info("=" * 80)
    
    # Gerar SQL para criar tabela
    create_stages_table_sql()
    
    # Encontrar arquivo JSON mais recente
    json_files = [f for f in os.listdir('.') if f.startswith('stages_data_') and f.endswith('.json')]
    if not json_files:
        logger.error("❌ Nenhum arquivo JSON de stages encontrado")
        return
    
    latest_json = max(json_files)
    logger.info(f"📁 Usando arquivo mais recente: {latest_json}")
    
    # Carregar dados do JSON
    stages_data = load_stages_from_json(latest_json)
    
    if stages_data:
        # Inserir no Supabase
        saved, skipped, errors = insert_stages_to_supabase(stages_data)
        
        # Gerar relatório final
        generate_final_report()
        
        logger.info("=" * 80)
        logger.info("✅ CRIAÇÃO DE TABELA E INSERÇÃO DE STAGES FINALIZADA!")
        logger.info(f"📊 Salvos: {saved}, Já existiam: {skipped}, Erros: {errors}")
        logger.info("=" * 80)
    else:
        logger.error("❌ Falha ao carregar dados do JSON")

if __name__ == "__main__":
    main()
