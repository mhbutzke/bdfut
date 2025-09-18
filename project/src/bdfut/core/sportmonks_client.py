"""
Cliente para API Sportmonks com tratamento de rate limiting
"""
import time
import requests
import hashlib
import json
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime, timedelta
import logging
from supabase import create_client

from ..config.config import Config
from .redis_cache import RedisCache, SmartCacheManager

logger = logging.getLogger(__name__)

class SportmonksClient:
    """Cliente para interação com a API Sportmonks"""
    
    def __init__(self, 
                 enable_cache: bool = True, 
                 cache_ttl_hours: int = 24,
                 use_redis: bool = True,
                 redis_url: Optional[str] = None):
        Config.validate()
        self.api_key = Config.SPORTMONKS_API_KEY
        self.base_url = Config.SPORTMONKS_BASE_URL
        self.rate_limit = Config.RATE_LIMIT_PER_HOUR
        self.max_retries = Config.MAX_RETRIES
        
        # Controle de rate limiting
        self.requests_made = 0
        self.request_timestamps = []
        self.rate_limit_remaining = self.rate_limit
        self.rate_limit_reset = None
        
        # Sistema de cache
        self.enable_cache = enable_cache
        self.cache_ttl_hours = cache_ttl_hours
        self.use_redis = use_redis
        self.cache_hits = 0
        self.cache_misses = 0
        
        if self.enable_cache:
            if self.use_redis:
                # Inicializar Redis cache
                try:
                    self.redis_cache = RedisCache(redis_url=redis_url, enable_fallback=True)
                    self.smart_cache = SmartCacheManager(self.redis_cache)
                    logger.info("✅ Sistema de cache Redis ativado")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao inicializar Redis: {e}. Usando fallback Supabase.")
                    self.use_redis = False
            
            if not self.use_redis:
                # Fallback para Supabase cache
                try:
                    self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
                    logger.info("✅ Sistema de cache Supabase ativado")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao inicializar cache: {e}. Continuando sem cache.")
                    self.enable_cache = False
    
    def _check_rate_limit(self):
        """Verifica e aguarda se necessário para respeitar o rate limit"""
        now = datetime.now()
        
        # Remove timestamps mais antigos que 1 hora
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if now - ts < timedelta(hours=1)
        ]
        
        # Se atingiu o limite, aguarda
        if len(self.request_timestamps) >= self.rate_limit:
            oldest_request = min(self.request_timestamps)
            wait_time = 3600 - (now - oldest_request).total_seconds()
            if wait_time > 0:
                logger.warning(f"Rate limit atingido. Aguardando {wait_time:.0f} segundos...")
                time.sleep(wait_time)
    
    def _update_rate_limit_from_headers(self, headers: Dict):
        """Atualiza informações de rate limit dos headers da resposta"""
        if 'X-RateLimit-Remaining' in headers:
            self.rate_limit_remaining = int(headers['X-RateLimit-Remaining'])
        
        if 'X-RateLimit-Reset' in headers:
            self.rate_limit_reset = datetime.fromtimestamp(int(headers['X-RateLimit-Reset']))
    
    def _generate_cache_key(self, endpoint: str, params: Dict) -> str:
        """Gera chave única para o cache baseada no endpoint e parâmetros"""
        # Remove api_token dos parâmetros para o hash (não é relevante para cache)
        cache_params = {k: v for k, v in params.items() if k != 'api_token'}
        cache_params['endpoint'] = endpoint
        
        # Ordena parâmetros para consistência
        sorted_params = json.dumps(cache_params, sort_keys=True)
        
        # Gera hash MD5
        return hashlib.md5(sorted_params.encode()).hexdigest()
    
    def _get_from_cache(self, endpoint: str, params: Dict, entity_type: str = 'default') -> Optional[Dict]:
        """Busca dados no cache"""
        if not self.enable_cache:
            return None
        
        try:
            if self.use_redis:
                # Usar Redis cache
                cached_data = self.smart_cache.get_cached_api_response(endpoint, params, entity_type)
                if cached_data is not None:
                    self.cache_hits += 1
                    logger.debug(f"🎯 Redis Cache HIT para {endpoint}")
                    return cached_data
                else:
                    self.cache_misses += 1
                    logger.debug(f"❌ Redis Cache MISS para {endpoint}")
                    return None
            else:
                # Fallback para Supabase cache
                cache_key = self._generate_cache_key(endpoint, params)
                
                result = self.supabase.table('api_cache').select('*').eq('cache_key', cache_key).gte('expires_at', datetime.now().isoformat()).execute()
                
                if result.data:
                    cache_entry = result.data[0]
                    
                    self.cache_hits += 1
                    logger.debug(f"🎯 Supabase Cache HIT para {endpoint}")
                    return cache_entry['data']
                
                self.cache_misses += 1
                logger.debug(f"❌ Supabase Cache MISS para {endpoint}")
                return None
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao buscar cache: {e}")
            self.cache_misses += 1
            return None
    
    def _save_to_cache(self, endpoint: str, params: Dict, response_data: Dict, entity_type: str = 'default'):
        """Salva dados no cache"""
        if not self.enable_cache:
            return
        
        try:
            if self.use_redis:
                # Usar Redis cache com TTL inteligente
                success = self.smart_cache.cache_api_response(endpoint, params, response_data, entity_type)
                if success:
                    logger.debug(f"💾 Dados salvos no Redis cache para {endpoint}")
                else:
                    logger.warning(f"⚠️ Falha ao salvar no Redis cache para {endpoint}")
            else:
                # Fallback para Supabase cache
                cache_key = self._generate_cache_key(endpoint, params)
                expires_at = datetime.now() + timedelta(hours=self.cache_ttl_hours)
                
                cache_data = {
                    'cache_key': cache_key,
                    'data': response_data,
                    'expires_at': expires_at.isoformat()
                }
                
                self.supabase.table('api_cache').upsert(cache_data, on_conflict='cache_key').execute()
                logger.debug(f"💾 Dados salvos no Supabase cache para {endpoint}")
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao salvar cache: {e}")
    
    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        if not self.enable_cache:
            return {"cache_enabled": False}
        
        try:
            base_stats = {
                "cache_enabled": True,
                "cache_type": "redis" if self.use_redis else "supabase",
                "client_cache_hits": self.cache_hits,
                "client_cache_misses": self.cache_misses,
                "client_hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
            }
            
            if self.use_redis and hasattr(self, 'smart_cache'):
                # Estatísticas do Redis
                redis_stats = self.smart_cache.get_comprehensive_stats()
                return {**base_stats, **redis_stats}
            else:
                # Estatísticas do Supabase
                result = self.supabase.table('api_cache').select('id', count='exact').execute()
                total_entries = result.count if result.count is not None else 0
                
                expired_result = self.supabase.table('api_cache').select('id', count='exact').lt('expires_at', datetime.now().isoformat()).execute()
                expired_entries = expired_result.count if expired_result.count is not None else 0
                
                return {
                    **base_stats,
                    "total_entries": total_entries,
                    "expired_entries": expired_entries
                }
        except Exception as e:
            logger.warning(f"⚠️ Erro ao obter estatísticas do cache: {e}")
            return {"cache_enabled": True, "error": str(e)}
    
    def invalidate_cache(self, entity_type: str, entity_id: Optional[int] = None) -> int:
        """
        Invalida cache de uma entidade específica
        
        Args:
            entity_type: Tipo de entidade
            entity_id: ID específico (opcional)
            
        Returns:
            Número de chaves invalidadas
        """
        if not self.enable_cache:
            return 0
        
        try:
            if self.use_redis and hasattr(self, 'smart_cache'):
                return self.smart_cache.invalidate_entity_cache(entity_type, entity_id)
            else:
                # Para Supabase, não temos invalidação por padrão
                logger.info(f"⚠️ Invalidação de cache não suportada para Supabase")
                return 0
        except Exception as e:
            logger.error(f"❌ Erro ao invalidar cache: {e}")
            return 0
    
    def warm_up_cache(self) -> Dict[str, int]:
        """
        Aquece o cache com dados frequentemente acessados
        
        Returns:
            Estatísticas do warm-up
        """
        if not self.enable_cache or not self.use_redis:
            return {"error": "Redis cache não disponível"}
        
        try:
            return self.smart_cache.warm_up_cache()
        except Exception as e:
            logger.error(f"❌ Erro ao aquecer cache: {e}")
            return {"error": str(e)}
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60)
    )
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, entity_type: str = None) -> Dict[str, Any]:
        """Faz uma requisição para a API com retry automático e cache"""
        if params is None:
            params = {}
        
        # Tentar buscar no cache primeiro
        cached_data = self._get_from_cache(endpoint, params, entity_type)
        if cached_data is not None:
            return cached_data
        
        # Se não encontrou no cache, fazer requisição à API
        self._check_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        params['api_token'] = self.api_key
        
        try:
            response = requests.get(url, params=params)
            
            # Atualiza controle de rate limit
            self.request_timestamps.append(datetime.now())
            self._update_rate_limit_from_headers(response.headers)
            
            # Verifica status 429 (Too Many Requests)
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limit excedido. Aguardando {retry_after} segundos...")
                time.sleep(retry_after)
                raise Exception("Rate limit exceeded")
            
            response.raise_for_status()
            response_data = response.json()
            
            # Salvar no cache
            self._save_to_cache(endpoint, params, response_data, entity_type)
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para {url}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.error(f"Detalhes do erro: {error_detail}")
                except:
                    logger.error(f"Resposta: {e.response.text}")
            raise
    
    def get_paginated_data(self, endpoint: str, params: Optional[Dict] = None, 
                          max_pages: Optional[int] = None, entity_type: str = None) -> List[Dict]:
        """Obtém dados paginados da API"""
        if params is None:
            params = {}
        
        all_data = []
        page = 1
        
        while True:
            params['page'] = page
            response = self._make_request(endpoint, params, entity_type)
            
            data = response.get('data', [])
            all_data.extend(data)
            
            # Verifica se há mais páginas
            pagination = response.get('pagination', {})
            if not pagination.get('has_more', False):
                break
            
            # Verifica limite de páginas
            if max_pages and page >= max_pages:
                break
            
            page += 1
            
            # Pequena pausa entre páginas
            time.sleep(0.1)  # Otimizado de 0.5s para 0.1s
        
        return all_data
    
    # Métodos para endpoints específicos
    
    def get_countries(self, include: Optional[str] = None) -> List[Dict]:
        """Obtém lista de países"""
        params = {}
        if include:
            params['include'] = include
        
        # Countries usa endpoint core ao invés de football
        original_base = self.base_url
        self.base_url = "https://api.sportmonks.com/v3/core"
        try:
            return self.get_paginated_data('/countries', params)
        finally:
            self.base_url = original_base
    
    def get_leagues(self, include: Optional[str] = None) -> List[Dict]:
        """Obtém lista de ligas"""
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data('/leagues', params)
    
    def get_league_by_id(self, league_id: int, include: Optional[str] = None) -> Dict:
        """Obtém detalhes de uma liga específica"""
        params = {}
        if include:
            params['include'] = include
        
        response = self._make_request(f'/leagues/{league_id}', params)
        return response.get('data', {})
    
    def get_seasons(self, include: Optional[str] = None) -> List[Dict]:
        """Obtém lista de temporadas"""
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data('/seasons', params)
    
    def get_season_by_id(self, season_id: int, include: Optional[str] = None) -> Dict:
        """Obtém detalhes de uma temporada específica"""
        params = {}
        if include:
            params['include'] = include
        
        response = self._make_request(f'/seasons/{season_id}', params)
        return response.get('data', {})
    
    def get_teams_by_season(self, season_id: int, include: Optional[str] = None) -> List[Dict]:
        """Obtém times de uma temporada"""
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data(f'/teams/seasons/{season_id}', params)
    
    def get_fixtures_by_date_range(self, start_date: str, end_date: str, 
                                   include: Optional[str] = None) -> List[Dict]:
        """Obtém partidas em um intervalo de datas"""
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data(f'/fixtures/between/{start_date}/{end_date}', params, entity_type='Fixture')
    
    def get_fixture_by_id(self, fixture_id: int, include: Optional[str] = None) -> Dict:
        """Obtém detalhes de uma partida específica"""
        params = {}
        if include:
            params['include'] = include
        
        response = self._make_request(f'/fixtures/{fixture_id}', params)
        return response.get('data', {})
    
    def get_venues(self, include: Optional[str] = None) -> List[Dict]:
        """Obtém lista de estádios"""
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data('/venues', params)
    
    def get_referees(self, include: Optional[str] = None) -> List[Dict]:
        """Obtém lista de árbitros"""
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data('/referees', params)
    
    def get_players_by_team(self, team_id: int, include: Optional[str] = None) -> List[Dict]:
        """Obtém jogadores de um time"""
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data(f'/squads/teams/{team_id}', params)
    
    def get_standings_by_season(self, season_id: int, include: Optional[str] = None) -> List[Dict]:
        """Obtém classificação de uma temporada"""
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data(f'/standings/seasons/{season_id}', params)
    
    def get_states(self) -> List[Dict]:
        """Obtém lista de estados (status de partidas)"""
        # States usa endpoint core ao invés de football
        original_base = self.base_url
        self.base_url = "https://api.sportmonks.com/v3/core"
        try:
            response = self._make_request('/states')
            return response.get('data', [])
        finally:
            self.base_url = original_base
    
    def get_types(self) -> List[Dict]:
        """Obtém lista de tipos (tipos de eventos, estatísticas, etc)"""
        # Types usa endpoint core ao invés de football
        original_base = self.base_url
        self.base_url = "https://api.sportmonks.com/v3/core"
        try:
            response = self._make_request('/types')
            return response.get('data', [])
        finally:
            self.base_url = original_base
    
    def get_player_by_id(self, player_id: int, include: Optional[str] = None) -> Dict:
        """Obtém detalhes de um jogador específico"""
        params = {}
        if include:
            params['include'] = include
        
        response = self._make_request(f'/players/{player_id}', params)
        return response.get('data', {})
    
    def get_coaches_by_team(self, team_id: int, include: Optional[str] = None) -> List[Dict]:
        """Obtém técnicos de um time"""
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data(f'/coaches/teams/{team_id}', params)
    
    def get_events_by_fixture(self, fixture_id: int, include: Optional[str] = None) -> List[Dict]:
        """Busca events de uma fixture específica"""
        endpoint = f'/fixtures/{fixture_id}'
        params = {'include': 'events'}
        if include:
            params['include'] = f"events,{include}"
        
        response = self._make_request(endpoint, params, 'events')
        if response and response.get('data'):
            return response['data'].get('events', [])
        return []
    
    def get_statistics_by_fixture(self, fixture_id: int, include: Optional[str] = None) -> List[Dict]:
        """Busca statistics de uma fixture específica"""
        endpoint = f'/fixtures/{fixture_id}'
        params = {'include': 'statistics'}
        if include:
            params['include'] = f"statistics,{include}"
        
        response = self._make_request(endpoint, params, 'statistics')
        if response and response.get('data'):
            return response['data'].get('statistics', [])
        return []
    
    def get_lineups_by_fixture(self, fixture_id: int, include: Optional[str] = None) -> List[Dict]:
        """Busca lineups de uma fixture específica"""
        endpoint = f'/fixtures/{fixture_id}'
        params = {'include': 'lineups'}
        if include:
            params['include'] = f"lineups,{include}"
        
        response = self._make_request(endpoint, params, 'lineups')
        if response and response.get('data'):
            return response['data'].get('lineups', [])
        return []
    
    def get_coaches_by_team(self, team_id: int, include: Optional[str] = None) -> List[Dict]:
        """Busca coaches de um team específico"""
        endpoint = f'/teams/{team_id}'
        params = {'include': 'coaches'}
        if include:
            params['include'] = f"coaches,{include}"
        
        response = self._make_request(endpoint, params, 'coaches')
        if response and response.get('data'):
            return response['data'].get('coaches', [])
        return []
    
    def get_standings(self, include: Optional[str] = None) -> List[Dict]:
        """Busca todas as classificações (standings)"""
        endpoint = '/standings'
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data(endpoint, params)
    
    def get_standings_by_season(self, season_id: int, include: Optional[str] = None) -> List[Dict]:
        """Busca classificações de uma temporada específica"""
        endpoint = '/standings'
        params = {'season_id': season_id}
        if include:
            params['include'] = include
        
        response = self._make_request(endpoint, params, 'standings')
        return response.get('data', []) if response else []
    
    def get_standings_by_league(self, league_id: int, include: Optional[str] = None) -> List[Dict]:
        """Busca classificações de uma liga específica"""
        endpoint = '/standings'
        params = {'league_id': league_id}
        if include:
            params['include'] = include
        
        response = self._make_request(endpoint, params, 'standings')
        return response.get('data', []) if response else []
    
    def get_coach_by_id(self, coach_id: int, include: Optional[str] = None) -> Dict:
        """Busca um coach específico por ID"""
        endpoint = f'/coaches/{coach_id}'
        params = {}
        if include:
            params['include'] = include
        
        response = self._make_request(endpoint, params, 'coach')
        return response.get('data', {}) if response else {}
    
    def get_transfers(self, include: Optional[str] = None, 
                     per_page: int = 500, 
                     page: int = 1) -> List[Dict]:
        """Obtém lista de transferências"""
        params = {
            'per_page': per_page,
            'page': page
        }
        if include:
            params['include'] = include
        
        return self.get_paginated_data('/transfers', params)
    
    def get_transfers_by_player(self, player_id: int, include: Optional[str] = None) -> List[Dict]:
        """Obtém transferências de um jogador específico"""
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data(f'/transfers/players/{player_id}', params)
    
    def get_transfers_by_team(self, team_id: int, include: Optional[str] = None) -> List[Dict]:
        """Obtém transferências de um time específico"""
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data(f'/transfers/teams/{team_id}', params)
    
    def get_rounds(self, include: Optional[str] = None, 
                   per_page: int = 500, 
                   page: int = 1) -> List[Dict]:
        """Obtém lista de rounds/rodadas"""
        params = {
            'per_page': per_page,
            'page': page
        }
        if include:
            params['include'] = include
        
        return self.get_paginated_data('/rounds', params)
    
    def get_rounds_by_season(self, season_id: int, include: Optional[str] = None) -> List[Dict]:
        """Obtém rounds de uma temporada específica"""
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data(f'/rounds/seasons/{season_id}', params)
    
    def get_round_by_id(self, round_id: int, include: Optional[str] = None) -> Dict:
        """Obtém um round específico por ID"""
        params = {}
        if include:
            params['include'] = include
        
        response = self._make_request(f'/rounds/{round_id}', params, 'round')
        return response.get('data', {}) if response else {}
    
    def get_stages(self, include: Optional[str] = None, 
                   per_page: int = 500, 
                   page: int = 1) -> List[Dict]:
        """Obtém lista de stages/fases"""
        params = {
            'per_page': per_page,
            'page': page
        }
        if include:
            params['include'] = include
        
        return self.get_paginated_data('/stages', params)
    
    def get_stages_by_season(self, season_id: int, include: Optional[str] = None) -> List[Dict]:
        """Obtém stages de uma temporada específica"""
        params = {}
        if include:
            params['include'] = include
        
        return self.get_paginated_data(f'/stages/seasons/{season_id}', params)
    
    def get_stage_by_id(self, stage_id: int, include: Optional[str] = None) -> Dict:
        """Obtém um stage específico por ID"""
        params = {}
        if include:
            params['include'] = include
        
        response = self._make_request(f'/stages/{stage_id}', params, 'stage')
        return response.get('data', {}) if response else {}
    
    def get_fixtures_multi(self, fixture_ids: str, include: Optional[str] = None) -> Dict:
        """Obtém múltiplas fixtures usando endpoint multi"""
        endpoint = f'/fixtures/multi/{fixture_ids}'
        params = {}
        if include:
            params['include'] = include
        
        response = self._make_request(endpoint, params, 'fixtures')
        return response if response else {}
    
    def get_fixture_with_includes(self, fixture_id: int, include: Optional[str] = None) -> Dict:
        """Obtém uma fixture específica com includes"""
        endpoint = f'/fixtures/{fixture_id}'
        params = {}
        if include:
            params['include'] = include
        
        response = self._make_request(endpoint, params, 'fixture')
        return response if response else {}