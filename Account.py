import datetime as dt
import uuid
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import json
from TX import TX


class Accounts:
    def __init__(self, blockchain=None):
        self.address = str(uuid.uuid4())
        self.blockchain = blockchain
        self.timestamp = dt.datetime.now(dt.UTC).timestamp()
        self.private_key = ec.generate_private_key(ec.SECP256K1(),
                                                   default_backend())
        self.public_key = self.serialize_pub_key()
        self.BurnWallet_grant = False
        self.Lock = False
        self.balance = 0
        self.public_key_raw = self.private_key.public_key()
        self.transactions = []

    def calculate_balance_by_txs(self):
        balance = 0
        for tx in self.transactions:
            if tx.output["from"] == self.address:
                balance -= tx.output["amount"]
                balance -= tx.output["fee"]
                balance -= tx.output["taxed"]
            if tx.input["to"] == self.address:
                balance += tx.input["amount"]
        return balance

    @staticmethod
    def calculate_balance(blockchain, address):
        bal = 0
        for b in blockchain.chain:
            for tx in b.transactions:
                if tx.output["from"] == str(address):
                    deduct = tx.output["amount"] + tx.output["fee"] + tx.output["taxed"]
                    bal -= deduct
                if tx.input["to"] == str(address):
                    net = tx.input["amount"]
                    bal += net
        return bal

    def burnwallet(self):
        if self.BurnWallet_grant:
            # self.send("RECEIVER",self.balance)
            self.balance = 0
            self.Lock = True

    def add_tx(self, tx):
        self.transactions.append(tx)

    def sign(self, data):
        return self.private_key.sign(data, ec.ECDSA(hashes.SHA256())).hex()

    @staticmethod
    def verify(pub_key_pem: str, data: bytes, signature: str):
        try:
            pub_key = load_pem_public_key(pub_key_pem.encode("utf-8"), backend=default_backend())
            pub_key.verify(
                bytes.fromhex(signature),
                data,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except InvalidSignature:
            print("[!] Invalid signature")
            return False
        except Exception as e:
            print(f"[ERROR] Signature verification failed: {e}")
            return False

    def serialize_pub_key(self):
        return self.private_key.public_key().public_bytes(encoding=serialization.Encoding.PEM,
                                                          format=serialization.PublicFormat.SubjectPublicKeyInfo).decode(
            "utf-8")

    def gen_private_key(self):
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode("utf-8")
        private_key_hex = hex(self.private_key.private_numbers().private_value)
        return [pem, private_key_hex]

    def to_json(self):
        return {"balance": self.balance}

    def calculate_balance_by_transactions(self):
        balance = 0
        for tx in self.transactions:
            if tx.output["from"] == self.address:
                balance -= tx.output["amount"]
                balance -= tx.output["fee"]
                balance -= tx.output["taxed"]
            if tx.input["to"] == self.address:
                balance += tx.input["amount"]
        return balance

    def to_dict(self):
        return {
            "address": self.address,
            "timestamp": self.timestamp,
            "public_key": self.public_key,
            "BurnWallet_grant": self.BurnWallet_grant,
            "Lock": self.Lock,
            "balance": self.balance,
            "transactions": [tx.to_dict() for tx in self.transactions]
        }

    def from_dict(self, data):
        self.address = data["address"]
        self.timestamp = data["timestamp"]
        self.public_key = data["public_key"]
        self.BurnWallet_grant = data["BurnWallet_grant"]
        self.Lock = data["Lock"]
        self.balance = data["balance"]
        self.transactions = [TX(self, "REC", 1).from_dict(tx) for tx in data["transactions"]] or []

    def send_ok(self, tx):
        if self.balance < tx.amount + tx.TAX + tx.FEE:
            print(f"Not enough balance. Balance: {self.balance}, Required:{tx.amount + tx.TAX + tx.FEE}")
            return False
        if self.Lock:
            print("Wallet is locked")
            return False
        if self.BurnWallet_grant:
            print("BurnWallet grant is active")
            return False
        if not self.verify(self.public_key, tx._tx_digest(), tx.signature):
            print(f"Invalid signature tx_Signature:{tx.signature}, calculated_Signature:{self.sign(tx._tx_digest())}")
            return False
        inflation = tx.TAX + tx.FEE
        if tx.amount + inflation > self.balance:
            print("Not enough balance")
            raise Exception(
                f"Not enough balance. Required: {tx.amount + inflation}, Available: {self.balance}")
        return True

    def send(self, to, amount):
        tx = TX(self.address, self.public_key, to, amount)
        tx.signature = self.sign(data=tx._tx_digest())
        tx.update_tx()
        if self.send_ok(tx) and tx.is_valid():
            tx.status = "Pending"
            tx.update_tx()
            return tx
        else:
            raise Exception("Transaction failed")

    def __repr__(self):
        return f"{self.balance}"
