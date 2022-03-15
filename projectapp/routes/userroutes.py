import requests, json
from flask import flash, render_template, request, redirect, session,url_for, jsonify
from flask_login import LoginManager, login_required, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import and_
from projectapp import app
from projectapp.models import Cards, db, Users, Accounts, BankFunding
from projectapp.forms import LoginForm, RegisterForm

from . import walletapiroutes as wlt

login_manager = LoginManager() 
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pass = generate_password_hash(form.password.data)
        #confirm email is unique
        register_deets = Users(user_fname=form.fname.data, user_lname=form.lname.data,user_password=hashed_pass,user_email=form.email.data,user_address=form.address.data,user_phone=form.phone.data)
        db.session.add(register_deets)
        db.session.commit()
        # create user wallet here
        wlt_res = wlt.CreateWallet(register_deets.user_email)
        if wlt_res.success:
            user_account = Accounts(user_id=register_deets.id, wallet_num=wlt_res.data.wallet_id, status=wlt_res.data.status)
            db.session.add(user_account)
            db.session.commit()
        return redirect('/login')
    return render_template('user/register.html', form=form) 

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_tbl = Users.query.filter_by(user_email=form.email.data).first()
        if user_tbl:
            checkpwd = check_password_hash(user_tbl.user_password,form.password.data)
            if checkpwd:
                login_user(user_tbl)
                return redirect('/dashboard')
            flash('invalid email or password')
        flash('invalid email or password')
    return render_template('user/login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        userinfo = db.session.query(Users).get(Users.id == current_user.id)        
        wallet = db.session.query(Accounts).get(Accounts.user_id == current_user.id)
        account_info = wlt.GetWalletDetails(wallet.wallet_num)
        if account_info.success:
            cardresinfo = []
            for card in account_info.saved_cards:
                entry = {}
                entry.user_id = current_user.id
                entry.cardnumber = card.card_pan
                entry.cardexpirydate = card.expiration
                entry.cardcvvnum = card.charge_code
                cardresinfo.append(entry)
                card_in_db = db.session.query(Cards).filter(and_(Cards.user_id == current_user.id, Cards.cardnumber == card.card_pan))
                bool_card_in_db = db.session.query(card_in_db.exists()).scalar()
                if not bool_card_in_db:
                    new_card = Cards(user_id=entry.user_id, cardnumber=entry.cardnumber, cardexpirydate=entry.cardexpirydate, cardcvvnum=entry.cardcvvnum )
                    db.session.add(new_card)
                    db.session.commit()

            return render_template('user/index.html', cardinfo=cardresinfo, account_balance=account_info.balance, userinfo=userinfo)

        cardinfo = db.session.query(Cards).filter(Cards.user_id == current_user.id).all()
        return render_template('user/index.html', cardinfo=cardinfo, account_balance=wallet.ngn_balance, userinfo=userinfo) 
    else:
        cardnum = request.form.get('cardnum')
        cardexp = request.form.get('cardexp')
        cardcvv = request.form.get('cardcvv')
        carddeets = Cards(cardnumber = cardnum, cardexpirydate=cardexp, cardcvvnum = cardcvv, user_id=current_user.id)
        db.session.add(carddeets)
        db.session.commit()

        #top up wallet
        selectedcard = request.form.get('mycard')
        amount = request.form.get('amount')
        return 'success'

@app.route('/topup', methods=['POST'])
def topup():
    # card top up
    # bank transfer topup
    # bank transfer returns bank account and bank to transfer to, then when the user transfers into that bank, a notification is sent to the webhook
    # so basically, bank transfer ends with returning the bank name and account to frontend, it's important to save the ref
    # a background service can check requests and confirm if a credit has occurred. I just dunno if the account number never changes
    # we need a table for logging bank transfers, in case user forgets the account number
    channel = request.args.get('channel')
    if channel == 'bank':
        # bank transfer
        wallet = db.session.query(Accounts).get(Accounts.user_id == current_user.id)
        bankres = wlt.FundWalletBankTransfer(wallet.wallet_num)
        if bankres.success and bankres.data.success:
            new_fund = BankFunding(user_id=current_user.id, wallet_num=wallet.wallet_num, third_party_num=bankres.data.data.account_number, bank_name=bankres.data.data.bank, reference=bankres.data.data.ref)
            db.session.add(new_fund)
            db.session.commit()
            return jsonify(bank_name=bankres.data.data.bank, account_number=bankres.data.data.account_number)
        
        return jsonify(bank_name=None, account_number=None)
    
    elif channel == 'card':
        pass
    pass      