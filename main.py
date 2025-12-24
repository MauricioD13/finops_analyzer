import tempfile
from typing import Union, Annotated
from fastapi import FastAPI, UploadFile, File, Request, Form, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
import os
import subprocess
import shutil
from pathlib import Path
# Local imports
from api.v1.pages import router as pages_v1_router
from api.deps import templates
import schemas
from api.deps import get_focus_converter_service, get_file_deleter_service
from converter_services.service import FocusConverterService, FileDeleterService
from config import UPLOAD_DIR, DOWNLOAD_DIR, BASE_OUTPUT_NAME, MAX_FILE_SIZE
from logger import get_logger
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_URL"),
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)
logger = get_logger()
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pages_v1_router, tags=["pages"])

@app.get("/")
def read_root():
    return RedirectResponse(url="/pages/")

@app.get("/debug/user")
def debug_user():
    return {
        "process_user": os.getenv("USER"),
        "process_uid": os.getuid(),
        "process_gid": os.getgid(),
        "groups": subprocess.run(['groups'], capture_output=True, text=True).stdout
    }

@app.post("/converter")
async def converter_post(
        request: Request,
        file_upload: Annotated[UploadFile, File()],
        provider_detection: Annotated[str, Form()],
        provider: Annotated[str, Form()],
        focus_converter_service: Annotated[FocusConverterService, Depends(get_focus_converter_service)],
        deleter_service: Annotated[FileDeleterService, Depends(get_file_deleter_service)]
    ):
    
    
    file_size = 0
    chunk_size = 1024 * 1024  # 1 MB chunks
    
    chunks = []
    logger.debug("Start receiving file")
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
    if file_upload.file.name is None:
        logger.debug("Content is in memory, don't has a file")
        # Create a named temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=True,suffix=Path(file_upload.filename).suffix, dir=UPLOAD_DIR) as input_temp_file:
            input_temp_file.write(contents)
            input_temp_file.flush()
            # Process the file here
            input_temp_file.seek(0)  # Reset file pointer to beginning
            logger.debug("File created with the content")
            output_filename = BASE_OUTPUT_NAME+str(hash(Path(input_temp_file.name).name))
            file_obj = schemas.ProcessFileRequest(
                file_content=contents,
                provider_detection=provider_detection,
                file_path=input_temp_file.name,
                file_name=Path(input_temp_file.name).name,
                output_filename=output_filename
            )
            try:
                logger.debug("Start convertion")
                result = focus_converter_service.convert_file(file_obj)
                logger.debug("Finish convertion")
            except Exception as e:
                if file_obj:   
                    print(f"Error: {e}, File att: {file_obj.model_dump()}")
                exit(1)
            
    else:
        output_filename = BASE_OUTPUT_NAME+str(hash(file_upload.filename))
        logger.debug(f"File has a path in disk: {file_upload.file.name}, {file_upload.filename}")
        file_location = f"{UPLOAD_DIR}/{file_upload.filename}"

    # Save uploaded file locally - use the contents we already read
        with open(file_location, "wb") as buffer:
            buffer.write(contents)

        file_obj = schemas.ProcessFileRequest(
                file_content=contents,
                provider_detection=provider_detection,
                file_path=file_location,
                file_name=file_upload.filename,
                output_filename=output_filename
            )
        result = focus_converter_service.convert_file(file_obj)
        deleter_service.delete_file(directory_path=str(UPLOAD_DIR), file_name=file_upload.filename)
    # Store filename for potential middleware cleanup
    download_file = output_filename + "." + result.get("file_type", "csv")
    request.state.full_file_name = download_file

    # Return HTML template instead of JSON for HTMX
    if result.get("status", False):
        return templates.TemplateResponse("partials/download_button.html", {
            "request": request,
            "filename": file_upload.filename,
            "size_mb": file_size / (1024 * 1024),
            "download_file": download_file
        })
    else:
        return templates.TemplateResponse("partials/conversion_error.html", {
            "request": request,
            "filename": file_upload.filename,
            "error": result.get("error", "Unknown error occurred")
        })
        
@app.get("/download/{file_name}")
def download_file(file_name: str, background_tasks: BackgroundTasks, file_deleter_service: Annotated[FileDeleterService, Depends(get_file_deleter_service)]):
    file_path = f"{DOWNLOAD_DIR}/{file_name}"
    if os.path.exists(file_path):
        background_tasks.add_task(
            file_deleter_service.delete_file,
            directory_path=str(DOWNLOAD_DIR),
            file_name=file_name
        )
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type='application/octet-stream'
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)