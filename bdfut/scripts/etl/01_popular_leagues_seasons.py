#!/usr/bin/env python3
"""
PASSO 1: Popular tabelas leagues e seasons
Estrutura hierárquica correta do banco de dados
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
import logging
from src.sportmonks_client import SportmonksClient
from supabase import create_client
from config.config import Config
import time
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dados das ligas e temporadas do arquivo
LIGAS_E_TEMPORADAS = {
    648: {
        'nome': 'Brasileirão Série A',
        'pais': 'Brasil',
        'tipo': 'domestic',
        'temporadas': {
            25184: {'nome': '2025', 'inicio': '2025-03-29', 'fim': '2025-12-21', 'atual': True},
            23265: {'nome': '2024', 'inicio': '2024-04-13', 'fim': '2024-12-08', 'atual': False},
            21207: {'nome': '2023', 'inicio': '2023-04-15', 'fim': '2023-12-07', 'atual': False},
            19434: {'nome': '2022', 'inicio': '2022-04-09', 'fim': '2022-11-13', 'atual': False}
        }
    },
    651: {
        'nome': 'Brasileirão Série B',
        'pais': 'Brasil',
        'tipo': 'domestic',
        'temporadas': {
            25185: {'nome': '2025', 'inicio': '2025-04-04', 'fim': '2025-11-22', 'atual': True},
            23291: {'nome': '2024', 'inicio': '2024-04-19', 'fim': '2024-11-24', 'atual': False},
            21210: {'nome': '2023', 'inicio': '2023-04-14', 'fim': '2023-11-25', 'atual': False}
        }
    },
    654: {
        'nome': 'Copa do Brasil',
        'pais': 'Brasil',
        'tipo': 'cup',
        'temporadas': {
            25165: {'nome': '2025', 'inicio': '2025-02-18', 'fim': '2025-08-08', 'atual': True},
            23161: {'nome': '2024', 'inicio': '2024-02-20', 'fim': '2024-11-10', 'atual': False},
            21194: {'nome': '2023', 'inicio': '2023-02-21', 'fim': '2023-09-24', 'atual': False}
        }
    },
    636: {
        'nome': 'Primera División',
        'pais': 'Argentina',
        'tipo': 'domestic',
        'temporadas': {
            24969: {'nome': '2025', 'inicio': '2025-01-23', 'fim': '2025-11-16', 'atual': True},
            23024: {'nome': '2024', 'inicio': '2024-05-10', 'fim': '2024-12-17', 'atual': False},
            20873: {'nome': '2023', 'inicio': '2023-01-27', 'fim': '2023-07-30', 'atual': False}
        }
    },
    1122: {
        'nome': 'Copa Libertadores',
        'pais': 'Internacional',
        'tipo': 'cup_international',
        'temporadas': {
            24957: {'nome': '2025', 'inicio': '2025-02-05', 'fim': '2025-08-22', 'atual': True},
            22969: {'nome': '2024', 'inicio': '2024-02-07', 'fim': '2024-11-30', 'atual': False},
            21019: {'nome': '2023', 'inicio': '2023-02-08', 'fim': '2023-11-04', 'atual': False}
        }
    },
    1116: {
        'nome': 'Copa Sudamericana',
        'pais': 'Internacional',
        'tipo': 'cup_international',
        'temporadas': {
            24955: {'nome': '2025', 'inicio': '2025-03-05', 'fim': '2025-08-22', 'atual': True},
            22971: {'nome': '2024', 'inicio': '2024-03-05', 'fim': '2024-11-23', 'atual': False},
            21020: {'nome': '2023', 'inicio': '2023-03-07', 'fim': '2023-10-28', 'atual': False}
        }
    },
    2: {
        'nome': 'Champions League',
        'pais': 'Europa',
        'tipo': 'cup_international',
        'temporadas': {
            25580: {'nome': '2025/2026', 'inicio': '2025-07-08', 'fim': '2025-09-16', 'atual': True},
            23619: {'nome': '2024/2025', 'inicio': '2024-07-09', 'fim': '2025-05-31', 'atual': False},
            21638: {'nome': '2023/2024', 'inicio': '2023-06-27', 'fim': '2024-06-01', 'atual': False}
        }
    },
    5: {
        'nome': 'Europa League',
        'pais': 'Europa',
        'tipo': 'cup_international',
        'temporadas': {
            25582: {'nome': '2025/2026', 'inicio': '2025-07-10', 'fim': '2025-08-14', 'atual': True},
            23620: {'nome': '2024/2025', 'inicio': '2024-07-11', 'fim': '2025-05-21', 'atual': False},
            22130: {'nome': '2023/2024', 'inicio': '2023-08-08', 'fim': '2024-05-22', 'atual': False}
        }
    },
    8: {
        'nome': 'Premier League',
        'pais': 'Inglaterra',
        'tipo': 'domestic',
        'temporadas': {
            25583: {'nome': '2025/2026', 'inicio': '2025-08-15', 'fim': '2026-05-24', 'atual': True},
            23614: {'nome': '2024/2025', 'inicio': '2024-08-16', 'fim': '2025-05-25', 'atual': False},
            21646: {'nome': '2023/2024', 'inicio': '2023-08-11', 'fim': '2024-05-19', 'atual': False}
        }
    },
    9: {
        'nome': 'Championship',
        'pais': 'Inglaterra',
        'tipo': 'domestic',
        'temporadas': {
            25648: {'nome': '2025/2026', 'inicio': '2025-08-08', 'fim': '2026-05-02', 'atual': True},
            23672: {'nome': '2024/2025', 'inicio': '2024-08-09', 'fim': '2025-05-24', 'atual': False},
            21689: {'nome': '2023/2024', 'inicio': '2023-08-04', 'fim': '2024-05-26', 'atual': False}
        }
    },
    564: {
        'nome': 'La Liga',
        'pais': 'Espanha',
        'tipo': 'domestic',
        'temporadas': {
            25659: {'nome': '2025/2026', 'inicio': '2025-08-15', 'fim': '2026-05-24', 'atual': True},
            23621: {'nome': '2024/2025', 'inicio': '2024-08-15', 'fim': '2025-05-25', 'atual': False},
            21694: {'nome': '2023/2024', 'inicio': '2023-08-11', 'fim': '2024-05-26', 'atual': False}
        }
    },
    462: {
        'nome': 'Liga Portugal',
        'pais': 'Portugal',
        'tipo': 'domestic',
        'temporadas': {
            25745: {'nome': '2025/2026', 'inicio': '2025-08-08', 'fim': '2026-05-17', 'atual': True},
            23793: {'nome': '2024/2025', 'inicio': '2024-08-09', 'fim': '2025-05-17', 'atual': False},
            21825: {'nome': '2023/2024', 'inicio': '2023-08-11', 'fim': '2024-05-18', 'atual': False}
        }
    },
    301: {
        'nome': 'Ligue 1',
        'pais': 'França',
        'tipo': 'domestic',
        'temporadas': {
            25651: {'nome': '2025/2026', 'inicio': '2025-08-15', 'fim': '2026-05-16', 'atual': True},
            23643: {'nome': '2024/2025', 'inicio': '2024-08-16', 'fim': '2025-05-17', 'atual': False},
            21779: {'nome': '2023/2024', 'inicio': '2023-08-11', 'fim': '2024-05-19', 'atual': False}
        }
    },
    82: {
        'nome': 'Bundesliga',
        'pais': 'Alemanha',
        'tipo': 'domestic',
        'temporadas': {
            25646: {'nome': '2025/2026', 'inicio': '2025-08-22', 'fim': '2026-05-16', 'atual': True},
            23744: {'nome': '2024/2025', 'inicio': '2024-08-23', 'fim': '2025-05-17', 'atual': False},
            21795: {'nome': '2023/2024', 'inicio': '2023-08-18', 'fim': '2024-05-18', 'atual': False}
        }
    },
    743: {
        'nome': 'Liga MX',
        'pais': 'México',
        'tipo': 'domestic',
        'temporadas': {}  # Buscar via API
    },
    779: {
        'nome': 'MLS',
        'pais': 'Estados Unidos',
        'tipo': 'domestic',
        'temporadas': {}  # Buscar via API
    }
}

def popular_leagues(sportmonks, supabase):
    """Popula a tabela leagues"""
    print("\n" + "="*80)
    print("📊 POPULANDO TABELA LEAGUES")
    print("="*80)
    
    leagues_salvas = 0
    
    for league_id, info in LIGAS_E_TEMPORADAS.items():
        try:
            # Buscar dados completos da liga na API
            print(f"\n🏆 {info['nome']} (ID: {league_id})")
            
            response = sportmonks._make_request(f'/leagues/{league_id}')
            league_data = response.get('data', {})
            
            # Preparar dados para salvar
            league_record = {
                'id': league_id,
                'sport_id': league_data.get('sport_id', 1),
                'country_id': league_data.get('country_id'),
                'name': info['nome'],
                'active': league_data.get('active', True),
                'short_code': league_data.get('short_code'),
                'image_path': league_data.get('image_path'),
                'type': info['tipo'],
                'sub_type': league_data.get('sub_type'),
                'last_played_at': league_data.get('last_played_at'),
                'category': league_data.get('category'),
                'has_jerseys': league_data.get('has_jerseys', False),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Salvar no Supabase
            supabase.table('leagues').upsert(league_record, on_conflict='id').execute()
            leagues_salvas += 1
            print(f"   ✅ Liga salva com sucesso")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        time.sleep(0.2)  # Rate limit
    
    print(f"\n✅ Total de ligas salvas: {leagues_salvas}")
    return leagues_salvas

def popular_seasons(sportmonks, supabase):
    """Popula a tabela seasons"""
    print("\n" + "="*80)
    print("📅 POPULANDO TABELA SEASONS")
    print("="*80)
    
    seasons_salvas = 0
    
    for league_id, info in LIGAS_E_TEMPORADAS.items():
        print(f"\n🏆 {info['nome']} (ID: {league_id})")
        
        # Se não temos temporadas, buscar via API
        if not info['temporadas']:
            print("   🔍 Buscando temporadas via API...")
            try:
                response = sportmonks._make_request(
                    f'/leagues/{league_id}',
                    {'include': 'seasons'}
                )
                seasons = response.get('data', {}).get('seasons', [])
                
                # Pegar as 3 mais recentes
                seasons_sorted = sorted(seasons, 
                                       key=lambda x: x.get('starting_at', ''), 
                                       reverse=True)[:3]
                
                for season in seasons_sorted:
                    info['temporadas'][season.get('id')] = {
                        'nome': season.get('name'),
                        'inicio': season.get('starting_at'),
                        'fim': season.get('ending_at'),
                        'atual': season.get('is_current', False)
                    }
            except Exception as e:
                print(f"   ❌ Erro ao buscar temporadas: {e}")
                continue
        
        # Salvar cada temporada
        for season_id, season_info in info['temporadas'].items():
            try:
                # Buscar dados completos da temporada
                response = sportmonks._make_request(f'/seasons/{season_id}')
                season_data = response.get('data', {})
                
                # Preparar dados para salvar
                season_record = {
                    'id': season_id,
                    'sport_id': season_data.get('sport_id', 1),
                    'league_id': league_id,
                    'tie_breaker_rule_id': season_data.get('tie_breaker_rule_id'),
                    'name': season_info['nome'],
                    'finished': season_data.get('finished', not season_info['atual']),
                    'pending': season_data.get('pending', False),
                    'is_current': season_info['atual'],
                    'starting_at': season_info['inicio'],
                    'ending_at': season_info['fim'],
                    'standings_recalculated_at': season_data.get('standings_recalculated_at'),
                    'games_in_current_week': season_data.get('games_in_current_week', False),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # Salvar no Supabase
                supabase.table('seasons').upsert(season_record, on_conflict='id').execute()
                seasons_salvas += 1
                print(f"   ✅ Temporada {season_info['nome']} salva")
                
            except Exception as e:
                print(f"   ❌ Erro na temporada {season_id}: {e}")
            
            time.sleep(0.2)  # Rate limit
    
    print(f"\n✅ Total de temporadas salvas: {seasons_salvas}")
    return seasons_salvas

def verificar_status(supabase):
    """Verifica o status das tabelas"""
    print("\n" + "="*80)
    print("📊 STATUS DO BANCO DE DADOS")
    print("="*80)
    
    try:
        # Contar leagues
        leagues = supabase.table('leagues').select('*', count='exact').execute()
        print(f"   • Leagues: {leagues.count}")
        
        # Contar seasons
        seasons = supabase.table('seasons').select('*', count='exact').execute()
        print(f"   • Seasons: {seasons.count}")
        
        # Contar fixtures
        fixtures = supabase.table('fixtures').select('*', count='exact').execute()
        print(f"   • Fixtures: {fixtures.count}")
        
        # Listar leagues com temporadas
        print(f"\n📋 LEAGUES COM TEMPORADAS:")
        seasons_data = supabase.table('seasons').select('league_id, name').execute()
        
        leagues_with_seasons = {}
        for season in seasons_data.data:
            league_id = season.get('league_id')
            if league_id not in leagues_with_seasons:
                leagues_with_seasons[league_id] = []
            leagues_with_seasons[league_id].append(season.get('name'))
        
        for league_id, season_names in sorted(leagues_with_seasons.items()):
            if league_id in LIGAS_E_TEMPORADAS:
                league_name = LIGAS_E_TEMPORADAS[league_id]['nome']
                print(f"   • {league_name}: {len(season_names)} temporadas")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar status: {e}")

def main():
    """Função principal"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 80)
    print("🎯 PASSO 1: ESTRUTURAR BANCO DE DADOS")
    print("=" * 80)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    print(f"📊 Objetivo: Popular tabelas leagues e seasons")
    
    tempo_inicio = datetime.now()
    
    # Popular leagues
    leagues_salvas = popular_leagues(sportmonks, supabase)
    
    # Popular seasons
    seasons_salvas = popular_seasons(sportmonks, supabase)
    
    # Verificar status
    verificar_status(supabase)
    
    tempo_total = (datetime.now() - tempo_inicio).seconds
    
    print("\n" + "=" * 80)
    print("✅ ESTRUTURAÇÃO CONCLUÍDA!")
    print("=" * 80)
    print(f"   • Tempo total: {tempo_total//60}min {tempo_total%60}s")
    print(f"   • Leagues populadas: {leagues_salvas}")
    print(f"   • Seasons populadas: {seasons_salvas}")
    
    print("\n🎯 PRÓXIMO PASSO:")
    print("   → Execute: python3 02_coletar_fixtures_por_season.py")
    print("   Para coletar fixtures de cada temporada")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
