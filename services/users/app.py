from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('username1')
parser.add_argument('username2')

app = Flask("users")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="users", user="postgres", password="postgres", host="users_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def username_exists(username):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE username = %s;", (username,))
    return bool(cur.fetchone()[0])  # Either True or False

def username_password_exists(username,password):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE username = %s AND password = %s;", (username, password))
    return bool(cur.fetchone()[0])  # Either True or False

def add_user(username, password):
    if not username_exists(username):
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s);", (username, password))
        conn.commit()
        return True
    return False

def checK_friends(username1,username2):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM friends WHERE (username1 = %s AND username2 = %s) OR (username1 = %s AND username2 = %s);", (username1, username2, username2, username1))
    return bool(cur.fetchone()[0])  # Either True or False

def add_friends(username1,username2):
    print(username2,flush=True)
    print(username1,flush=True)
    if username1 != username2:
        print("User can't add user",flush=True)
        if username_exists(username2):
            print("User2 exists",flush=True)
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

class Register(Resource):
    def post(self):
        args = flask_request.args
        return add_user(args['username'], args['password'])
    
class Login(Resource):
    def post(self):
        args = flask_request.args
        print(args['username'],flush=True)
        print(args['password'],flush=True)
        return username_password_exists(args['username'], args['password'])

   
class AddFriend(Resource):
    def post(self):
        args = flask_request.args
        return add_friends(args['username1'],args['username2'])
    
class Friends(Resource):
    def get(self):
        args = flask_request.args
        return all_friends(args['username'])





api.add_resource(Register, '/users/register/')
api.add_resource(Login, '/users/login/')
api.add_resource(AddFriend, '/users/add_friend/')
api.add_resource(Friends, '/users/friends/')

