from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
import requests

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('artist')
parser.add_argument('title')
parser.add_argument('playlist_id')

app = Flask("playlists")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="playlists", user="postgres", password="postgres", host="playlists_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def get_username(playlist_id):
    cur = conn.cursor()
    cur.execute("SELECT username FROM playlists WHERE id = %s;", (playlist_id,))
    (username,) = cur.fetchone()  # using tuple unpacking
    print(username,flush=True)
    return username

def username_exists(username):
    response = requests.get("http://users:5000/users/exist/?username=" + username)
    print(response.status_code,flush=True)
    if response.status_code == 200 : return response.json()  # TODO: call
    else:
        return False
    
def friends_exists(username1,username2):
    print(username1,username2,flush=True)
    response = requests.get("http://friends:5000/friends/exist/?username1=" + username1 + "&username2=" + username2)
    print(response.status_code,flush=True)
    if response.status_code == 200 : return response.json()  # TODO: call
    else:
        return False

def add_playlist(title,username):
    if username_exists(username):
        cur = conn.cursor()
        cur.execute("INSERT INTO playlists (title, username) VALUES (%s, %s);", (title, username))
        conn.commit()
        return True
    return False

def share_playlist(playlist_id,username):
    shared_by_username = get_username(playlist_id)
    if friends_exists(username,shared_by_username):
        cur = conn.cursor()
        cur.execute("INSERT INTO playlists_share (playlist_id, shared_by_username, shared_with_username) VALUES (%s, %s, %s);", (playlist_id, shared_by_username, username))
        conn.commit()
        return True
    return False

def all_playlists(username):
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM playlists WHERE username = %s", (username,))
    return cur.fetchall()

def shared_playlists(shared_with_username):
    cur = conn.cursor()
    cur.execute("SELECT p.id, p.title FROM playlists p JOIN playlists_share s ON p.id = s.playlist_id WHERE s.shared_with_username = %s;", (shared_with_username,))
    return cur.fetchall()

def add_song(playlist_id,title,artist): ########### TODO check if song exists 
    cur = conn.cursor()
    cur.execute("INSERT INTO playlists_song (playlist_id, title, artist) VALUES (%s, %s, %s);", (playlist_id, title, artist))
    conn.commit()
    return True

def all_songs_playlist(playlist_id): 
    cur = conn.cursor()
    cur.execute("SELECT title,artist FROM playlists_song WHERE playlist_id = %s;", (playlist_id,))
    return cur.fetchall()

class AddPlaylist(Resource):
    def post(self):
        args = flask_request.args
        return add_playlist(args['title'], args['username'])
    
class SharePlaylist(Resource):
    def post(self):
        args = flask_request.args
        return share_playlist(args['playlist_id'], args['username'])
    
class MyPlaylist(Resource):
    def get(self):
        args = flask_request.args
        return all_playlists(args['username'])
    
class SharedPlaylist(Resource):
    def get(self):
        args = flask_request.args
        return shared_playlists(args['username'])

class AddSong(Resource):
    def post(self):
        args = flask_request.args
        return add_song(args['playlist_id'], args['title'],args['artist'])
    
class AllSongsPlaylistResource(Resource):
    def get(self):
        args = flask_request.args
        return all_songs_playlist(args['playlist_id'])

api.add_resource(AllSongsPlaylistResource, '/playlists/songs/')
api.add_resource(AddSong, '/playlists/add_song/')
api.add_resource(AddPlaylist, '/playlists/add/')
api.add_resource(SharePlaylist, '/playlists/share/')
api.add_resource(MyPlaylist, '/playlists/')
api.add_resource(SharedPlaylist, '/playlists/shared/')


"""
SELECT playlist.*
FROM playlist
JOIN playlist_share ON playlist.id = playlists_share.playlist_id
WHERE playlists_share.shared_with_user = 'jane';
"""