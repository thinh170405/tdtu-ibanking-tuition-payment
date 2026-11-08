CREATE TABLE IF NOT EXISTS email_messages (
  message_id VARCHAR(100) PRIMARY KEY,
  payload_hash VARCHAR(64) NOT NULL,
  status VARCHAR(20) NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
