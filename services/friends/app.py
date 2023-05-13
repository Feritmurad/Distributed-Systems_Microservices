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

    response = requests.get("http://users:5000/users/exist/?username=" + username)
    print(response.status_code,flush=True)
    if response.status_code == 200 : return response.json()  # TODO: call
    else:
        return False
    
def add_friends(username1,username2):
    print(username2,flush=True)
    print(username1,flush=True)
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


api.add_resource(AddFriend, '/friends/add/')
api.add_resource(Friends, '/friends/')
api.add_resource(FriendsExist, '/friends/exist/')

