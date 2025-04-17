import json
from web3 import Web3
from .config import Config
from .wallet.py import WalletManager

class NFTMemoryManager:
    def __init__(self, web3: Web3, contract, wallet: WalletManager):
        self.web3 = web3
        self.contract = contract
        self.wallet = wallet

    def mint_memory_nft(self, memory_hash: str, metadata_uri: str, prev_hash: str = ""):
        # Gasless minting via meta-tx/relayer (simplified)
        tx = self.contract.functions.mintMemoryNFT(
            self.wallet.get_address(), memory_hash, metadata_uri, prev_hash
        ).build_transaction({
            'from': self.wallet.get_address(),
            'gas': 500_000,
            'gasPrice': 0  # Gasless: relayer will pay
        })
        return self.wallet.send_transaction(tx)

    def get_memory_nft(self, token_id: int):
        return self.contract.functions.tokenURI(token_id).call()
