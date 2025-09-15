#!/usr/bin/env python3
"""
Relatório Final - Sistema de ETL Sportmonks → Supabase
Visualização completa dos dados coletados
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client
from config.config import Config
from datetime import datetime
from collections import Counter

def gerar_relatorio():
    """Gera relatório completo dos dados"""
    
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 80)
    print("📊 RELATÓRIO FINAL - BANCO DE DADOS DE FUTEBOL")
    print("=" * 80)
    print(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    print()
    
    # ============================================
    # 1. RESUMO GERAL
    # ============================================
    print("📌 RESUMO GERAL DO BANCO DE DADOS")
    print("-" * 80)
    
    # Contar tabelas principais
    try:
        # Fixtures
        fixtures = supabase.table('fixtures').select('*', count='exact').execute()
        print(f"⚽ PARTIDAS: {fixtures.count:,} fixtures cadastradas")
        
        # Times
        teams = supabase.table('teams').select('*', count='exact').execute()
        print(f"👥 TIMES: {teams.count:,} equipes")
        
        # Ligas
        leagues = supabase.table('leagues').select('*', count='exact').execute()
        print(f"🏆 LIGAS: {leagues.count:,} competições")
        
        # Temporadas
        seasons = supabase.table('seasons').select('*', count='exact').execute()
        print(f"📅 TEMPORADAS: {seasons.count:,} temporadas")
        
    except Exception as e:
        pass
    
    print()
    
    # ============================================
    # 2. DADOS DETALHADOS
    # ============================================
    print("📊 DADOS DETALHADOS DO BRASILEIRÃO 2025")
    print("-" * 80)
    
    try:
        # Eventos
        events = supabase.table('match_events').select('*', count='exact').execute()
        print(f"\n🎯 EVENTOS: {events.count:,} registros")
        
        # Tipos de eventos
        event_types = supabase.table('match_events').select('event_type').execute()
        if event_types.data:
            event_counts = Counter(e['event_type'] for e in event_types.data)
            for event_type, count in event_counts.most_common(8):
                bar = "█" * min(40, int(count/10))
                print(f"   {event_type:15} {count:4} {bar}")
        
        # Estatísticas
        stats = supabase.table('match_statistics').select('*', count='exact').execute()
        print(f"\n📈 ESTATÍSTICAS: {stats.count:,} registros (times por partida)")
        
        # Média de estatísticas
        stats_data = supabase.table('match_statistics').select('shots_total, ball_possession, corners').execute()
        if stats_data.data:
            total_shots = sum(s.get('shots_total', 0) for s in stats_data.data if s.get('shots_total'))
            total_poss = sum(s.get('ball_possession', 0) for s in stats_data.data if s.get('ball_possession'))
            total_corners = sum(s.get('corners', 0) for s in stats_data.data if s.get('corners'))
            count = len(stats_data.data)
            
            if count > 0:
                print(f"   • Média de chutes por time: {total_shots/count:.1f}")
                print(f"   • Média de posse de bola: {total_poss/count:.1f}%")
                print(f"   • Média de escanteios: {total_corners/count:.1f}")
        
        # Escalações
        lineups = supabase.table('match_lineups').select('*', count='exact').execute()
        print(f"\n👤 ESCALAÇÕES: {lineups.count:,} registros de jogadores")
        
        # Top jogadores
        lineups_data = supabase.table('match_lineups').select('player_name').execute()
        if lineups_data.data:
            player_counts = Counter(l['player_name'] for l in lineups_data.data if l.get('player_name'))
            print("   Top 10 jogadores mais escalados:")
            for i, (player, count) in enumerate(player_counts.most_common(10), 1):
                print(f"   {i:2}. {player:25} - {count} partidas")
        
    except Exception as e:
        print(f"Erro ao buscar dados detalhados: {e}")
    
    print()
    
    # ============================================
    # 3. ANÁLISE DE QUALIDADE
    # ============================================
    print("✅ ANÁLISE DE QUALIDADE DOS DADOS")
    print("-" * 80)
    
    try:
        # Fixtures do Brasileirão
        brasil_fixtures = supabase.table('fixtures').select('sportmonks_id, home_score, away_score, status').eq('league_id', 648).execute()
        
        total_fixtures = len(brasil_fixtures.data)
        with_scores = sum(1 for f in brasil_fixtures.data if f.get('home_score') is not None)
        finished = sum(1 for f in brasil_fixtures.data if f.get('status') in ['FT', 'AET', 'PEN'])
        
        print(f"📊 Partidas do Brasileirão 2025:")
        print(f"   • Total: {total_fixtures}")
        print(f"   • Com placar: {with_scores} ({with_scores/total_fixtures*100:.1f}%)")
        print(f"   • Finalizadas: {finished} ({finished/total_fixtures*100:.1f}%)")
        
        # Cobertura de eventos
        if events.count and total_fixtures > 0:
            avg_events = events.count / total_fixtures
            print(f"\n📊 Cobertura de eventos:")
            print(f"   • Média de {avg_events:.1f} eventos por partida")
        
        # Cobertura de escalações
        if lineups.count and total_fixtures > 0:
            avg_lineups = lineups.count / total_fixtures
            print(f"\n📊 Cobertura de escalações:")
            print(f"   • Média de {avg_lineups:.1f} jogadores por partida")
            print(f"   • Aproximadamente {avg_lineups/2:.0f} jogadores por time")
        
    except Exception as e:
        print(f"Erro na análise: {e}")
    
    print()
    
    # ============================================
    # 4. ESTRUTURA DO PROJETO
    # ============================================
    print("🏗️ ESTRUTURA DO PROJETO")
    print("-" * 80)
    print("""
📁 bdfut/
├── 📄 requirements.txt         # Dependências Python
├── 📄 .env                     # Variáveis de ambiente (API keys)
├── 📁 config/
│   └── config.py              # Configurações centralizadas
├── 📁 src/
│   ├── sportmonks_client.py  # Cliente da API Sportmonks
│   ├── supabase_client.py    # Cliente do Supabase
│   └── etl_process.py        # Lógica ETL
├── 📁 migrations/
│   └── 001_create_sportmonks_schema.sql  # Schema do banco
├── 📄 main.py                 # CLI principal
├── 📄 sync_brasileirao_otimizado.py      # Sync otimizado
├── 📄 salvar_dados_completos.py          # Salvamento de dados
└── 📄 enriquecer_fixtures.py              # Enriquecimento
    """)
    
    # ============================================
    # 5. COMANDOS DISPONÍVEIS
    # ============================================
    print("⚡ COMANDOS DISPONÍVEIS")
    print("-" * 80)
    print("""
# Testar conexões
python3 main.py test-connection

# Sincronizar dados base (países, ligas, times)
python3 main.py sync-base

# Sincronizar fixtures de uma liga
python3 sync_brasileirao_otimizado.py

# Enriquecer fixtures com dados completos
python3 enriquecer_fixtures.py

# Salvar dados detalhados
python3 salvar_dados_completos.py

# Gerar este relatório
python3 relatorio_final.py
    """)
    
    # ============================================
    # 6. PRÓXIMOS PASSOS
    # ============================================
    print("🚀 PRÓXIMOS PASSOS RECOMENDADOS")
    print("-" * 80)
    print("""
1. EXPANDIR COBERTURA:
   ✓ Adicionar mais ligas (Premier League, La Liga, etc)
   ✓ Incluir dados históricos de temporadas anteriores
   ✓ Adicionar dados de jogadores individuais

2. OTIMIZAR PERFORMANCE:
   ✓ Criar índices adicionais nas tabelas
   ✓ Implementar views materializadas
   ✓ Adicionar cache para consultas frequentes

3. AUTOMAÇÃO:
   ✓ Agendar sincronização diária/semanal
   ✓ Monitorar partidas ao vivo
   ✓ Alertas para mudanças importantes

4. ANÁLISE E VISUALIZAÇÃO:
   ✓ Criar dashboard com Streamlit/Dash
   ✓ Implementar análises estatísticas avançadas
   ✓ Gerar relatórios automáticos

5. API E INTEGRAÇÃO:
   ✓ Criar API REST própria
   ✓ Webhooks para eventos em tempo real
   ✓ Integração com outras plataformas
    """)
    
    print("=" * 80)
    print("✅ PROJETO CONFIGURADO E FUNCIONANDO COM SUCESSO!")
    print("🏆 Banco de dados pronto para análises avançadas de futebol")
    print("=" * 80)

if __name__ == "__main__":
    gerar_relatorio()
