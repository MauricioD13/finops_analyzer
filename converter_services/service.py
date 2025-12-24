import subprocess
import os
import shutil
from pathlib import Path
#from watchdog.observers import Observer
#from watchdog.events import FileSystemEventHandler
import time

# Local Imports
import schemas
from logger import logger

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
    def __init__(self, input_dir: str = "./deploy/dev/input", output_dir: str = "./deploy/dev/output"):
        """
        Service to call focus-converter CLI directly (no docker exec needed).

        Args:
            input_dir: Directory where input files are stored
            output_dir: Directory where converted files will be written
        """
        self.input_dir = input_dir
        self.output_dir = output_dir

        # Ensure directories exist
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def convert_file(self, file_obj: schemas.ProcessFileRequest) -> dict:
        """
        Convert cloud billing file to FOCUS format using focus-converter CLI.

        Args:
            file_obj: Request object containing file details and conversion parameters

        Returns:
            dict: Conversion result with status and file_type or error message
        """
        file_type = self.get_file_type(file_name=file_obj.file_name)

        # Build input and output paths
        input_path = os.path.join(self.input_dir, file_obj.file_name)
        print(f"Output dir: {self.output_dir}")
        output_path = str(self.output_dir) + "/"  # focus-converter expects trailing slash

        # Build the command
        command = ["focus-converter"]

        if file_obj.provider_detection == "manual":
            command.extend([
                "convert",
                "--provider",
                file_obj.provider,
                "--data-path",
                input_path,
                "--export-format",
                file_type,
                "--export-path",
                output_path,
                "--basename-template",
                file_obj.output_filename
            ])
        else:
            command.extend([
                "convert-auto",
                "--data-path",
                input_path,
                "--export-format",
                file_type,
                "--export-path",
                output_path,
                "--basename-template",
                file_obj.output_filename
            ])

        logger.debug(f"Beginning convert process with command: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.debug(f"Conversion successful for {file_obj.file_name}")
                return {"status": True, "file_type": file_type}
            else:
                logger.error(f"Conversion failed - Command: {' '.join(command)}\n\nError: {result.stderr}")
                return {"status": False, "error": result.stderr}

        except subprocess.TimeoutExpired:
            logger.error(f"Conversion timeout for {file_obj.file_name}")
            return {"status": False, "error": "Conversion process timed out after 5 minutes"}
        except Exception as e:
            logger.error(f"Unexpected error during conversion: {str(e)}")
            return {"status": False, "error": f"Internal error: {str(e)}"}
    
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
