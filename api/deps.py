from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from converter_services.service import FocusConverterService, FileDeleterService
from config import UPLOAD_DIR, DOWNLOAD_DIR

templates = Jinja2Templates(directory="templates")

def get_focus_converter_service() -> FocusConverterService:
    return FocusConverterService(
        input_dir=UPLOAD_DIR,
        output_dir=DOWNLOAD_DIR
    )

def get_file_deleter_service() -> FileDeleterService:
    return FileDeleterService()