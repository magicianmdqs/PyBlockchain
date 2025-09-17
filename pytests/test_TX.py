import sys
from pathlib import Path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))
import pytest
from TX import TX  # Import the TX class
from config import TAX, FEE

# Mock Account class to represent the sender
class MockAccount:
    def __init__(self, balance, address="SENDER_ADDRESS", public_key="public_key", private_key="private_key"):
        self.balance = balance
        self.address = address
        self.public_key = public_key
        self.private_key = private_key

    def serialize_pub_key(self):
        # Mock the serialization of the public key
        return self.public_key

    def sign(self, message):
        # Mock the signing of a message
        return "mock_signature"


@pytest.fixture
def mock_account():
    return MockAccount(balance=1200)  # Mock account with a balance of 1200


def test_transaction_creation(mock_account):
    receiver = "RECEIVER_ADDRESS"
    amount = 1100
    tx = TX(mock_account, receiver, amount)

    # Verify transaction output
    assert tx.output["type"] == "OUT"
    assert tx.output["to"] == receiver
    assert tx.output["amount"] == amount
    assert tx.output["taxed"] == amount * TAX
    assert tx.output["fee"] == amount * FEE
    assert tx.output["sender_pub_key"] == mock_account.serialize_pub_key()
    assert tx.output["signature"] == "mock_signature"
    assert tx.output["from"] == mock_account.address


def test_insufficient_balance(mock_account):
    # Test case where the sender does not have enough balance
    with pytest.raises(Exception, match="Not enough balance"):
        TX(mock_account, "RECEIVER_ADDRESS", 1300)  # Transaction amount exceeds balance


def test_tax_fee_calculation(mock_account):
    amount = 10
    tx = TX(mock_account, "REC", amount)


    # Check tax and fee calculations
    assert tx.TAX == amount * TAX
    assert tx.FEE == amount * FEE
    assert mock_account.balance == (1200 - amount - tx.TAX - tx.FEE)  # Balance should be updated correctly


def test_transaction_input(mock_account):
    amount = 500
    tx = TX(mock_account, "REC", amount)

    # Check the input of the transaction
    assert tx.input["type"] == "IN"
    assert tx.input["amount"] == amount
    assert tx.input["from"] == mock_account.address
    assert tx.input["to"] == "REC"
    assert tx.input["sender_pub_key"] == mock_account.serialize_pub_key()

