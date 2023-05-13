#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE playlists;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "playlists" <<-EOSQL

    CREATE SEQUENCE playlist_id_seq START 1;
    CREATE SEQUENCE playlist_song_id_seq START 1;

    CREATE TABLE playlists (
        id INTEGER DEFAULT NEXTVAL('playlist_id_seq'),
        title TEXT NOT NULL,
        username TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id)
    );

    CREATE TABLE playlists_share (
        playlist_id INTEGER NOT NULL,
        shared_by_username TEXT NOT NULL,
        shared_with_username TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (playlist_id, shared_with_username),
        FOREIGN KEY (playlist_id) REFERENCES playlists (id)
    );

    CREATE TABLE playlists_song (
        id INTEGER DEFAULT NEXTVAL('playlist_song_id_seq') PRIMARY KEY,
        playlist_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (playlist_id) REFERENCES playlists (id)
    );
EOSQL
