"""
Expected Goals Calculator - Sistema próprio de cálculo xG
TASK-ETL-026: Sistema Próprio de Expected Goals

Algoritmo baseado em dados disponíveis (match_events e match_statistics)
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

@dataclass
class ExpectedGoalsResult:
    """Resultado do cálculo de Expected Goals"""
    fixture_id: int
    team_id: int
    player_id: Optional[int] = None
    expected_goals: float = 0.0
    expected_assists: float = 0.0
    expected_points: float = 0.0
    actual_goals: int = 0
    actual_assists: int = 0
    shots_total: int = 0
    shots_inside_box: int = 0
    shots_outside_box: int = 0
    penalties_taken: int = 0
    big_chances: int = 0
    calculation_method: str = "basic_algorithm_v1"

class ExpectedGoalsCalculator:
    """Calculadora de Expected Goals própria"""
    
    def __init__(self):
        # Fatores de conversão baseados em análise estatística (ajustados)
        self.SHOT_TO_GOAL_RATE = 0.08  # Taxa média de conversão de chutes em gols (mais realista)
        self.INSIDE_BOX_MULTIPLIER = 1.5  # Chutes dentro da área são mais efetivos
        self.OUTSIDE_BOX_MULTIPLIER = 0.2  # Chutes fora da área são menos efetivos
        self.PENALTY_CONVERSION_RATE = 0.75  # Taxa de conversão de pênaltis
        self.BIG_CHANCE_CONVERSION_RATE = 0.35  # Taxa de conversão de grandes chances
        
        # Fatores de contexto
        self.HOME_ADVANTAGE = 1.05  # Vantagem de jogar em casa (mais moderada)
        self.PERIOD_MULTIPLIERS = {
            1: 1.0,  # Primeiro tempo
            2: 0.9,  # Segundo tempo (jogadores mais cansados)
            3: 0.7,  # Prorrogação
            4: 0.6   # Segundo tempo da prorrogação
        }
    
    def calculate_team_xg(self, 
                         fixture_id: int, 
                         team_id: int,
                         shots_total: int = 0,
                         shots_inside_box: int = 0,
                         shots_outside_box: int = 0,
                         goals: List[Dict] = None,
                         penalties: List[Dict] = None,
                         is_home: bool = True) -> ExpectedGoalsResult:
        """
        Calcula xG para um time em uma partida
        
        Args:
            fixture_id: ID da partida
            team_id: ID do time
            shots_total: Total de chutes
            shots_inside_box: Chutes dentro da área
            shots_outside_box: Chutes fora da área
            goals: Lista de gols marcados
            penalties: Lista de pênaltis
            is_home: Se é time da casa
        """
        
        if goals is None:
            goals = []
        if penalties is None:
            penalties = []
        
        # Calcular xG baseado em chutes
        xg_from_shots = self._calculate_xg_from_shots(
            shots_total, shots_inside_box, shots_outside_box
        )
        
        # Calcular xG de pênaltis
        penalty_goals = len([p for p in penalties if p.get('event_type') == 'penalty_goal'])
        penalty_misses = len([p for p in penalties if p.get('event_type') == 'penalty_missed'])
        penalties_taken = penalty_goals + penalty_misses
        
        xg_from_penalties = penalties_taken * self.PENALTY_CONVERSION_RATE
        
        # xG total
        total_xg = xg_from_shots + xg_from_penalties
        
        # Aplicar fatores de contexto (mais moderado)
        if is_home:
            total_xg *= self.HOME_ADVANTAGE
        
        # Limitar xG a valores realistas (0-5 por time por jogo)
        total_xg = min(total_xg, 5.0)
        
        # Calcular Expected Assists (simplificado)
        expected_assists = total_xg * 0.7  # Assumindo que 70% dos gols têm assistência
        
        # Calcular Expected Points (simplificado)
        # Baseado na relação entre xG e probabilidade de vitória
        expected_points = self._calculate_expected_points(total_xg)
        
        # Dados reais para comparação
        actual_goals = len(goals)
        actual_assists = len([g for g in goals if g.get('assist_id')])
        
        return ExpectedGoalsResult(
            fixture_id=fixture_id,
            team_id=team_id,
            expected_goals=round(total_xg, 2),
            expected_assists=round(expected_assists, 2),
            expected_points=round(expected_points, 2),
            actual_goals=actual_goals,
            actual_assists=actual_assists,
            shots_total=shots_total,
            shots_inside_box=shots_inside_box or 0,
            shots_outside_box=shots_outside_box or 0,
            penalties_taken=penalties_taken,
            big_chances=0  # Não temos dados de big chances ainda
        )
    
    def _calculate_xg_from_shots(self, 
                                shots_total: int, 
                                shots_inside_box: int, 
                                shots_outside_box: int) -> float:
        """Calcula xG baseado em chutes"""
        
        if shots_total <= 0:
            return 0.0
        
        # Se temos dados detalhados de inside/outside box
        if shots_inside_box is not None and shots_outside_box is not None:
            xg_inside = shots_inside_box * self.SHOT_TO_GOAL_RATE * self.INSIDE_BOX_MULTIPLIER
            xg_outside = shots_outside_box * self.SHOT_TO_GOAL_RATE * self.OUTSIDE_BOX_MULTIPLIER
            return xg_inside + xg_outside
        
        # Caso contrário, usar cálculo simplificado baseado no total
        # Fator de conversão mais conservador quando não temos dados detalhados
        return shots_total * self.SHOT_TO_GOAL_RATE * 0.8  # Fator de redução para incerteza
    
    def _calculate_expected_points(self, xg: float) -> float:
        """
        Calcula Expected Points baseado em xG
        Fórmula simplificada baseada na distribuição de Poisson
        """
        
        if xg <= 0:
            return 0.0
        
        # Assumindo que o adversário tem xG médio de 1.2
        opponent_xg = 1.2
        
        # Probabilidades aproximadas usando distribuição de Poisson simplificada
        # P(vitória) ≈ xG / (xG + opponent_xG + 0.5)
        # P(empate) ≈ 0.3 (constante aproximada)
        # P(derrota) = 1 - P(vitória) - P(empate)
        
        prob_win = xg / (xg + opponent_xg + 0.5)
        prob_draw = 0.3
        prob_loss = max(0, 1 - prob_win - prob_draw)
        
        # Normalizar probabilidades
        total_prob = prob_win + prob_draw + prob_loss
        prob_win /= total_prob
        prob_draw /= total_prob
        prob_loss /= total_prob
        
        # Expected Points = 3 * P(win) + 1 * P(draw) + 0 * P(loss)
        expected_points = 3 * prob_win + 1 * prob_draw
        
        return max(0, min(3, expected_points))  # Limitar entre 0 e 3
    
    def calculate_player_xg(self, 
                           fixture_id: int, 
                           player_id: int, 
                           team_id: int,
                           goals: List[Dict] = None,
                           assists: List[Dict] = None,
                           penalties: List[Dict] = None) -> ExpectedGoalsResult:
        """
        Calcula xG para um jogador específico
        Versão simplificada baseada em eventos
        """
        
        if goals is None:
            goals = []
        if assists is None:
            assists = []
        if penalties is None:
            penalties = []
        
        # xG baseado em gols marcados (assumindo que se marcou, tinha chance)
        player_goals = len(goals)
        
        # Estimativa simples: cada gol representa aproximadamente 2-3 chances
        estimated_shots = player_goals * 2.5 if player_goals > 0 else 0
        
        # xG de pênaltis
        player_penalties = len(penalties)
        xg_penalties = player_penalties * self.PENALTY_CONVERSION_RATE
        
        # xG de jogadas normais (estimativa conservadora)
        xg_open_play = estimated_shots * self.SHOT_TO_GOAL_RATE * 1.2  # Multiplicador para jogadores que finalizam
        
        total_xg = xg_open_play + xg_penalties
        
        # Expected Assists baseado em assistências reais
        player_assists = len(assists)
        expected_assists = player_assists * 1.1  # Ligeiramente maior que o real
        
        return ExpectedGoalsResult(
            fixture_id=fixture_id,
            team_id=team_id,
            player_id=player_id,
            expected_goals=round(total_xg, 2),
            expected_assists=round(expected_assists, 2),
            expected_points=0.0,  # Não calculamos pontos para jogadores
            actual_goals=player_goals,
            actual_assists=player_assists,
            shots_total=int(estimated_shots),
            penalties_taken=player_penalties,
            calculation_method="basic_algorithm_v1_player"
        )
    
    def validate_calculation(self, result: ExpectedGoalsResult) -> Dict[str, float]:
        """
        Valida a qualidade do cálculo xG
        Retorna métricas de accuracy
        """
        
        metrics = {}
        
        # Goal Efficiency (actual / expected)
        if result.expected_goals > 0:
            metrics['goal_efficiency'] = (result.actual_goals / result.expected_goals) * 100
        else:
            metrics['goal_efficiency'] = 0.0
        
        # Performance Index (diferença absoluta)
        metrics['performance_index'] = (result.actual_goals - result.expected_goals) * 100
        
        # Assist Efficiency
        if result.expected_assists > 0:
            metrics['assist_efficiency'] = (result.actual_assists / result.expected_assists) * 100
        else:
            metrics['assist_efficiency'] = 0.0
        
        # Accuracy Score (quão próximo o xG ficou do real)
        max_diff = max(result.actual_goals, result.expected_goals, 1)  # Evitar divisão por 0
        accuracy = max(0, 100 - (abs(result.actual_goals - result.expected_goals) / max_diff * 100))
        metrics['accuracy_score'] = accuracy
        
        return metrics
