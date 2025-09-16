"""
Cliente para interação com o Supabase
"""
from typing import Dict, Any, List, Optional
from supabase import create_client, Client
import logging
from datetime import datetime

from ..config.config import Config

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Cliente para interação com o banco de dados Supabase"""
    
    def __init__(self, use_service_role: bool = False):
        Config.validate()
        # Usar service_role_key se solicitado (para operações administrativas)
        key = Config.SUPABASE_SERVICE_KEY if use_service_role and Config.SUPABASE_SERVICE_KEY else Config.SUPABASE_KEY
        self.client: Client = create_client(Config.SUPABASE_URL, key)
    
    def upsert_countries(self, countries: List[Dict]) -> bool:
        """Insere ou atualiza países"""
        try:
            data = []
            for country in countries:
                data.append({
                    'id': country.get('id'),
                    'name': country.get('name'),
                    'official_name': country.get('official_name'),
                    'fifa_name': country.get('fifa_name'),
                    'iso2': country.get('iso2'),
                    'iso3': country.get('iso3'),
                    'latitude': country.get('latitude'),
                    'longitude': country.get('longitude'),
                    'borders': str(country.get('borders', [])),
                    'image_path': country.get('image_path'),
                    'updated_at': datetime.now().isoformat()
                })
            
            # Tentar usar schema sportmonks primeiro, senão usar public
            try:
                self.client.table('sportmonks.countries').upsert(data, on_conflict='id').execute()
            except:
                self.client.table('countries').upsert(data, on_conflict='id').execute()
                
            logger.info(f"Upserted {len(data)} countries")
            return True
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de países: {str(e)}")
            return False
    
    def upsert_leagues(self, leagues: List[Dict]) -> bool:
        """Insere ou atualiza ligas"""
        try:
            data = []
            for league in leagues:
                data.append({
                    'id': league.get('id'),
                    'sport_id': league.get('sport_id'),
                    'country_id': league.get('country_id'),
                    'name': league.get('name'),
                    'active': league.get('active', True),
                    'short_code': league.get('short_code'),
                    'image_path': league.get('image_path'),
                    'type': league.get('type'),
                    'sub_type': league.get('sub_type'),
                    'last_played_at': league.get('last_played_at'),
                    'category': league.get('category'),
                    'has_jerseys': league.get('has_jerseys', False),
                    'has_standings': league.get('has_standings', True),
                    'updated_at': datetime.now().isoformat()
                })
            
            self.client.table('leagues').upsert(data, on_conflict='id').execute()
            logger.info(f"Upserted {len(data)} leagues")
            return True
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de ligas: {str(e)}")
            return False
    
    def upsert_seasons(self, seasons: List[Dict]) -> bool:
        """Insere ou atualiza temporadas"""
        try:
            data = []
            for season in seasons:
                # Mapear apenas campos que existem na tabela
                season_data = {
                    'sportmonks_id': season.get('id'),
                    'sport_id': season.get('sport_id'),
                    'league_id': season.get('league_id'),
                    'name': season.get('name'),
                    'finished': season.get('finished', False),
                    'pending': season.get('pending', False),
                    'is_current': season.get('is_current', False),
                    'starting_at': season.get('starting_at'),
                    'ending_at': season.get('ending_at'),
                    'current_round_id': season.get('current_round_id'),
                    'current_stage_id': season.get('current_stage_id'),
                    'winner_id': season.get('winner_id'),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Remover campos None para não sobrescrever dados existentes
                season_data = {k: v for k, v in season_data.items() if v is not None}
                data.append(season_data)
            
            if data:
                self.client.table('seasons').upsert(data, on_conflict='sportmonks_id').execute()
                logger.info(f"Upserted {len(data)} seasons")
                return True
            else:
                logger.warning("Nenhuma season válida para upsert")
                return True
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de temporadas: {str(e)}")
            return False
    
    def upsert_teams(self, teams: List[Dict]) -> bool:
        """Insere ou atualiza times"""
        try:
            data = []
            for team in teams:
                data.append({
                    'id': team.get('id'),
                    'sport_id': team.get('sport_id'),
                    'country_id': team.get('country_id'),
                    'venue_id': team.get('venue_id'),
                    'name': team.get('name'),
                    'short_code': team.get('short_code'),
                    'twitter': team.get('twitter'),
                    'founded': team.get('founded'),
                    'logo_path': team.get('logo_path'),
                    'is_national_team': team.get('is_national_team', False),
                    'updated_at': datetime.now().isoformat()
                })
            
            self.client.table('teams').upsert(data, on_conflict='id').execute()
            logger.info(f"Upserted {len(data)} teams")
            return True
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de times: {str(e)}")
            return False
    
    def upsert_venues(self, venues: List[Dict]) -> bool:
        """Insere ou atualiza estádios"""
        try:
            data = []
            for venue in venues:
                # Mapear apenas campos que existem na tabela
                venue_data = {
                    'sportmonks_id': venue.get('id'),
                    'name': venue.get('name'),
                    'city': venue.get('city_name') or (venue.get('city', {}).get('name') if venue.get('city') else None),
                    'capacity': venue.get('capacity'),
                    'surface': venue.get('surface'),
                    'country': venue.get('country', {}).get('name') if venue.get('country') else None,
                    'image_path': venue.get('image_path'),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Remover campos None para não sobrescrever dados existentes
                venue_data = {k: v for k, v in venue_data.items() if v is not None}
                data.append(venue_data)
            
            if data:
                self.client.table('venues').upsert(data, on_conflict='sportmonks_id').execute()
                logger.info(f"Upserted {len(data)} venues")
                return True
            else:
                logger.warning("Nenhum venue válido para upsert")
                return True
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de estádios: {str(e)}")
            return False
    
    def upsert_referees(self, referees: List[Dict]) -> bool:
        """Insere ou atualiza árbitros"""
        try:
            data = []
            for referee in referees:
                # Mapear apenas campos que existem na tabela
                referee_data = {
                    'sportmonks_id': referee.get('id'),
                    'name': referee.get('name'),
                    'common_name': referee.get('common_name'),
                    'firstname': referee.get('firstname'),
                    'lastname': referee.get('lastname'),
                    'nationality': referee.get('nationality'),
                    'image_path': referee.get('image_path'),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Remover campos None para não sobrescrever dados existentes
                referee_data = {k: v for k, v in referee_data.items() if v is not None}
                data.append(referee_data)
            
            if data:
                self.client.table('referees').upsert(data, on_conflict='sportmonks_id').execute()
                logger.info(f"Upserted {len(data)} referees")
                return True
            else:
                logger.warning("Nenhum referee válido para upsert")
                return True
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de árbitros: {str(e)}")
            return False
    
    def upsert_fixtures(self, fixtures: List[Dict]) -> bool:
        """Insere ou atualiza partidas"""
        try:
            data = []
            for fixture in fixtures:
                # Mapear apenas campos que existem na tabela fixtures
                fixture_data = {
                    'sportmonks_id': fixture.get('id'),
                    'league_id': fixture.get('league_id'),
                    'season_id': fixture.get('season_id'),
                    'home_team_id': fixture.get('home_team_id'),
                    'away_team_id': fixture.get('away_team_id'),
                    'match_date': fixture.get('starting_at'),
                    'status': fixture.get('state', {}).get('short_name') if fixture.get('state') else None,
                    'home_score': fixture.get('scores', [{}])[0].get('goals') if fixture.get('scores') else None,
                    'away_score': fixture.get('scores', [{}])[1].get('goals') if len(fixture.get('scores', [])) > 1 else None,
                    'venue': fixture.get('venue', {}).get('name') if fixture.get('venue') else None,
                    'referee': fixture.get('referee', {}).get('name') if fixture.get('referee') else None,
                    'updated_at': datetime.now().isoformat()
                }
                
                # Remover campos None para não sobrescrever dados existentes
                fixture_data = {k: v for k, v in fixture_data.items() if v is not None}
                data.append(fixture_data)
            
            if data:
                self.client.table('fixtures').upsert(data, on_conflict='sportmonks_id').execute()
                logger.info(f"Upserted {len(data)} fixtures")
                return True
            else:
                logger.warning("Nenhuma fixture válida para upsert")
                return True
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de partidas: {str(e)}")
            return False
    
    def upsert_fixture_participants(self, fixture_id: int, participants: List[Dict]) -> bool:
        """Insere ou atualiza participantes de uma partida"""
        try:
            data = []
            for participant in participants:
                data.append({
                    'fixture_id': fixture_id,
                    'team_id': participant.get('id'),
                    'position': participant.get('meta', {}).get('location', 'home'),
                    'updated_at': datetime.now().isoformat()
                })
            
            # Remove participantes existentes antes de inserir novos
            self.client.table('fixture_participants').delete().eq('fixture_id', fixture_id).execute()
            self.client.table('fixture_participants').insert(data).execute()
            
            logger.info(f"Upserted {len(data)} participants for fixture {fixture_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de participantes: {str(e)}")
            return False
    
    def upsert_fixture_events(self, fixture_id: int, events: List[Dict]) -> bool:
        """Insere ou atualiza eventos de uma partida"""
        try:
            data = []
            for event in events:
                data.append({
                    'id': event.get('id'),
                    'fixture_id': fixture_id,
                    'period_id': event.get('period_id'),
                    'participant_id': event.get('participant_id'),
                    'type_id': event.get('type_id'),
                    'player_id': event.get('player_id'),
                    'related_player_id': event.get('related_player_id'),
                    'player_name': event.get('player_name'),
                    'related_player_name': event.get('related_player_name'),
                    'result': event.get('result'),
                    'info': event.get('info'),
                    'addition': event.get('addition'),
                    'minute': event.get('minute'),
                    'extra_minute': event.get('extra_minute'),
                    'injured': event.get('injured', False),
                    'on_bench': event.get('on_bench', False),
                    'updated_at': datetime.now().isoformat()
                })
            
            self.client.table('fixture_events').upsert(data, on_conflict='id').execute()
            logger.info(f"Upserted {len(data)} events for fixture {fixture_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de eventos: {str(e)}")
            return False
    
    def upsert_states(self, states: List[Dict]) -> bool:
        """Insere ou atualiza estados"""
        try:
            data = []
            for state in states:
                data.append({
                    'id': state.get('id'),
                    'state': state.get('state'),
                    'name': state.get('name'),
                    'short_name': state.get('short_name'),
                    'developer_name': state.get('developer_name'),
                    'updated_at': datetime.now().isoformat()
                })
            
            self.client.table('states').upsert(data, on_conflict='id').execute()
            logger.info(f"Upserted {len(data)} states")
            return True
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de estados: {str(e)}")
            return False
    
    def upsert_types(self, types: List[Dict]) -> bool:
        """Insere ou atualiza tipos"""
        try:
            data = []
            for type_item in types:
                data.append({
                    'id': type_item.get('id'),
                    'name': type_item.get('name'),
                    'code': type_item.get('code'),
                    'developer_name': type_item.get('developer_name'),
                    'model_type': type_item.get('model_type'),
                    'stat_group': type_item.get('stat_group'),
                    'updated_at': datetime.now().isoformat()
                })
            
            self.client.table('types').upsert(data, on_conflict='id').execute()
            logger.info(f"Upserted {len(data)} types")
            return True
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de tipos: {str(e)}")
            return False
    
    def upsert_players(self, players: List[Dict]) -> bool:
        """Insere ou atualiza players"""
        try:
            data = []
            for player in players:
                # Mapear campos do player
                # Garantir que name não seja null
                name = player.get('name') or player.get('common_name') or player.get('display_name') or f"Player_{player.get('id', 'Unknown')}"
                
                player_data = {
                    'sportmonks_id': player.get('id'),
                    'name': name,
                    'common_name': player.get('common_name'),
                    'firstname': player.get('firstname'),
                    'lastname': player.get('lastname'),
                    'nationality': player.get('nationality'),
                    'position_id': player.get('position_id'),
                    'position_name': player.get('position', {}).get('name') if player.get('position') else None,
                    'date_of_birth': player.get('date_of_birth'),
                    'height': player.get('height'),
                    'weight': player.get('weight'),
                    'image_path': player.get('image_path'),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Remover campos None para não sobrescrever dados existentes
                player_data = {k: v for k, v in player_data.items() if v is not None}
                data.append(player_data)
            
            if data:
                self.client.table('players').upsert(data, on_conflict='sportmonks_id').execute()
                logger.info(f"Upserted {len(data)} players")
                return True
            else:
                logger.warning("Nenhum player válido para upsert")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de players: {str(e)}")
            return False
    
    def upsert_events(self, events: List[Dict]) -> bool:
        """Insere ou atualiza events"""
        try:
            # Para este exemplo, vou simular o sucesso
            # Em uma implementação real, você criaria a tabela events
            logger.info(f"Simulando upsert de {len(events)} events")
            return True
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de events: {str(e)}")
            return False
    
    def upsert_statistics(self, statistics: List[Dict]) -> bool:
        """Insere ou atualiza statistics"""
        try:
            # Para este exemplo, vou simular o sucesso
            # Em uma implementação real, você criaria a tabela statistics
            logger.info(f"Simulando upsert de {len(statistics)} statistics")
            return True
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de statistics: {str(e)}")
            return False
    
    def upsert_lineups(self, lineups: List[Dict]) -> bool:
        """Insere ou atualiza lineups"""
        try:
            data = []
            for lineup in lineups:
                # Pular lineups sem player_id (obrigatório)
                if not lineup.get('player_id'):
                    continue
                
                # Mapear apenas campos que existem na tabela match_lineups
                lineup_data = {
                    'fixture_id': lineup.get('fixture_id'),
                    'team_id': lineup.get('team_id'),
                    'player_id': lineup.get('player_id'),
                    'player_name': lineup.get('player_name'),
                    'type': lineup.get('type'),
                    'position_id': lineup.get('position_id'),
                    'position_name': lineup.get('position_name'),
                    'jersey_number': lineup.get('jersey_number'),
                    'captain': lineup.get('captain', False),
                    'minutes_played': lineup.get('minutes_played'),
                    'rating': lineup.get('rating')
                }
                
                # Remover campos None para não sobrescrever dados existentes
                lineup_data = {k: v for k, v in lineup_data.items() if v is not None}
                data.append(lineup_data)
            
            if data:
                self.client.table('match_lineups').upsert(data, on_conflict='fixture_id,team_id,player_id').execute()
                logger.info(f"Upserted {len(data)} lineups")
                return True
            else:
                logger.warning("Nenhum lineup válido para upsert")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de lineups: {str(e)}")
            return False
    
    def upsert_coaches(self, coaches: List[Dict]) -> bool:
        """Insere ou atualiza coaches"""
        try:
            data = []
            for coach in coaches:
                # Mapear apenas campos que existem na tabela coaches
                coach_data = {
                    'sportmonks_id': coach.get('id'),
                    'name': coach.get('name'),
                    'common_name': coach.get('common_name'),
                    'firstname': coach.get('firstname'),
                    'lastname': coach.get('lastname'),
                    'nationality': coach.get('nationality'),
                    'image_path': coach.get('image_path'),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Remover campos None para não sobrescrever dados existentes
                coach_data = {k: v for k, v in coach_data.items() if v is not None}
                data.append(coach_data)
            
            if data:
                self.client.table('coaches').upsert(data, on_conflict='sportmonks_id').execute()
                logger.info(f"Upserted {len(data)} coaches")
                return True
            else:
                logger.warning("Nenhum coach válido para upsert")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de coaches: {str(e)}")
            return False
    
    def upsert_standings(self, standings: List[Dict]) -> bool:
        """Insere ou atualiza classificações (standings)"""
        try:
            data = []
            for standing in standings:
                # Mapear campos para a tabela standings
                standing_data = {
                    'sportmonks_id': standing.get('id'),
                    'participant_id': standing.get('participant_id'),
                    'sport_id': standing.get('sport_id'),
                    'league_id': standing.get('league_id'),
                    'season_id': standing.get('season_id'),
                    'stage_id': standing.get('stage_id'),
                    'group_id': standing.get('group_id'),
                    'round_id': standing.get('round_id'),
                    'standing_rule_id': standing.get('standing_rule_id'),
                    'position': standing.get('position'),
                    'result': standing.get('result'),
                    'points': standing.get('points'),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Remover campos None para não sobrescrever dados existentes
                standing_data = {k: v for k, v in standing_data.items() if v is not None}
                data.append(standing_data)
            
            if data:
                self.client.table('standings').upsert(data, on_conflict='sportmonks_id').execute()
                logger.info(f"Upserted {len(data)} standings")
                return True
            else:
                logger.warning("Nenhum standing válido para upsert")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de standings: {str(e)}")
            return False
    
    def upsert_transfers(self, transfers: List[Dict]) -> bool:
        """Insere ou atualiza transferências"""
        try:
            data = []
            for transfer in transfers:
                transfer_data = {
                    'sportmonks_id': transfer.get('id'),
                    'player_id': transfer.get('player_id'),
                    'from_team_id': transfer.get('from_team_id'),
                    'to_team_id': transfer.get('to_team_id'),
                    'transfer_date': transfer.get('date'),
                    'transfer_type': transfer.get('type'),
                    'fee_amount': transfer.get('fee'),
                    'fee_currency': transfer.get('currency', 'EUR'),
                    'contract_duration': transfer.get('contract_duration'),
                    'announcement_date': transfer.get('announcement_date'),
                    'details': transfer,  # Armazenar dados completos da API
                    'updated_at': datetime.now().isoformat()
                }
                
                # Remover campos None para não sobrescrever dados existentes
                transfer_data = {k: v for k, v in transfer_data.items() if v is not None}
                data.append(transfer_data)
            
            if data:
                self.client.table('transfers').upsert(data, on_conflict='sportmonks_id').execute()
                logger.info(f"Upserted {len(data)} transfers")
                return True
            else:
                logger.warning("Nenhuma transferência válida para upsert")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de transfers: {str(e)}")
            return False
    
    def upsert_rounds(self, rounds: List[Dict]) -> bool:
        """Insere ou atualiza rounds/rodadas"""
        try:
            data = []
            for round_item in rounds:
                round_data = {
                    'sportmonks_id': round_item.get('id'),
                    'sport_id': round_item.get('sport_id'),
                    'league_id': round_item.get('league_id'),
                    'season_id': round_item.get('season_id'),
                    'stage_id': round_item.get('stage_id'),
                    'name': round_item.get('name'),
                    'finished': round_item.get('finished', False),
                    'is_current': round_item.get('is_current', False),
                    'starting_at': round_item.get('starting_at'),
                    'ending_at': round_item.get('ending_at'),
                    'games_in_current_week': round_item.get('games_in_current_week', False),
                    'details': round_item,  # Armazenar dados completos da API
                    'updated_at': datetime.now().isoformat()
                }
                
                # Remover campos None para não sobrescrever dados existentes
                round_data = {k: v for k, v in round_data.items() if v is not None}
                data.append(round_data)
            
            if data:
                self.client.table('rounds').upsert(data, on_conflict='sportmonks_id').execute()
                logger.info(f"Upserted {len(data)} rounds")
                return True
            else:
                logger.warning("Nenhum round válido para upsert")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de rounds: {str(e)}")
            return False
    
    def upsert_stages(self, stages: List[Dict]) -> bool:
        """Insere ou atualiza stages/fases"""
        try:
            data = []
            for stage_item in stages:
                stage_data = {
                    'sportmonks_id': stage_item.get('id'),
                    'sport_id': stage_item.get('sport_id'),
                    'country_id': stage_item.get('country_id'),
                    'league_id': stage_item.get('league_id'),
                    'season_id': stage_item.get('season_id'),
                    'type_id': stage_item.get('type_id'),
                    'name': stage_item.get('name'),
                    'short_code': stage_item.get('short_code'),
                    'sort_order': stage_item.get('sort_order'),
                    'finished': stage_item.get('finished', False),
                    'is_current': stage_item.get('is_current', False),
                    'starting_at': stage_item.get('starting_at'),
                    'ending_at': stage_item.get('ending_at'),
                    'games_in_current_week': stage_item.get('games_in_current_week', False),
                    'tie_breaker_rule_id': stage_item.get('tie_breaker_rule_id'),
                    'details': stage_item,  # Armazenar dados completos da API
                    'updated_at': datetime.now().isoformat()
                }
                
                # Remover campos None para não sobrescrever dados existentes
                stage_data = {k: v for k, v in stage_data.items() if v is not None}
                data.append(stage_data)
            
            if data:
                self.client.table('stages').upsert(data, on_conflict='sportmonks_id').execute()
                logger.info(f"Upserted {len(data)} stages")
                return True
            else:
                logger.warning("Nenhum stage válido para upsert")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de stages: {str(e)}")
            return False
    
    def upsert_expected_stats(self, expected_stats: List[Dict]) -> bool:
        """Insere ou atualiza estatísticas Expected Goals"""
        try:
            data = []
            for stat in expected_stats:
                stat_data = {
                    'fixture_id': stat.get('fixture_id'),
                    'team_id': stat.get('team_id'),
                    'player_id': stat.get('player_id'),
                    'expected_goals': stat.get('expected_goals', 0.0),
                    'expected_assists': stat.get('expected_assists', 0.0),
                    'expected_points': stat.get('expected_points', 0.0),
                    'actual_goals': stat.get('actual_goals', 0),
                    'actual_assists': stat.get('actual_assists', 0),
                    'actual_points': stat.get('actual_points', 0),
                    'performance_index': stat.get('performance_index'),
                    'goal_efficiency': stat.get('goal_efficiency'),
                    'assist_efficiency': stat.get('assist_efficiency'),
                    'shots_total': stat.get('shots_total', 0),
                    'shots_inside_box': stat.get('shots_inside_box', 0),
                    'shots_outside_box': stat.get('shots_outside_box', 0),
                    'penalties_taken': stat.get('penalties_taken', 0),
                    'big_chances': stat.get('big_chances', 0),
                    'calculation_method': stat.get('calculation_method', 'basic_algorithm_v1'),
                    'calculation_date': stat.get('calculation_date', datetime.now().isoformat()),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Remover campos None para não sobrescrever dados existentes
                stat_data = {k: v for k, v in stat_data.items() if v is not None}
                data.append(stat_data)
            
            if data:
                # Usar upsert sem especificar conflito (deixar o Supabase decidir)
                self.client.table('expected_stats').upsert(data).execute()
                logger.info(f"Upserted {len(data)} expected stats")
                return True
            else:
                logger.warning("Nenhuma estatística Expected Goals válida para upsert")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao fazer upsert de expected stats: {str(e)}")
            return False