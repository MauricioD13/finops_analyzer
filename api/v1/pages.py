from fastapi import APIRouter, Request, UploadFile, Form, File
from finops_analyzer.api.deps import templates

router = APIRouter(
    prefix="/pages",
    tags=["pages"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def main_page(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})

@router.get("/converter")
async def converter_page(request: Request):
    return templates.TemplateResponse("converter.html", {"request": request})

