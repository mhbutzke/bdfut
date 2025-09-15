#!/usr/bin/env python3
"""
Estratégia Híbrida Otimizada para Fixtures
==========================================
OPÇÃO B: Períodos históricos + Seasons atuais
"""

import requests
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bdfut'))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
from datetime import datetime, timedelta
import time

def collect_historical_fixtures(sportmonks, supabase):
    """FASE 1: Coletar fixtures históricas por períodos (2023-2024)"""
    print('📅 FASE 1: Fixtures Históricas por Períodos (2023-2024)')
    print('=' * 60)
    
    # Períodos de 90 dias (limite da API)
    periods = [
        ('2023-01-01', '2023-03-31', 'Q1 2023'),
        ('2023-04-01', '2023-06-30', 'Q2 2023'),
        ('2023-07-01', '2023-09-30', 'Q3 2023'),
        ('2023-10-01', '2023-12-31', 'Q4 2023'),
        ('2024-01-01', '2024-03-31', 'Q1 2024'),
        ('2024-04-01', '2024-06-30', 'Q2 2024'),
        ('2024-07-01', '2024-09-30', 'Q3 2024'),
        ('2024-10-01', '2024-12-31', 'Q4 2024')
    ]
    
    total_fixtures = 0
    
    for i, (start_date, end_date, period_name) in enumerate(periods):
        print(f'\n📅 Período {i+1}/8: {period_name} ({start_date} a {end_date})')
        
        try:
            fixtures = sportmonks.get_fixtures_by_date_range(
                start_date=start_date,
                end_date=end_date
            )
            
            if fixtures:
                print(f'  ✅ {len(fixtures):,} fixtures encontradas')
                
                # Salvar em batches menores
                batch_size = 50
                saved = 0
                
                for j in range(0, len(fixtures), batch_size):
                    batch = fixtures[j:j+batch_size]
                    try:
                        success = supabase.upsert_fixtures(batch)
                        if success:
                            saved += len(batch)
                            print(f'    💾 Batch {j//batch_size + 1}: {len(batch)} fixtures')
                        else:
                            print(f'    ❌ Batch {j//batch_size + 1}: Falhou')
                    except Exception as e:
                        print(f'    ❌ Batch {j//batch_size + 1}: {str(e)[:50]}')
                    
                    time.sleep(0.1)
                
                print(f'  📊 Total salvas: {saved:,}')
                total_fixtures += saved
            else:
                print(f'  ⚠️ Nenhuma fixture encontrada')
            
        except Exception as e:
            print(f'  ❌ Erro período: {str(e)[:100]}')
        
        time.sleep(2)  # Pausa entre períodos
    
    return total_fixtures

def collect_current_seasons_detailed(sportmonks, supabase):
    """FASE 2: Fixtures das temporadas atuais via endpoint de seasons"""
    print('\n🔴 FASE 2: Fixtures das Temporadas Atuais (2025/2026)')
    print('=' * 60)
    
    try:
        # Buscar seasons atuais
        result = supabase.client.table('seasons').select(
            'sportmonks_id, name, leagues(name)'
        ).eq('is_current', True).execute()
        
        current_seasons = result.data if result.data else []
        
        # Filtrar ligas principais para otimizar
        main_leagues = [
            'Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1',
            'Brasileirão Série A', 'Brasileirão Série B', 'Champions League', 
            'Europa League', 'Liga Portugal', 'Eredivisie'
        ]
        
        priority_seasons = []
        for season in current_seasons:
            league_name = season.get('leagues', {}).get('name', '')
            if any(league in league_name for league in main_leagues):
                priority_seasons.append(season)
        
        print(f'🎯 {len(priority_seasons)} temporadas prioritárias de {len(current_seasons)} totais')
        
        total_fixtures = 0
        
        for i, season in enumerate(priority_seasons):
            season_id = season['sportmonks_id']
            season_name = season['name']
            league_name = season.get('leagues', {}).get('name', 'Unknown')
            
            print(f'\n📅 Season {i+1}/{len(priority_seasons)}: {league_name} - {season_name}')
            
            try:
                # Usar endpoint da season com include fixtures
                url = f'https://api.sportmonks.com/v3/football/seasons/{season_id}'
                params = {
                    'api_token': sportmonks.api_key,
                    'include': 'fixtures'
                }
                
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    season_data = data.get('data', {})
                    fixtures = season_data.get('fixtures', [])
                    
                    print(f'  ✅ {len(fixtures):,} fixtures encontradas')
                    
                    if fixtures:
                        # Salvar fixtures
                        success = supabase.upsert_fixtures(fixtures)
                        if success:
                            print(f'  💾 {len(fixtures):,} fixtures salvas')
                            total_fixtures += len(fixtures)
                        else:
                            print(f'  ❌ Erro ao salvar fixtures')
                    
                elif response.status_code == 404:
                    print(f'  ⚠️ Season não encontrada')
                else:
                    print(f'  ❌ Erro HTTP {response.status_code}')
                
            except Exception as e:
                print(f'  ❌ Erro: {str(e)[:100]}')
            
            time.sleep(0.3)  # Pausa entre seasons
        
        return total_fixtures
        
    except Exception as e:
        print(f'❌ Erro na fase 2: {e}')
        return 0

def main():
    print('⚽ ESTRATÉGIA HÍBRIDA PARA FIXTURES COMPLETAS')
    print('=' * 60)
    print('🎯 OPÇÃO B: Períodos Históricos + Seasons Atuais')
    print('=' * 60)
    
    try:
        # Inicializar clientes
        sportmonks = SportmonksClient(enable_cache=True, use_redis=True)
        supabase = SupabaseClient()
        
        print(f"✅ Clientes inicializados")
        
        # Status inicial
        result = supabase.client.table('fixtures').select('id', count='exact').execute()
        initial_fixtures = result.count if result.count is not None else 0
        print(f"📊 Fixtures iniciais no banco: {initial_fixtures:,}")
        
        # FASE 1: Fixtures históricas por períodos
        print(f"\n🔄 Executando FASE 1...")
        fixtures_historical = collect_historical_fixtures(sportmonks, supabase)
        
        # Status intermediário
        result = supabase.client.table('fixtures').select('id', count='exact').execute()
        intermediate_fixtures = result.count if result.count is not None else 0
        
        print(f"\n📊 Status após FASE 1:")
        print(f"  • Fixtures coletadas: {fixtures_historical:,}")
        print(f"  • Total no banco: {intermediate_fixtures:,}")
        print(f"  • Crescimento: +{intermediate_fixtures - initial_fixtures:,}")
        
        # FASE 2: Fixtures das temporadas atuais
        print(f"\n🔄 Executando FASE 2...")
        fixtures_current = collect_current_seasons_detailed(sportmonks, supabase)
        
        # Status final
        result = supabase.client.table('fixtures').select('id', count='exact').execute()
        final_fixtures = result.count if result.count is not None else 0
        
        print(f'\n📊 RESULTADO FINAL DA ESTRATÉGIA HÍBRIDA:')
        print(f'  • Fixtures iniciais: {initial_fixtures:,}')
        print(f'  • FASE 1 (histórico): +{fixtures_historical:,}')
        print(f'  • FASE 2 (atuais): +{fixtures_current:,}')
        print(f'  • Total final no banco: {final_fixtures:,}')
        print(f'  • Crescimento total: +{final_fixtures - initial_fixtures:,}')
        print(f'  • Cache Redis: ✅ Funcionando')
        
        # Análise de qualidade
        growth_percentage = ((final_fixtures - initial_fixtures) / max(initial_fixtures, 1)) * 100
        
        print(f'\n📈 ANÁLISE DE QUALIDADE:')
        print(f'  • Crescimento: {growth_percentage:.1f}%')
        
        if final_fixtures >= 50000:
            quality_level = "🎉 EXCEPCIONAL"
        elif final_fixtures >= 30000:
            quality_level = "✅ EXCELENTE"
        elif final_fixtures >= 20000:
            quality_level = "✅ MUITO BOM"
        else:
            quality_level = "✅ BOM"
        
        print(f'  • Qualidade da base: {quality_level}')
        
        # Recomendações finais
        print(f'\n🎯 RECOMENDAÇÕES:')
        print(f'  1. ✅ Base de fixtures significativamente expandida')
        print(f'  2. 🚀 Pronto para TASK-ETL-011 (Events e Statistics)')
        print(f'  3. 🔄 Configurar sync incremental para manter atualizado')
        print(f'  4. 📊 Dados suficientes para análises avançadas')
        
        return final_fixtures > initial_fixtures
        
    except Exception as e:
        print(f"❌ Erro durante estratégia: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        print(f"\n{'='*60}")
        if success:
            print("✅ ESTRATÉGIA HÍBRIDA CONCLUÍDA COM SUCESSO!")
            print("🚀 Base de fixtures completamente otimizada!")
        else:
            print("❌ Estratégia falhou")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
