#!/usr/bin/env python3
"""
Script para criar tasks detalhadas no Task Master
para o planejamento completo de enriquecimento
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

def create_enrichment_tasks():
    """Criar tasks detalhadas para o planejamento de enriquecimento"""
    
    tasks = [
        {
            "id": "1",
            "title": "Análise e Validação da Estrutura das Tabelas",
            "description": "Verificar e documentar a estrutura atual das tabelas match_events, match_lineups e match_statistics",
            "status": "completed",
            "priority": "high",
            "dependencies": [],
            "details": """
            ✅ CONCLUÍDO - Análise completa realizada em 17/09/2025
            
            Estruturas identificadas:
            - match_events: 20 campos (id, fixture_id, type_id, event_type, minute, etc.)
            - match_lineups: 26 campos (id, fixture_id, team_id, player_id, type, etc.)
            - match_statistics: 40+ campos (id, fixture_id, team_id, shots_total, etc.)
            
            Status atual:
            - match_events: 62.781 registros
            - match_lineups: 18.424 registros
            - match_statistics: 1.474 registros
            """,
            "testStrategy": "Verificação manual da estrutura via Supabase e documentação completa"
        },
        {
            "id": "2", 
            "title": "Análise Detalhada da API Sportmonks",
            "description": "Mapear campos disponíveis na API Sportmonks para eventos, lineups e estatísticas",
            "status": "completed",
            "priority": "high", 
            "dependencies": ["1"],
            "details": """
            ✅ CONCLUÍDO - Mapeamento completo realizado em 17/09/2025
            
            API Endpoints analisados:
            - /fixtures/{id}?include=events
            - /fixtures/{id}?include=lineups  
            - /fixtures/{id}?include=statistics
            
            Campos identificados:
            - Events: 19 campos (id, type_id, participant_id, player_id, minute, etc.)
            - Lineups: 11 campos (id, team_id, player_id, type_id, position_id, etc.)
            - Statistics: 6 campos (id, type_id, participant_id, data, location, etc.)
            
            Mapeamento type_id para estatísticas:
            - 41-54: Mapeados para campos específicos (shots_total, yellow_cards, etc.)
            """,
            "testStrategy": "Teste com fixture específica (18863344) validando estrutura completa"
        },
        {
            "id": "3",
            "title": "Definição do Mapeamento API → Banco de Dados",
            "description": "Criar mapeamento detalhado entre campos da API e estrutura do banco",
            "status": "completed",
            "priority": "high",
            "dependencies": ["1", "2"],
            "details": """
            ✅ CONCLUÍDO - Mapeamento validado em 17/09/2025
            
            MATCH_EVENTS:
            - participant_id → team_id
            - addition → event_type
            - sort_order → sort_order
            - Campos removidos: var, var_reason, coordinates (não disponíveis na API)
            
            MATCH_LINEUPS:
            - type_id (11/12) → type (lineup/substitute)
            - Campos removidos: campos de substituição detalhada (não disponíveis na API)
            
            MATCH_STATISTICS:
            - Agrupamento por team_id (participant_id)
            - Mapeamento type_id → campos específicos
            - Estratégia: 1 registro por time com múltiplos campos
            """,
            "testStrategy": "Validação com fixture de teste mostrando mapeamento correto"
        },
        {
            "id": "4",
            "title": "Criação dos Scripts de Enriquecimento Otimizados",
            "description": "Desenvolver scripts otimizados para enriquecimento de cada tabela",
            "status": "completed",
            "priority": "high",
            "dependencies": ["3"],
            "details": """
            ✅ CONCLUÍDO - Scripts criados em 17/09/2025
            
            Scripts desenvolvidos:
            - 20_events_enrichment.py: Enriquecimento de eventos
            - 20_lineups_enrichment.py: Enriquecimento de lineups
            - 20_statistics_enrichment.py: Enriquecimento de estatísticas
            - 20_test_single_fixture.py: Validação de mapeamento
            
            Características:
            - Rate limiting: 1 req/segundo
            - Batch processing: 100 fixtures por lote
            - Upsert strategy: on_conflict='id'
            - Error handling completo
            - Logs detalhados
            """,
            "testStrategy": "Teste com fixture específica validando inserção correta"
        },
        {
            "id": "5",
            "title": "Validação do Mapeamento com Fixture de Teste",
            "description": "Testar mapeamento completo com uma fixture específica",
            "status": "completed",
            "priority": "medium",
            "dependencies": ["4"],
            "details": """
            ✅ CONCLUÍDO - Validação realizada em 17/09/2025
            
            Fixture testada: 18863344 (RB Leipzig vs Bayer 04 Leverkusen)
            
            Resultados:
            - Events: 19 eventos mapeados corretamente
            - Lineups: 40 lineups mapeados corretamente  
            - Statistics: 86 estatísticas → 2 registros agrupados por time
            
            Mapeamento validado:
            - Todos os campos da API mapeados corretamente
            - Estratégia de agrupamento funcionando
            - IDs únicos gerados corretamente
            """,
            "testStrategy": "Execução do script de teste com validação manual dos dados"
        },
        {
            "id": "6",
            "title": "Execução do Enriquecimento de Eventos",
            "description": "Executar enriquecimento completo da tabela match_events",
            "status": "in-progress",
            "priority": "high",
            "dependencies": ["5"],
            "details": """
            🔄 EM ANDAMENTO - Iniciado em 17/09/2025
            
            Script: 20_events_enrichment.py
            Target: ~11.000 fixtures sem eventos
            
            Estimativas:
            - Fixtures: ~11.000
            - Eventos por fixture: ~19
            - Total esperado: ~209.000 eventos
            - Tempo estimado: ~18 minutos
            
            Status: Executando em background
            """,
            "testStrategy": "Monitoramento em tempo real e validação de inserção"
        },
        {
            "id": "7",
            "title": "Execução do Enriquecimento de Lineups",
            "description": "Executar enriquecimento completo da tabela match_lineups",
            "status": "pending",
            "priority": "high",
            "dependencies": ["6"],
            "details": """
            ⏳ PENDENTE - Aguardando conclusão dos eventos
            
            Script: 20_lineups_enrichment.py
            Target: Fixtures sem lineups
            
            Estimativas:
            - Fixtures: ~11.000
            - Lineups por fixture: ~40
            - Total esperado: ~440.000 lineups
            - Tempo estimado: ~18 minutos
            
            Estratégia: Executar após conclusão dos eventos
            """,
            "testStrategy": "Execução sequencial após validação dos eventos"
        },
        {
            "id": "8",
            "title": "Execução do Enriquecimento de Estatísticas",
            "description": "Executar enriquecimento completo da tabela match_statistics",
            "status": "pending",
            "priority": "high",
            "dependencies": ["7"],
            "details": """
            ⏳ PENDENTE - Aguardando conclusão dos lineups
            
            Script: 20_statistics_enrichment.py
            Target: Fixtures sem estatísticas
            
            Estimativas:
            - Fixtures: ~11.000
            - Estatísticas por fixture: ~2 (1 por time)
            - Total esperado: ~22.000 estatísticas
            - Tempo estimado: ~18 minutos
            
            Estratégia: Executar após conclusão dos lineups
            """,
            "testStrategy": "Execução sequencial após validação dos lineups"
        },
        {
            "id": "9",
            "title": "Validação da Qualidade dos Dados Inseridos",
            "description": "Verificar qualidade e completude dos dados inseridos",
            "status": "pending",
            "priority": "medium",
            "dependencies": ["8"],
            "details": """
            ⏳ PENDENTE - Aguardando conclusão de todos os enriquecimentos
            
            Validações a realizar:
            - Contagem total de registros por tabela
            - Verificação de integridade referencial
            - Análise de cobertura por ano/liga
            - Validação de campos obrigatórios
            - Verificação de duplicatas
            
            Relatórios a gerar:
            - Status de enriquecimento por tabela
            - Cobertura temporal dos dados
            - Análise de qualidade dos dados
            """,
            "testStrategy": "Queries de validação e relatórios de qualidade"
        },
        {
            "id": "10",
            "title": "Análise de Dados para Mercados de Cartões",
            "description": "Analisar dados enriquecidos focando em mercados de cartões",
            "status": "pending",
            "priority": "medium",
            "dependencies": ["9"],
            "details": """
            ⏳ PENDENTE - Aguardando validação dos dados
            
            Análises a realizar:
            - Frequência de cartões amarelos/vermelhos por liga
            - Padrões de cartões por jogador/posição
            - Correlação entre faltas e cartões
            - Análise temporal (minutos mais críticos)
            - Comparação entre times/ligas
            
            Dados importantes identificados:
            - Events: type_id para cartões, minute, player_id
            - Statistics: yellow_cards, red_cards por time
            - Lineups: posições dos jogadores que receberam cartões
            """,
            "testStrategy": "Queries analíticas e visualizações de dados"
        },
        {
            "id": "11",
            "title": "Documentação Final do Enriquecimento",
            "description": "Documentar processo completo e resultados obtidos",
            "status": "pending",
            "priority": "low",
            "dependencies": ["10"],
            "details": """
            ⏳ PENDENTE - Aguardando conclusão das análises
            
            Documentação a criar:
            - Relatório final de enriquecimento
            - Estatísticas de performance
            - Mapeamento final API → Banco
            - Guia de uso dos dados para análise
            - Recomendações para futuros enriquecimentos
            
            Arquivos a atualizar:
            - ENRICHMENT_FINAL_REPORT.md
            - API_MAPPING_GUIDE.md
            - DATA_QUALITY_REPORT.md
            """,
            "testStrategy": "Revisão completa da documentação e validação"
        },
        {
            "id": "12",
            "title": "Otimização e Monitoramento Contínuo",
            "description": "Implementar monitoramento e otimizações para enriquecimentos futuros",
            "status": "pending",
            "priority": "low",
            "dependencies": ["11"],
            "details": """
            ⏳ PENDENTE - Aguardando documentação final
            
            Otimizações a implementar:
            - Sistema de monitoramento de qualidade
            - Alertas para dados incompletos
            - Otimização de queries de análise
            - Cache inteligente para consultas frequentes
            
            Monitoramento:
            - Dashboard de status das tabelas
            - Alertas de qualidade de dados
            - Métricas de performance da API
            - Relatórios automáticos de cobertura
            """,
            "testStrategy": "Implementação de dashboards e alertas"
        }
    ]
    
    return tasks

def save_tasks_to_file(tasks, file_path):
    """Salvar tasks no arquivo JSON do Task Master"""
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Salvar tasks
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Tasks salvas em: {file_path}")
        print(f"📊 Total de tasks: {len(tasks)}")
        
    except Exception as e:
        print(f"❌ Erro ao salvar tasks: {e}")

def main():
    """Função principal"""
    print("🚀 CRIANDO TASKS DETALHADAS PARA ENRIQUECIMENTO")
    print("=" * 60)
    
    # Criar tasks
    tasks = create_enrichment_tasks()
    
    # Caminho do arquivo de tasks
    tasks_file = Path('.taskmaster/tasks/tasks.json')
    
    # Salvar tasks
    save_tasks_to_file(tasks, tasks_file)
    
    # Mostrar resumo
    print("\n📋 RESUMO DAS TASKS CRIADAS:")
    print("=" * 40)
    
    status_counts = {}
    for task in tasks:
        status = task['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        emoji = "✅" if status == "completed" else "🔄" if status == "in-progress" else "⏳"
        print(f"{emoji} {status.title()}: {count} tasks")
    
    print(f"\n🎯 PRÓXIMAS AÇÕES:")
    print("1. Verificar tasks no Task Master")
    print("2. Executar enriquecimento de lineups")
    print("3. Executar enriquecimento de estatísticas")
    print("4. Validar qualidade dos dados")

if __name__ == "__main__":
    main()
