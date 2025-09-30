from typing import Union

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from finops_analyzer.api.v1.pages import router as pages_v1_router
from finops_analyzer.api.deps import templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pages_v1_router, tags=["pages"])


@app.get("/")
def read_root():
    return RedirectResponse(url="/pages/")


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}


@app.post("/converter")
async def converter_post(
        request: Request,
        file_upload: UploadFile,
        provider: str = None,
        provider_detection: str = None, 
    ):
    print(f"Request: {request}")
    url_str = request.url
    query_str = request.body
    print(f"Request object: {url_str} - {query_str}")
    filename = file_upload.filename
    content = await file_upload.read()
    print(f"Received file: {filename} with size {len(content)} bytes")
    # Process form data here
    return templates.TemplateResponse("converter.html", {"request": request, "message": "File processed"})