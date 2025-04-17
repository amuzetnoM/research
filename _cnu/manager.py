from fastapi import FastAPI, HTTPException
from .web3_connector import Web3Connector
from .wallet import WalletManager
from .nft_memory import NFTMemoryManager
from .memory_db import MemoryDB
from .ipfs_storage import IPFSStorage
from .config import Config

app = FastAPI(title="Core Neurological State Manager (CNU)")

# Initialize modules
web3c = Web3Connector()
wallet = WalletManager(web3c.get_web3())
# Assume contract ABI and address are loaded elsewhere
# contract = web3c.get_web3().eth.contract(address=..., abi=...)
contract = None  # Placeholder
nft_mgr = NFTMemoryManager(web3c.get_web3(), contract, wallet)
db = MemoryDB()
ipfs = IPFSStorage()

@app.post("/memory")
def store_memory_block(memory: bytes, prev_hash: str = ""):
    # Compress/encrypt memory as needed (omitted for brevity)
    cid = ipfs.add_data(memory)
    memory_hash = "TODO: hash(memory)"  # Replace with real hash
    metadata_uri = cid
    db.add_memory(memory_hash, prev_hash, metadata_uri, memory)
    # Mint NFT (gasless)
    nft_mgr.mint_memory_nft(memory_hash, metadata_uri, prev_hash)
    return {"memory_hash": memory_hash, "metadata_uri": metadata_uri}

@app.get("/memory/{memory_hash}")
def get_memory_block(memory_hash: str):
    block = db.get_memory(memory_hash)
    if not block:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {
        "memory_hash": block.memory_hash,
        "prev_hash": block.prev_hash,
        "metadata_uri": block.metadata_uri,
        "created_at": block.created_at
    }

# Add endpoints for querying, AI summarization, NFT transfer, etc.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
