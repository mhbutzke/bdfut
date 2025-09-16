#!/usr/bin/env python3
"""
Validação de qualidade: Stages
TASK-ETL-025: Implementar Sistema de Stages Expandido

Objetivo: Validar qualidade dos dados de stages coletados
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

def validate_stages_quality():
    """Validar qualidade dos stages"""
    print("🔍 VALIDAÇÃO DE QUALIDADE: Stages...")
    
    try:
        supabase = SupabaseClient()
        
        # Buscar todos os stages
        result = supabase.client.table('stages').select('*').execute()
        stages = result.data
        
        if not stages:
            print("⚠️ Nenhum stage encontrado no banco")
            return False
        
        print(f"📊 Analisando {len(stages)} stages...")
        
        # Estatísticas de qualidade
        stats = {
            'total': len(stages),
            'with_sportmonks_id': 0,
            'with_name': 0,
            'with_league_id': 0,
            'with_season_id': 0,
            'with_type_id': 0,
            'with_sort_order': 0,
            'with_starting_date': 0,
            'with_ending_date': 0,
            'valid_date_ranges': 0,
            'finished_stages': 0,
            'current_stages': 0,
            'with_short_code': 0,
            'duplicates': 0,
            'complete_records': 0
        }
        
        seen_ids = set()
        type_distribution = {}
        league_distribution = {}
        
        for stage in stages:
            # Campos obrigatórios
            if stage.get('sportmonks_id'):
                stats['with_sportmonks_id'] += 1
                
                # Verificar duplicatas
                if stage['sportmonks_id'] in seen_ids:
                    stats['duplicates'] += 1
                else:
                    seen_ids.add(stage['sportmonks_id'])
            
            if stage.get('name'):
                stats['with_name'] += 1
                
            if stage.get('league_id'):
                stats['with_league_id'] += 1
                league_id = stage['league_id']
                league_distribution[league_id] = league_distribution.get(league_id, 0) + 1
                
            if stage.get('season_id'):
                stats['with_season_id'] += 1
                
            if stage.get('type_id'):
                stats['with_type_id'] += 1
                type_id = stage['type_id']
                type_distribution[type_id] = type_distribution.get(type_id, 0) + 1
                
            if stage.get('sort_order') is not None:
                stats['with_sort_order'] += 1
                
            if stage.get('short_code'):
                stats['with_short_code'] += 1
                
            if stage.get('starting_at'):
                stats['with_starting_date'] += 1
                
            if stage.get('ending_at'):
                stats['with_ending_date'] += 1
                
            # Validar intervalo de datas (considerando que podem ser timestamp)
            if stage.get('starting_at') and stage.get('ending_at'):
                try:
                    start_str = stage['starting_at']
                    end_str = stage['ending_at']
                    
                    # Tentar diferentes formatos
                    if 'T' in start_str:  # ISO format
                        start_date = datetime.fromisoformat(start_str.replace('Z', '+00:00')).date()
                        end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00')).date()
                    else:  # Date format
                        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
                    
                    if start_date <= end_date:
                        stats['valid_date_ranges'] += 1
                except:
                    pass
                    
            if stage.get('finished'):
                stats['finished_stages'] += 1
                
            if stage.get('is_current'):
                stats['current_stages'] += 1
            
            # Registro completo (critérios mínimos)
            if (stage.get('sportmonks_id') and 
                stage.get('name') and 
                stage.get('season_id') and
                stage.get('type_id')):
                stats['complete_records'] += 1
        
        # Calcular percentuais
        total = stats['total']
        print("\n📊 RELATÓRIO DE QUALIDADE:")
        print("=" * 50)
        print(f"Total de stages: {total}")
        print(f"Com Sportmonks ID: {stats['with_sportmonks_id']} ({stats['with_sportmonks_id']/total*100:.1f}%)")
        print(f"Com Nome: {stats['with_name']} ({stats['with_name']/total*100:.1f}%)")
        print(f"Com League ID: {stats['with_league_id']} ({stats['with_league_id']/total*100:.1f}%)")
        print(f"Com Season ID: {stats['with_season_id']} ({stats['with_season_id']/total*100:.1f}%)")
        print(f"Com Type ID: {stats['with_type_id']} ({stats['with_type_id']/total*100:.1f}%)")
        print(f"Com Sort Order: {stats['with_sort_order']} ({stats['with_sort_order']/total*100:.1f}%)")
        print(f"Com Short Code: {stats['with_short_code']} ({stats['with_short_code']/total*100:.1f}%)")
        print(f"Com Data Início: {stats['with_starting_date']} ({stats['with_starting_date']/total*100:.1f}%)")
        print(f"Com Data Fim: {stats['with_ending_date']} ({stats['with_ending_date']/total*100:.1f}%)")
        print(f"Intervalos Válidos: {stats['valid_date_ranges']} ({stats['valid_date_ranges']/total*100:.1f}%)")
        print(f"Stages Finalizados: {stats['finished_stages']} ({stats['finished_stages']/total*100:.1f}%)")
        print(f"Stages Atuais: {stats['current_stages']} ({stats['current_stages']/total*100:.1f}%)")
        print(f"Registros Completos: {stats['complete_records']} ({stats['complete_records']/total*100:.1f}%)")
        print(f"Duplicatas: {stats['duplicates']}")
        
        # Distribuição de tipos
        if type_distribution:
            print(f"\n📊 DISTRIBUIÇÃO DE TIPOS:")
            sorted_types = sorted(type_distribution.items(), key=lambda x: x[1], reverse=True)
            for type_id, count in sorted_types[:5]:
                print(f"  Type {type_id}: {count} stages ({count/total*100:.1f}%)")
        
        # Distribuição de ligas
        if league_distribution:
            print(f"\n📊 DISTRIBUIÇÃO DE LIGAS:")
            sorted_leagues = sorted(league_distribution.items(), key=lambda x: x[1], reverse=True)
            for league_id, count in sorted_leagues[:5]:
                print(f"  League {league_id}: {count} stages ({count/total*100:.1f}%)")
        
        # Score de qualidade
        quality_score = (
            (stats['with_sportmonks_id'] * 0.2) +
            (stats['with_name'] * 0.15) +
            (stats['with_season_id'] * 0.15) +
            (stats['with_type_id'] * 0.15) +
            (stats['with_league_id'] * 0.1) +
            (stats['with_sort_order'] * 0.05) +
            (stats['with_starting_date'] * 0.1) +
            (stats['with_ending_date'] * 0.05) +
            (stats['complete_records'] * 0.05)
        ) / total * 100
        
        print(f"\n🎯 SCORE DE QUALIDADE: {quality_score:.1f}%")
        
        # Classificação
        if quality_score >= 85:
            classification = "🟢 EXCELENTE"
        elif quality_score >= 70:
            classification = "🟡 BOA"
        elif quality_score >= 50:
            classification = "🟠 REGULAR"
        else:
            classification = "🔴 RUIM"
            
        print(f"📈 CLASSIFICAÇÃO: {classification}")
        
        # Recomendações
        print("\n💡 RECOMENDAÇÕES:")
        if stats['duplicates'] > 0:
            print(f"  - Remover {stats['duplicates']} duplicatas")
            
        if stats['with_short_code'] < total * 0.5:
            print("  - Investigar stages sem short_code")
            
        if stats['valid_date_ranges'] < stats['with_starting_date'] * 0.9:
            print("  - Validar e corrigir intervalos de datas inválidos")
        
        if stats['current_stages'] == 0:
            print("  - Verificar se há stages atuais no sistema")
        
        if len(type_distribution) < 3:
            print("  - Expandir coleta para mais tipos de stages")
        
        # Considerado sucesso se score >= 75% (stages são estruturais importantes)
        success = quality_score >= 75.0
        
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
    success = validate_stages_quality()
    if success:
        print("🎉 Validação de qualidade concluída com sucesso!")
    else:
        print("💥 Validação de qualidade falhou!")
