-- Keep the existing Spring catalog and saved looks intact.
-- Asset bytes, source documents and searchable NepAo records live in this database.
CREATE TABLE asset_files (
 relative_path VARCHAR(1024) PRIMARY KEY,
 content_type VARCHAR(160) NOT NULL,
 byte_size BIGINT NOT NULL CHECK (byte_size >= 0),
 sha256 VARCHAR(64) NOT NULL,
 file_data BYTEA NOT NULL,
 updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE data_documents (
 data_key VARCHAR(100) PRIMARY KEY,
 source_path VARCHAR(1024) NOT NULL,
 sha256 VARCHAR(64) NOT NULL,
 payload JSONB NOT NULL
);
CREATE TABLE wardrobe_items (
 character VARCHAR(10) NOT NULL,
 category VARCHAR(30) NOT NULL,
 item_key VARCHAR(100) NOT NULL,
 display_name TEXT NOT NULL,
 slot VARCHAR(40),
 metadata JSONB NOT NULL,
 PRIMARY KEY (character, category, item_key)
);
CREATE TABLE ai_catalog_entries (
 dataset_key VARCHAR(40) NOT NULL,
 entry_key VARCHAR(100) NOT NULL,
 metadata JSONB NOT NULL,
 PRIMARY KEY (dataset_key, entry_key)
);
CREATE TABLE ai_cultural_rules (
 rule_key VARCHAR(100) PRIMARY KEY,
 criterion VARCHAR(40),
 active BOOLEAN NOT NULL,
 verified BOOLEAN NOT NULL,
 metadata JSONB NOT NULL
);
CREATE TABLE quiz_questions (
 question_key VARCHAR(40) PRIMARY KEY,
 sort_order INTEGER NOT NULL UNIQUE,
 metadata JSONB NOT NULL
);
CREATE TABLE scoring_criteria (
 criterion_key VARCHAR(40) PRIMARY KEY,
 sort_order INTEGER NOT NULL UNIQUE,
 metadata JSONB NOT NULL
);
CREATE TABLE checklist_entries (
 section_key VARCHAR(40) NOT NULL,
 entry_key VARCHAR(100) NOT NULL,
 metadata JSONB NOT NULL,
 PRIMARY KEY (section_key, entry_key)
);
