#!/usr/bin/env python
"""
Seed Firebase Firestore with test data.

This script adds sample users, assessments, and medical history to Firebase.
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_ai_backend.settings')
django.setup()

from common.firebase_db import get_firebase_db

def seed_data():
    """Seed Firebase with test data."""
    print("=" * 60)
    print("SEEDING FIREBASE FIRESTORE WITH TEST DATA")
    print("=" * 60)
    
    try:
        db = get_firebase_db()
        print("✓ Connected to Firebase Firestore")
        
        # Get direct access to Firestore for seeding
        from firebase_admin import firestore
        firestore_db = firestore.client()
        print("✓ Got Firestore client")
    except Exception as e:
        print(f"✗ Failed to connect to Firebase: {e}")
        return
    
    # Sample user IDs (these would normally come from Firebase Auth)
    test_users = [
        {
            'uid': 'test_user_1',
            'email': 'john.doe@example.com',
            'display_name': 'John Doe',
        },
        {
            'uid': 'test_user_2',
            'email': 'jane.smith@example.com',
            'display_name': 'Jane Smith',
        },
        {
            'uid': 'test_user_3',
            'email': 'bob.johnson@example.com',
            'display_name': 'Bob Johnson',
        }
    ]
    
    # Seed users
    print("\n" + "-" * 60)
    print("SEEDING USERS")
    print("-" * 60)
    
    for user in test_users:
        user_data = {
            'uid': user['uid'],
            'email': user['email'],
            'display_name': user['display_name'],
            'photo_url': '',
            'email_verified': True,
            'created_at': datetime.now() - timedelta(days=random.randint(30, 180)),
            'updated_at': datetime.now(),
            'last_login': datetime.now(),
            'phone_number': f'+1{random.randint(2000000000, 9999999999)}',
            'date_of_birth': f'19{random.randint(70, 95)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
            'gender': random.choice(['male', 'female', 'other']),
            'address': {},
            'emergency_contact': {},
            'medical_history': random.sample(['diabetes', 'hypertension', 'asthma', 'allergies'], k=random.randint(0, 2)),
            'allergies': random.sample(['penicillin', 'peanuts', 'shellfish', 'latex'], k=random.randint(0, 2)),
            'current_medications': random.sample(['metformin', 'lisinopril', 'aspirin', 'ibuprofen'], k=random.randint(0, 2))
        }
        
        firestore_db.collection('users').document(user['uid']).set(user_data)
        print(f"✓ Created user: {user['display_name']} ({user['email']})")
    
    # Seed medical history
    print("\n" + "-" * 60)
    print("SEEDING MEDICAL HISTORY")
    print("-" * 60)
    
    for user in test_users[:2]:  # Only for first 2 users
        medical_history = {
            'user_id': user['uid'],
            'conditions': random.sample(['diabetes', 'hypertension', 'asthma', 'arthritis'], k=random.randint(1, 3)),
            'surgeries': [
                {
                    'type': random.choice(['appendectomy', 'tonsillectomy', 'knee surgery']),
                    'date': f'20{random.randint(10, 22)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'hospital': random.choice(['General Hospital', 'City Medical Center', 'Regional Hospital'])
                }
            ] if random.random() > 0.5 else [],
            'family_history': random.sample(['heart disease', 'cancer', 'diabetes', 'alzheimers'], k=random.randint(1, 3)),
            'allergies': random.sample(['penicillin', 'sulfa drugs', 'peanuts', 'shellfish'], k=random.randint(0, 2)),
            'current_medications': [
                {
                    'name': med,
                    'dosage': f'{random.choice([5, 10, 25, 50, 100])}mg',
                    'frequency': random.choice(['once daily', 'twice daily', 'three times daily'])
                }
                for med in random.sample(['metformin', 'lisinopril', 'atorvastatin', 'aspirin'], k=random.randint(1, 3))
            ],
            'immunizations': [
                {
                    'vaccine': vaccine,
                    'date': f'20{random.randint(20, 24)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'dose': random.choice(['first', 'second', 'booster'])
                }
                for vaccine in random.sample(['COVID-19', 'Flu', 'Tetanus', 'Hepatitis B'], k=random.randint(1, 3))
            ],
            'lifestyle': {
                'smoking': random.choice(['never', 'former', 'current']),
                'alcohol': random.choice(['never', 'occasional', 'moderate', 'heavy']),
                'exercise': random.choice(['sedentary', '1-2 times/week', '3-4 times/week', 'daily']),
                'diet': random.choice(['balanced', 'vegetarian', 'vegan', 'high-protein', 'low-carb'])
            },
            'notes': 'Patient is generally healthy and compliant with medications.',
            'last_updated': datetime.now()
        }
        
        firestore_db.collection('medical_history').document(user['uid']).set(medical_history)
        print(f"✓ Created medical history for: {user['display_name']}")
    
    # Seed assessments
    print("\n" + "-" * 60)
    print("SEEDING ASSESSMENTS")
    print("-" * 60)
    
    diseases = ['Diabetes', 'Hypertension', 'Common Cold', 'Influenza', 'Migraine', 'Asthma']
    symptom_sets = [
        ['increased thirst', 'frequent urination', 'fatigue'],
        ['headache', 'dizziness', 'chest pain'],
        ['fever', 'cough', 'sore throat'],
        ['fever', 'body aches', 'fatigue'],
        ['severe headache', 'nausea', 'sensitivity to light'],
        ['shortness of breath', 'wheezing', 'chest tightness']
    ]
    
    assessment_count = 0
    for user in test_users:
        # Create 3-8 assessments per user
        num_assessments = random.randint(3, 8)
        
        for i in range(num_assessments):
            disease_idx = random.randint(0, len(diseases) - 1)
            disease = diseases[disease_idx]
            symptoms = symptom_sets[disease_idx]
            
            confidence = random.choice(['LOW', 'MEDIUM', 'HIGH'])
            probability = {
                'LOW': random.uniform(0.3, 0.54),
                'MEDIUM': random.uniform(0.55, 0.74),
                'HIGH': random.uniform(0.75, 0.95)
            }[confidence]
            
            assessment_data = {
                'user_id': user['uid'],
                'created_at': datetime.now() - timedelta(days=random.randint(1, 90)),
                'symptoms': symptoms,
                'age': random.randint(25, 65),
                'gender': user.get('gender', 'male'),
                'disease': disease,
                'probability': probability,
                'confidence': confidence,
                'extraction_data': {
                    'confidence': random.uniform(0.7, 0.95),
                    'method': 'gemini_ai_extraction',
                    'extracted_features': random.sample(['glucose', 'bmi', 'age', 'blood_pressure'], k=random.randint(2, 4))
                },
                'prediction_metadata': {
                    'model_version': 'v1.0',
                    'processing_time': random.uniform(1.0, 3.0)
                },
                'explanation': {
                    'text': f'Based on the symptoms provided including {", ".join(symptoms)}, there is a {confidence.lower()} probability of {disease}.',
                    'generated_by': 'gemini',
                    'confidence': confidence
                },
                'recommendations': {
                    'items': [
                        'Consult a healthcare professional',
                        'Monitor symptoms closely',
                        'Maintain a healthy lifestyle'
                    ],
                    'urgency': random.choice(['low', 'medium', 'high']),
                    'confidence': confidence
                },
                'status': 'completed'
            }
            
            # Add treatment info for MEDIUM and HIGH confidence
            if confidence in ['MEDIUM', 'HIGH']:
                assessment_data['treatment_info'] = {
                    'allopathy': {
                        'approach': 'Medication and monitoring',
                        'focus': 'Symptom management',
                        'disclaimer': 'Consult healthcare professional'
                    },
                    'ayurveda': {
                        'approach': 'Holistic balance',
                        'focus': 'Natural remedies',
                        'disclaimer': 'Consult Ayurvedic practitioner'
                    },
                    'lifestyle': {
                        'approach': 'Diet and exercise',
                        'focus': 'Preventive care',
                        'disclaimer': 'General wellness information'
                    }
                }
            
            # Create assessment document
            assessment_ref = firestore_db.collection('assessments').document()
            assessment_ref.set(assessment_data)
            assessment_count += 1
            
            if assessment_count % 5 == 0:
                print(f"✓ Created {assessment_count} assessments...")
    
    print(f"✓ Total assessments created: {assessment_count}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SEEDING COMPLETE!")
    print("=" * 60)
    print(f"✓ Users created: {len(test_users)}")
    print(f"✓ Medical histories created: 2")
    print(f"✓ Assessments created: {assessment_count}")
    print("\nTest User Credentials (for Firebase Auth):")
    print("-" * 60)
    for user in test_users:
        print(f"  Email: {user['email']}")
        print(f"  UID: {user['uid']}")
        print()
    print("Note: These users need to be created in Firebase Authentication")
    print("      to actually log in. The data above is just for Firestore.")
    print("=" * 60)

if __name__ == '__main__':
    seed_data()
