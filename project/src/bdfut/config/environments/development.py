"""
Configurações para ambiente de desenvolvimento
=============================================
"""
import os
from typing import List

class DevelopmentConfig:
    """Configurações específicas para desenvolvimento"""
    
    # URLs e chaves
    SPORTMONKS_BASE_URL = "https://api.sportmonks.com/v3/football"
    SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY_DEV", "")
    
    SUPABASE_URL = os.getenv("SUPABASE_URL_DEV", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY_DEV", "")
    
    # Configurações de rate limiting
    RATE_LIMIT_PER_HOUR = 1000  # Limite menor para desenvolvimento
    BATCH_SIZE = 50  # Batch menor para testes
    MAX_RETRIES = 2
    RETRY_DELAY = 3
    
    # Configurações de logging
    LOG_LEVEL = "DEBUG"
    LOG_FILE = "bdfut/logs/development.log"
    
    # Ligas para desenvolvimento (apenas algumas para teste)
    MAIN_LEAGUES: List[int] = [
        648,  # Brasil - Serie A
        651,  # Brasil - Serie B
    ]
    
    # Configurações de debug
    DEBUG = True
    VERBOSE_LOGGING = True
    SAVE_RAW_DATA = True  # Salvar dados brutos para análise
    
    # Configurações de banco
    DATABASE_SCHEMA = "sportmonks_dev"
    AUTO_CREATE_TABLES = True
    
    # Configurações de cache
    CACHE_ENABLED = False
    CACHE_TTL = 300  # 5 minutos
