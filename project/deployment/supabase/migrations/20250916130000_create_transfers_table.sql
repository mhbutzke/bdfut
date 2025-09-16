-- Migração: Criar tabela transfers
-- Data: 2025-09-16
-- Objetivo: Implementar sistema de transferências (TASK-ETL-023)

-- Criar tabela transfers
CREATE TABLE IF NOT EXISTS transfers (
    id BIGSERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE NOT NULL,
    player_id BIGINT,
    from_team_id BIGINT,
    to_team_id BIGINT,
    transfer_date DATE,
    transfer_type TEXT, -- permanent, loan, free, etc.
    fee_amount BIGINT,
    fee_currency TEXT DEFAULT 'EUR',
    contract_duration INTEGER, -- em meses
    announcement_date DATE,
    details JSONB, -- dados adicionais da API
    
    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_transfers_player FOREIGN KEY (player_id) REFERENCES players(id),
    CONSTRAINT fk_transfers_from_team FOREIGN KEY (from_team_id) REFERENCES teams(id),
    CONSTRAINT fk_transfers_to_team FOREIGN KEY (to_team_id) REFERENCES teams(id),
    CONSTRAINT chk_transfer_date CHECK (transfer_date IS NULL OR transfer_date >= '2000-01-01'),
    CONSTRAINT chk_fee_amount CHECK (fee_amount IS NULL OR fee_amount >= 0),
    CONSTRAINT chk_contract_duration CHECK (contract_duration IS NULL OR contract_duration > 0)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_transfers_sportmonks_id ON transfers(sportmonks_id);
CREATE INDEX IF NOT EXISTS idx_transfers_player_id ON transfers(player_id);
CREATE INDEX IF NOT EXISTS idx_transfers_from_team_id ON transfers(from_team_id);
CREATE INDEX IF NOT EXISTS idx_transfers_to_team_id ON transfers(to_team_id);
CREATE INDEX IF NOT EXISTS idx_transfers_transfer_date ON transfers(transfer_date);
CREATE INDEX IF NOT EXISTS idx_transfers_transfer_type ON transfers(transfer_type);
CREATE INDEX IF NOT EXISTS idx_transfers_created_at ON transfers(created_at);

-- Trigger para updated_at
CREATE OR REPLACE FUNCTION update_transfers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_transfers_updated_at
    BEFORE UPDATE ON transfers
    FOR EACH ROW
    EXECUTE FUNCTION update_transfers_updated_at();

-- Comentários para documentação
COMMENT ON TABLE transfers IS 'Tabela de transferências de jogadores entre clubes';
COMMENT ON COLUMN transfers.sportmonks_id IS 'ID único da transferência na API Sportmonks';
COMMENT ON COLUMN transfers.player_id IS 'Referência ao jogador transferido';
COMMENT ON COLUMN transfers.from_team_id IS 'Time de origem da transferência';
COMMENT ON COLUMN transfers.to_team_id IS 'Time de destino da transferência';
COMMENT ON COLUMN transfers.transfer_date IS 'Data oficial da transferência';
COMMENT ON COLUMN transfers.transfer_type IS 'Tipo: permanent, loan, free, etc.';
COMMENT ON COLUMN transfers.fee_amount IS 'Valor da transferência em centavos';
COMMENT ON COLUMN transfers.fee_currency IS 'Moeda da transferência (padrão EUR)';
COMMENT ON COLUMN transfers.contract_duration IS 'Duração do contrato em meses';
COMMENT ON COLUMN transfers.details IS 'Dados JSON adicionais da API Sportmonks';
