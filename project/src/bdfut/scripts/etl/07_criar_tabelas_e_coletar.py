#!/usr/bin/env python3
"""
Script para criar tabelas e coletar dados completos
Usa uma abordagem alternativa para criar as tabelas
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

def create_tables_via_sql(supabase):
    """Tentar criar tabelas via SQL direto"""
    
    logger.info("🔨 Tentando criar tabelas via SQL...")
    
    # SQL para criar as tabelas
    create_sql = """
    -- Criar tabela venues
    CREATE TABLE IF NOT EXISTS venues (
        id SERIAL PRIMARY KEY,
        sportmonks_id INTEGER UNIQUE,
        name VARCHAR(255) NOT NULL,
        city VARCHAR(255),
        capacity INTEGER,
        surface VARCHAR(100),
        country VARCHAR(100),
        image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Criar tabela referees
    CREATE TABLE IF NOT EXISTS referees (
        id SERIAL PRIMARY KEY,
        sportmonks_id INTEGER UNIQUE,
        name VARCHAR(255) NOT NULL,
        common_name VARCHAR(255),
        firstname VARCHAR(255),
        lastname VARCHAR(255),
        nationality VARCHAR(100),
        image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Criar tabela players
    CREATE TABLE IF NOT EXISTS players (
        id SERIAL PRIMARY KEY,
        sportmonks_id INTEGER UNIQUE,
        name VARCHAR(255) NOT NULL,
        common_name VARCHAR(255),
        firstname VARCHAR(255),
        lastname VARCHAR(255),
        nationality VARCHAR(100),
        position_id INTEGER,
        position_name VARCHAR(100),
        date_of_birth DATE,
        height INTEGER,
        weight INTEGER,
        image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Criar tabela coaches
    CREATE TABLE IF NOT EXISTS coaches (
        id SERIAL PRIMARY KEY,
        sportmonks_id INTEGER UNIQUE,
        name VARCHAR(255) NOT NULL,
        common_name VARCHAR(255),
        firstname VARCHAR(255),
        lastname VARCHAR(255),
        nationality VARCHAR(100),
        image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Criar tabela states
    CREATE TABLE IF NOT EXISTS states (
        id SERIAL PRIMARY KEY,
        sportmonks_id INTEGER UNIQUE,
        name VARCHAR(255) NOT NULL,
        short_name VARCHAR(10),
        developer_name VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Criar tabela types
    CREATE TABLE IF NOT EXISTS types (
        id SERIAL PRIMARY KEY,
        sportmonks_id INTEGER UNIQUE,
        name VARCHAR(255) NOT NULL,
        developer_name VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Criar tabela countries
    CREATE TABLE IF NOT EXISTS countries (
        id SERIAL PRIMARY KEY,
        sportmonks_id INTEGER UNIQUE,
        name VARCHAR(255) NOT NULL,
        code VARCHAR(10),
        image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        # Tentar executar via RPC
        result = supabase.rpc('exec_sql', {'sql': create_sql}).execute()
        logger.info("✅ Tabelas criadas com sucesso via RPC")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível criar via RPC: {e}")
        
        # Tentar executar SQL direto
        try:
            result = supabase.postgrest.rpc('exec_sql', {'sql': create_sql}).execute()
            logger.info("✅ Tabelas criadas com sucesso via PostgREST")
            return True
        except Exception as e2:
            logger.error(f"❌ Não foi possível criar tabelas: {e2}")
            return False

def collect_and_save_data(sportmonks: SportmonksClient, supabase):
    """Coletar e salvar dados nas tabelas existentes"""
    
    logger.info("📊 Coletando dados das fixtures existentes...")
    
    # Coletar venues únicos
    try:
        fixtures_response = supabase.table('fixtures').select('venue').not_.is_('venue', 'null').execute()
        
        venues_set = set()
        for fixture in fixtures_response.data:
            venue = fixture.get('venue')
            if venue and venue.strip():
                venues_set.add(venue.strip())
        
        logger.info(f"📊 {len(venues_set)} venues únicos encontrados")
        
        # Salvar venues (se a tabela existir)
        if venues_set:
            venues_to_save = []
            for venue_name in venues_set:
                venue_data = {
                    'name': venue_name,
                    'created_at': datetime.utcnow().isoformat()
                }
                venues_to_save.append(venue_data)
            
            try:
                supabase.table('venues').upsert(venues_to_save, on_conflict='name').execute()
                logger.info(f"✅ {len(venues_to_save)} venues salvos")
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível salvar venues: {e}")
                
    except Exception as e:
        logger.error(f"❌ Erro ao coletar venues: {e}")
    
    # Coletar players únicos dos events e lineups
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
        
        # Salvar players (se a tabela existir)
        if players_set:
            players_to_save = []
            for player_id, player_name in players_set:
                player_data = {
                    'sportmonks_id': player_id,
                    'name': player_name,
                    'created_at': datetime.utcnow().isoformat()
                }
                players_to_save.append(player_data)
            
            try:
                supabase.table('players').upsert(players_to_save, on_conflict='sportmonks_id').execute()
                logger.info(f"✅ {len(players_to_save)} players salvos")
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível salvar players: {e}")
                
    except Exception as e:
        logger.error(f"❌ Erro ao coletar players: {e}")

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 CRIANDO TABELAS E COLETANDO DADOS COMPLETOS")
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
    
    # Tentar criar tabelas
    tables_created = create_tables_via_sql(supabase)
    
    if not tables_created:
        logger.info("⚠️ Tabelas não foram criadas automaticamente")
        logger.info("📝 Execute o SQL do arquivo 'create_tables.sql' manualmente no Supabase SQL Editor")
        logger.info("🔗 Acesse: https://supabase.com/dashboard/project/qoqeshyuwmxfrjdkhwii/sql")
    
    # Coletar dados das fixtures existentes
    collect_and_save_data(sportmonks, supabase)
    
    # Relatório final
    logger.info("=" * 80)
    logger.info("📊 RELATÓRIO FINAL")
    logger.info("=" * 80)
    
    # Contar registros nas tabelas existentes
    existing_tables = ['leagues', 'seasons', 'teams', 'fixtures', 'match_events', 'match_statistics', 'match_lineups']
    for table in existing_tables:
        try:
            response = supabase.table(table).select('*', count='exact').execute()
            count = response.count
            logger.info(f"   • {table}: {count:,} registros")
        except Exception as e:
            logger.warning(f"   • {table}: erro ao contar - {e}")
    
    logger.info("")
    logger.info("🎯 PRÓXIMOS PASSOS:")
    logger.info("   1. Execute o SQL do arquivo 'create_tables.sql' no Supabase SQL Editor")
    logger.info("   2. Execute novamente este script para popular as novas tabelas")
    logger.info("   3. Ou execute: python3 08_coletar_dados_finais.py")
    
    logger.info("=" * 80)
    logger.info("✅ PROCESSO CONCLUÍDO!")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()
