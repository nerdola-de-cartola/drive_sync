import os
import time
from typing import List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from googleapiclient.http import MediaFileUpload
from auth import get_drive_service
from drive import *
from database import get_session
from helpers import get_files_and_folders, init_db
from observer import ChangeHandler
from sqlalchemy.orm import Session


def handle_file(file: FileModel, service, db: Session):
    try:
        file.link_with_remote(service, db)

        if file.deleted:
            file.delete_from_remote(service, db)

        if file.need_to_update():
            file.upload_to_drive(service, db)
    except Exception as e:
        pass
                
def main():
    directories_to_watch = [
        "/home/matheus-lucas/Downloads",
    ]

    files, folders = get_files_and_folders(directories_to_watch)
    service = get_drive_service()
    db = get_session()
    init_db(files, db)
    observer = Observer()
    handler = ChangeHandler(db)

    for path in directories_to_watch:
        observer.schedule(handler, path, recursive=True)

    observer.start()
    print("[WATCHING] Directories...")

    try:
        while True:
            print("[FETCH] files")
            files = FileModel.get_all(db)

            for file in files:
                handle_file(file, service, db)

            time.sleep(5)
    except KeyboardInterrupt:
        print("[STOPED]")
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main()
