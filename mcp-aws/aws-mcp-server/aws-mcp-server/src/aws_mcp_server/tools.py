"""Command execution utilities for AWS MCP Server.

This module provides utilities for validating and executing commands, including:
- AWS CLI commands
- Basic Unix commands
- Command pipes (piping output from one command to another)
"""

import asyncio
import logging
import shlex
from typing import List, TypedDict

from aws_mcp_server.config import DEFAULT_TIMEOUT, MAX_OUTPUT_SIZE

# Configure module logger
logger = logging.getLogger(__name__)

# List of allowed Unix commands that can be used in a pipe
ALLOWED_UNIX_COMMANDS = [
    # File operations
    "cat",
    "ls",
    "cd",
    "pwd",
    "cp",
    "mv",
    "rm",
    "mkdir",
    "touch",
    "chmod",
    "chown",
    # Text processing
    "grep",
    "sed",
    "awk",
    "cut",
    "sort",
    "uniq",
    "wc",
    "head",
    "tail",
    "tr",
    "find",
    # System information
    "ps",
    "top",
    "df",
    "du",
    "uname",
    "whoami",
    "date",
    "which",
    "echo",
    # Networking
    "ping",
    "ifconfig",
    "netstat",
    "curl",
    "wget",
    "dig",
    "nslookup",
    "ssh",
    "scp",
    # Other utilities
    "man",
    "less",
    "tar",
    "gzip",
    "gunzip",
    "zip",
    "unzip",
    "xargs",
    "jq",
    "tee",
]


class CommandResult(TypedDict):
    """Type definition for command execution results."""

    status: str
    output: str


def validate_unix_command(command: str) -> bool:
    """Validate that a command is an allowed Unix command.

    Args:
        command: The Unix command to validate

    Returns:
        True if the command is valid, False otherwise
    """
    cmd_parts = shlex.split(command)
    if not cmd_parts:
        return False

    # Check if the command is in the allowed list
    return cmd_parts[0] in ALLOWED_UNIX_COMMANDS


def is_pipe_command(command: str) -> bool:
    """Check if a command contains a pipe operator.

    Args:
        command: The command to check

    Returns:
        True if the command contains a pipe operator, False otherwise
    """
    # Check for pipe operator that's not inside quotes
    in_single_quote = False
    in_double_quote = False
    escaped = False

    for _, char in enumerate(command):
        # Handle escape sequences
        if char == "\\" and not escaped:
            escaped = True
            continue

        if not escaped:
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
            elif char == "|" and not in_single_quote and not in_double_quote:
                return True

        escaped = False

    return False


def split_pipe_command(pipe_command: str) -> List[str]:
    """Split a piped command into individual commands.

    Args:
        pipe_command: The piped command string

    Returns:
        List of individual command strings
    """
    commands = []
    current_command = ""
    in_single_quote = False
    in_double_quote = False
    escaped = False

    for _, char in enumerate(pipe_command):
        # Handle escape sequences
        if char == "\\" and not escaped:
            escaped = True
            current_command += char
            continue

        if not escaped:
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                current_command += char
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                current_command += char
            elif char == "|" and not in_single_quote and not in_double_quote:
                commands.append(current_command.strip())
                current_command = ""
            else:
                current_command += char
        else:
            # Add the escaped character
            current_command += char
            escaped = False

    if current_command.strip():
        commands.append(current_command.strip())

    return commands


async def execute_piped_command(pipe_command: str, timeout: int | None = None) -> CommandResult:
    """Execute a command that contains pipes.

    Args:
        pipe_command: The piped command to execute
        timeout: Optional timeout in seconds (defaults to DEFAULT_TIMEOUT)

    Returns:
        CommandResult containing output and status
    """
    # Set timeout
    if timeout is None:
        timeout = DEFAULT_TIMEOUT

    logger.debug(f"Executing piped command: {pipe_command}")

    try:
        # Split the pipe_command into individual commands
        commands = split_pipe_command(pipe_command)

        # For each command, split it into command parts for subprocess_exec
        command_parts_list = [shlex.split(cmd) for cmd in commands]

        if len(commands) == 0:
            return CommandResult(status="error", output="Empty command")

        # Execute the first command
        first_cmd = command_parts_list[0]
        first_process = await asyncio.create_subprocess_exec(*first_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        current_process = first_process
        current_stdout = None
        current_stderr = None

        # For each additional command in the pipe, execute it with the previous command's output
        for cmd_parts in command_parts_list[1:]:
            try:
                # Wait for the previous command to complete with timeout
                current_stdout, current_stderr = await asyncio.wait_for(current_process.communicate(), timeout)

                if current_process.returncode != 0:
                    # If previous command failed, stop the pipe execution
                    stderr_str = current_stderr.decode("utf-8", errors="replace")
                    logger.warning(f"Piped command failed with return code {current_process.returncode}: {pipe_command}")
                    logger.debug(f"Command error output: {stderr_str}")
                    return CommandResult(status="error", output=stderr_str or "Command failed with no error output")

                # Create the next process with the previous output as input
                next_process = await asyncio.create_subprocess_exec(
                    *cmd_parts, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )

                # Pass the output of the previous command to the input of the next command
                stdout, stderr = await asyncio.wait_for(next_process.communicate(input=current_stdout), timeout)

                current_process = next_process
                current_stdout = stdout
                current_stderr = stderr

            except asyncio.TimeoutError:
                logger.warning(f"Piped command timed out after {timeout} seconds: {pipe_command}")
                try:
                    # process.kill() is synchronous, not a coroutine
                    current_process.kill()
                except Exception as e:
                    logger.error(f"Error killing process: {e}")
                return CommandResult(status="error", output=f"Command timed out after {timeout} seconds")

        # Wait for the final command to complete if it hasn't already
        if current_stdout is None:
            try:
                current_stdout, current_stderr = await asyncio.wait_for(current_process.communicate(), timeout)
            except asyncio.TimeoutError:
                logger.warning(f"Piped command timed out after {timeout} seconds: {pipe_command}")
                try:
                    current_process.kill()
                except Exception as e:
                    logger.error(f"Error killing process: {e}")
                return CommandResult(status="error", output=f"Command timed out after {timeout} seconds")

        # Process output
        stdout_str = current_stdout.decode("utf-8", errors="replace")
        stderr_str = current_stderr.decode("utf-8", errors="replace")

        # Truncate output if necessary
        if len(stdout_str) > MAX_OUTPUT_SIZE:
            logger.info(f"Output truncated from {len(stdout_str)} to {MAX_OUTPUT_SIZE} characters")
            stdout_str = stdout_str[:MAX_OUTPUT_SIZE] + "\n... (output truncated)"

        if current_process.returncode != 0:
            logger.warning(f"Piped command failed with return code {current_process.returncode}: {pipe_command}")
            logger.debug(f"Command error output: {stderr_str}")
            return CommandResult(status="error", output=stderr_str or "Command failed with no error output")

        return CommandResult(status="success", output=stdout_str)
    except Exception as e:
        logger.error(f"Failed to execute piped command: {str(e)}")
        return CommandResult(status="error", output=f"Failed to execute command: {str(e)}")
