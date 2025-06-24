"""Integration tests for security rules in AWS MCP Server.

These tests verify that security rules properly prevent dangerous commands
while allowing safe operations.
"""

import pytest

from aws_mcp_server.server import aws_cli_pipeline


class TestSecurityIntegration:
    """Integration tests for security system.

    These tests validate that:
    1. Safe operations are allowed
    2. Dangerous operations are blocked
    3. Pipe commands are properly validated
    """

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.parametrize(
        "command,should_succeed,expected_message",
        [
            # Safe operations that should succeed
            ("aws s3 ls", True, None),
            ("aws ec2 describe-instances", True, None),
            ("aws iam list-users", True, None),
            # Dangerous IAM operations that should be blocked
            (
                "aws iam create-user --user-name test-user-12345",
                False,
                "restricted for security reasons",
            ),
            (
                "aws iam create-access-key --user-name admin",
                False,
                "restricted for security reasons",
            ),
            # Dangerous CloudTrail operations (good for testing as they're security-related but not destructive)
            (
                "aws cloudtrail delete-trail --name test-trail",
                False,
                "restricted for security reasons",
            ),
            # Complex regex pattern tests
            (
                "aws iam create-user --user-name admin-user12345",
                False,
                "Creating users with sensitive names",
            ),
            (
                "aws ec2 authorize-security-group-ingress --group-id sg-12345 --protocol tcp --port 22 --cidr 0.0.0.0/0",
                False,
                "restricted for security reasons",
            ),
            # Commands with safe overrides
            (
                "aws iam create-user --help",
                True,
                None,
            ),
            (
                "aws ec2 describe-security-groups",
                True,
                None,
            ),
        ],
    )
    async def test_security_rules(self, ensure_aws_credentials, command, should_succeed, expected_message):
        """Test that security rules block dangerous commands and allow safe operations.

        This test verifies each command against security rules without actually executing them
        against AWS services.
        """
        # Execute the command
        result = await aws_cli_pipeline(command=command, timeout=None, ctx=None)

        if should_succeed:
            if result["status"] != "success":
                # If command would succeed but API returns error (e.g., invalid resource),
                # we still want to verify it wasn't blocked by security rules
                assert "restricted for security reasons" not in result["output"], f"Command should pass security validation but was blocked: {result['output']}"
                assert "Command validation error" not in result["output"], f"Command should pass security validation but failed validation: {result['output']}"
            else:
                assert result["status"] == "success", f"Command should succeed but failed: {result['output']}"
        else:
            assert result["status"] == "error", f"Command should fail but succeeded: {result['output']}"
            assert expected_message in result["output"], f"Expected error message '{expected_message}' not found in: {result['output']}"

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.parametrize(
        "command,should_succeed,expected_message",
        [
            # Safe pipe commands
            (
                "aws ec2 describe-regions --output text | grep us-east",
                True,
                None,
            ),
            (
                "aws s3 ls | grep bucket | wc -l",
                True,
                None,
            ),
            # Dangerous first command
            (
                "aws iam create-user --user-name test-user-12345 | grep test",
                False,
                "restricted for security reasons",
            ),
            # Unsafe pipe command
            (
                "aws s3 ls | sudo",  # sudo shouldn't be allowed in the allowed unix command list
                False,
                "not allowed",
            ),
            # Complex pipe chain
            (
                "aws ec2 describe-regions --output json | grep RegionName | head -5 | sort",
                True,
                None,
            ),
        ],
    )
    async def test_piped_command_security(self, ensure_aws_credentials, command, should_succeed, expected_message):
        """Test that security rules properly validate piped commands."""
        result = await aws_cli_pipeline(command=command, timeout=None, ctx=None)

        if should_succeed:
            if result["status"] != "success":
                # If command should be allowed but failed for other reasons,
                # verify it wasn't blocked by security rules
                assert "restricted for security reasons" not in result["output"], f"Command should pass security validation but was blocked: {result['output']}"
                assert "not allowed" not in result["output"], f"Command should pass security validation but was blocked: {result['output']}"
        else:
            assert result["status"] == "error", f"Command should fail but succeeded: {result['output']}"
            assert expected_message in result["output"], f"Expected error message '{expected_message}' not found in: {result['output']}"
