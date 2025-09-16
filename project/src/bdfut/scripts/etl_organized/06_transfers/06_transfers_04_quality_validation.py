#!/usr/bin/env python3
"""
Validação de qualidade: Transfers
TASK-ETL-023: Implementar Sistema de Transfers

Objetivo: Validar qualidade dos dados de transfers coletados
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

def validate_transfers_quality():
    """Validar qualidade dos transfers"""
    print("🔍 VALIDAÇÃO DE QUALIDADE: Transfers...")
    
    try:
        supabase = SupabaseClient()
        
        # Buscar todos os transfers
        result = supabase.client.table('transfers').select('*').execute()
        transfers = result.data
        
        if not transfers:
            print("⚠️ Nenhum transfer encontrado no banco")
            return False
        
        print(f"📊 Analisando {len(transfers)} transfers...")
        
        # Estatísticas de qualidade
        stats = {
            'total': len(transfers),
            'with_sportmonks_id': 0,
            'with_player_id': 0,
            'with_from_team': 0,
            'with_to_team': 0,
            'with_transfer_date': 0,
            'with_transfer_type': 0,
            'with_fee_info': 0,
            'valid_dates': 0,
            'duplicates': 0,
            'complete_records': 0
        }
        
        seen_ids = set()
        
        for transfer in transfers:
            # Campos obrigatórios
            if transfer.get('sportmonks_id'):
                stats['with_sportmonks_id'] += 1
                
                # Verificar duplicatas
                if transfer['sportmonks_id'] in seen_ids:
                    stats['duplicates'] += 1
                else:
                    seen_ids.add(transfer['sportmonks_id'])
            
            if transfer.get('player_id'):
                stats['with_player_id'] += 1
                
            if transfer.get('from_team_id'):
                stats['with_from_team'] += 1
                
            if transfer.get('to_team_id'):
                stats['with_to_team'] += 1
                
            if transfer.get('transfer_date'):
                stats['with_transfer_date'] += 1
                
                # Validar data
                try:
                    transfer_date = datetime.strptime(transfer['transfer_date'], '%Y-%m-%d').date()
                    if date(2000, 1, 1) <= transfer_date <= date.today():
                        stats['valid_dates'] += 1
                except:
                    pass
                    
            if transfer.get('transfer_type'):
                stats['with_transfer_type'] += 1
                
            if transfer.get('fee_amount') or transfer.get('fee_currency'):
                stats['with_fee_info'] += 1
            
            # Registro completo (critérios mínimos)
            if (transfer.get('sportmonks_id') and 
                transfer.get('player_id') and 
                (transfer.get('from_team_id') or transfer.get('to_team_id'))):
                stats['complete_records'] += 1
        
        # Calcular percentuais
        total = stats['total']
        print("\n📊 RELATÓRIO DE QUALIDADE:")
        print("=" * 50)
        print(f"Total de transfers: {total}")
        print(f"Com Sportmonks ID: {stats['with_sportmonks_id']} ({stats['with_sportmonks_id']/total*100:.1f}%)")
        print(f"Com Player ID: {stats['with_player_id']} ({stats['with_player_id']/total*100:.1f}%)")
        print(f"Com From Team: {stats['with_from_team']} ({stats['with_from_team']/total*100:.1f}%)")
        print(f"Com To Team: {stats['with_to_team']} ({stats['with_to_team']/total*100:.1f}%)")
        print(f"Com Data Transfer: {stats['with_transfer_date']} ({stats['with_transfer_date']/total*100:.1f}%)")
        print(f"Com Tipo Transfer: {stats['with_transfer_type']} ({stats['with_transfer_type']/total*100:.1f}%)")
        print(f"Com Info Taxa: {stats['with_fee_info']} ({stats['with_fee_info']/total*100:.1f}%)")
        print(f"Datas Válidas: {stats['valid_dates']} ({stats['valid_dates']/total*100:.1f}%)")
        print(f"Registros Completos: {stats['complete_records']} ({stats['complete_records']/total*100:.1f}%)")
        print(f"Duplicatas: {stats['duplicates']}")
        
        # Score de qualidade
        quality_score = (
            (stats['with_sportmonks_id'] * 0.2) +
            (stats['with_player_id'] * 0.2) +
            (stats['with_from_team'] * 0.1) +
            (stats['with_to_team'] * 0.1) +
            (stats['with_transfer_date'] * 0.15) +
            (stats['valid_dates'] * 0.15) +
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
            
        if stats['with_transfer_type'] < total * 0.5:
            print("  - Melhorar coleta de tipos de transferência")
            
        if stats['with_fee_info'] < total * 0.3:
            print("  - Investigar endpoints adicionais para valores de transferência")
            
        if stats['valid_dates'] < stats['with_transfer_date']:
            print("  - Validar e corrigir datas inválidas")
        
        # Considerado sucesso se score >= 60%
        success = quality_score >= 60.0
        
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
    success = validate_transfers_quality()
    if success:
        print("🎉 Validação de qualidade concluída com sucesso!")
    else:
        print("💥 Validação de qualidade falhou!")
