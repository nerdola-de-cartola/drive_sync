import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from database import get_session
from file import FileModel
from helpers import get_all_files_recursive, get_files_and_folders, init_db

WATCH_DIRS = ["/home/matheus-lucas/Downloads"]

class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.db = get_session()
        files, folders = get_files_and_folders(WATCH_DIRS)
        db = get_session()
        init_db(files, db)

    def on_created(self, event):
        if event.is_directory or not os.path.exists(event.src_path):
            return
        
        print(f"[CREATE] {event.src_path}")
        FileModel.from_path(event.src_path).add_if_new(self.db)

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"[DELETE] {event.src_path}")
            file = self.db.query(FileModel).filter_by(local_path=event.src_path).first()
            if file:
                file.deleted = True
                self.db.commit()
                self.db.flush()
            return

        files = get_all_files_recursive(event.src_path) # TODO get children
        print(files)

        for file in files:
            print(f"[DELETE] {file}")

def main():
    
    observer = Observer()
    handler = ChangeHandler()

    for path in WATCH_DIRS:
        observer.schedule(handler, path, recursive=True)

    observer.start()
    print("[WATCHING] Directories...")

    try:
        observer.join()
    except KeyboardInterrupt:
        print("[STOPED]")
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main()
