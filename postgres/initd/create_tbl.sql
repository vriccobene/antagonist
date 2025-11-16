-- CREATE DATABASE
CREATE DATABASE antagonist;
GRANT ALL PRIVILEGES ON DATABASE antagonist TO postgres;

-- Enable the uuid-ossp extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- TODO Remove the hardcoded generation of the password from here
CREATE USER antagonist WITH ENCRYPTED PASSWORD 'antagonist-password';
GRANT ALL PRIVILEGES ON DATABASE antagonist TO antagonist;
GRANT USAGE ON SCHEMA public TO antagonist;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO antagonist;
