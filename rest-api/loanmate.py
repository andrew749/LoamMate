import pdb
import json
from flask import Flask
from flask import request
from flask.ext.pymongo import PyMongo
from data import UserModel

import braintree

braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id="",
                                  public_key="",
                                  private_key="")


app = Flask(__name__)
mongo = PyMongo(app)

@app.route("/")
def hello():
    return str(mongo.db.users.count())

@app.route('/data/login/<username>')
def login(username):
    if not mongo.db.users.find_one({"username": username}):
        user = UserModel(username)
        mongo.db.users.insert(user.to_dict())

    return "done"

@app.route('/data/payLoan')
def pay_loan():
    username = request.args.get('username')
    loan_id = float(request.args.get('loan_id'))

    user = mongo.db.users.find_one({"username": username})

    if not user:
        return "NO GOOD"

    loans_outstanding = user['loans_outstanding']
    for loan in loans_outstanding:
        if loan['id'] == loan_id:
            for username in loan['chain']:
                debt_paid_user = mongo.db.users.find_one({"username": username})
                granted = (g for g in debt_paid_user['loans_granted'] if g['id'] == loan_id).next()
                debt_paid_user['loans_granted'] = filter(lambda x: x['id'] != loan_id, debt_paid_user['loans_granted'])
                debt_paid_user['lending_balance'] += granted['amount']
                mongo.db.users.update({"username": debt_paid_user['username']}, {"$set": debt_paid_user}, upsert=False)

    loans_outstanding = filter(lambda x: x['id'] != loan_id, loans_outstanding)
    user['loans_outstanding'] = loans_outstanding

    mongo.db.users.update({"username": user['username']}, {"$set": user})

    return "GREAT"

@app.route('/data/requestLoan')
def request_loan():
    username = request.args.get('username')
    amount = request.args.get('amount')
    user = mongo.db.users.find_one({"username": username})

    if not user:
        return "NO GOOD"

    trusted = user['trusted']

    if not len(trusted):
        return "NO GOOD"

    for trusted_user in trusted:
        trusted_user
        pass

def find_chain(username, loan_id, amount):
    user = mongo.db.users.find_one({"username": username})
    trusted = user['trusted']
    for trusted_username in trusted:
        trusted_user = mongo.db.users.find_one({"username": trusted_username})
        trusted_user['lending_balance'] -= amount
        trusted_user['loans_granted'].append({'id': loan_id, 'amount': amount})
        if trusted_user['lending_balance'] >= amount:
            mongo.db.users.update({"username": trusted_username, "$set": trusted_user})
            return trusted_username


@app.route('/data/userData/<username>')
def get_user_data(username):
    return braintree.ClientToken.generate()
   # entry=mongo.db.user.find_one({"username":username})
   # return json.dumps({"lending_balance":entry["lending_balance"],"username":entry["username"],"loans":[{}for x in entry["loans"]]},indent=4)


if __name__ == "__main__":
    app.run(debug=True)
