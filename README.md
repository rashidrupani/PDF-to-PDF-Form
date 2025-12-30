# Simple AI Document Processor

A simplified, database-free version of the AI Document Processor that can be easily deployed on web hosting services. Perfect for single-user applications or integration into existing systems.

## Features

- **Multi-Engine OCR**: Tesseract, EasyOCR, and PaddleOCR with ensemble methods
- **Form Field Detection**: Automatic detection of text fields, checkboxes, radio buttons, signatures
- **Confidence Scoring**: Multi-dimensional confidence scoring
- **Export Options**: JSON, CSV, Excel exports
- **Template Learning**: Auto-detection and learning of form templates
- **Validation Engine**: Format validation and custom rules
- **Simple Web Interface**: Easy-to-use web interface with drag-and-drop functionality
- **No Database Required**: In-memory processing for simplicity
- **No User Authentication**: Direct access for single-user scenarios

## Live Demo

This application can be deployed to various platforms and accessed via a live URL. See [LIVE_DEPLOYMENT.md](LIVE_DEPLOYMENT.md) for instructions on how to deploy and get your own live URL.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   React/Vue     │  │   Document      │  │   Dashboard     │ │
│  │   Application   │  │   Viewer        │  │   Analytics     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Backend Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Document      │  │   OCR &         │  │   Validation    │ │
│  │   Processing    │  │   Extraction    │  │   Engine        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start with Docker

1. Clone this repository:
```bash
git clone <repository-url>
cd web-ai-document-processor-simple
```

2. Build and start the services:
```bash
docker-compose up --build
```

3. Access the application at: `http://localhost:3000`

## Manual Installation

### Backend Setup

1. Install system dependencies (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install -y tesseract-ocr libtesseract-dev libleptonica-dev pkg-config
```

2. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Start the backend:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

## API Endpoints

### Documents
- `POST /documents/upload` - Upload and process document
- `GET /documents/{job_id}` - Get document details
- `GET /documents/{job_id}/status` - Get processing status
- `GET /documents` - List all documents
- `POST /documents/{job_id}/export` - Export document in specified format

### Templates
- `POST /templates` - Create template
- `GET /templates` - List templates
- `GET /templates/{id}` - Get template
- `POST /templates/learn-from-document/{job_id}` - Learn template from document

## Usage Examples

### Upload and Process Document
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -H "accept: application/json" \
     -F "file=@document.pdf"
```

### Get Processing Status
```bash
curl -X GET "http://localhost:8000/documents/JOB_ID/status"
```

### Export Document
```bash
curl -X POST "http://localhost:8000/documents/JOB_ID/export?format_type=xlsx" \
     -H "accept: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
     --output exported_document.xlsx
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

## Deployment

This application is designed for easy deployment on various platforms:

1. **Render.com**: One-click deployment with Docker support
2. **Heroku**: Container-based deployment
3. **Railway.app**: Modern deployment platform
4. **VPS**: Self-hosted on any Linux server
5. **Google Cloud Run**: Serverless container platform

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## File Structure

```
web-ai-document-processor-simple/
├── frontend/                 # React frontend
│   ├── pages/               # Next.js pages
│   ├── components/          # React components
│   ├── hooks/              # Custom hooks
│   ├── services/           # API services
│   ├── types/              # TypeScript types
│   └── public/             # Static assets
├── backend/                 # FastAPI backend
│   ├── api/                # API routes
│   ├── services/           # Business logic
│   ├── core/               # Core utilities
│   └── static/             # Static files
├── uploads/                 # Uploaded documents
├── processed/               # Processed documents
├── exports/                 # Exported files
├── docker-compose.yml      # Multi-container setup
├── README.md               # This file
├── DEPLOYMENT.md           # Deployment guide
└── LIVE_DEPLOYMENT.md      # Live URL deployment guide
```

## Performance Considerations

- OCR processing is memory-intensive and may take 1-5 minutes per document
- Recommended: 4GB+ RAM for optimal performance
- Processing speed depends on document complexity and system resources
- Each processing job stores data in memory until completion

## Limitations

- No persistent storage (data is in-memory only)
- No user authentication/authorization
- No database for storing results permanently
- Processing jobs are stored in memory only
- Not suitable for multi-user scenarios without additional setup

## Security Considerations

- File upload validation is implemented
- Maximum file size is enforced
- No user authentication means open access
- For production use, implement additional security measures

## Support

For deployment and live URL instructions, see:
- [LIVE_DEPLOYMENT.md](LIVE_DEPLOYMENT.md) - How to get a live URL
- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide

## License

[Specify your license here]