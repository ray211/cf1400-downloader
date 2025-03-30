CREATE DATABASE cf_1400;

CREATE TABLE cf1400_files (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    pdf_filename TEXT NOT NULL UNIQUE,
    file_url TEXT NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_to_excel BOOLEAN DEFAULT FALSE
);

CREATE TABLE cf1400_excel_files (
    id SERIAL PRIMARY KEY,
    cf1400_file_id INTEGER NOT NULL REFERENCES cf1400_files(id) ON DELETE CASCADE,
    excel_filename TEXT NOT NULL UNIQUE,
    converted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE TABLE foreign_trade_entrances  (
    filing_port_code         INTEGER,
    filing_port_name         TEXT,
    manifest_number          TEXT,
    filing_date              DATE,
    last_domestic_port       TEXT,
    vessel_name              TEXT,
    last_foreign_port        TEXT,
    call_sign_number         TEXT,
    imo_number               TEXT,
    last_foreign_country     TEXT,
    trade_code               TEXT,
    official_number          TEXT,
    voyage_number            TEXT,
    vessel_flag              TEXT,
    vessel_type_code         TEXT,
    agent_name               TEXT,
    pax                      TEXT,
    total_crew               INTEGER,
    operator_name            TEXT,
    draft                    TEXT,
    tonnage                 NUMERIC,
    owner_name               TEXT,
    dock_name                TEXT,
    dock_intrans             TEXT
);

ALTER TABLE foreign_trade_entrances
ADD COLUMN cf1400_excel_file_id INTEGER REFERENCES cf1400_excel_files(id);
