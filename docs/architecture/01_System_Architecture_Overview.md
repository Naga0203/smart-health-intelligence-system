# SymptomSense Health AI - System Architecture Overview

## Executive Summary

SymptomSense Health AI is a comprehensive health assessment platform that leverages artificial intelligence to analyze symptoms, predict potential health conditions, and provide personalized treatment recommendations across multiple medical systems (Allopathy, Ayurveda, Homeopathy, and Lifestyle modifications).

## High-Level Architecture

### Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                   (React + TypeScript)                       │
│                                                              │
│  • User Interface Components                                │
│  • State Management (Zustand)                               │
│  • Client-Side Routing                                      │
│  • Form Validation                                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ REST API (HTTPS + JWT)
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                   (Django + DRF)                            │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Multi-Agent Orchestration System           │    │
│  │                                                      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │    │
│  │  │ Orchestrator │→ │  Validation  │→ │ Predictor│ │    │
│  │  │    Agent     │  │    Agent     │  │  Agent   │ │    │
│  │  └──────────────┘  └──────────────┘  └──────────┘ │    │
│  │         │                                    │      │    │
│  │         ▼                                    ▼      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │    │
│  │  │ Explanation  │  │Recommendation│  │Extraction│ │    │
│  │  │    Agent     │  │    Agent     │  │  Agent   │ │    │
│  │  └──────────────┘  └──────────────┘  └──────────┘ │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Machine Learning Module                     │    │
│  │  • PyTorch Neural Network                          │    │
│  │  • Multi-hot Encoding                              │    │
│  │  • Disease Prediction                              │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Firebase SDK / Gemini API
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                    DATA & SERVICES LAYER                     │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────┐ │
│  │  Firebase Auth   │  │ Firebase Storage │  │ Firestore│ │
│  │  (OAuth 2.0)     │  │  (Medical Files) │  │ Database │ │
│  └──────────────────┘  └──────────────────┘  └──────────┘ │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  Google Gemini   │  │  Treatment KB    │               │
│  │  AI (LLM)        │  │  (Knowledge Base)│               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## Core Modules

### 1. Presentation Layer (Frontend)

**Technology Stack:**
- React 18 with TypeScript
- Vite (Build Tool)
- Material-UI (Component Library)
- Zustand (State Management)
- React Router v6 (Routing)
- Axios (HTTP Client)

**Key Modules:**
- **Authentication Module**: Login, registration, session management
- **Assessment Module**: Symptom input, medical report upload, form management
- **Results Module**: Risk visualization, confidence scoring, treatment display
- **History Module**: Assessment timeline, trend analysis
- **Profile Module**: User profile management

### 2. Application Layer (Backend)

**Technology Stack:**
- Django 4.2
- Django REST Framework
- Python 3.8+
- PyTorch (ML Framework)
- Firebase Admin SDK
- Google Gemini API

**Key Modules:**

#### A. Multi-Agent System
- **Orchestrator Agent**: Coordinates workflow between all agents
- **Validation Agent**: Validates input data using AI
- **Predictor Agent**: ML-based disease prediction
- **Explanation Agent**: Generates AI-powered explanations
- **Recommendation Agent**: Creates treatment recommendations
- **Extraction Agent**: Extracts data from medical reports (PDF/Images)

#### B. Machine Learning Module
- **Neural Network**: PyTorch-based multi-label classifier
- **Preprocessing**: Feature engineering and normalization
- **Inference Engine**: Real-time prediction service

#### C. API Layer
- **RESTful Endpoints**: CRUD operations for all resources
- **Authentication Middleware**: JWT token validation
- **Rate Limiting**: Throttling for API protection
- **Serialization**: Data validation and transformation

### 3. Data & Services Layer

**Firebase Services:**
- **Authentication**: Google OAuth 2.0, JWT tokens
- **Firestore**: NoSQL database for user data, assessments
- **Storage**: Medical report file storage

**External Services:**
- **Google Gemini AI**: Natural language processing, explanations
- **Treatment Knowledge Base**: Multi-system treatment database

## Data Flow Architecture

### Assessment Processing Pipeline

```
User Input
    │
    ▼
┌─────────────────────┐
│  Frontend           │
│  Validation         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  API Gateway        │
│  (Django REST)      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Orchestrator       │
│  Agent              │
└──────┬──────────────┘
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌─────────────────────┐              ┌─────────────────────┐
│  Validation Agent   │              │  Extraction Agent   │
│  (Gemini AI)        │              │  (Medical Reports)  │
└──────┬──────────────┘              └──────┬──────────────┘
       │                                      │
       └──────────────┬───────────────────────┘
                      │
                      ▼
              ┌─────────────────────┐
              │  Predictor Agent    │
              │  (ML Model)         │
              └──────┬──────────────┘
                     │
                     ├────────────────────────┐
                     │                        │
                     ▼                        ▼
          ┌─────────────────────┐  ┌─────────────────────┐
          │  Explanation Agent  │  │ Recommendation Agent│
          │  (Gemini AI)        │  │ (Treatment KB)      │
          └──────┬──────────────┘  └──────┬──────────────┘
                 │                        │
                 └────────┬───────────────┘
                          │
                          ▼
                  ┌─────────────────────┐
                  │  Firestore          │
                  │  (Data Storage)     │
                  └──────┬──────────────┘
                         │
                         ▼
                  ┌─────────────────────┐
                  │  Response to User   │
                  └─────────────────────┘
```

## Security Architecture

### Multi-Layer Security Model

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Transport Security                                │
│  • HTTPS/TLS Encryption                                     │
│  • Secure WebSocket Connections                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Authentication & Authorization                    │
│  • Firebase Authentication (OAuth 2.0)                      │
│  • JWT Token Validation                                     │
│  • Role-Based Access Control (RBAC)                         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: API Security                                      │
│  • CORS Protection                                          │
│  • Rate Limiting (10 req/min, 100 req/hr, 200 req/day)    │
│  • Request Validation                                       │
│  • CSRF Protection                                          │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Data Security                                     │
│  • Input Sanitization                                       │
│  • SQL Injection Prevention                                 │
│  • XSS Protection                                           │
│  • Data Encryption at Rest                                  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: Database Security                                 │
│  • Firestore Security Rules                                 │
│  • User Data Isolation                                      │
│  • Audit Logging                                            │
└─────────────────────────────────────────────────────────────┘
```

## Scalability Considerations

### Horizontal Scaling Strategy

1. **Frontend**: CDN distribution, static asset caching
2. **Backend**: Load-balanced Django instances
3. **Database**: Firestore auto-scaling
4. **ML Model**: Model serving with caching
5. **AI Services**: Gemini API with rate limiting

### Performance Optimization

- **Caching**: Redis for frequently accessed data
- **Async Processing**: Celery for background tasks
- **Database Indexing**: Optimized Firestore queries
- **Code Splitting**: Lazy loading of React components
- **API Response Compression**: Gzip compression

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Environment                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   CDN            │         │  Load Balancer   │         │
│  │   (Frontend)     │         │  (Backend)       │         │
│  └────────┬─────────┘         └────────┬─────────┘         │
│           │                            │                    │
│           ▼                            ▼                    │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Static Assets   │         │  Django App      │         │
│  │  (React Build)   │         │  Instances (N)   │         │
│  └──────────────────┘         └────────┬─────────┘         │
│                                        │                    │
│                                        ▼                    │
│                               ┌──────────────────┐         │
│                               │  Firebase        │         │
│                               │  Services        │         │
│                               └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Technology Decisions & Rationale

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Frontend Framework | React | Component reusability, large ecosystem, TypeScript support |
| State Management | Zustand | Lightweight, simple API, no boilerplate |
| Backend Framework | Django | Rapid development, built-in admin, ORM, security features |
| Database | Firestore | Real-time sync, scalability, Firebase integration |
| ML Framework | PyTorch | Flexibility, research-friendly, production-ready |
| AI Service | Google Gemini | Advanced NLP, multimodal support, cost-effective |
| Authentication | Firebase Auth | OAuth integration, secure, managed service |

## System Metrics & Monitoring

### Key Performance Indicators (KPIs)

1. **Response Time**: < 2 seconds for API calls
2. **Availability**: 99.9% uptime
3. **Prediction Accuracy**: > 85% for top-3 predictions
4. **User Satisfaction**: > 4.5/5 rating
5. **Error Rate**: < 1% of requests

### Monitoring Stack

- **Application Monitoring**: Django logging, error tracking
- **Performance Monitoring**: Response time tracking
- **User Analytics**: Usage patterns, feature adoption
- **Security Monitoring**: Failed auth attempts, rate limit violations

## Future Enhancements

1. **Real-time Collaboration**: Multi-user assessment reviews
2. **Mobile Applications**: Native iOS/Android apps
3. **Telemedicine Integration**: Video consultations
4. **Wearable Device Integration**: Real-time vitals monitoring
5. **Advanced Analytics**: Predictive health trends
6. **Multi-language Support**: Internationalization
7. **Voice Input**: Speech-to-text for symptom entry

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Maintained By**: SymptomSense Development Team
