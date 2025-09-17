import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from Account import Accounts
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from Blockchain import Blockchain
from TX import TX
from Block import Block


def test_Accounts():
    a = Accounts()
    a.balance = 10
    assert a.address
    assert a.balance == 10
    assert a.BurnWallet_grant == False
    a.BurnWallet_grant = True
    a.burnwallet()
    assert a.balance == 0
    assert a.Lock


def test_sign():
    a = Accounts()
    assert a.serialize_pub_key() == a.private_key.public_key().public_bytes(encoding=serialization.Encoding.PEM,
                                                              format=serialization.PublicFormat.SubjectPublicKeyInfo
                                                              ).decode("utf-8")
    assert a.verify(a.public_key_raw, a.public_key, a.sign(a.public_key))


def test_calculate_balance():
    bc = Blockchain()
    a=bc.create_wallet()
    a.balance=1000
    bc.generate_blocks(1,a.public_key)
    bc.transact(TX(a, "REC", 100))
    assert a.balance == (1000 - 100 - (100 * 0.011))
    assert bc.chain[-1].hash_valid()
    assert a.calculate_balance(bc, a.address) == a.balance
