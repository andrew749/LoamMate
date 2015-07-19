import pdb
import json
from flask import Flask
from flask import request
from flask.ext.pymongo import PyMongo
from data import UserModel
import sendgrid
import braintree
from uuid import uuid4
from flask import render_template
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
                'last_name': userId,
                'email': "example@gmail.com",
                'phone': "555-555-5555",
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
                'legal_name': "MerchantAccount",
                'dba_name': "MerchantAccount",
                'tax_id': "98-7654321",
                'address': {
                            'street_address': "111 Main St",
                            'locality': "Chicago",
                            'region': "IL",
                            'postal_code': "60622"
                        }
            },
        'funding': {
                'descriptor': "Description",
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
@app.route('/nonce')
def handleNonce():
   pdb.set_trace()
   doTransactionWithNonce(req.form["payment_method_nonce"],"10","andrew749development")
@app.route('/indexrender')
def indexRender():
    return render_template("index.html",data={"clienttoken":braintree.ClientToken.generate(),"amount":"10"})

@app.route('/data/requestLoan')
def request_loan():
    username = request.args.get('username')
    amount = request.args.get('amount')
    description = request.args.get('description')
    user = mongo.db.users.find_one({"username": username})
    pdb.set_trace()
    if not user:
        return "NO GOOD"
    trusted = user['trusted']
    #need to send a bunch of emails to people asking to authenticate
    #mongo.db.users.update({"username":username},{"$set":{"loans_outstanding":user["loans_outstanding"].append({"id":uuid4(),"amount":amount,"description":description,"chains":find_chain()})}})
    sendSendGridWithAuthRequest()


def sendSendGridWithAuthRequest():
    sg = sendgrid.SendGridClient('andrew749', 'trolololo1')
    message = sendgrid.Mail()
    message.add_to('John Doe <andrewcod749@gmail.com>')
    message.set_subject('Example')
    message.set_html('Confirmation needed')
    message.set_text('Please visit http://127.0.0.1:5000/indexrender')
    message.set_from('Doe John <doe@email.com>')
    status, msg = sg.send(message)

def requestToken(customerid):
    return braintree.ClientToken.generate({
        "customer_id": customerid
    })

def doTransactionWithNonce(nonce, amount, id):
    createTransaction(nonce,id,amount)

def createTransaction(nonce, id, amount):
    result = braintree.Transaction.sale({
        "merchant_account_id": id,
        "amount": amount,
        "payment_method_nonce": nonce,
        "service_fee_amount": "0.00"
    })
    return result

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
            mongo.db.users.update({"username": trusted_username, "$set": trusted_user})
            fin_array.append(trusted_username)
        else:
            new_amount = amount - trusted_user['lending_balance']
            trusted_user['loans_granted'].append({'id': loan_id, 'amount': amount})
            trusted_user['lending_balance'] -= amount
            mongo.db.users.update({"username": trusted_username, "$set": trusted_user})
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
