from flask import Flask, Response
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

def get_username_of_playlist(playlist_id):
    cur = conn.cursor()
    cur.execute("SELECT username FROM playlists WHERE id = %s;", (playlist_id,))
    (username,) = cur.fetchone()  # using tuple unpacking
    return username

def get_title_of_playlist(playlist_id):
    cur = conn.cursor()
    cur.execute("SELECT title FROM playlists WHERE id = %s;", (playlist_id,))
    (username,) = cur.fetchone()  # using tuple unpacking
    return username

def username_exists(username):
    try:
        response = requests.get("http://users:5000/users/exist/?username=" + username)
        if response.status_code == 200 : return response.json()  
        else:
            return False
    except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'users' host cannot be reached
            print("Error: Connection to 'users' host failed.",flush=True)
            raise
    
def friends_exists(username1,username2):
    try:
        response = requests.get("http://friends:5000/friends/exist/?username1=" + username1 + "&username2=" + username2)
        if response.status_code == 200 : return response.json()  
        else:
            return False
    except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'friends' host cannot be reached
            print("Error: Connection to 'friends' host failed.",flush=True)
            raise
    
def get_friends(username):
    try:
        response = requests.get("http://friends:5000/friends/?username=" + username)
        if response.status_code == 200 : return response.json()
        else:
            return False
    except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'friends' host cannot be reached
            print("Error: Connection to 'friends' host failed.",flush=True)
            raise

    
def song_exists(title,artist):
    try:
        response = requests.get("http://songs:5000/songs/exist/?title=" + title + "&artist=" + artist)
        if response.status_code == 200 : return response.json() 
        else:
            return False
    except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'songs' host cannot be reached
            print("Error: Connection to 'songs' host failed.",flush=True)

def add_playlist(title,username):
    try:
        if username_exists(username):
            cur = conn.cursor()
            cur.execute("INSERT INTO playlists (title, username) VALUES (%s, %s);", (title, username))
            conn.commit()
            return True
        return False
    except requests.exceptions.ConnectionError as e:
        headers = {'Content-Type': 'text/plain'}
        status = 503
        message = "Error: Connection to 'users' host failed."
        return Response(message, status=status, headers=headers)

def share_playlist(playlist_id,username):
    try:
        shared_by_username = get_username_of_playlist(playlist_id)
        if friends_exists(username,shared_by_username):
            cur = conn.cursor()
            cur.execute("INSERT INTO playlists_share (playlist_id, shared_by_username, shared_with_username) VALUES (%s, %s, %s);", (playlist_id, shared_by_username, username))
            conn.commit()
            return True
        return False
    except requests.exceptions.ConnectionError as e:
        headers = {'Content-Type': 'text/plain'}
        status = 503
        message = "Error: Connection to 'friends' host failed."
        return Response(message, status=status, headers=headers)



def all_playlists(username):
    try:
        if username_exists(username):
            cur = conn.cursor()
            cur.execute("SELECT id, title FROM playlists WHERE username = %s", (username,))
            return cur.fetchall()
        return False
    except requests.exceptions.ConnectionError as e:
        headers = {'Content-Type': 'text/plain'}
        status = 503
        message = "Error: Connection to 'users' host failed."
        return Response(message, status=status, headers=headers)

def shared_playlists(shared_with_username):
    try:
        if username_exists(shared_with_username):
            cur = conn.cursor()
            cur.execute("SELECT p.id, p.title FROM playlists p JOIN playlists_share s ON p.id = s.playlist_id WHERE s.shared_with_username = %s;", (shared_with_username,))
            return cur.fetchall()
        return False
    except requests.exceptions.ConnectionError as e:
        headers = {'Content-Type': 'text/plain'}
        status = 503
        message = "Error: Connection to 'users' host failed."
        return Response(message, status=status, headers=headers)

def add_song(playlist_id,title,artist,username):
    try:
        if song_exists(title,artist):
            cur = conn.cursor()
            cur.execute("INSERT INTO playlists_song (playlist_id, username, title, artist) VALUES (%s, %s, %s, %s);", (playlist_id, username, title, artist))
            conn.commit()
            return True
        return False
    except requests.exceptions.ConnectionError as e:
        headers = {'Content-Type': 'text/plain'}
        status = 503
        message = "Error: Connection to 'songs' host failed."
        return Response(message, status=status, headers=headers)

def all_songs_playlist(playlist_id): 
    cur = conn.cursor()
    cur.execute("SELECT title,artist FROM playlists_song WHERE playlist_id = %s;", (playlist_id,))
    return cur.fetchall()

def activities(username):
    try:
        friends = get_friends(username)
        friend_usernames = []
        if friends: friend_usernames = [friend[0] if friend[0] != username else friend[1] for friend in friends]
        friend_data = []
        for friend_username in friend_usernames:
            cur = conn.cursor()
            cur.execute("SELECT username, created_at, title  FROM playlists WHERE username = %s", (friend_username,))
            playlists = cur.fetchall()
            cur.execute("SELECT shared_by_username, created_at, shared_with_username, playlist_id   FROM playlists_share WHERE shared_by_username = %s", (friend_username,))
            shared = cur.fetchall()
            cur.execute("SELECT username, created_at, title, artist, playlist_id FROM playlists_song WHERE username = %s", (friend_username,))
            adding_song = cur.fetchall()
            if playlists:
                for info in playlists:
                    user, timestamp, title  = info
                    friend_info_with_status = (user, timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'Created the playlist: ' + title)
                    friend_data.extend(friend_info_with_status)
            if shared:
                for info in shared:
                    user, timestamp, shared_user, playlist_id = info
                    playlist_name = get_title_of_playlist(playlist_id)
                    friend_info_with_status = (user, timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'Shared the playlist ' + '\'' + playlist_name + '\' ' + 'with ' + shared_user)
                    friend_data.extend(friend_info_with_status)
            if adding_song:
                for info in adding_song:
                    user, timestamp, title, artist, playlist_id = info
                    playlist_name = get_title_of_playlist(playlist_id)
                    friend_info_with_status = (user, timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'Added the song ' + '\'' + title + '\' ' + 'by ' + '\'' + artist + '\'' + ' to the playlist' + ' \'' + playlist_name + '\'' )
                    friend_data.extend(friend_info_with_status)
        formatted_data = []
        if friend_data:
            formatted_data  = [(friend_data[i], friend_data[i+1], friend_data[i+2]) for i in range(0, len(friend_data), 3)]
        return formatted_data
    except requests.exceptions.ConnectionError as e:
        headers = {'Content-Type': 'text/plain'}
        status = 503
        message = "Error: Connection to 'friends' host failed."
        return Response(message, status=status, headers=headers)



class PlaylistActivities(Resource):
    def get(self):
        args = flask_request.args
        return activities(args['username'])

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
        return add_song(args['playlist_id'], args['title'],args['artist'],args['username'])
    
class AllSongsPlaylistResource(Resource):
    def get(self):
        args = flask_request.args
        return all_songs_playlist(args['playlist_id'])

api.add_resource(AllSongsPlaylistResource, '/playlists/songs/')
api.add_resource(AddSong, '/playlists/add_song/')
api.add_resource(AddPlaylist, '/playlists/add_playlist/')
api.add_resource(SharePlaylist, '/playlists/share_playlist/')
api.add_resource(MyPlaylist, '/playlists/')
api.add_resource(SharedPlaylist, '/playlists/shared/')
api.add_resource(PlaylistActivities, '/playlists/activities/')

