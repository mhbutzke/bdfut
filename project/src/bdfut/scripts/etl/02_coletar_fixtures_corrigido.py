#!/usr/bin/env python3
"""
PASSO 2: Coletar fixtures por temporada (VERSÃO CORRIGIDA)
Usando apenas colunas existentes na tabela fixtures
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

def coletar_fixtures_por_temporada(sportmonks, supabase, season_id, season_name, league_name):
    """Coleta todas as fixtures de uma temporada específica"""
    
    print(f"\n📅 {season_name} ({league_name})")
    
    try:
        # PASSO 1: Buscar todos os fixture IDs da temporada
        print("   🔍 Buscando fixture IDs...")
        response = sportmonks._make_request(
            f'/seasons/{season_id}',
            {'include': 'fixtures'}
        )
        
        season_data = response.get('data', {})
        fixtures_data = season_data.get('fixtures', [])
        
        if not fixtures_data:
            print("   ⚠️  Nenhuma fixture encontrada")
            return 0
        
        fixture_ids = [f.get('id') for f in fixtures_data if f.get('id')]
        print(f"   📊 {len(fixture_ids)} fixtures encontradas")
        
        if not fixture_ids:
            print("   ⚠️  Nenhum ID válido encontrado")
            return 0
        
        # PASSO 2: Buscar detalhes das fixtures em lotes
        fixtures_salvas = 0
        batch_size = 25  # Sportmonks permite até 25 IDs por vez
        
        for i in range(0, len(fixture_ids), batch_size):
            batch_ids = fixture_ids[i:i + batch_size]
            ids_str = ','.join(map(str, batch_ids))
            
            print(f"   📦 Processando lote {i//batch_size + 1}/{(len(fixture_ids)-1)//batch_size + 1} ({len(batch_ids)} fixtures)")
            
            try:
                # Buscar detalhes das fixtures
                includes = 'participants;scores;state;venue;referees'
                response = sportmonks._make_request(
                    f'/fixtures/multi/{ids_str}',
                    {'include': includes}
                )
                
                fixtures_details = response.get('data', [])
                
                # Processar cada fixture
                for fixture in fixtures_details:
                    try:
                        # Preparar dados APENAS com colunas existentes
                        fixture_data = {
                            'sportmonks_id': fixture.get('id'),
                            'league_id': fixture.get('league_id'),
                            'season_id': fixture.get('season_id'),
                            'match_date': fixture.get('starting_at'),
                            'status': None,
                            'home_score': None,
                            'away_score': None,
                            'venue': None,
                            'referee': None,
                            'updated_at': datetime.utcnow().isoformat()
                        }
                        
                        # Extrair participantes (home/away teams)
                        participants = fixture.get('participants', [])
                        for participant in participants:
                            meta = participant.get('meta', {})
                            if meta.get('location') == 'home':
                                fixture_data['home_team_id'] = participant.get('id')
                            elif meta.get('location') == 'away':
                                fixture_data['away_team_id'] = participant.get('id')
                        
                        # Extrair scores
                        scores = fixture.get('scores', [])
                        for score in scores:
                            if score.get('participant') == 'home':
                                fixture_data['home_score'] = score.get('score', {}).get('goals')
                            elif score.get('participant') == 'away':
                                fixture_data['away_score'] = score.get('score', {}).get('goals')
                        
                        # Extrair status
                        state = fixture.get('state', {})
                        fixture_data['status'] = state.get('state') or state.get('name')
                        
                        # Extrair venue (nome simples)
                        venue = fixture.get('venue', {})
                        if venue:
                            fixture_data['venue'] = venue.get('name')
                        
                        # Extrair referee (nome simples)
                        referees = fixture.get('referees', [])
                        if referees:
                            referee_names = [r.get('name') for r in referees if r.get('name')]
                            fixture_data['referee'] = ', '.join(referee_names) if referee_names else None
                        
                        # Salvar no Supabase
                        supabase.table('fixtures').upsert(fixture_data, on_conflict='sportmonks_id').execute()
                        fixtures_salvas += 1
                        
                    except Exception as e:
                        print(f"      ❌ Erro ao processar fixture {fixture.get('id')}: {e}")
                
                print(f"      ✅ {len(fixtures_details)} fixtures processadas")
                
            except Exception as e:
                print(f"      ❌ Erro no lote: {e}")
            
            # Rate limit
            time.sleep(0.5)
        
        print(f"   ✅ Total: {fixtures_salvas} fixtures salvas")
        return fixtures_salvas
        
    except Exception as e:
        print(f"   ❌ Erro geral: {e}")
        return 0

def verificar_fixtures_existentes(supabase, season_id):
    """Verifica quantas fixtures já existem para uma temporada"""
    try:
        result = supabase.table('fixtures').select('sportmonks_id', count='exact').eq('season_id', season_id).execute()
        return result.count
    except:
        return 0

def main():
    """Função principal"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 80)
    print("🎯 PASSO 2: COLETAR FIXTURES POR TEMPORADA (CORRIGIDO)")
    print("=" * 80)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    print(f"📊 Objetivo: Coletar fixtures de todas as temporadas")
    
    tempo_inicio = datetime.now()
    
    # Buscar todas as temporadas do banco
    try:
        seasons = supabase.table('seasons').select('sportmonks_id, name, league_id').execute()
        seasons_data = seasons.data
        
        print(f"\n📋 {len(seasons_data)} temporadas encontradas no banco")
        
        total_fixtures_salvas = 0
        temporadas_processadas = 0
        
        for season in seasons_data:
            season_id = season.get('sportmonks_id')
            season_name = season.get('name')
            league_id = season.get('league_id')
            
            # Buscar nome da liga
            try:
                league = supabase.table('leagues').select('name').eq('sportmonks_id', league_id).execute()
                league_name = league.data[0].get('name') if league.data else f"Liga {league_id}"
            except:
                league_name = f"Liga {league_id}"
            
            # Verificar se já tem fixtures
            fixtures_existentes = verificar_fixtures_existentes(supabase, season_id)
            
            if fixtures_existentes > 0:
                print(f"\n⏭️  {season_name} ({league_name}) - {fixtures_existentes} fixtures já existem")
                continue
            
            # Coletar fixtures
            fixtures_salvas = coletar_fixtures_por_temporada(
                sportmonks, supabase, season_id, season_name, league_name
            )
            
            total_fixtures_salvas += fixtures_salvas
            temporadas_processadas += 1
            
            # Pausa entre temporadas
            time.sleep(1)
        
        # Status final
        print("\n" + "="*80)
        print("📊 STATUS FINAL")
        print("="*80)
        
        # Contar total de fixtures
        total_fixtures = supabase.table('fixtures').select('*', count='exact').execute()
        print(f"   • Total de fixtures no banco: {total_fixtures.count}")
        print(f"   • Fixtures coletadas nesta execução: {total_fixtures_salvas}")
        print(f"   • Temporadas processadas: {temporadas_processadas}")
        
        tempo_total = (datetime.now() - tempo_inicio).seconds
        
        print("\n" + "=" * 80)
        print("✅ COLETA DE FIXTURES CONCLUÍDA!")
        print("=" * 80)
        print(f"   • Tempo total: {tempo_total//60}min {tempo_total%60}s")
        print(f"   • Fixtures coletadas: {total_fixtures_salvas}")
        
        print("\n🎯 PRÓXIMO PASSO:")
        print("   → Execute: python3 03_enriquecer_fixtures_com_events.py")
        print("   Para coletar events, statistics e lineups")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()
