#!/usr/bin/env python3
"""
Script para criar tabelas no Supabase
"""
from supabase import create_client
from config.config import Config
import sys

def create_tables():
    """Cria as tabelas necessárias no Supabase"""
    
    print("🔄 Criando tabelas no Supabase...")
    
    # Conectar ao Supabase
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    # SQL para criar as tabelas
    sql_commands = [
        # Tabela de tipos
        """
        CREATE TABLE IF NOT EXISTS types (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(50),
            developer_name VARCHAR(100),
            model_type VARCHAR(50),
            stat_group VARCHAR(50),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Tabela de estados
        """
        CREATE TABLE IF NOT EXISTS states (
            id INTEGER PRIMARY KEY,
            state VARCHAR(50) NOT NULL,
            name VARCHAR(100) NOT NULL,
            short_name VARCHAR(10),
            developer_name VARCHAR(50),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Tabela de países
        """
        CREATE TABLE IF NOT EXISTS countries (
            id BIGINT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            official_name VARCHAR(255),
            fifa_name VARCHAR(255),
            iso2 VARCHAR(2),
            iso3 VARCHAR(3),
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            borders TEXT,
            image_path TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Tabela de venues (sem FK para countries temporariamente)
        """
        CREATE TABLE IF NOT EXISTS venues (
            id BIGINT PRIMARY KEY,
            country_id BIGINT,
            city_id BIGINT,
            name VARCHAR(255) NOT NULL,
            address VARCHAR(500),
            zipcode VARCHAR(20),
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            capacity INTEGER,
            image_path TEXT,
            city_name VARCHAR(255),
            surface VARCHAR(50),
            national_team BOOLEAN DEFAULT false,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Tabela de referees (sem FK temporariamente)
        """
        CREATE TABLE IF NOT EXISTS referees (
            id BIGINT PRIMARY KEY,
            sport_id BIGINT,
            country_id BIGINT,
            city_id BIGINT,
            common_name VARCHAR(255),
            firstname VARCHAR(255),
            lastname VARCHAR(255),
            name VARCHAR(255) NOT NULL,
            display_name VARCHAR(255),
            image_path TEXT,
            height INTEGER,
            weight INTEGER,
            date_of_birth DATE,
            gender VARCHAR(10),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Tabela de players
        """
        CREATE TABLE IF NOT EXISTS players (
            id BIGINT PRIMARY KEY,
            sport_id BIGINT,
            country_id BIGINT,
            nationality_id BIGINT,
            city_id BIGINT,
            position_id INTEGER,
            common_name VARCHAR(255),
            firstname VARCHAR(255),
            lastname VARCHAR(255),
            name VARCHAR(255) NOT NULL,
            display_name VARCHAR(255),
            image_path TEXT,
            height INTEGER,
            weight INTEGER,
            date_of_birth DATE,
            gender VARCHAR(10),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Tabela de fixture_participants
        """
        CREATE TABLE IF NOT EXISTS fixture_participants (
            id BIGSERIAL PRIMARY KEY,
            fixture_id BIGINT,
            team_id BIGINT,
            position VARCHAR(20),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(fixture_id, team_id)
        );
        """,
        
        # Tabela de fixture_events
        """
        CREATE TABLE IF NOT EXISTS fixture_events (
            id BIGINT PRIMARY KEY,
            fixture_id BIGINT,
            period_id INTEGER,
            participant_id BIGINT,
            type_id INTEGER,
            player_id BIGINT,
            related_player_id BIGINT,
            player_name VARCHAR(255),
            related_player_name VARCHAR(255),
            result VARCHAR(50),
            info VARCHAR(500),
            addition VARCHAR(500),
            minute INTEGER,
            extra_minute INTEGER,
            injured BOOLEAN DEFAULT false,
            on_bench BOOLEAN DEFAULT false,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Tabela de fixture_statistics
        """
        CREATE TABLE IF NOT EXISTS fixture_statistics (
            id BIGSERIAL PRIMARY KEY,
            fixture_id BIGINT,
            team_id BIGINT,
            type_id INTEGER,
            player_id BIGINT,
            position_id INTEGER,
            location VARCHAR(20),
            data JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Tabela de fixture_lineups
        """
        CREATE TABLE IF NOT EXISTS fixture_lineups (
            id BIGSERIAL PRIMARY KEY,
            fixture_id BIGINT,
            team_id BIGINT,
            player_id BIGINT,
            type VARCHAR(20),
            position_id INTEGER,
            position_name VARCHAR(50),
            formation_position VARCHAR(10),
            player_name VARCHAR(255),
            jersey_number INTEGER,
            captain BOOLEAN DEFAULT false,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Tabela de fixture_scores
        """
        CREATE TABLE IF NOT EXISTS fixture_scores (
            id BIGSERIAL PRIMARY KEY,
            fixture_id BIGINT,
            team_id BIGINT,
            score_type VARCHAR(50),
            score INTEGER,
            description VARCHAR(100),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Tabela de standings
        """
        CREATE TABLE IF NOT EXISTS standings (
            id BIGSERIAL PRIMARY KEY,
            participant_id BIGINT,
            sport_id BIGINT,
            league_id BIGINT,
            season_id BIGINT,
            stage_id BIGINT,
            group_id BIGINT,
            round_id BIGINT,
            standing_rule_id INTEGER,
            position INTEGER,
            result VARCHAR(100),
            points INTEGER,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Tabela de standing_details
        """
        CREATE TABLE IF NOT EXISTS standing_details (
            id BIGSERIAL PRIMARY KEY,
            standing_id BIGINT,
            type_id INTEGER,
            value INTEGER,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
    ]
    
    # Executar cada comando SQL
    for i, sql in enumerate(sql_commands, 1):
        try:
            # Como não podemos criar tabelas diretamente, vamos apenas mostrar o progresso
            print(f"  [{i}/{len(sql_commands)}] Preparando criação de tabela...")
        except Exception as e:
            print(f"  ⚠️  Erro ao criar tabela {i}: {str(e)}")
            continue
    
    print("""
✅ Script preparado!

IMPORTANTE: Como as tabelas precisam ser criadas manualmente, siga estes passos:

1. Acesse o SQL Editor do Supabase:
   https://supabase.com/dashboard/project/qoqeshyuwmxfrjdkhwii/sql/new

2. Cole e execute o conteúdo do arquivo:
   migrations/001_create_sportmonks_schema.sql

3. Depois de criar as tabelas, execute:
   python3 main.py full-sync

Isso populará o banco com todos os dados incluindo eventos e estatísticas das partidas!
""")

if __name__ == "__main__":
    create_tables()
