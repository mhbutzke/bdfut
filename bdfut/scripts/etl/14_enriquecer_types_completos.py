#!/usr/bin/env python3
"""
Script para enriquecer a tabela types com dados completos conhecidos
Baseado na documentação da Sportmonks API
"""

import os
import sys
import logging
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from supabase import create_client
from config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def enrich_types_with_complete_data():
    """Enriquecer tabela types com dados completos conhecidos"""
    
    logger.info("🚀 Enriquecendo tabela types com dados completos conhecidos...")
    
    # Inicializar cliente
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente: {e}")
        return
    
    # Dados completos de types baseados na documentação Sportmonks
    complete_types_data = [
        # Eventos de Gol
        {'sportmonks_id': 14, 'name': 'Goal', 'developer_name': 'goal'},
        {'sportmonks_id': 15, 'name': 'Penalty Goal', 'developer_name': 'penalty_goal'},
        {'sportmonks_id': 16, 'name': 'Penalty Missed', 'developer_name': 'penalty_missed'},
        {'sportmonks_id': 17, 'name': 'Own Goal', 'developer_name': 'own_goal'},
        
        # Cartões
        {'sportmonks_id': 19, 'name': 'Yellow Card', 'developer_name': 'yellow_card'},
        {'sportmonks_id': 20, 'name': 'Red Card', 'developer_name': 'red_card'},
        {'sportmonks_id': 21, 'name': 'Second Yellow Card', 'developer_name': 'second_yellow_card'},
        
        # Substituições
        {'sportmonks_id': 18, 'name': 'Substitution', 'developer_name': 'substitution'},
        {'sportmonks_id': 83, 'name': 'Substitution In', 'developer_name': 'substitution_in'},
        {'sportmonks_id': 84, 'name': 'Substitution Out', 'developer_name': 'substitution_out'},
        
        # Faltas e Infrações
        {'sportmonks_id': 22, 'name': 'Foul', 'developer_name': 'foul'},
        {'sportmonks_id': 23, 'name': 'Offside', 'developer_name': 'offside'},
        {'sportmonks_id': 24, 'name': 'Handball', 'developer_name': 'handball'},
        {'sportmonks_id': 25, 'name': 'Dangerous Play', 'developer_name': 'dangerous_play'},
        
        # Cobranças
        {'sportmonks_id': 26, 'name': 'Corner Kick', 'developer_name': 'corner_kick'},
        {'sportmonks_id': 27, 'name': 'Free Kick', 'developer_name': 'free_kick'},
        {'sportmonks_id': 28, 'name': 'Throw In', 'developer_name': 'throw_in'},
        {'sportmonks_id': 29, 'name': 'Goal Kick', 'developer_name': 'goal_kick'},
        {'sportmonks_id': 30, 'name': 'Kick Off', 'developer_name': 'kick_off'},
        
        # Defesas
        {'sportmonks_id': 31, 'name': 'Save', 'developer_name': 'save'},
        {'sportmonks_id': 32, 'name': 'Block', 'developer_name': 'block'},
        {'sportmonks_id': 33, 'name': 'Interception', 'developer_name': 'interception'},
        {'sportmonks_id': 34, 'name': 'Clearance', 'developer_name': 'clearance'},
        
        # Ataques
        {'sportmonks_id': 35, 'name': 'Shot', 'developer_name': 'shot'},
        {'sportmonks_id': 36, 'name': 'Shot On Target', 'developer_name': 'shot_on_target'},
        {'sportmonks_id': 37, 'name': 'Shot Off Target', 'developer_name': 'shot_off_target'},
        {'sportmonks_id': 38, 'name': 'Shot Blocked', 'developer_name': 'shot_blocked'},
        {'sportmonks_id': 39, 'name': 'Shot Inside Box', 'developer_name': 'shot_inside_box'},
        {'sportmonks_id': 40, 'name': 'Shot Outside Box', 'developer_name': 'shot_outside_box'},
        
        # Passes
        {'sportmonks_id': 41, 'name': 'Pass', 'developer_name': 'pass'},
        {'sportmonks_id': 42, 'name': 'Accurate Pass', 'developer_name': 'accurate_pass'},
        {'sportmonks_id': 43, 'name': 'Key Pass', 'developer_name': 'key_pass'},
        {'sportmonks_id': 44, 'name': 'Long Pass', 'developer_name': 'long_pass'},
        {'sportmonks_id': 45, 'name': 'Short Pass', 'developer_name': 'short_pass'},
        {'sportmonks_id': 46, 'name': 'Cross', 'developer_name': 'cross'},
        {'sportmonks_id': 47, 'name': 'Accurate Cross', 'developer_name': 'accurate_cross'},
        
        # Assistências
        {'sportmonks_id': 48, 'name': 'Assist', 'developer_name': 'assist'},
        {'sportmonks_id': 49, 'name': 'Big Chance Created', 'developer_name': 'big_chance_created'},
        {'sportmonks_id': 50, 'name': 'Big Chance Missed', 'developer_name': 'big_chance_missed'},
        
        # Dribles
        {'sportmonks_id': 51, 'name': 'Dribble', 'developer_name': 'dribble'},
        {'sportmonks_id': 52, 'name': 'Successful Dribble', 'developer_name': 'successful_dribble'},
        {'sportmonks_id': 53, 'name': 'Unsuccessful Dribble', 'developer_name': 'unsuccessful_dribble'},
        
        # Duelos
        {'sportmonks_id': 54, 'name': 'Duel', 'developer_name': 'duel'},
        {'sportmonks_id': 55, 'name': 'Duel Won', 'developer_name': 'duel_won'},
        {'sportmonks_id': 56, 'name': 'Duel Lost', 'developer_name': 'duel_lost'},
        {'sportmonks_id': 57, 'name': 'Aerial Duel', 'developer_name': 'aerial_duel'},
        {'sportmonks_id': 58, 'name': 'Aerial Duel Won', 'developer_name': 'aerial_duel_won'},
        {'sportmonks_id': 59, 'name': 'Aerial Duel Lost', 'developer_name': 'aerial_duel_lost'},
        
        # Tackles
        {'sportmonks_id': 60, 'name': 'Tackle', 'developer_name': 'tackle'},
        {'sportmonks_id': 61, 'name': 'Successful Tackle', 'developer_name': 'successful_tackle'},
        {'sportmonks_id': 62, 'name': 'Unsuccessful Tackle', 'developer_name': 'unsuccessful_tackle'},
        
        # Posse de Bola
        {'sportmonks_id': 63, 'name': 'Possession', 'developer_name': 'possession'},
        {'sportmonks_id': 64, 'name': 'Ball Recovery', 'developer_name': 'ball_recovery'},
        {'sportmonks_id': 65, 'name': 'Ball Loss', 'developer_name': 'ball_loss'},
        
        # Eventos de Tempo
        {'sportmonks_id': 66, 'name': 'First Half Start', 'developer_name': 'first_half_start'},
        {'sportmonks_id': 67, 'name': 'First Half End', 'developer_name': 'first_half_end'},
        {'sportmonks_id': 68, 'name': 'Second Half Start', 'developer_name': 'second_half_start'},
        {'sportmonks_id': 69, 'name': 'Second Half End', 'developer_name': 'second_half_end'},
        {'sportmonks_id': 70, 'name': 'Extra Time Start', 'developer_name': 'extra_time_start'},
        {'sportmonks_id': 71, 'name': 'Extra Time End', 'developer_name': 'extra_time_end'},
        {'sportmonks_id': 72, 'name': 'Penalties Start', 'developer_name': 'penalties_start'},
        {'sportmonks_id': 73, 'name': 'Penalties End', 'developer_name': 'penalties_end'},
        
        # Eventos de Arbitragem
        {'sportmonks_id': 74, 'name': 'Referee Decision', 'developer_name': 'referee_decision'},
        {'sportmonks_id': 75, 'name': 'VAR Check', 'developer_name': 'var_check'},
        {'sportmonks_id': 76, 'name': 'VAR Decision', 'developer_name': 'var_decision'},
        
        # Eventos Especiais
        {'sportmonks_id': 77, 'name': 'Injury', 'developer_name': 'injury'},
        {'sportmonks_id': 78, 'name': 'Medical Treatment', 'developer_name': 'medical_treatment'},
        {'sportmonks_id': 79, 'name': 'Player Return', 'developer_name': 'player_return'},
        {'sportmonks_id': 80, 'name': 'Player Exit', 'developer_name': 'player_exit'},
        
        # Estatísticas Avançadas
        {'sportmonks_id': 81, 'name': 'Expected Goals', 'developer_name': 'expected_goals'},
        {'sportmonks_id': 82, 'name': 'Expected Assists', 'developer_name': 'expected_assists'},
        {'sportmonks_id': 85, 'name': 'Progressive Pass', 'developer_name': 'progressive_pass'},
        {'sportmonks_id': 86, 'name': 'Progressive Run', 'developer_name': 'progressive_run'},
        {'sportmonks_id': 87, 'name': 'Pressure', 'developer_name': 'pressure'},
        {'sportmonks_id': 88, 'name': 'Counter Attack', 'developer_name': 'counter_attack'},
        {'sportmonks_id': 89, 'name': 'High Turnover', 'developer_name': 'high_turnover'},
        {'sportmonks_id': 90, 'name': 'Low Turnover', 'developer_name': 'low_turnover'},
        
        # Eventos de Goleiro
        {'sportmonks_id': 91, 'name': 'Goalkeeper Save', 'developer_name': 'goalkeeper_save'},
        {'sportmonks_id': 92, 'name': 'Goalkeeper Punch', 'developer_name': 'goalkeeper_punch'},
        {'sportmonks_id': 93, 'name': 'Goalkeeper Catch', 'developer_name': 'goalkeeper_catch'},
        {'sportmonks_id': 94, 'name': 'Goalkeeper Drop', 'developer_name': 'goalkeeper_drop'},
        {'sportmonks_id': 95, 'name': 'Goalkeeper Throw', 'developer_name': 'goalkeeper_throw'},
        {'sportmonks_id': 96, 'name': 'Goalkeeper Kick', 'developer_name': 'goalkeeper_kick'},
        
        # Eventos de Capitão
        {'sportmonks_id': 97, 'name': 'Captain', 'developer_name': 'captain'},
        {'sportmonks_id': 98, 'name': 'Captain Change', 'developer_name': 'captain_change'},
        
        # Eventos de Tempo Adicional
        {'sportmonks_id': 99, 'name': 'Added Time', 'developer_name': 'added_time'},
        {'sportmonks_id': 100, 'name': 'Time Announcement', 'developer_name': 'time_announcement'},
    ]
    
    logger.info(f"📊 {len(complete_types_data)} types completos preparados")
    
    # Salvar types um por vez
    saved_count = 0
    skipped_count = 0
    
    for type_data in complete_types_data:
        try:
            type_data['created_at'] = datetime.utcnow().isoformat()
            supabase.table('types').insert(type_data).execute()
            saved_count += 1
            logger.info(f"✅ Type salvo: {type_data['name']} (ID: {type_data['sportmonks_id']})")
        except Exception as e:
            if 'duplicate key' in str(e).lower() or 'unique constraint' in str(e).lower():
                skipped_count += 1
                logger.info(f"⏭️ Type já existe: {type_data['name']} (ID: {type_data['sportmonks_id']})")
            else:
                logger.warning(f"⚠️ Erro ao salvar type '{type_data['name']}': {e}")
    
    logger.info(f"✅ {saved_count} types novos salvos")
    logger.info(f"⏭️ {skipped_count} types já existiam")
    
    # Relatório final
    logger.info("=" * 80)
    logger.info("📊 RELATÓRIO FINAL - TABELA TYPES ENRIQUECIDA")
    logger.info("=" * 80)
    
    try:
        response = supabase.table('types').select('*', count='exact').execute()
        total_count = response.count
        logger.info(f"📊 Total de types na tabela: {total_count}")
        
        # Mostrar alguns examples por categoria
        logger.info("📋 Exemplos de types por categoria:")
        
        # Eventos de Gol
        goal_types = supabase.table('types').select('sportmonks_id,name,developer_name').in_('sportmonks_id', [14,15,16,17]).execute()
        logger.info("⚽ Eventos de Gol:")
        for goal_type in goal_types.data:
            logger.info(f"   • ID {goal_type['sportmonks_id']}: {goal_type['name']}")
        
        # Cartões
        card_types = supabase.table('types').select('sportmonks_id,name,developer_name').in_('sportmonks_id', [19,20,21]).execute()
        logger.info("🟨🟥 Cartões:")
        for card_type in card_types.data:
            logger.info(f"   • ID {card_type['sportmonks_id']}: {card_type['name']}")
        
        # Substituições
        sub_types = supabase.table('types').select('sportmonks_id,name,developer_name').in_('sportmonks_id', [18,83,84]).execute()
        logger.info("🔄 Substituições:")
        for sub_type in sub_types.data:
            logger.info(f"   • ID {sub_type['sportmonks_id']}: {sub_type['name']}")
        
        # Estatísticas Avançadas
        advanced_types = supabase.table('types').select('sportmonks_id,name,developer_name').in_('sportmonks_id', [81,82,85,86]).execute()
        logger.info("📈 Estatísticas Avançadas:")
        for advanced_type in advanced_types.data:
            logger.info(f"   • ID {advanced_type['sportmonks_id']}: {advanced_type['name']}")
            
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")
    
    logger.info("=" * 80)
    logger.info("✅ ENRIQUECIMENTO COMPLETO DA TABELA TYPES CONCLUÍDO!")
    logger.info("=" * 80)

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 ENRIQUECENDO TABELA TYPES COM DADOS COMPLETOS")
    logger.info("=" * 80)
    
    enrich_types_with_complete_data()

if __name__ == "__main__":
    main()
