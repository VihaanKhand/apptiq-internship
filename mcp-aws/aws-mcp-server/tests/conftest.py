"""Configuration for pytest."""

import os

import pytest


def pytest_addoption(parser):
    """Add command-line options to pytest."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests that require AWS CLI and AWS account",
    )


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: mark test as requiring AWS CLI and AWS account")


def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless --run-integration is specified."""
    print(f"Run integration flag: {config.getoption('--run-integration')}")

    if config.getoption("--run-integration"):
        # Run all tests
        print("Integration tests will be run")
        return

    skip_integration = pytest.mark.skip(reason="Integration tests need --run-integration option")
    print(f"Will check {len(items)} items for integration markers")

    for item in items:
        print(f"Test: {item.name}, keywords: {list(item.keywords)}")
        if "integration" in item.keywords:
            print(f"Skipping integration test: {item.name}")
            item.add_marker(skip_integration)


@pytest.fixture(scope="function")
async def aws_s3_bucket(ensure_aws_credentials):
    """Create or use an S3 bucket for integration tests.

    Uses AWS_TEST_BUCKET if specified, otherwise creates a temporary bucket
    and cleans it up after tests complete.
    """
    import asyncio
    import time
    import uuid

    from aws_mcp_server.server import aws_cli_pipeline

    print("AWS S3 bucket fixture called")

    # Use specified bucket or create a dynamically named one
    bucket_name = os.environ.get("AWS_TEST_BUCKET")
    bucket_created = False

    # Get region from environment or use configured default
    region = os.environ.get("AWS_TEST_REGION", os.environ.get("AWS_REGION", "us-east-1"))
    print(f"Using AWS region: {region}")

    print(f"Using bucket name: {bucket_name or 'Will create dynamic bucket'}")

    if not bucket_name:
        # Generate a unique bucket name with timestamp and random id
        timestamp = int(time.time())
        random_id = str(uuid.uuid4())[:8]
        bucket_name = f"aws-mcp-test-{timestamp}-{random_id}"
        print(f"Generated bucket name: {bucket_name}")

        # Create the bucket with region specified
        create_cmd = f"aws s3 mb s3://{bucket_name} --region {region}"
        print(f"Creating bucket with command: {create_cmd}")
        result = await aws_cli_pipeline(command=create_cmd, timeout=None, ctx=None)
        if result["status"] != "success":
            print(f"Failed to create bucket: {result['output']}")
            pytest.skip(f"Failed to create test bucket: {result['output']}")
        bucket_created = True
        print("Bucket created successfully")
        # Wait a moment for bucket to be fully available
        await asyncio.sleep(3)

    # Yield the bucket name for tests to use
    print(f"Yielding bucket name: {bucket_name}")
    yield bucket_name

    # Clean up the bucket if we created it
    if bucket_created:
        print(f"Cleaning up bucket: {bucket_name}")
        try:
            # First remove all objects
            print("Removing objects from bucket")
            await aws_cli_pipeline(command=f"aws s3 rm s3://{bucket_name} --recursive --region {region}", timeout=None, ctx=None)
            # Then delete the bucket
            print("Deleting bucket")
            await aws_cli_pipeline(command=f"aws s3 rb s3://{bucket_name} --region {region}", timeout=None, ctx=None)
            print("Bucket cleanup complete")
        except Exception as e:
            print(f"Warning: Error cleaning up test bucket: {e}")


@pytest.fixture
def ensure_aws_credentials():
    """Ensure AWS credentials are configured and AWS CLI is installed."""
    import subprocess

    print("Checking AWS credentials and CLI")

    # Check for AWS CLI installation
    try:
        result = subprocess.run(["aws", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        print(f"AWS CLI check: {result.returncode == 0}")
        if result.returncode != 0:
            print(f"AWS CLI not found: {result.stderr.decode('utf-8')}")
            pytest.skip("AWS CLI not installed or not in PATH")
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"AWS CLI check error: {str(e)}")
        pytest.skip("AWS CLI not installed or not in PATH")

    # Check for AWS credentials - simplified check
    home_dir = os.path.expanduser("~")
    creds_file = os.path.join(home_dir, ".aws", "credentials")
    config_file = os.path.join(home_dir, ".aws", "config")

    has_creds = os.path.exists(creds_file)
    has_config = os.path.exists(config_file)
    print(f"AWS files: credentials={has_creds}, config={has_config}")
    # Don't skip based on file presence - let the get-caller-identity check decide

    # Verify AWS credentials work by making a simple call
    try:
        result = subprocess.run(["aws", "sts", "get-caller-identity"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, check=False)
        print(f"AWS auth check: {result.returncode == 0}")
        if result.returncode != 0:
            error_msg = result.stderr.decode("utf-8")
            print(f"AWS auth failed: {error_msg}")
            pytest.skip(f"AWS credentials not valid: {error_msg}")
        else:
            print(f"AWS identity: {result.stdout.decode('utf-8')}")
    except subprocess.SubprocessError as e:
        print(f"AWS auth check error: {str(e)}")
        pytest.skip("Failed to verify AWS credentials")

    # All checks passed - AWS CLI and credentials are working
    print("AWS credentials verification successful")
    return True
