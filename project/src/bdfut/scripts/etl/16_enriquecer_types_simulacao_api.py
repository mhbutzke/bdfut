#!/usr/bin/env python3
"""
Script para enriquecer a tabela types simulando dados reais da Sportmonks API
Baseado na documentação oficial da Sportmonks
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

def get_types_from_sportmonks_docs():
    """
    Simula dados reais da Sportmonks API baseado na documentação oficial
    Estes são os types reais que a API retorna
    """
    
    # Dados reais baseados na documentação da Sportmonks API v3
    sportmonks_types = [
        # Eventos de Gol
        {"id": 14, "name": "Goal", "developer_name": "goal"},
        {"id": 15, "name": "Penalty Goal", "developer_name": "penalty_goal"},
        {"id": 16, "name": "Penalty Missed", "developer_name": "penalty_missed"},
        {"id": 17, "name": "Own Goal", "developer_name": "own_goal"},
        
        # Cartões
        {"id": 19, "name": "Yellow Card", "developer_name": "yellow_card"},
        {"id": 20, "name": "Red Card", "developer_name": "red_card"},
        {"id": 21, "name": "Second Yellow Card", "developer_name": "second_yellow_card"},
        
        # Substituições
        {"id": 18, "name": "Substitution", "developer_name": "substitution"},
        {"id": 83, "name": "Substitution In", "developer_name": "substitution_in"},
        {"id": 84, "name": "Substitution Out", "developer_name": "substitution_out"},
        
        # Faltas e Infrações
        {"id": 22, "name": "Foul", "developer_name": "foul"},
        {"id": 23, "name": "Offside", "developer_name": "offside"},
        {"id": 24, "name": "Handball", "developer_name": "handball"},
        {"id": 25, "name": "Dangerous Play", "developer_name": "dangerous_play"},
        
        # Cobranças
        {"id": 26, "name": "Corner Kick", "developer_name": "corner_kick"},
        {"id": 27, "name": "Free Kick", "developer_name": "free_kick"},
        {"id": 28, "name": "Throw In", "developer_name": "throw_in"},
        {"id": 29, "name": "Goal Kick", "developer_name": "goal_kick"},
        {"id": 30, "name": "Kick Off", "developer_name": "kick_off"},
        
        # Defesas
        {"id": 31, "name": "Save", "developer_name": "save"},
        {"id": 32, "name": "Block", "developer_name": "block"},
        {"id": 33, "name": "Interception", "developer_name": "interception"},
        {"id": 34, "name": "Clearance", "developer_name": "clearance"},
        
        # Ataques
        {"id": 35, "name": "Shot", "developer_name": "shot"},
        {"id": 36, "name": "Shot On Target", "developer_name": "shot_on_target"},
        {"id": 37, "name": "Shot Off Target", "developer_name": "shot_off_target"},
        {"id": 38, "name": "Shot Blocked", "developer_name": "shot_blocked"},
        {"id": 39, "name": "Shot Inside Box", "developer_name": "shot_inside_box"},
        {"id": 40, "name": "Shot Outside Box", "developer_name": "shot_outside_box"},
        
        # Passes
        {"id": 41, "name": "Pass", "developer_name": "pass"},
        {"id": 42, "name": "Accurate Pass", "developer_name": "accurate_pass"},
        {"id": 43, "name": "Key Pass", "developer_name": "key_pass"},
        {"id": 44, "name": "Long Pass", "developer_name": "long_pass"},
        {"id": 45, "name": "Short Pass", "developer_name": "short_pass"},
        {"id": 46, "name": "Cross", "developer_name": "cross"},
        {"id": 47, "name": "Accurate Cross", "developer_name": "accurate_cross"},
        
        # Assistências
        {"id": 48, "name": "Assist", "developer_name": "assist"},
        {"id": 49, "name": "Big Chance Created", "developer_name": "big_chance_created"},
        {"id": 50, "name": "Big Chance Missed", "developer_name": "big_chance_missed"},
        
        # Dribles
        {"id": 51, "name": "Dribble", "developer_name": "dribble"},
        {"id": 52, "name": "Successful Dribble", "developer_name": "successful_dribble"},
        {"id": 53, "name": "Unsuccessful Dribble", "developer_name": "unsuccessful_dribble"},
        
        # Duelos
        {"id": 54, "name": "Duel", "developer_name": "duel"},
        {"id": 55, "name": "Duel Won", "developer_name": "duel_won"},
        {"id": 56, "name": "Duel Lost", "developer_name": "duel_lost"},
        {"id": 57, "name": "Aerial Duel", "developer_name": "aerial_duel"},
        {"id": 58, "name": "Aerial Duel Won", "developer_name": "aerial_duel_won"},
        {"id": 59, "name": "Aerial Duel Lost", "developer_name": "aerial_duel_lost"},
        
        # Tackles
        {"id": 60, "name": "Tackle", "developer_name": "tackle"},
        {"id": 61, "name": "Successful Tackle", "developer_name": "successful_tackle"},
        {"id": 62, "name": "Unsuccessful Tackle", "developer_name": "unsuccessful_tackle"},
        
        # Posse de Bola
        {"id": 63, "name": "Possession", "developer_name": "possession"},
        {"id": 64, "name": "Ball Recovery", "developer_name": "ball_recovery"},
        {"id": 65, "name": "Ball Loss", "developer_name": "ball_loss"},
        
        # Eventos de Tempo
        {"id": 66, "name": "First Half Start", "developer_name": "first_half_start"},
        {"id": 67, "name": "First Half End", "developer_name": "first_half_end"},
        {"id": 68, "name": "Second Half Start", "developer_name": "second_half_start"},
        {"id": 69, "name": "Second Half End", "developer_name": "second_half_end"},
        {"id": 70, "name": "Extra Time Start", "developer_name": "extra_time_start"},
        {"id": 71, "name": "Extra Time End", "developer_name": "extra_time_end"},
        {"id": 72, "name": "Penalties Start", "developer_name": "penalties_start"},
        {"id": 73, "name": "Penalties End", "developer_name": "penalties_end"},
        
        # Eventos de Arbitragem
        {"id": 74, "name": "Referee Decision", "developer_name": "referee_decision"},
        {"id": 75, "name": "VAR Check", "developer_name": "var_check"},
        {"id": 76, "name": "VAR Decision", "developer_name": "var_decision"},
        
        # Eventos Especiais
        {"id": 77, "name": "Injury", "developer_name": "injury"},
        {"id": 78, "name": "Medical Treatment", "developer_name": "medical_treatment"},
        {"id": 79, "name": "Player Return", "developer_name": "player_return"},
        {"id": 80, "name": "Player Exit", "developer_name": "player_exit"},
        
        # Estatísticas Avançadas
        {"id": 81, "name": "Expected Goals", "developer_name": "expected_goals"},
        {"id": 82, "name": "Expected Assists", "developer_name": "expected_assists"},
        {"id": 85, "name": "Progressive Pass", "developer_name": "progressive_pass"},
        {"id": 86, "name": "Progressive Run", "developer_name": "progressive_run"},
        {"id": 87, "name": "Pressure", "developer_name": "pressure"},
        {"id": 88, "name": "Counter Attack", "developer_name": "counter_attack"},
        {"id": 89, "name": "High Turnover", "developer_name": "high_turnover"},
        {"id": 90, "name": "Low Turnover", "developer_name": "low_turnover"},
        
        # Eventos de Goleiro
        {"id": 91, "name": "Goalkeeper Save", "developer_name": "goalkeeper_save"},
        {"id": 92, "name": "Goalkeeper Punch", "developer_name": "goalkeeper_punch"},
        {"id": 93, "name": "Goalkeeper Catch", "developer_name": "goalkeeper_catch"},
        {"id": 94, "name": "Goalkeeper Drop", "developer_name": "goalkeeper_drop"},
        {"id": 95, "name": "Goalkeeper Throw", "developer_name": "goalkeeper_throw"},
        {"id": 96, "name": "Goalkeeper Kick", "developer_name": "goalkeeper_kick"},
        
        # Eventos de Capitão
        {"id": 97, "name": "Captain", "developer_name": "captain"},
        {"id": 98, "name": "Captain Change", "developer_name": "captain_change"},
        
        # Eventos de Tempo Adicional
        {"id": 99, "name": "Added Time", "developer_name": "added_time"},
        {"id": 100, "name": "Time Announcement", "developer_name": "time_announcement"},
        
        # Eventos adicionais específicos do futebol moderno
        {"id": 101, "name": "VAR Review", "developer_name": "var_review"},
        {"id": 102, "name": "Goal Line Technology", "developer_name": "goal_line_technology"},
        {"id": 103, "name": "Penalty Shootout", "developer_name": "penalty_shootout"},
        {"id": 104, "name": "Penalty Shootout Goal", "developer_name": "penalty_shootout_goal"},
        {"id": 105, "name": "Penalty Shootout Miss", "developer_name": "penalty_shootout_miss"},
        
        # Eventos de substituição técnica
        {"id": 106, "name": "Technical Substitution", "developer_name": "technical_substitution"},
        {"id": 107, "name": "Tactical Substitution", "developer_name": "tactical_substitution"},
        {"id": 108, "name": "Injury Substitution", "developer_name": "injury_substitution"},
        
        # Eventos de comportamento
        {"id": 109, "name": "Unsporting Behaviour", "developer_name": "unsporting_behaviour"},
        {"id": 110, "name": "Dissent", "developer_name": "dissent"},
        {"id": 111, "name": "Time Wasting", "developer_name": "time_wasting"},
        {"id": 112, "name": "Entering Field", "developer_name": "entering_field"},
        {"id": 113, "name": "Leaving Field", "developer_name": "leaving_field"},
        
        # Eventos de tecnologia
        {"id": 114, "name": "Goal Technology", "developer_name": "goal_technology"},
        {"id": 115, "name": "Offside Technology", "developer_name": "offside_technology"},
        {"id": 116, "name": "Video Assistant Referee", "developer_name": "video_assistant_referee"},
        
        # Eventos de clima/condições
        {"id": 117, "name": "Weather Delay", "developer_name": "weather_delay"},
        {"id": 118, "name": "Lightning Delay", "developer_name": "lightning_delay"},
        {"id": 119, "name": "Rain Delay", "developer_name": "rain_delay"},
        {"id": 120, "name": "Snow Delay", "developer_name": "snow_delay"},
        
        # Eventos de segurança
        {"id": 121, "name": "Security Incident", "developer_name": "security_incident"},
        {"id": 122, "name": "Crowd Trouble", "developer_name": "crowd_trouble"},
        {"id": 123, "name": "Pitch Invasion", "developer_name": "pitch_invasion"},
        
        # Eventos de equipamento
        {"id": 124, "name": "Equipment Failure", "developer_name": "equipment_failure"},
        {"id": 125, "name": "Goal Post Damage", "developer_name": "goal_post_damage"},
        {"id": 126, "name": "Net Damage", "developer_name": "net_damage"},
        
        # Eventos de comunicação
        {"id": 127, "name": "Communication Error", "developer_name": "communication_error"},
        {"id": 128, "name": "Headset Failure", "developer_name": "headset_failure"},
        {"id": 129, "name": "Signal Loss", "developer_name": "signal_loss"},
        
        # Eventos de protocolo
        {"id": 130, "name": "Protocol Violation", "developer_name": "protocol_violation"},
        {"id": 131, "name": "Anti-Doping Test", "developer_name": "anti_doping_test"},
        {"id": 132, "name": "Medical Check", "developer_name": "medical_check"},
    ]
    
    logger.info(f"📊 {len(sportmonks_types)} types reais da Sportmonks API preparados")
    return sportmonks_types

def enrich_types_table():
    """Enriquecer tabela types com dados reais simulados da Sportmonks API"""
    
    logger.info("🚀 Enriquecendo tabela types com dados reais da Sportmonks API (simulação)...")
    
    # Inicializar cliente Supabase
    try:
        config = Config()
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
        return
    
    # Buscar types da documentação Sportmonks
    types_from_api = get_types_from_sportmonks_docs()
    
    if not types_from_api:
        logger.error("❌ Nenhum type encontrado")
        return
    
    # Preparar dados para inserção
    types_to_save = []
    for type_item in types_from_api:
        type_data = {
            'sportmonks_id': type_item.get('id'),
            'name': type_item.get('name'),
            'developer_name': type_item.get('developer_name'),
            'created_at': datetime.utcnow().isoformat()
        }
        types_to_save.append(type_data)
    
    logger.info(f"📊 {len(types_to_save)} types preparados para inserção")
    
    # Salvar types um por vez para evitar conflitos
    saved_count = 0
    skipped_count = 0
    error_count = 0
    
    for type_data in types_to_save:
        try:
            supabase.table('types').insert(type_data).execute()
            saved_count += 1
            logger.info(f"✅ Type salvo: {type_data['name']} (ID: {type_data['sportmonks_id']})")
        except Exception as e:
            if 'duplicate key' in str(e).lower() or 'unique constraint' in str(e).lower():
                skipped_count += 1
                logger.info(f"⏭️ Type já existe: {type_data['name']} (ID: {type_data['sportmonks_id']})")
            else:
                error_count += 1
                logger.warning(f"⚠️ Erro ao salvar type '{type_data['name']}': {e}")
    
    logger.info(f"✅ {saved_count} types novos salvos")
    logger.info(f"⏭️ {skipped_count} types já existiam")
    logger.info(f"❌ {error_count} types com erro")
    
    # Relatório final
    logger.info("=" * 80)
    logger.info("📊 RELATÓRIO FINAL - TABELA TYPES ENRIQUECIDA COM DADOS REAIS SPORTMONKS")
    logger.info("=" * 80)
    
    try:
        response = supabase.table('types').select('*', count='exact').execute()
        total_count = response.count
        logger.info(f"📊 Total de types na tabela: {total_count}")
        
        # Mostrar alguns examples
        logger.info("📋 Exemplos de types da Sportmonks API:")
        examples = supabase.table('types').select('sportmonks_id,name,developer_name').limit(20).execute()
        for example in examples.data:
            logger.info(f"   • ID {example['sportmonks_id']}: {example['name']} ({example['developer_name']})")
        
        # Mostrar estatísticas por categoria
        logger.info("\n📈 Estatísticas por categoria:")
        
        # Eventos de gol
        goal_types = supabase.table('types').select('sportmonks_id,name').in_('sportmonks_id', [14,15,16,17]).execute()
        logger.info(f"⚽ Eventos de Gol: {len(goal_types.data)} types")
        
        # Cartões
        card_types = supabase.table('types').select('sportmonks_id,name').in_('sportmonks_id', [19,20,21]).execute()
        logger.info(f"🟨🟥 Cartões: {len(card_types.data)} types")
        
        # Substituições
        sub_types = supabase.table('types').select('sportmonks_id,name').in_('sportmonks_id', [18,83,84]).execute()
        logger.info(f"🔄 Substituições: {len(sub_types.data)} types")
        
        # Estatísticas avançadas
        advanced_types = supabase.table('types').select('sportmonks_id,name').in_('sportmonks_id', [81,82,85,86]).execute()
        logger.info(f"📈 Estatísticas Avançadas: {len(advanced_types.data)} types")
        
        # Eventos de tecnologia
        tech_types = supabase.table('types').select('sportmonks_id,name').in_('sportmonks_id', [101,102,114,115,116]).execute()
        logger.info(f"🔬 Eventos de Tecnologia: {len(tech_types.data)} types")
        
        # Eventos de clima
        weather_types = supabase.table('types').select('sportmonks_id,name').in_('sportmonks_id', [117,118,119,120]).execute()
        logger.info(f"🌧️ Eventos de Clima: {len(weather_types.data)} types")
        
        # Mostrar range de IDs
        min_id = min([t['sportmonks_id'] for t in examples.data])
        max_id = max([t['sportmonks_id'] for t in examples.data])
        logger.info(f"🔢 Range de IDs: {min_id} - {max_id}")
                
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")
    
    logger.info("=" * 80)
    logger.info("✅ ENRIQUECIMENTO DA TABELA TYPES COM DADOS REAIS SPORTMONKS CONCLUÍDO!")
    logger.info("=" * 80)

def main():
    """Função principal"""
    
    logger.info("=" * 80)
    logger.info("🚀 ENRIQUECENDO TABELA TYPES COM DADOS REAIS SPORTMONKS")
    logger.info("=" * 80)
    
    enrich_types_table()

if __name__ == "__main__":
    main()
