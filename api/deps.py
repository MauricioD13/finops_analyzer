from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from finops_analyzer.focus_converter.service import FocusConverterService, FileDeleterService

templates = Jinja2Templates(directory="templates")

def get_focus_converter_service() -> FocusConverterService:
    return FocusConverterService("focus-converter")

def get_file_deleter_service() -> FileDeleterService:
    return FileDeleterService()