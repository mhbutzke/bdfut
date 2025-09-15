-- Criar tabela venues
CREATE TABLE IF NOT EXISTS venues (
    id SERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(255),
    capacity INTEGER,
    surface VARCHAR(100),
    country VARCHAR(100),
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela referees
CREATE TABLE IF NOT EXISTS referees (
    id SERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE,
    name VARCHAR(255) NOT NULL,
    common_name VARCHAR(255),
    firstname VARCHAR(255),
    lastname VARCHAR(255),
    nationality VARCHAR(100),
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela players
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE,
    name VARCHAR(255) NOT NULL,
    common_name VARCHAR(255),
    firstname VARCHAR(255),
    lastname VARCHAR(255),
    nationality VARCHAR(100),
    position_id INTEGER,
    position_name VARCHAR(100),
    date_of_birth DATE,
    height INTEGER,
    weight INTEGER,
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela coaches
CREATE TABLE IF NOT EXISTS coaches (
    id SERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE,
    name VARCHAR(255) NOT NULL,
    common_name VARCHAR(255),
    firstname VARCHAR(255),
    lastname VARCHAR(255),
    nationality VARCHAR(100),
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela states
CREATE TABLE IF NOT EXISTS states (
    id SERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(10),
    developer_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela types
CREATE TABLE IF NOT EXISTS types (
    id SERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE,
    name VARCHAR(255) NOT NULL,
    developer_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela countries
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    sportmonks_id INTEGER UNIQUE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(10),
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Adicionar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_venues_name ON venues(name);
CREATE INDEX IF NOT EXISTS idx_referees_name ON referees(name);
CREATE INDEX IF NOT EXISTS idx_players_name ON players(name);
CREATE INDEX IF NOT EXISTS idx_coaches_name ON coaches(name);
CREATE INDEX IF NOT EXISTS idx_states_name ON states(name);
CREATE INDEX IF NOT EXISTS idx_types_name ON types(name);
CREATE INDEX IF NOT EXISTS idx_countries_name ON countries(name);
