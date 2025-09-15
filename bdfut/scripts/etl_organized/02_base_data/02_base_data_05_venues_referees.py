#!/usr/bin/env python3
"""
02_base_data_05_venues_referees.py
==================================

Script para coleta completa de venues e referees
TASK-ETL-010: Expandir venues (106 → 500+) e referees (35 → 200+)

DEPENDÊNCIAS:
- TASK-ETL-009 concluída
- Sistema de cache Redis funcionando
- Tabelas de metadados ETL criadas

FUNCIONALIDADE:
- Coletar venues de todas as ligas ativas
- Coletar referees de fixtures recentes
- Sistema de metadados ETL para rastreamento
- Cache Redis para otimização
- Checkpoints para retomada automática
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set
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
        logging.FileHandler(f'bdfut/logs/venues_referees_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VenuesRefereesManager:
    """Gerenciador de coleta completa de venues e referees"""
    
    def __init__(self, use_redis: bool = True, batch_size: int = 50):
        """
        Inicializa o gerenciador de venues e referees
        
        Args:
            use_redis: Usar cache Redis
            batch_size: Tamanho do batch para processamento
        """
        self.sportmonks = SportmonksClient(
            enable_cache=True,
            use_redis=use_redis,
            cache_ttl_hours=24  # TTL longo para venues/referees (dados mais estáveis)
        )
        self.supabase = SupabaseClient()
        self.metadata_manager = ETLMetadataManager()
        self.batch_size = batch_size
        
        # Estatísticas
        self.total_venues_collected = 0
        self.total_referees_collected = 0
        self.total_api_requests = 0
        self.total_errors = 0
        
        logger.info(f"✅ VenuesRefereesManager inicializado")
        logger.info(f"📊 Batch size: {batch_size}")
        logger.info(f"📊 Cache Redis: {use_redis}")
    
    def get_teams_for_venues(self) -> List[Dict]:
        """
        Obtém lista de teams para coletar venues
        
        Returns:
            Lista de teams com venue_id
        """
        try:
            logger.info("🏟️ Buscando teams para coleta de venues...")
            
            # Buscar teams que têm venue_id
            result = self.supabase.client.table('teams').select(
                'sportmonks_id, name, venue_id'
            ).not_.is_('venue_id', 'null').execute()
            
            teams = result.data if result.data else []
            
            logger.info(f"✅ {len(teams)} teams com venues encontrados")
            
            return teams
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar teams: {e}")
            return []
    
    def get_recent_fixtures_for_referees(self, days_back: int = 30) -> List[Dict]:
        """
        Obtém fixtures recentes para extrair referees
        
        Args:
            days_back: Dias para trás para buscar fixtures
            
        Returns:
            Lista de fixtures com referee_id
        """
        try:
            logger.info(f"👨‍⚖️ Buscando fixtures recentes para coleta de referees (últimos {days_back} dias)...")
            
            # Calcular data limite
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # Buscar fixtures recentes com referee_id
            result = self.supabase.client.table('fixtures').select(
                'sportmonks_id, name, referee_id'
            ).not_.is_('referee_id', 'null').gte('match_date', start_date).execute()
            
            fixtures = result.data if result.data else []
            
            logger.info(f"✅ {len(fixtures)} fixtures com referees encontradas")
            
            return fixtures
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixtures: {e}")
            return []
    
    def collect_venues_by_teams(self) -> Dict[str, Any]:
        """
        Coleta venues através dos teams
        
        Returns:
            Estatísticas da coleta de venues
        """
        stats = {
            'venues_found': 0,
            'venues_saved': 0,
            'teams_processed': 0,
            'api_requests': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        try:
            logger.info("🏟️ Coletando venues através dos teams...")
            
            teams = self.get_teams_for_venues()
            if not teams:
                logger.warning("⚠️ Nenhum team com venue_id encontrado")
                return stats
            
            # Extrair venue_ids únicos
            venue_ids = set()
            for team in teams:
                if team.get('venue_id'):
                    venue_ids.add(team['venue_id'])
            
            logger.info(f"🎯 {len(venue_ids)} venues únicos para coletar")
            
            # Buscar venues existentes
            existing_result = self.supabase.client.table('venues').select('sportmonks_id').execute()
            existing_venue_ids = set(v['sportmonks_id'] for v in existing_result.data) if existing_result.data else set()
            
            # Filtrar venues que ainda não temos
            new_venue_ids = venue_ids - existing_venue_ids
            logger.info(f"📊 {len(new_venue_ids)} venues novos para coletar")
            
            if not new_venue_ids:
                logger.info("✅ Todos os venues dos teams já estão no banco")
                return stats
            
            # Coletar venues em batches
            venue_ids_list = list(new_venue_ids)
            total_batches = (len(venue_ids_list) + self.batch_size - 1) // self.batch_size
            
            for batch_idx in range(total_batches):
                start_idx = batch_idx * self.batch_size
                end_idx = min(start_idx + self.batch_size, len(venue_ids_list))
                batch_venue_ids = venue_ids_list[start_idx:end_idx]
                
                logger.info(f"📦 Batch {batch_idx + 1}/{total_batches}: Coletando venues {start_idx + 1}-{end_idx}")
                
                for venue_id in tqdm(batch_venue_ids, desc=f"Venues Batch {batch_idx + 1}"):
                    try:
                        # Buscar venue por ID
                        venue = self.sportmonks.get_venue_by_id(venue_id)
                        stats['api_requests'] += 1
                        
                        if venue:
                            # Salvar venue no banco
                            success = self.supabase.upsert_venues([venue])
                            
                            if success:
                                stats['venues_saved'] += 1
                                logger.debug(f"✅ Venue {venue.get('name', venue_id)} salvo")
                            else:
                                stats['errors'] += 1
                                logger.error(f"❌ Erro ao salvar venue {venue_id}")
                        else:
                            logger.warning(f"⚠️ Venue {venue_id} não encontrado")
                            stats['errors'] += 1
                        
                        stats['venues_found'] += 1 if venue else 0
                        
                        # Pausa mínima
                        time.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"❌ Erro ao coletar venue {venue_id}: {e}")
                        stats['errors'] += 1
                
                # Pausa entre batches
                time.sleep(1.0)
            
            stats['teams_processed'] = len(teams)
            
        except Exception as e:
            logger.error(f"❌ Erro durante coleta de venues: {e}")
            stats['errors'] += 1
        
        stats['end_time'] = datetime.now()
        stats['duration_seconds'] = int((stats['end_time'] - stats['start_time']).total_seconds())
        
        return stats
    
    def collect_referees_from_fixtures(self) -> Dict[str, Any]:
        """
        Coleta referees através das fixtures recentes
        
        Returns:
            Estatísticas da coleta de referees
        """
        stats = {
            'referees_found': 0,
            'referees_saved': 0,
            'fixtures_processed': 0,
            'api_requests': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        try:
            logger.info("👨‍⚖️ Coletando referees através das fixtures...")
            
            fixtures = self.get_recent_fixtures_for_referees(days_back=60)  # 2 meses
            if not fixtures:
                logger.warning("⚠️ Nenhuma fixture com referee_id encontrada")
                return stats
            
            # Extrair referee_ids únicos
            referee_ids = set()
            for fixture in fixtures:
                if fixture.get('referee_id'):
                    referee_ids.add(fixture['referee_id'])
            
            logger.info(f"🎯 {len(referee_ids)} referees únicos para coletar")
            
            # Buscar referees existentes
            existing_result = self.supabase.client.table('referees').select('sportmonks_id').execute()
            existing_referee_ids = set(r['sportmonks_id'] for r in existing_result.data) if existing_result.data else set()
            
            # Filtrar referees que ainda não temos
            new_referee_ids = referee_ids - existing_referee_ids
            logger.info(f"📊 {len(new_referee_ids)} referees novos para coletar")
            
            if not new_referee_ids:
                logger.info("✅ Todos os referees das fixtures já estão no banco")
                return stats
            
            # Coletar referees em batches
            referee_ids_list = list(new_referee_ids)
            total_batches = (len(referee_ids_list) + self.batch_size - 1) // self.batch_size
            
            for batch_idx in range(total_batches):
                start_idx = batch_idx * self.batch_size
                end_idx = min(start_idx + self.batch_size, len(referee_ids_list))
                batch_referee_ids = referee_ids_list[start_idx:end_idx]
                
                logger.info(f"📦 Batch {batch_idx + 1}/{total_batches}: Coletando referees {start_idx + 1}-{end_idx}")
                
                for referee_id in tqdm(batch_referee_ids, desc=f"Referees Batch {batch_idx + 1}"):
                    try:
                        # Buscar referee por ID
                        referee = self.sportmonks.get_referee_by_id(referee_id)
                        stats['api_requests'] += 1
                        
                        if referee:
                            # Salvar referee no banco
                            success = self.supabase.upsert_referees([referee])
                            
                            if success:
                                stats['referees_saved'] += 1
                                logger.debug(f"✅ Referee {referee.get('name', referee_id)} salvo")
                            else:
                                stats['errors'] += 1
                                logger.error(f"❌ Erro ao salvar referee {referee_id}")
                        else:
                            logger.warning(f"⚠️ Referee {referee_id} não encontrado")
                            stats['errors'] += 1
                        
                        stats['referees_found'] += 1 if referee else 0
                        
                        # Pausa mínima
                        time.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"❌ Erro ao coletar referee {referee_id}: {e}")
                        stats['errors'] += 1
                
                # Pausa entre batches
                time.sleep(1.0)
            
            stats['fixtures_processed'] = len(fixtures)
            
        except Exception as e:
            logger.error(f"❌ Erro durante coleta de referees: {e}")
            stats['errors'] += 1
        
        stats['end_time'] = datetime.now()
        stats['duration_seconds'] = int((stats['end_time'] - stats['start_time']).total_seconds())
        
        return stats
    
    def run_venues_referees_collection(self) -> Dict[str, Any]:
        """
        Executa a coleta completa de venues e referees
        
        Returns:
            Estatísticas completas da operação
        """
        with ETLJobContext(
            job_name="venues_referees_collection",
            job_type="base_data",
            metadata_manager=self.metadata_manager,
            script_path=__file__,
            input_parameters={
                "target": "venues_and_referees",
                "batch_size": self.batch_size
            }
        ) as job:
            
            logger.info("🏟️👨‍⚖️ INICIANDO COLETA COMPLETA DE VENUES E REFEREES")
            logger.info("=" * 70)
            job.log("INFO", "Iniciando coleta completa de venues e referees")
            
            overall_stats = {
                'start_time': datetime.now(),
                'venues_collected': 0,
                'referees_collected': 0,
                'total_api_requests': 0,
                'total_errors': 0,
                'venues_stats': {},
                'referees_stats': {},
                'success': False
            }
            
            try:
                # 1. Coletar Venues
                logger.info("🏟️ FASE 1: Coletando Venues")
                logger.info("-" * 40)
                
                venues_stats = self.collect_venues_by_teams()
                overall_stats['venues_stats'] = venues_stats
                overall_stats['venues_collected'] = venues_stats['venues_saved']
                overall_stats['total_api_requests'] += venues_stats['api_requests']
                overall_stats['total_errors'] += venues_stats['errors']
                
                # Atualizar job
                job.increment_api_requests(venues_stats['api_requests'])
                job.increment_records(
                    processed=venues_stats['venues_found'],
                    inserted=venues_stats['venues_saved'],
                    failed=venues_stats['errors']
                )
                
                # Checkpoint após venues
                job.checkpoint(
                    name="venues_collection_completed",
                    data={
                        "venues_collected": venues_stats['venues_saved'],
                        "venues_found": venues_stats['venues_found'],
                        "api_requests": venues_stats['api_requests']
                    },
                    progress_percentage=50.0
                )
                
                logger.info(f"✅ Venues coletados: {venues_stats['venues_saved']}")
                logger.info(f"🌐 Requisições API: {venues_stats['api_requests']}")
                logger.info(f"❌ Erros: {venues_stats['errors']}")
                
                # 2. Coletar Referees
                logger.info("\n👨‍⚖️ FASE 2: Coletando Referees")
                logger.info("-" * 40)
                
                referees_stats = self.collect_referees_from_fixtures()
                overall_stats['referees_stats'] = referees_stats
                overall_stats['referees_collected'] = referees_stats['referees_saved']
                overall_stats['total_api_requests'] += referees_stats['api_requests']
                overall_stats['total_errors'] += referees_stats['errors']
                
                # Atualizar job
                job.increment_api_requests(referees_stats['api_requests'])
                job.increment_records(
                    processed=referees_stats['referees_found'],
                    inserted=referees_stats['referees_saved'],
                    failed=referees_stats['errors']
                )
                
                # Checkpoint após referees
                job.checkpoint(
                    name="referees_collection_completed",
                    data={
                        "referees_collected": referees_stats['referees_saved'],
                        "referees_found": referees_stats['referees_found'],
                        "api_requests": referees_stats['api_requests']
                    },
                    progress_percentage=90.0
                )
                
                logger.info(f"✅ Referees coletados: {referees_stats['referees_saved']}")
                logger.info(f"🌐 Requisições API: {referees_stats['api_requests']}")
                logger.info(f"❌ Erros: {referees_stats['errors']}")
                
                # Finalizar operação
                overall_stats['end_time'] = datetime.now()
                overall_stats['duration_seconds'] = int((overall_stats['end_time'] - overall_stats['start_time']).total_seconds())
                overall_stats['success'] = True
                
                logger.info("\n" + "=" * 70)
                logger.info("🎉 COLETA DE VENUES E REFEREES CONCLUÍDA!")
                logger.info("=" * 70)
                logger.info(f"🏟️ Venues coletados: {overall_stats['venues_collected']}")
                logger.info(f"👨‍⚖️ Referees coletados: {overall_stats['referees_collected']}")
                logger.info(f"🌐 Requisições API: {overall_stats['total_api_requests']:,}")
                logger.info(f"❌ Erros: {overall_stats['total_errors']}")
                logger.info(f"⏱️ Duração: {overall_stats['duration_seconds']}s ({overall_stats['duration_seconds']//60}min)")
                
                total_collected = overall_stats['venues_collected'] + overall_stats['referees_collected']
                success_rate = (overall_stats['total_api_requests'] - overall_stats['total_errors']) / max(overall_stats['total_api_requests'], 1)
                
                logger.info(f"📈 Total coletado: {total_collected}")
                logger.info(f"📈 Taxa de sucesso: {success_rate:.1%}")
                
                job.log("INFO", f"Coleta concluída - {total_collected} itens coletados")
                
                # Checkpoint final
                job.checkpoint(
                    name="venues_referees_collection_finished",
                    data=overall_stats,
                    progress_percentage=100.0
                )
                
                return overall_stats
                
            except Exception as e:
                logger.error(f"❌ Erro durante coleta de venues e referees: {e}")
                overall_stats['success'] = False
                overall_stats['error'] = str(e)
                job.log("ERROR", f"Erro durante coleta: {e}")
                return overall_stats
    
    def validate_venues_referees_data(self) -> Dict[str, Any]:
        """
        Valida os dados de venues e referees coletados
        
        Returns:
            Relatório de validação
        """
        logger.info("🔍 Validando dados de venues e referees...")
        
        validation_report = {
            'total_venues': 0,
            'total_referees': 0,
            'venues_with_city': 0,
            'venues_with_country': 0,
            'referees_with_nationality': 0,
            'data_quality_score': 0.0,
            'issues_found': []
        }
        
        try:
            # Contar venues
            result = self.supabase.client.table('venues').select('id', count='exact').execute()
            validation_report['total_venues'] = result.count if result.count is not None else 0
            
            # Contar referees
            result = self.supabase.client.table('referees').select('id', count='exact').execute()
            validation_report['total_referees'] = result.count if result.count is not None else 0
            
            logger.info(f"📊 Total venues: {validation_report['total_venues']}")
            logger.info(f"📊 Total referees: {validation_report['total_referees']}")
            
            # Calcular score de qualidade
            venues_score = min(validation_report['total_venues'] / 500, 1.0)  # Meta: 500 venues
            referees_score = min(validation_report['total_referees'] / 200, 1.0)  # Meta: 200 referees
            validation_report['data_quality_score'] = (venues_score + referees_score) / 2
            
            logger.info(f"📊 Score de qualidade: {validation_report['data_quality_score']:.1%}")
            
            # Verificar metas
            if validation_report['total_venues'] >= 500:
                logger.info("✅ Meta de 500+ venues atingida!")
            elif validation_report['total_venues'] >= 300:
                logger.info("✅ Boa cobertura de venues (300+)")
            else:
                validation_report['issues_found'].append(f"Venues insuficientes: {validation_report['total_venues']} < 500")
            
            if validation_report['total_referees'] >= 200:
                logger.info("✅ Meta de 200+ referees atingida!")
            elif validation_report['total_referees'] >= 100:
                logger.info("✅ Boa cobertura de referees (100+)")
            else:
                validation_report['issues_found'].append(f"Referees insuficientes: {validation_report['total_referees']} < 200")
            
            return validation_report
            
        except Exception as e:
            logger.error(f"❌ Erro durante validação: {e}")
            validation_report['issues_found'].append(f"Erro de validação: {e}")
            return validation_report


def main():
    """Função principal da coleta de venues e referees"""
    print("🏟️👨‍⚖️ COLETA COMPLETA DE VENUES E REFEREES - TASK-ETL-010")
    print("=" * 70)
    
    try:
        # Inicializar gerenciador
        manager = VenuesRefereesManager(
            use_redis=True,
            batch_size=50
        )
        
        # Executar coleta
        print("🔄 Executando coleta de venues e referees...")
        stats = manager.run_venues_referees_collection()
        
        # Validar dados
        print("🔍 Validando dados coletados...")
        validation = manager.validate_venues_referees_data()
        
        print(f"\n📊 RESULTADO:")
        print(f"  • Venues coletados: {stats.get('venues_collected', 0)}")
        print(f"  • Referees coletados: {stats.get('referees_collected', 0)}")
        print(f"  • Total venues no banco: {validation.get('total_venues', 0)}")
        print(f"  • Total referees no banco: {validation.get('total_referees', 0)}")
        print(f"  • Requisições API: {stats.get('total_api_requests', 0):,}")
        print(f"  • Erros: {stats.get('total_errors', 0)}")
        print(f"  • Score de qualidade: {validation.get('data_quality_score', 0):.1%}")
        
        # Verificar critérios de sucesso
        success_criteria = [
            ("Coleta executada", stats.get('success', False)),
            ("Venues coletados", stats.get('venues_collected', 0) > 0 or validation.get('total_venues', 0) >= 300),
            ("Referees coletados", stats.get('referees_collected', 0) > 0 or validation.get('total_referees', 0) >= 100),
            ("Score de qualidade > 60%", validation.get('data_quality_score', 0) > 0.6),
            ("Taxa de erro < 20%", (stats.get('total_errors', 0) / max(stats.get('total_api_requests', 1), 1)) < 0.2)
        ]
        
        print("\n✅ CRITÉRIOS DE SUCESSO:")
        all_passed = True
        for criterion, passed in success_criteria:
            status = "✅" if passed else "❌"
            print(f"  {status} {criterion}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 TASK-ETL-010 CONCLUÍDA COM SUCESSO!")
            print("🚀 Pronto para iniciar TASK-ETL-011")
            return True
        else:
            print("\n⚠️ TASK-ETL-010 CONCLUÍDA COM PROBLEMAS")
            print("🔧 Revisar coleta antes de prosseguir")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro fatal durante coleta: {e}")
        print(f"❌ Erro fatal: {e}")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {str(e)}")
        sys.exit(1)
