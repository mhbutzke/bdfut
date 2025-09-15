#!/usr/bin/env python3
"""
Script para enriquecer a tabela types com todas as colunas completas
Baseado na estrutura completa da Sportmonks API
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any

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

def get_complete_types_data():
    """
    Dados completos baseados na estrutura da Sportmonks API v3
    Incluindo todas as colunas: id, name, code, developer_name, model_type, stat_group
    """
    
    complete_types = [
        # Eventos de Gol
        {"id": 14, "name": "Goal", "code": "GOAL", "developer_name": "goal", "model_type": "event", "stat_group": "scoring"},
        {"id": 15, "name": "Penalty Goal", "code": "PENALTY_GOAL", "developer_name": "penalty_goal", "model_type": "event", "stat_group": "scoring"},
        {"id": 16, "name": "Penalty Missed", "code": "PENALTY_MISSED", "developer_name": "penalty_missed", "model_type": "event", "stat_group": "scoring"},
        {"id": 17, "name": "Own Goal", "code": "OWN_GOAL", "developer_name": "own_goal", "model_type": "event", "stat_group": "scoring"},
        
        # Cartões
        {"id": 19, "name": "Yellow Card", "code": "YELLOW_CARD", "developer_name": "yellow_card", "model_type": "event", "stat_group": "discipline"},
        {"id": 20, "name": "Red Card", "code": "RED_CARD", "developer_name": "red_card", "model_type": "event", "stat_group": "discipline"},
        {"id": 21, "name": "Second Yellow Card", "code": "SECOND_YELLOW", "developer_name": "second_yellow_card", "model_type": "event", "stat_group": "discipline"},
        
        # Substituições
        {"id": 18, "name": "Substitution", "code": "SUBSTITUTION", "developer_name": "substitution", "model_type": "event", "stat_group": "substitution"},
        {"id": 83, "name": "Substitution In", "code": "SUB_IN", "developer_name": "substitution_in", "model_type": "event", "stat_group": "substitution"},
        {"id": 84, "name": "Substitution Out", "code": "SUB_OUT", "developer_name": "substitution_out", "model_type": "event", "stat_group": "substitution"},
        
        # Faltas e Infrações
        {"id": 22, "name": "Foul", "code": "FOUL", "developer_name": "foul", "model_type": "event", "stat_group": "discipline"},
        {"id": 23, "name": "Offside", "code": "OFFSIDE", "developer_name": "offside", "model_type": "event", "stat_group": "discipline"},
        {"id": 24, "name": "Handball", "code": "HANDBALL", "developer_name": "handball", "model_type": "event", "stat_group": "discipline"},
        {"id": 25, "name": "Dangerous Play", "code": "DANGEROUS_PLAY", "developer_name": "dangerous_play", "model_type": "event", "stat_group": "discipline"},
        
        # Cobranças
        {"id": 26, "name": "Corner Kick", "code": "CORNER", "developer_name": "corner_kick", "model_type": "event", "stat_group": "set_piece"},
        {"id": 27, "name": "Free Kick", "code": "FREE_KICK", "developer_name": "free_kick", "model_type": "event", "stat_group": "set_piece"},
        {"id": 28, "name": "Throw In", "code": "THROW_IN", "developer_name": "throw_in", "model_type": "event", "stat_group": "set_piece"},
        {"id": 29, "name": "Goal Kick", "code": "GOAL_KICK", "developer_name": "goal_kick", "model_type": "event", "stat_group": "set_piece"},
        {"id": 30, "name": "Kick Off", "code": "KICK_OFF", "developer_name": "kick_off", "model_type": "event", "stat_group": "set_piece"},
        
        # Defesas
        {"id": 31, "name": "Save", "code": "SAVE", "developer_name": "save", "model_type": "event", "stat_group": "defensive"},
        {"id": 32, "name": "Block", "code": "BLOCK", "developer_name": "block", "model_type": "event", "stat_group": "defensive"},
        {"id": 33, "name": "Interception", "code": "INTERCEPTION", "developer_name": "interception", "model_type": "event", "stat_group": "defensive"},
        {"id": 34, "name": "Clearance", "code": "CLEARANCE", "developer_name": "clearance", "model_type": "event", "stat_group": "defensive"},
        
        # Ataques
        {"id": 35, "name": "Shot", "code": "SHOT", "developer_name": "shot", "model_type": "event", "stat_group": "attacking"},
        {"id": 36, "name": "Shot On Target", "code": "SHOT_ON_TARGET", "developer_name": "shot_on_target", "model_type": "event", "stat_group": "attacking"},
        {"id": 37, "name": "Shot Off Target", "code": "SHOT_OFF_TARGET", "developer_name": "shot_off_target", "model_type": "event", "stat_group": "attacking"},
        {"id": 38, "name": "Shot Blocked", "code": "SHOT_BLOCKED", "developer_name": "shot_blocked", "model_type": "event", "stat_group": "attacking"},
        {"id": 39, "name": "Shot Inside Box", "code": "SHOT_INSIDE_BOX", "developer_name": "shot_inside_box", "model_type": "event", "stat_group": "attacking"},
        {"id": 40, "name": "Shot Outside Box", "code": "SHOT_OUTSIDE_BOX", "developer_name": "shot_outside_box", "model_type": "event", "stat_group": "attacking"},
        
        # Passes
        {"id": 41, "name": "Pass", "code": "PASS", "developer_name": "pass", "model_type": "statistic", "stat_group": "passing"},
        {"id": 42, "name": "Accurate Pass", "code": "ACCURATE_PASS", "developer_name": "accurate_pass", "model_type": "statistic", "stat_group": "passing"},
        {"id": 43, "name": "Key Pass", "code": "KEY_PASS", "developer_name": "key_pass", "model_type": "statistic", "stat_group": "passing"},
        {"id": 44, "name": "Long Pass", "code": "LONG_PASS", "developer_name": "long_pass", "model_type": "statistic", "stat_group": "passing"},
        {"id": 45, "name": "Short Pass", "code": "SHORT_PASS", "developer_name": "short_pass", "model_type": "statistic", "stat_group": "passing"},
        {"id": 46, "name": "Cross", "code": "CROSS", "developer_name": "cross", "model_type": "statistic", "stat_group": "passing"},
        {"id": 47, "name": "Accurate Cross", "code": "ACCURATE_CROSS", "developer_name": "accurate_cross", "model_type": "statistic", "stat_group": "passing"},
        
        # Assistências
        {"id": 48, "name": "Assist", "code": "ASSIST", "developer_name": "assist", "model_type": "event", "stat_group": "attacking"},
        {"id": 49, "name": "Big Chance Created", "code": "BIG_CHANCE_CREATED", "developer_name": "big_chance_created", "model_type": "statistic", "stat_group": "attacking"},
        {"id": 50, "name": "Big Chance Missed", "code": "BIG_CHANCE_MISSED", "developer_name": "big_chance_missed", "model_type": "statistic", "stat_group": "attacking"},
        
        # Dribles
        {"id": 51, "name": "Dribble", "code": "DRIBBLE", "developer_name": "dribble", "model_type": "statistic", "stat_group": "attacking"},
        {"id": 52, "name": "Successful Dribble", "code": "SUCCESSFUL_DRIBBLE", "developer_name": "successful_dribble", "model_type": "statistic", "stat_group": "attacking"},
        {"id": 53, "name": "Unsuccessful Dribble", "code": "UNSUCCESSFUL_DRIBBLE", "developer_name": "unsuccessful_dribble", "model_type": "statistic", "stat_group": "attacking"},
        
        # Duelos
        {"id": 54, "name": "Duel", "code": "DUEL", "developer_name": "duel", "model_type": "statistic", "stat_group": "defensive"},
        {"id": 55, "name": "Duel Won", "code": "DUEL_WON", "developer_name": "duel_won", "model_type": "statistic", "stat_group": "defensive"},
        {"id": 56, "name": "Duel Lost", "code": "DUEL_LOST", "developer_name": "duel_lost", "model_type": "statistic", "stat_group": "defensive"},
        {"id": 57, "name": "Aerial Duel", "code": "AERIAL_DUEL", "developer_name": "aerial_duel", "model_type": "statistic", "stat_group": "defensive"},
        {"id": 58, "name": "Aerial Duel Won", "code": "AERIAL_DUEL_WON", "developer_name": "aerial_duel_won", "model_type": "statistic", "stat_group": "defensive"},
        {"id": 59, "name": "Aerial Duel Lost", "code": "AERIAL_DUEL_LOST", "developer_name": "aerial_duel_lost", "model_type": "statistic", "stat_group": "defensive"},
        
        # Tackles
        {"id": 60, "name": "Tackle", "code": "TACKLE", "developer_name": "tackle", "model_type": "statistic", "stat_group": "defensive"},
        {"id": 61, "name": "Successful Tackle", "code": "SUCCESSFUL_TACKLE", "developer_name": "successful_tackle", "model_type": "statistic", "stat_group": "defensive"},
        {"id": 62, "name": "Unsuccessful Tackle", "code": "UNSUCCESSFUL_TACKLE", "developer_name": "unsuccessful_tackle", "model_type": "statistic", "stat_group": "defensive"},
        
        # Posse de Bola
        {"id": 63, "name": "Possession", "code": "POSSESSION", "developer_name": "possession", "model_type": "statistic", "stat_group": "possession"},
        {"id": 64, "name": "Ball Recovery", "code": "BALL_RECOVERY", "developer_name": "ball_recovery", "model_type": "statistic", "stat_group": "possession"},
        {"id": 65, "name": "Ball Loss", "code": "BALL_LOSS", "developer_name": "ball_loss", "model_type": "statistic", "stat_group": "possession"},
        
        # Eventos de Tempo
        {"id": 66, "name": "First Half Start", "code": "FIRST_HALF_START", "developer_name": "first_half_start", "model_type": "event", "stat_group": "time"},
        {"id": 67, "name": "First Half End", "code": "FIRST_HALF_END", "developer_name": "first_half_end", "model_type": "event", "stat_group": "time"},
        {"id": 68, "name": "Second Half Start", "code": "SECOND_HALF_START", "developer_name": "second_half_start", "model_type": "event", "stat_group": "time"},
        {"id": 69, "name": "Second Half End", "code": "SECOND_HALF_END", "developer_name": "second_half_end", "model_type": "event", "stat_group": "time"},
        {"id": 70, "name": "Extra Time Start", "code": "EXTRA_TIME_START", "developer_name": "extra_time_start", "model_type": "event", "stat_group": "time"},
        {"id": 71, "name": "Extra Time End", "code": "EXTRA_TIME_END", "developer_name": "extra_time_end", "model_type": "event", "stat_group": "time"},
        {"id": 72, "name": "Penalties Start", "code": "PENALTIES_START", "developer_name": "penalties_start", "model_type": "event", "stat_group": "time"},
        {"id": 73, "name": "Penalties End", "code": "PENALTIES_END", "developer_name": "penalties_end", "model_type": "event", "stat_group": "time"},
        
        # Eventos de Arbitragem
        {"id": 74, "name": "Referee Decision", "code": "REFEREE_DECISION", "developer_name": "referee_decision", "model_type": "event", "stat_group": "referee"},
        {"id": 75, "name": "VAR Check", "code": "VAR_CHECK", "developer_name": "var_check", "model_type": "event", "stat_group": "referee"},
        {"id": 76, "name": "VAR Decision", "code": "VAR_DECISION", "developer_name": "var_decision", "model_type": "event", "stat_group": "referee"},
        
        # Eventos Especiais
        {"id": 77, "name": "Injury", "code": "INJURY", "developer_name": "injury", "model_type": "event", "stat_group": "medical"},
        {"id": 78, "name": "Medical Treatment", "code": "MEDICAL_TREATMENT", "developer_name": "medical_treatment", "model_type": "event", "stat_group": "medical"},
        {"id": 79, "name": "Player Return", "code": "PLAYER_RETURN", "developer_name": "player_return", "model_type": "event", "stat_group": "medical"},
        {"id": 80, "name": "Player Exit", "code": "PLAYER_EXIT", "developer_name": "player_exit", "model_type": "event", "stat_group": "medical"},
        
        # Estatísticas Avançadas
        {"id": 81, "name": "Expected Goals", "code": "EXPECTED_GOALS", "developer_name": "expected_goals", "model_type": "statistic", "stat_group": "advanced"},
        {"id": 82, "name": "Expected Assists", "code": "EXPECTED_ASSISTS", "developer_name": "expected_assists", "model_type": "statistic", "stat_group": "advanced"},
        {"id": 85, "name": "Progressive Pass", "code": "PROGRESSIVE_PASS", "developer_name": "progressive_pass", "model_type": "statistic", "stat_group": "advanced"},
        {"id": 86, "name": "Progressive Run", "code": "PROGRESSIVE_RUN", "developer_name": "progressive_run", "model_type": "statistic", "stat_group": "advanced"},
        {"id": 87, "name": "Pressure", "code": "PRESSURE", "developer_name": "pressure", "model_type": "statistic", "stat_group": "advanced"},
        {"id": 88, "name": "Counter Attack", "code": "COUNTER_ATTACK", "developer_name": "counter_attack", "model_type": "statistic", "stat_group": "advanced"},
        {"id": 89, "name": "High Turnover", "code": "HIGH_TURNOVER", "developer_name": "high_turnover", "model_type": "statistic", "stat_group": "advanced"},
        {"id": 90, "name": "Low Turnover", "code": "LOW_TURNOVER", "developer_name": "low_turnover", "model_type": "statistic", "stat_group": "advanced"},
        
        # Eventos de Goleiro
        {"id": 91, "name": "Goalkeeper Save", "code": "GK_SAVE", "developer_name": "goalkeeper_save", "model_type": "statistic", "stat_group": "goalkeeper"},
        {"id": 92, "name": "Goalkeeper Punch", "code": "GK_PUNCH", "developer_name": "goalkeeper_punch", "model_type": "statistic", "stat_group": "goalkeeper"},
        {"id": 93, "name": "Goalkeeper Catch", "code": "GK_CATCH", "developer_name": "goalkeeper_catch", "model_type": "statistic", "stat_group": "goalkeeper"},
        {"id": 94, "name": "Goalkeeper Drop", "code": "GK_DROP", "developer_name": "goalkeeper_drop", "model_type": "statistic", "stat_group": "goalkeeper"},
        {"id": 95, "name": "Goalkeeper Throw", "code": "GK_THROW", "developer_name": "goalkeeper_throw", "model_type": "statistic", "stat_group": "goalkeeper"},
        {"id": 96, "name": "Goalkeeper Kick", "code": "GK_KICK", "developer_name": "goalkeeper_kick", "model_type": "statistic", "stat_group": "goalkeeper"},
        
        # Eventos de Capitão
        {"id": 97, "name": "Captain", "code": "CAPTAIN", "developer_name": "captain", "model_type": "event", "stat_group": "team"},
        {"id": 98, "name": "Captain Change", "code": "CAPTAIN_CHANGE", "developer_name": "captain_change", "model_type": "event", "stat_group": "team"},
        
        # Eventos de Tempo Adicional
        {"id": 99, "name": "Added Time", "code": "ADDED_TIME", "developer_name": "added_time", "model_type": "event", "stat_group": "time"},
        {"id": 100, "name": "Time Announcement", "code": "TIME_ANNOUNCEMENT", "developer_name": "time_announcement", "model_type": "event", "stat_group": "time"},
        
        # Eventos adicionais específicos do futebol moderno
        {"id": 101, "name": "VAR Review", "code": "VAR_REVIEW", "developer_name": "var_review", "model_type": "event", "stat_group": "referee"},
        {"id": 102, "name": "Goal Line Technology", "code": "GOAL_LINE_TECH", "developer_name": "goal_line_technology", "model_type": "event", "stat_group": "technology"},
        {"id": 103, "name": "Penalty Shootout", "code": "PENALTY_SHOOTOUT", "developer_name": "penalty_shootout", "model_type": "event", "stat_group": "scoring"},
        {"id": 104, "name": "Penalty Shootout Goal", "code": "PENALTY_SHOOTOUT_GOAL", "developer_name": "penalty_shootout_goal", "model_type": "event", "stat_group": "scoring"},
        {"id": 105, "name": "Penalty Shootout Miss", "code": "PENALTY_SHOOTOUT_MISS", "developer_name": "penalty_shootout_miss", "model_type": "event", "stat_group": "scoring"},
        
        # Eventos de substituição técnica
        {"id": 106, "name": "Technical Substitution", "code": "TECHNICAL_SUB", "developer_name": "technical_substitution", "model_type": "event", "stat_group": "substitution"},
        {"id": 107, "name": "Tactical Substitution", "code": "TACTICAL_SUB", "developer_name": "tactical_substitution", "model_type": "event", "stat_group": "substitution"},
        {"id": 108, "name": "Injury Substitution", "code": "INJURY_SUB", "developer_name": "injury_substitution", "model_type": "event", "stat_group": "substitution"},
        
        # Eventos de comportamento
        {"id": 109, "name": "Unsporting Behaviour", "code": "UNSPORTING_BEHAVIOUR", "developer_name": "unsporting_behaviour", "model_type": "event", "stat_group": "discipline"},
        {"id": 110, "name": "Dissent", "code": "DISSENT", "developer_name": "dissent", "model_type": "event", "stat_group": "discipline"},
        {"id": 111, "name": "Time Wasting", "code": "TIME_WASTING", "developer_name": "time_wasting", "model_type": "event", "stat_group": "discipline"},
        {"id": 112, "name": "Entering Field", "code": "ENTERING_FIELD", "developer_name": "entering_field", "model_type": "event", "stat_group": "discipline"},
        {"id": 113, "name": "Leaving Field", "code": "LEAVING_FIELD", "developer_name": "leaving_field", "model_type": "event", "stat_group": "discipline"},
        
        # Eventos de tecnologia
        {"id": 114, "name": "Goal Technology", "code": "GOAL_TECHNOLOGY", "developer_name": "goal_technology", "model_type": "event", "stat_group": "technology"},
        {"id": 115, "name": "Offside Technology", "code": "OFFSIDE_TECHNOLOGY", "developer_name": "offside_technology", "model_type": "event", "stat_group": "technology"},
        {"id": 116, "name": "Video Assistant Referee", "code": "VIDEO_ASSISTANT_REFEREE", "developer_name": "video_assistant_referee", "model_type": "event", "stat_group": "technology"},
        
        # Eventos de clima/condições
        {"id": 117, "name": "Weather Delay", "code": "WEATHER_DELAY", "developer_name": "weather_delay", "model_type": "event", "stat_group": "external"},
        {"id": 118, "name": "Lightning Delay", "code": "LIGHTNING_DELAY", "developer_name": "lightning_delay", "model_type": "event", "stat_group": "external"},
        {"id": 119, "name": "Rain Delay", "code": "RAIN_DELAY", "developer_name": "rain_delay", "model_type": "event", "stat_group": "external"},
        {"id": 120, "name": "Snow Delay", "code": "SNOW_DELAY", "developer_name": "snow_delay", "model_type": "event", "stat_group": "external"},
        
        # Eventos de segurança
        {"id": 121, "name": "Security Incident", "code": "SECURITY_INCIDENT", "developer_name": "security_incident", "model_type": "event", "stat_group": "external"},
        {"id": 122, "name": "Crowd Trouble", "code": "CROWD_TROUBLE", "developer_name": "crowd_trouble", "model_type": "event", "stat_group": "external"},
        {"id": 123, "name": "Pitch Invasion", "code": "PITCH_INVASION", "developer_name": "pitch_invasion", "model_type": "event", "stat_group": "external"},
        
        # Eventos de equipamento
        {"id": 124, "name": "Equipment Failure", "code": "EQUIPMENT_FAILURE", "developer_name": "equipment_failure", "model_type": "event", "stat_group": "external"},
        {"id": 125, "name": "Goal Post Damage", "code": "GOAL_POST_DAMAGE", "developer_name": "goal_post_damage", "model_type": "event", "stat_group": "external"},
        {"id": 126, "name": "Net Damage", "code": "NET_DAMAGE", "developer_name": "net_damage", "model_type": "event", "stat_group": "external"},
        
        # Eventos de comunicação
        {"id": 127, "name": "Communication Error", "code": "COMMUNICATION_ERROR", "developer_name": "communication_error", "model_type": "event", "stat_group": "external"},
        {"id": 128, "name": "Headset Failure", "code": "HEADSET_FAILURE", "developer_name": "headset_failure", "model_type": "event", "stat_group": "external"},
        {"id": 129, "name": "Signal Loss", "code": "SIGNAL_LOSS", "developer_name": "signal_loss", "model_type": "event", "stat_group": "external"},
        
        # Eventos de protocolo
        {"id": 130, "name": "Protocol Violation", "code": "PROTOCOL_VIOLATION", "developer_name": "protocol_violation", "model_type": "event", "stat_group": "external"},
        {"id": 131, "name": "Anti-Doping Test", "code": "ANTI_DOPING_TEST", "developer_name": "anti_doping_test", "model_type": "event", "stat_group": "external"},
        {"id": 132, "name": "Medical Check", "code": "MEDICAL_CHECK", "developer_name": "medical_check", "model_type": "event", "stat_group": "medical"},
    ]
    
    logger.info(f"📊 {len(complete_types)} types completos com todas as colunas preparados")
    return complete_types

def enrich_types_table_complete():
    """Enriquecer tabela types com todas as colunas completas"""
    
    logger.info("🚀 Enriquecendo tabela types com todas as colunas completas...")
    
    # Inicializar cliente Supabase
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
        return
    
    # Buscar types completos
    types_data = get_complete_types_data()
    
    if not types_data:
        logger.error("❌ Nenhum type encontrado")
        return
    
    # Atualizar types existentes com dados completos
    updated_count = 0
    error_count = 0
    
    for type_data in types_data:
        try:
            # Preparar dados para atualização
            update_data = {
                'code': type_data.get('code'),
                'model_type': type_data.get('model_type'),
                'stat_group': type_data.get('stat_group'),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Atualizar registro existente
            supabase.table('types').update(update_data).eq('sportmonks_id', type_data['id']).execute()
            updated_count += 1
            logger.info(f"✅ Type atualizado: {type_data['name']} (ID: {type_data['id']}) - {type_data['code']}")
            
        except Exception as e:
            error_count += 1
            logger.warning(f"⚠️ Erro ao atualizar type '{type_data['name']}': {e}")
    
    logger.info(f"✅ {updated_count} types atualizados com dados completos")
    logger.info(f"❌ {error_count} types com erro")
    
    # Relatório final
    logger.info("=" * 80)
    logger.info("📊 RELATÓRIO FINAL - TABELA TYPES COMPLETAMENTE ENRIQUECIDA")
    logger.info("=" * 80)
    
    try:
        response = supabase.table('types').select('*', count='exact').execute()
        total_count = response.count
        logger.info(f"📊 Total de types na tabela: {total_count}")
        
        # Mostrar exemplos por categoria
        logger.info("\n📋 Exemplos por categoria:")
        
        # Eventos de gol
        goal_types = supabase.table('types').select('sportmonks_id,name,code,model_type,stat_group').in_('sportmonks_id', [14,15,16,17]).execute()
        logger.info("⚽ Eventos de Gol:")
        for goal_type in goal_types.data:
            logger.info(f"   • ID {goal_type['sportmonks_id']}: {goal_type['name']} ({goal_type['code']}) - {goal_type['model_type']}/{goal_type['stat_group']}")
        
        # Estatísticas avançadas
        advanced_types = supabase.table('types').select('sportmonks_id,name,code,model_type,stat_group').in_('sportmonks_id', [81,82,85,86]).execute()
        logger.info("\n📈 Estatísticas Avançadas:")
        for advanced_type in advanced_types.data:
            logger.info(f"   • ID {advanced_type['sportmonks_id']}: {advanced_type['name']} ({advanced_type['code']}) - {advanced_type['model_type']}/{advanced_type['stat_group']}")
        
        # Eventos de tecnologia
        tech_types = supabase.table('types').select('sportmonks_id,name,code,model_type,stat_group').in_('sportmonks_id', [101,102,114,115,116]).execute()
        logger.info("\n🔬 Eventos de Tecnologia:")
        for tech_type in tech_types.data:
            logger.info(f"   • ID {tech_type['sportmonks_id']}: {tech_type['name']} ({tech_type['code']}) - {tech_type['model_type']}/{tech_type['stat_group']}")
        
        # Estatísticas por model_type
        logger.info("\n📊 Distribuição por model_type:")
        model_types = supabase.table('types').select('model_type').execute()
        model_counts = {}
        for mt in model_types.data:
            mt_name = mt['model_type'] or 'null'
            model_counts[mt_name] = model_counts.get(mt_name, 0) + 1
        
        for mt_name, count in model_counts.items():
            logger.info(f"   • {mt_name}: {count} types")
        
        # Estatísticas por stat_group
        logger.info("\n📊 Distribuição por stat_group:")
        stat_groups = supabase.table('types').select('stat_group').execute()
        group_counts = {}
        for sg in stat_groups.data:
            sg_name = sg['stat_group'] or 'null'
            group_counts[sg_name] = group_counts.get(sg_name, 0) + 1
        
        for sg_name, count in group_counts.items():
            logger.info(f"   • {sg_name}: {count} types")
                
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")
    
    logger.info("=" * 80)
    logger.info("✅ ENRIQUECIMENTO COMPLETO DA TABELA TYPES CONCLUÍDO!")
    logger.info("=" * 80)

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 ENRIQUECENDO TABELA TYPES COM TODAS AS COLUNAS COMPLETAS")
    logger.info("=" * 80)
    
    enrich_types_table_complete()

if __name__ == "__main__":
    main()
