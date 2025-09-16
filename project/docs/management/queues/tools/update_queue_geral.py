#!/usr/bin/env python3
"""
Script para Atualizar QUEUE-GERAL.md
====================================

Script para agentes atualizarem automaticamente a QUEUE-GERAL.md
quando concluírem tasks ou fizerem modificações.
"""

import os
import re
from datetime import datetime
from pathlib import Path

class QueueGeralUpdater:
    def __init__(self):
        self.queues_dir = Path(__file__).parent
        self.queue_geral_file = self.queues_dir / "QUEUE-GERAL.md"
        
    def mark_task_completed(self, task_id, agent_name, completion_notes=""):
        """Marcar uma task como concluída na QUEUE-GERAL"""
        if not self.queue_geral_file.exists():
            print(f"❌ QUEUE-GERAL.md não encontrada!")
            return False
            
        content = self.queue_geral_file.read_text()
        
        # Procurar pela task específica
        task_pattern = rf'\*\*{task_id}\*\* \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|'
        task_match = re.search(task_pattern, content)
        
        if not task_match:
            print(f"❌ Task {task_id} não encontrada na QUEUE-GERAL!")
            return False
        
        # Substituir status por ✅ CONCLUÍDO
        old_line = task_match.group(0)
        new_line = old_line.replace(task_match.group(4), "✅ CONCLUÍDO")
        
        new_content = content.replace(old_line, new_line)
        
        # Adicionar ao histórico de atualizações
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        history_entry = f"| {timestamp} | {agent_name} | CONCLUÍDA | {task_id} - {completion_notes} |"
        
        # Encontrar seção de histórico e adicionar
        history_pattern = r'(\| Data \| Agente \| Ação \| Detalhes \|\n\|------|--------|------|----------\|\n)'
        history_match = re.search(history_pattern, new_content)
        
        if history_match:
            new_content = new_content.replace(
                history_match.group(1),
                history_match.group(1) + history_entry + "\n"
            )
        
        # Salvar arquivo atualizado
        self.queue_geral_file.write_text(new_content)
        print(f"✅ Task {task_id} marcada como CONCLUÍDA na QUEUE-GERAL!")
        return True
    
    def add_new_task(self, task_id, agent_emoji, agent_name, description, status, dependencies, deadline):
        """Adicionar nova task à QUEUE-GERAL"""
        if not self.queue_geral_file.exists():
            print(f"❌ QUEUE-GERAL.md não encontrada!")
            return False
            
        content = self.queue_geral_file.read_text()
        
        # Criar linha da nova task
        new_task_line = f"| **{task_id}** | {agent_emoji} {agent_name} | {description} | {status} | {dependencies} | {deadline} |"
        
        # Encontrar local apropriado para inserir (baseado na fase)
        if task_id.endswith('-001'):
            # Task crítica - inserir na FASE 1
            pattern = r'(\| \*\*ORCH-001\*\* \| .+? \|\n)'
            replacement = r'\1' + new_task_line + "\n"
        else:
            # Inserir na fase apropriada baseada no número
            pattern = r'(\| \*\*' + task_id.split('-')[0] + r'-\d+\*\* \| .+? \|\n)(?=\n|\|)'
            replacement = r'\1' + new_task_line + "\n"
        
        new_content = re.sub(pattern, replacement, content)
        
        # Adicionar ao histórico
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        history_entry = f"| {timestamp} | {agent_name} | ADICIONADA | {task_id} - {description} |"
        
        history_pattern = r'(\| Data \| Agente \| Ação \| Detalhes \|\n\|------|--------|------|----------\|\n)'
        history_match = re.search(history_pattern, new_content)
        
        if history_match:
            new_content = new_content.replace(
                history_match.group(1),
                history_match.group(1) + history_entry + "\n"
            )
        
        # Salvar arquivo atualizado
        self.queue_geral_file.write_text(new_content)
        print(f"✅ Task {task_id} adicionada à QUEUE-GERAL!")
        return True
    
    def update_progress_summary(self):
        """Atualizar resumo de progresso na QUEUE-GERAL"""
        if not self.queue_geral_file.exists():
            print(f"❌ QUEUE-GERAL.md não encontrada!")
            return False
            
        content = self.queue_geral_file.read_text()
        
        # Contar tasks por status
        completed_tasks = len(re.findall(r'\| \*\*.*?\*\* \| .+? \| .+? \| ✅ CONCLUÍDO \|', content))
        total_tasks = len(re.findall(r'\| \*\*.*?\*\* \| .+? \| .+? \| .+? \| .+? \| .+? \|', content))
        
        if total_tasks > 0:
            progress_percentage = (completed_tasks / total_tasks) * 100
            
            # Atualizar linha de progresso geral
            progress_pattern = r'\*\*TOTAL\*\* \| \*\*\d+ tasks\*\* \| \*\*\d+\*\* \| \*\*\d+\*\* \| \*\*\d+\*\* \| \*\*\d+%\*\* \|'
            new_progress_line = f"**TOTAL** | **{total_tasks} tasks** | **{completed_tasks}** | **0** | **{total_tasks - completed_tasks}** | **{progress_percentage:.0f}%** |"
            
            new_content = re.sub(progress_pattern, new_progress_line, content)
            
            # Salvar arquivo atualizado
            self.queue_geral_file.write_text(new_content)
            print(f"✅ Progresso geral atualizado: {progress_percentage:.1f}% ({completed_tasks}/{total_tasks})")
            return True
        
        return False
    
    def print_current_status(self):
        """Imprimir status atual da QUEUE-GERAL"""
        if not self.queue_geral_file.exists():
            print(f"❌ QUEUE-GERAL.md não encontrada!")
            return
            
        content = self.queue_geral_file.read_text()
        
        # Extrair tasks críticas pendentes
        critical_tasks = re.findall(r'\| \*\*(.*?)\*\* \| (.+?) \| (.+?) \| 🔴 CRÍTICO \| (.+?) \| (.+?) \|', content)
        
        print("=" * 80)
        print("🗺️ STATUS ATUAL DA QUEUE-GERAL")
        print("=" * 80)
        
        if critical_tasks:
            print("🔴 TASKS CRÍTICAS PENDENTES:")
            for task_id, agent, description, deps, deadline in critical_tasks:
                print(f"   • {task_id} ({agent}): {description}")
                if deps != "Nenhuma":
                    print(f"     Dependências: {deps}")
        else:
            print("🟢 Nenhuma task crítica pendente")
        
        # Extrair progresso geral
        progress_match = re.search(r'\*\*TOTAL\*\* \| \*\*(\d+) tasks\*\* \| \*\*(\d+)\*\* \| \*\*\d+\*\* \| \*\*\d+\*\* \| \*\*(\d+)%\*\* \|', content)
        if progress_match:
            total, completed, percentage = progress_match.groups()
            print(f"\n📊 PROGRESSO GERAL: {percentage}% ({completed}/{total} tasks)")
        
        print("\n💡 Use os comandos abaixo para atualizar:")
        print("   python3 update_queue_geral.py --complete TASK-ID 'AGENTE' 'Notas de conclusão'")
        print("   python3 update_queue_geral.py --add TASK-ID 'AGENTE' 'Descrição' 'Status' 'Deps' 'Prazo'")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Atualizador da QUEUE-GERAL - BDFut')
    parser.add_argument('--complete', nargs=3, metavar=('TASK_ID', 'AGENT', 'NOTES'), 
                       help='Marcar task como concluída')
    parser.add_argument('--add', nargs=6, metavar=('TASK_ID', 'AGENT', 'DESC', 'STATUS', 'DEPS', 'DEADLINE'), 
                       help='Adicionar nova task')
    parser.add_argument('--status', action='store_true', help='Mostrar status atual')
    parser.add_argument('--update-progress', action='store_true', help='Atualizar resumo de progresso')
    
    args = parser.parse_args()
    
    updater = QueueGeralUpdater()
    
    if args.complete:
        task_id, agent, notes = args.complete
        updater.mark_task_completed(task_id, agent, notes)
        updater.update_progress_summary()
    elif args.add:
        task_id, agent, desc, status, deps, deadline = args.add
        updater.add_new_task(task_id, "🔧", agent, desc, status, deps, deadline)
    elif args.update_progress:
        updater.update_progress_summary()
    else:
        updater.print_current_status()

if __name__ == '__main__':
    main()
