-- Adicionar colunas faltantes à tabela types
-- Baseado na estrutura completa da Sportmonks API

-- Adicionar coluna code
ALTER TABLE types ADD COLUMN IF NOT EXISTS code VARCHAR(50);

-- Adicionar coluna model_type
ALTER TABLE types ADD COLUMN IF NOT EXISTS model_type VARCHAR(50);

-- Adicionar coluna stat_group
ALTER TABLE types ADD COLUMN IF NOT EXISTS stat_group VARCHAR(50);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_types_code ON types(code);
CREATE INDEX IF NOT EXISTS idx_types_model_type ON types(model_type);
CREATE INDEX IF NOT EXISTS idx_types_stat_group ON types(stat_group);

-- Comentários para documentação
COMMENT ON COLUMN types.code IS 'Código único do tipo de evento';
COMMENT ON COLUMN types.model_type IS 'Tipo de modelo (event, statistic, etc.)';
COMMENT ON COLUMN types.stat_group IS 'Grupo estatístico do evento';
