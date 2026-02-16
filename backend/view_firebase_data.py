#!/usr/bin/env python
"""
View Firebase Firestore Data

This script extracts and displays all data from Firebase Firestore collections.
"""
import os
import sys
import django
from datetime import datetime
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_ai_backend.settings')
django.setup()

from common.firebase_db import get_firebase_db
from firebase_admin import firestore

# Initialize Firebase
try:
    db_instance = get_firebase_db()
    print("Firebase initialized successfully")
except Exception as e:
    print(f"Warning: Firebase initialization: {e}")

def format_timestamp(timestamp):
    """Format timestamp for display."""
    if isinstance(timestamp, datetime):
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return str(timestamp)

def print_section(title, char="="):
    """Print a formatted section header."""
    print("\n" + char * 80)
    print(f" {title}")
    print(char * 80)

def print_subsection(title):
    """Print a formatted subsection header."""
    print("\n" + "-" * 80)
    print(f" {title}")
    print("-" * 80)

def view_users():
    """View all users from Firestore."""
    print_section("USERS COLLECTION", "=")
    
    try:
        db = firestore.client()
        users_ref = db.collection('users')
        users = list(users_ref.stream())
        
        if not users:
            print("No users found in the database.")
            return
        
        print(f"\nTotal Users: {len(users)}\n")
        
        for idx, user_doc in enumerate(users, 1):
            user_data = user_doc.to_dict()
            
            print_subsection(f"User #{idx}: {user_data.get('display_name', 'Unknown')}")
            
            print(f"  UID:              {user_data.get('uid', 'N/A')}")
            print(f"  Email:            {user_data.get('email', 'N/A')}")
            print(f"  Display Name:     {user_data.get('display_name', 'N/A')}")
            print(f"  Email Verified:   {user_data.get('email_verified', False)}")
            print(f"  Phone:            {user_data.get('phone_number', 'N/A')}")
            print(f"  Date of Birth:    {user_data.get('date_of_birth', 'N/A')}")
            print(f"  Gender:           {user_data.get('gender', 'N/A')}")
            print(f"  Created:          {format_timestamp(user_data.get('created_at'))}")
            print(f"  Last Login:       {format_timestamp(user_data.get('last_login'))}")
            
            # Medical information
            medical_history = user_data.get('medical_history', [])
            if medical_history:
                print(f"  Medical History:  {', '.join(medical_history)}")
            
            allergies = user_data.get('allergies', [])
            if allergies:
                print(f"  Allergies:        {', '.join(allergies)}")
            
            medications = user_data.get('current_medications', [])
            if medications:
                print(f"  Medications:      {', '.join(medications)}")
            
            print()
    
    except Exception as e:
        print(f"Error fetching users: {e}")

def view_medical_history():
    """View all medical history records."""
    print_section("MEDICAL HISTORY COLLECTION", "=")
    
    try:
        db = firestore.client()
        history_ref = db.collection('medical_history')
        histories = list(history_ref.stream())
        
        if not histories:
            print("No medical history records found.")
            return
        
        print(f"\nTotal Medical History Records: {len(histories)}\n")
        
        for idx, history_doc in enumerate(histories, 1):
            history_data = history_doc.to_dict()
            
            print_subsection(f"Medical History #{idx} - User: {history_data.get('user_id', 'Unknown')}")
            
            # Conditions
            conditions = history_data.get('conditions', [])
            if conditions:
                print(f"  Conditions:       {', '.join(conditions)}")
            
            # Surgeries
            surgeries = history_data.get('surgeries', [])
            if surgeries:
                print(f"  Surgeries:")
                for surgery in surgeries:
                    print(f"    - {surgery.get('type', 'Unknown')} on {surgery.get('date', 'Unknown date')} at {surgery.get('hospital', 'Unknown hospital')}")
            
            # Family History
            family_history = history_data.get('family_history', [])
            if family_history:
                print(f"  Family History:   {', '.join(family_history)}")
            
            # Allergies
            allergies = history_data.get('allergies', [])
            if allergies:
                print(f"  Allergies:        {', '.join(allergies)}")
            
            # Current Medications
            medications = history_data.get('current_medications', [])
            if medications:
                print(f"  Current Medications:")
                for med in medications:
                    print(f"    - {med.get('name', 'Unknown')} {med.get('dosage', '')} {med.get('frequency', '')}")
            
            # Immunizations
            immunizations = history_data.get('immunizations', [])
            if immunizations:
                print(f"  Immunizations:")
                for imm in immunizations:
                    print(f"    - {imm.get('vaccine', 'Unknown')} ({imm.get('dose', 'Unknown dose')}) on {imm.get('date', 'Unknown date')}")
            
            # Lifestyle
            lifestyle = history_data.get('lifestyle', {})
            if lifestyle:
                print(f"  Lifestyle:")
                print(f"    Smoking:        {lifestyle.get('smoking', 'N/A')}")
                print(f"    Alcohol:        {lifestyle.get('alcohol', 'N/A')}")
                print(f"    Exercise:       {lifestyle.get('exercise', 'N/A')}")
                print(f"    Diet:           {lifestyle.get('diet', 'N/A')}")
            
            # Notes
            notes = history_data.get('notes', '')
            if notes:
                print(f"  Notes:            {notes}")
            
            print(f"  Last Updated:     {format_timestamp(history_data.get('last_updated'))}")
            print()
    
    except Exception as e:
        print(f"Error fetching medical history: {e}")

def view_assessments():
    """View all assessments."""
    print_section("ASSESSMENTS COLLECTION", "=")
    
    try:
        db = firestore.client()
        assessments_ref = db.collection('assessments')
        assessments = list(assessments_ref.stream())
        
        if not assessments:
            print("No assessments found.")
            return
        
        print(f"\nTotal Assessments: {len(assessments)}\n")
        
        # Group by user
        assessments_by_user = {}
        for assessment_doc in assessments:
            assessment_data = assessment_doc.to_dict()
            user_id = assessment_data.get('user_id', 'Unknown')
            if user_id not in assessments_by_user:
                assessments_by_user[user_id] = []
            assessments_by_user[user_id].append({
                'id': assessment_doc.id,
                'data': assessment_data
            })
        
        # Display by user
        for user_id, user_assessments in assessments_by_user.items():
            print_subsection(f"User: {user_id} ({len(user_assessments)} assessments)")
            
            for idx, assessment in enumerate(user_assessments, 1):
                assessment_data = assessment['data']
                
                print(f"\n  Assessment #{idx} (ID: {assessment['id']})")
                print(f"    Created:          {format_timestamp(assessment_data.get('created_at'))}")
                print(f"    Disease:          {assessment_data.get('disease', 'Unknown')}")
                print(f"    Confidence:       {assessment_data.get('confidence', 'Unknown')}")
                print(f"    Probability:      {assessment_data.get('probability', 0):.2%}")
                print(f"    Status:           {assessment_data.get('status', 'Unknown')}")
                
                # Symptoms
                symptoms = assessment_data.get('symptoms', [])
                if symptoms:
                    print(f"    Symptoms:         {', '.join(symptoms)}")
                
                # Demographics
                print(f"    Age:              {assessment_data.get('age', 'N/A')}")
                print(f"    Gender:           {assessment_data.get('gender', 'N/A')}")
                
                # Extraction data
                extraction = assessment_data.get('extraction_data', {})
                if extraction:
                    print(f"    Extraction:")
                    print(f"      Confidence:     {extraction.get('confidence', 0):.2%}")
                    print(f"      Method:         {extraction.get('method', 'Unknown')}")
                
                # Explanation
                explanation = assessment_data.get('explanation', {})
                if explanation:
                    print(f"    Explanation:")
                    explanation_text = explanation.get('text', '')
                    if len(explanation_text) > 100:
                        explanation_text = explanation_text[:100] + "..."
                    print(f"      {explanation_text}")
                
                # Recommendations
                recommendations = assessment_data.get('recommendations', {})
                if recommendations:
                    items = recommendations.get('items', [])
                    if items:
                        print(f"    Recommendations:  {len(items)} items")
                        for rec in items[:3]:  # Show first 3
                            print(f"      - {rec}")
                
                # Treatment info
                treatment_info = assessment_data.get('treatment_info', {})
                if treatment_info:
                    print(f"    Treatment Info:   Available for {len(treatment_info)} systems")
            
            print()
    
    except Exception as e:
        print(f"Error fetching assessments: {e}")

def view_statistics():
    """View database statistics."""
    print_section("DATABASE STATISTICS", "=")
    
    try:
        db = firestore.client()
        
        # Count documents in each collection
        collections = ['users', 'medical_history', 'assessments', 'predictions', 'explanations', 'recommendations', 'audit_logs']
        
        print("\nCollection Document Counts:")
        print("-" * 40)
        
        total_docs = 0
        for collection_name in collections:
            try:
                docs = list(db.collection(collection_name).stream())
                count = len(docs)
                total_docs += count
                print(f"  {collection_name:20s}: {count:5d} documents")
            except Exception as e:
                print(f"  {collection_name:20s}: Error - {e}")
        
        print("-" * 40)
        print(f"  {'TOTAL':20s}: {total_docs:5d} documents")
        
        # Assessment statistics
        print("\n\nAssessment Statistics:")
        print("-" * 40)
        
        assessments = list(db.collection('assessments').stream())
        if assessments:
            confidence_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}
            disease_counts = {}
            
            for assessment_doc in assessments:
                data = assessment_doc.to_dict()
                confidence = data.get('confidence', 'Unknown')
                if confidence in confidence_counts:
                    confidence_counts[confidence] += 1
                
                disease = data.get('disease', 'Unknown')
                disease_counts[disease] = disease_counts.get(disease, 0) + 1
            
            print(f"  By Confidence Level:")
            for level, count in confidence_counts.items():
                percentage = (count / len(assessments)) * 100
                print(f"    {level:10s}: {count:3d} ({percentage:5.1f}%)")
            
            print(f"\n  By Disease (Top 5):")
            sorted_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)
            for disease, count in sorted_diseases[:5]:
                percentage = (count / len(assessments)) * 100
                print(f"    {disease:20s}: {count:3d} ({percentage:5.1f}%)")
        
        print()
    
    except Exception as e:
        print(f"Error fetching statistics: {e}")

def export_to_json():
    """Export all data to JSON file."""
    print_section("EXPORTING DATA TO JSON", "=")
    
    try:
        db = firestore.client()
        
        export_data = {
            'users': [],
            'medical_history': [],
            'assessments': [],
            'export_date': datetime.now().isoformat()
        }
        
        # Export users
        users = list(db.collection('users').stream())
        for user_doc in users:
            user_data = user_doc.to_dict()
            # Convert datetime objects to strings
            for key, value in user_data.items():
                if isinstance(value, datetime):
                    user_data[key] = value.isoformat()
            export_data['users'].append(user_data)
        
        # Export medical history
        histories = list(db.collection('medical_history').stream())
        for history_doc in histories:
            history_data = history_doc.to_dict()
            for key, value in history_data.items():
                if isinstance(value, datetime):
                    history_data[key] = value.isoformat()
            export_data['medical_history'].append(history_data)
        
        # Export assessments
        assessments = list(db.collection('assessments').stream())
        for assessment_doc in assessments:
            assessment_data = assessment_doc.to_dict()
            assessment_data['id'] = assessment_doc.id
            for key, value in assessment_data.items():
                if isinstance(value, datetime):
                    assessment_data[key] = value.isoformat()
            export_data['assessments'].append(assessment_data)
        
        # Write to file
        filename = 'firebase_data_export.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Data exported successfully to: {filename}")
        print(f"  Users:            {len(export_data['users'])}")
        print(f"  Medical History:  {len(export_data['medical_history'])}")
        print(f"  Assessments:      {len(export_data['assessments'])}")
        print()
    
    except Exception as e:
        print(f"Error exporting data: {e}")

def main():
    """Main function to display all data."""
    print("\n" + "=" * 80)
    print(" FIREBASE FIRESTORE DATA VIEWER")
    print("=" * 80)
    print(f" Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # View all data
    view_users()
    view_medical_history()
    view_assessments()
    view_statistics()
    export_to_json()
    
    # Summary
    print_section("VIEWING COMPLETE", "=")
    print("\nAll data has been displayed above.")
    print("Data has also been exported to: firebase_data_export.json")
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
