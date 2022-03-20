import datetime
from enum import unique
from flask_login import UserMixin, current_user
from flask_admin.contrib.sqla import ModelView

from projectapp import db

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    user_fname = db.Column(db.String(50), nullable=False)
    user_lname = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(100), nullable=False, unique=True)
    user_password = db.Column(db.String(500), nullable=False)
    user_address = db.Column(db.String(100), nullable=False)
    user_phone = db.Column(db.String(15), nullable=False)

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return "You're unauthorized to access this page"

class Cards(db.Model):
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer())
    cardnumber = db.Column(db.String(30), nullable=False)
    cardexpirydate = db.Column(db.String(5), nullable=False)
    cardcvvnum = db.Column(db.String(3), nullable=False)

class Accounts(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer(), unique=True)
    wallet_num = db.Column(db.String(50), unique=True)
    third_party_account = db.Column(db.String(50), unique=True)
    account_status = db.Column(db.String(20))
    ngn_balance = db.Column(db.Numeric(precision=18, scale=2), default=0.00)
    usd_balance = db.Column(db.Numeric(precision=18, scale=2), default=0.00)

class BankFunding(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer())
    wallet_num = db.Column(db.String(50))
    third_party_num = db.Column(db.String(50))
    bank_name = db.Column(db.String(50))
    reference = db.Column(db.String(50))
    status = db.Column(db.String(50))
    account_name = db.Column(db.String(50))

class Transactions(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer())
    wallet_num = db.Column(db.String(50))
    posting_type = db.Column(db.String(5))
    reference = db.Column(db.String(1000))
    third_party_reference = db.Column(db.String(1000))
    transaction_type = db.Column(db.String(100))
    transaction_service = db.Column(db.String(100))
    status = db.Column(db.String(100))
    transaction_date = db.Column(db.DateTime())
    transaction_amount = db.Column(db.Numeric(precision=18, scale=2))
    balance_before_transaction = db.Column(db.Numeric(precision=18, scale=2))
    balance_after_transaction = db.Column(db.Numeric(precision=18, scale=2))
    provider_details = db.Column(db.String(1000))
    to_wallet_id = db.Column(db.String(1000))
    customer_ref = db.Column(db.String(1000))

# good practice to have a banks table, incase you integrate other apis and they have different bank codes
class Banks(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    get_wallet_code = db.Column(db.String(1000))