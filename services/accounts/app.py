from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('pwd')

app = Flask("accounts")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="accounts", user="postgres", password="postgres", host="accounts_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def username_exists(name):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM accounts WHERE name = %s", (name,))
    return bool(cur.fetchone()[0])  # Either True or False

def add_user(name, pwd):
    if not username_exists(name):
        cur = conn.cursor()
        cur.execute("INSERT INTO accounts (name, pwd) VALUES (%s, %s);", (name, pwd))
        conn.commit()
        return True
    return False

class Register(Resource):
    def post(self):
        args = flask_request.args
        return add_user(args['name'], args['pwd'])



api.add_resource(Register, '/accounts/register/')

