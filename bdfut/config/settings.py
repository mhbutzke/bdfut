"""
Configurações principais do BDFut
=================================

Sistema de configuração centralizado com suporte a múltiplos ambientes.
"""
import os
from typing import List, Optional
from enum import Enum
from .environments.development import DevelopmentConfig
from .environments.production import ProductionConfig

class Environment(Enum):
    """Ambientes disponíveis"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"

class Config:
    """Configuração principal do BDFut"""
    
    def __init__(self, environment: Environment = Environment.PRODUCTION):
        self.environment = environment
        self._load_config()
    
    def _load_config(self):
        """Carrega configurações baseadas no ambiente"""
        if self.environment == Environment.DEVELOPMENT:
            config = DevelopmentConfig()
        else:
            config = ProductionConfig()
        
        # Carregar configurações
        self.SPORTMONKS_BASE_URL = config.SPORTMONKS_BASE_URL
        self.SPORTMONKS_API_KEY = config.SPORTMONKS_API_KEY
        self.SUPABASE_URL = config.SUPABASE_URL
        self.SUPABASE_KEY = config.SUPABASE_KEY
        
        # Rate limiting
        self.RATE_LIMIT_PER_HOUR = config.RATE_LIMIT_PER_HOUR
        self.BATCH_SIZE = config.BATCH_SIZE
        self.MAX_RETRIES = config.MAX_RETRIES
        self.RETRY_DELAY = config.RETRY_DELAY
        
        # Logging
        self.LOG_LEVEL = config.LOG_LEVEL
        self.LOG_FILE = config.LOG_FILE
        
        # Ligas
        self.MAIN_LEAGUES = config.MAIN_LEAGUES
        
        # Configurações específicas
        self.DEBUG = config.DEBUG
        self.VERBOSE_LOGGING = config.VERBOSE_LOGGING
        self.SAVE_RAW_DATA = config.SAVE_RAW_DATA
        
        # Banco de dados
        self.DATABASE_SCHEMA = config.DATABASE_SCHEMA
        self.AUTO_CREATE_TABLES = config.AUTO_CREATE_TABLES
        
        # Cache
        self.CACHE_ENABLED = config.CACHE_ENABLED
        self.CACHE_TTL = config.CACHE_TTL
    
    @classmethod
    def validate(cls) -> None:
        """Valida se todas as configurações necessárias estão presentes"""
        required_vars = [
            "SPORTMONKS_API_KEY",
            "SUPABASE_URL", 
            "SUPABASE_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(
                f"Variáveis de ambiente obrigatórias não encontradas: {', '.join(missing_vars)}"
            )
    
    def get_database_url(self) -> str:
        """Retorna a URL completa do banco de dados"""
        return f"{self.SUPABASE_URL}/rest/v1/"
    
    def get_api_headers(self) -> dict:
        """Retorna headers padrão para requisições à API"""
        return {
            "Authorization": f"Bearer {self.SPORTMONKS_API_KEY}",
            "Accept": "application/json",
            "User-Agent": "BDFut/2.0.0"
        }
    
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento"""
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção"""
        return self.environment == Environment.PRODUCTION

# Instância global da configuração
# Pode ser sobrescrita para testes
_config: Optional[Config] = None

def get_config() -> Config:
    """Retorna a instância global da configuração"""
    global _config
    if _config is None:
        env = Environment(os.getenv("BDFUT_ENV", "production"))
        _config = Config(env)
    return _config

def set_config(config: Config) -> None:
    """Define a configuração global (útil para testes)"""
    global _config
    _config = config
