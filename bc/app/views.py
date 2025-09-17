from django.shortcuts import render, redirect
from django.http import HttpResponse
import numpy as np
import json
from django.contrib import messages
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(parent_dir))

from Blockchain import Blockchain
from config import INITIAL_SYSTEM_BALANCE, PENDING_POOL_LIMIT

bc = Blockchain()
account1 = bc.create_wallet()

system_account = bc.init_system_account()
bc.action(system_account, account1.address, 200)
bc.action(system_account, account1.address, 200)
bc.action(system_account, account1.address, 200)
bc.action(system_account, account1.address, 200)
bc.action(system_account, account1.address, 200)


def index(request):
    random_transact = int(request.POST.get("index_input_tx") or 0) or 0
    if random_transact:
        try:
            for _ in range(random_transact):
                bc.action(account1, bc.create_wallet().address, np.random.randint(10, 100))
        except Exception as e:
            messages.error(request, str(e))
    context = {"random_transact": random_transact,
               "bc_nblocks": json.dumps(bc.export_chain(), indent=2),
               "bc": bc, "PENDING_NO": PENDING_POOL_LIMIT,
               "accounts": account1}
    return render(request, "index.html", context=context)


def blocks(request):
    context = {"bc": bc.chain, "accounts": account1}
    return render(request, "blocks.html", context=context)


def tx_account(request, address):
    balance = account1.calculate_balance(blockchain=bc, address=address)
    return HttpResponse(json.dumps({"balance_tx": balance, "address": address,
                                    "balance_ledger": bc.get_balance_ledger(address)})
                        , content_type="application/json")


def tx_account_html(request):
    address = request.POST.get("address")
    context = {"address": address, "balance": bc.get_balance_ledger(address), "accounts": account1}
    return render(request, "tx_account_html.html", context=context)


def transfer_send(request, address, amount):
    tx = bc.action(account1, address, int(amount))
    status, tx_message = tx.status, tx.confirmation
    return HttpResponse(json.dumps({"status": status, "confirmation": tx_message, "tx": tx.to_dict()}))


def transfer_send_html(request):
    address = request.POST.get("address")
    amount = request.POST.get("amount")
    if address and amount:
        try:
            tx = bc.action(account1, address, float(amount))
            status, tx_message = tx.status, tx.confirmation
            context = {"address": address, "amount": amount, "status": status, "confirmation": tx_message, "tx": tx,
                       "accounts": account1}
        except Exception as e:
            messages.error(request, str(e))
            context = {}
    else:
        context = {}
        return render(request, "transfer_send_html.html", context=context)
    return render(request, "transfer_send_html.html", context=context)


def wallet_info(request, address):
    context = bc.get_wallet_info(address=address)
    return render(request, "wallet.html", context=context)


def wallet(request):
    revoked = request.POST.get("revoked")
    revoked_tx = None
    if revoked:
        for i in bc.pending_transactions:
            if i.id == revoked:
                bc.pending_transactions.remove(i)
                revoked_tx = i
                break
        if revoked_tx:
            messages.success(request, f"Transaction {revoked_tx.id} revoked successfully.")
        else:
            messages.error(request, f"Transaction {revoked} not found.")
    context = {"address": account1.address, "balance": bc.get_balance_ledger(account1.address),
               "public_key": account1.public_key, "txs": bc.find_txs(address=account1.address),
               "balance_accountOBJ": account1.balance, "private_key": account1.gen_private_key(), "accounts": account1
        , "pending_txs": bc.search_tx(account1.address, pending=True)}
    return render(request, "wallet.html", context=context)


def search_tx(request):
    tx_info = request.POST.get("tx_info")
    if tx_info:
        try:
            tx = bc.search_tx(tx_info, pending=True, confirmed=True,faulty=True)
            context = {"tx": tx, "accounts": account1}
        except Exception as e:
            messages.error(request, str(e))
            context = {}
    else:
        context = {}
    return render(request, "search_tx.html", context=context)
