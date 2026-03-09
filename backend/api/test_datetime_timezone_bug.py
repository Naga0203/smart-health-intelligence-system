"""
Property-Based Tests for Datetime Timezone Bug

This test file contains bug condition exploration tests for the datetime timezone
mismatch bug in the UserStatisticsAPIView endpoint.

**Validates: Requirements 1.1, 1.2**

Bug Context:
- The /api/user/statistics/ endpoint crashes with TypeError when calculating account age
- Root cause: datetime.utcnow() (timezone-naive) - created_at (timezone-aware from Firestore)
- Location: Line 1568 in backend/api/views.py

Properties Tested:
- Property 1: Bug Condition - Timezone-Aware Datetime Arithmetic
  CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists
  When run on FIXED code, this test will pass and validate the fix
"""

import pytest
pytestmark = pytest.mark.pbt

from datetime import datetime, timezone, timedelta
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, patch, MagicMock
from django.test import RequestFactory
from rest_framework.test import force_authenticate

# Import the view we're testing
from api.views import UserStatisticsAPIView


# ============================================================================
# Hypothesis Strategies for Generating Test Data
# ============================================================================

# Strategy for generating timezone-aware datetimes (simulating Firestore timestamps)
# Generate datetimes within the last 10 years
# Note: Hypothesis requires naive datetimes, we'll add timezone info in the test
timezone_aware_datetime_strategy = st.datetimes(
    min_value=datetime(2015, 1, 1),
    max_value=datetime(2025, 12, 31)
).map(lambda dt: dt.replace(tzinfo=timezone.utc))


# ============================================================================
# Property 1: Bug Condition - Timezone-Aware Datetime Arithmetic
# **Validates: Requirements 1.1, 1.2**
# ============================================================================

@pytest.mark.pbt
@given(created_at=timezone_aware_datetime_strategy)
@settings(max_examples=50, deadline=None)
def test_property_timezone_aware_datetime_subtraction(created_at):
    """
    Property 1: Bug Condition - Timezone-Aware Datetime Arithmetic
    
    **Validates: Requirements 1.1, 1.2**
    
    CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists
    
    Property: When calculating account age with timezone-aware created_at datetime,
    the system SHALL successfully compute the difference without raising TypeError.
    
    Bug Condition: datetime.utcnow() - created_at raises TypeError when created_at
    is timezone-aware (from Firestore).
    
    Expected Behavior: Timezone-aware datetime arithmetic completes without TypeError.
    
    Test Strategy:
    - Generate timezone-aware created_at datetimes (simulating Firestore data)
    - Mock Firestore to return user data with timezone-aware created_at
    - Call the UserStatisticsAPIView endpoint
    - Verify the response succeeds without TypeError
    - Verify account_age_days is calculated correctly
    
    EXPECTED OUTCOME ON UNFIXED CODE: Test FAILS with TypeError
    EXPECTED OUTCOME ON FIXED CODE: Test PASSES
    """
    # Ensure created_at is in the past (account age should be positive)
    assume(created_at < datetime.now(timezone.utc))
    
    # Setup mocks
    factory = RequestFactory()
    request = factory.get('/api/user/statistics/')
    
    # Mock authenticated user
    mock_user = Mock()
    mock_user.uid = 'test_user_123'
    request.user = mock_user
    
    # Mock Firestore database
    with patch('common.firebase_db.get_firebase_db') as mock_get_db:
        # Setup mock database structure
        mock_db = MagicMock()
        mock_get_db.return_value.db = mock_db
        
        # Mock user document with timezone-aware created_at
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'created_at': created_at,  # Timezone-aware datetime from Firestore
            'email': 'test@example.com'
        }
        
        # Mock assessments collection (empty for simplicity)
        mock_assessments_ref = MagicMock()
        mock_assessments_ref.stream.return_value = []
        
        # Wire up the mocks
        mock_db.collection.return_value.document.return_value.get.return_value = mock_user_doc
        mock_db.collection.return_value.where.return_value = mock_assessments_ref
        
        # Create view and call it
        view = UserStatisticsAPIView()
        
        # CRITICAL: This call will raise TypeError on unfixed code
        # because datetime.utcnow() (naive) - created_at (aware) is invalid
        response = view.get(request)
        
        # Assertions - verify expected behavior
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        
        data = response.data
        assert 'account_age_days' in data, "Response should contain account_age_days"
        
        # Verify account_age_days is calculated correctly
        # Calculate expected age using timezone-aware arithmetic
        now_aware = datetime.now(timezone.utc)
        expected_age_days = (now_aware - created_at).days
        
        actual_age_days = data['account_age_days']
        
        # Allow for small differences due to timing (test execution time)
        assert abs(actual_age_days - expected_age_days) <= 1, \
            f"Account age mismatch: expected ~{expected_age_days} days, got {actual_age_days} days"
        
        # Verify other fields are present (basic structure check)
        assert 'total_assessments' in data
        assert 'assessments_by_confidence' in data
        assert 'most_common_diseases' in data
        assert 'last_assessment_date' in data


# ============================================================================
# Property 2: Preservation - Non-Created-At Statistics Behavior
# **Validates: Requirements 3.1, 3.2, 3.3**
# ============================================================================

@pytest.mark.pbt
def test_property_preservation_no_created_at():
    """
    Property 2: Preservation - Users Without created_at Get account_age_days=0
    
    **Validates: Requirement 3.1**
    
    IMPORTANT: This is a preservation test - runs on UNFIXED code
    
    Property: When a user has no created_at timestamp, the system SHALL
    return account_age_days=0 and not crash.
    
    This behavior must be preserved after the fix.
    
    Test Strategy:
    - Mock Firestore to return user data WITHOUT created_at field
    - Call the UserStatisticsAPIView endpoint
    - Verify account_age_days is 0
    - Verify response succeeds without errors
    
    EXPECTED OUTCOME: Test PASSES on unfixed code (confirms baseline behavior)
    """
    # Setup mocks
    factory = RequestFactory()
    request = factory.get('/api/user/statistics/')
    
    # Mock authenticated user
    mock_user = Mock()
    mock_user.uid = 'test_user_no_created_at'
    request.user = mock_user
    
    # Mock Firestore database
    with patch('common.firebase_db.get_firebase_db') as mock_get_db:
        # Setup mock database structure
        mock_db = MagicMock()
        mock_get_db.return_value.db = mock_db
        
        # Mock user document WITHOUT created_at field
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'email': 'test@example.com'
            # Note: No 'created_at' field
        }
        
        # Mock assessments collection (empty)
        mock_assessments_ref = MagicMock()
        mock_assessments_ref.stream.return_value = []
        
        # Wire up the mocks
        mock_db.collection.return_value.document.return_value.get.return_value = mock_user_doc
        mock_db.collection.return_value.where.return_value = mock_assessments_ref
        
        # Create view and call it
        view = UserStatisticsAPIView()
        response = view.get(request)
        
        # Assertions - verify preservation behavior
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        
        data = response.data
        assert 'account_age_days' in data, "Response should contain account_age_days"
        assert data['account_age_days'] == 0, \
            f"Expected account_age_days=0 for user without created_at, got {data['account_age_days']}"
        
        # Verify response structure is preserved
        assert 'total_assessments' in data
        assert 'assessments_by_confidence' in data
        assert 'most_common_diseases' in data
        assert 'last_assessment_date' in data


# Strategy for generating assessment data
assessment_data_strategy = st.fixed_dictionaries({
    'confidence': st.sampled_from(['LOW', 'MEDIUM', 'HIGH']),
    'disease': st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=65, max_codepoint=122)),
    'created_at': st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2025, 12, 31)
    ).map(lambda dt: dt.replace(tzinfo=timezone.utc))
})


@pytest.mark.pbt
@given(assessments=st.lists(assessment_data_strategy, min_size=0, max_size=20))
@settings(max_examples=50, deadline=None)
def test_property_preservation_statistics_calculation(assessments):
    """
    Property 2: Preservation - Other Statistics Compute Correctly
    
    **Validates: Requirements 3.2, 3.3**
    
    IMPORTANT: This is a preservation test - runs on UNFIXED code
    
    Property: The system SHALL correctly compute statistics for:
    - total_assessments: Count of all assessments
    - assessments_by_confidence: Count by confidence level (LOW, MEDIUM, HIGH)
    - most_common_diseases: Top 5 diseases by count
    - last_assessment_date: Most recent assessment timestamp
    - Response structure: All expected fields present
    
    This behavior must be preserved after the fix.
    
    Test Strategy:
    - Generate random assessment data with various confidence levels and diseases
    - Mock Firestore to return this assessment data
    - Mock user WITHOUT created_at to avoid triggering the bug
    - Call the UserStatisticsAPIView endpoint
    - Verify all statistics are calculated correctly
    - Verify response structure is complete
    
    EXPECTED OUTCOME: Test PASSES on unfixed code (confirms baseline behavior)
    """
    # Setup mocks
    factory = RequestFactory()
    request = factory.get('/api/user/statistics/')
    
    # Mock authenticated user
    mock_user = Mock()
    mock_user.uid = 'test_user_stats'
    request.user = mock_user
    
    # Mock Firestore database
    with patch('common.firebase_db.get_firebase_db') as mock_get_db:
        # Setup mock database structure
        mock_db = MagicMock()
        mock_get_db.return_value.db = mock_db
        
        # Mock user document WITHOUT created_at to avoid triggering the bug
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'email': 'test@example.com'
            # No created_at - avoids the bug
        }
        
        # Mock assessment documents
        mock_assessment_docs = []
        for assessment_data in assessments:
            mock_doc = MagicMock()
            mock_doc.to_dict.return_value = assessment_data
            mock_assessment_docs.append(mock_doc)
        
        mock_assessments_ref = MagicMock()
        mock_assessments_ref.stream.return_value = mock_assessment_docs
        
        # Wire up the mocks
        mock_db.collection.return_value.document.return_value.get.return_value = mock_user_doc
        mock_db.collection.return_value.where.return_value = mock_assessments_ref
        
        # Create view and call it
        view = UserStatisticsAPIView()
        response = view.get(request)
        
        # Assertions - verify preservation behavior
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        
        data = response.data
        
        # Verify response structure (Requirement 3.3)
        assert 'total_assessments' in data, "Response should contain total_assessments"
        assert 'assessments_by_confidence' in data, "Response should contain assessments_by_confidence"
        assert 'most_common_diseases' in data, "Response should contain most_common_diseases"
        assert 'last_assessment_date' in data, "Response should contain last_assessment_date"
        assert 'account_age_days' in data, "Response should contain account_age_days"
        
        # Verify total_assessments (Requirement 3.2)
        expected_total = len(assessments)
        assert data['total_assessments'] == expected_total, \
            f"Expected total_assessments={expected_total}, got {data['total_assessments']}"
        
        # Verify assessments_by_confidence (Requirement 3.2)
        expected_confidence_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}
        for assessment in assessments:
            confidence = assessment.get('confidence', 'LOW')
            expected_confidence_counts[confidence] = expected_confidence_counts.get(confidence, 0) + 1
        
        actual_confidence_counts = data['assessments_by_confidence']
        for confidence_level in ['LOW', 'MEDIUM', 'HIGH']:
            expected_count = expected_confidence_counts[confidence_level]
            actual_count = actual_confidence_counts.get(confidence_level, 0)
            assert actual_count == expected_count, \
                f"Expected {confidence_level} count={expected_count}, got {actual_count}"
        
        # Verify most_common_diseases (Requirement 3.2)
        expected_disease_counts = {}
        for assessment in assessments:
            disease = assessment.get('disease', 'Unknown')
            expected_disease_counts[disease] = expected_disease_counts.get(disease, 0) + 1
        
        expected_most_common = sorted(
            [{'disease': d, 'count': c} for d, c in expected_disease_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:5]
        
        actual_most_common = data['most_common_diseases']
        assert len(actual_most_common) == len(expected_most_common), \
            f"Expected {len(expected_most_common)} diseases, got {len(actual_most_common)}"
        
        for expected, actual in zip(expected_most_common, actual_most_common):
            assert actual['disease'] == expected['disease'], \
                f"Disease mismatch: expected {expected['disease']}, got {actual['disease']}"
            assert actual['count'] == expected['count'], \
                f"Count mismatch for {expected['disease']}: expected {expected['count']}, got {actual['count']}"
        
        # Verify last_assessment_date (Requirement 3.2)
        if assessments:
            expected_last_date = max(a['created_at'] for a in assessments)
            actual_last_date = data['last_assessment_date']
            assert actual_last_date == expected_last_date, \
                f"Expected last_assessment_date={expected_last_date}, got {actual_last_date}"
        else:
            assert data['last_assessment_date'] is None, \
                f"Expected last_assessment_date=None for no assessments, got {data['last_assessment_date']}"
        
        # Verify account_age_days is 0 (no created_at)
        assert data['account_age_days'] == 0, \
            f"Expected account_age_days=0, got {data['account_age_days']}"
