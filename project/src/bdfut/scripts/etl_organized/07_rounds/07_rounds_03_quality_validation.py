#!/usr/bin/env python3
"""
Validação de qualidade: Rounds
TASK-ETL-024: Implementar Sistema de Rounds

Objetivo: Validar qualidade dos dados de rounds coletados
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from bdfut.core.supabase_client import SupabaseClient
import logging
from datetime import datetime, date

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_rounds_quality():
    """Validar qualidade dos rounds"""
    print("🔍 VALIDAÇÃO DE QUALIDADE: Rounds...")
    
    try:
        supabase = SupabaseClient()
        
        # Buscar todos os rounds
        result = supabase.client.table('rounds').select('*').execute()
        rounds = result.data
        
        if not rounds:
            print("⚠️ Nenhum round encontrado no banco")
            return False
        
        print(f"📊 Analisando {len(rounds)} rounds...")
        
        # Estatísticas de qualidade
        stats = {
            'total': len(rounds),
            'with_sportmonks_id': 0,
            'with_name': 0,
            'with_league_id': 0,
            'with_season_id': 0,
            'with_stage_id': 0,
            'with_starting_date': 0,
            'with_ending_date': 0,
            'valid_date_ranges': 0,
            'finished_rounds': 0,
            'current_rounds': 0,
            'duplicates': 0,
            'complete_records': 0
        }
        
        seen_ids = set()
        
        for round_item in rounds:
            # Campos obrigatórios
            if round_item.get('sportmonks_id'):
                stats['with_sportmonks_id'] += 1
                
                # Verificar duplicatas
                if round_item['sportmonks_id'] in seen_ids:
                    stats['duplicates'] += 1
                else:
                    seen_ids.add(round_item['sportmonks_id'])
            
            if round_item.get('name'):
                stats['with_name'] += 1
                
            if round_item.get('league_id'):
                stats['with_league_id'] += 1
                
            if round_item.get('season_id'):
                stats['with_season_id'] += 1
                
            if round_item.get('stage_id'):
                stats['with_stage_id'] += 1
                
            if round_item.get('starting_at'):
                stats['with_starting_date'] += 1
                
            if round_item.get('ending_at'):
                stats['with_ending_date'] += 1
                
            # Validar intervalo de datas
            if round_item.get('starting_at') and round_item.get('ending_at'):
                try:
                    start_date = datetime.strptime(round_item['starting_at'], '%Y-%m-%d').date()
                    end_date = datetime.strptime(round_item['ending_at'], '%Y-%m-%d').date()
                    if start_date <= end_date:
                        stats['valid_date_ranges'] += 1
                except:
                    pass
                    
            if round_item.get('finished'):
                stats['finished_rounds'] += 1
                
            if round_item.get('is_current'):
                stats['current_rounds'] += 1
            
            # Registro completo (critérios mínimos)
            if (round_item.get('sportmonks_id') and 
                round_item.get('name') and 
                round_item.get('season_id')):
                stats['complete_records'] += 1
        
        # Calcular percentuais
        total = stats['total']
        print("\n📊 RELATÓRIO DE QUALIDADE:")
        print("=" * 50)
        print(f"Total de rounds: {total}")
        print(f"Com Sportmonks ID: {stats['with_sportmonks_id']} ({stats['with_sportmonks_id']/total*100:.1f}%)")
        print(f"Com Nome: {stats['with_name']} ({stats['with_name']/total*100:.1f}%)")
        print(f"Com League ID: {stats['with_league_id']} ({stats['with_league_id']/total*100:.1f}%)")
        print(f"Com Season ID: {stats['with_season_id']} ({stats['with_season_id']/total*100:.1f}%)")
        print(f"Com Stage ID: {stats['with_stage_id']} ({stats['with_stage_id']/total*100:.1f}%)")
        print(f"Com Data Início: {stats['with_starting_date']} ({stats['with_starting_date']/total*100:.1f}%)")
        print(f"Com Data Fim: {stats['with_ending_date']} ({stats['with_ending_date']/total*100:.1f}%)")
        print(f"Intervalos Válidos: {stats['valid_date_ranges']} ({stats['valid_date_ranges']/total*100:.1f}%)")
        print(f"Rounds Finalizados: {stats['finished_rounds']} ({stats['finished_rounds']/total*100:.1f}%)")
        print(f"Rounds Atuais: {stats['current_rounds']} ({stats['current_rounds']/total*100:.1f}%)")
        print(f"Registros Completos: {stats['complete_records']} ({stats['complete_records']/total*100:.1f}%)")
        print(f"Duplicatas: {stats['duplicates']}")
        
        # Score de qualidade
        quality_score = (
            (stats['with_sportmonks_id'] * 0.2) +
            (stats['with_name'] * 0.15) +
            (stats['with_season_id'] * 0.15) +
            (stats['with_league_id'] * 0.1) +
            (stats['with_starting_date'] * 0.1) +
            (stats['with_ending_date'] * 0.1) +
            (stats['valid_date_ranges'] * 0.1) +
            (stats['complete_records'] * 0.1)
        ) / total * 100
        
        print(f"\n🎯 SCORE DE QUALIDADE: {quality_score:.1f}%")
        
        # Classificação
        if quality_score >= 80:
            classification = "🟢 EXCELENTE"
        elif quality_score >= 60:
            classification = "🟡 BOA"
        elif quality_score >= 40:
            classification = "🟠 REGULAR"
        else:
            classification = "🔴 RUIM"
            
        print(f"📈 CLASSIFICAÇÃO: {classification}")
        
        # Recomendações
        print("\n💡 RECOMENDAÇÕES:")
        if stats['duplicates'] > 0:
            print(f"  - Remover {stats['duplicates']} duplicatas")
            
        if stats['with_stage_id'] < total * 0.8:
            print("  - Investigar rounds sem stage_id")
            
        if stats['valid_date_ranges'] < stats['with_starting_date']:
            print("  - Validar e corrigir intervalos de datas inválidos")
        
        if stats['current_rounds'] == 0:
            print("  - Verificar se há rounds atuais no sistema")
        
        # Considerado sucesso se score >= 70% (rounds são estruturais, precisam de qualidade alta)
        success = quality_score >= 70.0
        
        if success:
            print("\n✅ Validação de qualidade APROVADA!")
        else:
            print("\n❌ Validação de qualidade REPROVADA!")
            
        return success
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = validate_rounds_quality()
    if success:
        print("🎉 Validação de qualidade concluída com sucesso!")
    else:
        print("💥 Validação de qualidade falhou!")
