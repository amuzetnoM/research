import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Web3/Chain
    WEB3_PROVIDER = os.getenv("WEB3_PROVIDER", "https://alfajores-forno.celo-testnet.org")
    CHAIN_ID = int(os.getenv("CHAIN_ID", "44787"))  # Celo Alfajores
    PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
    NFT_CONTRACT_ADDRESS = os.getenv("NFT_CONTRACT_ADDRESS", "")
    RELAYER_URL = os.getenv("RELAYER_URL", "")
    RELAYER_API_KEY = os.getenv("RELAYER_API_KEY", "")

    # Storage
    IPFS_API = os.getenv("IPFS_API", "/dns/localhost/tcp/5001/http")
    DB_URL = os.getenv("DB_URL", "sqlite:///memory.db")

    # Security
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "changeme")
    HASH_ALGO = os.getenv("HASH_ALGO", "sha3_256")

    # Misc
    AI_SUMMARIZATION = os.getenv("AI_SUMMARIZATION", "false").lower() in ("1", "true", "yes")
