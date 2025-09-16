# Guia de Commits - BDFut 📝

## Visão Geral

Este documento define as convenções e padrões para commits no projeto BDFut, garantindo um histórico limpo, organizado e fácil de entender.

## Índice

1. [Formato de Commit](#formato-de-commit)
2. [Tipos de Commit](#tipos-de-commit)
3. [Escopo de Commit](#escopo-de-commit)
4. [Descrição do Commit](#descrição-do-commit)
5. [Corpo do Commit](#corpo-do-commit)
6. [Rodapé do Commit](#rodapé-do-commit)
7. [Exemplos Práticos](#exemplos-práticos)
8. [Ferramentas](#ferramentas)

---

## Formato de Commit

### Estrutura Padrão

```
<tipo>(<escopo>): <descrição>

[corpo opcional]

[rodapé opcional]
```

### Regras Básicas

1. **Primeira linha**: Máximo 50 caracteres
2. **Tipo**: Sempre em minúsculas
3. **Escopo**: Sempre em minúsculas
4. **Descrição**: Sempre em minúsculas, sem ponto final
5. **Corpo**: Separado por linha em branco
6. **Rodapé**: Separado por linha em branco

### Exemplo Básico

```
feat(etl): adiciona sincronização incremental

Implementa sincronização incremental que processa apenas
dados modificados desde a última execução, reduzindo
significativamente o tempo de processamento.

Closes #123
```

---

## Tipos de Commit

### Tipos Principais

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova funcionalidade | `feat(api): adiciona endpoint de ligas` |
| `fix` | Correção de bug | `fix(cache): corrige invalidação de cache` |
| `docs` | Documentação | `docs(readme): atualiza instruções de instalação` |
| `style` | Formatação, sem mudança de código | `style(core): corrige formatação com black` |
| `refactor` | Refatoração de código | `refactor(client): simplifica lógica de retry` |
| `test` | Adição ou correção de testes | `test(etl): adiciona testes para sync_leagues` |
| `chore` | Tarefas de manutenção | `chore(deps): atualiza requests para v2.31.0` |

### Tipos Especiais

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `perf` | Melhoria de performance | `perf(cache): otimiza algoritmo de busca` |
| `ci` | Mudanças em CI/CD | `ci(github): adiciona workflow de testes` |
| `build` | Mudanças no sistema de build | `build(docker): atualiza imagem base` |
| `revert` | Reversão de commit | `revert: feat(api): adiciona endpoint de ligas` |

### Quando Usar Cada Tipo

#### `feat` - Nova Funcionalidade
- Adicionar nova funcionalidade
- Implementar novo endpoint
- Adicionar novo comando CLI
- Implementar nova estratégia de cache

```bash
feat(etl): adiciona sincronização incremental
feat(api): implementa endpoint de estatísticas
feat(cli): adiciona comando de backup
feat(cache): implementa cache distribuído
```

#### `fix` - Correção de Bug
- Corrigir bug existente
- Corrigir erro de validação
- Corrigir problema de performance
- Corrigir erro de configuração

```bash
fix(api): corrige rate limiting para ligas
fix(validation): corrige validação de datas
fix(performance): corrige vazamento de memória
fix(config): corrige carregamento de variáveis
```

#### `docs` - Documentação
- Atualizar README
- Adicionar documentação de API
- Corrigir documentação
- Adicionar exemplos

```bash
docs(readme): atualiza instruções de instalação
docs(api): adiciona documentação de endpoints
docs(fix): corrige exemplo de uso
docs(examples): adiciona exemplos de configuração
```

#### `style` - Formatação
- Corrigir formatação com Black
- Corrigir imports
- Corrigir espaçamento
- Corrigir nomenclatura

```bash
style(core): corrige formatação com black
style(imports): organiza imports por padrão
style(spacing): corrige espaçamento em funções
style(naming): corrige nomenclatura de variáveis
```

#### `refactor` - Refatoração
- Simplificar código
- Melhorar estrutura
- Otimizar algoritmo
- Reorganizar módulos

```bash
refactor(client): simplifica lógica de retry
refactor(etl): melhora estrutura de processamento
refactor(cache): otimiza algoritmo de invalidação
refactor(modules): reorganiza estrutura de pacotes
```

#### `test` - Testes
- Adicionar novos testes
- Corrigir testes existentes
- Melhorar cobertura
- Adicionar testes de integração

```bash
test(etl): adiciona testes para sync_leagues
test(fix): corrige teste de validação
test(coverage): melhora cobertura de cache
test(integration): adiciona testes de integração
```

#### `chore` - Manutenção
- Atualizar dependências
- Atualizar configurações
- Limpar código
- Atualizar ferramentas

```bash
chore(deps): atualiza requests para v2.31.0
chore(config): atualiza configuração do pytest
chore(cleanup): remove código não utilizado
chore(tools): atualiza versão do black
```

---

## Escopo de Commit

### Escopos Principais

| Escopo | Descrição | Exemplo |
|--------|-----------|---------|
| `api` | API e endpoints | `feat(api): adiciona endpoint de ligas` |
| `etl` | Processo de ETL | `feat(etl): adiciona sincronização incremental` |
| `cache` | Sistema de cache | `fix(cache): corrige invalidação de cache` |
| `config` | Configuração | `fix(config): corrige carregamento de variáveis` |
| `cli` | Interface CLI | `feat(cli): adiciona comando de backup` |
| `core` | Módulos principais | `refactor(core): simplifica lógica de retry` |
| `docs` | Documentação | `docs(readme): atualiza instruções` |
| `test` | Testes | `test(etl): adiciona testes para sync_leagues` |

### Escopos por Módulo

| Módulo | Escopo | Exemplo |
|--------|--------|---------|
| `sportmonks_client.py` | `sportmonks` | `fix(sportmonks): corrige rate limiting` |
| `supabase_client.py` | `supabase` | `feat(supabase): adiciona upsert de eventos` |
| `etl_process.py` | `etl` | `feat(etl): adiciona sincronização incremental` |
| `redis_cache.py` | `cache` | `perf(cache): otimiza algoritmo de busca` |
| `config.py` | `config` | `fix(config): corrige validação de API key` |

### Quando Usar Escopo

#### Com Escopo
- Mudança específica em um módulo
- Funcionalidade relacionada a um componente
- Bug específico de uma área

```bash
feat(etl): adiciona sincronização incremental
fix(cache): corrige invalidação de cache
refactor(sportmonks): simplifica lógica de retry
```

#### Sem Escopo
- Mudança geral no projeto
- Múltiplos módulos afetados
- Mudança de configuração global

```bash
feat: adiciona sistema de logging
fix: corrige problemas de compatibilidade
chore: atualiza dependências
```

---

## Descrição do Commit

### Regras para Descrição

1. **Máximo 50 caracteres**
2. **Sempre em minúsculas**
3. **Sem ponto final**
4. **Verbo no imperativo**
5. **Clara e concisa**

### Exemplos de Descrição

#### ✅ Corretas

```bash
feat(etl): adiciona sincronização incremental
fix(cache): corrige invalidação de cache
docs(readme): atualiza instruções de instalação
refactor(client): simplifica lógica de retry
test(etl): adiciona testes para sync_leagues
```

#### ❌ Incorretas

```bash
feat(etl): Adiciona sincronização incremental.
fix(cache): corrige invalidação de cache
docs(readme): atualiza instruções de instalação
refactor(client): simplifica lógica de retry
test(etl): adiciona testes para sync_leagues
```

### Verbos Comuns

| Verbo | Uso | Exemplo |
|-------|-----|---------|
| `adiciona` | Nova funcionalidade | `feat(etl): adiciona sincronização incremental` |
| `implementa` | Implementação completa | `feat(api): implementa endpoint de estatísticas` |
| `corrige` | Correção de bug | `fix(cache): corrige invalidação de cache` |
| `atualiza` | Atualização | `chore(deps): atualiza requests para v2.31.0` |
| `melhora` | Melhoria | `perf(cache): melhora algoritmo de busca` |
| `simplifica` | Simplificação | `refactor(client): simplifica lógica de retry` |
| `remove` | Remoção | `chore(cleanup): remove código não utilizado` |
| `reorganiza` | Reorganização | `refactor(modules): reorganiza estrutura de pacotes` |

---

## Corpo do Commit

### Quando Usar Corpo

- Explicar o que foi feito
- Explicar por que foi feito
- Explicar como foi feito
- Detalhar mudanças importantes

### Formato do Corpo

```
feat(etl): adiciona sincronização incremental

Implementa sincronização incremental que processa apenas
dados modificados desde a última execução, reduzindo
significativamente o tempo de processamento.

A implementação inclui:
- Verificação de timestamps de modificação
- Cache de metadados de sincronização
- Processamento em lotes otimizado
- Logging detalhado de progresso

Performance melhorada em 60% para sincronizações
diárias de ligas principais.
```

### Exemplos de Corpo

#### Funcionalidade Complexa

```
feat(api): implementa endpoint de estatísticas

Adiciona endpoint /api/v1/statistics que retorna
estatísticas detalhadas de sincronização e performance.

Inclui:
- Número de registros sincronizados por dia
- Taxa de sucesso de sincronizações
- Tempo médio de processamento
- Uso de cache e hit rate

Endpoint protegido por autenticação JWT e
rate limiting de 100 requests/hora.
```

#### Correção de Bug

```
fix(cache): corrige invalidação de cache

Corrige problema onde cache não era invalidado
após atualizações de dados, causando dados
desatualizados serem retornados.

Mudanças:
- Adiciona invalidação automática após upsert
- Implementa TTL baseado em timestamp de dados
- Adiciona validação de consistência de cache

Resolve issue #123 onde dados de ligas não
eram atualizados após sincronização.
```

#### Refatoração

```
refactor(client): simplifica lógica de retry

Refatora lógica de retry para usar tenacity
em vez de implementação customizada, melhorando
legibilidade e manutenibilidade.

Mudanças:
- Substitui retry customizado por tenacity
- Adiciona backoff exponencial configurável
- Melhora tratamento de exceções específicas
- Adiciona métricas de retry

Reduz código em 40% e melhora tratamento
de erros de rede.
```

---

## Rodapé do Commit

### Tipos de Rodapé

#### Referências a Issues

```
Closes #123
Fixes #456
Resolves #789
```

#### Breaking Changes

```
BREAKING CHANGE: API endpoint /api/v1/leagues agora
requer autenticação JWT. Atualize clientes para
incluir header Authorization.
```

#### Co-authored-by

```
Co-authored-by: João Silva <joao@example.com>
Co-authored-by: Maria Santos <maria@example.com>
```

### Exemplos de Rodapé

#### Com Referências

```
feat(api): implementa autenticação JWT

Implementa sistema de autenticação JWT para
proteger endpoints da API.

Closes #123
Fixes #456
```

#### Com Breaking Change

```
feat(api): implementa autenticação JWT

Implementa sistema de autenticação JWT para
proteger endpoints da API.

BREAKING CHANGE: Todos os endpoints da API agora
requerem autenticação JWT. Atualize clientes para
incluir header Authorization: Bearer <token>.

Closes #123
```

#### Com Co-autoria

```
feat(etl): adiciona sincronização incremental

Implementa sincronização incremental que processa
apenas dados modificados desde a última execução.

Co-authored-by: João Silva <joao@example.com>
Co-authored-by: Maria Santos <maria@example.com>
```

---

## Exemplos Práticos

### Commits de Funcionalidade

```bash
# Nova funcionalidade simples
feat(etl): adiciona sincronização incremental

# Nova funcionalidade complexa
feat(api): implementa endpoint de estatísticas

Implementa endpoint /api/v1/statistics que retorna
estatísticas detalhadas de sincronização e performance.

Inclui:
- Número de registros sincronizados por dia
- Taxa de sucesso de sincronizações
- Tempo médio de processamento
- Uso de cache e hit rate

Closes #123
```

### Commits de Correção

```bash
# Correção simples
fix(cache): corrige invalidação de cache

# Correção complexa
fix(api): corrige rate limiting para ligas

Corrige problema onde rate limiting não era aplicado
corretamente para requisições de ligas, causando
erro 429 Too Many Requests.

Mudanças:
- Aplica rate limiting por endpoint
- Adiciona janela deslizante de 1 hora
- Implementa backoff exponencial
- Adiciona métricas de rate limiting

Fixes #456
```

### Commits de Documentação

```bash
# Documentação simples
docs(readme): atualiza instruções de instalação

# Documentação complexa
docs(api): adiciona documentação de endpoints

Adiciona documentação completa para todos os
endpoints da API, incluindo exemplos de uso,
códigos de erro e autenticação.

Inclui:
- Documentação de todos os endpoints
- Exemplos de requisições e respostas
- Códigos de erro e tratamento
- Guia de autenticação JWT

Closes #789
```

### Commits de Refatoração

```bash
# Refatoração simples
refactor(client): simplifica lógica de retry

# Refatoração complexa
refactor(etl): melhora estrutura de processamento

Refatora estrutura de processamento ETL para
melhorar legibilidade, manutenibilidade e
performance.

Mudanças:
- Separa lógica de extração, transformação e carga
- Implementa padrão Strategy para diferentes tipos de dados
- Adiciona factory para criação de processadores
- Melhora tratamento de erros e logging

Performance melhorada em 30% e código
reduzido em 25%.
```

### Commits de Testes

```bash
# Testes simples
test(etl): adiciona testes para sync_leagues

# Testes complexos
test(integration): adiciona testes de integração

Adiciona suite completa de testes de integração
que valida fluxo completo de sincronização ETL.

Inclui:
- Testes de sincronização completa
- Testes de sincronização incremental
- Testes de tratamento de erros
- Testes de performance

Cobertura de testes aumentada para 85%.
```

### Commits de Manutenção

```bash
# Manutenção simples
chore(deps): atualiza requests para v2.31.0

# Manutenção complexa
chore(cleanup): remove código não utilizado

Remove código não utilizado e deprecações
para limpar codebase e melhorar manutenibilidade.

Mudanças:
- Remove funções deprecadas
- Limpa imports não utilizados
- Remove comentários obsoletos
- Atualiza documentação

Reduz tamanho do código em 15% e melhora
legibilidade.
```

---

## Ferramentas

### Commitizen

#### Instalação

```bash
pip install commitizen
```

#### Configuração

```toml
# pyproject.toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.1.0"
tag_format = "v$version"
version_files = [
    "pyproject.toml:version"
]
```

#### Uso

```bash
# Commit interativo
cz commit

# Verificar commits
cz check

# Gerar changelog
cz changelog
```

### Pre-commit Hooks

#### Configuração

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v2.20.2
    hooks:
      - id: commitizen
        stages: [commit-msg]
```

#### Instalação

```bash
pre-commit install --hook-type commit-msg
```

### Git Hooks

#### commit-msg Hook

```bash
#!/bin/sh
# .git/hooks/commit-msg

# Verificar formato do commit
commit_regex='^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}$'

if ! grep -qE "$commit_regex" "$1"; then
    echo "❌ Formato de commit inválido!"
    echo "Formato esperado: <tipo>(<escopo>): <descrição>"
    echo "Exemplo: feat(etl): adiciona sincronização incremental"
    exit 1
fi

echo "✅ Formato de commit válido!"
```

### Scripts de Ajuda

#### Script de Commit

```bash
#!/bin/bash
# scripts/commit.sh

echo "🚀 Assistente de Commit BDFut"
echo ""

# Perguntar tipo
echo "Tipo de commit:"
echo "1) feat - Nova funcionalidade"
echo "2) fix - Correção de bug"
echo "3) docs - Documentação"
echo "4) style - Formatação"
echo "5) refactor - Refatoração"
echo "6) test - Testes"
echo "7) chore - Manutenção"
read -p "Escolha (1-7): " tipo

case $tipo in
    1) tipo="feat" ;;
    2) tipo="fix" ;;
    3) tipo="docs" ;;
    4) tipo="style" ;;
    5) tipo="refactor" ;;
    6) tipo="test" ;;
    7) tipo="chore" ;;
    *) echo "Tipo inválido"; exit 1 ;;
esac

# Perguntar escopo
read -p "Escopo (opcional): " escopo

# Perguntar descrição
read -p "Descrição: " descricao

# Montar commit
if [ -n "$escopo" ]; then
    commit="$tipo($escopo): $descricao"
else
    commit="$tipo: $descricao"
fi

echo ""
echo "Commit: $commit"
read -p "Confirmar? (y/n): " confirm

if [ "$confirm" = "y" ]; then
    git commit -m "$commit"
    echo "✅ Commit realizado!"
else
    echo "❌ Commit cancelado"
fi
```

---

**Última atualização**: 2025-01-13  
**Versão**: 2.0  
**Responsável**: Technical Writer
