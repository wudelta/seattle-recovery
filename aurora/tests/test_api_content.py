# ======================================================================
# FILE: aurora/tests/test_api_content.py (PATCH 1 OF 1)
# START: CONTENT_ENDPOINT_TWIN_TRACK_SUITE
# ======================================================================
import json
import unittest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from django.contrib.auth.models import User
from aurora.api.content_api import content_endpoint

class StaticContentAPIIsolatedUnitTest(unittest.TestCase):
    """Executes database-free functional verification for the Content API logic layer."""

    def setUp(self):
        # Using RequestFactory completely skips Django's HTTP middleware and database engine loops
        self.factory = RequestFactory()

    @patch('aurora.models.StaticContent.objects.all')
    def test_empty_inventory_retrieval_authenticated(self, mock_all):
        """Verifies authenticated requests fetch a structured inventory dictionary successfully."""
        # Arrange: Setup mocked user session context properties
        mock_user = MagicMock(spec=User)
        mock_user.is_authenticated = True
        mock_user.username = "dev_tester"

        mock_query = MagicMock()
        mock_query.order_by.return_value = []
        mock_all.return_value = mock_query

        # Build request envelope without firing the test runner's DB syncer
        request = self.factory.get('/aurora/api/content-panel/', {'application': 'all'})
        request.user = mock_user
        request.method = 'GET'

        # Act: Pass request target directly to your endpoint function view
        response = content_endpoint(request)

        # Assert: Verify json contract structures match specifications
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'SUCCESS')
        self.assertEqual(data['inventory'], [])
# ======================================================================
# END: CONTENT_ENDPOINT_TWIN_TRACK_SUITE (PATCH 1 OF 1)
# ======================================================================
