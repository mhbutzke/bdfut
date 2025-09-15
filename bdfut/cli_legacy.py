#!/usr/bin/env python3
"""
Script principal para ETL de dados da Sportmonks API para Supabase
"""
import click
import logging
from datetime import datetime
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.etl_process import ETLProcess
from config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'etl_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """CLI para gerenciar ETL de dados Sportmonks para Supabase"""
    try:
        Config.validate()
        click.echo(click.style("✅ Configuração validada com sucesso!", fg='green'))
    except ValueError as e:
        click.echo(click.style(f"❌ Erro de configuração: {str(e)}", fg='red'))
        click.echo("Por favor, configure as variáveis de ambiente no arquivo .env")
        sys.exit(1)

@cli.command()
def sync_base():
    """Sincroniza dados base (countries, states, types)"""
    click.echo(click.style("🔄 Sincronizando dados base...", fg='yellow'))
    etl = ETLProcess()
    etl.sync_base_data()
    click.echo(click.style("✅ Dados base sincronizados!", fg='green'))

@cli.command()
@click.option('--league-ids', '-l', multiple=True, type=int, 
              help='IDs das ligas a sincronizar (pode ser usado múltiplas vezes)')
def sync_leagues(league_ids):
    """Sincroniza ligas e suas temporadas"""
    etl = ETLProcess()
    
    if league_ids:
        league_list = list(league_ids)
        click.echo(click.style(f"🔄 Sincronizando {len(league_list)} ligas específicas...", fg='yellow'))
        etl.sync_leagues(league_list)
    else:
        click.echo(click.style("🔄 Sincronizando ligas principais...", fg='yellow'))
        etl.sync_leagues()
    
    click.echo(click.style("✅ Ligas sincronizadas!", fg='green'))

@cli.command()
@click.argument('season_id', type=int)
def sync_teams(season_id):
    """Sincroniza times de uma temporada específica"""
    click.echo(click.style(f"🔄 Sincronizando times da temporada {season_id}...", fg='yellow'))
    etl = ETLProcess()
    if etl.sync_teams_by_season(season_id):
        click.echo(click.style("✅ Times sincronizados!", fg='green'))
    else:
        click.echo(click.style("❌ Erro ao sincronizar times!", fg='red'))

@cli.command()
@click.argument('start_date')
@click.argument('end_date')
@click.option('--details', is_flag=True, help='Incluir detalhes completos das partidas')
def sync_fixtures(start_date, end_date, details):
    """
    Sincroniza partidas em um intervalo de datas
    
    Datas devem estar no formato YYYY-MM-DD
    """
    click.echo(click.style(f"🔄 Sincronizando partidas de {start_date} até {end_date}...", fg='yellow'))
    
    etl = ETLProcess()
    if etl.sync_fixtures_by_date_range(start_date, end_date, include_details=details):
        click.echo(click.style("✅ Partidas sincronizadas!", fg='green'))
    else:
        click.echo(click.style("❌ Erro ao sincronizar partidas!", fg='red'))

@cli.command()
@click.option('--days-back', '-b', default=7, type=int, 
              help='Dias para trás a partir de hoje (padrão: 7)')
@click.option('--days-forward', '-f', default=7, type=int,
              help='Dias para frente a partir de hoje (padrão: 7)')
def sync_recent(days_back, days_forward):
    """Sincroniza partidas recentes e próximas"""
    click.echo(click.style(
        f"🔄 Sincronizando partidas dos últimos {days_back} dias e próximos {days_forward} dias...", 
        fg='yellow'
    ))
    
    etl = ETLProcess()
    if etl.sync_recent_fixtures(days_back, days_forward):
        click.echo(click.style("✅ Partidas recentes sincronizadas!", fg='green'))
    else:
        click.echo(click.style("❌ Erro ao sincronizar partidas recentes!", fg='red'))

@cli.command()
@click.argument('fixture_id', type=int)
def sync_fixture(fixture_id):
    """Sincroniza detalhes completos de uma partida específica"""
    click.echo(click.style(f"🔄 Sincronizando detalhes da partida {fixture_id}...", fg='yellow'))
    
    etl = ETLProcess()
    if etl.sync_fixture_details(fixture_id):
        click.echo(click.style("✅ Detalhes da partida sincronizados!", fg='green'))
    else:
        click.echo(click.style("❌ Erro ao sincronizar detalhes da partida!", fg='red'))

@cli.command()
@click.confirmation_option(prompt='Isso pode demorar. Tem certeza que deseja continuar?')
def full_sync():
    """Executa sincronização completa de todos os dados"""
    click.echo(click.style("🚀 Iniciando sincronização completa...", fg='yellow', bold=True))
    
    start_time = datetime.now()
    etl = ETLProcess()
    
    try:
        etl.full_sync()
        
        elapsed_time = datetime.now() - start_time
        click.echo(click.style(
            f"✅ Sincronização completa finalizada em {elapsed_time}!", 
            fg='green', bold=True
        ))
    except Exception as e:
        logger.error(f"Erro durante sincronização completa: {str(e)}")
        click.echo(click.style(f"❌ Erro: {str(e)}", fg='red'))
        sys.exit(1)

@cli.command()
def incremental():
    """Executa sincronização incremental (apenas atualizações recentes)"""
    click.echo(click.style("🔄 Executando sincronização incremental...", fg='yellow'))
    
    etl = ETLProcess()
    etl.incremental_sync()
    
    click.echo(click.style("✅ Sincronização incremental concluída!", fg='green'))

@cli.command()
def test_connection():
    """Testa as conexões com Sportmonks API e Supabase"""
    click.echo(click.style("🔍 Testando conexões...", fg='yellow'))
    
    # Testar Sportmonks
    try:
        from src.sportmonks_client import SportmonksClient
        client = SportmonksClient()
        states = client.get_states()
        click.echo(click.style(f"✅ Sportmonks API: OK ({len(states)} states encontrados)", fg='green'))
    except Exception as e:
        click.echo(click.style(f"❌ Sportmonks API: {str(e)}", fg='red'))
    
    # Testar Supabase
    try:
        from src.supabase_client import SupabaseClient
        client = SupabaseClient()
        # Tentar fazer uma query simples em uma tabela existente
        result = client.client.table('leagues').select("*").limit(1).execute()
        click.echo(click.style(f"✅ Supabase: OK (conexão estabelecida)", fg='green'))
    except Exception as e:
        # Se não houver tabelas, é esperado
        if "PGRST" in str(e):
            click.echo(click.style(f"⚠️  Supabase: Conectado mas tabelas ainda não criadas", fg='yellow'))
            click.echo(click.style(f"   Execute a migração no SQL Editor do Supabase primeiro", fg='yellow'))
        else:
            click.echo(click.style(f"❌ Supabase: {str(e)}", fg='red'))

@cli.command()
def show_config():
    """Mostra a configuração atual (sem dados sensíveis)"""
    click.echo(click.style("📋 Configuração Atual:", fg='cyan', bold=True))
    click.echo(f"  Base URL: {Config.SPORTMONKS_BASE_URL}")
    click.echo(f"  Supabase URL: {Config.SUPABASE_URL[:30]}..." if Config.SUPABASE_URL else "  Supabase URL: Não configurado")
    click.echo(f"  Rate Limit: {Config.RATE_LIMIT_PER_HOUR} req/hora")
    click.echo(f"  Batch Size: {Config.BATCH_SIZE}")
    click.echo(f"  Max Retries: {Config.MAX_RETRIES}")
    click.echo(f"  Ligas Principais: {len(Config.MAIN_LEAGUES)} ligas")
    
    if Config.MAIN_LEAGUES:
        click.echo("\n📊 Ligas configuradas:")
        leagues_names = {
            648: "Brasil - Serie A",
            651: "Brasil - Serie B", 
            654: "Brasil - Copa do Brasil",
            636: "Argentina - Liga Profesional",
            1122: "Copa Libertadores",
            1116: "Copa Sudamericana",
            2: "Champions League",
            5: "Europa League",
            8: "Premier League",
            9: "Championship",
            564: "La Liga",
            462: "Liga Portugal",
            301: "Ligue 1",
            82: "Bundesliga",
            743: "Liga MX",
            779: "MLS"
        }
        for league_id in Config.MAIN_LEAGUES:
            name = leagues_names.get(league_id, f"Liga ID: {league_id}")
            click.echo(f"    • {name}")

if __name__ == '__main__':
    cli()
