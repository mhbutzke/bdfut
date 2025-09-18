-- Reorganizar tabela stages conforme estrutura da API Sportmonks
-- Baseado no exemplo fornecido pelo usuário

-- Remover colunas desnecessárias
ALTER TABLE stages DROP COLUMN IF EXISTS country_id;
ALTER TABLE stages DROP COLUMN IF EXISTS short_code;
ALTER TABLE stages DROP COLUMN IF EXISTS details;
ALTER TABLE stages DROP COLUMN IF EXISTS created_at;
ALTER TABLE stages DROP COLUMN IF EXISTS updated_at;

-- Renomear stage_id para id para seguir o padrão da API
ALTER TABLE stages RENAME COLUMN stage_id TO id;

-- Verificar se todas as colunas necessárias existem
-- As seguintes colunas já existem conforme o exemplo:
-- id (renomeado de stage_id)
-- sport_id
-- league_id  
-- season_id
-- type_id
-- name
-- sort_order
-- finished
-- is_current
-- starting_at
-- ending_at
-- games_in_current_week
-- tie_breaker_rule_id

-- Adicionar comentários para documentar a estrutura
COMMENT ON TABLE stages IS 'Tabela de estágios/fases das competições conforme API Sportmonks v3';
COMMENT ON COLUMN stages.id IS 'ID único do estágio (Sportmonks ID)';
COMMENT ON COLUMN stages.sport_id IS 'ID do esporte (1 = futebol)';
COMMENT ON COLUMN stages.league_id IS 'ID da liga/competição';
COMMENT ON COLUMN stages.season_id IS 'ID da temporada';
COMMENT ON COLUMN stages.type_id IS 'ID do tipo de estágio';
COMMENT ON COLUMN stages.name IS 'Nome do estágio (ex: Regular Season)';
COMMENT ON COLUMN stages.sort_order IS 'Ordem de classificação do estágio';
COMMENT ON COLUMN stages.finished IS 'Se o estágio foi finalizado';
COMMENT ON COLUMN stages.is_current IS 'Se é o estágio atual';
COMMENT ON COLUMN stages.starting_at IS 'Data de início do estágio';
COMMENT ON COLUMN stages.ending_at IS 'Data de fim do estágio';
COMMENT ON COLUMN stages.games_in_current_week IS 'Se há jogos na semana atual';
COMMENT ON COLUMN stages.tie_breaker_rule_id IS 'ID da regra de desempate';
