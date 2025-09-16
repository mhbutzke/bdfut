"""
BDFut - Sistema ETL para dados de futebol
=========================================

Sistema completo de ETL (Extract, Transform, Load) para sincronizar 
dados de futebol da API Sportmonks com banco de dados Supabase.

Versão: 2.0.0
Autor: BDFut Team
"""

__version__ = "2.0.0"
__author__ = "BDFut Team"
__email__ = "team@bdfut.com"
__description__ = "Sistema ETL para dados de futebol da Sportmonks API"

# Imports principais
from .core.sportmonks_client import SportmonksClient
from .core.supabase_client import SupabaseClient
from .core.etl_process import ETLProcess

__all__ = [
    "SportmonksClient",
    "SupabaseClient", 
    "ETLProcess",
    "__version__",
    "__author__",
    "__email__",
    "__description__"
]
