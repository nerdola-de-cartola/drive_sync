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

class SyncHandler(FileSystemEventHandler):
    def __init__(self, service, synced_files):
        self.service = service
        self.synced_files = synced_files  # dict: {local_path: drive_file_id}

    def on_modified(self, event):
        if not event.is_directory:
            upload_file_to_drive(self.service, event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            upload_file_to_drive(self.service, event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            path = event.src_path
            if path in self.synced_files:
                file_id = self.synced_files[path]
                try:
                    self.service.files().delete(fileId=file_id).execute()
                    print(f'[DELETED] {path} (Drive ID: {file_id})')
                    del self.synced_files[path]
                except Exception as e:
                    print(f'[ERROR] Could not delete {path} from Drive: {e}')


# Inicia a sincronização em uma lista de diretórios
def start_sync(service, directories: List[str]):
    observers = []
    for path in directories:
        if not os.path.isdir(path):
            print(f'[WARN] Ignoring invalid directory: {path}')
            continue

        event_handler = SyncHandler(service)
        observer = Observer()
        observer.schedule(event_handler, path=path, recursive=True)
        observer.start()
        observers.append(observer)
        print(f'[WATCHING] {path}')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOPPING] Stopping all observers...")
        for obs in observers:
            obs.stop()
        for obs in observers:
            obs.join()

# Função principal com lista de diretórios
def main():
    # Coloque aqui os diretórios que deseja sincronizar
    directories_to_watch = [
        "/home/matheus-lucas/Downloads",
        "/home/matheus-lucas/Estudos",
    ]

    files, folders = get_files_and_folders(directories_to_watch)
    service = get_drive_service()
    db = get_session()

    init_db(files, db)



if __name__ == "__main__":
    main()
