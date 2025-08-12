import os
from googleapiclient.http import MediaFileUpload
from auth import get_drive_service
from file import FileModel


def get_remote_file(service, folder_id: str, filename: str):
    """Verifica se já existe um arquivo com o nome na pasta remota."""
    query = (
        f"'{folder_id}' in parents and "
        f"name = '{filename}' and trashed = false"
    )
    results = service.files().list(q=query, spaces='drive', fields='files(id, name, size, md5Checksum, modifiedTime)').execute()
    files = results.get('files', [])
    return files[0] if files else None

def update_file_on_drive(service, file: FileModel):
    if not file.remote_id:
        raise Exception("File does not have a remote id")

    print(f'[UPDATE] {file.local_path} - Replacing remote file.')
    media = MediaFileUpload(file.local_path, resumable=True)
    updated = service.files().update(
        fileId=file.remote_id,
        media_body=media
    ).execute()
    return updated['id']

# Retorna o id remoto do arquivo
def upload_file_to_drive_if_different(service, file: FileModel) -> str:
    folder_id = ensure_drive_path(service, file.remote_folder)
    filename = os.path.basename(file.local_path)

    # Verifica se o arquivo já existe
    existing_file = get_remote_file(service, folder_id, filename)

    if existing_file:
        local_size = os.path.getsize(file.local_path)
        remote_size = int(existing_file.get('size', -1))

        if local_size == remote_size and file.get_checksum() == existing_file.get("md5Checksum"):
            print(f'[SKIPPED] {file.local_path} - Content identical to remote.')
            return existing_file['id']
        else:
            return update_file_on_drive(service, file, existing_file)
    else:
        return upload_file_to_drive(service, file)

def upload_file_to_drive(service, file: FileModel):
    """
    Faz upload do arquivo local_path para a pasta remota remote_folder_path no Drive,
    criando a estrutura de pastas se necessário.
    """
    folder_id = ensure_drive_path(service, file.remote_folder)
    file_metadata = {
        'name': os.path.basename(file.local_path),
        'parents': [folder_id]
    }

    try:
        media = MediaFileUpload(file.local_path, resumable=True)
    except Exception as e:
        print(e)
        return None

    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'[UPLOADED] {file.local_path} → Drive ID: {uploaded_file.get("id")}')
    return uploaded_file.get("id")

def get_drive_file_id_by_name(service, filename):
    try:
        response = service.files().list(
            q=f"name = '{os.path.basename(filename)}' and trashed = false",
            spaces='drive',
            fields="files(id, name)",
            pageSize=1
        ).execute()
        files = response.get('files', [])
        if files:
            return files[0]['id']
        else:
            return None
    except Exception as e:
        print(f"[ERROR] Failed to get Drive ID for {filename}: {e}")
        return None

def get_or_create_drive_folder(service, folder_name, parent_id=None):
    """
    Retorna o ID da pasta no Drive com o nome especificado dentro do parent_id.
    Cria a pasta se ela não existir.
    """
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    else:
        query += " and 'root' in parents"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)',
        pageSize=1
    ).execute()

    files = results.get('files', [])
    if files:
        return files[0]['id']
    else:
        # Criar a pasta
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

def ensure_drive_path(service, remote_path):
    """
    Garante que toda a estrutura de pastas do remote_path exista no Drive.
    Retorna o ID da pasta final.
    Exemplo: 'work/example/subfolder' cria ou retorna o ID da subfolder.
    """
    parts = remote_path.strip('/').split('/')
    parent_id = None  # Começa da raiz do Drive

    for part in parts:
        parent_id = get_or_create_drive_folder(service, part, parent_id)
    return parent_id

def main():
    local_file = "/home/matheus-lucas/Downloads/events3.csv"
    service = get_drive_service()
    upload_file_to_drive_if_different(service, FileModel.from_path(local_file))
    # print(ensure_drive_path(service, "Downloads/thunderbird.tmp/"))

if __name__ == "__main__":
    main()

