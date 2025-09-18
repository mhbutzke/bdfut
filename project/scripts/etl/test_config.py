#!/usr/bin/env python3
"""
Configuração de Teste para Batch Processing
==========================================

Configuração temporária para testes do sistema de batch processing.
"""

import os

# Configurações de teste (substitua pelos valores reais)
TEST_CONFIG = {
    'SPORTMONKS_API_KEY': 'test_token_123',  # Substitua pelo token real
    'SUPABASE_CONNECTION_STRING': 'postgresql://test:test@localhost:5432/testdb'  # Substitua pela string real
}

def setup_test_env():
    """Configura variáveis de ambiente para teste"""
    for key, value in TEST_CONFIG.items():
        os.environ[key] = value

if __name__ == "__main__":
    setup_test_env()
    print("✅ Variáveis de ambiente configuradas para teste")
    print("⚠️  Lembre-se de substituir pelos valores reais antes de executar!")
