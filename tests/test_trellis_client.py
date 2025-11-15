"""
Tests for Trellis API Client - Integration tests
"""

import pytest
from trellis_mcp.trellis_client import TrellisClient


def test_get_entities_success():
    """Test that get_entities returns a successful response from the real API."""
    # Create client (will use env vars from .env file)
    client = TrellisClient()
    
    # Call the real API
    result = client.get_entities()
    
    # Assert we got a successful response with entities
    assert result is not None
