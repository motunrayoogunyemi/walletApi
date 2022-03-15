from flask import redirect
import requests, json


def CreateWallet(email):
    url = "https://api.getwallets.co/v1/wallets"

    payload = {"customer_email":email}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    return response.json()

def GetAllWallets():
    url = "https://api.getwallets.co/v1/wallets"

    headers = {"Accept": "application/json",
    "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"
    }

    response = requests.get(url, headers=headers)

    return response.json()

def GetWalletDetails(walletid):
    url = "https://api.getwallets.co/v1/wallets/{walletid}"
    headers = {"Accept": "application/json", "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"}
    response = requests.get(url, headers=headers)
    return response.json()

def GetWalletTransactions(walletid):
    url = f"https://api.getwallets.co/v1/transactions/wallets/{walletid}"
    headers = {"Accept": "application/json", "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"}
    response = requests.get(url, headers=headers)
    return response.json()

def ValidateFundWallet(ref):
    url = f"https://api.getwallets.co/v1/transactions/validate/{ref}"
    headers = {"Accept": "application/json", "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"}
    response = requests.get(url, headers=headers)
    return response.json()

def FundWalletBankTransfer(wallet_id):
    url = "https://api.getwallets.co/v1/wallets/funds/banktransfer"
    payload = {"wallet_id":wallet_id}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def FundWalletCard(wallet_id, amount, save_card, redirect_url):
    url = "https://api.getwallets.co/v1/wallets/funds/cards"
    # redirect_url = ""
    payload = {"wallet_id":wallet_id, "amount":amount, "save_card":save_card, "redirect_url":redirect_url}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def SaveWalletCard(wallet_id, redirect_url):
    url = "https://api.getwallets.co/v1/wallets/funds/cards"
    # redirect_url = ""
    payload = {"wallet_id":wallet_id, "save_card":True, "redirect_url":redirect_url}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def FundWalletSavedCard(wallet_id,amount,code):
    url = "https://api.getwallets.co/v1/wallets/funds/cards/charge"
    payload = {"wallet_id":wallet_id, "amount":amount, "card_charge_code":code}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def FundWalletManually(wallet_id, amount):
    url = "https://api.getwallets.co/v1/wallets/funds/manual"
    payload = {"wallet_id":wallet_id, "amount":amount}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def WalletToWallet(from_wallet, amount, to_wallet):
    url = "https://api.getwallets.co/v1/wallets/transfers/wallet"
    payload = {"from_wallet_id":from_wallet, "to_wallet_id":to_wallet, "amount":amount}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def WalletToBank(wallet_id, amount, bank_code, accnum):
    url = "https://api.getwallets.co/v1/wallets/transfers/bank"
    payload = {"from_wallet_id":wallet_id, "amount":amount, "bank_code":bank_code, "account_number":accnum}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def DebitWalletManually(wallet_id, amount):
    url = "https://api.getwallets.co/v1/wallets/debit/manual"
    payload = {"wallet_id":wallet_id, "amount":amount}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def SetWebhooks(myurl):
    url = "https://api.getwallets.co/v1/webhooks"
    # myurl = ''
    payload = {"url":myurl}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def GetBanks():
    url = "https://api.getwallets.co/v1/banks"

    headers = {
        "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"
    }

    response = requests.get(url, headers=headers)
    return response.json()

def VerifyName(bank_code, accnum):
    url = 'https://api.getwallets.co/v1/resolve'

    params = {
        "account_number" : accnum,
        "bank_code" : bank_code
    }

    headers = {
        "Authorization": "Bearer sk_test_622bdb64bd975352423021da622bdb64bd975352423021db"
    }

    response = requests.get(url, params=params, headers=headers)
    return response.json()





