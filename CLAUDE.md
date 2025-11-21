# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FinOps Analyzer is a FastAPI web application that converts cloud billing data from major cloud providers (AWS, Azure, GCP, Oracle) into the FOCUS (FinOps Open Cost and Usage Specification) framework. The application uses a dockerized `focus-converter` service to perform the conversion and provides a web interface for file uploads and conversions.

## Development Commands

### Running the Application

```bash
# Run the FastAPI application (development)
fastapi dev main.py

# Run with Uvicorn directly
uvicorn main:app --reload

# Start the focus-converter Docker container
cd deploy/dev
docker compose -f docker-compose.focus-converter.yaml up -d

# Stop the focus-converter container
docker compose -f docker-compose.focus-converter.yaml down
```

### Dependencies

```bash
# Install dependencies using poetry
poetry install

# Add a new dependency
poetry add <package-name>
```

## Architecture

### Application Structure

The application follows a layered architecture with clear separation of concerns:

- **main.py**: FastAPI application entry point, registers routes and middleware
- **api/**: API layer containing route handlers
  - **api/v1/pages.py**: Page route handlers (main page, converter page)
  - **api/deps.py**: Dependency injection for services and templates
- **focus_converter/**: Service layer for business logic
  - **service.py**: Contains `FocusConverterService` (handles docker exec calls to focus-converter) and `FileDeleterService` (cleans up temporary files)
- **middleware/**: HTTP middleware components
  - **delete_files.py**: Automatically deletes converted files after response
- **schemas.py**: Pydantic models for request/response validation
- **templates/**: Jinja2 HTML templates
- **static/**: CSS and JavaScript assets

### Key Design Patterns

**Docker-based Conversion Service**: The application doesn't perform conversions directly. Instead, it uses `docker exec` to run commands in a separate `focus-converter` container. This provides isolation and allows the converter to be updated independently.

**File Lifecycle Management**:
1. User uploads a file via POST to `/converter`
2. File is temporarily stored in `./deploy/dev/input/`
3. `FocusConverterService` executes docker command to convert file
4. Converted output is written to `./deploy/dev/output/`
5. `file_deletion_middleware` automatically cleans up output files after response is sent
6. Input files are auto-deleted by using Python's `tempfile.NamedTemporaryFile` with `delete=True`

**Service Injection**: Services are provided via FastAPI's dependency injection system (see `api/deps.py`). This makes services easily mockable for testing.

### Docker Volume Mapping

The focus-converter container has these volume mappings:
- Host `./deploy/dev/input/` → Container `/app/workspace/`
- Host `./deploy/dev/output/` → Container `/app/output/`

When calling the converter service, file paths must be translated from host paths to container paths (e.g., `./deploy/dev/input/file.csv` → `/app/workspace/file.csv`).

### Provider Detection

The converter supports two modes:
- **Automatic**: `convert-auto` command detects provider automatically
- **Manual**: `convert` command with explicit `--provider` flag (aws, azure, gcp, oracle)

### Focus Converter Commands

The focus-converter CLI tool (running inside the container) supports:

```bash
# Automatic provider detection
focus-converter convert-auto --data-path /app/workspace/file.csv --export-format csv --export-path /app/output/

# Manual provider specification
focus-converter convert --provider aws --data-path /app/workspace/file.csv --export-format parquet --export-path /app/output/

# Dataset conversion (for multi-file parquet datasets)
focus-converter convert --provider aws --data-path /path/to/dataset/ --data-format parquet --parquet-data-format dataset --export-path /output/
```

## Important Implementation Details

- **File size limit**: Maximum upload size is 100MB (defined in `main.py:29`)
- **Chunked uploads**: Files are read in 1MB chunks to handle large files efficiently
- **Temp file handling**: Input files use `tempfile.NamedTemporaryFile` with `delete=True` and are stored in `./deploy/dev/input/`
- **Middleware cleanup**: The `file_deletion_middleware` only runs after POST requests to `/converter` endpoint
- **Logging**: Custom logger configured in `logger.py` with output to both console and `logs/app.log`
- **Container dependency**: The FastAPI app requires the `focus-converter` container to be running
