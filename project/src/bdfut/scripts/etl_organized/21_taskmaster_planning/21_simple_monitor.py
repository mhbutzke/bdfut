#!/usr/bin/env python3
"""
Monitor simples para acompanhar progresso do enriquecimento
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
import logging

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_counts():
    """Obter contagens atuais"""
    try:
        supabase = SupabaseClient()
        counts = {}
        
        tables = ['match_events', 'match_lineups', 'match_statistics']
        for table in tables:
            response = supabase.client.table(table).select('id', count='exact').execute()
            counts[table] = response.count
        
        return counts
    except Exception as e:
        logger.error(f"Erro ao obter contagens: {e}")
        return {}

def main():
    """Monitor principal"""
    logger.info("🔍 INICIANDO MONITORAMENTO SIMPLES")
    logger.info("=" * 50)
    
    # Contagens iniciais
    initial_counts = get_counts()
    logger.info("📊 Contagens iniciais:")
    for table, count in initial_counts.items():
        logger.info(f"   {table}: {count:,}")
    
    iteration = 0
    while True:
        try:
            iteration += 1
            current_counts = get_counts()
            
            logger.info(f"\n📊 RELATÓRIO #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
            logger.info("=" * 40)
            
            for table in ['match_events', 'match_lineups', 'match_statistics']:
                current = current_counts.get(table, 0)
                initial = initial_counts.get(table, 0)
                increase = current - initial
                
                logger.info(f"📈 {table}: {current:,} (+{increase:,})")
            
            logger.info("⏳ Próximo relatório em 30 segundos...")
            time.sleep(30)
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Monitoramento interrompido pelo usuário")
            break
        except Exception as e:
            logger.error(f"❌ Erro no monitoramento: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
