#!/usr/bin/env python3
"""
Script principal para enriquecer todas as tabelas do Supabase com dados da Sportmonks API
Este script coordena o processo completo de enriquecimento de dados
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set
from tqdm import tqdm

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
from bdfut.config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/Users/mhbutzke/Documents/BDFut/bdfut/bdfut/logs/enriquecimento_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnriquecimentoCompleto:
    """Classe principal para coordenar o enriquecimento completo das tabelas"""
    
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.supabase = SupabaseClient()
        self.main_leagues = Config.MAIN_LEAGUES
        
    def enriquecer_referees(self):
        """Enriquecer tabela de árbitros"""
        logger.info("🟨 Enriquecendo tabela REFEREES...")
        
        try:
            # Buscar árbitros da API
            referees = self.sportmonks.get_referees()
            
            if referees:
                self.supabase.upsert_referees(referees)
                logger.info(f"✅ {len(referees)} árbitros enriquecidos")
                return len(referees)
            else:
                logger.warning("⚠️ Nenhum árbitro encontrado na API")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer árbitros: {str(e)}")
            return 0
    
    def enriquecer_players_completos(self):
        """Enriquecer tabela de jogadores com dados completos"""
        logger.info("⚽ Enriquecendo tabela PLAYERS com dados completos...")
        
        try:
            # Buscar jogadores únicos dos eventos e lineups existentes
            players_set = set()
            
            # Players dos eventos
            events_response = self.supabase.client.table('match_events').select('player_id,player_name').not_.is_('player_id', 'null').execute()
            for event in events_response.data:
                player_id = event.get('player_id')
                player_name = event.get('player_name')
                if player_id and player_name:
                    players_set.add((player_id, player_name))
            
            # Players dos lineups
            lineups_response = self.supabase.client.table('match_lineups').select('player_id,player_name').not_.is_('player_id', 'null').execute()
            for lineup in lineups_response.data:
                player_id = lineup.get('player_id')
                player_name = lineup.get('player_name')
                if player_id and player_name:
                    players_set.add((player_id, player_name))
            
            logger.info(f"📊 {len(players_set)} jogadores únicos encontrados")
            
            # Enriquecer dados dos jogadores via API
            enriched_count = 0
            for player_id, player_name in tqdm(players_set, desc="Enriquecendo jogadores"):
                try:
                    # Buscar dados completos do jogador na API
                    player_data = self.sportmonks.get_player_by_id(player_id)
                    
                    if player_data:
                        # Preparar dados para inserção/atualização
                        insert_data = {
                            'sportmonks_id': player_id,
                            'name': player_data.get('name', player_name),
                            'common_name': player_data.get('common_name'),
                            'firstname': player_data.get('firstname'),
                            'lastname': player_data.get('lastname'),
                            'nationality': player_data.get('nationality'),
                            'position_id': player_data.get('position_id'),
                            'position_name': player_data.get('position_name'),
                            'date_of_birth': player_data.get('date_of_birth'),
                            'height': player_data.get('height'),
                            'weight': player_data.get('weight'),
                            'image_path': player_data.get('image_path'),
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        # Upsert do jogador
                        self.supabase.client.table('players').upsert(insert_data, on_conflict='sportmonks_id').execute()
                        enriched_count += 1
                    
                    # Pequena pausa para respeitar rate limit
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao enriquecer jogador {player_name} (ID: {player_id}): {str(e)}")
                    continue
            
            logger.info(f"✅ {enriched_count} jogadores enriquecidos com dados completos")
            return enriched_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer jogadores: {str(e)}")
            return 0
    
    def enriquecer_coaches(self):
        """Enriquecer tabela de técnicos"""
        logger.info("👨‍💼 Enriquecendo tabela COACHES...")
        
        try:
            # Buscar técnicos dos times existentes
            teams_response = self.supabase.client.table('teams').select('sportmonks_id,name').execute()
            
            coaches_set = set()
            enriched_count = 0
            
            for team in tqdm(teams_response.data, desc="Buscando técnicos"):
                team_id = team.get('sportmonks_id')
                team_name = team.get('name')
                
                if team_id:
                    try:
                        # Buscar técnicos do time na API
                        coaches = self.sportmonks.get_coaches_by_team(team_id)
                        
                        if coaches:
                            for coach in coaches:
                                coaches_set.add((
                                    coach.get('id'),
                                    coach.get('name'),
                                    coach.get('common_name'),
                                    coach.get('firstname'),
                                    coach.get('lastname'),
                                    coach.get('nationality'),
                                    coach.get('image_path')
                                ))
                        
                        time.sleep(0.1)  # Rate limit
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao buscar técnicos do time {team_name}: {str(e)}")
                        continue
            
            logger.info(f"📊 {len(coaches_set)} técnicos únicos encontrados")
            
            # Salvar técnicos
            for coach_data in coaches_set:
                try:
                    insert_data = {
                        'sportmonks_id': coach_data[0],
                        'name': coach_data[1],
                        'common_name': coach_data[2],
                        'firstname': coach_data[3],
                        'lastname': coach_data[4],
                        'nationality': coach_data[5],
                        'image_path': coach_data[6],
                        'created_at': datetime.now().isoformat()
                    }
                    
                    self.supabase.client.table('coaches').upsert(insert_data, on_conflict='sportmonks_id').execute()
                    enriched_count += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao salvar técnico: {str(e)}")
                    continue
            
            logger.info(f"✅ {enriched_count} técnicos enriquecidos")
            return enriched_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer técnicos: {str(e)}")
            return 0
    
    def enriquecer_venues_completos(self):
        """Enriquecer tabela de estádios com dados completos"""
        logger.info("🏟️ Enriquecendo tabela VENUES com dados completos...")
        
        try:
            # Buscar venues da API
            venues = self.sportmonks.get_venues()
            
            if venues:
                self.supabase.upsert_venues(venues)
                logger.info(f"✅ {len(venues)} estádios enriquecidos")
                return len(venues)
            else:
                logger.warning("⚠️ Nenhum estádio encontrado na API")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer estádios: {str(e)}")
            return 0
    
    def enriquecer_fixtures_detalhadas(self):
        """Enriquecer fixtures com dados mais detalhados"""
        logger.info("⚽ Enriquecendo FIXTURES com dados detalhados...")
        
        try:
            # Buscar fixtures que não têm dados completos
            fixtures_response = self.supabase.client.table('fixtures').select('sportmonks_id').limit(100).execute()
            
            enriched_count = 0
            
            for fixture in tqdm(fixtures_response.data, desc="Enriquecendo fixtures"):
                fixture_id = fixture.get('sportmonks_id')
                
                try:
                    # Buscar dados detalhados da fixture
                    detailed_fixture = self.sportmonks.get_fixture_by_id(
                        fixture_id,
                        include='participants;state;venue;events;statistics;lineups;referees'
                    )
                    
                    if detailed_fixture:
                        # Processar venues
                        if 'venue' in detailed_fixture and detailed_fixture['venue']:
                            self.supabase.upsert_venues([detailed_fixture['venue']])
                        
                        # Processar árbitros
                        if 'referees' in detailed_fixture and detailed_fixture['referees']:
                            self.supabase.upsert_referees(detailed_fixture['referees'])
                        
                        # Atualizar fixture
                        self.supabase.upsert_fixtures([detailed_fixture])
                        
                        # Processar participantes
                        if 'participants' in detailed_fixture:
                            self.supabase.upsert_fixture_participants(
                                fixture_id, detailed_fixture['participants']
                            )
                        
                        # Processar eventos
                        if 'events' in detailed_fixture and detailed_fixture['events']:
                            self.supabase.upsert_fixture_events(
                                fixture_id, detailed_fixture['events']
                            )
                        
                        enriched_count += 1
                    
                    time.sleep(0.2)  # Rate limit
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao enriquecer fixture {fixture_id}: {str(e)}")
                    continue
            
            logger.info(f"✅ {enriched_count} fixtures enriquecidas com dados detalhados")
            return enriched_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer fixtures: {str(e)}")
            return 0
    
    def gerar_relatorio_final(self):
        """Gerar relatório final do enriquecimento"""
        logger.info("📊 Gerando relatório final...")
        
        try:
            # Contar registros em todas as tabelas
            all_tables = [
                'leagues', 'seasons', 'teams', 'fixtures', 
                'match_events', 'match_statistics', 'match_lineups',
                'countries', 'states', 'types', 'venues', 
                'referees', 'players', 'coaches', 'stages'
            ]
            
            total_records = 0
            logger.info("\n📋 CONTAGEM FINAL DE REGISTROS:")
            logger.info("=" * 60)
            
            for table in all_tables:
                try:
                    response = self.supabase.client.table(table).select('*', count='exact').execute()
                    count = response.count
                    total_records += count
                    status = "✅" if count > 0 else "❌"
                    logger.info(f"{status} {table:20}: {count:>8,} registros")
                except Exception as e:
                    logger.warning(f"⚠️ {table:20}: erro ao contar - {e}")
            
            logger.info("=" * 60)
            logger.info(f"📊 TOTAL GERAL: {total_records:>8,} registros")
            
            # Estatísticas específicas
            logger.info("\n📈 ESTATÍSTICAS ESPECÍFICAS:")
            
            # Fixtures por status
            fixtures_status = self.supabase.client.table('fixtures').select('status').execute()
            status_counts = {}
            for fixture in fixtures_status.data:
                status = fixture.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            logger.info("⚽ Fixtures por status:")
            for status, count in status_counts.items():
                logger.info(f"   • {status}: {count:,}")
            
            # Players por posição
            players_pos = self.supabase.client.table('players').select('position_name').not_.is_('position_name', 'null').execute()
            pos_counts = {}
            for player in players_pos.data:
                pos = player.get('position_name', 'unknown')
                pos_counts[pos] = pos_counts.get(pos, 0) + 1
            
            logger.info("\n⚽ Players por posição:")
            for pos, count in pos_counts.items():
                logger.info(f"   • {pos}: {count:,}")
            
            # Countries por continente
            countries_continent = self.supabase.client.table('countries').select('continent_id').not_.is_('continent_id', 'null').execute()
            continent_counts = {}
            continent_names = {1: "Europa", 2: "América do Norte", 4: "América do Sul"}
            
            for country in countries_continent.data:
                cid = country.get('continent_id')
                continent_counts[cid] = continent_counts.get(cid, 0) + 1
            
            logger.info("\n🌍 Countries por continente:")
            for cid, count in continent_counts.items():
                continent_name = continent_names.get(cid, f"Continente {cid}")
                logger.info(f"   • {continent_name}: {count:,}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {str(e)}")
    
    def executar_enriquecimento_completo(self):
        """Executar processo completo de enriquecimento"""
        logger.info("=" * 80)
        logger.info("🚀 INICIANDO ENRIQUECIMENTO COMPLETO DAS TABELAS")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        total_enriched = 0
        
        # 1. Enriquecer árbitros
        total_enriched += self.enriquecer_referees()
        
        # 2. Enriquecer jogadores
        total_enriched += self.enriquecer_players_completos()
        
        # 3. Enriquecer técnicos
        total_enriched += self.enriquecer_coaches()
        
        # 4. Enriquecer estádios
        total_enriched += self.enriquecer_venues_completos()
        
        # 5. Enriquecer fixtures detalhadas
        total_enriched += self.enriquecer_fixtures_detalhadas()
        
        # Tempo total
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Relatório final
        logger.info("=" * 80)
        logger.info("📊 RELATÓRIO FINAL DO ENRIQUECIMENTO")
        logger.info("=" * 80)
        logger.info(f"⏱️ Tempo total: {duration}")
        logger.info(f"📈 Registros enriquecidos: {total_enriched:,}")
        
        # Gerar relatório detalhado
        self.gerar_relatorio_final()
        
        logger.info("=" * 80)
        logger.info("🎉 ENRIQUECIMENTO COMPLETO FINALIZADO!")
        logger.info("=" * 80)

def main():
    """Função principal"""
    
    logger.info("🚀 Iniciando processo de enriquecimento completo...")
    
    try:
        # Validar configurações
        Config.validate()
        logger.info("✅ Configurações validadas")
        
        # Executar enriquecimento
        enriquecimento = EnriquecimentoCompleto()
        enriquecimento.executar_enriquecimento_completo()
        
    except Exception as e:
        logger.error(f"❌ Erro no processo principal: {str(e)}")
        raise

if __name__ == "__main__":
    main()
