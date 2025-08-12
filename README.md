# Drive Sync - Docker Setup

A Google Drive synchronization application that watches local directories and automatically syncs files to Google Drive.

## Prerequisites

- Docker and Docker Compose installed
- Google Drive API credentials (see setup instructions below)

## Setup

### 1. Google Drive API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API for your project
4. Create credentials (OAuth 2.0 Client ID) for a desktop application
5. Download the credentials JSON file and rename it to `credentials.json`
6. Place the `credentials.json` file in the `./credentials/` directory

### 2. Directory Structure

```
drive_sync/
├── src/                    # Source code
├── credentials/           # Google API credentials (not in git)
│   └── credentials.json   # Your Google Drive API credentials
├── data/                 # Persistent database storage
├── Dockerfile
├── docker-compose.yml
└── environment.yml       # Conda dependencies
```

## Usage

### Install dependencies

```bash
conda env create -f environment.yml
conda activate activate drive_sync
```

### Run the Application

```bash
python src/main.py
```

#### Environment Variables:

- `WATCH_DIR`: Directory to watch for file changes
- `CREDENTIALS_DIR`: Directory containing Google Drive credentials
- `DATA_DIR`: Directory for database storage
- `SUPER_FOLDER`: Base folder for relative path calculations
