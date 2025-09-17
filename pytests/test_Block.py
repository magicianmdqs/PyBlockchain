import pytest
import os
from Block import Block, genesis  # adjust import if file name is different
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey


@pytest.fixture(scope="module")
def rsa_keys():
    # Generate RSA keys for testing if not provided
    if not os.path.exists("private.pem") or not os.path.exists("public.pem"):
        key = RSA.generate(2048)
        with open("private.pem", "wb") as priv:
            priv.write(key.export_key())
        with open("public.pem", "wb") as pub:
            pub.write(key.publickey().export_key())

    return "private.pem", "public.pem"


def test_block_creation_and_hashing(rsa_keys):
    block = Block(transactions=["tx1", "tx2"], block_no=1, last_hash="abc123", owner="Alice")
    block.hash = block.gen_hash()
    assert block.hash_valid(), "Hash validation failed"

def test_block_signing_and_verification(rsa_keys):
    priv, pub = rsa_keys
    block = Block(transactions=["tx1"], block_no=2, last_hash="xyz789", owner="Bob")
    block.hash = block.gen_hash()
    block.sign_block(private_key_path=priv)
    assert block.signature is not None, "Signature not generated"
    assert block.sign_valid(public_key_path=pub), "Signature verification failed"

def test_genesis_block_valid(rsa_keys):
    _, pub = rsa_keys
    g = genesis()
    assert g.block_no == 0
    assert g.last_hash == "UNKNOWN"
    assert g.hash_valid(), "Genesis block hash invalid"
    assert g.sign_valid(public_key_path=pub), "Genesis block signature invalid"
