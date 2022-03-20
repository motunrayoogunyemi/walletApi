from asyncio.trsock import TransportSocket
from email.policy import default
import requests, json
from flask import flash, render_template, request, redirect, session,url_for, jsonify
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import and_
from projectapp import app
from projectapp.models import Cards, Transactions, db, Users, Accounts, BankFunding
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
        # print(wlt_res)
        # print(wlt_res['success'])
        if wlt_res['success']:
            user_account = Accounts(user_id=register_deets.id, wallet_num=wlt_res['data']['wallet_id'], account_status=wlt_res['data']['status'])
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

# @app.route('/register', methods=['GET','POST'])
# def register():
#     if request.method=='POST':
#         request_data = json.loads(request.data)
#         hashed_pass = generate_password_hash(request_data['password'])
#         register_deets = Users(user_fname=request_data['fname'],user_fname=request_data['lname'],user_password=hashed_pass,user_email=request_data['email'], user_address=request_data['address'], user_phone=request_data['phone'])
#         db.session.add(register_deets)
#         db.session.commit()
#         # create user wallet here
#         wlt_res = wlt.CreateWallet(register_deets.user_email)
#         # print(wlt_res)
#         # print(wlt_res['success'])
#         if wlt_res['success']:
#             user_account = Accounts(user_id=register_deets.id, wallet_num=wlt_res['data']['wallet_id'], account_status=wlt_res['data']['status'])
#             db.session.add(user_account)
#             db.session.commit()
#         return redirect('/login')
# #return render_template('user/register.html', form=form) 
    

@app.route('/logout') 
@login_required
def logout():
    logout_user()
    return 'logged out'


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def home():
    wallet = db.session.query(Accounts).filter(Accounts.user_id == current_user.id).first()
    print(wallet)
    if request.method == 'GET':
        userinfo = db.session.query(Users).get(current_user.id)
        account_info = wlt.GetWalletDetails(wallet.wallet_num)
        print(wallet.wallet_num)
        print(account_info)
        if account_info['success']:
            cardresinfo = []
            if account_info['data'].get('saved_cards'):
                for card in account_info['data']['saved_cards']:
                    entry = {}
                    entry['user_id'] = current_user.id
                    entry['cardnumber'] = card['card_pan']
                    entry['cardexpirydate'] = card['expiration']
                    entry['cardcvvnum'] = card['charge_code']
                    cardresinfo.append(entry)
                    card_in_db = db.session.query(Cards).filter(and_(Cards.user_id == current_user.id, Cards.cardnumber == card['card_pan'])).first()
                    bool_card_in_db = db.session.query(card_in_db.exists()).scalar()
                    if not bool_card_in_db:
                        new_card = Cards(user_id=entry['user_id'], cardnumber=entry['cardnumber'], cardexpirydate=entry['cardexpirydate'], cardcvvnum=entry['cardcvvnum'] )
                        db.session.add(new_card)
                        db.session.commit()
                print(cardresinfo)
                return render_template('user/index.html', cardinfo=cardresinfo, account_balance=account_info['balance'], userinfo=userinfo)

        cardinfo = db.session.query(Cards).filter(Cards.user_id == current_user.id).all()
        for c in cardinfo:
            print(c)
        return render_template('user/index.html', cardinfo=cardinfo, account_balance=wallet.ngn_balance, userinfo=userinfo) 
    else:
        # cardnum = request.form.get('cardnum')
        # cardexp = request.form.get('cardexp')
        # cardcvv = request.form.get('cardcvv')
        # carddeets = Cards(cardnumber = cardnum, cardexpirydate=cardexp, cardcvvnum = cardcvv, user_id=current_user.id)
        # db.session.add(carddeets)
        # db.session.commit()

        # save card, not feasible
        # save_card = wlt.SaveWalletCard(wallet.wallet_num, "tbd")
        # print(save_card)
        # if save_card.success and save_card.data.success:
        #     return jsonify(status=True, message=save_card.data.message)

        #top up wallet, discard this, lool. Or not. Might be useful later
        # selectedcard = request.form.get('mycard')
        # amount = request.form.get('amount')
        return 'success'

@app.route('/topup', methods=['GET','POST'])
def topup():
    # card top up
    # bank transfer topup
    # bank transfer returns bank account and bank to transfer to, then when the user transfers into that bank, a notification is sent to the webhook
    # so basically, bank transfer ends with returning the bank name and account to frontend, it's important to save the ref
    # a background service can check requests and confirm if a credit has occurred. I just dunno if the account number never changes
    # we need a table for logging bank transfers, in case user forgets the account number
    channel = request.args.get('channel')
    if request.method == 'POST':
        body = request.get_json()
        channel = request.args.get('channel')
        #channel = request.form.get('channel')
        wallet = db.session.query(Accounts).filter(Accounts.user_id == current_user.id).first()
        if channel == 'bank':
            # bank transfer
            bankres = wlt.FundWalletBankTransfer(wallet.wallet_num)
            print(bankres)
            if bankres['success']:
                new_fund = BankFunding(user_id=current_user.id, wallet_num=wallet.wallet_num,
                third_party_num=bankres['data']['account_number'], bank_name=bankres['data']['bank'], reference=bankres['data']['ref'],
                account_name=bankres['data']['account_name'])
                db.session.add(new_fund)
                db.session.commit()
                return jsonify(bank_name=bankres['data']['bank'], account_number=bankres['data']['account_number'], account_name=bankres['data']['account_name'])
            
            return jsonify(bank_name=None, account_number=None, account_name=None)
        
        elif channel == 'card':
            # cards
            amount = body['amount'] * 100 # convert to kobo
            card_res = wlt.FundWalletCard(wallet.wallet_num, amount, True, "http://localhost:5000/dashboard")
            print(card_res)
            if card_res['success']:
                return jsonify(cardurl=card_res['data'])
            return jsonify(cardurl=None)

        elif channel == 'saved':
        # saved cards
            amount = body['amount'] * 100 # convert to kobo
            code = body['card_code']
            card_res = wlt.FundWalletSavedCard(wallet.wallet_num, amount, code)
            print(card_res)
            if card_res['success']:
                return jsonify(status=True, message=card_res['message'])
        
        return jsonify(status=False, message="failed")

    elif request.method == 'GET':
        if channel == 'card':
            cards = db.session.query(Cards).filter(Cards.user_id == current_user.id).all()
            print(len(cards))
            resp = []
            for card in cards:
                entry = {}
                entry['id'] = card.id
                entry['user_id'] = card.user_id
                entry['cardnumber'] = card.cardnumber
                entry['cardcvvnum'] = card.cardcvvnum
                entry['cardexpirydate'] = card.cardexpirydate
                resp.append(entry)
        
            return jsonify(cardinfo=resp)

@app.route('/notify', methods=['POST'])
def notify():
    # this is the notification webhook
    body = request.get_json()
    print("notify event", body)
    if body['event'] == 'wallet.created':
        account_exist = db.session.query(Accounts).filter(Accounts.wallet_num == body['data'].wallet_id)
        bool_account_exist = db.session.query(account_exist.exists()).scalar()
        if not bool_account_exist:
            user = db.session.query(Users).get(Users.user_email == body['data'].customer_email)
            if user:
                new_acct = Accounts(user_id=user.id, wallet_num=body['data'].wallet_id, account_status=body['data'].status, ngn_balance=body['data'].balance)
                db.session.add(new_acct)
                db.session.commit()
                return
            return
        return
        
    elif body['event'] == 'wallet.fund.back_account.successful' or body['event'] == 'wallet.fund.card_funding.successful':
        trx = db.session.query(Transactions).filter(and_(Transactions.reference == body['data'].transaction_id, Transactions.posting_type == body['data'].drcr, Transactions.wallet_num == body['data'].wallet_id))
        bool_trx = db.session.query(trx.exists()).scalar()
        if bool_trx:
            return

        wallet = db.session.query(Accounts).filter(Accounts.wallet_num == body['data'].wallet_id)
        bool_wallet_exist = db.session.query(wallet.exists()).scalar()
        if bool_wallet_exist:
            new_trx = Transactions(
                user_id = wallet.user_id,
                wallet_num = wallet.wallet_num,
                posting_type = body['data'].drcr,
                reference = body['data'].transaction_id,
                third_party_reference = body['data'].reference,
                transaction_type = body['data'].funding_method,
                transaction_service = body['data'].type,
                status = body['data'].status,
                transaction_date = body['data'].updated_at,
                transaction_amount = body['data'].amount,
                balance_before_transaction = body['data'].previous_wallet_balance,
                balance_after_transaction = body['data'].previous_wallet_balance + body['data'].amount if body['data'].status == 'successful' else body['data'].previous_wallet_balance,
                provider_details = f"{body['data'].provider_name} {body['data'].provider_ref} {body['data'].provider}",
                to_wallet_id = body['data'].to_wallet_id,
                customer_ref = body['data'].customer_ref
            )
            db.session.add(new_trx)
            wallet.ngn_balance = new_trx.balance_after_transaction

            db.session.commit()
            # confirm credit to account balance
            user_wallet = wlt.GetWalletDetails(body['data'].wallet_id)
            if user_wallet.success:
                # only credit the wallet if it has not been updated yet, and even then, this is iffy, might remove
                if user_wallet.data.balance != new_trx.balance_after_transaction and user_wallet.data.updated_at < new_trx.transaction_date and new_trx.status == 'successful':
                    # credit wallet manually, confirm amount is in naira not kobo
                    credit_res = wlt.FundWalletManually(body['data'].wallet_id, new_trx.transaction_amount)
                    if credit_res.success and credit_res.success.success:
                        return
                    return
                return
            return
        return
        # normally, we'd log the events, but I dunno how you set up logging  
    elif body['event'] == 'wallet.transfer.wallet_to_bank.successful':
        trx = db.session.query(Transactions).filter(and_(Transactions.reference == body['data'].transaction_id, Transactions.posting_type == body['data'].drcr, Transactions.wallet_num == body['data'].wallet_id))
        bool_trx = db.session.query(trx.exists()).scalar()
        if bool_trx:
            return

        # not sure whether to dr or cr here, we'd have to test it to see
        wallet = db.session.query(Accounts).filter(Accounts.wallet_num == body['data'].wallet_id)
        bool_wallet_exist = db.session.query(wallet.exists()).scalar()
        if bool_wallet_exist:
            new_trx = Transactions(
                user_id = wallet.user_id,
                wallet_num = wallet.wallet_num,
                posting_type = body['data'].drcr,
                reference = body['data'].transaction_id,
                third_party_reference = body['data'].reference,
                transaction_type = body['data'].funding_method,
                transaction_service = body['data'].type,
                status = body['data'].status,
                transaction_date = body['data'].updated_at,
                transaction_amount = body['data'].amount,
                balance_before_transaction = body['data'].previous_wallet_balance,
                balance_after_transaction = body['data'].previous_wallet_balance + body['data'].amount if body['data'].status == 'successful' and body['data'].drcr == 'CR' else body['data'].previous_wallet_balance - body['data'].amount, # needs review
                provider_details = f"{body['data'].provider_name} {body['data'].provider_ref} {body['data'].provider}",
                to_wallet_id = body['data'].to_wallet_id,
                customer_ref = body['data'].customer_ref
            )
            db.session.add(new_trx)
            wallet.ngn_balance = new_trx.balance_after_transaction
            db.session.commit()
            # confirm credit to account balance
            user_wallet = wlt.GetWalletDetails(body['data'].wallet_id)
            if user_wallet.success:
                # only credit the wallet if it has not been updated yet, and even then, this is iffy, might remove
                if user_wallet.data.balance != new_trx.balance_after_transaction and user_wallet.data.updated_at < new_trx.transaction_date:
                    # credit or debit wallet manually, confirm amount is in naira not kobo
                    if new_trx.posting_type == 'CR' :
                        credit_res = wlt.FundWalletManually(body['data'].wallet_id, new_trx.transaction_amount)
                        if credit_res.success and credit_res.success.success:
                            return
                        return
                    else :
                        debit_res = wlt.DebitWalletManually(body['data'].wallet_id, new_trx.transaction_amount)
                        if debit_res.success and debit_res.success.success:
                            return
                        return
                return
            return
        return

    elif body['event'] == 'wallet.transfer.wallet_to_bank.failed':
        trx = db.session.query(Transactions).filter(and_(Transactions.reference == body['data'].transaction_id, Transactions.posting_type == body['data'].drcr, Transactions.wallet_num == body['data'].wallet_id))
        bool_trx = db.session.query(trx.exists()).scalar()
        if bool_trx:
            return

        wallet = db.session.query(Accounts).filter(Accounts.wallet_num == body['data'].wallet_id)
        bool_wallet_exist = db.session.query(wallet.exists()).scalar()
        if bool_wallet_exist:
            new_trx = Transactions(
                user_id = wallet.user_id,
                wallet_num = wallet.wallet_num,
                posting_type = body['data'].drcr,
                reference = body['data'].transaction_id,
                third_party_reference = body['data'].reference,
                transaction_type = body['data'].funding_method,
                transaction_service = body['data'].type,
                status = body['data'].status,
                transaction_date = body['data'].updated_at,
                transaction_amount = body['data'].amount,
                balance_before_transaction = body['data'].previous_wallet_balance,
                balance_after_transaction = body['data'].previous_wallet_balance, # needs review
                provider_details = f"{body['data'].provider_name} {body['data'].provider_ref} {body['data'].provider}",
                to_wallet_id = body['data'].to_wallet_id,
                customer_ref = body['data'].customer_ref
            )
            db.session.add(new_trx)
            wallet.ngn_balance = new_trx.balance_after_transaction
            db.session.commit()
            return
        return
    
    return
    
@app.route('/payout', methods=['POST', 'GET'])
def payout():
    # for transfers, wallet to wallet, wallet to bank
    channel = request.args.get('channel')
    wallet = db.session.query(Accounts).filter(Accounts.user_id == current_user.id).first()
    if request.method == 'POST':
        body = request.get_json()
        if channel == 'wallet':
            trf_res = wlt.WalletToWallet(wallet.wallet_num, body['amount'] * 100, body['to_wallet'])
            print(trf_res)
            if trf_res['success']:
                return jsonify(status=True, message=trf_res['message'])
            return jsonify(status=False, message=trf_res['message']) # changeable depending on if trf_res returns anything at all

        elif channel == 'bank':
            trf_res = wlt.WalletToBank(wallet.wallet_num, body['amount'] * 100, body['bank_code'], body['accnum'])
            print(trf_res)
            if trf_res['success']:
                return jsonify(status=True, message=trf_res['message'])
            return jsonify(status=False, message=trf_res['message']) # changeable depending on if trf_res returns anything at all

        return jsonify(status=False, message='Invalid channel specified')

    elif request.method == 'GET':
        if channel == 'bank':
            name_check = request.args.get('name_check', default=False)
            if name_check:
                accnum = request.args.get('accnum')
                bank_code = request.args.get('bank_code')
                name = wlt.VerifyName(bank_code, accnum)
                if name['success']:
                    return jsonify(status=True, data=name['data'])
                return jsonify(status=False, message='Unable to verify name')

            banks_res = wlt.GetBanks()
            if banks_res['success']:
                return jsonify(banks_res['data'])
            return
        return jsonify(status=False, message='Invalid channel specified')

    return jsonify(status=False, message='Invalid method')

@app.route('/transferquery', methods=['GET'])
def requery():
    reference = request.args.get('ref', default=None)
    if reference:
        query_res = wlt.ValidateFundWallet(reference)
        print(query_res)
        if query_res['success']:
            trx = db.session.query(Transactions).filter(and_(Transactions.reference == query_res['data']['transaction_id'], Transactions.posting_type == query_res['data']['drcr'], Transactions.wallet_num == query_res['data']['wallet_id']))
            bool_trx = db.session.query(trx.exists()).scalar()
            if not bool_trx:
                # add to transactions table, not yet implemented for now, more tests to be done
                pass
            return jsonify(status=True, data=query_res['data'])
        return jsonify(status=False, message=query_res['message'])

    return jsonify(status=False, message='Reference required')

@app.route('/manualcredit', methods=['POST'])
def mcredit():
    body = request.get_json()
    wallet = db.session.query(Accounts).filter(Accounts.user_id == current_user.id).first()
    dest_wallet = body.get('dest_wallet')
    amount = body['amount'] * 100 # convert to kobo
    add_res = wlt.FundWalletManually(dest_wallet if dest_wallet else wallet.wallet_num, amount)
    print(add_res)
    if add_res['success']:
        return jsonify(status=True, data=add_res['message'])
    return jsonify(status=False, message=add_res['message'])

@app.route('/transactions', methods=['GET'])
def transactions():
    wallet = db.session.query(Accounts).filter(Accounts.user_id == current_user.id).first()
    dest_wallet = request.args.get('dest_wallet', default=None)
    trxs = wlt.GetWalletTransactions(dest_wallet if dest_wallet else wallet.wallet_num)
    print(trxs)
    if trxs['success']:
        return jsonify(status=True, data=trxs['data'])
    return jsonify(status=False, message=trxs['message'])

@app.route('/setwebhook', methods=['GET'])
def setwebhook():
    url = request.args.get('url', default=None)
    if url:
        res = wlt.SetWebhooks(url)
        print(res)
        if res['success']:
            return jsonify(status=True, data=res['data'])
        return jsonify(status=False, message=res['message'])
    return jsonify(status=False, message='URL is missing')