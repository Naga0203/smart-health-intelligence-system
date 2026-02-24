# SymptomSense Health AI - Architecture Documentation

## Overview

This directory contains comprehensive architecture documentation for the SymptomSense Health AI system. The documentation is organized into multiple focused documents covering different aspects of the system architecture.

## Available Documents

### 1. System Architecture Overview
**File**: `01_System_Architecture_Overview.md`

**Contents**:
- High-level three-tier architecture
- Core modules and components
- Data flow architecture
- Security architecture
- Scalability considerations
- Deployment architecture
- Technology stack and rationale
- System metrics and monitoring
- Future enhancements

**Key Topics**:
- Presentation Layer (React Frontend)
- Application Layer (Django Backend + Multi-Agent System)
- Data & Services Layer (Firebase + Gemini AI)
- Security multi-layer model
- Performance optimization strategies

---

### 2. Multi-Agent System Architecture
**File**: `02_Multi_Agent_System_Architecture.md`

**Contents**:
- Agent architecture pattern and design philosophy
- Agent hierarchy and communication
- Detailed specifications for each agent
- Agent communication protocol
- Error handling strategies
- Performance optimization

**Agents Covered**:
1. **Orchestrator Agent**: Central coordinator
2. **Validation Agent**: Input validation using AI
3. **Predictor Agent**: ML-based disease prediction
4. **Explanation Agent**: AI-powered explanations
5. **Recommendation Agent**: Treatment recommendations
6. **Extraction Agent**: Medical report data extraction
7. **Severity Agent**: Severity and urgency assessment

**Key Algorithms**:
- Pipeline orchestration workflow
- Validation with Gemini AI
- ML prediction and confidence scoring
- AI explanation generation
- Multi-system treatment recommendation
- Medical report extraction with OCR
- Severity assessment with red flag detection

---

### 3. Machine Learning Architecture
**File**: `03_Machine_Learning_Architecture.md`

**Contents**:
- ML pipeline architecture
- Neural network architecture (PyTorch)
- Feature engineering (multi-hot encoding)
- Training process and optimization
- Inference process and algorithms
- Model evaluation metrics
- Model deployment and versioning
- Continuous learning and feedback loop

**Key Components**:
- Multi-label classification neural network
- 3-layer architecture (512-256-128 neurons)
- Dropout regularization (30%)
- Binary cross-entropy loss
- Adam optimizer
- Confidence scoring algorithm
- A/B testing strategy

**Performance Metrics**:
- Overall Accuracy: 87.3%
- Top-3 Accuracy: 94.1%
- Top-5 Accuracy: 97.2%
- Inference Time: ~50ms

---

### 4. Medical Report Upload Architecture
**File**: `04_Medical_Report_Upload_Architecture.md`

**Contents**:
- Feature architecture overview
- Frontend components (FileUploadComponent, AssessmentForm)
- Backend services (FileStorageService, ExtractionJobManager, EnhancedExtractionAgent)
- Data models and API endpoints
- Integration with assessment flow
- Error handling and recovery
- Performance considerations
- Security and privacy

**Key Features**:
- PDF and image upload support
- OCR for scanned documents
- AI-powered data extraction using Gemini
- Asynchronous processing with job tracking
- Auto-population of assessment forms
- Data source tracking (manual vs extracted)
- User edit priority

**API Endpoints**:
- `POST /api/reports/upload/` - Upload medical report
- `GET /api/reports/extract/{job_id}/` - Check extraction status
- `GET /api/reports/{report_id}/` - Get report metadata

---

## Document Format

All documents are written in **Markdown** format for easy reading, version control, and conversion to other formats.

## Converting to PDF

You can convert these Markdown documents to PDF using various methods:

### Method 1: Online Converters
- [Markdown to PDF](https://www.markdowntopdf.com/)
- [Dillinger](https://dillinger.io/) - Export as PDF
- [StackEdit](https://stackedit.io/) - Export as PDF

### Method 2: VS Code Extensions
1. Install "Markdown PDF" extension in VS Code
2. Open any `.md` file
3. Right-click → "Markdown PDF: Export (pdf)"

### Method 3: Command Line Tools

**Using Pandoc** (recommended):
```bash
# Install pandoc
# Windows: choco install pandoc
# Mac: brew install pandoc
# Linux: sudo apt-get install pandoc

# Convert to PDF
pandoc 01_System_Architecture_Overview.md -o 01_System_Architecture_Overview.pdf
```

**Using md-to-pdf** (Node.js):
```bash
npm install -g md-to-pdf
md-to-pdf 01_System_Architecture_Overview.md
```

**Using Python markdown-pdf**:
```bash
pip install markdown-pdf
md2pdf 01_System_Architecture_Overview.md
```

### Method 4: Print to PDF
1. Open the `.md` file in any Markdown viewer (VS Code, GitHub, etc.)
2. Use browser's "Print" function
3. Select "Save as PDF" as the printer

## Viewing Markdown Files

### Recommended Viewers:
- **VS Code**: Built-in Markdown preview (Ctrl+Shift+V)
- **GitHub**: Automatically renders Markdown files
- **Typora**: Dedicated Markdown editor with live preview
- **MarkText**: Free open-source Markdown editor
- **Obsidian**: Knowledge base with Markdown support

## Architecture Diagrams

All documents include ASCII-based architecture diagrams that render correctly in any text viewer. These diagrams show:
- System component relationships
- Data flow between modules
- Agent communication patterns
- ML pipeline architecture
- API request/response flows
- Security layers
- Deployment architecture

## Document Maintenance

**Version**: 1.0  
**Last Updated**: 2024  
**Maintained By**: SymptomSense Development Team

### Update Guidelines:
1. Keep diagrams synchronized with code changes
2. Update algorithms when implementation changes
3. Add new sections for new features
4. Maintain consistent formatting across documents
5. Include version history for major changes

## Quick Reference

### System Components
- **Frontend**: React + TypeScript + Vite + Material-UI
- **Backend**: Django + DRF + Python
- **Database**: Firebase Firestore
- **Storage**: Firebase Storage
- **AI**: Google Gemini API
- **ML**: PyTorch Neural Network
- **Authentication**: Firebase Auth (OAuth 2.0)

### Key Ports
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/api/docs/`

### Architecture Highlights
- **Multi-Agent System**: 7 specialized agents working in orchestrated workflow
- **ML Prediction**: PyTorch neural network with 87.3% accuracy
- **Medical Report Upload**: AI-powered extraction from PDF/images
- **Multi-System Treatment**: Allopathy, Ayurveda, Homeopathy, Lifestyle
- **Security**: Multi-layer security with Firebase Auth + JWT
- **Scalability**: Horizontal scaling with load balancing

## Additional Resources

- **API Documentation**: `backend/API_DOCUMENTATION.md`
- **Setup Guide**: `backend/README.md`
- **Quick Start**: `QUICK_START.md`
- **Main Architecture Diagram**: `ARCHITECTURE_DIAGRAM.md`

## Contact

For questions or clarifications about the architecture:
- Review the detailed documents in this directory
- Check the inline code documentation
- Refer to the API documentation
- Contact the development team

---

**Note**: These architecture documents provide a comprehensive understanding of the system design, algorithms, and implementation details. They are intended for developers, architects, and technical stakeholders who need to understand or work with the SymptomSense Health AI system.
