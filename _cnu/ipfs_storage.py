import ipfshttpclient
from .config import Config

class IPFSStorage:
    def __init__(self):
        self.client = ipfshttpclient.connect(Config.IPFS_API)

    def add_data(self, data: bytes) -> str:
        res = self.client.add_bytes(data)
        return f"ipfs://{res}"

    def get_data(self, cid: str) -> bytes:
        return self.client.cat(cid.replace("ipfs://", ""))
