import subprocess
import os
from finops_analyzer import schemas
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class OutputHandler(FileSystemEventHandler):
        
    def on_modified(self, event):
        if not event.is_directory:
            print(f"Modified: {event.src_path}")
    def on_created(self, event):
        print(f"Created: {event.src_path}")

    def on_deleted(self, event):
        print(f"Deleted: {event.src_path}")

# Replace with the path I want to monitor
path = "/path/to/watch"
handler = MyHandler()
observer = Observer()
observer.schedule(handler, path=path, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()





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
        container_path = self._host_to_container_path(file_obj.file_path)
        
        if file_obj.provider_detection == "manual":
            self.command.extend([
                "convert",
                "--provider",
                file_obj.provider,
                "--data-path",
                container_path,
                "--export-format",
                self.get_file_type(file_name=file_obj.file_name),
                "--export-path",
                "/app/output/"
            ])
        else:
            self.command.extend([
                "convert-auto",
                "--data-path",
                container_path,
                "--export-format",
                self.get_file_type(file_name=file_obj.file_name),
                "--export-path",
                "/app/output/"
            ])
        result = subprocess.run(self.command, capture_output=True)
        print(f"Result: {result}")
        if result.returncode == 0:
            return True
        else:
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
