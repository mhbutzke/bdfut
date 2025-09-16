#!/usr/bin/env python3
"""
Exemplo de uso do sistema de metadados ETL
==========================================

Este script demonstra como usar o sistema de metadados ETL
para rastrear jobs, criar checkpoints e logs.
"""

import os
import sys
import time
from datetime import datetime

# Adicionar o diretório bdfut ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from bdfut.core.etl_metadata import ETLMetadataManager, ETLJobContext
from bdfut.core.etl_process import ETLProcess

def example_basic_metadata_usage():
    """Exemplo básico de uso de metadados"""
    print("🧪 EXEMPLO: Uso Básico de Metadados ETL")
    print("=" * 50)
    
    # Inicializar gerenciador de metadados
    metadata_manager = ETLMetadataManager()
    
    # Método 1: Uso manual
    print("\n📝 Método 1: Uso Manual")
    job_id = metadata_manager.start_job(
        job_name="example_manual_job",
        job_type="base_data",
        script_path=__file__,
        input_parameters={"example_param": "value"}
    )
    
    if job_id:
        print(f"✅ Job iniciado: {job_id}")
        
        # Simular trabalho
        for i in range(3):
            print(f"  Processando item {i+1}...")
            metadata_manager.log_job(job_id, "INFO", f"Processando item {i+1}")
            time.sleep(0.5)
            
            # Criar checkpoint
            metadata_manager.create_checkpoint(
                job_id=job_id,
                checkpoint_name=f"item_{i+1}_processed",
                checkpoint_data={"current_item": i+1, "items_processed": i+1},
                progress_percentage=(i+1) * 33.33
            )
        
        # Finalizar job
        metadata_manager.complete_job(
            job_id=job_id,
            status="completed",
            api_requests=3,
            records_processed=3,
            records_inserted=3
        )
        print("✅ Job finalizado manualmente")

def example_context_manager_usage():
    """Exemplo usando context manager"""
    print("\n📝 Método 2: Context Manager (RECOMENDADO)")
    print("-" * 40)
    
    metadata_manager = ETLMetadataManager()
    
    try:
        with ETLJobContext(
            job_name="example_context_job",
            job_type="fixtures_events",
            metadata_manager=metadata_manager,
            script_path=__file__,
            input_parameters={"league_id": 8, "season_id": 25583}
        ) as job:
            
            job.log("INFO", "Iniciando processamento com context manager")
            
            # Simular coleta de dados
            leagues = ["Premier League", "La Liga", "Serie A"]
            
            for i, league in enumerate(leagues):
                job.log("INFO", f"Processando liga: {league}")
                print(f"  📊 Processando {league}...")
                
                # Simular requisições à API
                job.increment_api_requests(2)  # 2 requisições por liga
                
                # Simular processamento de dados
                records = (i + 1) * 10  # 10, 20, 30 registros
                job.increment_records(
                    processed=records,
                    inserted=records - 1,  # 1 falha por liga
                    failed=1
                )
                
                # Checkpoint de progresso
                job.checkpoint(
                    name=f"league_{league.lower().replace(' ', '_')}_completed",
                    data={
                        "league": league,
                        "records_processed": records,
                        "current_step": i + 1,
                        "total_steps": len(leagues)
                    },
                    progress_percentage=((i + 1) / len(leagues)) * 100
                )
                
                time.sleep(0.3)
            
            job.log("INFO", "Processamento concluído com sucesso")
            print("✅ Context manager finalizado automaticamente")
            
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")

def example_etl_process_with_metadata():
    """Exemplo usando ETLProcess com metadados integrados"""
    print("\n📝 Método 3: ETLProcess Integrado")
    print("-" * 40)
    
    try:
        etl_process = ETLProcess()
        
        # O método sync_base_data já usa metadados automaticamente
        print("  🔄 Executando sync_base_data com metadados...")
        etl_process.sync_base_data()
        
        print("✅ ETLProcess executado com metadados automáticos")
        
    except Exception as e:
        print(f"❌ Erro no ETLProcess: {e}")

def example_view_statistics():
    """Exemplo de visualização de estatísticas"""
    print("\n📊 Estatísticas dos Jobs ETL")
    print("-" * 40)
    
    metadata_manager = ETLMetadataManager()
    
    # Obter estatísticas gerais
    stats = metadata_manager.get_job_stats()
    if "error" not in stats:
        print("📈 Estatísticas Gerais:")
        for key, value in stats.items():
            print(f"  • {key}: {value}")
    else:
        print(f"⚠️ Erro ao obter estatísticas: {stats['error']}")
    
    # Obter jobs recentes
    print("\n📋 Jobs Recentes:")
    recent_jobs = metadata_manager.get_recent_jobs(limit=5)
    
    if recent_jobs:
        for job in recent_jobs:
            status_emoji = {
                'completed': '✅',
                'failed': '❌',
                'running': '🔄',
                'pending': '⏳'
            }.get(job.get('status', 'unknown'), '❓')
            
            print(f"  {status_emoji} {job.get('job_name', 'Unknown')} ({job.get('job_type', 'Unknown')})")
            if job.get('duration_seconds'):
                duration = job['duration_seconds']
                print(f"    ⏱️ Duração: {duration}s")
            if job.get('records_processed'):
                print(f"    📊 Registros: {job['records_processed']}")
    else:
        print("  (Nenhum job encontrado)")

def main():
    """Função principal do exemplo"""
    print("🚀 DEMONSTRAÇÃO DO SISTEMA DE METADADOS ETL")
    print("=" * 60)
    
    # Executar exemplos
    example_basic_metadata_usage()
    example_context_manager_usage()
    example_etl_process_with_metadata()
    example_view_statistics()
    
    print("\n" + "=" * 60)
    print("✅ Demonstração concluída!")
    print("\n💡 DICAS:")
    print("  • Use o ETLJobContext para gerenciamento automático")
    print("  • Crie checkpoints em pontos importantes")
    print("  • Use logs para rastreamento detalhado")
    print("  • Monitore estatísticas regularmente")

if __name__ == "__main__":
    main()
