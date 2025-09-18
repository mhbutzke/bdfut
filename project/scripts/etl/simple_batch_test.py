#!/usr/bin/env python3
"""
Teste Simples do Batch Processing
=================================

Teste básico para validar a implementação do batch processing
sem dependências externas.
"""

import os
import sys

# Configura variáveis de ambiente para teste
os.environ['SPORTMONKS_API_KEY'] = 'test_token_123'
os.environ['SUPABASE_CONNECTION_STRING'] = 'postgresql://test:test@localhost:5432/testdb'

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_batch_collector_import():
    """Testa se o módulo pode ser importado"""
    try:
        from etl.batch_collector import BatchCollector, SportmonksBatchAPI
        print("✅ Módulo batch_collector importado com sucesso")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
        return False

def test_sportmonks_api_creation():
    """Testa criação da API"""
    try:
        from etl.batch_collector import SportmonksBatchAPI
        api = SportmonksBatchAPI('test_token')
        print("✅ SportmonksBatchAPI criada com sucesso")
        print(f"   Base URL: {api.BASE_URL}")
        print(f"   Max Batch Size: {api.MAX_BATCH_SIZE}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar API: {e}")
        return False

def test_batch_collector_creation():
    """Testa criação do coletor"""
    try:
        from etl.batch_collector import BatchCollector
        collector = BatchCollector('test_token', 'test_connection')
        print("✅ BatchCollector criado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar coletor: {e}")
        return False

def test_config_validation():
    """Testa validação de configuração"""
    try:
        from etl.config import ETLConfig
        is_valid = ETLConfig.validate()
        if is_valid:
            print("✅ Configuração validada com sucesso")
        else:
            print("⚠️  Configuração de teste detectada")
        return True
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 Teste Simples do Batch Processing")
    print("=" * 40)
    
    tests = [
        ("Importação do módulo", test_batch_collector_import),
        ("Criação da API", test_sportmonks_api_creation),
        ("Criação do coletor", test_batch_collector_creation),
        ("Validação de configuração", test_config_validation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Implementação básica está funcionando.")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
    
    print("\n💡 Próximos passos:")
    print("   • Configurar variáveis de ambiente reais")
    print("   • Testar com dados reais da API Sportmonks")
    print("   • Integrar com sistema de monitoramento")

if __name__ == "__main__":
    main()
