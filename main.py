from typing import Union

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
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
    if provider:
        print(f"Provider: {provider}")
    if provider_detection:
        print(f"Provider detection: {provider_detection}")
    else:
        print("Params not received")
    #print(f"Request: {request}")
    #url_str = request.url
    try:
        query_str = await request.form()
        print(f"Request object: {query_str}")
    except Exception as e:
        print(e)
    
    filename = file_upload.filename
    content = await file_upload.read()
    print(f"Received file: {filename} with size {len(content)} bytes")
    # Process form data here
    return JSONResponse(content={"message":"File succesful process"})