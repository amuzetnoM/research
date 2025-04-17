from web3 import Web3, Account
from eth_account.messages import encode_defunct
from .config import Config

class WalletManager:
    def __init__(self, web3: Web3):
        self.web3 = web3
        self.account = Account.from_key(Config.PRIVATE_KEY)

    def get_address(self):
        return self.account.address

    def sign_message(self, message: str):
        msg = encode_defunct(text=message)
        return self.web3.eth.account.sign_message(msg, private_key=Config.PRIVATE_KEY)

    def send_transaction(self, tx):
        tx['nonce'] = self.web3.eth.get_transaction_count(self.account.address)
        tx['chainId'] = Config.CHAIN_ID
        signed = self.web3.eth.account.sign_transaction(tx, Config.PRIVATE_KEY)
        return self.web3.eth.send_raw_transaction(signed.rawTransaction)
