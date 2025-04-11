-- Core tables needed for application bootstrap

-- Config table for storing application configuration and security keys
CREATE TABLE IF NOT EXISTS config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL UNIQUE,
    value TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissions on table and sequence
GRANT ALL PRIVILEGES ON TABLE config TO homelab_discord_bot;
GRANT USAGE, SELECT ON SEQUENCE config_id_seq TO homelab_discord_bot; 