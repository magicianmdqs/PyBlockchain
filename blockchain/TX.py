import datetime as dt
import uuid
from Crypto.Hash import SHA256
from blockchain.config import TAX, FEE
import json
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key

class TX:
    def __init__(self, sender_address:str,sender_pub_key:str, recv: str, amount: float,signature=None):
        self.timestamp = dt.datetime.now(dt.UTC).timestamp()
        self.id = SHA256.new(f"{str(uuid.uuid4())}{self.timestamp}".encode()).hexdigest()
        self.recv = recv
        self.sender_address = sender_address
        self.sender_pub_key = sender_pub_key
        self.amount = float(amount)
        self.TAX = float(self.amount * TAX)
        self.FEE = float(self.amount * FEE)
        self.signature = signature
        self.confirmation = 0
        self.status = None
        self.output = self._create_output()
        self.input = self._create_input()

    def _create_output(self):
        return {
            "type": "OUT",
            "id": self.id,
            "taxed": self.TAX,
            "fee": self.FEE,
            "timestamp": self.timestamp,
            "sender_pub_key": self.sender_pub_key,  # Expecting 'serialize_pub_key' in sender class
            "signature": self.signature,
            "from": self.sender_address,  # The sender's address
            "to": self.recv,  # The recipient's address
            "amount": self.amount,  # The transfer amount
            "confirmation":self.confirmation,
            "status": self.status,
        }

    def _create_input(self):
        return {
            "type": "IN",
            "id": self.id,
            "timestamp": self.timestamp,
            "sender_pub_key": self.sender_pub_key,
            "signature": self.signature,
            "from": self.sender_address,
            "to": self.recv,
            "amount": self.amount,
            "confirmation":self.confirmation,
            "status": self.status,
        }

    def _tx_digest(self):
        return f"{self.id}{self.timestamp}".encode("utf-8")

    def is_valid(self):
        if not self.signature:
            print("[INVALID] Missing signature")
            return False

        try:
            pub_key = load_pem_public_key(self.sender_pub_key.encode("utf-8"), backend=default_backend())
            pub_key.verify(
                bytes.fromhex(self.signature),
                self._tx_digest(),
                ec.ECDSA(hashes.SHA256())
            )
        except InvalidSignature:
            print("[INVALID] Signature does not match transaction digest")
            return False
        except Exception as e:
            print(f"[ERROR] Verification failed: {e}")
            return False

        if self.amount <= 0 or self.FEE < 0 or self.TAX < 0:
            print("[INVALID] Non-positive amount, fee or tax")
            return False

        if self.sender_address != self.output["from"] or self.recv != self.output["to"]:
            print("[INVALID] Address mismatch")
            return False

        if self.output["id"] != self.input["id"]:
            print("[INVALID] Input/output ID mismatch")
            return False

        return True


    def to_json(self):
        return json.dumps({
            self.id:{
                    "output":self.output,
                    "input":self.input}
        },indent=4)

    def from_dict(self,tx):
        self.output = tx["output"]
        self.input = tx["input"]
        self.id = tx["output"]["id"]
        self.timestamp = tx["output"]["timestamp"]
        self.recv = tx["output"]["to"]
        self.sender_address = tx["output"]["from"]
        self.sender_pub_key = tx["output"]["sender_pub_key"]
        self.amount = tx["output"]["amount"]
        self.TAX = tx["output"]["taxed"]
        self.FEE = tx["output"]["fee"]
        self.signature = tx["output"]["signature"]
        self.confirmation = tx["output"]["confirmation"]
        self.status = tx["output"]["status"]
        return self

    def to_dict(self):
        return {
            "output":self.output,
            "input":self.input
        }

    def update_tx(self):
        self.output = self._create_output()
        self.input = self._create_input()





