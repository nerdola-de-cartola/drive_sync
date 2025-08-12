import os
from typing import List
from sqlalchemy.orm import Session
from file import FileModel


def get_all_files_recursive(directory):
    """
    Returns a list of all file paths under the given directory (recursive).
    """
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            file_paths.append(os.path.join(root, name))
    return file_paths

import os

def get_all_folders_recursive(directory):
    """
    Returns a list of all folders under the given directory (recursive).
    Includes the root directory.
    """
    folder_paths = []
    for root, dirs, files in os.walk(directory):
        folder_paths.append(root)
    return folder_paths

def init_db(files: List[str], db: Session):
    for file in files:
        FileModel.from_path(file).add_if_new(db)

    db.commit()
    count = db.query(FileModel).count()
    print(f"{count} files in database")

def get_files_and_folders(directories_to_watch):
    files = []
    folders = []

    for dir in directories_to_watch:
        files += get_all_files_recursive(dir)
        folders += get_all_folders_recursive(dir)

    return (files, folders)

def need_update(local_file: FileModel, service):
    from drive import ensure_drive_path, get_remote_file
    folder_id = ensure_drive_path(service, local_file.remote_folder)
    filename = os.path.basename(local_file.local_path)

    remote_file = get_remote_file(service, folder_id, filename)
    local_size = os.path.getsize(local_file.local_path)
    remote_size = int(remote_file.get('size', -1))

    if local_size == remote_size and local_file.get_checksum() == remote_file.get("md5Checksum"):
        return False

    return True