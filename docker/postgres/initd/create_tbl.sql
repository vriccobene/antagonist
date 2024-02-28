DROP TYPE IF EXISTS author_type;
CREATE TYPE author_type AS ENUM (
    'human',
    'algorithm'
);

-- CREATE DATABASE
CREATE DATABASE incidents;
GRANT ALL PRIVILEGES ON DATABASE incidents TO postgres;

\c incidents

-- CREATE TABLE
-- DROP TABLE IF EXISTS incident;
-- Create the table containing all the incidents
CREATE TABLE IF NOT EXISTS "incident" (
    id uuid DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    descript VARCHAR(1000),
    author_id uuid NOT NULL,
    version INTEGER NOT NULL,
    state VARCHAR(100) NOT NULL,
    PRIMARY KEY(id, version, state)
);

CREATE TABLE IF NOT EXISTS "author" (
    id uuid DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    author_type VARCHAR(100) NOT NULL,
    version INTEGER,
    PRIMARY KEY(name, author_type, version)
);

-- CREATE TABLE
-- DROP TABLE IF EXISTS symptom;
-- Create the table containing all the symptoms
CREATE TABLE IF NOT EXISTS "symptom" (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    event_id uuid,
    plane VARCHAR(1000),
    condition VARCHAR(1000),
    action VARCHAR(1000),
    cause VARCHAR(1000),
    pattern VARCHAR(1000),
    source_name VARCHAR(1000),
    source_type VARCHAR(1000),
    concern_score FLOAT,
    confidence_score FLOAT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    descript VARCHAR(1000)
);

-- CREATE TABLE
-- DROP TABLE IF EXISTS metric;
-- Create the table containing all the tags
CREATE TABLE IF NOT EXISTS "tag" (
  symptom_id uuid NOT NULL,
  tag_key VARCHAR(100) NOT NULL,
  tag_value VARCHAR(100),
  PRIMARY KEY(symptom_id, tag_key, tag_value)
);

CREATE TABLE IF NOT EXISTS "tag" (
    tag_id VARCHAR(1000),
    symptom_id INTEGER NOT NULL,
    PRIMARY KEY(tag_id, symptom_id)
);

-- CREATE TABLE
-- DROP TABLE IF EXISTS contains;
CREATE TABLE IF NOT EXISTS "incident_contains_symptom" (
    incident_id uuid NOT NULL,
    symptom_id uuid NOT NULL,
    -- symptom_concern SMALLINT,
    PRIMARY KEY(incident_id, symptom_id),
    CONSTRAINT incident
      FOREIGN KEY(incident_id) 
	  REFERENCES incident(id),
    CONSTRAINT symptom
      FOREIGN KEY(symptom_id) 
	  REFERENCES symptom(id)
);

-- -- CREATE TABLE
-- -- DROP TABLE IF EXISTS affects;
-- CREATE TABLE IF NOT EXISTS "affects" (
--     symptom_id INTEGER NOT NULL,
--     metric_id INTEGER NOT NULL,
--     PRIMARY KEY(symptom_id, metric_id),
--     CONSTRAINT symptom
--       FOREIGN KEY(symptom_id) 
-- 	  REFERENCES symptom(id),
--     CONSTRAINT metric
--       FOREIGN KEY(metric_id) 
-- 	  REFERENCES metric(id)
-- );

CREATE USER antagonist WITH ENCRYPTED PASSWORD 'antagonist-password';
GRANT ALL PRIVILEGES ON DATABASE incidents TO antagonist;
GRANT USAGE ON SCHEMA public TO antagonist;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO antagonist;