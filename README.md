# AI Health Intelligence System

A comprehensive healthcare decision-support platform using **LangChain** framework with **Google Gemini AI** for intelligent health risk assessment.

## 🌟 Features

- **AI-Powered Data Extraction**: Uses Gemini AI to parse natural language symptoms and map them to ML model features
- **Multi-Disease Prediction**: Supports Diabetes, Heart Disease, and Hypertension prediction
- **LangChain Agent System**: Intelligent agents for validation, extraction, explanation, and recommendations
- **Confidence-Aware Responses**: Adapts output based on prediction confidence (LOW/MEDIUM/HIGH)
- **Multi-System Treatment Information**: Provides information across Allopathy, Ayurveda, Homeopathy, and Lifestyle approaches
- **Ethical Safeguards**: Multiple layers of disclaimers and confidence-based gating
- **Complete Audit Trail**: MongoDB storage for all assessments and operations
- **Explainable AI**: Clear explanations for all predictions using Gemini AI

## 🏗️ Architecture

```
User Input → Validation → Data Extraction (Gemini) → ML Prediction → 
Confidence Evaluation → Explanation (Gemini) → Recommendations → 
MongoDB Storage → Frontend Response
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- MongoDB (optional for development)
- Google Gemini API Key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd health_ai_backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Start the development server**
```bash
python manage.py runserver
```

## 📋 Environment Configuration

Create a `.env` file with the following variables:

```bash
# Django Configuration
DJANGO_SECRET_KEY=your_django_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/health_ai_db
MONGO_DB_NAME=health_ai_db

# Google Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 🔧 System Components

### AI Agents (LangChain-based)

1. **ValidationAgent**: Input validation and sanitization
2. **DataExtractionAgent**: Symptom-to-feature mapping using Gemini AI
3. **ExplanationAgent**: Natural language explanation generation
4. **RecommendationAgent**: Ethical gating and treatment recommendations
5. **OrchestratorAgent**: Complete pipeline coordination

### ML Prediction Engine

- **DiseasePredictor**: ML-based disease prediction
- **Supported Diseases**: Diabetes, Heart Disease, Hypertension
- **Models**: Mock models (can be replaced with trained models)

### Database Layer

- **MongoDB**: Document storage for assessments
- **Collections**: symptoms, predictions, explanations, recommendations, audit_logs

## 📡 API Usage

### Health Assessment Endpoint

```http
POST /api/health/analyze
Content-Type: application/json

{
  "user_id": "user123",
  "age": 45,
  "gender": "male",
  "symptoms": [
    "increased thirst",
    "frequent urination",
    "fatigue",
    "blurred vision"
  ],
  "additional_info": {
    "weight_loss": true
  }
}
```

### Response

```json
{
  "user_id": "user123",
  "assessment_id": "pred_abc123",
  "prediction": {
    "disease": "Diabetes",
    "probability": 0.85,
    "probability_percent": 85.0,
    "confidence": "HIGH",
    "model_version": "v1.0_mock"
  },
  "extraction": {
    "confidence": 0.85,
    "method": "gemini_ai_extraction"
  },
  "explanation": {
    "summary": "Risk assessment for Diabetes",
    "main_explanation": "Based on your symptoms...",
    "confidence_reasoning": {...},
    "educational_content": {...},
    "disclaimer": "This is not a medical diagnosis..."
  },
  "recommendations": {
    "treatment_information": {
      "available": true,
      "systems": {
        "allopathy": {...},
        "ayurveda": {...},
        "homeopathy": {...},
        "lifestyle": {...}
      }
    },
    "professional_referral": {...}
  },
  "metadata": {
    "processing_time_seconds": 0.5,
    "timestamp": "2026-02-09T12:00:00Z",
    "storage_ids": {...}
  }
}
```

## 🧪 Testing

Run the complete pipeline test:

```bash
python test_complete_pipeline.py
```

This will test:
- Individual component functionality
- Complete pipeline flow
- Data extraction with Gemini AI
- ML prediction
- Agent orchestration
- Database operations (if MongoDB is running)

## 📊 System Flow

See [SYSTEM_FLOW.md](SYSTEM_FLOW.md) for detailed pipeline documentation.

## 🔒 Security Features

- **Input Validation**: Multiple layers of validation
- **Safety Filters**: XSS and SQL injection prevention
- **Sanitization**: All input data sanitized
- **Audit Logging**: Complete trail of all operations
- **No Hardcoded Secrets**: All sensitive data in environment variables

## ⚖️ Ethical Safeguards

1. **Confidence-Based Gating**: Treatment information only for MEDIUM/HIGH confidence
2. **Medical Disclaimers**: All responses include appropriate disclaimers
3. **Professional Referrals**: Always recommend consulting healthcare professionals
4. **No Diagnosis Claims**: System never claims to provide medical diagnosis
5. **Transparency**: Clear explanation of how assessments are made

## 📦 Dependencies

### Core
- Django 6.0.1
- Django REST Framework 3.15.2
- LangChain 0.3.13
- LangChain Google GenAI 2.0.8

### Database
- PyMongo 4.10.1

### ML & Data
- Scikit-learn 1.6.0
- NumPy 2.2.1
- Pandas 2.2.3

### Testing
- Pytest 8.3.4
- Hypothesis 6.122.2 (for property-based testing)

See [requirements.txt](requirements.txt) for complete list.

## 📁 Project Structure

```
health_ai_backend/
├── agents/                    # AI Agents (LangChain-based)
│   ├── base_agent.py         # Base agent class
│   ├── validation.py         # Validation agent
│   ├── data_extraction.py    # Data extraction agent (Gemini)
│   ├── explanation.py        # Explanation agent (Gemini)
│   ├── recommendation.py     # Recommendation agent
│   └── orchestrator.py       # Main orchestrator
├── prediction/               # ML Prediction Engine
│   └── predictor.py         # Disease predictor
├── treatment/               # Treatment Knowledge Base
│   └── knowledge_base.py    # Multi-system treatment data
├── common/                  # Common Utilities
│   ├── database.py         # MongoDB connection
│   └── gemini_client.py    # LangChain Gemini client
├── api/                    # REST API
├── health_ai_backend/      # Django project settings
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
└── SYSTEM_FLOW.md         # Detailed flow documentation
```

## 🎯 Use Cases

1. **Health Risk Assessment**: Users can input symptoms and get risk assessments
2. **Treatment Exploration**: Learn about different treatment approaches
3. **Health Education**: Understand health conditions and risk factors
4. **Decision Support**: Get guidance on when to seek professional help

## ⚠️ Important Disclaimers

- **NOT FOR DIAGNOSIS**: This system is for educational and informational purposes only
- **NOT A SUBSTITUTE**: Does not replace professional medical advice
- **CONSULT PROFESSIONALS**: Always consult qualified healthcare providers
- **DECISION SUPPORT**: Provides decision support, not medical diagnosis

## 🔮 Future Enhancements

- [ ] Replace mock models with trained ML models
- [ ] Add more disease types
- [ ] Implement user authentication
- [ ] Add real-time monitoring dashboard
- [ ] Implement caching for better performance
- [ ] Add multi-language support
- [ ] Mobile app integration
- [ ] EHR system integration (future scope)

## 📄 License

[Your License Here]

## 👥 Contributors

[Your Team Here]

## 📞 Support

For issues and questions, please open an issue on GitHub or contact [your-email@example.com]

---

**Built with ❤️ using LangChain and Google Gemini AI**