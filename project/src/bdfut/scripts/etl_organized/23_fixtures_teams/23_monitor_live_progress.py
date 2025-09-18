#!/usr/bin/env python3
"""
Script de monitoramento em tempo real do enriquecimento de fixtures
Mostra progresso contínuo com atualizações a cada 30 segundos
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
logging.basicConfig(level=logging.WARNING)  # Reduzir logs para não poluir o monitoramento

class LiveProgressMonitor:
    """Monitor de progresso em tempo real"""
    
    def __init__(self):
        self.supabase = SupabaseClient()
        self.start_time = datetime.now()
        self.last_count = 0
        
    def get_current_progress(self):
        """Obter progresso atual"""
        try:
            # Total de fixtures
            total_response = self.supabase.client.from_('fixtures').select('fixture_id', count='exact').execute()
            total_fixtures = total_response.count if total_response.count else 0

            # Fixtures com ambos preenchidos
            both_response = self.supabase.client.from_('fixtures').select('fixture_id', count='exact').not_.is_('home_team_id', 'null').not_.is_('away_team_id', 'null').execute()
            both_filled = both_response.count if both_response.count else 0
            
            return total_fixtures, both_filled
            
        except Exception as e:
            print(f"❌ Erro ao obter progresso: {e}")
            return 0, 0
    
    def calculate_rate(self, current_count):
        """Calcular taxa de processamento"""
        elapsed_time = datetime.now() - self.start_time
        elapsed_minutes = elapsed_time.total_seconds() / 60
        
        if elapsed_minutes > 0:
            rate = current_count / elapsed_minutes
            return rate, elapsed_minutes
        return 0, 0
    
    def print_progress(self, total_fixtures, current_count, rate, elapsed_minutes):
        """Imprimir progresso formatado"""
        # Limpar tela (funciona na maioria dos terminais)
        print("\033[2J\033[H", end="")
        
        progress_pct = (current_count / total_fixtures) * 100 if total_fixtures > 0 else 0
        remaining = total_fixtures - current_count
        
        # Calcular ETA
        eta_minutes = remaining / rate if rate > 0 else 0
        eta_hours = eta_minutes / 60
        
        # Calcular taxa de processamento atual (últimos 30 segundos)
        if hasattr(self, 'last_count') and elapsed_minutes > 0:
            recent_rate = (current_count - self.last_count) * 2  # *2 porque atualiza a cada 30s
        else:
            recent_rate = rate
        
        print("🚀 MONITORAMENTO EM TEMPO REAL - ENRIQUECIMENTO DE FIXTURES")
        print("=" * 70)
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Tempo decorrido: {elapsed_minutes:.1f} min")
        print("")
        print(f"📊 PROGRESSO GERAL:")
        print(f"   📈 Total de fixtures: {total_fixtures:,}")
        print(f"   ✅ Processadas: {current_count:,} ({progress_pct:.1f}%)")
        print(f"   ⏳ Restam: {remaining:,}")
        print("")
        print(f"🚀 PERFORMANCE:")
        print(f"   📊 Taxa média: {rate:.1f} fixtures/minuto")
        print(f"   ⚡ Taxa atual: {recent_rate:.1f} fixtures/minuto")
        print(f"   🕐 ETA: {eta_minutes:.0f} minutos ({eta_hours:.1f} horas)")
        print("")
        
        # Barra de progresso visual
        bar_length = 50
        filled_length = int(bar_length * progress_pct / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"📊 [{bar}] {progress_pct:.1f}%")
        print("")
        print("💡 Pressione Ctrl+C para sair")
        
        self.last_count = current_count
    
    def run_monitoring(self, update_interval=30):
        """Executar monitoramento contínuo"""
        print("🚀 Iniciando monitoramento em tempo real...")
        print("💡 Atualizações a cada 30 segundos")
        print("💡 Pressione Ctrl+C para sair")
        time.sleep(2)
        
        try:
            while True:
                total_fixtures, current_count = self.get_current_progress()
                rate, elapsed_minutes = self.calculate_rate(current_count)
                
                self.print_progress(total_fixtures, current_count, rate, elapsed_minutes)
                
                # Verificar se terminou
                if current_count >= total_fixtures:
                    print("\n🎉 ENRIQUECIMENTO CONCLUÍDO!")
                    break
                
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoramento interrompido pelo usuário")
        except Exception as e:
            print(f"\n❌ Erro no monitoramento: {e}")

def main():
    """Função principal"""
    monitor = LiveProgressMonitor()
    monitor.run_monitoring()

if __name__ == "__main__":
    main()
