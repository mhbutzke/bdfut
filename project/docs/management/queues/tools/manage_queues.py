#!/usr/bin/env python3
"""
Gerenciador de Filas de Tasks - BDFut
=====================================

Script para gerenciar e monitorar o progresso das filas de tasks dos agentes.
"""

import os
import re
from datetime import datetime
from pathlib import Path

class QueueManager:
    def __init__(self):
        self.queues_dir = Path(__file__).parent
        self.agents = {
            'ORCH': '🎭 Project Orchestrator',
            'SECURITY': '🔐 Security Specialist',
            'ETL': 'ETL Engineer',
            'DATABASE': 'Database Specialist', 
            'QA': 'QA Engineer',
            'DEVOPS': 'DevOps Engineer',
            'FRONTEND': 'Frontend Developer',
            'DOCS': 'Technical Writer'
        }
    
    def get_queue_status(self, agent_code):
        """Obter status de uma fila específica"""
        queue_file = self.queues_dir / f"QUEUE-{agent_code}.md"
        
        if not queue_file.exists():
            return None
            
        content = queue_file.read_text()
        
        # Extrair informações da fila
        status_match = re.search(r'Status da Fila: (.*)', content)
        priority_match = re.search(r'Prioridade: (.*)', content)
        progress_match = re.search(r'Tasks Concluídas: (\d+)/(\d+)', content)
        
        return {
            'status': status_match.group(1) if status_match else 'UNKNOWN',
            'priority': priority_match.group(1) if priority_match else 'UNKNOWN',
            'completed': int(progress_match.group(1)) if progress_match else 0,
            'total': int(progress_match.group(2)) if progress_match else 0,
            'progress': (int(progress_match.group(1)) / int(progress_match.group(2)) * 100) if progress_match else 0
        }
    
    def get_all_queues_status(self):
        """Obter status de todas as filas"""
        status = {}
        for agent_code in self.agents.keys():
            status[agent_code] = self.get_queue_status(agent_code)
        return status
    
    def print_status_report(self):
        """Imprimir relatório de status de todas as filas"""
        print("=" * 80)
        print("📊 RELATÓRIO DE STATUS DAS FILAS - BDFut")
        print("=" * 80)
        print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        status = self.get_all_queues_status()
        
        # Cabeçalho da tabela
        print(f"{'Agente':<20} {'Status':<15} {'Prioridade':<12} {'Progresso':<15} {'Tasks':<10}")
        print("-" * 80)
        
        # Dados das filas
        for agent_code, agent_name in self.agents.items():
            queue_status = status[agent_code]
            if queue_status:
                progress_bar = "█" * int(queue_status['progress'] / 10) + "░" * (10 - int(queue_status['progress'] / 10))
                print(f"{agent_name:<20} {queue_status['status']:<15} {queue_status['priority']:<12} {progress_bar:<15} {queue_status['completed']}/{queue_status['total']}")
            else:
                print(f"{agent_name:<20} {'ERRO':<15} {'N/A':<12} {'N/A':<15} {'N/A'}")
        
        print()
        
        # Resumo geral
        total_completed = sum(s['completed'] for s in status.values() if s)
        total_tasks = sum(s['total'] for s in status.values() if s)
        overall_progress = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
        
        print(f"📈 PROGRESSO GERAL: {overall_progress:.1f}% ({total_completed}/{total_tasks} tasks)")
        print()
        
        # Próximas ações
        print("🎯 PRÓXIMAS AÇÕES RECOMENDADAS:")
        critical_agents = [code for code, status in status.items() if status and status['priority'] == 'CRÍTICA']
        if critical_agents:
            print(f"   🔴 Prioridade CRÍTICA: {', '.join([self.agents[code] for code in critical_agents])}")
        
        high_priority_agents = [code for code, status in status.items() if status and status['priority'] == 'ALTA']
        if high_priority_agents:
            print(f"   🟠 Prioridade ALTA: {', '.join([self.agents[code] for code in high_priority_agents])}")
        
        print()
        print("💡 Use 'python manage_queues.py --help' para mais opções")
    
    def update_task_status(self, agent_code, task_id, new_status):
        """Atualizar status de uma task específica"""
        queue_file = self.queues_dir / f"QUEUE-{agent_code}.md"
        
        if not queue_file.exists():
            print(f"❌ Arquivo de fila não encontrado: {queue_file}")
            return False
        
        content = queue_file.read_text()
        
        # Procurar pela task específica
        task_pattern = rf'### {task_id}:(.*?)(?=###|\Z)'
        task_match = re.search(task_pattern, content, re.DOTALL)
        
        if not task_match:
            print(f"❌ Task {task_id} não encontrada na fila {agent_code}")
            return False
        
        # Atualizar status da task
        old_status = re.search(r'\*\*Status:\*\* (.*)', task_match.group(1))
        if old_status:
            old_status_text = old_status.group(1)
            new_content = content.replace(
                f"**Status:** {old_status_text}",
                f"**Status:** {new_status}"
            )
            
            # Atualizar timestamp
            timestamp_pattern = r'\*\*Última Atualização:\*\* (.*)'
            timestamp_match = re.search(timestamp_pattern, new_content)
            if timestamp_match:
                new_timestamp = datetime.now().strftime('%Y-%m-%d')
                new_content = new_content.replace(
                    f"**Última Atualização:** {timestamp_match.group(1)}",
                    f"**Última Atualização:** {new_timestamp}"
                )
            
            # Salvar arquivo atualizado
            queue_file.write_text(new_content)
            print(f"✅ Status da task {task_id} atualizado para: {new_status}")
            return True
        else:
            print(f"❌ Não foi possível encontrar o status da task {task_id}")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciador de Filas de Tasks - BDFut')
    parser.add_argument('--status', action='store_true', help='Mostrar status de todas as filas')
    parser.add_argument('--update', nargs=3, metavar=('AGENT', 'TASK_ID', 'STATUS'), 
                       help='Atualizar status de uma task (AGENT TASK_ID STATUS)')
    parser.add_argument('--agent', choices=['ORCH', 'SECURITY', 'ETL', 'DATABASE', 'QA', 'DEVOPS', 'FRONTEND', 'DOCS'],
                       help='Mostrar status de um agente específico')
    
    args = parser.parse_args()
    
    manager = QueueManager()
    
    if args.status:
        manager.print_status_report()
    elif args.update:
        agent, task_id, status = args.update
        manager.update_task_status(agent, task_id, status)
    elif args.agent:
        status = manager.get_queue_status(args.agent)
        if status:
            print(f"Status da fila {args.agent}: {status}")
        else:
            print(f"❌ Fila {args.agent} não encontrada")
    else:
        manager.print_status_report()

if __name__ == '__main__':
    main()
