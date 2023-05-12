#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE users;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "users" <<-EOSQL
    CREATE TABLE users(
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        PRIMARY KEY (username)
    );
    CREATE TABLE friends(
        username1 TEXT NOT NULL,
        username2 TEXT NOT NULL,
        PRIMARY KEY (username1,username2)
    );
EOSQL
