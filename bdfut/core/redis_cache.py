"""
Cliente Redis para cache distribuído avançado
============================================

Sistema de cache robusto com TTL inteligente e fallback local
"""
import json
import logging
import hashlib
import pickle
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timedelta
import redis
from redis.exceptions import ConnectionError, TimeoutError

from ..config.config import Config

logger = logging.getLogger(__name__)


class RedisCache:
    """Cliente Redis com fallback para cache local"""
    
    # TTL inteligente baseado no tipo de dados (em segundos)
    TTL_MAPPING = {
        'countries': 7 * 24 * 3600,      # 7 dias (dados estáticos)
        'states': 7 * 24 * 3600,         # 7 dias (dados estáticos)
        'types': 7 * 24 * 3600,          # 7 dias (dados estáticos)
        'leagues': 3 * 24 * 3600,        # 3 dias (mudanças raras)
        'seasons': 1 * 24 * 3600,        # 1 dia (mudanças ocasionais)
        'teams': 6 * 3600,               # 6 horas (mudanças frequentes)
        'venues': 12 * 3600,             # 12 horas (mudanças raras)
        'referees': 12 * 3600,           # 12 horas (mudanças raras)
        'fixtures': 2 * 3600,            # 2 horas (mudanças muito frequentes)
        'events': 1 * 3600,              # 1 hora (dados dinâmicos)
        'statistics': 30 * 60,           # 30 minutos (dados em tempo real)
        'lineups': 1 * 3600,             # 1 hora (mudanças pré-jogo)
        'default': 4 * 3600              # 4 horas (padrão)
    }
    
    def __init__(self, 
                 redis_url: Optional[str] = None,
                 enable_fallback: bool = True,
                 max_local_cache_size: int = 1000):
        """
        Inicializa cliente Redis com fallback
        
        Args:
            redis_url: URL de conexão Redis
            enable_fallback: Habilitar cache local como fallback
            max_local_cache_size: Tamanho máximo do cache local
        """
        self.redis_url = redis_url or getattr(Config, 'REDIS_URL', 'redis://localhost:6379')
        self.enable_fallback = enable_fallback
        self.max_local_cache_size = max_local_cache_size
        
        # Estatísticas
        self.redis_hits = 0
        self.redis_misses = 0
        self.local_hits = 0
        self.local_misses = 0
        self.redis_errors = 0
        
        # Cache local (fallback)
        self.local_cache = {} if enable_fallback else None
        self.local_cache_timestamps = {} if enable_fallback else None
        
        # Inicializar Redis
        self._init_redis()
    
    def _init_redis(self):
        """Inicializa conexão Redis"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Testar conexão
            self.redis_client.ping()
            logger.info(f"✅ Redis conectado: {self.redis_url}")
            self.redis_available = True
            
        except Exception as e:
            logger.warning(f"⚠️ Redis não disponível: {e}")
            self.redis_client = None
            self.redis_available = False
            
            if self.enable_fallback:
                logger.info("💾 Fallback para cache local ativado")
            else:
                logger.warning("❌ Cache desabilitado (Redis indisponível e fallback desabilitado)")
    
    def _get_ttl(self, entity_type: str) -> int:
        """Obtém TTL inteligente baseado no tipo de entidade"""
        return self.TTL_MAPPING.get(entity_type.lower(), self.TTL_MAPPING['default'])
    
    def _generate_key(self, prefix: str, data: Dict) -> str:
        """Gera chave única para cache"""
        # Remover api_token e outros dados sensíveis
        cache_data = {k: v for k, v in data.items() if k not in ['api_token', 'api_key']}
        cache_data['prefix'] = prefix
        
        # Ordenar para consistência
        sorted_data = json.dumps(cache_data, sort_keys=True)
        
        # Gerar hash
        return f"bdfut:{hashlib.md5(sorted_data.encode()).hexdigest()}"
    
    def get(self, key: str, entity_type: str = 'default') -> Optional[Any]:
        """
        Busca dados no cache
        
        Args:
            key: Chave do cache
            entity_type: Tipo de entidade para TTL inteligente
            
        Returns:
            Dados do cache ou None se não encontrado
        """
        # Tentar Redis primeiro
        if self.redis_available:
            try:
                data = self.redis_client.get(key)
                if data is not None:
                    self.redis_hits += 1
                    logger.debug(f"🎯 Redis HIT: {key}")
                    return json.loads(data)
                else:
                    self.redis_misses += 1
                    logger.debug(f"❌ Redis MISS: {key}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro no Redis: {e}")
                self.redis_errors += 1
                self._handle_redis_error()
        
        # Fallback para cache local
        if self.enable_fallback and self.local_cache is not None:
            if key in self.local_cache:
                # Verificar se não expirou
                timestamp = self.local_cache_timestamps.get(key)
                ttl = self._get_ttl(entity_type)
                
                if timestamp and (datetime.now() - timestamp).total_seconds() < ttl:
                    self.local_hits += 1
                    logger.debug(f"🎯 Local HIT: {key}")
                    return self.local_cache[key]
                else:
                    # Expirado - remover
                    del self.local_cache[key]
                    del self.local_cache_timestamps[key]
            
            self.local_misses += 1
            logger.debug(f"❌ Local MISS: {key}")
        
        return None
    
    def set(self, key: str, value: Any, entity_type: str = 'default') -> bool:
        """
        Salva dados no cache
        
        Args:
            key: Chave do cache
            value: Dados a serem salvos
            entity_type: Tipo de entidade para TTL inteligente
            
        Returns:
            True se sucesso, False se erro
        """
        ttl = self._get_ttl(entity_type)
        success = False
        
        # Tentar Redis primeiro
        if self.redis_available:
            try:
                serialized_data = json.dumps(value)
                self.redis_client.setex(key, ttl, serialized_data)
                logger.debug(f"💾 Redis SET: {key} (TTL: {ttl}s)")
                success = True
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao salvar no Redis: {e}")
                self.redis_errors += 1
                self._handle_redis_error()
        
        # Fallback para cache local
        if self.enable_fallback and self.local_cache is not None:
            try:
                # Limpar cache local se muito grande
                if len(self.local_cache) >= self.max_local_cache_size:
                    self._cleanup_local_cache()
                
                self.local_cache[key] = value
                self.local_cache_timestamps[key] = datetime.now()
                logger.debug(f"💾 Local SET: {key}")
                success = True
                
            except Exception as e:
                logger.error(f"❌ Erro ao salvar no cache local: {e}")
        
        return success
    
    def delete(self, key: str) -> bool:
        """
        Remove dados do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            True se removido, False se não encontrado/erro
        """
        success = False
        
        # Remover do Redis
        if self.redis_available:
            try:
                result = self.redis_client.delete(key)
                if result > 0:
                    success = True
                    logger.debug(f"🗑️ Redis DELETE: {key}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro ao deletar do Redis: {e}")
                self.redis_errors += 1
        
        # Remover do cache local
        if self.enable_fallback and self.local_cache is not None:
            if key in self.local_cache:
                del self.local_cache[key]
                del self.local_cache_timestamps[key]
                success = True
                logger.debug(f"🗑️ Local DELETE: {key}")
        
        return success
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalida chaves que correspondem ao padrão
        
        Args:
            pattern: Padrão de chaves (ex: 'bdfut:fixtures:*')
            
        Returns:
            Número de chaves invalidadas
        """
        invalidated = 0
        
        # Invalidar no Redis
        if self.redis_available:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    invalidated += self.redis_client.delete(*keys)
                    logger.debug(f"🗑️ Redis INVALIDATE: {len(keys)} chaves com padrão {pattern}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro ao invalidar no Redis: {e}")
                self.redis_errors += 1
        
        # Invalidar no cache local
        if self.enable_fallback and self.local_cache is not None:
            # Simular pattern matching para cache local
            import fnmatch
            keys_to_remove = [k for k in self.local_cache.keys() if fnmatch.fnmatch(k, pattern)]
            
            for key in keys_to_remove:
                del self.local_cache[key]
                del self.local_cache_timestamps[key]
                invalidated += 1
            
            if keys_to_remove:
                logger.debug(f"🗑️ Local INVALIDATE: {len(keys_to_remove)} chaves com padrão {pattern}")
        
        return invalidated
    
    def _handle_redis_error(self):
        """Trata erros do Redis"""
        if self.redis_errors > 10:  # Muitos erros
            logger.warning("⚠️ Muitos erros do Redis - tentando reconectar...")
            self._init_redis()
    
    def _cleanup_local_cache(self):
        """Limpa cache local removendo entradas mais antigas"""
        if not self.local_cache or not self.local_cache_timestamps:
            return
        
        # Ordenar por timestamp e remover 25% mais antigos
        sorted_keys = sorted(
            self.local_cache_timestamps.keys(),
            key=lambda k: self.local_cache_timestamps[k]
        )
        
        keys_to_remove = sorted_keys[:len(sorted_keys) // 4]
        
        for key in keys_to_remove:
            del self.local_cache[key]
            del self.local_cache_timestamps[key]
        
        logger.debug(f"🧹 Cache local limpo: {len(keys_to_remove)} entradas removidas")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do cache
        
        Returns:
            Dicionário com estatísticas
        """
        total_redis = self.redis_hits + self.redis_misses
        total_local = self.local_hits + self.local_misses
        total_requests = total_redis + total_local
        
        stats = {
            "redis_available": self.redis_available,
            "fallback_enabled": self.enable_fallback,
            "redis_hits": self.redis_hits,
            "redis_misses": self.redis_misses,
            "redis_hit_rate": self.redis_hits / total_redis if total_redis > 0 else 0,
            "local_hits": self.local_hits,
            "local_misses": self.local_misses,
            "local_hit_rate": self.local_hits / total_local if total_local > 0 else 0,
            "total_hit_rate": (self.redis_hits + self.local_hits) / total_requests if total_requests > 0 else 0,
            "redis_errors": self.redis_errors,
            "local_cache_size": len(self.local_cache) if self.local_cache else 0
        }
        
        # Estatísticas do Redis se disponível
        if self.redis_available:
            try:
                redis_info = self.redis_client.info('memory')
                stats.update({
                    "redis_memory_used_mb": round(redis_info.get('used_memory', 0) / 1024 / 1024, 2),
                    "redis_memory_peak_mb": round(redis_info.get('used_memory_peak', 0) / 1024 / 1024, 2),
                    "redis_keys_count": self.redis_client.dbsize()
                })
            except Exception as e:
                logger.debug(f"Erro ao obter info do Redis: {e}")
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica saúde do sistema de cache
        
        Returns:
            Status de saúde
        """
        health = {
            "redis_healthy": False,
            "local_cache_healthy": False,
            "overall_healthy": False
        }
        
        # Verificar Redis
        if self.redis_available:
            try:
                self.redis_client.ping()
                health["redis_healthy"] = True
            except Exception as e:
                logger.warning(f"⚠️ Redis não saudável: {e}")
                health["redis_healthy"] = False
        
        # Verificar cache local
        if self.enable_fallback and self.local_cache is not None:
            health["local_cache_healthy"] = True
        
        # Status geral
        health["overall_healthy"] = health["redis_healthy"] or health["local_cache_healthy"]
        
        return health
    
    def flush_all(self) -> bool:
        """
        Limpa todo o cache
        
        Returns:
            True se sucesso
        """
        success = False
        
        # Limpar Redis
        if self.redis_available:
            try:
                self.redis_client.flushdb()
                logger.info("🧹 Redis cache limpo")
                success = True
            except Exception as e:
                logger.error(f"❌ Erro ao limpar Redis: {e}")
        
        # Limpar cache local
        if self.enable_fallback and self.local_cache is not None:
            self.local_cache.clear()
            self.local_cache_timestamps.clear()
            logger.info("🧹 Cache local limpo")
            success = True
        
        return success


class SmartCacheManager:
    """Gerenciador inteligente de cache com múltiplas estratégias"""
    
    def __init__(self, redis_cache: RedisCache):
        self.redis_cache = redis_cache
        
        # Estratégias de cache por entidade
        self.cache_strategies = {
            'countries': {'preload': True, 'batch_invalidate': False},
            'states': {'preload': True, 'batch_invalidate': False},
            'types': {'preload': True, 'batch_invalidate': False},
            'leagues': {'preload': False, 'batch_invalidate': True},
            'seasons': {'preload': False, 'batch_invalidate': True},
            'teams': {'preload': False, 'batch_invalidate': True},
            'venues': {'preload': False, 'batch_invalidate': True},
            'referees': {'preload': False, 'batch_invalidate': False},
            'fixtures': {'preload': False, 'batch_invalidate': True},
            'events': {'preload': False, 'batch_invalidate': False}
        }
    
    def cache_api_response(self, 
                          endpoint: str, 
                          params: Dict, 
                          response_data: Any,
                          entity_type: str = 'default') -> bool:
        """
        Cacheia resposta da API com estratégia inteligente
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            response_data: Dados da resposta
            entity_type: Tipo de entidade
            
        Returns:
            True se cacheado com sucesso
        """
        cache_key = self.redis_cache._generate_key(endpoint, params)
        
        # Aplicar estratégia específica
        strategy = self.cache_strategies.get(entity_type, {})
        
        # Cache padrão
        success = self.redis_cache.set(cache_key, response_data, entity_type)
        
        # Cache adicional para entidades que fazem preload
        if strategy.get('preload', False) and isinstance(response_data, dict):
            if 'data' in response_data and isinstance(response_data['data'], list):
                # Cachear itens individuais para acesso rápido
                for item in response_data['data']:
                    if 'id' in item:
                        item_key = f"bdfut:{entity_type}:id:{item['id']}"
                        self.redis_cache.set(item_key, item, entity_type)
        
        return success
    
    def get_cached_api_response(self, 
                               endpoint: str, 
                               params: Dict,
                               entity_type: str = 'default') -> Optional[Any]:
        """
        Busca resposta da API no cache
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            entity_type: Tipo de entidade
            
        Returns:
            Dados cacheados ou None
        """
        cache_key = self.redis_cache._generate_key(endpoint, params)
        return self.redis_cache.get(cache_key, entity_type)
    
    def invalidate_entity_cache(self, entity_type: str, entity_id: Optional[int] = None) -> int:
        """
        Invalida cache de uma entidade específica
        
        Args:
            entity_type: Tipo de entidade
            entity_id: ID específico (opcional)
            
        Returns:
            Número de chaves invalidadas
        """
        if entity_id:
            # Invalidar entidade específica
            pattern = f"bdfut:*{entity_type}*{entity_id}*"
        else:
            # Invalidar todas as entidades do tipo
            pattern = f"bdfut:*{entity_type}*"
        
        return self.redis_cache.invalidate_pattern(pattern)
    
    def warm_up_cache(self, entities_to_preload: List[str] = None) -> Dict[str, int]:
        """
        Aquece o cache com dados frequentemente acessados
        
        Args:
            entities_to_preload: Lista de entidades para preload
            
        Returns:
            Estatísticas do warm-up
        """
        if entities_to_preload is None:
            entities_to_preload = [k for k, v in self.cache_strategies.items() if v.get('preload', False)]
        
        stats = {}
        
        for entity_type in entities_to_preload:
            try:
                logger.info(f"🔥 Aquecendo cache para {entity_type}...")
                
                # Implementar lógica específica de preload aqui
                # Por exemplo, buscar dados mais acessados
                
                stats[entity_type] = 0  # Placeholder
                
            except Exception as e:
                logger.error(f"❌ Erro ao aquecer cache para {entity_type}: {e}")
                stats[entity_type] = -1
        
        return stats
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas abrangentes do sistema de cache
        
        Returns:
            Estatísticas completas
        """
        redis_stats = self.redis_cache.get_stats()
        health = self.redis_cache.health_check()
        
        return {
            **redis_stats,
            **health,
            "ttl_mapping": self.redis_cache.TTL_MAPPING,
            "cache_strategies": self.cache_strategies
        }
