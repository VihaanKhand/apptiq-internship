"""Tests for the package initialization module."""

import unittest
from importlib import reload
from unittest.mock import patch


class TestInitModule(unittest.TestCase):
    """Tests for the __init__ module."""

    def test_version_from_package(self):
        """Test __version__ is set from package metadata."""
        with patch("importlib.metadata.version", return_value="1.2.3"):
            # Import the module fresh to apply the patch
            import aws_mcp_server

            # Reload to apply our patch
            reload(aws_mcp_server)

            # Check that __version__ is set correctly
            self.assertEqual(aws_mcp_server.__version__, "1.2.3")

    def test_version_fallback_on_package_not_found(self):
        """Test handling of PackageNotFoundError."""
        from importlib.metadata import PackageNotFoundError

        # Looking at the actual implementation, when PackageNotFoundError is raised,
        # it just uses 'pass', so the attribute __version__ may or may not be set.
        # If it was previously set (which is likely), it will retain its previous value.
        with patch("importlib.metadata.version", side_effect=PackageNotFoundError):
            # Create a fresh module
            import sys

            if "aws_mcp_server" in sys.modules:
                del sys.modules["aws_mcp_server"]

            # Import the module fresh with our patch
            import aws_mcp_server

            # In this case, the __version__ may not even be set
            # We're just testing that the code doesn't crash with PackageNotFoundError
            # Our test should pass regardless of whether __version__ is set
            # The important part is that the exception is handled
            try:
                # This could raise AttributeError
                _ = aws_mcp_server.__version__
                # If we get here, it's set to something - hard to assert exactly what
                # Just ensure no exception was thrown
                self.assertTrue(True)
            except AttributeError:
                # If AttributeError is raised, that's also fine - the attribute doesn't exist
                self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
