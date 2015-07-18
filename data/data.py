from pymongo import MongoClient

client = MongoClient()

db = client.loanmate
users = db.users
