#!/usr/bin/env python3
"""
Script para monitorar o progresso do enriquecimento
e atualizar status das tasks no Task Master
"""

import os
import sys
import json
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnrichmentProgressMonitor:
    def __init__(self):
        self.supabase = SupabaseClient()
        self.tasks_file = Path('.taskmaster/tasks/tasks.json')
        self.start_time = time.time()
        
        # Contadores iniciais
        self.initial_counts = self.get_current_counts()
        
    def get_current_counts(self):
        """Obter contagens atuais das tabelas"""
        try:
            counts = {}
            tables = ['match_events', 'match_lineups', 'match_statistics']
            
            for table in tables:
                response = self.supabase.client.table(table).select('id', count='exact').execute()
                counts[table] = response.count
            
            return counts
        except Exception as e:
            logger.error(f"Erro ao obter contagens: {e}")
            return {}
    
    def load_tasks(self):
        """Carregar tasks do Task Master"""
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar tasks: {e}")
            return []
    
    def save_tasks(self, tasks):
        """Salvar tasks no Task Master"""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar tasks: {e}")
    
    def update_task_status(self, task_id, status, details_update=None):
        """Atualizar status de uma task"""
        try:
            tasks = self.load_tasks()
            
            for task in tasks:
                if task['id'] == task_id:
                    old_status = task['status']
                    task['status'] = status
                    
                    if details_update:
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        task['details'] += f"\n\n[{current_time}] {details_update}"
                    
                    logger.info(f"📝 Task {task_id} atualizada: {old_status} → {status}")
                    break
            
            self.save_tasks(tasks)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar task {task_id}: {e}")
    
    def check_enrichment_completion(self):
        """Verificar se enriquecimentos foram concluídos"""
        try:
            current_counts = self.get_current_counts()
            
            # Verificar se eventos aumentaram significativamente
            events_increase = current_counts.get('match_events', 0) - self.initial_counts.get('match_events', 0)
            
            # Verificar se lineups aumentaram significativamente  
            lineups_increase = current_counts.get('match_lineups', 0) - self.initial_counts.get('match_lineups', 0)
            
            # Verificar se estatísticas aumentaram significativamente
            stats_increase = current_counts.get('match_statistics', 0) - self.initial_counts.get('match_statistics', 0)
            
            return {
                'events_increase': events_increase,
                'lineups_increase': lineups_increase,
                'stats_increase': stats_increase,
                'current_counts': current_counts
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar conclusão: {e}")
            return {}
    
    def monitor_progress(self, interval: int = 60):
        """Monitorar progresso do enriquecimento"""
        logger.info("🔍 INICIANDO MONITORAMENTO DO ENRIQUECIMENTO")
        logger.info("=" * 60)
        
        logger.info(f"📊 Contagens iniciais:")
        for table, count in self.initial_counts.items():
            logger.info(f"   {table}: {count:,}")
        
        iteration = 0
        while True:
            try:
                iteration += 1
                elapsed = time.time() - self.start_time
                
                # Verificar progresso
                progress = self.check_enrichment_completion()
                
                logger.info(f"\\n📊 RELATÓRIO #{iteration} - {time.strftime('%H:%M:%S')}")
                logger.info("=" * 50)
                logger.info(f"⏱️ Tempo decorrido: {elapsed/60:.1f} minutos")
                
                # Mostrar aumentos
                if progress:
                    logger.info(f"📈 Eventos: +{progress['events_increase']:,}")
                    logger.info(f"👥 Lineups: +{progress['lineups_increase']:,}")
                    logger.info(f"📊 Estatísticas: +{progress['stats_increase']:,}")
                    
                    # Verificar se algum enriquecimento foi concluído
                    if progress['events_increase'] > 1000:  # Threshold para considerar concluído
                        self.update_task_status('6', 'completed', 
                            f"Enriquecimento de eventos concluído. +{progress['events_increase']:,} eventos inseridos.")
                    
                    if progress['lineups_increase'] > 1000:  # Threshold para considerar concluído
                        self.update_task_status('7', 'completed',
                            f"Enriquecimento de lineups concluído. +{progress['lineups_increase']:,} lineups inseridos.")
                    
                    if progress['stats_increase'] > 100:  # Threshold para considerar concluído
                        self.update_task_status('8', 'completed',
                            f"Enriquecimento de estatísticas concluído. +{progress['stats_increase']:,} estatísticas inseridas.")
                
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
    monitor = EnrichmentProgressMonitor()
    
    # Monitorar a cada 60 segundos
    monitor.monitor_progress(interval=60)

if __name__ == "__main__":
    main()
