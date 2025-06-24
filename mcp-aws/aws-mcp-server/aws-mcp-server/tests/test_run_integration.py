"""Simple test to verify integration test setup."""

import pytest


@pytest.mark.integration
def test_integration_marker_works():
    """Test that tests with integration marker run."""
    print("Integration test is running!")
    assert True
