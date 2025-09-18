#!/usr/bin/env python3
"""
Análise da Estrutura da Tabela Fixtures vs API Response
======================================================

Objetivo: Analisar a estrutura atual da tabela fixtures e comparar com os dados da API
para identificar duplicações e campos desnecessários.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

import requests
import logging
import json
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_api_structure():
    """Analisar a estrutura da API Sportmonks para fixtures"""
    Config.validate()
    api_key = Config.SPORTMONKS_API_KEY
    base_url = Config.SPORTMONKS_BASE_URL
    
    # Testar com alguns fixtures diferentes
    test_fixture_ids = ["16475287", "11865351", "12345678"]  # IDs de teste
    
    includes = "referees;venue;league;season;state;round;stage;participants"
    
    logger.info("🔍 Analisando estrutura da API Sportmonks...")
    
    for fixture_id in test_fixture_ids:
        try:
            url = f'{base_url}/fixtures/{fixture_id}'
            params = {
                'api_token': api_key,
                'include': includes
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            fixture_data = data.get('data')
            
            if fixture_data:
                logger.info(f"\\n📊 FIXTURE ID: {fixture_id}")
                logger.info("=" * 50)
                
                # Campos principais da fixture
                logger.info("🏷️ CAMPOS PRINCIPAIS:")
                for key, value in fixture_data.items():
                    if key not in ['referees', 'venue', 'league', 'season', 'state', 'round', 'stage', 'participants']:
                        logger.info(f"  {key}: {type(value).__name__} = {value}")
                
                # Includes
                logger.info("\\n📋 INCLUDES:")
                
                # Referees
                referees = fixture_data.get('referees', [])
                if referees:
                    logger.info(f"  referees: {len(referees)} itens")
                    for ref in referees:
                        logger.info(f"    - referee_id: {ref.get('referee_id')}, type_id: {ref.get('type_id')}")
                
                # Venue
                venue = fixture_data.get('venue')
                if venue:
                    logger.info(f"  venue: id={venue.get('id')}, name={venue.get('name')}")
                
                # League
                league = fixture_data.get('league')
                if league:
                    logger.info(f"  league: id={league.get('id')}, name={league.get('name')}")
                
                # Season
                season = fixture_data.get('season')
                if season:
                    logger.info(f"  season: id={season.get('id')}, name={season.get('name')}")
                
                # State
                state = fixture_data.get('state')
                if state:
                    logger.info(f"  state: id={state.get('id')}, name={state.get('name')}")
                
                # Round
                round_data = fixture_data.get('round')
                if round_data:
                    logger.info(f"  round: id={round_data.get('id')}, name={round_data.get('name')}")
                
                # Stage
                stage = fixture_data.get('stage')
                if stage:
                    logger.info(f"  stage: id={stage.get('id')}, name={stage.get('name')}")
                
                # Participants
                participants = fixture_data.get('participants', [])
                if participants:
                    logger.info(f"  participants: {len(participants)} itens")
                    for part in participants:
                        meta = part.get('meta', {})
                        logger.info(f"    - id={part.get('id')}, name={part.get('name')}, location={meta.get('location')}")
                
                # Salvar resposta completa para análise
                with open(f"fixture_{fixture_id}_response.json", "w") as f:
                    json.dump(fixture_data, f, indent=2, default=str)
                logger.info(f"💾 Resposta salva em: fixture_{fixture_id}_response.json")
                
                break  # Usar apenas o primeiro fixture válido
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixture {fixture_id}: {e}")
            continue

def analyze_current_table_structure():
    """Analisar a estrutura atual da tabela fixtures"""
    logger.info("\\n📊 ESTRUTURA ATUAL DA TABELA FIXTURES:")
    logger.info("=" * 60)
    
    # Campos principais (originais)
    logger.info("🏷️ CAMPOS PRINCIPAIS:")
    main_fields = [
        'id', 'sportmonks_id', 'league_id', 'season_id', 'home_team_id', 'away_team_id',
        'match_date', 'status', 'home_score', 'away_score', 'venue', 'referee',
        'created_at', 'updated_at', 'name', 'starting_at', 'result_info', 'leg',
        'details', 'length', 'placeholder', 'has_odds', 'has_players', 'has_lineups',
        'has_statistics', 'has_events', 'is_deleted', 'tie_breaker_rule'
    ]
    
    for field in main_fields:
        logger.info(f"  {field}")
    
    # Campos de enriquecimento (adicionados)
    logger.info("\\n📋 CAMPOS DE ENRIQUECIMENTO (ADICIONADOS):")
    enrichment_fields = [
        'venue_id', 'venue_name', 'league_id', 'league_name', 'season_id', 'season_name',
        'state_id', 'state_name', 'round_id', 'round_name', 'stage_id', 'stage_name',
        'home_team_id', 'home_team_name', 'away_team_id', 'away_team_name',
        'referee_id', 'referee_name'
    ]
    
    for field in enrichment_fields:
        logger.info(f"  {field}")
    
    # Identificar duplicações
    logger.info("\\n⚠️ DUPLICAÇÕES IDENTIFICADAS:")
    duplicates = [
        ('league_id', 'league_id'),  # Duplicado
        ('season_id', 'season_id'),  # Duplicado
        ('home_team_id', 'home_team_id'),  # Duplicado
        ('away_team_id', 'away_team_id'),  # Duplicado
        ('venue', 'venue_name'),  # Campo antigo vs novo
        ('referee', 'referee_name')  # Campo antigo vs novo
    ]
    
    for old_field, new_field in duplicates:
        logger.info(f"  {old_field} vs {new_field}")

def suggest_optimized_structure():
    """Sugerir estrutura otimizada"""
    logger.info("\\n💡 ESTRUTURA OTIMIZADA SUGERIDA:")
    logger.info("=" * 50)
    
    logger.info("🏷️ CAMPOS PRINCIPAIS (MANTER):")
    keep_fields = [
        'id', 'sportmonks_id', 'match_date', 'starting_at', 'status',
        'home_score', 'away_score', 'length', 'placeholder',
        'has_odds', 'has_players', 'has_lineups', 'has_statistics', 'has_events',
        'is_deleted', 'created_at', 'updated_at'
    ]
    
    for field in keep_fields:
        logger.info(f"  ✅ {field}")
    
    logger.info("\\n📋 CAMPOS DE ENRIQUECIMENTO (MANTER):")
    enrichment_fields = [
        'league_id', 'league_name', 'season_id', 'season_name',
        'venue_id', 'venue_name', 'state_id', 'state_name',
        'round_id', 'round_name', 'stage_id', 'stage_name',
        'home_team_id', 'home_team_name', 'away_team_id', 'away_team_name',
        'referee_id', 'referee_name'
    ]
    
    for field in enrichment_fields:
        logger.info(f"  ✅ {field}")
    
    logger.info("\\n🗑️ CAMPOS PARA REMOVER (DUPLICADOS/DESNECESSÁRIOS):")
    remove_fields = [
        'venue',  # Substituído por venue_name
        'referee',  # Substituído por referee_name
        'name',  # Não usado
        'result_info',  # Não usado
        'leg',  # Não usado
        'details',  # Não usado
        'tie_breaker_rule'  # Não usado
    ]
    
    for field in remove_fields:
        logger.info(f"  ❌ {field}")

def main():
    """Função principal"""
    logger.info("🚀 INICIANDO ANÁLISE DA ESTRUTURA DA TABELA FIXTURES")
    
    # Analisar estrutura da API
    analyze_api_structure()
    
    # Analisar estrutura atual da tabela
    analyze_current_table_structure()
    
    # Sugerir estrutura otimizada
    suggest_optimized_structure()
    
    logger.info("\\n✅ Análise concluída!")

if __name__ == "__main__":
    main()
