# Scripts Utilitários

Esta pasta contém scripts utilitários para verificação, teste e manutenção do sistema BDFut.

## Scripts Disponíveis

### 🔍 Verificação de Estrutura
- **`51_verificar_estrutura_fixtures.py`** - Verifica a estrutura atual da tabela fixtures no banco de dados
- **`52_verificar_fixtures_simples.py`** - Verificação simples da tabela fixtures usando credenciais diretas

### 🧪 Testes
- **`test_sportmonks_api.py`** - Script de teste para verificar conectividade com a API Sportmonks

## Como Usar

```bash
# Executar verificação de estrutura
python bdfut/scripts/utils/51_verificar_estrutura_fixtures.py

# Executar verificação simples
python bdfut/scripts/utils/52_verificar_fixtures_simples.py

# Testar API Sportmonks
python bdfut/scripts/utils/test_sportmonks_api.py
```

## Notas

- Estes scripts são utilitários de desenvolvimento e manutenção
- Certifique-se de ter as configurações corretas no arquivo `.env`
- Os scripts podem ser executados independentemente do sistema principal
