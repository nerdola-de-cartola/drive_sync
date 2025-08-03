from typing import ClassVar, Optional
from pydantic import BaseModel
import os
import hashlib
from sqlalchemy import Column, Integer, String, LargeBinary, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import os
import hashlib
from database import Base, get_session
    
def calculate_checksum(file_path: str, chunk_size: int = 8192):
    """Calculate MD5 checksum of local file."""
    hash_md5 = hashlib.md5()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()

class FileModel(Base):
    __tablename__ = 'files'
    super_folder: ClassVar[str] = "/home/matheus-lucas/"

    id = Column(Integer, primary_key=True)
    local_path = Column(String, unique=True, nullable=False)
    relative_path = Column(String, unique=True, nullable=False)
    remote_folder = Column(String, nullable=False)
    size = Column(Integer)


    @classmethod
    def from_path(cls, local_path: str) -> "FileModel":
        relative_path = os.path.relpath(local_path, cls.super_folder)
        remote_folder=os.path.dirname(relative_path)

        return cls(
            local_path=local_path,
            relative_path=relative_path,
            remote_folder=remote_folder,
            size=os.path.getsize(local_path),
        )
    
    def add_if_new(self, db: Session) -> "FileModel":
        existing = db.query(FileModel).filter_by(local_path=self.local_path).first()
        if existing:
            return existing

        db.add(self)
        db.commit()
        db.refresh(self)
        return self
    
    def get_checksum(self):
        return calculate_checksum(self.local_path)
    
    def __str__(self) -> str:
        return (
            f"FileModel(id={self.id}, "
            f"local_path='{self.local_path}', "
            f"relative_path='{self.relative_path}', "
            f"remote_folder='{self.remote_folder}', "
            f"size={self.size})"
        )


def main():
    session = get_session()
    file_path = "/home/matheus-lucas/Downloads/events3.csv"
    file_entry = FileModel.from_path(file_path)

    existing = session.query(FileModel).filter_by(local_path=file_entry.local_path).first()
    if existing:
        print(f"File already in DB: {existing}")
    else:
        session.add(file_entry)
        session.commit()
        print(f"Saved file: {file_entry}")
    return

if __name__ == "__main__":
    main()

