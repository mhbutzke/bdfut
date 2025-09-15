#!/usr/bin/env python3
"""
PASSO 1: Popular tabelas leagues e seasons (VERSÃO AJUSTADA)
Usando apenas colunas existentes no banco
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dados das ligas e temporadas
LIGAS_E_TEMPORADAS = {
    648: {
        'nome': 'Brasileirão Série A',
        'pais': 'Brasil',
        'temporadas': {
            25184: {'nome': '2025', 'inicio': '2025-03-29', 'fim': '2025-12-21', 'atual': True},
            23265: {'nome': '2024', 'inicio': '2024-04-13', 'fim': '2024-12-08', 'atual': False},
            21207: {'nome': '2023', 'inicio': '2023-04-15', 'fim': '2023-12-07', 'atual': False}
        }
    },
    651: {
        'nome': 'Brasileirão Série B',
        'pais': 'Brasil',
        'temporadas': {
            25185: {'nome': '2025', 'inicio': '2025-04-04', 'fim': '2025-11-22', 'atual': True},
            23291: {'nome': '2024', 'inicio': '2024-04-19', 'fim': '2024-11-24', 'atual': False},
            21210: {'nome': '2023', 'inicio': '2023-04-14', 'fim': '2023-11-25', 'atual': False}
        }
    },
    654: {
        'nome': 'Copa do Brasil',
        'pais': 'Brasil',
        'temporadas': {
            25165: {'nome': '2025', 'inicio': '2025-02-18', 'fim': '2025-08-08', 'atual': True},
            23161: {'nome': '2024', 'inicio': '2024-02-20', 'fim': '2024-11-10', 'atual': False},
            21194: {'nome': '2023', 'inicio': '2023-02-21', 'fim': '2023-09-24', 'atual': False}
        }
    },
    636: {
        'nome': 'Primera División',
        'pais': 'Argentina',
        'temporadas': {
            24969: {'nome': '2025', 'inicio': '2025-01-23', 'fim': '2025-11-16', 'atual': True},
            23024: {'nome': '2024', 'inicio': '2024-05-10', 'fim': '2024-12-17', 'atual': False},
            20873: {'nome': '2023', 'inicio': '2023-01-27', 'fim': '2023-07-30', 'atual': False}
        }
    },
    1122: {
        'nome': 'Copa Libertadores',
        'pais': 'CONMEBOL',
        'temporadas': {
            24957: {'nome': '2025', 'inicio': '2025-02-05', 'fim': '2025-08-22', 'atual': True},
            22969: {'nome': '2024', 'inicio': '2024-02-07', 'fim': '2024-11-30', 'atual': False},
            21019: {'nome': '2023', 'inicio': '2023-02-08', 'fim': '2023-11-04', 'atual': False}
        }
    },
    1116: {
        'nome': 'Copa Sudamericana',
        'pais': 'CONMEBOL',
        'temporadas': {
            24955: {'nome': '2025', 'inicio': '2025-03-05', 'fim': '2025-08-22', 'atual': True},
            22971: {'nome': '2024', 'inicio': '2024-03-05', 'fim': '2024-11-23', 'atual': False},
            21020: {'nome': '2023', 'inicio': '2023-03-07', 'fim': '2023-10-28', 'atual': False}
        }
    },
    2: {
        'nome': 'Champions League',
        'pais': 'UEFA',
        'temporadas': {
            25580: {'nome': '2025/2026', 'inicio': '2025-07-08', 'fim': '2026-05-31', 'atual': True},
            23619: {'nome': '2024/2025', 'inicio': '2024-07-09', 'fim': '2025-05-31', 'atual': False},
            21638: {'nome': '2023/2024', 'inicio': '2023-06-27', 'fim': '2024-06-01', 'atual': False}
        }
    },
    5: {
        'nome': 'Europa League',
        'pais': 'UEFA',
        'temporadas': {
            25582: {'nome': '2025/2026', 'inicio': '2025-07-10', 'fim': '2026-05-21', 'atual': True},
            23620: {'nome': '2024/2025', 'inicio': '2024-07-11', 'fim': '2025-05-21', 'atual': False},
            22130: {'nome': '2023/2024', 'inicio': '2023-08-08', 'fim': '2024-05-22', 'atual': False}
        }
    },
    8: {
        'nome': 'Premier League',
        'pais': 'Inglaterra',
        'temporadas': {
            25583: {'nome': '2025/2026', 'inicio': '2025-08-15', 'fim': '2026-05-24', 'atual': True},
            23614: {'nome': '2024/2025', 'inicio': '2024-08-16', 'fim': '2025-05-25', 'atual': False},
            21646: {'nome': '2023/2024', 'inicio': '2023-08-11', 'fim': '2024-05-19', 'atual': False}
        }
    },
    9: {
        'nome': 'Championship',
        'pais': 'Inglaterra',
        'temporadas': {
            25648: {'nome': '2025/2026', 'inicio': '2025-08-08', 'fim': '2026-05-02', 'atual': True},
            23672: {'nome': '2024/2025', 'inicio': '2024-08-09', 'fim': '2025-05-24', 'atual': False},
            21689: {'nome': '2023/2024', 'inicio': '2023-08-04', 'fim': '2024-05-26', 'atual': False}
        }
    },
    564: {
        'nome': 'La Liga',
        'pais': 'Espanha',
        'temporadas': {
            25659: {'nome': '2025/2026', 'inicio': '2025-08-15', 'fim': '2026-05-24', 'atual': True},
            23621: {'nome': '2024/2025', 'inicio': '2024-08-15', 'fim': '2025-05-25', 'atual': False},
            21694: {'nome': '2023/2024', 'inicio': '2023-08-11', 'fim': '2024-05-26', 'atual': False}
        }
    },
    462: {
        'nome': 'Liga Portugal',
        'pais': 'Portugal',
        'temporadas': {
            25745: {'nome': '2025/2026', 'inicio': '2025-08-08', 'fim': '2026-05-17', 'atual': True},
            23793: {'nome': '2024/2025', 'inicio': '2024-08-09', 'fim': '2025-05-17', 'atual': False},
            21825: {'nome': '2023/2024', 'inicio': '2023-08-11', 'fim': '2024-05-18', 'atual': False}
        }
    },
    301: {
        'nome': 'Ligue 1',
        'pais': 'França',
        'temporadas': {
            25651: {'nome': '2025/2026', 'inicio': '2025-08-15', 'fim': '2026-05-16', 'atual': True},
            23643: {'nome': '2024/2025', 'inicio': '2024-08-16', 'fim': '2025-05-17', 'atual': False},
            21779: {'nome': '2023/2024', 'inicio': '2023-08-11', 'fim': '2024-05-19', 'atual': False}
        }
    },
    82: {
        'nome': 'Bundesliga',
        'pais': 'Alemanha',
        'temporadas': {
            25646: {'nome': '2025/2026', 'inicio': '2025-08-22', 'fim': '2026-05-16', 'atual': True},
            23744: {'nome': '2024/2025', 'inicio': '2024-08-23', 'fim': '2025-05-17', 'atual': False},
            21795: {'nome': '2023/2024', 'inicio': '2023-08-18', 'fim': '2024-05-18', 'atual': False}
        }
    },
    743: {
        'nome': 'Liga MX',
        'pais': 'México',
        'temporadas': {}
    },
    779: {
        'nome': 'MLS',
        'pais': 'Estados Unidos',
        'temporadas': {}
    }
}

def popular_leagues(sportmonks, supabase):
    """Popula a tabela leagues com colunas existentes"""
    print("\n" + "="*80)
    print("📊 POPULANDO TABELA LEAGUES")
    print("="*80)
    
    leagues_salvas = 0
    
    for league_id, info in LIGAS_E_TEMPORADAS.items():
        try:
            print(f"\n🏆 {info['nome']} (ID: {league_id})")
            
            # Buscar dados da liga
            response = sportmonks._make_request(f'/leagues/{league_id}')
            league_data = response.get('data', {})
            
            # Preparar dados APENAS com colunas existentes
            league_record = {
                'sportmonks_id': league_id,  # Usar sportmonks_id ao invés de id
                'name': info['nome'],
                'country': info['pais'],
                'logo_url': league_data.get('image_path'),
                'active': league_data.get('active', True),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Salvar no Supabase
            supabase.table('leagues').upsert(league_record, on_conflict='sportmonks_id').execute()
            leagues_salvas += 1
            print(f"   ✅ Liga salva com sucesso")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        time.sleep(0.2)
    
    print(f"\n✅ Total de ligas salvas: {leagues_salvas}")
    return leagues_salvas

def popular_seasons(sportmonks, supabase):
    """Popula a tabela seasons com colunas existentes"""
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
                # Buscar dados completos (opcional)
                try:
                    response = sportmonks._make_request(f'/seasons/{season_id}')
                    season_data = response.get('data', {})
                except:
                    season_data = {}
                
                # Preparar dados APENAS com colunas existentes
                season_record = {
                    'sportmonks_id': season_id,  # Usar sportmonks_id ao invés de id
                    'league_id': league_id,
                    'name': season_info['nome'],
                    'current': season_info['atual'],  # Usar 'current' ao invés de 'is_current'
                    'start_date': season_info['inicio'],
                    'end_date': season_info['fim'],
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # Salvar no Supabase
                supabase.table('seasons').upsert(season_record, on_conflict='sportmonks_id').execute()
                seasons_salvas += 1
                print(f"   ✅ Temporada {season_info['nome']} salva")
                
            except Exception as e:
                print(f"   ❌ Erro na temporada {season_id}: {e}")
            
            time.sleep(0.2)
    
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
        print(f"\n📋 LEAGUES POPULADAS:")
        leagues_data = supabase.table('leagues').select('sportmonks_id, name').execute()
        
        for league in leagues_data.data[:10]:  # Mostrar só as primeiras 10
            league_id = league.get('sportmonks_id')
            league_name = league.get('name')
            
            # Contar temporadas dessa liga
            seasons_count = supabase.table('seasons').select('sportmonks_id', count='exact').eq('league_id', league_id).execute()
            
            if seasons_count.count > 0:
                print(f"   • {league_name}: {seasons_count.count} temporadas")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar status: {e}")

def main():
    """Função principal"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 80)
    print("🎯 PASSO 1: ESTRUTURAR BANCO DE DADOS (v2)")
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
