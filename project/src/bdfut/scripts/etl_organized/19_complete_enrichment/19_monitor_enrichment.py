#!/usr/bin/env python3
"""
Script para monitorar o progresso do enriquecimento
"""

import os
import sys
from pathlib import Path
import time
import logging

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnrichmentMonitor:
    def __init__(self):
        self.supabase = SupabaseClient()
        self.last_events = 0
        self.last_lineups = 0
        self.last_stats = 0
        self.start_time = time.time()
        
    def get_current_counts(self):
        """Obter contagens atuais das tabelas"""
        try:
            # Contar eventos
            events_response = self.supabase.client.from_('match_events').select('id', count='exact').execute()
            events_count = events_response.count
            
            # Contar lineups
            lineups_response = self.supabase.client.from_('match_lineups').select('id', count='exact').execute()
            lineups_count = lineups_response.count
            
            # Contar estatísticas
            stats_response = self.supabase.client.from_('match_statistics').select('id', count='exact').execute()
            stats_count = stats_response.count
            
            return {
                'events': events_count,
                'lineups': lineups_count,
                'statistics': stats_count
            }
        except Exception as e:
            logger.error(f"Erro ao obter contagens: {e}")
            return {'events': 0, 'lineups': 0, 'statistics': 0}
    
    def monitor_progress(self, interval: int = 60):
        """Monitorar progresso do enriquecimento"""
        logger.info("🔍 INICIANDO MONITORAMENTO DO ENRIQUECIMENTO")
        logger.info("=" * 60)
        
        # Obter contagens iniciais
        initial_counts = self.get_current_counts()
        self.last_events = initial_counts['events']
        self.last_lineups = initial_counts['lineups']
        self.last_stats = initial_counts['statistics']
        
        logger.info(f"📊 Contagens iniciais:")
        logger.info(f"   Eventos: {self.last_events:,}")
        logger.info(f"   Lineups: {self.last_lineups:,}")
        logger.info(f"   Estatísticas: {self.last_stats:,}")
        
        iteration = 0
        while True:
            try:
                iteration += 1
                current_counts = self.get_current_counts()
                
                # Calcular diferenças
                events_diff = current_counts['events'] - self.last_events
                lineups_diff = current_counts['lineups'] - self.last_lineups
                stats_diff = current_counts['statistics'] - self.last_stats
                
                # Calcular tempo decorrido
                elapsed = time.time() - self.start_time
                
                logger.info(f"\\n📊 RELATÓRIO #{iteration} - {time.strftime('%H:%M:%S')}")
                logger.info("=" * 50)
                logger.info(f"⏱️ Tempo decorrido: {elapsed/60:.1f} minutos")
                logger.info(f"📈 Eventos: {current_counts['events']:,} (+{events_diff:,})")
                logger.info(f"👥 Lineups: {current_counts['lineups']:,} (+{lineups_diff:,})")
                logger.info(f"📊 Estatísticas: {current_counts['statistics']:,} (+{stats_diff:,})")
                
                # Calcular taxas
                if elapsed > 0:
                    events_rate = events_diff / (interval / 60)
                    lineups_rate = lineups_diff / (interval / 60)
                    stats_rate = stats_diff / (interval / 60)
                    
                    logger.info(f"🚀 Taxas (por minuto):")
                    logger.info(f"   Eventos: {events_rate:.1f}")
                    logger.info(f"   Lineups: {lineups_rate:.1f}")
                    logger.info(f"   Estatísticas: {stats_rate:.1f}")
                
                # Atualizar contadores
                self.last_events = current_counts['events']
                self.last_lineups = current_counts['lineups']
                self.last_stats = current_counts['statistics']
                
                # Aguardar próximo intervalo
                logger.info(f"⏳ Próximo relatório em {interval} segundos...")
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("\\n🛑 Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                time.sleep(interval)

def main():
    """Função principal"""
    monitor = EnrichmentMonitor()
    
    # Monitorar a cada 60 segundos
    monitor.monitor_progress(interval=60)

if __name__ == "__main__":
    main()
