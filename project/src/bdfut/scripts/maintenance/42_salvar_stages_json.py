#!/usr/bin/env python3
"""
Script para salvar os stages coletados em arquivo JSON
"""

import os
import sys
import requests
import json
import logging
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

def save_stages_to_json(stages_data):
    """Salvar stages em arquivo JSON"""
    
    logger.info("💾 Salvando stages em arquivo JSON...")
    
    if not stages_data:
        logger.error("❌ Nenhum stage para salvar")
        return
    
    # Preparar dados para JSON
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
    
    # Salvar em arquivo JSON
    filename = f"stages_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(stages_to_save, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ {len(stages_to_save)} stages salvos em {filename}")
    
    # Mostrar estatísticas
    logger.info("\n📊 Estatísticas dos stages:")
    
    # Contar por liga
    league_counts = {}
    for stage in stages_to_save:
        lid = stage.get('league_id')
        if lid:
            league_counts[lid] = league_counts.get(lid, 0) + 1
    
    # Top 10 ligas com mais stages
    top_leagues = sorted(league_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    logger.info("🏆 Top 10 ligas com mais stages:")
    for league_id, count in top_leagues:
        logger.info(f"   • Liga ID {league_id}: {count} stages")
    
    # Stages finalizados vs ativos
    finished_count = sum(1 for s in stages_to_save if s.get('finished'))
    current_count = sum(1 for s in stages_to_save if s.get('is_current'))
    logger.info(f"\n✅ Stages finalizados: {finished_count}")
    logger.info(f"🔄 Stages ativos: {current_count}")
    
    # Stages com datas
    with_dates = sum(1 for s in stages_to_save if s.get('starting_at'))
    logger.info(f"📅 Stages com datas: {with_dates}")
    
    # Exemplos de stages
    logger.info("\n📋 Exemplos de stages:")
    for i, stage in enumerate(stages_to_save[:10]):
        status = "✅ Finalizado" if stage.get('finished') else "🔄 Ativo"
        current = "⭐ Atual" if stage.get('is_current') else ""
        logger.info(f"   • ID {stage['sportmonks_id']}: {stage['name']} - Liga {stage.get('league_id', 'N/A')} - {status} {current}")
    
    return filename

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("💾 COLETANDO STAGES E SALVANDO EM JSON")
    logger.info("=" * 80)
    
    # Coletar todos os stages com paginação completa
    stages_data = get_all_stages_with_pagination()
    
    if stages_data:
        # Salvar em arquivo JSON
        filename = save_stages_to_json(stages_data)
        
        logger.info("=" * 80)
        logger.info("✅ COLETA E SALVAMENTO FINALIZADOS!")
        logger.info(f"📁 Arquivo salvo: {filename}")
        logger.info("=" * 80)
    else:
        logger.error("❌ Falha na coleta de stages")

if __name__ == "__main__":
    main()
