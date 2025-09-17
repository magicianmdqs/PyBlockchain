from Block import Block
from Blockchain import Blockchain
from TX import TX
from Account import Accounts
from ledger import Ledger

bc = Blockchain()
a=bc.create_wallet()
a.balance=105
bc.init_system_account()
bc.transact(TX(a,"REC",20))
bc.transact(TX(a,"REC",20))
bc.transact(TX(a,"REC",20))
bc.transact(TX(a,"REC",20))
bc.transact(TX(a,"REC",20))
print(a.balance)
block=bc.chain[1].to_dict()
tx=bc.chain[1].transactions[0].to_dict()
TX(a.address,a.public_key,"REC",10).from_dict(tx)
