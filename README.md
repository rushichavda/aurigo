# Aurigo - EB-1A Attorney Letter Generation System

Fully automated AI-powered system for generating professional EB-1A (Extraordinary Ability) visa petition attorney letters from client evidence folders.

## Overview

Aurigo processes client-provided evidence folders containing diverse document formats (PDFs, images, certificates, scanned documents) and automatically generates professional attorney support letters with auto-numbered exhibits following the official EB-1A format.

### Key Features

- **Multi-format Document Processing**: Handles PDFs, DOCX, images, PPTX, HTML, and scanned documents with OCR
- **Intelligent Criteria Mapping**: Automatically maps client folder names to official EB-1A criteria using pattern matching and LLM analysis
- **Structured Information Extraction**: Extracts key facts, entities, and summaries from all evidence documents
- **Auto-Exhibit Management**: Systematic exhibit numbering (A-1, A-2... B-1, B-2...) with descriptive titles
- **Professional Letter Generation**: Creates attorney letters following legal formatting standards
- **DOCX Export**: Generates formatted attorney letter and exhibit index documents
- **Background Processing**: Async case processing with real-time progress tracking

## Technology Stack

- **Backend**: Python 3.11+ + FastAPI
- **Frontend**: Next.js 14 + React + TypeScript
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **LLM**: Gemini 2.5 Flash (primary), Claude Sonnet 4 (optional polish)
- **Document Parser**: Docling (97.9% accuracy with OCR)
- **UI**: Tailwind CSS

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Node.js 18+ and npm (for frontend)
- Tesseract OCR (for document parsing with OCR)
- Gemini API key (required) - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Claude API key (optional) - Get from [Anthropic Console](https://console.anthropic.com/)

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment variables
cp .env.example .env
# Edit .env and add your API keys:
#   GEMINI_API_KEY=your-gemini-api-key-here
#   CLAUDE_API_KEY=your-claude-api-key-here-optional
#   USE_CLAUDE_POLISH=false

# 6. Run database migrations (creates tables)
python -c "from app.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)"

# 7. Start the backend server
python run.py
```

Backend will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local and ensure NEXT_PUBLIC_API_URL points to your backend

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

**Features:**
- Modern responsive UI with dark/light theme toggle
- Case upload with drag-and-drop support
- Real-time processing progress tracking
- Letter preview with exhibit index
- Complete case management dashboard

## System Workflow

1. **Upload**: Client uploads a ZIP file containing case folder with `Case_Overview.docx` and `Evidence/` subfolder
2. **Validation**: System validates folder structure and checks for required documents
3. **Criteria Mapping**: Automatically maps evidence folder names to EB-1A criteria
4. **Document Parsing**: Extracts text, tables, and metadata from all documents using Docling
5. **Information Extraction**: Uses Gemini 2.5 Flash to extract structured information (key facts, entities, summaries)
6. **Exhibit Management**: Assigns exhibit IDs (A-1, A-2... B-1, B-2...) systematically
7. **Letter Generation**: Generates professional attorney letter following legal template
8. **Export**: Creates formatted DOCX files for attorney letter and exhibit index

## Backend Features - Completed ✅

### Core Services
- [x] **Document Parser** (`document_parser.py`) - Docling-based multi-format parsing with OCR
- [x] **Folder Validator** (`folder_validator.py`) - Validates case folder structure
- [x] **Criteria Mapper** (`criteria_mapper.py`) - Maps folder names to EB-1A criteria
- [x] **Information Extractor** (`information_extractor.py`) - Extracts structured data using Gemini
- [x] **Exhibit Manager** (`exhibit_manager.py`) - Auto-assigns exhibit IDs and tracks mappings
- [x] **Letter Generator** (`letter_generator.py`) - Generates complete attorney letters
- [x] **Document Exporter** (`document_exporter.py`) - Creates formatted DOCX files
- [x] **Case Orchestrator** (`case_orchestrator.py`) - Coordinates complete workflow

### LLM Integration
- [x] **Gemini 2.5 Flash** (`gemini.py`) - Primary LLM for document analysis and generation
- [x] **Claude Sonnet 4** (`claude.py`) - Optional letter polishing for legal tone
- [x] **LLM Factory** (`factory.py`) - Flexible provider switching

### API & Database
- [x] **User Authentication** - JWT-based auth with signup/login
- [x] **Database Models** - Case, Document, CaseExhibit, GeneratedLetter models
- [x] **REST API Endpoints** - Upload, process, status, preview, download, list, delete
- [x] **Background Processing** - Async case processing with progress tracking

### API Endpoints
- `POST /api/cases/upload` - Upload case folder (ZIP)
- `POST /api/cases/{id}/process` - Start background processing
- `GET /api/cases/{id}/status` - Get processing status
- `GET /api/cases/{id}/preview` - Preview generated letter
- `GET /api/cases/{id}/download` - Get download links for DOCX files
- `GET /api/cases` - List all cases
- `DELETE /api/cases/{id}` - Delete case

### Frontend - Completed ✅
- [x] **Authentication Pages** - Login and registration with JWT auth
- [x] **Dashboard** - Overview with case statistics and recent activity
- [x] **Case Upload** - Drag-and-drop ZIP upload with validation
- [x] **Case List** - View all cases with status indicators
- [x] **Case Detail** - Real-time processing progress with live updates
- [x] **Letter Preview** - View generated letter with exhibit index
- [x] **Dark/Light Theme** - Seamless theme switching with persistence
- [x] **Responsive Design** - Optimized for desktop, tablet, and mobile

## Project Structure

```
aurigo/
├── backend/
│   ├── app/
│   │   ├── llm/                    # LLM integrations
│   │   │   ├── gemini.py          # Gemini 2.5 Flash
│   │   │   ├── claude.py          # Claude Sonnet 4
│   │   │   └── factory.py         # LLM factory
│   │   ├── services/              # Core business logic
│   │   │   ├── document_parser.py      # Docling parser
│   │   │   ├── folder_validator.py     # Folder validation
│   │   │   ├── criteria_mapper.py      # Criteria mapping
│   │   │   ├── information_extractor.py # Info extraction
│   │   │   ├── exhibit_manager.py      # Exhibit management
│   │   │   ├── letter_generator.py     # Letter generation
│   │   │   ├── document_exporter.py    # DOCX export
│   │   │   └── case_orchestrator.py    # Workflow orchestration
│   │   ├── routers/               # API endpoints
│   │   │   ├── auth.py           # Authentication
│   │   │   ├── llm.py            # LLM endpoints
│   │   │   └── cases.py          # Case management
│   │   ├── models.py             # Database models
│   │   ├── database.py           # Database connection
│   │   ├── auth.py               # Authentication logic
│   │   ├── config.py             # Configuration
│   │   └── main.py               # FastAPI app
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example             # Environment template
│   └── run.py                    # Server runner
├── frontend/                     # Next.js frontend (planned)
├── Pranav_Case_Data/            # Sample case data
├── docs/                        # Sample documents
└── README.md                    # This file
```

## Architecture Highlights

### Service-Oriented Design
All core functionality is organized into modular services that can be tested and modified independently:

```python
# Example: Processing a case
orchestrator = CaseOrchestrator(db)
result = await orchestrator.process_case(
    case_id=case_id,
    folder_path=folder_path,
    beneficiary_name=beneficiary_name
)
```

### Flexible LLM Integration
Easy to swap between Gemini and Claude:

```python
# Gemini for analysis
gemini = GeminiLLM()
extracted = await gemini.analyze_document(document_text, criterion)

# Claude for polishing (optional)
claude = ClaudeLLM()
polished = await claude.polish_letter(draft_letter)
```

### Background Task Processing
Long-running case processing happens in the background with real-time progress updates:

```python
# Start processing
background_tasks.add_task(orchestrator.process_case, ...)

# Check status anytime
GET /api/cases/{id}/status
# Returns: {"status": "processing", "progress": 45, "current_step": "extracting_information"}
```

### Database Schema
Comprehensive tracking of cases, documents, exhibits, and generated letters:

- **Case**: Main entity with status, progress, criteria matched, output paths
- **Document**: Individual files with parsed text, extracted info, exhibit assignment
- **CaseExhibit**: Exhibit assignments with group-based numbering
- **GeneratedLetter**: Version tracking for attorney letters

## Expected Folder Structure

Your case folder should follow this structure:

```
Client_Case_Folder/
├── Case_Overview.docx          # Beneficiary background and overview
└── Evidence/
    ├── 1. Awards and Prizes/   # Evidence folder for criterion 1
    │   ├── certificate1.pdf
    │   └── award_letter.jpg
    ├── 2. Membership/          # Evidence folder for criterion 2
    │   └── membership_card.pdf
    ├── 3. Critical Role/       # Evidence folder for criterion 8
    │   ├── job_offer.docx
    │   └── org_chart.png
    └── ...
```

**Supported Document Formats**: PDF, DOCX, JPG, PNG, TIFF, PPTX, HTML, MD

## EB-1A Criteria Reference

The system automatically maps evidence to these 10 official EB-1A criteria:

1. **Awards / Prizes** - Recognition for excellence
2. **Membership** - Elite associations requiring outstanding achievements
3. **Published Material** - Media coverage about the applicant
4. **Judging** - Judging work of others in the field
5. **Original Contributions** - Major significance to the field
6. **Authorship** - Published scholarly articles
7. **Exhibitions** - Artistic displays
8. **Leading or Critical Role** - Critical positions in distinguished organizations
9. **High Salary** - High remuneration compared to others
10. **Performing Arts Success** - Commercial success in performing arts

**Note**: EB-1A visa requires meeting at least 3 out of 10 criteria.

## Testing with Sample Data

You can test the system using the provided Pranav case data:

```bash
# 1. Start the backend server
cd backend
python run.py

# 2. Create a test user via API
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"test","password":"test123","full_name":"Test User"}'

# 3. Login and get token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# 4. ZIP the Pranav_Case_Data folder
# 5. Upload via API (see API docs at http://localhost:8000/docs)
```

## API Documentation

Full interactive API documentation is available at `http://localhost:8000/docs` when the backend is running.

### Key Endpoints

**Authentication**
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token

**Case Management**
- `POST /api/cases/upload` - Upload case folder (ZIP)
- `POST /api/cases/{id}/process` - Start processing
- `GET /api/cases/{id}/status` - Check progress
- `GET /api/cases/{id}/preview` - Preview letter
- `GET /api/cases/{id}/download` - Download files

## Configuration

Configure the system via `.env` file:

```env
# Database
DATABASE_URL=sqlite:///./aurigo.db

# LLM Provider
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash-exp

# Optional Claude Polishing
CLAUDE_API_KEY=your-claude-api-key
CLAUDE_MODEL=claude-sonnet-4-20250514
USE_CLAUDE_POLISH=false

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## Development

```bash
# Backend (with hot reload)
cd backend
python run.py

# Run specific service tests
python -m pytest tests/

# Frontend (with hot reload) - Coming Soon
cd frontend
npm run dev
```

## Cost Estimation

Processing a typical case with 143 documents (~500KB total):

- **Gemini 2.5 Flash**: ~$0.40 per case
- **Claude Sonnet 4** (if enabled): ~$3-5 per case for polishing

Total cost per case: **$0.40 - $5.40** depending on configuration

## Roadmap

### Phase 1: Backend MVP ✅ (Completed)
- [x] Document parsing and extraction
- [x] Criteria mapping
- [x] Exhibit management
- [x] Letter generation
- [x] REST API

### Phase 2: Frontend ✅ (Completed)
- [x] Case upload interface
- [x] Processing dashboard
- [x] Letter preview
- [x] Export functionality
- [x] Dark/light theme support
- [x] Responsive design

### Phase 3: Enhancements
- [ ] Manual exhibit reordering
- [ ] Letter section editing
- [ ] Template customization
- [ ] Multiple letter versions
- [ ] Physical exhibit assembly guidance

## Troubleshooting

### Common Issues

**Issue**: `ImportError: cannot import name 'Document' from 'docling'`
**Solution**: Install Docling: `pip install docling==2.9.1`

**Issue**: Tesseract not found for OCR
**Solution**: Install Tesseract OCR:
- Windows: Download from [GitHub releases](https://github.com/tesseract-ocr/tesseract/releases)
- macOS: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

**Issue**: API returns 401 Unauthorized
**Solution**: Ensure you're passing the JWT token in Authorization header: `Authorization: Bearer <token>`

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests, please open an issue on GitHub.
