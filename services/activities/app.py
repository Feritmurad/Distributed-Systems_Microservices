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


def get_activities():
    pass


def friends_exists(username1,username2):
    print(username1,username2,flush=True)
    response = requests.get("http://friends:5000/friends/exist/?username1=" + username1 + "&username2=" + username2)
    print(response.status_code,flush=True)
    if response.status_code == 200 : return response.json()  # TODO: call
    else:
        return False


class Activities(Resource):
    def get(self):
        args = flask_request.args
        return get_activities()
    
api.add_resource(Activities, '/activites/')