from Block import Block, genesis
import json
from config import INITIAL_SYSTEM_BALANCE, PENDING_POOL_LIMIT
from ledger import Ledger
from Account import Accounts
from TX import TX


class Blockchain:
    def __init__(self):
        self.ledger = Ledger()
        self.chain = [genesis()]
        self.pending_transactions = []
        self.faulty_txs = []

    def init_system_account(self):
        if "SYSTEM" in self.ledger.ledger:
            return None
        else:
            SYSTEM_ACCOUNT = Accounts()
            SYSTEM_ACCOUNT.timestamp = 0
            SYSTEM_ACCOUNT.balance = INITIAL_SYSTEM_BALANCE
            SYSTEM_ACCOUNT.address = "SYSTEM"
            self.ledger.add_to_ledger(SYSTEM_ACCOUNT)
            return SYSTEM_ACCOUNT

    def create_wallet(self, address=None, balance=None):
        wallet = Accounts(blockchain=self)
        wallet.address = address if address else wallet.address
        wallet.balance = balance if balance else wallet.balance
        self.ledger.add_to_ledger(wallet)
        return wallet

    def calculate_balances_ledger(self):
        for account in self.ledger.ledger:
            account.balance = account.calculate_balance(self, account.address)

    def calculate_balance_by_account_txs(self, address):
        return self.ledger.ledger[address].calculate_balance_by_txs()

    def get_balance_ledger(self, address):
        return self.ledger.get_balance(address)

    def get_active_wallets(self):
        active_wallets = set()
        for block in self.chain:
            for transaction in block.transactions:
                active_wallets.add(transaction.input["from"])
                active_wallets.add(transaction.input["to"])
        return active_wallets

    def chains_last_hash(self):
        return self.chain[-1].hash

    def craft_block(self, owner_public_key=None):
        block = Block(owner=owner_public_key)
        block.last_hash = self.chains_last_hash()
        block.block_no = len(self.chain)
        return block

    def manual_craft(self, block_no=None, last_hash=None, owner_public_key=None):
        block = Block()
        block.block_no = block_no or self.no_blocks()
        block.last_hash = last_hash or self.chains_last_hash()
        block.owner = owner_public_key or "GENESIS"
        block.hash = block.gen_hash()
        return block

    def add_block(self, block):
        block.set_hash()
        block.sign_block()
        self.chain.append(block)

    def no_blocks(self):
        return len(self.chain)

    def get_blocks_info(self, number=None):
        if number:
            if number > len(self.chain):
                print("Input more than numbers of  blocks.")
                return None
            else:
                for i in self.chain[:number + 1]:
                    print(f"{'=' * 20}\n"
                          f"Block {i.block_no}\n"
                          f"Time: {i.timestamp}\n"
                          f"Hash: {i.hash}\n"
                          f"Last Hash: {i.last_hash}\n"
                          f"Signature: {i.signature}\n"
                          f"Transactions: {i.transactions}\n"
                          f"Owner: {i.owner}\n"
                          f"{'=' * 20}\n")
        else:
            self.get_blocks_info(len(self.chain))

    def find_block(self, timestamp=None, block_no=None, hash=None, last_hash=None,
                   transactions=None, owner=None):
        found_block = list()
        for i in self.chain:
            if timestamp and i.timestamp == timestamp:
                found_block.append(i)
            if block_no and i.block_no == block_no:
                found_block.append(i)
            if hash and i.hash == hash:
                found_block.append(i)
            if last_hash and i.last_hash == last_hash:
                found_block.append(i)
            if transactions and i.transactions == transactions:
                found_block.append(i)
            if owner and i.owner == owner:
                found_block.append(i)
        return set(found_block)

    def check_bc_validation(self):
        valid = True
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]
            sign_valid = current.sign_valid("./public.pem")
            if not current.hash_valid():
                print(f"Block {current.block_no} has invalid hash!. Signature: {sign_valid}")
                valid = False
            elif current.last_hash != prev.hash:
                print(f"Block {current.block_no} has broken link to previous block!. Signature: {sign_valid}")
                valid = False
            else:
                print(f"Block {current.block_no} is valid. Signature: {sign_valid}")
        return valid

    def export_chain(self):
        return json.dumps([
            {
                'block_no': b.block_no,
                'timestamp': b.timestamp,
                'hash': b.hash,
                'last_hash': b.last_hash,
                'signature': b.signature,
                'transactions': [
                    {b.transactions[i].id: {"output": b.transactions[i].output, "input": b.transactions[i].input}} for i
                    in range(len(b.transactions))],
                'owner': b.owner
            } for b in self.chain
        ], indent=4)

    @staticmethod
    def load_chain(json_data):
        bc = Blockchain()
        bc.chain = []
        data = json.loads(json_data)

        for entry in data:
            block = Block(
                transactions=[TX("a","a","a",1).from_dict(tx) for tx in entry["transactions"]],
                block_no=entry["block_no"],
                timestamp=entry["timestamp"],
                last_hash=entry["last_hash"],
                hash=entry["hash"],
                signature=entry.get("signature"),  # NEW
                owner=entry.get("owner")  # NEW
            )
            bc.chain.append(block)

        return bc

    def action(self, sender, to, amount):
        tx = sender.send(to, amount)
        self.transact(tx)
        return tx

    def transact(self, tx):
        if not any(tx in self.chain[i].transactions for i in range(len(self.chain))):
            if tx.amount + tx.FEE + tx.TAX > self.get_balance_ledger(tx.sender_address):
                return "Insufficient Balance"
            if tx not in self.pending_transactions:
                self.pending_transactions.append(tx)
            self.act_pending_transactions()
            return tx.status, tx.confirmation
        else:
            return "Transaction already in chain"

    def act_pending_transactions(self):
        if self.number_of_pending_txs() >= PENDING_POOL_LIMIT:
            block = self.craft_block()
            for tx in self.pending_transactions:
                if tx.is_valid():
                    tx.confirmation += 1
                    tx.status = "Confirmed"
                    tx.update_tx()
                    try:
                        self.ledger.update_ledger(tx)
                    except KeyError:
                        self.create_wallet(address=tx.recv, balance=tx.amount)
                    block.transactions.append(tx)
                else:
                    tx.status = "Failed"
                    tx.update_tx()
                    self.faulty_txs.append(tx)
            self.add_block(block)
            self.pending_transactions = []

    def find_txs(self, address):
        txs = []
        for i in self.chain:
            for j in i.transactions:
                if j.output["from"] == str(address) or j.input["to"] == str(address):
                    txs.append(j)
        return txs

    def search_tx(self, tx_info,pending=False,faulty=False,confirmed=False):
        found = []
        if confirmed:
            for block in self.chain:
                for tx in block.transactions:
                    if tx.id == tx_info or tx.sender_address == tx_info or tx.recv == tx_info or tx.sender_pub_key == tx_info or tx.timestamp == tx_info:
                        found.append(tx)
        if pending:
            for tx in self.pending_transactions:
                if tx.id == tx_info or tx.sender_address == tx_info or tx.recv == tx_info or tx.sender_pub_key == tx_info or tx.timestamp == tx_info:
                    found.append(tx)
        if faulty:
            for tx in self.faulty_txs:
                if tx.id == tx_info or tx.sender_address == tx_info or tx.recv == tx_info or tx.sender_pub_key == tx_info or tx.timestamp == tx_info:
                    found.append(tx)
        return found

    def number_of_pending_txs(self):
        return len(self.pending_transactions)

    def remove_pending_tx(self, tx_id, revoked=False):
        if revoked:
            tx=self.search_tx(tx_id)
            tx=tx[0]
            if tx:
                self.pending_transactions.remove(tx)
                tx.status = "CanceledByUser"
                tx.update_tx()
                self.ledger.ledger[tx.sender_address].transactions.append(tx)
                return True
        return False

    def get_wallet_info(self,address):
        try:
            account=self.ledger.ledger[address]
            context={}
            context["address"]=account.address
            context["balance"]=account.balance
            context["txs"]=account.transactions
            context["public_key"]=account.public_key
            context["pending_txs"]=self.search_tx(address,pending=True)
        except:
            return None
        return context


    def __repr__(self):
        return f"Blocks avaliable: {self.no_blocks()}"
