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


# Função principal com lista de diretórios
def main():
    # Coloque aqui os diretórios que deseja sincronizar
    directories_to_watch = [
        "/home/matheus-lucas/Downloads",
    ]

    files, folders = get_files_and_folders(directories_to_watch)
    service = get_drive_service()
    init_db(files, get_session())
    print("Init Database")

    while True:
        db = get_session()
        #print("Fetching files")
        files = FileModel.get_all(db)

        for file in files:
            try:
                file.link_with_remote(service, db)

                if file.deleted:
                    file.delete_from_remote(service, db)

                if file.need_to_update():
                    file.upload_to_drive(service, db)
            except Exception as e:
                pass
                
        time.sleep(5)
        


        



if __name__ == "__main__":
    main()
