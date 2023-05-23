from flask import Flask, Response
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
import requests


parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('username1')
parser.add_argument('username2')

app = Flask("friends")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="friends", user="postgres", password="postgres", host="friends_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def checK_friends(username1,username2):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM friends WHERE (username1 = %s AND username2 = %s) OR (username1 = %s AND username2 = %s);", (username1, username2, username2, username1))
    return bool(cur.fetchone()[0])  # Either True or False

def username_exists(username):
    try:
        response = requests.get("http://users:5000/users/exist/?username=" + username)
        if response.status_code == 200 : return response.json() 
        else:
            return False
    except requests.exceptions.ConnectionError as e:
            # Handle the connection error when 'friends' host cannot be reached
            print("Error: Connection to 'friends' host failed.",flush=True)
    
def add_friends(username1,username2):
    if username1 != username2:
        if username_exists(username2):
            if not checK_friends(username1,username2):
                cur = conn.cursor()
                cur.execute("INSERT INTO friends (username1, username2) VALUES (%s, %s);", (username1, username2))
                conn.commit()
                return True
    return False

def all_friends(username):
    cur = conn.cursor()
    cur.execute("SELECT CASE WHEN username1 = %s THEN username2 WHEN username2 = %s THEN username1 ELSE NULL END AS friend_username FROM friends WHERE username1 = %s OR username2 = %s;", (username,username,username,username))
    return cur.fetchall()

def activities(username):
    friends = all_friends(username)
    friend_usernames = []
    if friends: friend_usernames = [friend[0] if friend[0] != username else friend[1] for friend in friends]
    friend_data = []
    cur = conn.cursor()
    for friend_username in friend_usernames:
        cur.execute("SELECT CASE WHEN username1 = %s THEN username2 WHEN username2 = %s THEN username1 ELSE NULL END AS friend_username, created_at FROM friends WHERE (username1 = %s OR username2 = %s) AND (CASE WHEN username1 = %s THEN username2 WHEN username2 = %s THEN username1 ELSE NULL END) <> %s;", (friend_username, friend_username, friend_username, friend_username, friend_username, friend_username, username))
        friend_info = cur.fetchall()
        if friend_info:
            for info in friend_info:
                friend, timestamp = info
                friend_info_with_status = (friend_username, timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'Added ' + friend + ' as a friend')
                friend_data.extend(friend_info_with_status)
    formatted_data = []
    if friend_data:
        formatted_data  = [(friend_data[i], friend_data[i+1], friend_data[i+2]) for i in range(0, len(friend_data), 3)]
    return formatted_data
   
class AddFriend(Resource):
    def post(self):
        args = flask_request.args
        return add_friends(args['username1'],args['username2'])
    
class Friends(Resource):
    def get(self):
        args = flask_request.args
        return all_friends(args['username'])
    
class FriendsExist(Resource):
    def get(self):
        args = flask_request.args
        return checK_friends(args['username1'],args['username2'])

class FriendsActivities(Resource):
    def get(self):
        args = flask_request.args
        return activities(args['username'])


api.add_resource(AddFriend, '/friends/add/')
api.add_resource(Friends, '/friends/')
api.add_resource(FriendsExist, '/friends/exist/')
api.add_resource(FriendsActivities, '/friends/activities/')

