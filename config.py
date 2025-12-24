import os
from pathlib import Path

# Create upload directory
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./upload"))
DOWNLOAD_DIR = Path(os.getenv("OUTPUT_DIR", "./download"))

BASE_OUTPUT_NAME = "focus-converted-output"
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
