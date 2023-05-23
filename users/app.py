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

def all_users(limit=1000):
    cur = conn.cursor()
    cur.execute(f"SELECT username, password FROM users LIMIT {limit};")
    return cur.fetchall()

class Register(Resource):
    def post(self):
        args = flask_request.args
        return add_user(args['username'], args['password'])
    
class Login(Resource):
    def post(self):
        args = flask_request.args
        return username_password_exists(args['username'], args['password'])
    
class AllUsersResource(Resource):
    def get(self):
        args = flask_request.args
        return all_users
    
class UserExists(Resource):
    def get(self):
        args = flask_request.args
        return username_exists(args['username'])




api.add_resource(AllUsersResource, '/users/')
api.add_resource(UserExists, '/users/exist/')
api.add_resource(Register, '/users/register/')
api.add_resource(Login, '/users/login/')

