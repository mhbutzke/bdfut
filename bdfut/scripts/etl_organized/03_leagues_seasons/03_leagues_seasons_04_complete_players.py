#!/usr/bin/env python3
"""
03_leagues_seasons_04_complete_players.py
=========================================

Script para coleta completa de players de todos os teams
TASK-ETL-008: Expandir de 659 para 22.000+ players

DEPENDÊNCIAS:
- TASK-ETL-007 concluída
- Sistema de cache Redis funcionando
- Tabelas de metadados ETL criadas
- Teams já populados no banco

FUNCIONALIDADE:
- Coleta players de todos os 882 teams
- Sistema de metadados ETL para rastreamento
- Cache Redis para otimização
- Checkpoints para retomada automática
- Validação de dados integrada
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple
from tqdm import tqdm

# Adicionar o diretório bdfut ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from bdfut.core.sportmonks_client import SportmonksClient
from bdfut.core.supabase_client import SupabaseClient
from bdfut.core.etl_metadata import ETLMetadataManager, ETLJobContext

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'bdfut/logs/complete_players_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CompletePlayersManager:
    """Gerenciador de coleta completa de players"""
    
    def __init__(self, use_redis: bool = True, batch_size: int = 50):
        """
        Inicializa o gerenciador de coleta de players
        
        Args:
            use_redis: Usar cache Redis
            batch_size: Tamanho do batch para processamento
        """
        self.sportmonks = SportmonksClient(
            enable_cache=True,
            use_redis=use_redis,
            cache_ttl_hours=12  # TTL médio para players
        )
        self.supabase = SupabaseClient()
        self.metadata_manager = ETLMetadataManager()
        self.batch_size = batch_size
        
        # Estatísticas
        self.total_teams_processed = 0
        self.total_players_collected = 0
        self.total_api_requests = 0
        self.total_errors = 0
        
        logger.info(f"✅ CompletePlayersManager inicializado")
        logger.info(f"📊 Batch size: {batch_size}")
        logger.info(f"📊 Cache Redis: {use_redis}")
    
    def get_teams_for_player_collection(self) -> List[Dict]:
        """
        Obtém lista de teams para coleta de players
        
        Returns:
            Lista de teams com sportmonks_id
        """
        try:
            logger.info("🔍 Buscando teams para coleta de players...")
            
            # Buscar teams do banco
            result = self.supabase.client.table('teams').select('sportmonks_id, name').not_.is_('sportmonks_id', 'null').order('id').execute()
            
            teams = result.data if result.data else []
            
            logger.info(f"✅ {len(teams)} teams encontrados para coleta de players")
            
            # Mostrar alguns exemplos
            for i, team in enumerate(teams[:5]):
                logger.info(f"  📊 {i+1}. {team['name']} (ID: {team['sportmonks_id']})")
            
            if len(teams) > 5:
                logger.info(f"  📊 ... e mais {len(teams) - 5} teams")
            
            return teams
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar teams: {e}")
            return []
    
    def collect_team_players(self, team_id: int, team_name: str) -> Dict[str, Any]:
        """
        Coleta players de um team específico
        
        Args:
            team_id: ID do team na Sportmonks
            team_name: Nome do team
            
        Returns:
            Estatísticas da coleta
        """
        stats = {
            'team_id': team_id,
            'team_name': team_name,
            'players_found': 0,
            'players_saved': 0,
            'api_requests': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        try:
            logger.debug(f"👥 Coletando players do team {team_name} (ID: {team_id})")
            
            # Buscar players do team
            players = self.sportmonks.get_players_by_team(
                team_id=team_id,
                include='position'
            )
            
            stats['api_requests'] = 1
            stats['players_found'] = len(players) if players else 0
            
            if players:
                # Salvar players no banco
                success = self.supabase.upsert_players(players)
                
                if success:
                    stats['players_saved'] = len(players)
                    logger.debug(f"✅ {len(players)} players salvos para {team_name}")
                else:
                    stats['errors'] = len(players)
                    logger.error(f"❌ Erro ao salvar players do {team_name}")
            else:
                logger.warning(f"⚠️ Nenhum player encontrado para {team_name}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar players do team {team_name}: {e}")
            stats['errors'] = 1
        
        stats['end_time'] = datetime.now()
        stats['duration_seconds'] = int((stats['end_time'] - stats['start_time']).total_seconds())
        
        return stats
    
    def run_complete_players_collection(self) -> Dict[str, Any]:
        """
        Executa a coleta completa de players
        
        Returns:
            Estatísticas completas da coleta
        """
        with ETLJobContext(
            job_name="complete_players_collection",
            job_type="leagues_seasons",
            metadata_manager=self.metadata_manager,
            script_path=__file__,
            input_parameters={
                "target": "all_teams_players",
                "batch_size": self.batch_size
            }
        ) as job:
            
            logger.info("👥 INICIANDO COLETA COMPLETA DE PLAYERS")
            logger.info("=" * 60)
            job.log("INFO", "Iniciando coleta completa de players")
            
            overall_stats = {
                'start_time': datetime.now(),
                'teams_processed': 0,
                'total_players_collected': 0,
                'total_api_requests': 0,
                'total_errors': 0,
                'teams_with_players': 0,
                'teams_without_players': 0,
                'team_details': [],
                'success': False
            }
            
            try:
                # Obter lista de teams
                teams = self.get_teams_for_player_collection()
                
                if not teams:
                    logger.error("❌ Nenhum team encontrado para coleta")
                    return overall_stats
                
                logger.info(f"🎯 Meta: Coletar players de {len(teams)} teams")
                logger.info(f"📊 Estimativa: ~25 players/team = ~{len(teams) * 25:,} players")
                
                # Checkpoint inicial
                job.checkpoint(
                    name="teams_loaded",
                    data={
                        "total_teams": len(teams),
                        "target_players": len(teams) * 25
                    },
                    progress_percentage=5.0
                )
                
                # Processar teams em batches
                total_batches = (len(teams) + self.batch_size - 1) // self.batch_size
                
                logger.info(f"📦 Processando em {total_batches} batches de {self.batch_size} teams")
                
                for batch_idx in range(total_batches):
                    start_idx = batch_idx * self.batch_size
                    end_idx = min(start_idx + self.batch_size, len(teams))
                    batch_teams = teams[start_idx:end_idx]
                    
                    logger.info(f"\n📦 Batch {batch_idx + 1}/{total_batches}: Processando teams {start_idx + 1}-{end_idx}")
                    
                    batch_stats = {
                        'teams_processed': 0,
                        'players_collected': 0,
                        'api_requests': 0,
                        'errors': 0
                    }
                    
                    # Processar cada team do batch
                    for team in tqdm(batch_teams, desc=f"Batch {batch_idx + 1}"):
                        team_id = team['sportmonks_id']
                        team_name = team['name']
                        
                        # Coletar players do team
                        team_stats = self.collect_team_players(team_id, team_name)
                        
                        # Atualizar estatísticas do batch
                        batch_stats['teams_processed'] += 1
                        batch_stats['players_collected'] += team_stats['players_saved']
                        batch_stats['api_requests'] += team_stats['api_requests']
                        batch_stats['errors'] += team_stats['errors']
                        
                        # Atualizar job
                        job.increment_api_requests(team_stats['api_requests'])
                        job.increment_records(
                            processed=team_stats['players_found'],
                            inserted=team_stats['players_saved'],
                            failed=team_stats['errors']
                        )
                        
                        # Contabilizar teams com/sem players
                        if team_stats['players_saved'] > 0:
                            overall_stats['teams_with_players'] += 1
                        else:
                            overall_stats['teams_without_players'] += 1
                        
                        # Salvar detalhes do team
                        overall_stats['team_details'].append(team_stats)
                        
                        # Pausa mínima entre teams
                        time.sleep(0.1)
                    
                    # Atualizar estatísticas gerais
                    overall_stats['teams_processed'] += batch_stats['teams_processed']
                    overall_stats['total_players_collected'] += batch_stats['players_collected']
                    overall_stats['total_api_requests'] += batch_stats['api_requests']
                    overall_stats['total_errors'] += batch_stats['errors']
                    
                    # Checkpoint de batch
                    progress = ((batch_idx + 1) / total_batches) * 90 + 5  # 5-95%
                    job.checkpoint(
                        name=f"batch_{batch_idx + 1}_completed",
                        data={
                            "batch_index": batch_idx + 1,
                            "total_batches": total_batches,
                            "batch_stats": batch_stats,
                            "overall_progress": overall_stats
                        },
                        progress_percentage=progress
                    )
                    
                    logger.info(f"✅ Batch {batch_idx + 1} concluído:")
                    logger.info(f"  📊 Teams processados: {batch_stats['teams_processed']}")
                    logger.info(f"  👥 Players coletados: {batch_stats['players_collected']}")
                    logger.info(f"  🌐 Requisições API: {batch_stats['api_requests']}")
                    logger.info(f"  ❌ Erros: {batch_stats['errors']}")
                    
                    # Pausa entre batches
                    time.sleep(1.0)
                
                # Finalizar coleta
                overall_stats['end_time'] = datetime.now()
                overall_stats['duration_seconds'] = int((overall_stats['end_time'] - overall_stats['start_time']).total_seconds())
                overall_stats['success'] = True
                
                logger.info("\n" + "=" * 60)
                logger.info("🎉 COLETA COMPLETA DE PLAYERS CONCLUÍDA!")
                logger.info("=" * 60)
                logger.info(f"📊 Teams processados: {overall_stats['teams_processed']}")
                logger.info(f"👥 Players coletados: {overall_stats['total_players_collected']:,}")
                logger.info(f"🌐 Requisições API: {overall_stats['total_api_requests']:,}")
                logger.info(f"✅ Teams com players: {overall_stats['teams_with_players']}")
                logger.info(f"⚠️ Teams sem players: {overall_stats['teams_without_players']}")
                logger.info(f"❌ Erros: {overall_stats['total_errors']}")
                logger.info(f"⏱️ Duração: {overall_stats['duration_seconds']}s ({overall_stats['duration_seconds']//60}min)")
                
                # Calcular estatísticas
                avg_players_per_team = overall_stats['total_players_collected'] / max(overall_stats['teams_processed'], 1)
                success_rate = (overall_stats['teams_processed'] - overall_stats['total_errors']) / max(overall_stats['teams_processed'], 1)
                
                logger.info(f"📈 Média de players/team: {avg_players_per_team:.1f}")
                logger.info(f"📈 Taxa de sucesso: {success_rate:.1%}")
                
                job.log("INFO", f"Coleta concluída - {overall_stats['total_players_collected']:,} players coletados")
                
                # Checkpoint final
                job.checkpoint(
                    name="players_collection_completed",
                    data=overall_stats,
                    progress_percentage=100.0
                )
                
                return overall_stats
                
            except Exception as e:
                logger.error(f"❌ Erro durante coleta de players: {e}")
                overall_stats['success'] = False
                overall_stats['error'] = str(e)
                job.log("ERROR", f"Erro durante coleta: {e}")
                return overall_stats
    
    def validate_players_data(self) -> Dict[str, Any]:
        """
        Valida os dados de players coletados
        
        Returns:
            Relatório de validação
        """
        logger.info("🔍 Validando dados de players...")
        
        validation_report = {
            'total_players': 0,
            'players_with_position': 0,
            'players_with_nationality': 0,
            'players_with_birth_date': 0,
            'teams_represented': 0,
            'positions_covered': [],
            'nationalities_covered': [],
            'data_quality_score': 0.0,
            'issues_found': []
        }
        
        try:
            # Contar players total
            result = self.supabase.client.table('players').select('id', count='exact').execute()
            validation_report['total_players'] = result.count if result.count is not None else 0
            
            logger.info(f"📊 Total de players no banco: {validation_report['total_players']:,}")
            
            # Validações específicas (implementação simplificada)
            if validation_report['total_players'] >= 22000:
                validation_report['data_quality_score'] = 0.95
                logger.info("✅ Meta de 22.000+ players atingida!")
            elif validation_report['total_players'] >= 15000:
                validation_report['data_quality_score'] = 0.80
                logger.info("✅ Boa cobertura de players (15k+)")
            else:
                validation_report['data_quality_score'] = 0.60
                validation_report['issues_found'].append(f"Players insuficientes: {validation_report['total_players']} < 22.000")
            
            return validation_report
            
        except Exception as e:
            logger.error(f"❌ Erro durante validação: {e}")
            validation_report['issues_found'].append(f"Erro de validação: {e}")
            return validation_report
    
    def generate_players_report(self, stats: Dict[str, Any], validation: Dict[str, Any]) -> str:
        """
        Gera relatório completo da coleta de players
        
        Args:
            stats: Estatísticas da coleta
            validation: Relatório de validação
            
        Returns:
            Relatório formatado
        """
        report_lines = [
            "=" * 80,
            "👥 RELATÓRIO FINAL DA COLETA COMPLETA DE PLAYERS",
            "=" * 80,
            "",
            f"🕒 Executado em: {stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"⏱️ Duração: {stats.get('duration_seconds', 0)}s ({stats.get('duration_seconds', 0)//60}min)",
            f"✅ Status: {'SUCESSO' if stats.get('success', False) else 'FALHA'}",
            "",
            "📈 ESTATÍSTICAS GERAIS:",
            f"  • Teams processados: {stats.get('teams_processed', 0)}/882",
            f"  • Players coletados: {stats.get('total_players_collected', 0):,}",
            f"  • Requisições à API: {stats.get('total_api_requests', 0):,}",
            f"  • Teams com players: {stats.get('teams_with_players', 0)}",
            f"  • Teams sem players: {stats.get('teams_without_players', 0)}",
            f"  • Erros encontrados: {stats.get('total_errors', 0)}",
            "",
            "📊 MÉTRICAS DE PERFORMANCE:",
            f"  • Média players/team: {stats.get('total_players_collected', 0) / max(stats.get('teams_processed', 1), 1):.1f}",
            f"  • Taxa de sucesso: {(stats.get('teams_processed', 0) - stats.get('total_errors', 0)) / max(stats.get('teams_processed', 1), 1):.1%}",
            f"  • Velocidade: {stats.get('total_players_collected', 0) / max(stats.get('duration_seconds', 1), 1):.1f} players/segundo",
            "",
            "🔍 VALIDAÇÃO DE DADOS:",
            f"  • Total no banco: {validation.get('total_players', 0):,}",
            f"  • Score de qualidade: {validation.get('data_quality_score', 0):.1%}",
        ]
        
        # Top 10 teams com mais players
        if stats.get('team_details'):
            sorted_teams = sorted(stats['team_details'], key=lambda x: x['players_saved'], reverse=True)
            report_lines.extend([
                "",
                "🏆 TOP 10 TEAMS COM MAIS PLAYERS:",
            ])
            for i, team in enumerate(sorted_teams[:10], 1):
                report_lines.append(f"  {i:2d}. {team['team_name']}: {team['players_saved']} players")
        
        # Problemas encontrados
        if validation.get('issues_found'):
            report_lines.extend([
                "",
                "⚠️ PROBLEMAS ENCONTRADOS:",
            ])
            for issue in validation['issues_found']:
                report_lines.append(f"  • {issue}")
        
        # Recomendações
        report_lines.extend([
            "",
            "💡 RECOMENDAÇÕES:",
            f"  • Meta de 22.000 players: {'✅ ATINGIDA' if validation.get('total_players', 0) >= 22000 else '❌ NÃO ATINGIDA'}",
            f"  • Cobertura de teams: {stats.get('teams_with_players', 0)}/{stats.get('teams_processed', 0)} ({(stats.get('teams_with_players', 0) / max(stats.get('teams_processed', 1), 1)):.1%})",
            f"  • Próximo passo: {'Iniciar TASK-ETL-009' if validation.get('total_players', 0) >= 15000 else 'Revisar coleta de players'}",
            "",
            "=" * 80
        ])
        
        return "\n".join(report_lines)


def main():
    """Função principal da coleta de players"""
    print("👥 COLETA COMPLETA DE PLAYERS - TASK-ETL-008")
    print("=" * 60)
    
    try:
        # Inicializar gerenciador
        players_manager = CompletePlayersManager(
            use_redis=True,
            batch_size=50  # 50 teams por batch
        )
        
        # Executar coleta
        print("🔄 Executando coleta completa de players...")
        stats = players_manager.run_complete_players_collection()
        
        # Validar dados
        print("🔍 Validando dados de players...")
        validation = players_manager.validate_players_data()
        
        # Gerar relatório
        print("📊 Gerando relatório final...")
        report = players_manager.generate_players_report(stats, validation)
        
        # Salvar relatório
        report_file = f"bdfut/logs/players_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"💾 Relatório salvo: {report_file}")
        print("\n" + report)
        
        # Verificar critérios de sucesso
        success_criteria = [
            ("Coleta executada", stats.get('success', False)),
            ("Meta de 22.000+ players", validation.get('total_players', 0) >= 22000),
            ("Pelo menos 15.000 players", validation.get('total_players', 0) >= 15000),
            ("80%+ teams processados", stats.get('teams_processed', 0) >= (882 * 0.8)),
            ("Taxa de erro < 10%", (stats.get('total_errors', 0) / max(stats.get('teams_processed', 1), 1)) < 0.1)
        ]
        
        print("\n✅ CRITÉRIOS DE SUCESSO:")
        all_passed = True
        for criterion, passed in success_criteria:
            status = "✅" if passed else "❌"
            print(f"  {status} {criterion}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 TASK-ETL-008 CONCLUÍDA COM SUCESSO!")
            print("🚀 Pronto para iniciar TASK-ETL-009")
            return True
        else:
            print("\n⚠️ TASK-ETL-008 CONCLUÍDA COM PROBLEMAS")
            print("🔧 Revisar coleta antes de prosseguir")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro fatal durante coleta de players: {e}")
        print(f"❌ Erro fatal: {e}")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {str(e)}")
        sys.exit(1)
