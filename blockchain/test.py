from blockchain.Blockchain import Blockchain
from blockchain.Account import Accounts
from blockchain.config import *

if __name__ == "__main__":
    bc = Blockchain()
    account_0 = Accounts(blockchain=bc)
    bc.generate_blocks(TEST_AUTO_GEN,
                       [f"Node {i}" for i in range(1, TEST_AUTO_GEN + 1)],
                       "None")
    bc.check_bc_validation()
    bc.get_blocks_info()
    # bc.get_blocks_info()
    # bc.check_bc_validation()
    # print(bc.find_block(block_no=5))
    # chain = bc.export_chain()
    # with open("blockchain.json", "w") as f:
    #     f.write(chain)
    # print(chain)
    # bc.chain = []
    # bc = bc.load_chain(chain)
    # account_0.balance = 102
    # # tx=TX(account_0,"REC",100)
    # # bc.add_block(bc.manual_craft(transactions=tx))
    # bc.check_bc_validation()
    # for i in range(0,len(bc.chain)):
    #     current=bc.chain[i]
    #     prev=bc.chain[i-1]
    #     print(f"{current.block_no}:\n{prev.hash}\n{current.last_hash}")
    #
    # print(bc.no_blocks())