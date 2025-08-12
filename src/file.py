import os
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import Session
import hashlib
from database import Base, get_session
from datetime import datetime, timedelta, timezone
from typing import ClassVar

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
    last_upload = Column(DateTime, nullable=True)
    remote_id = Column(String, nullable=True)
    remote_folder_id = Column(String, nullable=True)
    deleted = Column(Boolean, nullable=False, default=False)
    # created_time = Column(DateTime, default=datetime.utcnow)
    # last_update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    
    @classmethod
    def fetch_from_path(cls, db: Session, path: str):
        return FileModel.from_path(path).fetch(db)
    
    @classmethod
    def fetch_or_add_from_path(cls, db: Session, path: str):
        file = FileModel.from_path(path)
        fetched = file.fetch(db)
        if fetched:
            return fetched
        
        db.add(file)
        db.commit()
        return file.fetch(db)
    
    @classmethod
    def get_all(cls, db: Session):
        return db.query(FileModel).all()
    
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
    
    def get_create_time(self) -> DateTime:
         stat = os.stat(self.local_path)
         return datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)

    def get_last_update_time(self) -> DateTime:
         stat = os.stat(self.local_path)
         return datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

    def fetch(self, db):
        return db.query(FileModel).filter_by(local_path=self.local_path).first()
    
    def get_last_upload(self):
        return self.last_upload.replace(tzinfo=timezone.utc)
    
    def link_with_remote(self, service, db: Session):
        if self.remote_id and self.remote_folder_id:
            return

        from drive import ensure_drive_path, get_remote_file, upload_file_to_drive

        self.remote_folder_id = ensure_drive_path(service, self.remote_folder)
        filename = os.path.basename(self.local_path)
        remote_file = get_remote_file(service, self.remote_folder_id, filename)

        if remote_file:
            self.remote_id = remote_file.get("id")
            self.last_upload = datetime.fromisoformat(remote_file.get("modifiedTime").replace("Z", "+00:00"))
        else:
            self.remote_id = upload_file_to_drive(service, self)
            self.last_upload = datetime.now(tz=timezone.utc)

        db.commit()

    def upload_to_drive(self, service, db: Session):
        from drive import update_file_on_drive

        if not self.remote_id or not self.remote_folder_id:
            raise Exception("File not linked with remote")

        update_file_on_drive(service, self)
        self.last_upload = datetime.now(tz=timezone.utc)
        db.commit()

    def need_to_update(self):
        local_update = self.get_last_update_time()
        remote_update = self.get_last_upload()

        diff = local_update - remote_update

        if diff > timedelta(minutes=5):
            return True
        
        return False
    
    def delete_from_remote(self, service, db: Session):
        from drive import delete_file_by_id
        delete_file_by_id(self.remote_id, service)
        db.delete(self)
        db.commit()

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

