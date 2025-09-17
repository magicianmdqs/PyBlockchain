import datetime as dt
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
import json
from .TX import TX
import os
private_key_path = os.path.join(os.path.dirname(__file__), "private.pem")
public_key_path = os.path.join(os.path.dirname(__file__), "public.pem")

def genesis():
    genesis_block = Block(block_no=0, owner="Genesis_Owner")
    genesis_block.last_hash = "UNKNOWN"
    genesis_block.sign_block(private_key_path=private_key_path)
    genesis_block.hash = genesis_block.gen_hash()
    genesis_block.sign_block(private_key_path=private_key_path)
    return genesis_block


class Block:
    def __init__(self, transactions=None,timestamp=None, hash=None, last_hash=None,
                 block_no=None, signature=None, owner=None):
        self.timestamp = timestamp or dt.datetime.now(dt.UTC).timestamp()
        self.last_hash = last_hash
        self.transactions = transactions or []
        self.block_no = block_no
        self.signature = signature
        self.owner = owner
        self.hash = hash or "UNHASHED"
        #Every Block should have a ledger that keeps the record of all transactions
        #Hash is based on the block number, last_hash, tx

    def sign_block(self, private_key_path=private_key_path):
        key = RSA.import_key(open(private_key_path, "r").read())
        hash_obj = SHA256.new(self.hash.encode())
        self.signature = pkcs1_15.new(key).sign(hash_obj).hex()

    def gen_hash(self):
        return SHA256.new(f"{self.block_no}{self.last_hash}{self.transactions}".encode("utf-8")).hexdigest()

    def set_hash(self):
        self.hash = self.gen_hash()

    def sign_valid(self, public_key_path=public_key_path):
        try:
            key = RSA.import_key(open(public_key_path, "r").read())
            hash_obj = SHA256.new(self.hash.encode())
            pkcs1_15.new(key).verify(hash_obj, bytes.fromhex(self.signature))
            return True
        except (ValueError, TypeError):
            return False

    def hash_valid(self):
        new_hash = str(
            SHA256.new(f"{self.block_no}{self.last_hash}{self.transactions}".encode("utf-8")).hexdigest())
        return self.hash == new_hash

    def json_tx(self):
        dicttx={}
        for i in self.transactions:
            dicttx[i.id]={"output":i.output,
                          "input":i.input}
        return json.dumps(dicttx,indent=4)

    def to_dict(self):
        return {
            "block": self.block_no,
            "time": self.timestamp,
            "hash": self.hash,
            "last_hash": self.last_hash,
            "signature": self.signature,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "owner": self.owner
        }

    def from_dict(self, data):
        self.block_no = data["block"]
        self.timestamp = data["time"]
        self.hash = data["hash"]
        self.last_hash = data["last_hash"]
        self.signature = data["signature"]
        self.transactions = [TX().from_dict(tx) for tx in data["transactions"]]
        self.owner = data["owner"]

    def __repr__(self):
        return json.dumps({
            "Block": self.block_no,
            "Time": self.timestamp,
            "Hash": self.hash,
            "Last Hash": self.last_hash,
            "Signature": self.signature,
            "Transactions": {
                tx.id: {"output": tx.output, "input": tx.input}
                for tx in self.transactions
            },
            "Owner": self.owner
        },indent=4)




