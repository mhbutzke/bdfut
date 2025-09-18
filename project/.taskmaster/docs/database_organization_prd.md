# PRD: Organização e Padronização das Tabelas do Supabase - BDFut

## 1. Visão Geral

### Objetivo Principal
Organizar e padronizar as tabelas do banco de dados Supabase do projeto BDFut, garantindo que todas as tabelas tenham as colunas necessárias correspondentes às respostas da API Sportmonks, com foco especial na tabela `fixtures` como centro agregador de informações.

### Contexto
O projeto BDFut coleta dados da API Sportmonks e armazena no Supabase. Atualmente temos 25 tabelas principais, mas precisamos:
- Padronizar estruturas de colunas
- Garantir que todas as tabelas tenham colunas correspondentes aos dados da API
- Otimizar a tabela `fixtures` como tabela principal agregadora
- Implementar views otimizadas para consultas

## 2. Escopo do Projeto

### Tabelas Principais Identificadas
- **fixtures** (67,085 registros) - Tabela central agregadora
- **teams** (14,561 registros) - Times
- **players** (78,340 registros) - Jogadores  
- **referees** (15,835 registros) - Árbitros
- **leagues** (113 registros) - Ligas
- **seasons** (1,920 registros) - Temporadas
- **match_events** (62,781 registros) - Eventos das partidas
- **match_statistics** (1,474 registros) - Estatísticas das partidas
- **match_lineups** (18,424 registros) - Escalações
- **venues** (2,575 registros) - Estádios
- **countries** (237 registros) - Países
- **states** (25 registros) - Estados das partidas
- **types** (1,124 registros) - Tipos de eventos
- **coaches** (115 registros) - Treinadores
- **standings** (25 registros) - Classificações
- **transfers** (25 registros) - Transferências
- **rounds** (25 registros) - Rodadas
- **stages** (6,590 registros) - Fases
- **expected_stats** (10 registros) - Estatísticas esperadas
- **match_referees** (399 registros) - Árbitros por partida
- **match_periods** (202 registros) - Períodos das partidas
- **match_participants** (317 registros) - Participantes das partidas

### Requisitos Funcionais

#### 1. Análise da Estrutura Atual
- Mapear todas as colunas existentes em cada tabela
- Identificar colunas faltantes comparando com respostas da API Sportmonks
- Documentar relacionamentos entre tabelas
- Identificar inconsistências de nomenclatura

#### 2. Padronização de Esquemas
- Criar migrations para adicionar colunas faltantes
- Padronizar nomenclatura de colunas (snake_case)
- Implementar constraints e índices adequados
- Definir tipos de dados corretos

#### 3. Otimização da Tabela Fixtures
- Adicionar todas as colunas de agregação necessárias
- Implementar campos calculados para estatísticas
- Criar índices compostos para consultas otimizadas
- Adicionar colunas de metadados para controle ETL

#### 4. Criação de Views
- Views para consultas de partidas completas
- Views agregadas por liga/temporada
- Views de estatísticas por time
- Views de ranking e classificações

#### 5. Sistema de Validação
- Scripts para validar integridade dos dados
- Verificação de referências entre tabelas
- Validação de dados obrigatórios
- Relatórios de qualidade de dados

### Requisitos Técnicos

#### Tecnologias
- PostgreSQL (Supabase)
- Python para scripts de migração
- SQL para criação de views e índices

#### Padrões
- Nomenclatura em snake_case
- Timestamps em UTC
- IDs como integers
- Metadados em JSONB quando necessário

## 3. Entregas

### Fase 1: Análise e Planejamento (1 semana)
- Mapeamento completo das tabelas atuais
- Comparação com estrutura da API Sportmonks
- Plano de migrations detalhado
- Identificação de views necessárias

### Fase 2: Implementação de Migrations (1 semana)
- Criação de migrations para colunas faltantes
- Implementação de índices e constraints
- Otimização da tabela fixtures
- Testes de performance

### Fase 3: Views e Otimizações (1 semana)
- Criação de views para consultas principais
- Implementação de índices compostos
- Scripts de validação de dados
- Documentação técnica

### Fase 4: Validação e Deploy (1 semana)
- Testes completos em ambiente de desenvolvimento
- Validação de integridade dos dados
- Deploy em produção
- Monitoramento pós-deploy

## 4. Critérios de Sucesso

- Todas as tabelas têm colunas correspondentes aos dados da API
- Tabela fixtures funciona como centro agregador eficiente
- Views otimizadas reduzem tempo de consulta em 50%
- Zero perda de dados durante migrations
- Documentação completa da estrutura final

## 5. Riscos e Mitigações

### Riscos
- Perda de dados durante migrations
- Impacto na performance durante alterações
- Inconsistências em dados existentes

### Mitigações
- Backup completo antes de qualquer alteração
- Migrations incrementais e reversíveis
- Testes extensivos em ambiente de desenvolvimento
- Rollback plan definido para cada migration

## 6. Recursos Necessários

- 1 Database Specialist (principal)
- 1 ETL Engineer (suporte)
- Ambiente de desenvolvimento isolado
- Backup completo da base de produção
- Ferramentas de monitoramento de performance
