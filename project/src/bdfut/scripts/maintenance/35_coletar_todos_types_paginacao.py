#!/usr/bin/env python3
"""
Script para coletar TODOS os types da Sportmonks API com paginação completa
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

def get_all_types_with_pagination():
    """Buscar TODOS os types da API Sportmonks com paginação completa"""
    
    # Token válido fornecido pelo usuário
    api_token = "teW8DGJoAC7Gc6r4u0RrCMB4IR4iy8s22BF9mgOTtoNUu3UBMc58wulgveYB"
    
    all_types = []
    page = 1
    per_page = 25  # Máximo por página
    total_pages = None
    total_count = None
    
    logger.info("🌐 Iniciando coleta COMPLETA de types com paginação...")
    logger.info(f"🔑 Usando token válido: {api_token[:10]}...")
    
    while True:
        # URL da API Sportmonks para types com paginação
        url = f"https://api.sportmonks.com/v3/core/types?api_token={api_token}&include=&page={page}&per_page={per_page}"
        
        logger.info(f"📄 Página {page} - Fazendo requisição...")
        
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extrair dados da página atual
                types = data.get('data', [])
                pagination = data.get('pagination', {})
                
                logger.info(f"✅ Página {page}: {len(types)} types encontrados")
                
                # Mostrar alguns exemplos da página atual
                if types:
                    logger.info(f"   📋 Exemplos: {types[0].get('name')} (ID: {types[0].get('id')}), {types[1].get('name') if len(types) > 1 else 'N/A'}")
                
                # Adicionar types à lista total
                all_types.extend(types)
                
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
        if page > 50:  # Máximo de 50 páginas (1250 types)
            logger.warning("⚠️ Limite de páginas atingido (50)")
            break
    
    logger.info(f"🎉 Coleta COMPLETA finalizada: {len(all_types)} types coletados")
    return all_types

def save_types_to_database(types_data):
    """Salvar types no banco de dados"""
    
    logger.info("💾 Salvando types no banco de dados...")
    
    # Inicializar cliente Supabase
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
        return
    
    if not types_data:
        logger.error("❌ Nenhum type para salvar")
        return
    
    # Preparar dados para inserção
    types_to_save = []
    for type_item in types_data:
        type_data = {
            'sportmonks_id': type_item.get('id'),
            'name': type_item.get('name'),
            'code': type_item.get('code'),
            'developer_name': type_item.get('developer_name'),
            'model_type': type_item.get('model_type'),
            'stat_group': type_item.get('stat_group'),
            'created_at': datetime.utcnow().isoformat()
        }
        types_to_save.append(type_data)
    
    logger.info(f"📊 {len(types_to_save)} types preparados para inserção")
    
    # Salvar types em lotes para melhor performance
    batch_size = 50
    saved_count = 0
    skipped_count = 0
    error_count = 0
    
    for i in range(0, len(types_to_save), batch_size):
        batch = types_to_save[i:i + batch_size]
        
        try:
            # Tentar inserir lote completo
            supabase.table('types').insert(batch).execute()
            saved_count += len(batch)
            logger.info(f"✅ Lote {i//batch_size + 1}: {len(batch)} types salvos")
            
        except Exception as e:
            if 'duplicate key' in str(e).lower() or 'unique constraint' in str(e).lower():
                # Se houver conflito, salvar um por vez
                logger.info(f"⚠️ Conflito no lote {i//batch_size + 1}, salvando individualmente...")
                for type_data in batch:
                    try:
                        supabase.table('types').insert(type_data).execute()
                        saved_count += 1
                        logger.info(f"✅ Type salvo: {type_data['name']} (ID: {type_data['sportmonks_id']})")
                    except Exception as e2:
                        if 'duplicate key' in str(e2).lower() or 'unique constraint' in str(e2).lower():
                            skipped_count += 1
                            logger.info(f"⏭️ Type já existe: {type_data['name']} (ID: {type_data['sportmonks_id']})")
                        else:
                            error_count += 1
                            logger.warning(f"⚠️ Erro ao salvar type '{type_data['name']}': {e2}")
            else:
                error_count += len(batch)
                logger.warning(f"⚠️ Erro no lote {i//batch_size + 1}: {e}")
        
        # Aguardar entre lotes para evitar rate limiting
        time.sleep(0.2)
    
    logger.info(f"✅ {saved_count} types novos salvos")
    logger.info(f"⏭️ {skipped_count} types já existiam")
    logger.info(f"❌ {error_count} types com erro")
    
    return saved_count, skipped_count, error_count

def generate_final_report():
    """Gerar relatório final da tabela types"""
    
    logger.info("📊 Gerando relatório final...")
    
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        
        # Contagem total
        response = supabase.table('types').select('*', count='exact').execute()
        total_count = response.count
        logger.info(f"📊 Total de types na tabela: {total_count}")
        
        # Estatísticas por model_type
        logger.info("\n📈 Estatísticas por model_type:")
        model_stats = supabase.table('types').select('model_type').not_.is_('model_type', 'null').execute()
        model_counts = {}
        for type_item in model_stats.data:
            model = type_item['model_type']
            model_counts[model] = model_counts.get(model, 0) + 1
        
        for model_type, count in sorted(model_counts.items()):
            logger.info(f"   • {model_type}: {count} types")
        
        # Types com código
        with_code = supabase.table('types').select('sportmonks_id,name,code').not_.is_('code', 'null').execute()
        logger.info(f"\n🔢 Types com código: {len(with_code.data)}")
        
        # Types com developer_name
        with_dev_name = supabase.table('types').select('sportmonks_id,name,developer_name').not_.is_('developer_name', 'null').execute()
        logger.info(f"👨‍💻 Types com developer_name: {len(with_dev_name.data)}")
        
        # Types com stat_group
        with_stat_group = supabase.table('types').select('sportmonks_id,name,stat_group').not_.is_('stat_group', 'null').execute()
        logger.info(f"📊 Types com stat_group: {len(with_stat_group.data)}")
        
        # Exemplos de types por model_type
        logger.info("\n📋 Exemplos por model_type:")
        for model_type in sorted(model_counts.keys()):
            examples = supabase.table('types').select('sportmonks_id,name,code,developer_name').eq('model_type', model_type).limit(5).execute()
            logger.info(f"\n{model_type}:")
            for type_item in examples.data:
                logger.info(f"   • ID {type_item['sportmonks_id']}: {type_item['name']} ({type_item['code']}) - Dev: {type_item['developer_name']}")
        
        # Top 10 types por ID (mais antigos na API)
        logger.info("\n🏆 Top 10 types (IDs mais baixos):")
        top_types = supabase.table('types').select('sportmonks_id,name,code,model_type').order('sportmonks_id').limit(10).execute()
        for type_item in top_types.data:
            logger.info(f"   • ID {type_item['sportmonks_id']}: {type_item['name']} ({type_item['code']}) - Model: {type_item['model_type']}")
        
        # Types mais comuns (por nome)
        logger.info("\n📊 Types mais comuns:")
        common_types = supabase.table('types').select('sportmonks_id,name,code,model_type').in_('sportmonks_id', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).execute()
        for type_item in common_types.data:
            logger.info(f"   • ID {type_item['sportmonks_id']}: {type_item['name']} ({type_item['code']}) - Model: {type_item['model_type']}")
                
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 COLETANDO TODOS OS TYPES DA SPORTMONKS API COM PAGINAÇÃO COMPLETA")
    logger.info("=" * 80)
    
    # Coletar todos os types com paginação completa
    types_data = get_all_types_with_pagination()
    
    if types_data:
        # Salvar no banco de dados
        saved, skipped, errors = save_types_to_database(types_data)
        
        # Gerar relatório final
        generate_final_report()
        
        logger.info("=" * 80)
        logger.info("✅ COLETA COMPLETA DE TYPES FINALIZADA!")
        logger.info(f"📊 Salvos: {saved}, Já existiam: {skipped}, Erros: {errors}")
        logger.info("=" * 80)
    else:
        logger.error("❌ Falha na coleta completa de types")

if __name__ == "__main__":
    main()
