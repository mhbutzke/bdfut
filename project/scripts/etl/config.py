"""
Configuração para Scripts ETL
============================

Configurações centralizadas para scripts de ETL do BDFut.

Autor: ETL Engineer
Data: 17 de Janeiro de 2025
"""

import os
from typing import Dict, Any

class ETLConfig:
    """Configurações ETL"""
    
    # API Sportmonks
    SPORTMONKS_API_KEY = os.getenv('SPORTMONKS_API_KEY')
    SPORTMONKS_BASE_URL = "https://api.sportmonks.com/v3/football"
    
    # Supabase
    SUPABASE_CONNECTION_STRING = os.getenv('SUPABASE_CONNECTION_STRING')
    
    # Rate Limiting
    MIN_REQUEST_INTERVAL = 0.1  # 100ms entre requests (10 req/s)
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # segundos
    
    # Batch Processing
    DEFAULT_BATCH_SIZE = 100
    MAX_FIXTURES_PER_RUN = 1000
    
    # Logging
    LOG_LEVEL = os.getenv('ETL_LOG_LEVEL', 'INFO')
    LOG_FILE = 'etl_incremental.log'
    
    # Data Quality
    MIN_DATA_QUALITY_SCORE = 80
    DEFAULT_DATA_QUALITY_SCORE = 100
    
    @classmethod
    def validate(cls) -> bool:
        """Valida se todas as configurações necessárias estão presentes"""
        required_vars = [
            'SPORTMONKS_API_KEY',
            'SUPABASE_CONNECTION_STRING'
        ]
        
        missing = []
        for var in required_vars:
            if not getattr(cls, var):
                missing.append(var)
        
        if missing:
            print(f"❌ Variáveis de ambiente faltando: {', '.join(missing)}")
            return False
        
        print("✅ Todas as configurações estão presentes")
        return True
    
    @classmethod
    def get_connection_params(cls) -> Dict[str, Any]:
        """Retorna parâmetros de conexão para Supabase"""
        return {
            'connection_string': cls.SUPABASE_CONNECTION_STRING,
            'api_key': cls.SPORTMONKS_API_KEY,
            'base_url': cls.SPORTMONKS_BASE_URL
        }
