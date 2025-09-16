#!/usr/bin/env python3
"""
Script de teste para verificar endpoints da API Sportmonks
"""

import os
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_api_endpoints():
    """Testar diferentes endpoints da API Sportmonks"""
    
    api_key = os.getenv("SPORTMONKS_API_KEY")
    base_url = "https://api.sportmonks.com/v3/football"
    
    if not api_key:
        print("❌ SPORTMONKS_API_KEY não encontrado")
        return
    
    print(f"🔑 API Key: {api_key[:10]}...")
    print("=" * 80)
    
    # Teste 1: Listar ligas
    print("📋 Teste 1: Listar ligas")
    try:
        url = f"{base_url}/leagues"
        params = {'api_token': api_key, 'per_page': 5}
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! {len(data.get('data', []))} ligas encontradas")
            if data.get('data'):
                print(f"Primeira liga: {data['data'][0].get('name')} (ID: {data['data'][0].get('id')})")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
    
    print("\n" + "=" * 80)
    
    # Teste 2: Listar temporadas de uma liga específica
    print("📅 Teste 2: Listar temporadas da Premier League (ID: 8)")
    try:
        url = f"{base_url}/seasons"
        params = {
            'api_token': api_key,
            'league_id': 8,
            'per_page': 5
        }
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! {len(data.get('data', []))} temporadas encontradas")
            if data.get('data'):
                season = data['data'][0]
                print(f"Primeira temporada: {season.get('name')} (ID: {season.get('id')})")
                return season.get('id')  # Retornar ID da primeira temporada para teste
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
    
    print("\n" + "=" * 80)
    
    # Teste 3: Listar fixtures sem filtro
    print("⚽ Teste 3: Listar fixtures (sem filtro)")
    try:
        url = f"{base_url}/fixtures"
        params = {
            'api_token': api_key,
            'per_page': 5
        }
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! {len(data.get('data', []))} fixtures encontradas")
            if data.get('data'):
                fixture = data['data'][0]
                print(f"Primeira fixture: {fixture.get('id')} - {fixture.get('starting_at')}")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
    
    print("\n" + "=" * 80)
    
    # Teste 4: Listar fixtures com filtro de temporada
    season_id = 25583  # ID da temporada atual da Premier League
    print(f"⚽ Teste 4: Listar fixtures da temporada {season_id}")
    try:
        url = f"{base_url}/fixtures"
        params = {
            'api_token': api_key,
            'season_id': season_id,
            'per_page': 5
        }
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        print(f"URL: {response.url}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! {len(data.get('data', []))} fixtures encontradas")
            if data.get('data'):
                fixture = data['data'][0]
                print(f"Primeira fixture: {fixture.get('id')} - {fixture.get('starting_at')}")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
    
    print("\n" + "=" * 80)
    
    # Teste 5: Listar fixtures com filtro de liga
    print("⚽ Teste 5: Listar fixtures da Premier League (ID: 8)")
    try:
        url = f"{base_url}/fixtures"
        params = {
            'api_token': api_key,
            'league_id': 8,
            'per_page': 5
        }
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        print(f"URL: {response.url}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! {len(data.get('data', []))} fixtures encontradas")
            if data.get('data'):
                fixture = data['data'][0]
                print(f"Primeira fixture: {fixture.get('id')} - {fixture.get('starting_at')}")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")

if __name__ == "__main__":
    test_api_endpoints()
