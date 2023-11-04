-- DROP TYPE IF EXISTS actor;
CREATE TYPE ACTOR AS ENUM (
    'human',
    'algorithm',
);

-- CREATE DATABASE
CREATE DATABASE incidents;

CREATE USER grafana WITH ENCRYPTED PASSWORD 'grafana-password';
GRANT ALL PRIVILEGES ON DATABASE incidents TO grafana;
GRANT ALL PRIVILEGES ON DATABASE incidents TO postgres;

\c incidents

-- CREATE TABLE
-- DROP TABLE IF EXISTS incident;
CREATE TABLE IF NOT EXISTS "incident" (
    id SERIAL PRIMARY KEY,
    tag_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    descript VARCHAR(1000),
    concern SMALLINT,
    source ACTOR,
    source_name VARCHAR(200)
);

-- CREATE TABLE
-- DROP TABLE IF EXISTS symptom;
CREATE TABLE IF NOT EXISTS "symptom" (
    id SERIAL PRIMARY KEY,
    tag_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    descript VARCHAR(1000),
    source ACTOR,
    source_name VARCHAR(200)
);

-- CREATE TABLE
-- DROP TABLE IF EXISTS metric;
CREATE TABLE IF NOT EXISTS "metric" (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(1000)
);

-- CREATE TABLE
-- DROP TABLE IF EXISTS contains;
CREATE TABLE IF NOT EXISTS "contains" (
    incident_id INTEGER NOT NULL,
    symptom_id INTEGER NOT NULL,
    symptom_concern SMALLINT,
    PRIMARY KEY(incident_id, symptom_id),
    CONSTRAINT incident
      FOREIGN KEY(incident_id) 
	  REFERENCES incident(id),
    CONSTRAINT symptom
      FOREIGN KEY(symptom_id) 
	  REFERENCES symptom(id)
);

-- CREATE TABLE
-- DROP TABLE IF EXISTS affects;
CREATE TABLE IF NOT EXISTS "affects" (
    symptom_id INTEGER NOT NULL,
    metric_id INTEGER NOT NULL,
    PRIMARY KEY(symptom_id, metric_id),
    CONSTRAINT symptom
      FOREIGN KEY(symptom_id) 
	  REFERENCES symptom(id),
    CONSTRAINT metric
      FOREIGN KEY(metric_id) 
	  REFERENCES metric(id)
);
