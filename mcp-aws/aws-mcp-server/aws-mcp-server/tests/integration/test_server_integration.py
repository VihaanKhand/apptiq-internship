"""Mocked integration tests for AWS MCP Server functionality.

These tests use mocks rather than actual AWS CLI calls, so they can
run without AWS credentials or AWS CLI installed.
"""

import json
import logging
import os
from unittest.mock import patch

import pytest

from aws_mcp_server.server import aws_cli_help, aws_cli_pipeline, mcp

# Enable debug logging for tests
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def mock_aws_environment():
    """Set up mock AWS environment variables for testing."""
    original_env = os.environ.copy()
    os.environ["AWS_PROFILE"] = "test-profile"
    os.environ["AWS_REGION"] = "us-west-2"
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mcp_client():
    """Return a FastMCP client for testing."""
    return mcp


class TestServerIntegration:
    """Integration tests for the AWS MCP Server using mocks.

    These tests use mocks and don't actually call AWS, but they test
    more of the system together than unit tests. They don't require the
    integration marker since they can run without AWS CLI or credentials."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "service,command,mock_response,expected_content",
        [
            # Basic service help
            ("s3", None, {"help_text": "AWS S3 HELP\nCommands:\ncp\nls\nmv\nrm\nsync"}, ["AWS S3 HELP", "Commands", "ls", "sync"]),
            # Command-specific help
            (
                "ec2",
                "describe-instances",
                {"help_text": "DESCRIPTION\n  Describes the specified instances.\n\nSYNOPSIS\n  describe-instances\n  [--instance-ids <value>]"},
                ["DESCRIPTION", "SYNOPSIS", "instance-ids"],
            ),
            # Help for a different service
            ("lambda", "list-functions", {"help_text": "LAMBDA LIST-FUNCTIONS\nLists your Lambda functions"}, ["LAMBDA", "LIST-FUNCTIONS", "Lists"]),
        ],
    )
    @patch("aws_mcp_server.server.get_command_help")
    async def test_aws_cli_help_integration(self, mock_get_help, mock_aws_environment, service, command, mock_response, expected_content):
        """Test the aws_cli_help functionality with table-driven tests."""
        # Configure the mock response
        mock_get_help.return_value = mock_response

        # Call the aws_cli_help function
        result = await aws_cli_help(service=service, command=command, ctx=None)

        # Verify the results
        assert "help_text" in result
        for content in expected_content:
            assert content in result["help_text"], f"Expected '{content}' in help text"

        # Verify the mock was called correctly
        mock_get_help.assert_called_once_with(service, command)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "command,mock_response,expected_result,timeout",
        [
            # JSON output test
            (
                "aws s3 ls --output json",
                {"status": "success", "output": json.dumps({"Buckets": [{"Name": "test-bucket", "CreationDate": "2023-01-01T00:00:00Z"}]})},
                {"status": "success", "contains": ["Buckets", "test-bucket"]},
                None,
            ),
            # Text output test
            (
                "aws ec2 describe-instances --query 'Reservations[*]' --output text",
                {"status": "success", "output": "i-12345\trunning\tt2.micro"},
                {"status": "success", "contains": ["i-12345", "running"]},
                None,
            ),
            # Test with custom timeout
            ("aws rds describe-db-instances", {"status": "success", "output": "DB instances list"}, {"status": "success", "contains": ["DB instances"]}, 60),
            # Error case
            (
                "aws s3 ls --invalid-flag",
                {"status": "error", "output": "Unknown options: --invalid-flag"},
                {"status": "error", "contains": ["--invalid-flag"]},
                None,
            ),
            # Piped command
            (
                "aws s3api list-buckets --query 'Buckets[*].Name' --output text | sort",
                {"status": "success", "output": "bucket1\nbucket2\nbucket3"},
                {"status": "success", "contains": ["bucket1", "bucket3"]},
                None,
            ),
        ],
    )
    @patch("aws_mcp_server.server.execute_aws_command")
    async def test_aws_cli_pipeline_scenarios(self, mock_execute, mock_aws_environment, command, mock_response, expected_result, timeout):
        """Test aws_cli_pipeline with various scenarios using table-driven tests."""
        # Configure the mock response
        mock_execute.return_value = mock_response

        # Call the aws_cli_pipeline function
        result = await aws_cli_pipeline(command=command, timeout=timeout, ctx=None)

        # Verify status
        assert result["status"] == expected_result["status"]

        # Verify expected content is present
        for content in expected_result["contains"]:
            assert content in result["output"], f"Expected '{content}' in output"

        # Verify the mock was called correctly
        mock_execute.assert_called_once_with(command, timeout)

    @pytest.mark.asyncio
    @patch("aws_mcp_server.resources.get_aws_profiles")
    @patch("aws_mcp_server.resources.get_aws_regions")
    @patch("aws_mcp_server.resources.get_aws_environment")
    @patch("aws_mcp_server.resources.get_aws_account_info")
    async def test_mcp_resources_access(
        self, mock_get_aws_account_info, mock_get_aws_environment, mock_get_aws_regions, mock_get_aws_profiles, mock_aws_environment, mcp_client
    ):
        """Test that MCP resources are properly registered and accessible to clients."""
        # Set up mock return values
        mock_get_aws_profiles.return_value = ["default", "test-profile", "dev"]
        mock_get_aws_regions.return_value = [
            {"RegionName": "us-east-1", "RegionDescription": "US East (N. Virginia)"},
            {"RegionName": "us-west-2", "RegionDescription": "US West (Oregon)"},
        ]
        mock_get_aws_environment.return_value = {
            "aws_profile": "test-profile",
            "aws_region": "us-west-2",
            "has_credentials": True,
            "credentials_source": "profile",
        }
        mock_get_aws_account_info.return_value = {
            "account_id": "123456789012",
            "account_alias": "test-account",
            "organization_id": "o-abcdef123456",
        }

        # Define the expected resource URIs
        expected_resources = ["aws://config/profiles", "aws://config/regions", "aws://config/environment", "aws://config/account"]

        # Test that resources are accessible through MCP client
        resources = await mcp_client.list_resources()

        # Verify all expected resources are present
        resource_uris = [str(r.uri) for r in resources]
        for uri in expected_resources:
            assert uri in resource_uris, f"Resource {uri} not found in resources list"

        # Test accessing each resource by URI
        for uri in expected_resources:
            resource = await mcp_client.read_resource(uri=uri)
            assert resource is not None, f"Failed to read resource {uri}"

            # Resource is a list with one item that has a content attribute
            # The content is a JSON string that needs to be parsed
            import json

            content = json.loads(resource[0].content)

            # Verify specific resource content
            if uri == "aws://config/profiles":
                assert "profiles" in content
                assert len(content["profiles"]) == 3
                assert any(p["name"] == "test-profile" and p["is_current"] for p in content["profiles"])

            elif uri == "aws://config/regions":
                assert "regions" in content
                assert len(content["regions"]) == 2
                assert any(r["name"] == "us-west-2" and r["is_current"] for r in content["regions"])

            elif uri == "aws://config/environment":
                assert content["aws_profile"] == "test-profile"
                assert content["aws_region"] == "us-west-2"
                assert content["has_credentials"] is True

            elif uri == "aws://config/account":
                assert content["account_id"] == "123456789012"
                assert content["account_alias"] == "test-account"
