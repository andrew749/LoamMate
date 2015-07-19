import pdb
import json
from flask import Flask
from flask import request
from flask.ext.pymongo import PyMongo
from data import UserModel

import braintree

braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id="wwygxtq3k3mp4cw2",
                                  public_key="k3j7655xc63f2jxx",
                                  private_key="b97a6538608cf5bd1460c3052efde146")

app = Flask(__name__)
mongo = PyMongo(app)
def createMerchantAccount(userId):
    result = braintree.MerchantAccount.create({
        'individual': {
                'first_name': userId,
                'last_name': userId+"trololol",
                'email': "andrewcod749@gmail.com",
                'phone': "4165287547",
                'date_of_birth': "1981-11-19",
                'ssn': "456-45-4567",
                'address': {
                            'street_address': "111 Main St",
                            'locality': "Chicago",
                            'region': "IL",
                            'postal_code': "60622"
                        }
            },
        'business': {
                'legal_name': "Jane's Ladders",
                'dba_name': "Jane's Ladders",
                'tax_id': "98-7654321",
                'address': {
                            'street_address': "111 Main St",
                            'locality': "Chicago",
                            'region': "IL",
                            'postal_code': "60622"
                        }
            },
        'funding': {
                'descriptor': "Blue Ladders",
                'destination': braintree.MerchantAccount.FundingDestination.Bank,
                'email': "funding@blueladders.com",
                'mobile_phone': "5555555555",
                'account_number': "1123581321",
                'routing_number': "071101307",
            },
        "tos_accepted": True,
        "master_merchant_account_id": "andrew749development",
        "id": userId
    })
    return result
@app.route("/")
def hello():
    return str(mongo.db.users.count())

@app.route('/data/login/<username>')
def login(username):
    if not mongo.db.users.find_one({"username": username}):
        user = UserModel(username)
        mongo.db.users.insert(user.to_dict())
        result = createMerchantAccount(username)
        pdb.set_trace()
        print result.merchant_account.status

    return "Success!!!"

@app.route('/data/payLoan',methods=['POST'])
def pay_loan():
    username = request.args.get('username')
    loan_id = float(request.args.get('loan_id'))
    user = mongo.db.users.find_one({"username": username})
    nonce= request.form["payment_method_nonce"]
    pdb.set_trace()
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
                result = braintree.Transaction.sale({
                    "amount": granted,
                    "payment_method_nonce": nonce
                })
    mongo.db.users.update({"username": debt_paid_user['username']}, {"$set": debt_paid_user}, upsert=False)
    loans_outstanding = filter(lambda x: x['id'] != loan_id, loans_outstanding)
    user['loans_outstanding'] = loans_outstanding
    mongo.db.users.update({"username": user['username']}, {"$set": user})
    return "GREAT"

@app.route('/data/requestLoan')
def request_loan():
    username = request.args.get('username')
    amount = request.args.get('amount')
    description = request.args.get('description')
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return "NO GOOD"
    trusted = user['trusted']
    if not len(trusted):
        return "NO GOOD"

def find_chain(username, loan_id, amount, visited):
    if username in visited:
        return []
    visited.append(username)
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return []
    trusted = user['trusted']
    fin_array = []
    for trusted_username in trusted:
        if amount == 0:
            break
        trusted_user = mongo.db.users.find_one({"username": trusted_username})
        if trusted_user['lending_balance'] >= amount:
            trusted_user['loans_granted'].append({'id': loan_id, 'amount': amount})
            trusted_user['lending_balance'] -= amount
            amount = 0
            # mongo.db.users.update({"username": trusted_username, "$set": trusted_user})
            fin_array.append(trusted_username)
        else:
            new_amount = amount - trusted_user['lending_balance']
            trusted_user['loans_granted'].append({'id': loan_id, 'amount': amount})
            trusted_user['lending_balance'] -= amount
            # mongo.db.users.update({"username": trusted_username, "$set": trusted_user})
            fin_array.append(trusted_username)
            acount = new_amount
    if amount > 0:
        fin_array += find_chain(random.choice(trusted), loan_id, amount, visited)
    return fin_array


@app.route('/data/userData/<username>')
def get_user_data(username):
   user = mongo.db.users.find_one({"username":username})
   if user is not None:
       resDict = {x : user[x] for x in ['username', 'lending_balance', 'loans_outstanding', 'loans_granted']}
   else:
       resDict = {}
   resDict.update({"client_token": braintree.ClientToken.generate()})
   return json.dumps(resDict)

if __name__ == "__main__":
    app.run(debug=True)
