import subprocess
from finops_analyzer import schemas
from pathlib import Path

class FocusConverterService:
    def __init__(self, container_name: str):
        """
        AUTO
        docker exec focus-converter focus-converter convert-auto 
        --data-path /app/workspace/truncated_data_cur.csv 
        --export-format csv --export-path /app/output/
        """
        base_command = ["docker","exec",container_name,"focus-converter"]

    def convert_file(self, file_obj: schemas.ProcessFileRequest) -> dict:
        self.command = base_command.copy()
        if file_obj.provider_detection == "manual":
            self.command.extend([
                "convert",
                "--provider",
                file_obj.provider,
                "--data-path",
                file_obj.file_path,
                "--export-format",
                self.get_file_type(file_name=file_obj.file_name),
                "--export-path",
                "/app/output/"
            ])
        else:
            self.command.extend([
                "convert-auto",
                "--data-path",
                file_obj.file_path,
                "--export-format",
                self.get_file_type(file_name=file_obj.file_name),
                "--export-path",
                "/app/output/"
            ])
        result = subprocess.run(command)
        if result.returncode == 0:
            return {"message":"Conversion success"}
        else:
            return {"message":"Conversion error"}

    @staticmethod
    def get_file_type(file_name: str):
        return Path(file_name).suffix.replace(".","")