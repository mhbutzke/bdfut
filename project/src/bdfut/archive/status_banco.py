#!/usr/bin/env python3
"""
Relatório detalhado do status atual do banco
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client
from config.config import Config
from datetime import datetime

# Configuração das ligas
LIGAS_CONFIG = {
    648: {'nome': 'Brasileirão Série A', 'pais': 'Brasil', 'prioridade': 1},
    651: {'nome': 'Brasileirão Série B', 'pais': 'Brasil', 'prioridade': 1},
    654: {'nome': 'Copa do Brasil', 'pais': 'Brasil', 'prioridade': 1},
    636: {'nome': 'Primera División', 'pais': 'Argentina', 'prioridade': 2},
    1122: {'nome': 'Copa Libertadores', 'pais': 'CONMEBOL', 'prioridade': 1},
    1116: {'nome': 'Copa Sudamericana', 'pais': 'CONMEBOL', 'prioridade': 2},
    2: {'nome': 'Champions League', 'pais': 'UEFA', 'prioridade': 1},
    5: {'nome': 'Europa League', 'pais': 'UEFA', 'prioridade': 2},
    8: {'nome': 'Premier League', 'pais': 'Inglaterra', 'prioridade': 1},
    9: {'nome': 'Championship', 'pais': 'Inglaterra', 'prioridade': 3},
    564: {'nome': 'LaLiga', 'pais': 'Espanha', 'prioridade': 1},
    462: {'nome': 'Liga Portugal', 'pais': 'Portugal', 'prioridade': 2},
    301: {'nome': 'Ligue 1', 'pais': 'França', 'prioridade': 2},
    82: {'nome': 'Bundesliga', 'pais': 'Alemanha', 'prioridade': 1},
    743: {'nome': 'Liga MX', 'pais': 'México', 'prioridade': 3},
    779: {'nome': 'MLS', 'pais': 'EUA', 'prioridade': 3}
}

def analisar_status():
    """Analisa status detalhado do banco"""
    
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("=" * 80)
    print("📊 STATUS ATUAL DO BANCO DE DADOS")
    print("=" * 80)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y às %H:%M')}\n")
    
    # ============================================
    # 1. TOTAIS GERAIS
    # ============================================
    print("📈 TOTAIS GERAIS:")
    print("-" * 40)
    
    try:
        fixtures = supabase.table('fixtures').select('*', count='exact').execute()
        events = supabase.table('match_events').select('*', count='exact').execute()
        stats = supabase.table('match_statistics').select('*', count='exact').execute()
        lineups = supabase.table('match_lineups').select('*', count='exact').execute()
        
        print(f"   • Fixtures: {fixtures.count:,}")
        print(f"   • Eventos: {events.count:,}")
        print(f"   • Estatísticas: {stats.count:,}")
        print(f"   • Escalações: {lineups.count:,}")
    except:
        pass
    
    # ============================================
    # 2. ANÁLISE POR LIGA
    # ============================================
    print("\n📊 STATUS POR LIGA:")
    print("-" * 40)
    
    try:
        # Buscar todas as fixtures
        fixtures_data = supabase.table('fixtures').select('league_id, season_id, sportmonks_id').execute()
        
        # Buscar eventos
        events_data = supabase.table('match_events').select('fixture_id').execute()
        fixtures_with_events = set(e['fixture_id'] for e in events_data.data if e.get('fixture_id'))
        
        # Analisar por liga
        liga_stats = {}
        
        for f in fixtures_data.data:
            league_id = f.get('league_id')
            if league_id not in liga_stats:
                liga_stats[league_id] = {
                    'fixtures': 0,
                    'seasons': set(),
                    'with_events': 0
                }
            
            liga_stats[league_id]['fixtures'] += 1
            liga_stats[league_id]['seasons'].add(f.get('season_id'))
            
            if f.get('sportmonks_id') in fixtures_with_events:
                liga_stats[league_id]['with_events'] += 1
        
        # Ordenar por prioridade e mostrar
        ligas_ordenadas = sorted(
            [(lid, stats) for lid, stats in liga_stats.items() if lid in LIGAS_CONFIG],
            key=lambda x: (LIGAS_CONFIG[x[0]]['prioridade'], -x[1]['fixtures'])
        )
        
        status_summary = {
            'completas': [],  # Com eventos
            'basicas': [],    # Sem eventos
            'faltando': []    # Não coletadas
        }
        
        for league_id, stats in ligas_ordenadas:
            info = LIGAS_CONFIG[league_id]
            pct_events = (stats['with_events'] / stats['fixtures'] * 100) if stats['fixtures'] > 0 else 0
            
            status = "✅" if pct_events > 80 else "⚠️" if pct_events > 0 else "❌"
            
            print(f"\n{status} {info['nome']} ({info['pais']})")
            print(f"   • Fixtures: {stats['fixtures']}")
            print(f"   • Temporadas: {len(stats['seasons'])}")
            print(f"   • Com eventos: {stats['with_events']} ({pct_events:.1f}%)")
            
            if pct_events > 80:
                status_summary['completas'].append(info['nome'])
            elif stats['fixtures'] > 0:
                status_summary['basicas'].append(info['nome'])
        
        # Ligas faltando
        ligas_no_banco = set(liga_stats.keys())
        ligas_faltando = set(LIGAS_CONFIG.keys()) - ligas_no_banco
        
        for lid in ligas_faltando:
            status_summary['faltando'].append(LIGAS_CONFIG[lid]['nome'])
        
        # ============================================
        # 3. RESUMO E RECOMENDAÇÕES
        # ============================================
        print("\n" + "=" * 80)
        print("📋 RESUMO DO STATUS:")
        print("-" * 40)
        
        print(f"\n✅ LIGAS COMPLETAS (com eventos): {len(status_summary['completas'])}")
        for liga in status_summary['completas'][:5]:
            print(f"   • {liga}")
        
        print(f"\n⚠️  LIGAS BÁSICAS (sem eventos): {len(status_summary['basicas'])}")
        for liga in status_summary['basicas'][:5]:
            print(f"   • {liga}")
        
        print(f"\n❌ LIGAS FALTANDO: {len(status_summary['faltando'])}")
        for liga in status_summary['faltando'][:5]:
            print(f"   • {liga}")
        
        print("\n" + "=" * 80)
        print("🎯 RECOMENDAÇÃO DE PRÓXIMOS PASSOS:")
        print("-" * 40)
        
        if status_summary['faltando']:
            print(f"\n1️⃣ COLETAR LIGAS FALTANTES ({len(status_summary['faltando'])} ligas)")
            print("   Prioridade Alta:")
            for lid in ligas_faltando:
                if LIGAS_CONFIG[lid]['prioridade'] == 1:
                    print(f"   • {LIGAS_CONFIG[lid]['nome']}")
        
        if status_summary['basicas']:
            print(f"\n2️⃣ ENRIQUECER LIGAS BÁSICAS ({len(status_summary['basicas'])} ligas)")
            print("   Adicionar eventos, estatísticas e escalações")
        
        print("\n3️⃣ MANTER ATUALIZAÇÕES")
        print("   Criar rotina de sincronização diária/semanal")
        
        print("\n" + "=" * 80)
        
        return {
            'completas': len(status_summary['completas']),
            'basicas': len(status_summary['basicas']),
            'faltando': len(status_summary['faltando'])
        }
        
    except Exception as e:
        print(f"Erro na análise: {e}")
        return None

if __name__ == "__main__":
    resultado = analisar_status()
    
    if resultado:
        print(f"\n🚀 AÇÃO RECOMENDADA:")
        if resultado['faltando'] > 0:
            print(f"   → Execute: python3 coletar_ligas_faltantes.py")
        elif resultado['basicas'] > 0:
            print(f"   → Execute: python3 enriquecer_ligas_basicas.py")
        else:
            print(f"   → Banco completo! Configure sincronização automática.")
