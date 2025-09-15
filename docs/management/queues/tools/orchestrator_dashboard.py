#!/usr/bin/env python3
"""
Dashboard do Orquestrador - BDFut
===============================

Script específico para o Agente Orquestrador gerenciar e monitorar todas as filas.
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

class OrchestratorDashboard:
    def __init__(self):
        self.queues_dir = Path(__file__).parent
        self.agents = {
            'ORCH': '🎭 Project Orchestrator',
            'ETL': 'ETL Engineer',
            'DATABASE': 'Database Specialist', 
            'DEVOPS': 'DevOps Engineer',
            'QA': 'QA Engineer',
            'FRONTEND': 'Frontend Developer',
            'DOCS': 'Technical Writer'
        }
        
        self.priorities = {
            'MÁXIMA': '🔴',
            'CRÍTICA': '🔴', 
            'ALTA': '🟠',
            'MÉDIA': '🟡',
            'BAIXA': '🟢'
        }
    
    def get_queue_status(self, agent_code):
        """Obter status detalhado de uma fila específica"""
        queue_file = self.queues_dir / f"QUEUE-{agent_code}.md"
        
        if not queue_file.exists():
            return None
            
        content = queue_file.read_text()
        
        # Extrair informações da fila
        status_match = re.search(r'Status da Fila: (.*)', content)
        priority_match = re.search(r'Prioridade: (.*)', content)
        progress_match = re.search(r'Tasks Concluídas: (\d+)/(\d+)', content)
        last_update_match = re.search(r'Última Atualização: (.*)', content)
        
        # Extrair tasks críticas
        critical_tasks = re.findall(r'### TASK-.*?\*\*Status:\*\* (🔴 CRÍTICO)', content)
        
        # Extrair impedimentos
        impediments_match = re.search(r'\*\*IMPEDIMENTOS CRÍTICOS:\*\* (.*)', content)
        
        return {
            'status': status_match.group(1) if status_match else 'UNKNOWN',
            'priority': priority_match.group(1) if priority_match else 'UNKNOWN',
            'completed': int(progress_match.group(1)) if progress_match else 0,
            'total': int(progress_match.group(2)) if progress_match else 0,
            'progress': (int(progress_match.group(1)) / int(progress_match.group(2)) * 100) if progress_match else 0,
            'critical_tasks': len(critical_tasks),
            'impediments': impediments_match.group(1) if impediments_match else 'Nenhum identificado',
            'last_update': last_update_match.group(1) if last_update_match else 'N/A'
        }
    
    def get_all_queues_status(self):
        """Obter status de todas as filas"""
        status = {}
        for agent_code in self.agents.keys():
            status[agent_code] = self.get_queue_status(agent_code)
        return status
    
    def print_orchestrator_dashboard(self):
        """Imprimir dashboard completo do orquestrador"""
        print("=" * 100)
        print("🎭 DASHBOARD DO ORQUESTRADOR - BDFut")
        print("=" * 100)
        print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        status = self.get_all_queues_status()
        
        # Resumo executivo
        total_completed = sum(s['completed'] for s in status.values() if s)
        total_tasks = sum(s['total'] for s in status.values() if s)
        overall_progress = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
        
        critical_agents = [code for code, s in status.items() if s and s['priority'] in ['MÁXIMA', 'CRÍTICA']]
        critical_tasks_total = sum(s['critical_tasks'] for s in status.values() if s)
        
        print("📊 RESUMO EXECUTIVO")
        print("-" * 50)
        print(f"Progresso Geral: {overall_progress:.1f}% ({total_completed}/{total_tasks} tasks)")
        print(f"Agentes Críticos: {len(critical_agents)}")
        print(f"Tasks Críticas: {critical_tasks_total}")
        print(f"Impedimentos: {sum(1 for s in status.values() if s and 'Nenhum' not in s['impediments'])}")
        print()
        
        # Status detalhado por agente
        print("📋 STATUS DETALHADO POR AGENTE")
        print("-" * 100)
        print(f"{'Agente':<25} {'Prioridade':<12} {'Progresso':<15} {'Tasks':<10} {'Críticas':<10} {'Impedimentos':<15}")
        print("-" * 100)
        
        for agent_code, agent_name in self.agents.items():
            queue_status = status[agent_code]
            if queue_status:
                progress_bar = "█" * int(queue_status['progress'] / 10) + "░" * (10 - int(queue_status['progress'] / 10))
                priority_icon = self.priorities.get(queue_status['priority'], '⚪')
                impediment_status = "🔴" if "Nenhum" not in queue_status['impediments'] else "🟢"
                
                print(f"{agent_name:<25} {priority_icon} {queue_status['priority']:<10} {progress_bar:<15} {queue_status['completed']}/{queue_status['total']:<8} {queue_status['critical_tasks']:<10} {impediment_status}")
            else:
                print(f"{agent_name:<25} {'❌ ERRO':<12} {'N/A':<15} {'N/A':<10} {'N/A':<10} {'❌':<15}")
        
        print()
        
        # Alertas e ações recomendadas
        print("🚨 ALERTAS E AÇÕES RECOMENDADAS")
        print("-" * 50)
        
        # Verificar agentes com impedimentos
        agents_with_impediments = [code for code, s in status.items() if s and "Nenhum" not in s['impediments']]
        if agents_with_impediments:
            print("🔴 IMPEDIMENTOS CRÍTICOS:")
            for agent_code in agents_with_impediments:
                agent_name = self.agents[agent_code]
                impediment = status[agent_code]['impediments']
                print(f"   • {agent_name}: {impediment}")
        else:
            print("🟢 Nenhum impedimento crítico identificado")
        
        print()
        
        # Verificar tasks críticas
        if critical_tasks_total > 0:
            print("🔴 TASKS CRÍTICAS PENDENTES:")
            for agent_code, s in status.items():
                if s and s['critical_tasks'] > 0:
                    agent_name = self.agents[agent_code]
                    print(f"   • {agent_name}: {s['critical_tasks']} tasks críticas")
        else:
            print("🟢 Nenhuma task crítica pendente")
        
        print()
        
        # Próximas ações
        print("🎯 PRÓXIMAS AÇÕES RECOMENDADAS:")
        if critical_agents:
            print("1. 🔴 Prioridade MÁXIMA:")
            for agent_code in critical_agents:
                agent_name = self.agents[agent_code]
                print(f"   • {agent_name}: Verificar status e impedimentos")
        
        print("2. 📊 Monitoramento:")
        print("   • Verificar progresso diário de todas as filas")
        print("   • Identificar dependências bloqueadas")
        print("   • Coordenar handoffs entre agentes")
        
        print()
        print("💡 Use 'python orchestrator_dashboard.py --help' para mais opções")
    
    def check_dependencies(self):
        """Verificar dependências entre agentes"""
        print("🔗 ANÁLISE DE DEPENDÊNCIAS")
        print("-" * 50)
        
        dependencies = {
            'ETL': ['DATABASE'],  # ETL precisa de schema otimizado
            'DATABASE': ['QA'],   # Database precisa de testes
            'QA': ['DEVOPS'],     # QA precisa de CI/CD
            'FRONTEND': ['ETL', 'DATABASE'],  # Frontend precisa de dados
            'DOCS': ['ETL', 'DATABASE', 'DEVOPS']  # Docs precisa de tudo
        }
        
        status = self.get_all_queues_status()
        
        for agent, deps in dependencies.items():
            agent_name = self.agents[agent]
            agent_progress = status[agent]['progress'] if status[agent] else 0
            
            print(f"\n📋 {agent_name}:")
            print(f"   Progresso: {agent_progress:.1f}%")
            
            if deps:
                print("   Dependências:")
                for dep in deps:
                    dep_name = self.agents[dep]
                    dep_progress = status[dep]['progress'] if status[dep] else 0
                    status_icon = "🟢" if dep_progress > 50 else "🟡" if dep_progress > 0 else "🔴"
                    print(f"     {status_icon} {dep_name}: {dep_progress:.1f}%")
            else:
                print("   Sem dependências")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Dashboard do Orquestrador - BDFut')
    parser.add_argument('--dashboard', action='store_true', help='Mostrar dashboard completo')
    parser.add_argument('--dependencies', action='store_true', help='Analisar dependências entre agentes')
    parser.add_argument('--summary', action='store_true', help='Mostrar resumo executivo')
    
    args = parser.parse_args()
    
    dashboard = OrchestratorDashboard()
    
    if args.dashboard:
        dashboard.print_orchestrator_dashboard()
    elif args.dependencies:
        dashboard.check_dependencies()
    elif args.summary:
        status = dashboard.get_all_queues_status()
        total_completed = sum(s['completed'] for s in status.values() if s)
        total_tasks = sum(s['total'] for s in status.values() if s)
        overall_progress = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
        print(f"📊 Progresso Geral: {overall_progress:.1f}% ({total_completed}/{total_tasks} tasks)")
    else:
        dashboard.print_orchestrator_dashboard()

if __name__ == '__main__':
    main()
