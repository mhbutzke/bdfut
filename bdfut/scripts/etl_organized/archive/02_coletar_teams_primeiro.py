#!/usr/bin/env python3
"""
PASSO 2A: Coletar teams primeiro, depois fixtures
Estratégia: coletar todos os times das temporadas antes de coletar fixtures
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

def coletar_teams_da_temporada(sportmonks, supabase, season_id, season_name, league_name):
    """Coleta todos os times de uma temporada específica"""
    
    print(f"\n📅 {season_name} ({league_name})")
    
    try:
        # PASSO 1: Buscar todos os fixture IDs da temporada
        print("   🔍 Buscando fixtures da temporada...")
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
        
        # PASSO 2: Buscar detalhes das fixtures para extrair teams
        teams_coletados = set()
        batch_size = 25
        
        for i in range(0, len(fixture_ids), batch_size):
            batch_ids = fixture_ids[i:i + batch_size]
            ids_str = ','.join(map(str, batch_ids))
            
            print(f"   📦 Processando lote {i//batch_size + 1}/{(len(fixture_ids)-1)//batch_size + 1}")
            
            try:
                # Buscar detalhes das fixtures
                includes = 'participants'
                response = sportmonks._make_request(
                    f'/fixtures/multi/{ids_str}',
                    {'include': includes}
                )
                
                fixtures_details = response.get('data', [])
                
                # Extrair team IDs dos participantes
                for fixture in fixtures_details:
                    participants = fixture.get('participants', [])
                    for participant in participants:
                        team_id = participant.get('id')
                        if team_id:
                            teams_coletados.add(team_id)
                
                print(f"      ✅ {len(fixtures_details)} fixtures processadas")
                
            except Exception as e:
                print(f"      ❌ Erro no lote: {e}")
            
            time.sleep(0.5)
        
        print(f"   📊 {len(teams_coletados)} teams únicos encontrados")
        
        # PASSO 3: Buscar detalhes dos teams e salvar
        teams_salvos = 0
        for team_id in teams_coletados:
            try:
                # Verificar se team já existe
                existing = supabase.table('teams').select('sportmonks_id').eq('sportmonks_id', team_id).execute()
                if existing.data:
                    continue  # Team já existe
                
                # Buscar detalhes do team
                response = sportmonks._make_request(f'/teams/{team_id}')
                team_data = response.get('data', {})
                
                if not team_data:
                    continue
                
                # Preparar dados do team
                team_record = {
                    'sportmonks_id': team_id,
                    'name': team_data.get('name'),
                    'short_code': team_data.get('short_code'),
                    'logo_url': team_data.get('image_path'),
                    'founded': team_data.get('founded'),
                    'venue_name': team_data.get('venue', {}).get('name') if team_data.get('venue') else None,
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # Salvar no Supabase
                supabase.table('teams').upsert(team_record, on_conflict='sportmonks_id').execute()
                teams_salvos += 1
                
            except Exception as e:
                print(f"      ❌ Erro ao processar team {team_id}: {e}")
            
            time.sleep(0.2)
        
        print(f"   ✅ {teams_salvos} teams novos salvos")
        return teams_salvos
        
    except Exception as e:
        print(f"   ❌ Erro geral: {e}")
        return 0

def main():
    """Função principal"""
    
    sportmonks = SportmonksClient()
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 80)
    print("🎯 PASSO 2A: COLETAR TEAMS PRIMEIRO")
    print("=" * 80)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    print(f"📊 Objetivo: Coletar todos os times das temporadas")
    
    tempo_inicio = datetime.now()
    
    # Buscar todas as temporadas do banco
    try:
        seasons = supabase.table('seasons').select('sportmonks_id, name, league_id').execute()
        seasons_data = seasons.data
        
        print(f"\n📋 {len(seasons_data)} temporadas encontradas no banco")
        
        total_teams_salvos = 0
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
            
            # Coletar teams desta temporada
            teams_salvos = coletar_teams_da_temporada(
                sportmonks, supabase, season_id, season_name, league_name
            )
            
            total_teams_salvos += teams_salvos
            temporadas_processadas += 1
            
            # Pausa entre temporadas
            time.sleep(1)
        
        # Status final
        print("\n" + "="*80)
        print("📊 STATUS FINAL")
        print("="*80)
        
        # Contar total de teams
        total_teams = supabase.table('teams').select('*', count='exact').execute()
        print(f"   • Total de teams no banco: {total_teams.count}")
        print(f"   • Teams coletados nesta execução: {total_teams_salvos}")
        print(f"   • Temporadas processadas: {temporadas_processadas}")
        
        tempo_total = (datetime.now() - tempo_inicio).seconds
        
        print("\n" + "=" * 80)
        print("✅ COLETA DE TEAMS CONCLUÍDA!")
        print("=" * 80)
        print(f"   • Tempo total: {tempo_total//60}min {tempo_total%60}s")
        print(f"   • Teams coletados: {total_teams_salvos}")
        
        print("\n🎯 PRÓXIMO PASSO:")
        print("   → Execute: python3 02_coletar_fixtures_corrigido.py")
        print("   Para coletar fixtures (agora com teams disponíveis)")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()
