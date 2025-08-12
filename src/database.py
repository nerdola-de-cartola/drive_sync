import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

Base = declarative_base()

def get_session(db_path=None):
    if db_path is None:
        data_dir = os.getenv('DATA_DIR', 'data/')
        db_path = f"sqlite:///{os.path.join(data_dir, 'sqlite.db')}"
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()