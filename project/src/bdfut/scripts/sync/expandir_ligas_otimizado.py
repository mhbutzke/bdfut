#!/usr/bin/env python3
"""
Script OTIMIZADO de expansão - verifica dados existentes
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
    level=logging.WARNING,  # Reduzir verbosidade
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração das ligas
LIGAS_CONFIG = {
    # Brasil
    648: {'nome': 'Brasileirão Série A', 'pais': 'Brasil'},
    651: {'nome': 'Brasileirão Série B', 'pais': 'Brasil'},
    654: {'nome': 'Copa do Brasil', 'pais': 'Brasil'},
    
    # Argentina
    636: {'nome': 'Primera División', 'pais': 'Argentina'},
    
    # CONMEBOL
    1122: {'nome': 'Copa Libertadores', 'pais': 'CONMEBOL'},
    1116: {'nome': 'Copa Sudamericana', 'pais': 'CONMEBOL'},
    
    # UEFA
    2: {'nome': 'Champions League', 'pais': 'UEFA'},
    5: {'nome': 'Europa League', 'pais': 'UEFA'},
    
    # Inglaterra
    8: {'nome': 'Premier League', 'pais': 'Inglaterra'},
    9: {'nome': 'Championship', 'pais': 'Inglaterra'},
    
    # Outros países
    564: {'nome': 'LaLiga', 'pais': 'Espanha'},
    462: {'nome': 'Liga Portugal', 'pais': 'Portugal'},
    301: {'nome': 'Ligue 1', 'pais': 'França'},
    82: {'nome': 'Bundesliga', 'pais': 'Alemanha'},
    743: {'nome': 'Liga MX', 'pais': 'México'},
    779: {'nome': 'MLS', 'pais': 'EUA'}
}

def verificar_dados_existentes(supabase):
    """Verifica o que já existe no banco"""
    print("\n📊 Verificando dados existentes...")
    
    try:
        # Verificar fixtures por liga
        fixtures_data = supabase.table('fixtures').select('league_id, season_id').execute()
        
        dados_existentes = {}
        if fixtures_data.data:
            for f in fixtures_data.data:
                league_id = f.get('league_id')
                season_id = f.get('season_id')
                
                if league_id not in dados_existentes:
                    dados_existentes[league_id] = set()
                
                if season_id:
                    dados_existentes[league_id].add(season_id)
        
        # Mostrar resumo
        print(f"   ✅ {len(dados_existentes)} ligas com dados")
        for league_id, seasons in dados_existentes.items():
            if league_id in LIGAS_CONFIG:
                print(f"      • {LIGAS_CONFIG[league_id]['nome']}: {len(seasons)} temporadas")
        
        return dados_existentes
        
    except Exception as e:
        print(f"   ⚠️  Erro ao verificar: {e}")
        return {}

def processar_liga_rapido(sportmonks, supabase, league_id, league_info, dados_existentes, num_temporadas=3):
    """Processa liga evitando duplicações"""
    
    print(f"\n{'='*60}")
    print(f"🏆 {league_info['nome']} - Liga ID: {league_id}")
    print(f"{'='*60}")
    
    temporadas_existentes = dados_existentes.get(league_id, set())
    
    if temporadas_existentes:
        print(f"   ℹ️  {len(temporadas_existentes)} temporadas já existem")
    
    try:
        # Buscar temporadas
        print(f"   📅 Buscando temporadas...")
        response = sportmonks._make_request(
            f'/leagues/{league_id}',
            {'include': 'seasons'}
        )
        
        league_data = response.get('data', {})
        seasons = league_data.get('seasons', [])
        
        if not seasons:
            print(f"   ❌ Nenhuma temporada encontrada")
            return {'novas': 0, 'existentes': len(temporadas_existentes)}
        
        # Ordenar e filtrar temporadas
        seasons_sorted = sorted(seasons, 
                               key=lambda x: x.get('starting_at', ''), 
                               reverse=True)[:num_temporadas]
        
        # Filtrar apenas temporadas novas
        seasons_novas = [s for s in seasons_sorted if s.get('id') not in temporadas_existentes]
        
        if not seasons_novas:
            print(f"   ✅ Todas as temporadas já processadas")
            return {'novas': 0, 'existentes': len(temporadas_existentes)}
        
        print(f"   🆕 {len(seasons_novas)} temporadas novas para processar")
        
        # Processar apenas temporadas novas
        fixtures_novas = 0
        
        for season in seasons_novas:
            season_id = season.get('id')
            season_name = season.get('name')
            
            print(f"      📊 Processando: {season_name}")
            
            # Buscar fixtures
            response = sportmonks._make_request(
                f'/seasons/{season_id}',
                {'include': 'fixtures'}
            )
            
            fixtures_data = response.get('data', {}).get('fixtures', [])
            fixture_ids = [f.get('id') for f in fixtures_data if f.get('id')]
            
            if not fixture_ids:
                continue
            
            print(f"         • {len(fixture_ids)} fixtures encontradas")
            
            # Processar em lotes MENORES para evitar timeout
            batch_size = 10  # Reduzido
            includes = 'participants;scores;state'  # Simplificado por enquanto
            
            for i in range(0, len(fixture_ids), batch_size):
                batch_ids = fixture_ids[i:i + batch_size]
                batch_ids_str = ','.join(map(str, batch_ids))
                
                try:
                    # Buscar dados
                    response = sportmonks._make_request(
                        f'/fixtures/multi/{batch_ids_str}',
                        {'include': includes}
                    )
                    
                    fixtures_batch = response.get('data', [])
                    
                    # Salvar fixtures básicas
                    for fixture in fixtures_batch:
                        fixture_data = {
                            'sportmonks_id': fixture.get('id'),
                            'league_id': league_id,
                            'season_id': season_id,
                            'match_date': fixture.get('starting_at'),
                            'status': fixture.get('state', {}).get('state'),
                            'updated_at': datetime.utcnow().isoformat()
                        }
                        
                        # Times
                        for p in fixture.get('participants', []):
                            loc = (p.get('meta') or {}).get('location')
                            if loc == 'home':
                                fixture_data['home_team_id'] = p.get('id')
                                fixture_data['home_team_name'] = p.get('name')
                            elif loc == 'away':
                                fixture_data['away_team_id'] = p.get('id')
                                fixture_data['away_team_name'] = p.get('name')
                        
                        # Placar
                        for s in fixture.get('scores', []):
                            if s.get('description') in ('CURRENT', 'FT'):
                                if s.get('participant') == 'home':
                                    fixture_data['home_score'] = (s.get('score') or {}).get('goals')
                                elif s.get('participant') == 'away':
                                    fixture_data['away_score'] = (s.get('score') or {}).get('goals')
                        
                        # Salvar
                        try:
                            supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
                            fixtures_novas += 1
                        except Exception as e:
                            # Ignorar conflitos
                            if '409' not in str(e):
                                logger.debug(f"Erro: {e}")
                    
                    # Rate limit
                    time.sleep(0.3)
                    
                except Exception as e:
                    logger.warning(f"Erro no lote: {e}")
                    continue
                
                # Mostrar progresso
                if (i + batch_size) % 100 == 0 or i + batch_size >= len(fixture_ids):
                    print(f"         • Progresso: {min(i + batch_size, len(fixture_ids))}/{len(fixture_ids)}")
        
        print(f"   ✅ {fixtures_novas} fixtures novas salvas")
        return {'novas': fixtures_novas, 'existentes': len(temporadas_existentes)}
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return {'novas': 0, 'existentes': len(temporadas_existentes)}

def expandir_ligas_otimizado():
    """Versão otimizada da expansão"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 80)
    print("🚀 EXPANSÃO OTIMIZADA - MÚLTIPLAS LIGAS")
    print("=" * 80)
    print(f"📅 Início: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    print(f"🏆 {len(LIGAS_CONFIG)} ligas configuradas")
    
    # Verificar o que já existe
    dados_existentes = verificar_dados_existentes(supabase)
    
    # Estatísticas
    total_novas = 0
    total_existentes = 0
    ligas_processadas = 0
    
    # Processar cada liga
    for league_id, league_info in LIGAS_CONFIG.items():
        resultado = processar_liga_rapido(
            sportmonks, supabase, league_id, league_info, 
            dados_existentes, num_temporadas=3
        )
        
        total_novas += resultado['novas']
        total_existentes += resultado['existentes']
        ligas_processadas += 1
        
        # Pausa entre ligas
        time.sleep(1)
    
    # Relatório final
    print("\n" + "=" * 80)
    print("✅ EXPANSÃO CONCLUÍDA!")
    print("=" * 80)
    
    print(f"\n📊 RESUMO:")
    print(f"   • Ligas processadas: {ligas_processadas}/{len(LIGAS_CONFIG)}")
    print(f"   • Fixtures novas: {total_novas:,}")
    print(f"   • Temporadas já existentes: {total_existentes}")
    
    # Totais no banco
    try:
        fixtures = supabase.table('fixtures').select('*', count='exact').execute()
        print(f"\n📊 TOTAL NO BANCO:")
        print(f"   • Fixtures: {fixtures.count:,}")
        
        # Ligas com dados
        fixtures_data = supabase.table('fixtures').select('league_id').execute()
        if fixtures_data.data:
            unique_leagues = set(f['league_id'] for f in fixtures_data.data if f.get('league_id'))
            print(f"   • Ligas com dados: {len(unique_leagues)}")
            
            # Mostrar quais ligas
            print(f"\n📋 LIGAS NO BANCO:")
            for lid in sorted(unique_leagues):
                if lid in LIGAS_CONFIG:
                    # Contar fixtures da liga
                    count = sum(1 for f in fixtures_data.data if f.get('league_id') == lid)
                    print(f"   • {LIGAS_CONFIG[lid]['nome']}: {count} fixtures")
    
    except Exception as e:
        print(f"Erro ao buscar totais: {e}")
    
    print(f"\n📅 Término: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    print("=" * 80)

if __name__ == "__main__":
    expandir_ligas_otimizado()
