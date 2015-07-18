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
    if not mongo.db.users.find_one({"username": username}):
        user = UserModel(username)
        mongo.db.users.insert(user.to_json())

    return "done"

@app.route('/data/payLoan')
def pay_loan():
    username = request.args.get('username')
    loan_id = request.args.get('loan_id')

    user = mongo.db.users.find_one({"username": username}):

    if not user:
        return


@app.route('/data/requestLoan')
def request_loan():
    from_user = request.args.get('from')

if __name__ == "__main__":
    app.run()
