from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from finops_analyzer.focus_converter import FocusConverterService
templates = Jinja2Templates(directory="templates")

def get_focus_converter_service():
    yield FocusConverterService() # REVISAR