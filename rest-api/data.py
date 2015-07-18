import json
import pdb

class UserModel():

    def __init__(self, username):
        self.username = username
        self.trusted = []
        self.lending_balance = 0.0
        self.loans_outstanding = []
        self.loans_granted = []

    def add_trusted_person(self, username):
        if type(username) == str:
            self.trusted.append(username)
        elif type(username) == list:
            self.trusted += username

    def add_lending_balance(self, balance):
        self.lending_balance += balance

    def to_dict(self):
        user_dict = {
            "username": self.username,
            "trusted": self.trusted,
            "lending_balance": self.lending_balance,
            "loans_outstanding": self.loans_granted,
            "loans_granted": self.loans_granted
        }

        return user_dict
