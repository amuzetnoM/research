from web3 import Web3
from .config import Config

class Web3Connector:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(Config.WEB3_PROVIDER))
        assert self.web3.is_connected(), "Web3 provider not connected"

    def get_web3(self):
        return self.web3
