from typing import Union, Annotated

from fastapi import FastAPI, UploadFile, File, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from finops_analyzer.api.v1.pages import router as pages_v1_router
from finops_analyzer.api.deps import templates
from finops_analyzer import schemas
from finops_analyzer.api.deps import get_focus_converter_service
from finops_analyzer.focus_converter.service import FocusConverterService

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pages_v1_router, tags=["pages"])
MAX_FILE_SIZE = 100 * 1024 * 1024  # 50 MB

@app.get("/")
def read_root():
    return RedirectResponse(url="/pages/")

@app.post("/converter")
async def converter_post(
        request: Request,
        file_upload: Annotated[UploadFile, File()],
        provider_detection: Annotated[str, Form()],
        provider: Annotated[str, Form()],
        focus_converter_service: Annotated[FocusConverterService, Depends(get_focus_converter_service)]
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
    print(f"Path: {file_upload.file.name}, Name: {file_upload.filename}")
    if file_upload.file.name is None:
        # PENDIENTE: Caso en donde el archivo es pequeño y no escribe en un archivo, sino que lo deja en memoria
        pass
    file_obj = schemas.ProcessFileRequest(
        file_content=contents,
        provider_detection=provider_detection,
        file_path=file_upload.file.name,
        file_name=file_upload.filename
        )
    result = focus_converter_service.convert_file(file_obj)
    if result:
        return {
            "filename": file_upload.filename,
            "size_mb": file_size / (1024 * 1024),
            "parametro": provider,
            "convertion": "successful"
        }
    else:
        return {
            "filename": file_upload.filename,
            "size_mb": file_size / (1024 * 1024),
            "parametro": provider,
            "convertion": "failed"
        }