#!/usr/bin/env python3
"""
Script de configuração inicial do projeto BDFut
"""
import os
import sys
from pathlib import Path

def create_env_file():
    """Cria arquivo .env com configurações básicas"""
    
    env_template = """# ====================================
# CONFIGURAÇÃO SPORTMONKS API
# ====================================
# Obtenha sua API key em: https://www.sportmonks.com/
SPORTMONKS_API_KEY={sportmonks_key}
SPORTMONKS_BASE_URL=https://api.sportmonks.com/v3/football

# ====================================
# CONFIGURAÇÃO SUPABASE
# ====================================
# Obtenha essas informações no painel do seu projeto Supabase
# Dashboard > Settings > API
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# ====================================
# CONFIGURAÇÕES DE ETL
# ====================================
RATE_LIMIT_PER_HOUR=3000
BATCH_SIZE=100
MAX_RETRIES=3
RETRY_DELAY=5
"""
    
    print("=" * 60)
    print("🚀 CONFIGURAÇÃO INICIAL DO BDFUT")
    print("=" * 60)
    print()
    
    # Verificar se .env já existe
    if Path(".env").exists():
        response = input("⚠️  Arquivo .env já existe. Deseja sobrescrever? (s/n): ")
        if response.lower() != 's':
            print("Configuração cancelada.")
            return False
    
    print("Por favor, forneça as seguintes informações:")
    print()
    
    # Coletar informações do Sportmonks
    print("1️⃣  SPORTMONKS API")
    print("   Acesse: https://www.sportmonks.com/")
    print("   Crie uma conta e obtenha sua API key")
    sportmonks_key = input("   Digite sua API key da Sportmonks: ").strip()
    
    if not sportmonks_key:
        print("❌ API key da Sportmonks é obrigatória!")
        return False
    
    print()
    print("2️⃣  SUPABASE")
    print("   Acesse: https://supabase.com/dashboard")
    print("   Crie um projeto ou use um existente")
    print("   Em Settings > API, copie a URL e a chave anon")
    
    supabase_url = input("   Digite a URL do Supabase (ex: https://xyz.supabase.co): ").strip()
    supabase_key = input("   Digite a chave anon do Supabase: ").strip()
    
    if not supabase_url or not supabase_key:
        print("❌ URL e chave do Supabase são obrigatórias!")
        return False
    
    # Criar arquivo .env
    env_content = env_template.format(
        sportmonks_key=sportmonks_key,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print()
    print("✅ Arquivo .env criado com sucesso!")
    print()
    
    return True

def show_next_steps():
    """Mostra os próximos passos após configuração"""
    
    print("=" * 60)
    print("📋 PRÓXIMOS PASSOS")
    print("=" * 60)
    print()
    print("1. Execute a migração no Supabase:")
    print("   - Acesse o SQL Editor no painel do Supabase")
    print("   - Cole e execute o conteúdo de: migrations/001_create_sportmonks_schema.sql")
    print()
    print("2. Teste a conexão:")
    print("   python3 main.py test-connection")
    print()
    print("3. Sincronize os dados base:")
    print("   python3 main.py sync-base")
    print()
    print("4. Sincronize as ligas principais:")
    print("   python3 main.py sync-leagues")
    print()
    print("5. Para sincronização completa:")
    print("   python3 main.py full-sync")
    print()
    print("Para mais comandos, use: python3 main.py --help")
    print()
    print("=" * 60)

def main():
    """Função principal"""
    
    # Verificar se está no diretório correto
    if not Path("main.py").exists():
        print("❌ Este script deve ser executado no diretório raiz do projeto BDFut")
        sys.exit(1)
    
    # Criar arquivo .env
    if create_env_file():
        show_next_steps()
        print("🎉 Configuração concluída com sucesso!")
    else:
        print("❌ Configuração não foi concluída")
        sys.exit(1)

if __name__ == "__main__":
    main()
