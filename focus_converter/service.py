import subprocess
import os
import shutil
from pathlib import Path
#from watchdog.observers import Observer
#from watchdog.events import FileSystemEventHandler
import time

# Local Imports
from finops_analyzer import schemas
from finops_analyzer.logger import logger

class FileDeleterService:
    def __init__(self):
        pass

    def delete_all_files(self, directory_path):
        """
        Delete all files in the specified directory.
        Subdirectories are not deleted, only files.
        
        Args:
            directory_path (str): Path to the directory to clean
        """
        # Check if directory exists
        if not os.path.exists(directory_path):
            logger.debug(f"Error: Directory '{directory_path}' does not exist.")
            return {"message":"Failed"}
        
        if not os.path.isdir(directory_path):
            logger.debug(f"Error: '{directory_path}' is not a directory.")
            return {"message":"Failed"}
        
        # Count files for feedback
        deleted_count = 0
        error_count = 0
        
        # Iterate through all items in the directory
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            
            # Only delete files, not directories
            if os.path.isfile(item_path):
                try:
                    os.remove(item_path)
                    logger.debug(f"Deleted: {item}")
                    deleted_count += 1
                except Exception as e:
                    logger.debug(f"Error deleting {item}: {e}")
                    error_count += 1
        
        return {
            "deleted_count": deleted_count,
            "error_count": error_count,
            "message":"success"
        }

class FocusConverterService:
    def __init__(self, container_name: str):
        """
        AUTO
        docker exec focus-converter focus-converter convert-auto 
        --data-path /app/workspace/truncated_data_cur.csv 
        --export-format csv --export-path /app/output/
        """
        self.base_command = ["docker","exec",container_name,"focus-converter"]

    def convert_file(self, file_obj: schemas.ProcessFileRequest) -> dict:
        self.command = self.base_command.copy()
        # Convert host path to container path
        #container_path = self._host_to_container_path(file_obj.file_path)
        
        if file_obj.provider_detection == "manual":
            self.command.extend([
                "convert",
                "--provider",
                file_obj.provider,
                "--data-path",
                "/app/workspace/"+file_obj.file_name,
                "--export-format",
                self.get_file_type(file_name=file_obj.file_name),
                "--export-path",
                "/app/output/"
            ])
        else:
            self.command.extend([
                "convert-auto",
                "--data-path",
                "/app/workspace/"+file_obj.file_name,
                "--export-format",
                self.get_file_type(file_name=file_obj.file_name),
                "--export-path",
                "/app/output/"
            ])
        logger.debug("Begging convert process")
        result = subprocess.run(self.command, capture_output=True)
        
        if result.returncode == 0:
            return True
        else:
            logger.debug(f"Convertion failed - Command: {self.command} \n\n Result: {result.stderr.decode()}")
            return False
    
    @staticmethod
    def _host_to_container_path(host_path: str) -> str:
        """
        Convert host path to container path.
        Host: ./deploy/dev/input/tmpXXX.csv -> Container: /app/workspace/tmpXXX.csv
        """
        file_name = Path(host_path).name
        return f"/app/workspace/{file_name}"
    
    @staticmethod
    def get_file_type(file_name: str):
        return Path(file_name).suffix.replace(".","")
