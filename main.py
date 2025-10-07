from typing import Union, Annotated

from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from finops_analyzer.api.v1.pages import router as pages_v1_router
from finops_analyzer.api.deps import templates
from finops_analyzer import schemas

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pages_v1_router, tags=["pages"])
MAX_FILE_SIZE = 100 * 1024 * 1024  # 50 MB

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
        file_upload: Annotated[UploadFile, File()],
        provider_detection: Annotated[str, Form()],
        provider: Annotated[str, Form()]
    ):
    file_size = 0
    chunk_size = 1024 * 1024  # 1 MB chunks
    
    chunks = []
    while chunk := await file_upload.read(chunk_size):
        file_size += len(chunk)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Archivo demasiado grande. Máximo: {MAX_FILE_SIZE / (1024*1024)} MB"
            )
        chunks.append(chunk)
 
    # Reconstruir el contenido completo
    contents = b''.join(chunks)
    file_obj = schemas.ProcessFileRequest(
        file_content=contents,
        provider_detection=provider_detection
        )
    
    return {
        "filename": file_upload.filename,
        "size_mb": file_size / (1024 * 1024),
        "parametro": provider
    }