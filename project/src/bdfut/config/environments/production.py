"""
Configurações para ambiente de produção
======================================
"""
import os
from typing import List

class ProductionConfig:
    """Configurações específicas para produção"""
    
    # URLs e chaves
    SPORTMONKS_BASE_URL = "https://api.sportmonks.com/v3/football"
    SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY", "")
    
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    
    # Configurações de rate limiting
    RATE_LIMIT_PER_HOUR = 3000  # Limite máximo da API
    BATCH_SIZE = 100  # Batch otimizado para produção
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    # Configurações de logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "bdfut/logs/production.log"
    
    # Ligas principais para produção
    MAIN_LEAGUES: List[int] = [
        648,  # Brasil - Serie A
        651,  # Brasil - Serie B
        654,  # Brasil - Copa do Brasil
        636,  # Argentina - Liga Profesional
        1122, # Copa Libertadores
        1116, # Copa Sudamericana
        2,    # Champions League
        5,    # Europa League
        8,    # Premier League
        9,    # Championship
        564,  # La Liga
        462,  # Liga Portugal
        301,  # Ligue 1
        82,   # Bundesliga
        743,  # Liga MX
        779,  # MLS
    ]
    
    # Configurações de produção
    DEBUG = False
    VERBOSE_LOGGING = False
    SAVE_RAW_DATA = False  # Não salvar dados brutos em produção
    
    # Configurações de banco
    DATABASE_SCHEMA = "sportmonks"
    AUTO_CREATE_TABLES = False
    
    # Configurações de cache
    CACHE_ENABLED = True
    CACHE_TTL = 3600  # 1 hora
    
    # Configurações de monitoramento
    HEALTH_CHECK_ENABLED = True
    METRICS_ENABLED = True
    
    # Configurações de segurança
    VALIDATE_API_RESPONSES = True
    SANITIZE_INPUTS = True
