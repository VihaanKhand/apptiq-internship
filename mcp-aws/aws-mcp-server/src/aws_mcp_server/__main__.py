"""Main entry point for the AWS MCP Server.

This module provides the entry point for running the AWS MCP Server.
FastMCP handles the command-line arguments and server configuration.
"""

import logging
import signal
import sys

from aws_mcp_server.server import logger, mcp

# Configure root logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler(sys.stderr)])


def handle_interrupt(signum, frame):
    """Handle keyboard interrupt (Ctrl+C) gracefully."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


# Using FastMCP's built-in CLI handling
if __name__ == "__main__":
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, handle_interrupt)
    signal.signal(signal.SIGTERM, handle_interrupt)

    try:
        # Use configured transport protocol
        from aws_mcp_server.config import TRANSPORT

        # Validate transport protocol
        if TRANSPORT not in ("stdio", "sse"):
            logger.error(f"Invalid transport protocol: {TRANSPORT}. Must be 'stdio' or 'sse'")
            sys.exit(1)

        # Run with the specified transport protocol
        logger.info(f"Starting server with transport protocol: {TRANSPORT}")
        mcp.run(transport=TRANSPORT)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down gracefully...")
        sys.exit(0)
