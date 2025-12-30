# Deployment Guide for Simple AI Document Processor

This guide provides instructions for deploying the Simple AI Document Processor on various web hosting platforms.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Deployment on Popular Platforms](#deployment-on-popular-platforms)
4. [Manual Deployment](#manual-deployment)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

- At least 4GB RAM (8GB+ recommended for OCR processing)
- Docker and Docker Compose (for containerized deployment)
- Git (for cloning the repository)

## Docker Deployment (Recommended)

### Local Deployment

1. Clone the repository:
```bash
git clone <repository-url>
cd web-ai-document-processor-simple
```

2. Build and run the application:
```bash
docker-compose up --build
```

3. Access the application:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000`

### Production Deployment with Docker

For production deployment, create a production-ready docker-compose file:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://your-domain.com:8000
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DEBUG=False
      - MAX_FILE_SIZE=52428800  # 50MB
    volumes:
      - ./uploads:/app/uploads
      - ./processed:/app/processed
      - ./exports:/app/exports
    restart: unless-stopped
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Deployment on Popular Platforms

### Heroku

1. Create a `Procfile` in the root directory:
```
web: cd backend && uvicorn main:app --host=0.0.0.0 --port=${PORT:-8000}
```

2. Create a `heroku.yml` file:
```yaml
build:
  docker:
    web: backend/Dockerfile
run:
  web: cd backend && uvicorn main:app --host=0.0.0.0 --port=${PORT:-8000}
```

3. Deploy using Heroku CLI:
```bash
heroku create your-app-name
heroku stack:set container
git push heroku main
```

### DigitalOcean App Platform

1. Create a `Dockerfile.web` for the backend:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev pkg-config

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY backend/ .

# Create directories
RUN mkdir -p uploads processed exports

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Create a `docker-compose.yml` for DigitalOcean:
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - MAX_FILE_SIZE=52428800
    volumes:
      - uploads:/app/uploads
      - processed:/app/processed
      - exports:/app/exports

volumes:
  uploads:
  processed:
  exports:
```

### AWS Elastic Beanstalk

1. Create a `Dockerrun.aws.json` file:
```json
{
  "AWSEBDockerrunVersion": 2,
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-registry/ai-document-processor:latest",
      "memory": 2048,
      "cpu": 1024,
      "essential": true,
      "portMappings": [
        {
          "hostPort": 8000,
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "mountPoints": [
        {
          "sourceVolume": "uploads",
          "containerPath": "/app/uploads"
        },
        {
          "sourceVolume": "processed",
          "containerPath": "/app/processed"
        },
        {
          "sourceVolume": "exports",
          "containerPath": "/app/exports"
        }
      ]
    }
  ],
  "volumes": [
    {
      "name": "uploads",
      "host": {
        "sourcePath": "/var/app/uploads"
      }
    },
    {
      "name": "processed",
      "host": {
        "sourcePath": "/var/app/processed"
      }
    },
    {
      "name": "exports",
      "host": {
        "sourcePath": "/var/app/exports"
      }
    }
  ]
}
```

### Google Cloud Run

1. Create a `cloudbuild.yaml` file:
```yaml
steps:
  # Build the backend container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/backend', './backend']

  # Push the backend container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/backend']

  # Deploy backend to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'ai-document-processor'
      - '--image=gcr.io/$PROJECT_ID/backend'
      - '--region=us-central1'
      - '--platform=managed'
      - '--port=8000'
      - '--memory=4Gi'
      - '--cpu=2'
      - '--set-env-vars=ENVIRONMENT=production'
      - '--allow-unauthenticated'
```

Deploy with:
```bash
gcloud builds submit
```

### VPS/Cloud Server Deployment

1. SSH into your server:
```bash
ssh user@your-server-ip
```

2. Install Docker and Docker Compose:
```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

3. Clone and deploy:
```bash
git clone <repository-url>
cd web-ai-document-processor-simple
docker-compose up -d
```

4. Set up a reverse proxy with Nginx:
```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/default
```

Add the following configuration:
```
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site and restart Nginx:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

## Configuration

### Environment Variables

The application supports the following environment variables:

**Backend:**
- `ENVIRONMENT`: Set to "production" for production (default: "development")
- `DEBUG`: Enable/disable debug mode (default: "True")
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 52428800 for 50MB)
- `ALLOWED_FILE_TYPES`: Comma-separated list of allowed file types (default: "pdf,jpg,jpeg,png,tiff")
- `PROCESSING_TIMEOUT`: Processing timeout in seconds (default: 300)
- `UPLOAD_FOLDER`: Directory for uploads (default: "./uploads")
- `PROCESSED_FOLDER`: Directory for processed files (default: "./processed")
- `EXPORT_FOLDER`: Directory for exports (default: "./exports")

### SSL/HTTPS Setup

For production, set up SSL certificates using Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Performance Optimization

### Memory and CPU Requirements

- **Minimum**: 2GB RAM, 1 CPU core
- **Recommended**: 4GB+ RAM, 2+ CPU cores
- **For heavy usage**: 8GB+ RAM, 4+ CPU cores

### OCR Performance Tips

1. Increase available memory for OCR processing
2. Use a server with good CPU performance
3. Monitor resource usage during processing
4. Consider processing queue management for high volume

## Troubleshooting

### Common Issues

**Docker Build Issues:**
- Ensure system has enough memory during build
- Check that all dependencies are available

**OCR Processing Issues:**
- Verify Tesseract is installed correctly
- Check that image files are properly formatted
- Monitor memory usage during processing

**File Upload Issues:**
- Verify upload directory permissions
- Check file size limits
- Ensure sufficient disk space

**API Connection Issues:**
- Verify CORS settings
- Check port bindings
- Ensure frontend can reach backend API

### Logs and Monitoring

Check application logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Health Checks

The application provides a health check endpoint:
```
GET /health
```

### Scaling

For high-traffic applications, consider:
- Running multiple backend instances behind a load balancer
- Using a message queue for document processing
- Implementing caching for processed documents
- Using CDN for static assets

## Security Considerations

1. **File Upload Security:**
   - Validate file types and sizes
   - Sanitize file names
   - Scan for malicious content

2. **API Security:**
   - Use HTTPS in production
   - Implement rate limiting
   - Validate all inputs

3. **Server Security:**
   - Keep system updated
   - Use firewall rules
   - Regular security audits

## Maintenance

### Backup Strategy

Regularly backup:
- Uploaded documents
- Processed results
- Exported files
- Application configuration

### Updates

To update the application:
```bash
git pull origin main
docker-compose down
docker-compose up --build
```

## Support

For issues or questions, check the logs first:
```bash
docker-compose logs
```

If you continue to have problems, consider:
- Checking system resources (memory, disk space)
- Verifying file permissions
- Ensuring all dependencies are properly installed