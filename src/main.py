import os
import time
from typing import List
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from googleapiclient.http import MediaFileUpload
from auth import get_drive_service
from drive import *
from database import get_session
from helpers import get_files_and_folders, init_db
from observer import ChangeHandler
from sqlalchemy.orm import Session

# Load environment variables from .env file
load_dotenv()


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
    # Use environment variable or default to container path
    watch_dir = os.getenv('WATCH_DIR', 'Downloads/')
    directories_to_watch = [dir for dir in watch_dir.split(":")]

    if len(directories_to_watch) == 0:
        print("No directories to watch")
        return

    files, folders = get_files_and_folders(directories_to_watch)
    service = get_drive_service()
    db = get_session()
    init_db(files, db)
    observer = Observer()
    handler = ChangeHandler(db)

    for path in directories_to_watch:
        observer.schedule(handler, path, recursive=True)

    observer.start()
    print(f"[WATCHING] Directories {directories_to_watch}")

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
