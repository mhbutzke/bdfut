#!/usr/bin/env python3
"""
04_fixtures_events_07_current_season_complete.py
================================================

Script para completar fixtures das temporadas atuais
TASK-ETL-009: Completar fixtures das temporadas 2025/2026 (100% cobertura atual)

DEPENDÊNCIAS:
- TASK-ETL-008 concluída
- Sistema de cache Redis funcionando
- Tabelas de metadados ETL criadas
- Fixtures básicas já populadas

FUNCIONALIDADE:
- Completar dados de fixtures das temporadas atuais
- Atualizar status, scores, participants, venue
- Coletar fixtures futuras (próximos 6 meses)
- Sistema de metadados ETL para rastreamento
- Cache Redis para otimização
- Checkpoints para retomada automática
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
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
        logging.FileHandler(f'bdfut/logs/current_season_fixtures_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CurrentSeasonFixturesManager:
    """Gerenciador de coleta completa de fixtures das temporadas atuais"""
    
    def __init__(self, use_redis: bool = True, batch_size: int = 100):
        """
        Inicializa o gerenciador de fixtures atuais
        
        Args:
            use_redis: Usar cache Redis
            batch_size: Tamanho do batch para processamento
        """
        self.sportmonks = SportmonksClient(
            enable_cache=True,
            use_redis=use_redis,
            cache_ttl_hours=2  # TTL curto para fixtures (dados dinâmicos)
        )
        self.supabase = SupabaseClient()
        self.metadata_manager = ETLMetadataManager()
        self.batch_size = batch_size
        
        # Estatísticas
        self.total_fixtures_processed = 0
        self.total_fixtures_updated = 0
        self.total_api_requests = 0
        self.total_errors = 0
        
        logger.info(f"✅ CurrentSeasonFixturesManager inicializado")
        logger.info(f"📊 Batch size: {batch_size}")
        logger.info(f"📊 Cache Redis: {use_redis}")
    
    def get_current_seasons(self) -> List[Dict]:
        """
        Obtém lista de temporadas atuais
        
        Returns:
            Lista de temporadas atuais com suas ligas
        """
        try:
            logger.info("🔍 Buscando temporadas atuais...")
            
            # Buscar temporadas atuais
            result = self.supabase.client.table('seasons').select(
                'sportmonks_id, name, is_current, finished, league_id, leagues(name)'
            ).eq('is_current', True).execute()
            
            seasons = result.data if result.data else []
            
            logger.info(f"✅ {len(seasons)} temporadas atuais encontradas")
            
            # Mostrar algumas temporadas
            for i, season in enumerate(seasons[:5]):
                league_name = season.get('leagues', {}).get('name', 'Unknown')
                logger.info(f"  📊 {i+1}. {league_name} - {season['name']}")
            
            if len(seasons) > 5:
                logger.info(f"  📊 ... e mais {len(seasons) - 5} temporadas")
            
            return seasons
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar temporadas atuais: {e}")
            return []
    
    def get_fixtures_to_update(self, season_id: int, season_name: str) -> List[Dict]:
        """
        Obtém fixtures que precisam ser atualizadas para uma temporada
        
        Args:
            season_id: ID da temporada na Sportmonks
            season_name: Nome da temporada
            
        Returns:
            Lista de fixtures que precisam atualização
        """
        try:
            logger.debug(f"🔍 Buscando fixtures para atualização: {season_name}")
            
            # Buscar fixtures da temporada que precisam de atualização
            # (sem status, sem scores, sem participants detalhados)
            result = self.supabase.client.table('fixtures').select(
                'sportmonks_id, match_date, status, home_score, away_score'
            ).eq('season_id', season_id).execute()
            
            fixtures = result.data if result.data else []
            
            # Filtrar fixtures que precisam de atualização
            fixtures_to_update = []
            for fixture in fixtures:
                needs_update = (
                    not fixture.get('status') or 
                    fixture.get('status') == '' or
                    (fixture.get('home_score') is None and fixture.get('status') == 'Finished')
                )
                
                if needs_update:
                    fixtures_to_update.append(fixture)
            
            logger.debug(f"📊 {len(fixtures_to_update)}/{len(fixtures)} fixtures precisam atualização")
            return fixtures_to_update
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixtures para {season_name}: {e}")
            return []
    
    def update_fixture_details(self, fixture_id: int, season_name: str) -> Dict[str, Any]:
        """
        Atualiza detalhes de uma fixture específica
        
        Args:
            fixture_id: ID da fixture na Sportmonks
            season_name: Nome da temporada (para logs)
            
        Returns:
            Estatísticas da atualização
        """
        stats = {
            'fixture_id': fixture_id,
            'season_name': season_name,
            'updated': False,
            'api_requests': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        try:
            logger.debug(f"🔄 Atualizando fixture {fixture_id} ({season_name})")
            
            # Buscar detalhes completos da fixture
            fixture_details = self.sportmonks.get_fixture_by_id(
                fixture_id=fixture_id
            )
            
            stats['api_requests'] = 1
            
            if fixture_details:
                # Atualizar fixture no banco
                success = self.supabase.upsert_fixtures([fixture_details])
                
                if success:
                    stats['updated'] = True
                    logger.debug(f"✅ Fixture {fixture_id} atualizada")
                else:
                    stats['errors'] = 1
                    logger.error(f"❌ Erro ao atualizar fixture {fixture_id}")
            else:
                logger.warning(f"⚠️ Fixture {fixture_id} não encontrada na API")
                stats['errors'] = 1
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar fixture {fixture_id}: {e}")
            stats['errors'] = 1
        
        stats['end_time'] = datetime.now()
        stats['duration_seconds'] = int((stats['end_time'] - stats['start_time']).total_seconds())
        
        return stats
    
    def collect_future_fixtures(self, season_id: int, season_name: str, months_ahead: int = 6) -> Dict[str, Any]:
        """
        Coleta fixtures futuras para uma temporada
        
        Args:
            season_id: ID da temporada na Sportmonks
            season_name: Nome da temporada
            months_ahead: Meses à frente para coletar
            
        Returns:
            Estatísticas da coleta
        """
        stats = {
            'season_id': season_id,
            'season_name': season_name,
            'fixtures_collected': 0,
            'api_requests': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        try:
            logger.info(f"🔮 Coletando fixtures futuras para {season_name} (próximos {months_ahead} meses)")
            
            # Calcular data limite
            end_date = datetime.now() + timedelta(days=months_ahead * 30)
            
            # Buscar fixtures futuras da temporada
            fixtures = self.sportmonks.get_fixtures_by_date_range(
                start_date=datetime.now().strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            stats['api_requests'] = 1
            stats['fixtures_collected'] = len(fixtures) if fixtures else 0
            
            if fixtures:
                # Salvar fixtures no banco
                success = self.supabase.upsert_fixtures(fixtures)
                
                if success:
                    logger.info(f"✅ {len(fixtures)} fixtures futuras coletadas para {season_name}")
                else:
                    stats['errors'] = len(fixtures)
                    logger.error(f"❌ Erro ao salvar fixtures futuras de {season_name}")
            else:
                logger.warning(f"⚠️ Nenhuma fixture futura encontrada para {season_name}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar fixtures futuras de {season_name}: {e}")
            stats['errors'] = 1
        
        stats['end_time'] = datetime.now()
        stats['duration_seconds'] = int((stats['end_time'] - stats['start_time']).total_seconds())
        
        return stats
    
    def run_current_season_completion(self) -> Dict[str, Any]:
        """
        Executa a completação das fixtures das temporadas atuais
        
        Returns:
            Estatísticas completas da operação
        """
        with ETLJobContext(
            job_name="current_season_fixtures_completion",
            job_type="fixtures_events",
            metadata_manager=self.metadata_manager,
            script_path=__file__,
            input_parameters={
                "target": "current_seasons_complete",
                "batch_size": self.batch_size,
                "months_ahead": 6
            }
        ) as job:
            
            logger.info("⚽ INICIANDO COMPLETÃO DE FIXTURES DAS TEMPORADAS ATUAIS")
            logger.info("=" * 70)
            job.log("INFO", "Iniciando completação de fixtures das temporadas atuais")
            
            overall_stats = {
                'start_time': datetime.now(),
                'seasons_processed': 0,
                'total_fixtures_updated': 0,
                'total_fixtures_collected': 0,
                'total_api_requests': 0,
                'total_errors': 0,
                'season_details': [],
                'success': False
            }
            
            try:
                # Obter temporadas atuais
                current_seasons = self.get_current_seasons()
                
                if not current_seasons:
                    logger.error("❌ Nenhuma temporada atual encontrada")
                    return overall_stats
                
                logger.info(f"🎯 Processando {len(current_seasons)} temporadas atuais")
                
                # Checkpoint inicial
                job.checkpoint(
                    name="current_seasons_loaded",
                    data={
                        "total_seasons": len(current_seasons),
                        "seasons": [s['name'] for s in current_seasons]
                    },
                    progress_percentage=5.0
                )
                
                # Processar cada temporada
                for i, season in enumerate(current_seasons):
                    season_id = season['sportmonks_id']
                    season_name = season['name']
                    league_name = season.get('leagues', {}).get('name', 'Unknown')
                    
                    logger.info(f"\n📅 Processando temporada {i+1}/{len(current_seasons)}: {league_name} - {season_name}")
                    
                    season_stats = {
                        'season_id': season_id,
                        'season_name': season_name,
                        'league_name': league_name,
                        'fixtures_updated': 0,
                        'fixtures_collected': 0,
                        'api_requests': 0,
                        'errors': 0
                    }
                    
                    try:
                        # 1. Atualizar fixtures existentes
                        logger.info(f"🔄 Atualizando fixtures existentes...")
                        fixtures_to_update = self.get_fixtures_to_update(season_id, season_name)
                        
                        if fixtures_to_update:
                            logger.info(f"📊 {len(fixtures_to_update)} fixtures precisam atualização")
                            
                            # Processar fixtures em batches
                            total_batches = (len(fixtures_to_update) + self.batch_size - 1) // self.batch_size
                            
                            for batch_idx in range(total_batches):
                                start_idx = batch_idx * self.batch_size
                                end_idx = min(start_idx + self.batch_size, len(fixtures_to_update))
                                batch_fixtures = fixtures_to_update[start_idx:end_idx]
                                
                                logger.info(f"📦 Batch {batch_idx + 1}/{total_batches}: Atualizando fixtures {start_idx + 1}-{end_idx}")
                                
                                for fixture in tqdm(batch_fixtures, desc=f"Batch {batch_idx + 1}"):
                                    fixture_id = fixture['sportmonks_id']
                                    
                                    # Atualizar detalhes da fixture
                                    update_stats = self.update_fixture_details(fixture_id, season_name)
                                    
                                    # Atualizar estatísticas
                                    season_stats['fixtures_updated'] += 1 if update_stats['updated'] else 0
                                    season_stats['api_requests'] += update_stats['api_requests']
                                    season_stats['errors'] += update_stats['errors']
                                    
                                    # Atualizar job
                                    job.increment_api_requests(update_stats['api_requests'])
                                    job.increment_records(
                                        processed=1,
                                        updated=1 if update_stats['updated'] else 0,
                                        failed=update_stats['errors']
                                    )
                                    
                                    # Pausa mínima entre fixtures
                                    time.sleep(0.1)
                                
                                # Pausa entre batches
                                time.sleep(1.0)
                        else:
                            logger.info(f"✅ Todas as fixtures de {season_name} já estão atualizadas")
                        
                        # 2. Coletar fixtures futuras
                        logger.info(f"🔮 Coletando fixtures futuras...")
                        future_stats = self.collect_future_fixtures(season_id, season_name, months_ahead=6)
                        
                        season_stats['fixtures_collected'] = future_stats['fixtures_collected']
                        season_stats['api_requests'] += future_stats['api_requests']
                        season_stats['errors'] += future_stats['errors']
                        
                        # Atualizar job
                        job.increment_api_requests(future_stats['api_requests'])
                        job.increment_records(
                            processed=future_stats['fixtures_collected'],
                            inserted=future_stats['fixtures_collected'],
                            failed=future_stats['errors']
                        )
                        
                        # Checkpoint de temporada
                        progress = ((i + 1) / len(current_seasons)) * 90 + 5  # 5-95%
                        job.checkpoint(
                            name=f"season_{season_id}_completed",
                            data={
                                "season_index": i + 1,
                                "total_seasons": len(current_seasons),
                                "season_stats": season_stats
                            },
                            progress_percentage=progress
                        )
                        
                        logger.info(f"✅ Temporada {season_name} concluída:")
                        logger.info(f"  📊 Fixtures atualizadas: {season_stats['fixtures_updated']}")
                        logger.info(f"  🔮 Fixtures futuras coletadas: {season_stats['fixtures_collected']}")
                        logger.info(f"  🌐 Requisições API: {season_stats['api_requests']}")
                        logger.info(f"  ❌ Erros: {season_stats['errors']}")
                        
                        # Atualizar estatísticas gerais
                        overall_stats['seasons_processed'] += 1
                        overall_stats['total_fixtures_updated'] += season_stats['fixtures_updated']
                        overall_stats['total_fixtures_collected'] += season_stats['fixtures_collected']
                        overall_stats['total_api_requests'] += season_stats['api_requests']
                        overall_stats['total_errors'] += season_stats['errors']
                        overall_stats['season_details'].append(season_stats)
                        
                    except Exception as e:
                        logger.error(f"❌ Erro crítico ao processar temporada {season_name}: {str(e)}")
                        season_stats['errors'] = 1
                        overall_stats['total_errors'] += 1
                        continue
                
                # Finalizar operação
                overall_stats['end_time'] = datetime.now()
                overall_stats['duration_seconds'] = int((overall_stats['end_time'] - overall_stats['start_time']).total_seconds())
                overall_stats['success'] = True
                
                logger.info("\n" + "=" * 70)
                logger.info("🎉 COMPLETÃO DE FIXTURES DAS TEMPORADAS ATUAIS CONCLUÍDA!")
                logger.info("=" * 70)
                logger.info(f"📊 Temporadas processadas: {overall_stats['seasons_processed']}")
                logger.info(f"🔄 Fixtures atualizadas: {overall_stats['total_fixtures_updated']:,}")
                logger.info(f"🔮 Fixtures futuras coletadas: {overall_stats['total_fixtures_collected']:,}")
                logger.info(f"🌐 Requisições API: {overall_stats['total_api_requests']:,}")
                logger.info(f"❌ Erros: {overall_stats['total_errors']}")
                logger.info(f"⏱️ Duração: {overall_stats['duration_seconds']}s ({overall_stats['duration_seconds']//60}min)")
                
                # Calcular estatísticas
                total_fixtures = overall_stats['total_fixtures_updated'] + overall_stats['total_fixtures_collected']
                success_rate = (overall_stats['seasons_processed'] - overall_stats['total_errors']) / max(overall_stats['seasons_processed'], 1)
                
                logger.info(f"📈 Total de fixtures processadas: {total_fixtures:,}")
                logger.info(f"📈 Taxa de sucesso: {success_rate:.1%}")
                
                job.log("INFO", f"Completão concluída - {total_fixtures:,} fixtures processadas")
                
                # Checkpoint final
                job.checkpoint(
                    name="current_seasons_completion_finished",
                    data=overall_stats,
                    progress_percentage=100.0
                )
                
                return overall_stats
                
            except Exception as e:
                logger.error(f"❌ Erro durante completação de fixtures: {e}")
                overall_stats['success'] = False
                overall_stats['error'] = str(e)
                job.log("ERROR", f"Erro durante completação: {e}")
                return overall_stats
    
    def validate_current_season_data(self) -> Dict[str, Any]:
        """
        Valida os dados das temporadas atuais
        
        Returns:
            Relatório de validação
        """
        logger.info("🔍 Validando dados das temporadas atuais...")
        
        validation_report = {
            'total_current_seasons': 0,
            'seasons_with_fixtures': 0,
            'total_fixtures_current': 0,
            'fixtures_with_status': 0,
            'fixtures_with_scores': 0,
            'fixtures_future': 0,
            'data_quality_score': 0.0,
            'issues_found': []
        }
        
        try:
            # Contar temporadas atuais
            result = self.supabase.client.table('seasons').select('id', count='exact').eq('is_current', True).execute()
            validation_report['total_current_seasons'] = result.count if result.count is not None else 0
            
            # Contar fixtures das temporadas atuais
            result = self.supabase.client.table('fixtures').select(
                'id, status, home_score, away_score, match_date'
            ).execute()
            
            fixtures = result.data if result.data else []
            validation_report['total_fixtures_current'] = len(fixtures)
            
            # Validações específicas
            for fixture in fixtures:
                if fixture.get('status'):
                    validation_report['fixtures_with_status'] += 1
                
                if fixture.get('home_score') is not None and fixture.get('away_score') is not None:
                    validation_report['fixtures_with_scores'] += 1
                
                if fixture.get('match_date'):
                    match_date = datetime.fromisoformat(fixture['match_date'].replace('Z', '+00:00'))
                    if match_date > datetime.now():
                        validation_report['fixtures_future'] += 1
            
            # Calcular score de qualidade
            if validation_report['total_fixtures_current'] > 0:
                status_coverage = validation_report['fixtures_with_status'] / validation_report['total_fixtures_current']
                scores_coverage = validation_report['fixtures_with_scores'] / validation_report['total_fixtures_current']
                future_coverage = validation_report['fixtures_future'] / validation_report['total_fixtures_current']
                
                validation_report['data_quality_score'] = (status_coverage + scores_coverage + future_coverage) / 3
            
            logger.info(f"📊 Temporadas atuais: {validation_report['total_current_seasons']}")
            logger.info(f"📊 Fixtures totais: {validation_report['total_fixtures_current']:,}")
            logger.info(f"📊 Com status: {validation_report['fixtures_with_status']:,}")
            logger.info(f"📊 Com scores: {validation_report['fixtures_with_scores']:,}")
            logger.info(f"📊 Futuras: {validation_report['fixtures_future']:,}")
            logger.info(f"📊 Score de qualidade: {validation_report['data_quality_score']:.1%}")
            
            return validation_report
            
        except Exception as e:
            logger.error(f"❌ Erro durante validação: {e}")
            validation_report['issues_found'].append(f"Erro de validação: {e}")
            return validation_report


def main():
    """Função principal da completação de fixtures atuais"""
    print("⚽ COMPLETÃO DE FIXTURES DAS TEMPORADAS ATUAIS - TASK-ETL-009")
    print("=" * 70)
    
    try:
        # Inicializar gerenciador
        fixtures_manager = CurrentSeasonFixturesManager(
            use_redis=True,
            batch_size=100  # 100 fixtures por batch
        )
        
        # Executar completação
        print("🔄 Executando completação de fixtures das temporadas atuais...")
        stats = fixtures_manager.run_current_season_completion()
        
        # Validar dados
        print("🔍 Validando dados das temporadas atuais...")
        validation = fixtures_manager.validate_current_season_data()
        
        print(f"\n📊 RESULTADO:")
        print(f"  • Temporadas processadas: {stats.get('seasons_processed', 0)}")
        print(f"  • Fixtures atualizadas: {stats.get('total_fixtures_updated', 0):,}")
        print(f"  • Fixtures futuras coletadas: {stats.get('total_fixtures_collected', 0):,}")
        print(f"  • Requisições API: {stats.get('total_api_requests', 0):,}")
        print(f"  • Erros: {stats.get('total_errors', 0)}")
        print(f"  • Score de qualidade: {validation.get('data_quality_score', 0):.1%}")
        
        # Verificar critérios de sucesso
        success_criteria = [
            ("Completação executada", stats.get('success', False)),
            ("Temporadas processadas", stats.get('seasons_processed', 0) > 0),
            ("Fixtures atualizadas", stats.get('total_fixtures_updated', 0) > 0),
            ("Score de qualidade > 80%", validation.get('data_quality_score', 0) > 0.8),
            ("Taxa de erro < 10%", (stats.get('total_errors', 0) / max(stats.get('total_api_requests', 1), 1)) < 0.1)
        ]
        
        print("\n✅ CRITÉRIOS DE SUCESSO:")
        all_passed = True
        for criterion, passed in success_criteria:
            status = "✅" if passed else "❌"
            print(f"  {status} {criterion}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 TASK-ETL-009 CONCLUÍDA COM SUCESSO!")
            print("🚀 Pronto para iniciar TASK-ETL-010")
            return True
        else:
            print("\n⚠️ TASK-ETL-009 CONCLUÍDA COM PROBLEMAS")
            print("🔧 Revisar completação antes de prosseguir")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro fatal durante completação de fixtures: {e}")
        print(f"❌ Erro fatal: {e}")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {str(e)}")
        sys.exit(1)
