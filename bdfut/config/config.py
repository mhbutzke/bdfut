"""
Configuração do projeto Sportmonks ETL
"""
import os
from typing import List
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configurações do projeto"""
    
    # Sportmonks API
    SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY", "")
    SPORTMONKS_BASE_URL = os.getenv("SPORTMONKS_BASE_URL", "https://api.sportmonks.com/v3/football")
    
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Rate Limiting
    RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "3000"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))
    
    # Ligas principais para sincronização
    MAIN_LEAGUES = [
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
        779   # MLS
    ]
    
    @classmethod
    def get_main_leagues_str(cls) -> str:
        """Retorna as ligas principais como string separada por vírgula"""
        return ",".join(map(str, cls.MAIN_LEAGUES))
    
    @classmethod
    def validate(cls):
        """Valida as configurações necessárias"""
        errors = []
        
        if not cls.SPORTMONKS_API_KEY:
            errors.append("SPORTMONKS_API_KEY não configurada")
        
        if not cls.SUPABASE_URL:
            errors.append("SUPABASE_URL não configurada")
            
        if not cls.SUPABASE_KEY:
            errors.append("SUPABASE_KEY não configurada")
        
        if errors:
            raise ValueError(f"Erros de configuração: {', '.join(errors)}")
        
        return True
