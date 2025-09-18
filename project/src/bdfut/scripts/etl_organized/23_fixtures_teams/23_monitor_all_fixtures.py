#!/usr/bin/env python3
"""
Script para monitorar o progresso do enriquecimento completo de TODAS as fixtures
"""

import sys
import os
import time
import logging
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from bdfut.core.supabase_client import SupabaseClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AllFixturesMonitor:
    """Monitor do enriquecimento completo de todas as fixtures"""
    
    def __init__(self):
        self.supabase = SupabaseClient()
        self.start_time = datetime.now()
        
    def get_enrichment_stats(self):
        """Obter estatísticas do enriquecimento"""
        try:
            # Total de fixtures
            total_response = self.supabase.client.from_('fixtures').select('fixture_id', count='exact').execute()
            total_fixtures = total_response.count if total_response.count else 0
            
            # Fixtures com team IDs completos
            enriched_response = self.supabase.client.from_('fixtures').select(
                'fixture_id', count='exact'
            ).not_.or_('home_team_id.is.null,away_team_id.is.null').execute()
            enriched_fixtures = enriched_response.count if enriched_response.count else 0
            
            # Fixtures sem team IDs
            remaining_fixtures = total_fixtures - enriched_fixtures
            
            return {
                'total_fixtures': total_fixtures,
                'enriched_fixtures': enriched_fixtures,
                'remaining_fixtures': remaining_fixtures,
                'completion_percentage': (enriched_fixtures / total_fixtures * 100) if total_fixtures > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return None
    
    def monitor_progress(self):
        """Monitorar progresso continuamente"""
        logger.info("🔍 Iniciando monitoramento do enriquecimento COMPLETO de fixtures...")
        logger.info("=" * 80)
        
        last_enriched = 0
        
        while True:
            try:
                stats = self.get_enrichment_stats()
                
                if stats:
                    current_time = datetime.now()
                    elapsed_time = current_time - self.start_time
                    elapsed_minutes = elapsed_time.total_seconds() / 60
                    
                    # Calcular taxa de processamento
                    if elapsed_minutes > 0:
                        rate = stats['enriched_fixtures'] / elapsed_minutes
                        eta_minutes = stats['remaining_fixtures'] / rate if rate > 0 else 0
                    else:
                        rate = 0
                        eta_minutes = 0
                    
                    # Calcular incremento desde última verificação
                    increment = stats['enriched_fixtures'] - last_enriched
                    
                    logger.info(f"""
📊 STATUS DO ENRIQUECIMENTO COMPLETO - {current_time.strftime('%H:%M:%S')}
======================================================================
📈 Total de fixtures: {stats['total_fixtures']:,}
✅ Fixtures enriquecidas: {stats['enriched_fixtures']:,}
⏳ Fixtures restantes: {stats['remaining_fixtures']:,}
📊 Progresso: {stats['completion_percentage']:.1f}%
🚀 Taxa atual: {rate:.1f} fixtures/minuto
⏱️  ETA: {eta_minutes:.1f} minutos
📈 Incremento: +{increment} fixtures
""")
                    
                    last_enriched = stats['enriched_fixtures']
                    
                    # Verificar se concluído
                    if stats['remaining_fixtures'] == 0:
                        logger.info("🎉 ENRIQUECIMENTO COMPLETO CONCLUÍDO!")
                        break
                
                # Aguardar 30 segundos antes da próxima verificação
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                time.sleep(30)

def main():
    """Função principal"""
    try:
        monitor = AllFixturesMonitor()
        monitor.monitor_progress()
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()
