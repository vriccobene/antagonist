DROP TYPE IF EXISTS annotator_type;
CREATE TYPE annotator_type AS ENUM (
    'human',
    'algorithm'
);

-- CREATE DATABASE
CREATE DATABASE network_anomalies;
GRANT ALL PRIVILEGES ON DATABASE network_anomalies TO postgres;

\c network_anomalies

-- CREATE TABLE
-- DROP TABLE IF EXISTS network_anomaly;
-- Create the table containing all the network_anomalies
CREATE TABLE IF NOT EXISTS "network_anomaly" (
    id uuid DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    descript VARCHAR(1000),
    annotator_id uuid NOT NULL,
    version INTEGER NOT NULL,
    state VARCHAR(100) NOT NULL,
    PRIMARY KEY(id, version, state)
    -- TODO Add foreing key to annotator
);

CREATE TABLE IF NOT EXISTS "annotator" (
    id uuid DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    annotator_type VARCHAR(100) NOT NULL,
    version INTEGER,
    PRIMARY KEY(name, annotator_type)
);

-- CREATE TABLE
-- DROP TABLE IF EXISTS symptom;
-- Create the table containing all the symptoms
CREATE TABLE IF NOT EXISTS "symptom" (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    event_id uuid,
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
  tag_value VARCHAR(1000),
  PRIMARY KEY(symptom_id, tag_key, tag_value)
  -- TODO Add foreing key to symptom
);

-- CREATE TABLE
-- DROP TABLE IF EXISTS contains;
CREATE TABLE IF NOT EXISTS "network_anomaly_contains_symptom" (
    network_anomaly_id uuid NOT NULL,
    symptom_id uuid NOT NULL,
    -- symptom_concern SMALLINT,
    PRIMARY KEY(network_anomaly_id, symptom_id),
    CONSTRAINT network_anomaly
      FOREIGN KEY(network_anomaly_id) 
	  REFERENCES network_anomaly(id),
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
GRANT ALL PRIVILEGES ON DATABASE network_anomalies TO antagonist;
GRANT USAGE ON SCHEMA public TO antagonist;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO antagonist;