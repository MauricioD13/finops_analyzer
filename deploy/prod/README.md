# Production Deployment

This directory contains the production deployment configuration for FinOps Analyzer.

## Architecture

The application runs as a **single containerized service** with the `focus-converter` package installed directly inside the FastAPI container. This eliminates the need for separate containers and docker exec calls.

## Quick Start

### Build and Run

```bash
cd deploy/prod
docker compose up -d
```

### Stop

```bash
docker compose down
```

### View Logs

```bash
docker compose logs -f finops-analyzer
```

### Rebuild After Code Changes

```bash
docker compose up -d --build
```

## Configuration

### Environment Variables

You can customize the application by setting environment variables in the `docker-compose.yaml` file:

- `PYTHONUNBUFFERED=1` - Enable Python unbuffered output for better logging
- `LOG_LEVEL=INFO` - Set logging level (DEBUG, INFO, WARNING, ERROR)

### Volumes

The application uses three named volumes for persistence:

- `finops-input` - Temporary storage for uploaded files
- `finops-output` - Temporary storage for converted files
- `finops-logs` - Application logs

## Health Checks

The container includes a health check that verifies the service is responsive:
- Runs every 30 seconds
- 10-second timeout
- 3 retries before marking unhealthy
- 10-second startup grace period

Check health status:
```bash
docker compose ps
```

## Accessing the Application

Once running, access the application at:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Troubleshooting

### Container won't start

Check logs for errors:
```bash
docker compose logs finops-analyzer
```

### Permission issues with volumes

On Linux systems, you may need to adjust volume permissions:
```bash
docker compose exec finops-analyzer ls -la /app/deploy/dev/
```

### Focus-converter CLI issues

Verify focus-converter is installed:
```bash
docker compose exec finops-analyzer which focus-converter
docker compose exec finops-analyzer focus-converter --version
```

## Production Considerations

1. **Reverse Proxy**: Use nginx or Traefik in front of the application
2. **SSL/TLS**: Configure HTTPS certificates
3. **Resource Limits**: Add CPU/memory limits to docker-compose.yaml
4. **Monitoring**: Integrate with Prometheus/Grafana for metrics
5. **Log Aggregation**: Send logs to centralized logging system
6. **Backup**: Regular backups of volumes if needed

## Differences from Development

- Uses multi-stage build for smaller image size
- Production-grade ASGI server (uvicorn with 2 workers)
- Health checks enabled
- Named volumes for data persistence
- No hot-reload (restart required for code changes)
