-- A API nunca conecta como superusuario: o RLS (FORCE ROW LEVEL SECURITY) vale para o dono das tabelas.
CREATE ROLE wedu LOGIN PASSWORD 'wedu' NOSUPERUSER NOBYPASSRLS;
CREATE DATABASE wedu OWNER wedu;
