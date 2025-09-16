#!/usr/bin/env python3
"""
Script para configurar Supabase CLI e criar tabela stages via migrações
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_supabase_cli():
    """Verificar se Supabase CLI está instalado"""
    
    logger.info("🔍 Verificando se Supabase CLI está instalado...")
    
    try:
        result = subprocess.run(['supabase', '--version'], 
                              capture_output=True, text=True, check=True)
        logger.info(f"✅ Supabase CLI encontrado: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        logger.error("❌ Supabase CLI não encontrado")
        return False
    except FileNotFoundError:
        logger.error("❌ Supabase CLI não está instalado")
        return False

def install_supabase_cli():
    """Instalar Supabase CLI"""
    
    logger.info("📦 Instalando Supabase CLI...")
    
    try:
        # Tentar instalar via npm
        logger.info("Tentando instalar via npm...")
        subprocess.run(['npm', 'install', '-g', 'supabase'], 
                      check=True, capture_output=True)
        logger.info("✅ Supabase CLI instalado via npm")
        return True
    except subprocess.CalledProcessError:
        logger.warning("⚠️ Falha na instalação via npm")
        
        try:
            # Tentar instalar via brew (macOS)
            logger.info("Tentando instalar via brew...")
            subprocess.run(['brew', 'install', 'supabase/tap/supabase'], 
                          check=True, capture_output=True)
            logger.info("✅ Supabase CLI instalado via brew")
            return True
        except subprocess.CalledProcessError:
            logger.error("❌ Falha na instalação via brew")
            return False

def init_supabase_project():
    """Inicializar projeto Supabase"""
    
    logger.info("🚀 Inicializando projeto Supabase...")
    
    try:
        # Verificar se já existe diretório supabase
        if os.path.exists('supabase'):
            logger.info("📁 Diretório supabase já existe")
            return True
        
        # Inicializar projeto
        result = subprocess.run(['supabase', 'init'], 
                              capture_output=True, text=True, check=True)
        logger.info("✅ Projeto Supabase inicializado")
        logger.info(f"Output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao inicializar projeto: {e}")
        logger.error(f"Stderr: {e.stderr}")
        return False

def login_supabase():
    """Fazer login no Supabase"""
    
    logger.info("🔐 Fazendo login no Supabase...")
    
    try:
        # Usar token de acesso pessoal
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFvcWVzaHl1d214ZnJqZGtod2lpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzY5MzE3NCwiZXhwIjoyMDczMjY5MTc0fQ.QPgk88JViYHXekcJwsHtBgIU7CjKWx1ZUkd1nEkRGoQ"
        
        # Definir variável de ambiente
        env = os.environ.copy()
        env['SUPABASE_ACCESS_TOKEN'] = access_token
        
        result = subprocess.run(['supabase', 'login'], 
                              input=access_token, text=True,
                              capture_output=True, check=True, env=env)
        logger.info("✅ Login realizado com sucesso")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro no login: {e}")
        logger.error(f"Stderr: {e.stderr}")
        return False

def link_supabase_project():
    """Linkar projeto Supabase"""
    
    logger.info("🔗 Linkando projeto Supabase...")
    
    try:
        project_ref = "qoqeshyuwmxfrjdkhwii"
        
        result = subprocess.run(['supabase', 'link', '--project-ref', project_ref], 
                              capture_output=True, text=True, check=True)
        logger.info("✅ Projeto linkado com sucesso")
        logger.info(f"Output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao linkar projeto: {e}")
        logger.error(f"Stderr: {e.stderr}")
        return False

def create_stages_migration():
    """Criar migração para tabela stages"""
    
    logger.info("📝 Criando migração para tabela stages...")
    
    try:
        # Criar nova migração
        result = subprocess.run(['supabase', 'migration', 'new', 'create_stages_table'], 
                              capture_output=True, text=True, check=True)
        
        migration_file = result.stdout.strip()
        logger.info(f"✅ Migração criada: {migration_file}")
        
        # Escrever SQL na migração
        sql_content = """
create table if not exists public.stages (
    id bigint primary key generated always as identity,
    sportmonks_id integer unique not null,
    sport_id integer,
    country_id integer,
    league_id integer,
    season_id integer,
    type_id integer,
    name text,
    short_code text,
    sort_order integer,
    finished boolean default false,
    is_current boolean default false,
    starting_at timestamptz,
    ending_at timestamptz,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);
"""
        
        # Encontrar arquivo de migração mais recente
        migrations_dir = "supabase/migrations"
        if os.path.exists(migrations_dir):
            migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.sql')]
            if migration_files:
                latest_migration = max(migration_files)
                migration_path = os.path.join(migrations_dir, latest_migration)
                
                with open(migration_path, 'w') as f:
                    f.write(sql_content)
                
                logger.info(f"✅ SQL adicionado à migração: {migration_path}")
                return True
        
        logger.error("❌ Não foi possível encontrar arquivo de migração")
        return False
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao criar migração: {e}")
        logger.error(f"Stderr: {e.stderr}")
        return False

def push_migration():
    """Fazer push da migração para o banco remoto"""
    
    logger.info("🚀 Fazendo push da migração...")
    
    try:
        result = subprocess.run(['supabase', 'db', 'push'], 
                              capture_output=True, text=True, check=True)
        logger.info("✅ Migração enviada com sucesso")
        logger.info(f"Output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao fazer push: {e}")
        logger.error(f"Stderr: {e.stderr}")
        return False

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 CONFIGURANDO SUPABASE CLI PARA CRIAR TABELA STAGES")
    logger.info("=" * 80)
    
    # Verificar se CLI está instalado
    if not check_supabase_cli():
        logger.info("📦 Tentando instalar Supabase CLI...")
        if not install_supabase_cli():
            logger.error("❌ Não foi possível instalar Supabase CLI")
            logger.info("💡 Instale manualmente: https://supabase.com/docs/guides/cli/getting-started")
            return
    
    # Inicializar projeto
    if not init_supabase_project():
        logger.error("❌ Falha na inicialização do projeto")
        return
    
    # Fazer login
    if not login_supabase():
        logger.error("❌ Falha no login")
        return
    
    # Linkar projeto
    if not link_supabase_project():
        logger.error("❌ Falha ao linkar projeto")
        return
    
    # Criar migração
    if not create_stages_migration():
        logger.error("❌ Falha ao criar migração")
        return
    
    # Fazer push da migração
    if not push_migration():
        logger.error("❌ Falha ao fazer push da migração")
        return
    
    logger.info("=" * 80)
    logger.info("✅ TABELA STAGES CRIADA COM SUCESSO!")
    logger.info("🎉 Agora você pode inserir os dados dos stages!")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()
