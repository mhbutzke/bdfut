# Guia de Testes de Qualidade de Dados - BDFut

## Visão Geral

Este documento descreve o sistema abrangente de testes de qualidade de dados implementado no projeto BDFut. Os testes garantem a integridade, consistência e precisão dos dados de futebol extraídos da API Sportmonks e armazenados no Supabase.

## Categorias de Testes

### 1. Integridade Referencial
**Arquivo:** `tests/test_data_quality.py::TestReferentialIntegrity`

Valida que todas as relações entre tabelas estão corretas:

- **Foreign Keys em Fixtures**: Verifica se `home_team_id`, `away_team_id`, `league_id`, `season_id` e `venue_id` referenciam registros válidos
- **Relacionamento Teams-Leagues**: Garante que todos os times têm uma liga válida associada
- **Relacionamento Seasons-Leagues**: Valida que temporadas estão associadas a ligas existentes

### 2. Detecção de Duplicados
**Arquivo:** `tests/test_data_quality.py::TestDuplicateDetection`

Identifica registros duplicados que podem causar inconsistências:

- **Fixtures Únicas**: Verifica ausência de fixtures duplicadas por `sportmonks_id`
- **Teams Únicos**: Valida que não há times duplicados
- **Leagues Únicas**: Garante que ligas não estão duplicadas

### 3. Campos Obrigatórios
**Arquivo:** `tests/test_data_quality.py::TestRequiredFields`

Valida que campos críticos não são nulos ou vazios:

- **Fixtures**: `sportmonks_id`, `home_team_id`, `away_team_id`, `league_id`, `season_id`, `match_date`
- **Teams**: `sportmonks_id`, `name`, `league_id` (nome não pode ser vazio)
- **Leagues**: `sportmonks_id`, `name`, `country_id` (nome não pode ser vazio)

### 4. Formatos e Tipos de Dados
**Arquivo:** `tests/test_data_quality.py::TestDataFormats`

Verifica que os dados estão nos formatos corretos:

- **Datas**: Formato ISO 8601 com timezone (ex: `2024-01-01T15:00:00Z`)
- **Scores**: Números inteiros não-negativos
- **IDs**: Todos os identificadores são números inteiros

### 5. Constraints de Negócio
**Arquivo:** `tests/test_data_quality.py::TestBusinessConstraints`

Valida regras específicas do domínio de futebol:

- **Times Diferentes**: `home_team_id` ≠ `away_team_id` em fixtures
- **Datas de Temporada**: `start_date` < `end_date` para seasons
- **Ano de Fundação**: Entre 1800 e ano atual + 1 para teams

### 6. Completude de Dados
**Arquivo:** `tests/test_data_quality.py::TestDataCompleteness`

Verifica que dados essenciais estão presentes:

- **Scores em Fixtures Finalizadas**: Fixtures com status "finished" devem ter scores
- **Dados Essenciais de Teams**: Nome e league_id obrigatórios
- **País das Ligas**: Todas as ligas devem ter country_id

### 7. Consistência Temporal
**Arquivo:** `tests/test_data_quality.py::TestTemporalConsistency`

Valida a sequência temporal dos dados:

- **Datas Cronológicas**: `created_at` ≤ `updated_at` ≤ `match_date`
- **Temporadas Sem Sobreposição**: Para a mesma liga, temporadas não podem se sobrepor

### 8. Integração de Qualidade
**Arquivo:** `tests/test_data_quality.py::TestDataQualityIntegration`

Testa qualidade durante o processo ETL:

- **Qualidade no ETL**: Validação durante sincronização de dados
- **Monitoramento**: Métricas de qualidade (completude ≥ 90%, precisão ≥ 95%)

### 9. Performance de Qualidade
**Arquivo:** `tests/test_data_quality.py::TestDataQualityPerformance`

Garante que verificações são eficientes:

- **Verificação Rápida**: < 1 segundo para verificações básicas
- **Detecção de Duplicados**: < 0.5 segundos para 10.000 registros

## Como Executar os Testes

### Executar Todos os Testes de Qualidade
```bash
python3 -m pytest tests/test_data_quality.py -v
```

### Executar Categoria Específica
```bash
# Integridade referencial
python3 -m pytest tests/test_data_quality.py::TestReferentialIntegrity -v

# Detecção de duplicados
python3 -m pytest tests/test_data_quality.py::TestDuplicateDetection -v

# Campos obrigatórios
python3 -m pytest tests/test_data_quality.py::TestRequiredFields -v
```

### Executar Teste Específico
```bash
python3 -m pytest tests/test_data_quality.py::TestReferentialIntegrity::test_fixtures_foreign_keys_valid -v
```

## Integração CI/CD

Os testes de qualidade estão integrados ao pipeline CI/CD do GitHub Actions:

```yaml
- name: Run Data Quality tests
  run: |
    pytest tests/test_data_quality.py -v
```

Os testes são executados automaticamente em:
- Push para branches `main` e `develop`
- Pull requests para `main`
- Múltiplas versões do Python (3.8, 3.9, 3.10)

## Interpretação dos Resultados

### Testes Passando ✅
- **24/24 testes passando**: Sistema de qualidade funcionando corretamente
- **Todas as categorias validadas**: Dados íntegros e consistentes

### Testes Falhando ❌
- **Integridade Referencial**: Verificar foreign keys e relacionamentos
- **Duplicados**: Investigar registros duplicados na fonte
- **Campos Obrigatórios**: Validar processo de extração da API
- **Formatos**: Verificar transformações de dados
- **Constraints**: Revisar regras de negócio
- **Completude**: Verificar qualidade da fonte de dados
- **Temporal**: Investigar sequência de eventos
- **Performance**: Otimizar verificações se necessário

## Métricas de Qualidade

### Indicadores Principais
- **Taxa de Completude**: ≥ 90% (campos obrigatórios preenchidos)
- **Taxa de Precisão**: ≥ 95% (dados corretos e válidos)
- **Taxa de Duplicados**: 0% (registros únicos)
- **Taxa de Integridade**: 100% (foreign keys válidas)

### Monitoramento Contínuo
- **Execução Automática**: CI/CD pipeline
- **Relatórios**: Coverage e resultados dos testes
- **Alertas**: Falhas nos testes geram notificações

## Troubleshooting

### Problemas Comuns

1. **Foreign Key Violations**
   ```bash
   # Verificar dados órfãos
   SELECT * FROM fixtures f 
   LEFT JOIN teams t ON f.home_team_id = t.sportmonks_id 
   WHERE t.sportmonks_id IS NULL;
   ```

2. **Duplicados**
   ```bash
   # Identificar duplicados
   SELECT sportmonks_id, COUNT(*) 
   FROM fixtures 
   GROUP BY sportmonks_id 
   HAVING COUNT(*) > 1;
   ```

3. **Campos Nulos**
   ```bash
   # Encontrar campos obrigatórios nulos
   SELECT * FROM teams 
   WHERE name IS NULL OR name = '';
   ```

### Logs e Debugging
- **Logs de Teste**: Verificar saída do pytest
- **Logs do ETL**: Monitorar processo de sincronização
- **Logs do Banco**: Verificar queries executadas

## Manutenção

### Atualizações Regulares
- **Revisar Testes**: Mensalmente
- **Atualizar Métricas**: Conforme necessário
- **Otimizar Performance**: Se verificações ficarem lentas

### Novos Testes
Para adicionar novos testes de qualidade:

1. **Identificar Categoria**: Escolher classe de teste apropriada
2. **Criar Teste**: Seguir padrão dos testes existentes
3. **Documentar**: Atualizar este guia
4. **Integrar**: Adicionar ao CI/CD se necessário

## Contato

Para dúvidas sobre testes de qualidade:
- **QA Engineer**: Responsável pela implementação
- **Documentação**: Este guia e código fonte
- **Issues**: GitHub issues para problemas específicos
