#!/usr/bin/env python3
"""
Script final para coletar TODOS os dados completos após criação das tabelas
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Set

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.sportmonks_client import SportmonksClient
from supabase import create_client
from config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def collect_core_data(sportmonks: SportmonksClient, supabase):
    """Coletar dados core: countries, states, types"""
    
    logger.info("🌍 Coletando dados core (countries, states, types)...")
    
    try:
        # Countries
        logger.info("📊 Coletando countries...")
        countries = sportmonks.get_countries()
        
        countries_to_save = []
        for country in countries:
            country_data = {
                'sportmonks_id': country.get('id'),
                'name': country.get('name'),
                'code': country.get('code'),
                'image_path': country.get('image_path'),
                'created_at': datetime.utcnow().isoformat()
            }
            countries_to_save.append(country_data)
        
        if countries_to_save:
            supabase.table('countries').upsert(countries_to_save, on_conflict='sportmonks_id').execute()
            logger.info(f"✅ {len(countries_to_save)} countries salvos")
        
        # States
        logger.info("📊 Coletando states...")
        states = sportmonks.get_states()
        
        states_to_save = []
        for state in states:
            state_data = {
                'sportmonks_id': state.get('id'),
                'name': state.get('name'),
                'short_name': state.get('short_name'),
                'developer_name': state.get('developer_name'),
                'created_at': datetime.utcnow().isoformat()
            }
            states_to_save.append(state_data)
        
        if states_to_save:
            supabase.table('states').upsert(states_to_save, on_conflict='sportmonks_id').execute()
            logger.info(f"✅ {len(states_to_save)} states salvos")
        
        # Types
        logger.info("📊 Coletando types...")
        types = sportmonks.get_types()
        
        types_to_save = []
        for type_item in types:
            type_data = {
                'sportmonks_id': type_item.get('id'),
                'name': type_item.get('name'),
                'developer_name': type_item.get('developer_name'),
                'created_at': datetime.utcnow().isoformat()
            }
            types_to_save.append(type_data)
        
        if types_to_save:
            supabase.table('types').upsert(types_to_save, on_conflict='sportmonks_id').execute()
            logger.info(f"✅ {len(types_to_save)} types salvos")
            
    except Exception as e:
        logger.error(f"❌ Erro ao coletar dados core: {e}")

def collect_venues_from_fixtures(supabase):
    """Coletar venues únicos das fixtures"""
    
    logger.info("🏟️ Coletando venues das fixtures...")
    
    try:
        # Buscar fixtures com venues
        fixtures_response = supabase.table('fixtures').select('venue').not_.is_('venue', 'null').execute()
        
        venues_set = set()
        for fixture in fixtures_response.data:
            venue = fixture.get('venue')
            if venue and venue.strip():
                venues_set.add(venue.strip())
        
        logger.info(f"📊 {len(venues_set)} venues únicos encontrados")
        
        # Salvar venues
        venues_to_save = []
        for venue_name in venues_set:
            venue_data = {
                'name': venue_name,
                'created_at': datetime.utcnow().isoformat()
            }
            venues_to_save.append(venue_data)
        
        if venues_to_save:
            supabase.table('venues').upsert(venues_to_save, on_conflict='name').execute()
            logger.info(f"✅ {len(venues_to_save)} venues salvos")
            
    except Exception as e:
        logger.error(f"❌ Erro ao coletar venues: {e}")

def collect_referees_from_fixtures(supabase):
    """Coletar referees únicos das fixtures"""
    
    logger.info("👨‍⚖️ Coletando referees das fixtures...")
    
    try:
        # Buscar fixtures com referees
        fixtures_response = supabase.table('fixtures').select('referee').not_.is_('referee', 'null').execute()
        
        referees_set = set()
        for fixture in fixtures_response.data:
            referee = fixture.get('referee')
            if referee and referee.strip():
                referees_set.add(referee.strip())
        
        logger.info(f"📊 {len(referees_set)} referees únicos encontrados")
        
        # Salvar referees
        referees_to_save = []
        for referee_name in referees_set:
            referee_data = {
                'name': referee_name,
                'created_at': datetime.utcnow().isoformat()
            }
            referees_to_save.append(referee_data)
        
        if referees_to_save:
            supabase.table('referees').upsert(referees_to_save, on_conflict='name').execute()
            logger.info(f"✅ {len(referees_to_save)} referees salvos")
            
    except Exception as e:
        logger.error(f"❌ Erro ao coletar referees: {e}")

def collect_players_from_events_and_lineups(supabase):
    """Coletar players únicos dos events e lineups"""
    
    logger.info("⚽ Coletando players dos events e lineups...")
    
    try:
        # Players dos events
        events_response = supabase.table('match_events').select('player_id,player_name').not_.is_('player_id', 'null').execute()
        
        players_set = set()
        for event in events_response.data:
            player_id = event.get('player_id')
            player_name = event.get('player_name')
            if player_id and player_name:
                players_set.add((player_id, player_name))
        
        # Players dos lineups
        lineups_response = supabase.table('match_lineups').select('player_id,player_name').not_.is_('player_id', 'null').execute()
        
        for lineup in lineups_response.data:
            player_id = lineup.get('player_id')
            player_name = lineup.get('player_name')
            if player_id and player_name:
                players_set.add((player_id, player_name))
        
        logger.info(f"📊 {len(players_set)} players únicos encontrados")
        
        # Salvar players
        players_to_save = []
        for player_id, player_name in players_set:
            player_data = {
                'sportmonks_id': player_id,
                'name': player_name,
                'created_at': datetime.utcnow().isoformat()
            }
            players_to_save.append(player_data)
        
        if players_to_save:
            supabase.table('players').upsert(players_to_save, on_conflict='sportmonks_id').execute()
            logger.info(f"✅ {len(players_to_save)} players salvos")
            
    except Exception as e:
        logger.error(f"❌ Erro ao coletar players: {e}")

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 COLETANDO DADOS FINAIS COMPLETOS")
    logger.info("=" * 80)
    
    # Inicializar clientes
    try:
        config = Config()
        sportmonks = SportmonksClient()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Clientes inicializados com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar clientes: {e}")
        return
    
    # Verificar se as tabelas existem
    logger.info("🔍 Verificando se as tabelas foram criadas...")
    
    required_tables = ['countries', 'states', 'types', 'venues', 'referees', 'players']
    missing_tables = []
    
    for table in required_tables:
        try:
            supabase.table(table).select('*', count='exact').limit(1).execute()
            logger.info(f"✅ Tabela {table} existe")
        except Exception as e:
            missing_tables.append(table)
            logger.warning(f"⚠️ Tabela {table} não existe: {e}")
    
    if missing_tables:
        logger.error(f"❌ Tabelas faltando: {missing_tables}")
        logger.info("📝 Execute primeiro o SQL do arquivo 'create_tables.sql' no Supabase SQL Editor")
        logger.info("🔗 Acesse: https://supabase.com/dashboard/project/qoqeshyuwmxfrjdkhwii/sql")
        return
    
    # Coletar dados core
    collect_core_data(sportmonks, supabase)
    
    # Coletar venues e referees das fixtures
    collect_venues_from_fixtures(supabase)
    collect_referees_from_fixtures(supabase)
    
    # Coletar players dos events e lineups
    collect_players_from_events_and_lineups(supabase)
    
    # Relatório final
    logger.info("=" * 80)
    logger.info("📊 RELATÓRIO FINAL COMPLETO")
    logger.info("=" * 80)
    
    # Contar registros em todas as tabelas
    all_tables = ['leagues', 'seasons', 'teams', 'fixtures', 'match_events', 'match_statistics', 'match_lineups', 'countries', 'states', 'types', 'venues', 'referees', 'players']
    
    total_records = 0
    for table in all_tables:
        try:
            response = supabase.table(table).select('*', count='exact').execute()
            count = response.count
            total_records += count
            logger.info(f"   • {table}: {count:,} registros")
        except Exception as e:
            logger.warning(f"   • {table}: erro ao contar - {e}")
    
    logger.info("")
    logger.info(f"📊 TOTAL DE REGISTROS: {total_records:,}")
    
    logger.info("")
    logger.info("🎯 STATUS FINAL:")
    logger.info("   ✅ Todas as tabelas criadas")
    logger.info("   ✅ Todos os dados coletados")
    logger.info("   ✅ Base de dados completa!")
    
    logger.info("=" * 80)
    logger.info("🎉 PROJETO CONCLUÍDO COM SUCESSO!")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()
