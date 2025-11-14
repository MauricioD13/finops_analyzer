from fastapi import Request
from finops_analyzer.api.deps import get_file_deleter_service
from finops_analyzer.logger import logger

async def file_deletion_middleware(request: Request, call_next):
    """
    Middleware to delete files from output directory after each request.
    This ensures temporary converted files are cleaned up.
    """
    response = await call_next(request)
    
    # Only run cleanup after converter endpoint
    if request.url.path == "/converter" and request.method == "POST":
        try:
            file_deleter_service = get_file_deleter_service()
            res_deletion = file_deleter_service.delete_all_files("./deploy/dev/output/")
            logger.debug(
                f"Finish deleting files: Message - {res_deletion.get('message', None)} "
                f"Deleted files - {res_deletion.get('deleted_count')}"
            )
        except Exception as e:
            logger.error(f"Error during file cleanup: {e}")
    
    return response
