"""
Django management command to create database indexes for optimal query performance.

Run this command to set up indexes:
    python manage.py create_indexes

This creates indexes on frequently queried fields in Firestore collections.
"""

from django.core.management.base import BaseCommand
from common.firebase_db import get_firebase_db
import logging

logger = logging.getLogger('health_ai.management')


class Command(BaseCommand):
    help = 'Create database indexes for optimal query performance'

    def handle(self, *args, **options):
        self.stdout.write('Creating database indexes...')
        
        try:
            db = get_firebase_db()
            
            # Note: Firestore automatically creates indexes for single-field queries
            # Composite indexes need to be created via  Firebase Console or gcloud CLI
            
            self.stdout.write(self.style.SUCCESS('\n✓ Firestore Auto-Indexing Information:'))
            self.stdout.write('  - Single-field indexes are created automatically')
            self.stdout.write('  - Composite indexes require Firebase Console or gcloud CLI')
            
            self.stdout.write('\n📋 Recommended Composite Indexes:')
            
            composite_indexes = [
                {
                    'collection': 'assessments',
                    'fields': [
                        ('user_id', 'ASCENDING'),
                        ('created_at', 'DESCENDING')
                    ],
                    'purpose': 'Fetch user assessments sorted by date'
                },
                {
                    'collection': 'assessments',
                    'fields': [
                        ('user_id', 'ASCENDING'),
                        ('disease', 'ASCENDING'),
                        ('created_at', 'DESCENDING')
                    ],
                    'purpose': 'Fetch user assessments for specific disease'
                },
                {
                    'collection': 'assessments',
                    'fields': [
                        ('user_id', 'ASCENDING'),
                        ('confidence', 'ASCENDING'),
                        ('created_at', 'DESCENDING')
                    ],
                    'purpose': 'Fetch user assessments by confidence level'
                },
                {
                    'collection': 'reports',
                    'fields': [
                        ('user_id', 'ASCENDING'),
                        ('upload_date', 'DESCENDING')
                    ],
                    'purpose': 'Fetch user reports sorted by upload date'
                },
                {
                    'collection': 'reports',
                    'fields': [
                        ('user_id', 'ASCENDING'),
                        ('report_type', 'ASCENDING'),
                        ('upload_date', 'DESCENDING')
                    ],
                    'purpose': 'Fetch user reports by type'
                }
            ]
            
            for idx, index_def in enumerate(composite_indexes, 1):
                self.stdout.write(f'\n{idx}. Collection: {index_def["collection"]}')
                self.stdout.write(f'   Fields: {", ".join([f"{field[0]} ({field[1]})" for field in index_def["fields"]])}')
                self.stdout.write(f'   Purpose: {index_def["purpose"]}')
            
            self.stdout.write('\n\n📝 To create these indexes:')
            self.stdout.write('   Option 1: Firebase Console → Firestore → Indexes → Create Index')
            self.stdout.write('   Option 2: Use gcloud CLI (see firestore_indexes.json)')
            
            # Generate firestore index configuration
            self.stdout.write('\n\n💾 Generating firestore_indexes.json...')
            
            index_config = {
                'indexes': []
            }
            
            for index_def in composite_indexes:
                fields_config = []
                for field_name, order in index_def['fields']:
                    fields_config.append({'fieldPath': field_name, 'order': order})
                
                index_config['indexes'].append({
                    'collectionGroup': index_def['collection'],
                    'queryScope': 'COLLECTION',
                    'fields': fields_config
                })
            
            import json
            import os
from django.conf import settings
            
            config_path = os.path.join(settings.BASE_DIR, 'firestore_indexes.json')
            with open(config_path, 'w') as f:
                json.dump(index_config, f, indent=2)
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Created {config_path}'))
            self.stdout.write('\n  Deploy with: gcloud firestore indexes create firestore_indexes.json')
            
            self.stdout.write(self.style.SUCCESS('\n\n✅ Index setup information generated successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error: {str(e)}'))
            logger.error(f'Index creation error: {str(e)}', exc_info=True)
