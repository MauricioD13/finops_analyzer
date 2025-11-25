from fastapi import Request
from api.deps import get_file_deleter_service
from logger import logger

async def file_deletion_middleware(request: Request, call_next):
    """
    Middleware to delete files from output directory after each request.
    This ensures temporary converted files are cleaned up.
    """
    response = await call_next(request)
    
    # Only run cleanup after converter endpoint
    if request.url.path == "/converter" and request.method == "POST":
        try:
            file_name = getattr(request.state, "full_file_name", None)
            file_deleter_service = get_file_deleter_service()
            res_deletion = file_deleter_service.delete_file(directory_path="./deploy/dev/output/", file_name=file_name)
            logger.debug(
                f"Finish deleting files: Message - {res_deletion.get('message', None)}" +
                f"Deleted files - {res_deletion.get('deleted_count')}"
            )
        except Exception as e:
            logger.error(f"Error during file cleanup: {e}")
    
    return response
