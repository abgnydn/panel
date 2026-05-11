-- Panel — Lakebase schema (Postgres-compatible)
-- Run via: psql $LAKEBASE_URL -f lakebase/001_schema.sql

BEGIN;

-- ---------------------------------------------------------------------------
-- workers: minimal anonymous record per worker session
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS workers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_of_origin   TEXT NOT NULL,            -- ISO-3166: 'PH', 'ID', 'BD', ...
    destination_country TEXT,                     -- 'SA', 'MY', 'SG', 'HK', 'AE'
    native_language     TEXT NOT NULL,            -- ISO-639: 'tl', 'id', 'en', ...
    age_range           TEXT,                     -- '18-25', '26-35', '36-50', '50+'
    consent_archive     BOOLEAN DEFAULT FALSE,    -- worker opt-in to contribute to case_archive
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- sessions: one row per contract review
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id           UUID REFERENCES workers(id) ON DELETE CASCADE,
    started_at          TIMESTAMPTZ DEFAULT NOW(),
    ended_at            TIMESTAMPTZ,
    contract_blob_path  TEXT,                     -- UC Volumes path for the uploaded image
    contract_text       TEXT,                     -- OCR + translation
    detected_language   TEXT,
    situation_text      TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_worker ON sessions(worker_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at DESC);

-- ---------------------------------------------------------------------------
-- agent_messages: each agent's structured output per session
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agent_messages (
    id          BIGSERIAL PRIMARY KEY,
    session_id  UUID REFERENCES sessions(id) ON DELETE CASCADE,
    agent       TEXT NOT NULL,                    -- 'lawyer' | 'translator' | 'regulator' | 'peer_advocate' | 'triage' | 'moderator'
    role        TEXT NOT NULL,                    -- 'analysis' | 'disagreement' | 'recommendation'
    content     JSONB NOT NULL,                   -- the agent's full JSON output
    confidence  REAL,
    latency_ms  INTEGER,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_messages_session ON agent_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_messages_agent ON agent_messages(agent);

-- ---------------------------------------------------------------------------
-- case_archive: anonymized historical cases (ILO + opt-in worker submissions)
-- powers the Peer Advocate via vector + SQL search
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS case_archive (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source              TEXT NOT NULL,            -- 'ilo' | 'amnesty' | 'hrw' | 'worker_consent'
    source_ref          TEXT,                     -- ILO publication ID, etc.
    country_of_origin   TEXT,
    destination_country TEXT,
    clause_category     TEXT,                     -- 'passport_retention' | 'wage_deduction' | 'live_in_isolation' | ...
    outcome             TEXT,                     -- 'resolved_favorably' | 'worker_returned_early' | 'abuse_reported' | 'unresolved'
    anonymized_facts    TEXT NOT NULL,
    year                INTEGER,
    embedding           VECTOR(1024),             -- bge-large or similar
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_case_archive_clause ON case_archive(clause_category);
CREATE INDEX IF NOT EXISTS idx_case_archive_destination ON case_archive(destination_country);
CREATE INDEX IF NOT EXISTS idx_case_archive_outcome ON case_archive(outcome);
CREATE INDEX IF NOT EXISTS idx_case_archive_embedding
    ON case_archive USING ivfflat (embedding vector_cosine_ops);

-- ---------------------------------------------------------------------------
-- recommendations: final synthesized output per session
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recommendations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID REFERENCES sessions(id) ON DELETE CASCADE,
    urgency_score   INTEGER CHECK (urgency_score BETWEEN 0 AND 10),
    summary_l1      TEXT NOT NULL,                -- summary in worker's L1
    summary_en      TEXT NOT NULL,                -- English for the dashboard
    action_items    JSONB NOT NULL,
    contacts        JSONB,                        -- embassy / NGO / hotline contacts
    disagreements   JSONB,                        -- the disagreement reel
    legal_disclaimer_l1 TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recommendations_session ON recommendations(session_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_urgency ON recommendations(urgency_score DESC);

-- ---------------------------------------------------------------------------
-- directory tables (seeded from open data)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS embassy_directory (
    id                  BIGSERIAL PRIMARY KEY,
    country_of_origin   TEXT NOT NULL,            -- whose embassy
    located_in_country  TEXT NOT NULL,            -- where the embassy is
    name                TEXT NOT NULL,
    phone               TEXT,
    whatsapp            TEXT,
    email               TEXT,
    is_24h_hotline      BOOLEAN DEFAULT FALSE,
    address             TEXT,
    languages           TEXT[]
);

CREATE TABLE IF NOT EXISTS ngo_directory (
    id                  BIGSERIAL PRIMARY KEY,
    name                TEXT NOT NULL,
    coverage_country    TEXT NOT NULL,            -- country where NGO operates
    serves_workers_from TEXT[],                   -- origin countries served
    focus_areas         TEXT[],                   -- 'trafficking', 'domestic_workers', 'wage_theft', ...
    phone               TEXT,
    whatsapp            TEXT,
    languages           TEXT[]
);

COMMIT;

-- Dashboard / aggregate views (the AI/BI "NGO heatmap" sources)

CREATE OR REPLACE VIEW v_abuse_pattern_heatmap AS
SELECT
    w.country_of_origin,
    w.destination_country,
    ca.clause_category,
    COUNT(*) AS cases,
    SUM(CASE WHEN ca.outcome IN ('worker_returned_early', 'abuse_reported') THEN 1 ELSE 0 END) AS bad_outcomes,
    ROUND(
        SUM(CASE WHEN ca.outcome IN ('worker_returned_early', 'abuse_reported') THEN 1 ELSE 0 END)::numeric
        / NULLIF(COUNT(*), 0) * 100, 1
    ) AS pct_bad_outcome
FROM case_archive ca
LEFT JOIN sessions s ON s.id::text = ca.source_ref
LEFT JOIN workers w ON w.id = s.worker_id
GROUP BY 1, 2, 3
ORDER BY pct_bad_outcome DESC NULLS LAST;

CREATE OR REPLACE VIEW v_urgent_sessions_24h AS
SELECT
    s.id AS session_id,
    s.started_at,
    w.country_of_origin,
    w.destination_country,
    w.native_language,
    r.urgency_score,
    r.summary_en
FROM sessions s
JOIN workers w ON w.id = s.worker_id
JOIN recommendations r ON r.session_id = s.id
WHERE r.urgency_score >= 7
  AND s.started_at >= NOW() - INTERVAL '24 hours'
ORDER BY r.urgency_score DESC, s.started_at DESC;
