import pdb
import json
from flask import Flask
from flask import request
from flask.ext.pymongo import PyMongo
from data import UserModel

app = Flask(__name__)
mongo = PyMongo(app)

@app.route("/")
def hello():
    return str(mongo.db.users.count())

@app.route('/data/login/<username>')
def login(username):
    if mongo.db.user.find_one({"username": username}):
        user = UserModel(username)
        mongo.db.user.insert(user.to_json())
    else:
        mongo.db.find_one({"username": username})['lending_balance']

    return "done"

@app.route('/data/payLoan')
def pay_loan():
    from_user = request.args.get('from')
    to_user = request.args.get('to')
    amount = request.args.get('amount')

@app.route('/data/requestLoan')
def request_loan():
    from_user = request.args.get('from')

@app.route('/data/userData/<username>')
def get_user_data(username):
    pass

if __name__ == "__main__":
    app.run()
