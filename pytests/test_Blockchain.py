import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))
from blockchain.Blockchain import Blockchain
import pytest
import os
from blockchain.Block import Block
from Crypto.PublicKey import RSA
from blockchain.TX import TX

bc=Blockchain()
accounts = bc.create_wallet()
accounts.balance=1000
tx1=TX(accounts.address,accounts.public_key,"REC",100)
tx2=TX(accounts.address,accounts.public_key,"REC",99)


def test_Blockchain():
    bc = Blockchain()
    a = bc.create_wallet()
    a.balance=1000
    bc.generate_blocks(2, owner_public_key=a.serialize_pub_key())
    assert bc.no_blocks() == len(bc.chain)
    assert bc.chains_last_hash() == bc.chain[-1].hash
    assert bc.chain[0].hash == bc.chain[1].last_hash
    b4 = bc.craft_and_add(a.serialize_pub_key())
    bc.add_block(b4)
    assert bc.no_blocks() == len(bc.chain)
    for i in range(1, len(bc.chain) - 1):
        current = bc.chain[i]
        prev = bc.chain[i - 1]
        assert current.last_hash == prev.hash


@pytest.fixture(scope="module")
def rsa_keys():
    if not os.path.exists("private.pem") or not os.path.exists("public.pem"):
        key = RSA.generate(2048)
        with open("private.pem", "wb") as priv_file:
            priv_file.write(key.export_key())
        with open("public.pem", "wb") as pub_file:
            pub_file.write(key.publickey().export_key())
    return "private.pem", "public.pem"


def test_blockchain_initialization():
    bc = Blockchain()
    assert len(bc.chain) == 1  # Genesis block
    assert isinstance(bc.chain[0], Block)


def test_block_addition_and_linking(rsa_keys):
    bc = Blockchain()
    txs = [[tx1], [tx2]]
    bc.generate_blocks(2, txs)
    assert len(bc.chain) == 3
    assert bc.chain[1].last_hash == bc.chain[0].hash
    assert bc.chain[2].last_hash == bc.chain[1].hash


def test_export_and_load_chain():
    bc = Blockchain()
    bc.generate_blocks(2)
    exported = bc.export_chain()
    loaded = Blockchain().load_chain(exported)
    assert len(loaded.chain) == len(bc.chain)
    assert loaded.chain[1].hash == bc.chain[1].hash


def test_block_finding():
    bc = Blockchain()
    bc.generate_blocks(2)
    found = bc.find_block(block_no=2)
    assert any(b.block_no == 2 for b in found)


def test_chain_validation_fails_on_tampering():
    bc = Blockchain()
    bc.generate_blocks(1)
    assert bc.check_bc_validation()
