from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import Config
import datetime

Base = declarative_base()

class MemoryBlock(Base):
    __tablename__ = "memory_blocks"
    id = Column(Integer, primary_key=True)
    memory_hash = Column(String, unique=True, index=True)
    prev_hash = Column(String)
    metadata_uri = Column(String)
    data = Column(LargeBinary)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

engine = create_engine(Config.DB_URL)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

class MemoryDB:
    def __init__(self):
        self.session = Session()

    def add_memory(self, memory_hash, prev_hash, metadata_uri, data):
        block = MemoryBlock(
            memory_hash=memory_hash,
            prev_hash=prev_hash,
            metadata_uri=metadata_uri,
            data=data
        )
        self.session.add(block)
        self.session.commit()

    def get_memory(self, memory_hash):
        return self.session.query(MemoryBlock).filter_by(memory_hash=memory_hash).first()
