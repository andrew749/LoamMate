#import os
from flask import Flask
#from flask.ext.pymongo import PyMongo

#MONGO_URL = os.environ.get('MONGO_URL')
#if not MONGO_URL:
#    MONGO_URL = "mongodb://localhost:27017";
#
app = Flask(__name__)
#mongo = PyMongo(app)

@app.route("/")
def hello():
    return "Testing"

if __name__ == "__main__":
    app.run()
