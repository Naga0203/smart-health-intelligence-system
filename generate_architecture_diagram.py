"""
Generate a complete system architecture diagram in PNG format
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Client
from diagrams.programming.framework import React, Django
from diagrams.firebase.base import Firebase
from diagrams.gcp.ml import AIHub
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.network import Nginx
from diagrams.programming.language import Python, TypeScript

# Configure diagram
graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.0"
}

with Diagram("SymptomSense Health AI - Complete Architecture", 
             filename="architecture_diagram",
             show=False,
             direction="TB",
             graph_attr=graph_attr):
    
    # User/Browser
    user = Client("User Browser\n(localhost:3000)")
    
    # Frontend Cluster
    with Cluster("React Frontend\n(Vite + TypeScript)"):
        with Cluster("Pages"):
            pages = React("Landing\nLogin\nDashboard\nAssessment\nResults\nHistory\nProfile")
        
        with Cluster("State Management"):
            stores = TypeScript("Zustand Stores\n- Auth\n- User\n- Assessment\n- System")
        
        with Cluster("Services"):
            firebase_svc = Firebase("Firebase Service\n- login()\n- logout()\n- getToken()")
            api_svc = React("API Service\n(Axios)\n- get()\n- post()\n- put()")
    
    # Backend Cluster
    with Cluster("Django Backend\n(localhost:8000)"):
        with Cluster("API Layer"):
            api_endpoints = Django("REST API\n/api/health/\n/api/status/\n/api/user/profile/\n/api/assess/")
        
        with Cluster("Agent System"):
            orchestrator = Python("Orchestrator\nAgent")
            validation = Python("Validation\nAgent")
            predictor = Python("Predictor\nAgent")
            explanation = Python("Explanation\nAgent")
            recommendation = Python("Recommendation\nAgent")
            extraction = Python("Data Extraction\nAgent")
        
        with Cluster("ML Pipeline"):
            ml_model = Python("PyTorch Model\n- Inference\n- Preprocessing")
        
        with Cluster("Services"):
            firebase_auth = Firebase("Firebase Auth\nService")
            firebase_db = Firebase("Firebase DB\nService")
            gemini_client = Python("Gemini Client\nService")
    
    # External Services
    with Cluster("External Services"):
        firebase_cloud = Firebase("Firebase Cloud\n- Authentication\n- Firestore DB")
        gemini_ai = AIHub("Google Gemini AI\n- Explanations\n- Extraction\n- Validation")
    
    # User interactions
    user >> Edge(label="HTTP Requests") >> pages
    user >> Edge(label="Google OAuth") >> firebase_svc
    
    # Frontend internal flow
    pages >> stores
    stores >> api_svc
    stores >> firebase_svc
    
    # Frontend to Backend
    api_svc >> Edge(label="HTTP + JWT Token") >> api_endpoints
    firebase_svc >> Edge(label="Auth") >> firebase_cloud
    
    # Backend API to Agents
    api_endpoints >> orchestrator
    orchestrator >> validation
    orchestrator >> predictor
    orchestrator >> explanation
    orchestrator >> recommendation
    orchestrator >> extraction
    
    # Agents to ML
    predictor >> ml_model
    
    # Agents to Services
    validation >> gemini_client
    explanation >> gemini_client
    extraction >> gemini_client
    
    # Backend Services to External
    firebase_auth >> firebase_cloud
    firebase_db >> firebase_cloud
    gemini_client >> gemini_ai
    
    # Data persistence
    api_endpoints >> Edge(label="Save/Load") >> firebase_db

print("Architecture diagram generated successfully!")
print("Output file: architecture_diagram.png")
