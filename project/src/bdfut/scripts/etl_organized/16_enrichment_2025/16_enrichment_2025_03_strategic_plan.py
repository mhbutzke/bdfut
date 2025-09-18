#!/usr/bin/env python3
"""
Script de planejamento estratégico para enriquecimento de eventos
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from bdfut.core.supabase_client import SupabaseClient

class StrategicPlan:
    def __init__(self):
        self.supabase = SupabaseClient()
        
    def analyze_current_status(self):
        """Analisar status atual do enriquecimento"""
        print("🔍 ANÁLISE ESTRATÉGICA DO ENRIQUECIMENTO DE EVENTOS")
        print("=" * 60)
        
        # Contar fixtures por ano
        total_fixtures = 0
        fixtures_with_events = 0
        
        for year in [2023, 2024, 2025]:
            # Fixtures totais do ano
            response = self.supabase.client.table('fixtures').select(
                'fixture_id', count='exact'
            ).gte('match_date', f'{year}-01-01').lt('match_date', f'{year+1}-01-01').in_(
                'status', ['FT', 'FT_PEN', 'AET']
            ).execute()
            
            year_fixtures = response.count
            
            # Fixtures com eventos
            response = self.supabase.client.table('match_events').select(
                'fixture_id'
            ).execute()
            
            all_fixtures_with_events = set([event['fixture_id'] for event in response.data])
            
            # Contar fixtures do ano que têm eventos
            year_fixtures_with_events = 0
            for fixture_id in all_fixtures_with_events:
                # Verificar se a fixture pertence ao ano
                fixture_response = self.supabase.client.table('fixtures').select(
                    'match_date'
                ).eq('fixture_id', fixture_id).execute()
                
                if fixture_response.data:
                    match_date = fixture_response.data[0]['match_date']
                    if f'{year}-01-01' <= match_date < f'{year+1}-01-01':
                        year_fixtures_with_events += 1
            
            coverage = (year_fixtures_with_events / year_fixtures * 100) if year_fixtures > 0 else 0
            
            print(f"📅 {year}:")
            print(f"   Fixtures: {year_fixtures:,}")
            print(f"   Com eventos: {year_fixtures_with_events:,}")
            print(f"   Cobertura: {coverage:.1f}%")
            print()
            
            total_fixtures += year_fixtures
            fixtures_with_events += year_fixtures_with_events
        
        # Total de eventos
        response = self.supabase.client.table('match_events').select('id', count='exact').execute()
        total_events = response.count
        
        print(f"📊 RESUMO GERAL:")
        print(f"   Total de fixtures: {total_fixtures:,}")
        print(f"   Fixtures com eventos: {fixtures_with_events:,}")
        print(f"   Total de eventos: {total_events:,}")
        print(f"   Cobertura geral: {(fixtures_with_events/total_fixtures*100):.1f}%")
        print()
        
        return {
            'total_fixtures': total_fixtures,
            'fixtures_with_events': fixtures_with_events,
            'total_events': total_events,
            'coverage': fixtures_with_events/total_fixtures*100
        }
        
    def estimate_completion_time(self, fixtures_remaining: int, rate_per_minute: float = 30):
        """Estimar tempo de conclusão"""
        print("⏱️ ESTIMATIVAS DE TEMPO:")
        print("=" * 30)
        
        if rate_per_minute <= 0:
            print("❌ Taxa de processamento inválida")
            return
            
        # Calcular tempo em diferentes unidades
        minutes_remaining = fixtures_remaining / rate_per_minute
        hours_remaining = minutes_remaining / 60
        days_remaining = hours_remaining / 24
        
        print(f"📈 Taxa estimada: {rate_per_minute} fixtures/minuto")
        print(f"⏰ Tempo restante:")
        print(f"   {minutes_remaining:.0f} minutos")
        print(f"   {hours_remaining:.1f} horas")
        print(f"   {days_remaining:.1f} dias")
        
        if days_remaining > 1:
            print(f"\\n💡 RECOMENDAÇÃO: Processar em lotes de 8-12 horas por dia")
            print(f"   Lotes diários: {int(hours_remaining/8)} dias")
        
        return {
            'minutes': minutes_remaining,
            'hours': hours_remaining,
            'days': days_remaining
        }
        
    def generate_execution_plan(self):
        """Gerar plano de execução recomendado"""
        print("\\n📋 PLANO DE EXECUÇÃO RECOMENDADO:")
        print("=" * 40)
        
        print("1️⃣ FASE 1 - VALIDAÇÃO (500 fixtures)")
        print("   - Executar script otimizado com limite de 500")
        print("   - Validar qualidade dos dados")
        print("   - Ajustar rate limiting se necessário")
        print("   - Tempo estimado: 15-20 minutos")
        print()
        
        print("2️⃣ FASE 2 - ENRIQUECIMENTO POR ANO")
        print("   - 2025: ~3.6k fixtures (prioridade alta)")
        print("   - 2024: ~4.8k fixtures")
        print("   - 2023: ~3.3k fixtures")
        print("   - Tempo total estimado: 6-8 horas")
        print()
        
        print("3️⃣ FASE 3 - MONITORAMENTO")
        print("   - Verificar cobertura por ano")
        print("   - Identificar fixtures sem eventos")
        print("   - Gerar relatório final")
        print()
        
        print("🔧 CONFIGURAÇÕES RECOMENDADAS:")
        print("   - Batch size: 100 fixtures")
        print("   - Rate limit: 0.5s entre requests")
        print("   - Log de progresso: a cada 50 fixtures")
        print("   - Verificação de completude: 80% dos eventos")
        
    def show_next_steps(self):
        """Mostrar próximos passos"""
        print("\\n🚀 PRÓXIMOS PASSOS:")
        print("=" * 20)
        print("1. Executar: python 16_enrichment_2025_02_events_optimized.py")
        print("2. Monitorar logs de progresso")
        print("3. Verificar qualidade dos dados coletados")
        print("4. Ajustar configurações se necessário")
        print("5. Executar enriquecimento completo")
        print()
        print("💡 DICA: Execute em background com nohup para sessões longas:")
        print("   nohup python 16_enrichment_2025_02_events_optimized.py > enrichment.log 2>&1 &")

if __name__ == "__main__":
    planner = StrategicPlan()
    
    # Análise atual
    status = planner.analyze_current_status()
    
    # Estimativas
    fixtures_remaining = status['total_fixtures'] - status['fixtures_with_events']
    planner.estimate_completion_time(fixtures_remaining)
    
    # Plano de execução
    planner.generate_execution_plan()
    
    # Próximos passos
    planner.show_next_steps()
