#!/usr/bin/env python3
"""
Script para testar quais endpoints estão disponíveis no plano atual
==================================================================
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bdfut'))

from bdfut.core.sportmonks_client import SportmonksClient
import time

def test_endpoint_access(sportmonks, endpoint_name, test_function, description):
    """Testa acesso a um endpoint específico"""
    print(f"\n🔍 TESTANDO: {endpoint_name}")
    print(f"📋 Descrição: {description}")
    print("-" * 50)
    
    try:
        print(f"🔄 Executando teste...")
        result = test_function()
        
        if result is None:
            print(f"⚠️ Endpoint retornou None")
            return False, "empty_response"
        
        if isinstance(result, list):
            count = len(result)
            print(f"✅ DISPONÍVEL - {count} registros encontrados")
            if count > 0:
                sample = result[0]
                fields = len(sample.keys()) if isinstance(sample, dict) else 0
                print(f"📊 Campos por registro: {fields}")
                print(f"🔧 Exemplo de campos: {list(sample.keys())[:5] if isinstance(sample, dict) else 'N/A'}")
            return True, count
        else:
            print(f"✅ DISPONÍVEL - Resposta válida")
            return True, 1
            
    except Exception as e:
        error_msg = str(e).lower()
        
        if "you do not have access" in error_msg or "access to this endpoint" in error_msg:
            print(f"❌ RESTRITO PELO PLANO")
            return False, "plan_restriction"
        elif "does not exist" in error_msg or "not found" in error_msg:
            print(f"❌ ENDPOINT NÃO EXISTE")
            return False, "not_found"
        else:
            print(f"⚠️ ERRO TÉCNICO: {str(e)[:60]}")
            return False, "technical_error"

def main():
    print('🔍 TESTE DE ENDPOINTS DISPONÍVEIS NO PLANO ATUAL')
    print('=' * 70)
    
    sportmonks = SportmonksClient(enable_cache=True, use_redis=True)
    
    # LISTA COMPLETA DE ENDPOINTS PARA TESTAR
    endpoints_to_test = [
        {
            'name': 'transfers',
            'test_function': lambda: sportmonks._make_request('/transfers', {}, 'transfers'),
            'description': 'Transferências de jogadores',
            'priority': 'CRÍTICA',
            'estimated_value': '50.000+ registros'
        },
        {
            'name': 'expected_goals',
            'test_function': lambda: sportmonks._make_request('/expected', {}, 'expected'),
            'description': 'Expected Goals e métricas avançadas',
            'priority': 'CRÍTICA',
            'estimated_value': '200.000+ registros'
        },
        {
            'name': 'predictions',
            'test_function': lambda: sportmonks._make_request('/predictions', {}, 'predictions'),
            'description': 'Predições e probabilidades',
            'priority': 'CRÍTICA',
            'estimated_value': '100.000+ registros'
        },
        {
            'name': 'topscorers',
            'test_function': lambda: sportmonks._make_request('/topscorers', {}, 'topscorers'),
            'description': 'Rankings de artilheiros',
            'priority': 'ALTA',
            'estimated_value': '10.000+ registros'
        },
        {
            'name': 'team_squads',
            'test_function': lambda: sportmonks._make_request('/team-squads', {}, 'squads'),
            'description': 'Elencos de times por temporada',
            'priority': 'ALTA',
            'estimated_value': '50.000+ registros'
        },
        {
            'name': 'odds',
            'test_function': lambda: sportmonks._make_request('/odds', {}, 'odds'),
            'description': 'Odds de casas de apostas',
            'priority': 'ALTA',
            'estimated_value': '500.000+ registros'
        },
        {
            'name': 'news',
            'test_function': lambda: sportmonks._make_request('/news', {}, 'news'),
            'description': 'Notícias pré e pós-jogo',
            'priority': 'MÉDIA',
            'estimated_value': '100.000+ registros'
        },
        {
            'name': 'rounds',
            'test_function': lambda: sportmonks._make_request('/rounds', {}, 'rounds'),
            'description': 'Rodadas de campeonatos',
            'priority': 'MÉDIA',
            'estimated_value': '10.000+ registros'
        },
        {
            'name': 'stages',
            'test_function': lambda: sportmonks._make_request('/stages', {}, 'stages'),
            'description': 'Fases de competições',
            'priority': 'MÉDIA',
            'estimated_value': '5.000+ registros'
        },
        {
            'name': 'bookmakers',
            'test_function': lambda: sportmonks._make_request('/bookmakers', {}, 'bookmakers'),
            'description': 'Casas de apostas',
            'priority': 'BAIXA',
            'estimated_value': '1.000+ registros'
        }
    ]
    
    # Resultados do teste
    available_endpoints = []
    restricted_endpoints = []
    error_endpoints = []
    total_estimated_records = 0
    
    print(f"📊 TESTANDO {len(endpoints_to_test)} ENDPOINTS...")
    
    for i, endpoint in enumerate(endpoints_to_test):
        print(f"\n{'='*70}")
        print(f"📍 TESTE {i+1}/{len(endpoints_to_test)}: {endpoint['name'].upper()}")
        print(f"🎯 Prioridade: {endpoint['priority']}")
        print(f"📊 Valor estimado: {endpoint['estimated_value']}")
        
        success, result = test_endpoint_access(
            sportmonks, 
            endpoint['name'], 
            endpoint['test_function'],
            endpoint['description']
        )
        
        if success:
            available_endpoints.append({
                'name': endpoint['name'],
                'priority': endpoint['priority'],
                'count': result,
                'estimated_value': endpoint['estimated_value']
            })
            
            # Extrair número estimado
            try:
                estimated = int(endpoint['estimated_value'].split('+')[0].replace('.', '').replace(',', ''))
                total_estimated_records += estimated
            except:
                total_estimated_records += 10000  # Padrão
                
        elif result == "plan_restriction":
            restricted_endpoints.append({
                'name': endpoint['name'],
                'priority': endpoint['priority'],
                'reason': 'Restrito pelo plano'
            })
        else:
            error_endpoints.append({
                'name': endpoint['name'],
                'priority': endpoint['priority'],
                'reason': result
            })
        
        # Pausa entre testes
        time.sleep(1)
    
    # RELATÓRIO FINAL
    print(f"\n{'='*70}")
    print(f"📊 RELATÓRIO FINAL - ENDPOINTS DISPONÍVEIS")
    print("=" * 70)
    
    print(f"\n✅ ENDPOINTS DISPONÍVEIS ({len(available_endpoints)}):")
    for endpoint in available_endpoints:
        priority_icon = {
            'CRÍTICA': '🔴',
            'ALTA': '🟡', 
            'MÉDIA': '🟢',
            'BAIXA': '⚪'
        }.get(endpoint['priority'], '⚪')
        
        print(f"  {priority_icon} {endpoint['name']:15} - {endpoint['estimated_value']}")
    
    print(f"\n❌ ENDPOINTS RESTRITOS ({len(restricted_endpoints)}):")
    for endpoint in restricted_endpoints:
        print(f"  🚫 {endpoint['name']:15} - {endpoint['reason']}")
    
    print(f"\n⚠️ ENDPOINTS COM ERRO ({len(error_endpoints)}):")
    for endpoint in error_endpoints:
        print(f"  ⚠️ {endpoint['name']:15} - {endpoint['reason']}")
    
    print(f"\n📈 POTENCIAL TOTAL:")
    print(f"  • Endpoints disponíveis: {len(available_endpoints)}/{len(endpoints_to_test)}")
    print(f"  • Registros estimados: {total_estimated_records:,}")
    print(f"  • Taxa de disponibilidade: {(len(available_endpoints) / len(endpoints_to_test)) * 100:.1f}%")
    
    # RECOMENDAÇÕES
    print(f"\n🎯 RECOMENDAÇÕES:")
    
    if len(available_endpoints) >= 7:
        print(f"  🎉 EXCELENTE! Maioria dos endpoints disponível")
        print(f"  🚀 Implementar roadmap completo")
    elif len(available_endpoints) >= 4:
        print(f"  ✅ BOM! Endpoints principais disponíveis")
        print(f"  📊 Focar nos endpoints de maior prioridade")
    elif len(available_endpoints) >= 2:
        print(f"  ⚠️ LIMITADO! Poucos endpoints disponíveis")
        print(f"  🔧 Implementar estratégias de fallback")
    else:
        print(f"  ❌ CRÍTICO! Muito poucos endpoints")
        print(f"  💡 Focar em otimizar dados existentes")
    
    return {
        'available_count': len(available_endpoints),
        'restricted_count': len(restricted_endpoints),
        'total_estimated': total_estimated_records,
        'available_endpoints': [e['name'] for e in available_endpoints]
    }

if __name__ == "__main__":
    try:
        result = main()
        print(f"\n{'='*70}")
        print(f"🎯 TESTE CONCLUÍDO!")
        print(f"✅ Disponíveis: {result['available_count']}")
        print(f"❌ Restritos: {result['restricted_count']}")
        print(f"📊 Potencial: {result['total_estimated']:,} registros")
        print(f"🚀 Endpoints para implementar: {', '.join(result['available_endpoints'])}")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
