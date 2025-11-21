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
    def delete_file(self, directory_path, file_name):
        """
        Delete a specific file in the specified directory.
        
        Args:
            directory_path (str): Path to the directory containing the file
            file_name (str): Name of the file to delete
            
        Returns:
            dict: Result message with status
        """
        # Validate inputs
        if not file_name:
            logger.debug("Error: file_name is required.")
            return {"message": "failed", "error": "file_name is required"}
        
        # Check if directory exists
        if not os.path.exists(directory_path):
            logger.debug(f"Error: Directory '{directory_path}' does not exist.")
            return {"message": "failed", "error": "directory not found"}
        
        if not os.path.isdir(directory_path):
            logger.debug(f"Error: '{directory_path}' is not a directory.")
            return {"message": "failed", "error": "not a directory"}
        
        # Build full file path
        file_path = os.path.join(directory_path, file_name)
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.debug(f"Error: File '{file_name}' not found in '{directory_path}'.")
            return {"message": "failed", "error": "file not found"}
        
        # Check if it's actually a file (not a directory)
        if not os.path.isfile(file_path):
            logger.debug(f"Error: '{file_name}' is not a file.")
            return {"message": "failed", "error": "not a file"}
        
        # Delete the file
        try:
            os.remove(file_path)
            logger.debug(f"Deleted: {file_name}")
            return {"message": "success", "file": file_name}
        except Exception as e:
            logger.debug(f"Error deleting {file_name}: {e}")
            return {"message": "failed", "error": str(e)}

class FocusConverterService:
    def __init__(self, container_name: str):
        """
        focus-converter convert-auto \
        --data-path /app/workspace/file.csv \
        --export-format csv \
        --export-path /app/output/ \
        --basename-template "converted_data_{i}"
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
        file_type = self.get_file_type(file_name=file_obj.file_name)
        if file_obj.provider_detection == "manual":
            self.command.extend([
                "convert",
                "--provider",
                file_obj.provider,
                "--data-path",
                "/app/workspace/"+file_obj.file_name,
                "--export-format",
                file_type,
                "--export-path",
                "/app/output/",
                "--basename-template",
                file_obj.output_filename
            ])
        else:
            self.command.extend([
                "convert-auto",
                "--data-path",
                "/app/workspace/"+file_obj.file_name,
                "--export-format",
                file_type,
                "--export-path",
                "/app/output/",
                "--basename-template",
                file_obj.output_filename
            ])
        logger.debug("Begging convert process")
        result = subprocess.run(self.command, capture_output=True)
        
        if result.returncode == 0:
            return {"status":True,"file_type":file_type}
        else:
            logger.debug(f"Convertion failed - Command: {self.command} \n\n Result: {result.stderr.decode()}")
            return {"status":False,"error":result.stderr.decode()}
    
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
