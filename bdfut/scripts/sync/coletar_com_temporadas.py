#!/usr/bin/env python3
"""
Coleta OTIMIZADA usando dados das temporadas do arquivo
Usa os IDs exatos das temporadas para coleta precisa
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
    level=logging.WARNING,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dados extraídos do arquivo - últimas 3 temporadas de cada liga
DADOS_TEMPORADAS = {
    648: {  # Brasileirão Série A
        'nome': 'Brasileirão Série A',
        'temporadas': [25184, 23265, 21207],  # 2025, 2024, 2023
        'pais': 'Brasil'
    },
    651: {  # Brasileirão Série B
        'nome': 'Brasileirão Série B', 
        'temporadas': [25185, 23291, 21210],  # 2025, 2024, 2023
        'pais': 'Brasil'
    },
    654: {  # Copa do Brasil
        'nome': 'Copa do Brasil',
        'temporadas': [25165, 23161, 21194],  # 2025, 2024, 2023
        'pais': 'Brasil'
    },
    636: {  # Primera División Argentina
        'nome': 'Primera División',
        'temporadas': [24969, 23024, 20873],  # 2025, 2024, 2023
        'pais': 'Argentina'
    },
    1122: {  # Copa Libertadores
        'nome': 'Copa Libertadores',
        'temporadas': [24957, 22969, 21019],  # 2025, 2024, 2023
        'pais': 'CONMEBOL'
    },
    1116: {  # Copa Sudamericana
        'nome': 'Copa Sudamericana',
        'temporadas': [24955, 22971, 21020],  # 2025, 2024, 2023
        'pais': 'CONMEBOL'
    },
    2: {  # Champions League
        'nome': 'Champions League',
        'temporadas': [25580, 23619, 21638],  # 2025/26, 2024/25, 2023/24
        'pais': 'UEFA'
    },
    5: {  # Europa League
        'nome': 'Europa League',
        'temporadas': [25582, 23620, 22130],  # 2025/26, 2024/25, 2023/24
        'pais': 'UEFA'
    },
    8: {  # Premier League
        'nome': 'Premier League',
        'temporadas': [25583, 23614, 21646],  # 2025/26, 2024/25, 2023/24
        'pais': 'Inglaterra'
    },
    9: {  # Championship
        'nome': 'Championship',
        'temporadas': [25648, 23672, 21689],  # 2025/26, 2024/25, 2023/24
        'pais': 'Inglaterra'
    },
    564: {  # La Liga
        'nome': 'La Liga',
        'temporadas': [25659, 23621, 21694],  # 2025/26, 2024/25, 2023/24
        'pais': 'Espanha'
    },
    462: {  # Liga Portugal
        'nome': 'Liga Portugal',
        'temporadas': [25745, 23793, 21825],  # 2025/26, 2024/25, 2023/24
        'pais': 'Portugal'
    },
    301: {  # Ligue 1
        'nome': 'Ligue 1',
        'temporadas': [25651, 23643, 21779],  # 2025/26, 2024/25, 2023/24
        'pais': 'França'
    },
    82: {  # Bundesliga
        'nome': 'Bundesliga',
        'temporadas': [25646, 23744, 21795],  # 2025/26, 2024/25, 2023/24
        'pais': 'Alemanha'
    }
}

# Adicionar Liga MX e MLS (não estavam no arquivo)
DADOS_TEMPORADAS_EXTRAS = {
    743: {  # Liga MX
        'nome': 'Liga MX',
        'temporadas': None,  # Buscar via API
        'pais': 'México'
    },
    779: {  # MLS
        'nome': 'MLS',
        'temporadas': None,  # Buscar via API
        'pais': 'EUA'
    }
}

def verificar_fixtures_existentes(supabase):
    """Verifica quais fixtures já existem"""
    print("\n📊 Verificando dados existentes...")
    
    try:
        # Buscar todas as fixtures agrupadas por liga e temporada
        fixtures_data = supabase.table('fixtures').select('league_id, season_id, sportmonks_id').execute()
        
        existentes = {}
        if fixtures_data.data:
            for f in fixtures_data.data:
                league_id = f.get('league_id')
                season_id = f.get('season_id')
                
                if league_id not in existentes:
                    existentes[league_id] = {}
                
                if season_id not in existentes[league_id]:
                    existentes[league_id][season_id] = []
                
                existentes[league_id][season_id].append(f.get('sportmonks_id'))
        
        # Resumo
        total_fixtures = sum(len(fixtures) for seasons in existentes.values() for fixtures in seasons.values())
        print(f"   ✅ {total_fixtures:,} fixtures já no banco")
        print(f"   ✅ {len(existentes)} ligas com dados")
        
        return existentes
        
    except Exception as e:
        print(f"   ⚠️  Erro ao verificar: {e}")
        return {}

def coletar_temporada_otimizada(sportmonks, supabase, league_id, season_id, league_name, existentes):
    """Coleta fixtures de uma temporada específica"""
    
    # Verificar se já existe
    fixtures_existentes = existentes.get(league_id, {}).get(season_id, [])
    
    if fixtures_existentes:
        print(f"      • Temporada {season_id}: {len(fixtures_existentes)} fixtures já existem")
        return 0
    
    print(f"      • Temporada {season_id}: ", end='')
    
    try:
        # Buscar temporada com fixtures
        response = sportmonks._make_request(
            f'/seasons/{season_id}',
            {'include': 'fixtures'}
        )
        
        fixtures = response.get('data', {}).get('fixtures', [])
        fixture_ids = [f.get('id') for f in fixtures if f.get('id')]
        
        if not fixture_ids:
            print("0 fixtures")
            return 0
        
        print(f"{len(fixture_ids)} fixtures", end='')
        
        # Processar em lotes
        batch_size = 20
        includes = 'participants;scores;state;venue'
        fixtures_salvas = 0
        
        for i in range(0, len(fixture_ids), batch_size):
            batch_ids = fixture_ids[i:i + batch_size]
            batch_ids_str = ','.join(map(str, batch_ids))
            
            try:
                # Buscar dados completos
                response = sportmonks._make_request(
                    f'/fixtures/multi/{batch_ids_str}',
                    {'include': includes}
                )
                
                fixtures_batch = response.get('data', [])
                
                # Salvar cada fixture
                for fixture in fixtures_batch:
                    fixture_data = {
                        'sportmonks_id': fixture.get('id'),
                        'league_id': league_id,
                        'season_id': season_id,
                        'match_date': fixture.get('starting_at'),
                        'status': fixture.get('state', {}).get('state'),
                        'venue': fixture.get('venue', {}).get('name') if fixture.get('venue') else None,
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    
                    # Times e placar
                    for p in fixture.get('participants', []):
                        loc = (p.get('meta') or {}).get('location')
                        if loc == 'home':
                            fixture_data['home_team_id'] = p.get('id')
                            fixture_data['home_team_name'] = p.get('name')
                        elif loc == 'away':
                            fixture_data['away_team_id'] = p.get('id')
                            fixture_data['away_team_name'] = p.get('name')
                    
                    for s in fixture.get('scores', []):
                        if s.get('description') in ('CURRENT', 'FT'):
                            if s.get('participant') == 'home':
                                fixture_data['home_score'] = (s.get('score') or {}).get('goals')
                            elif s.get('participant') == 'away':
                                fixture_data['away_score'] = (s.get('score') or {}).get('goals')
                    
                    try:
                        supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
                        fixtures_salvas += 1
                    except:
                        pass  # Ignorar duplicatas
                
                # Rate limit
                time.sleep(0.2)
                
            except Exception as e:
                logger.debug(f"Erro no lote: {e}")
                continue
        
        print(f" → {fixtures_salvas} salvas")
        return fixtures_salvas
        
    except Exception as e:
        print(f"erro: {e}")
        return 0

def buscar_temporadas_extras(sportmonks, league_id):
    """Busca temporadas para ligas não documentadas"""
    try:
        response = sportmonks._make_request(
            f'/leagues/{league_id}',
            {'include': 'seasons'}
        )
        
        seasons = response.get('data', {}).get('seasons', [])
        if seasons:
            # Ordenar por data e pegar as 3 mais recentes
            seasons_sorted = sorted(seasons, 
                                   key=lambda x: x.get('starting_at', ''), 
                                   reverse=True)[:3]
            
            return [s.get('id') for s in seasons_sorted if s.get('id')]
    except:
        return None
    
    return None

def coletar_com_temporadas():
    """Coleta usando IDs exatos das temporadas"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 80)
    print("🎯 COLETA OTIMIZADA COM IDs DAS TEMPORADAS")
    print("=" * 80)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    print(f"📊 14 ligas principais + 2 extras")
    print(f"📅 3 temporadas por liga")
    
    # Verificar o que já existe
    existentes = verificar_fixtures_existentes(supabase)
    
    total_fixtures = 0
    ligas_processadas = 0
    tempo_inicio = datetime.now()
    
    # ============================================
    # PROCESSAR LIGAS COM DADOS CONHECIDOS
    # ============================================
    print("\n" + "="*80)
    print("📌 LIGAS COM TEMPORADAS CONHECIDAS")
    print("="*80)
    
    # Ordenar por prioridade (Brasil primeiro, depois Europa, depois resto)
    ligas_ordenadas = sorted(DADOS_TEMPORADAS.items(), 
                             key=lambda x: (0 if 'Brasil' in x[1]['pais'] else 
                                          1 if x[1]['pais'] in ['UEFA', 'Inglaterra', 'Espanha'] else 2,
                                          x[0]))
    
    for league_id, info in ligas_ordenadas:
        print(f"\n{'='*60}")
        print(f"🏆 {info['nome']} ({info['pais']}) - Liga ID: {league_id}")
        print(f"{'='*60}")
        
        liga_fixtures = 0
        
        for season_id in info['temporadas'][:2]:  # Pegar só 2 temporadas por enquanto
            fixtures = coletar_temporada_otimizada(
                sportmonks, supabase, league_id, season_id, 
                info['nome'], existentes
            )
            liga_fixtures += fixtures
            time.sleep(0.3)
        
        if liga_fixtures > 0:
            total_fixtures += liga_fixtures
            ligas_processadas += 1
            print(f"   ✅ Total da liga: {liga_fixtures} fixtures")
    
    # ============================================
    # PROCESSAR LIGAS EXTRAS (MLS e Liga MX)
    # ============================================
    tempo_decorrido = (datetime.now() - tempo_inicio).seconds
    
    if tempo_decorrido < 900:  # Se menos de 15 minutos
        print("\n" + "="*80)
        print("📌 LIGAS EXTRAS")
        print("="*80)
        
        for league_id, info in DADOS_TEMPORADAS_EXTRAS.items():
            print(f"\n{'='*60}")
            print(f"🏆 {info['nome']} ({info['pais']}) - Liga ID: {league_id}")
            print(f"{'='*60}")
            
            # Buscar temporadas via API
            print("   🔍 Buscando temporadas...")
            temporadas = buscar_temporadas_extras(sportmonks, league_id)
            
            if temporadas:
                print(f"   ✅ {len(temporadas)} temporadas encontradas")
                
                liga_fixtures = 0
                for season_id in temporadas[:2]:  # Só 2 temporadas
                    fixtures = coletar_temporada_otimizada(
                        sportmonks, supabase, league_id, season_id, 
                        info['nome'], existentes
                    )
                    liga_fixtures += fixtures
                    time.sleep(0.3)
                
                if liga_fixtures > 0:
                    total_fixtures += liga_fixtures
                    ligas_processadas += 1
                    print(f"   ✅ Total da liga: {liga_fixtures} fixtures")
            else:
                print("   ❌ Não foi possível buscar temporadas")
    
    # ============================================
    # RELATÓRIO FINAL
    # ============================================
    tempo_total = (datetime.now() - tempo_inicio).seconds
    
    print("\n" + "=" * 80)
    print("✅ COLETA CONCLUÍDA!")
    print("=" * 80)
    
    print(f"\n📊 RESULTADOS:")
    print(f"   • Ligas processadas: {ligas_processadas}")
    print(f"   • Fixtures coletadas: {total_fixtures:,}")
    print(f"   • Tempo total: {tempo_total//60}min {tempo_total%60}s")
    
    # Verificar totais
    try:
        fixtures = supabase.table('fixtures').select('*', count='exact').execute()
        
        # Contar ligas e temporadas
        fixtures_data = supabase.table('fixtures').select('league_id, season_id').execute()
        unique_leagues = set()
        unique_seasons = set()
        
        if fixtures_data.data:
            for f in fixtures_data.data:
                unique_leagues.add(f.get('league_id'))
                unique_seasons.add(f.get('season_id'))
        
        print(f"\n📊 BANCO DE DADOS ATUALIZADO:")
        print(f"   • Total de fixtures: {fixtures.count:,}")
        print(f"   • Total de ligas: {len(unique_leagues)}")
        print(f"   • Total de temporadas: {len(unique_seasons)}")
        
        # Mostrar ligas com dados
        print(f"\n📋 LIGAS NO BANCO:")
        for lid in sorted(unique_leagues):
            if lid in DADOS_TEMPORADAS:
                count = sum(1 for f in fixtures_data.data if f.get('league_id') == lid)
                print(f"   • {DADOS_TEMPORADAS[lid]['nome']}: {count} fixtures")
    except:
        pass
    
    print("\n🎯 PRÓXIMO PASSO:")
    print("   → Execute: python3 enriquecer_com_eventos.py")
    print("   Para adicionar eventos, estatísticas e escalações")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    coletar_com_temporadas()
