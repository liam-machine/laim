#!/usr/bin/env python3
"""
Databricks Execution Context - Execute arbitrary code on Databricks clusters.

A fully templated, configurable script for executing Python, SQL, or Scala code
on Databricks clusters via the Execution Context API (1.2).

Configuration can be provided via:
1. CLI arguments (highest priority)
2. Environment variables
3. ~/.databrickscfg profile (lowest priority)

Usage:
    # Execute Python command using default profile
    python databricks_exec.py -c "print(spark.version)"

    # Execute SQL query
    python databricks_exec.py --language sql -c "SHOW DATABASES"

    # Execute a file
    python databricks_exec.py -f script.py

    # Use specific profile and cluster
    python databricks_exec.py --profile PROD --cluster-id "abc-123-xyz" -c "spark.sql('SELECT 1').show()"

    # Use environment variables for auth
    DATABRICKS_HOST=https://adb-xxx.azuredatabricks.net DATABRICKS_TOKEN=xxx python databricks_exec.py -c "print(1)"

    # Interactive REPL mode
    python databricks_exec.py --repl

Environment Variables:
    DATABRICKS_HOST       - Databricks workspace URL
    DATABRICKS_TOKEN      - Personal access token or OAuth token
    DATABRICKS_CLUSTER_ID - Default cluster ID
    DATABRICKS_PROFILE    - Profile name in ~/.databrickscfg
"""

import argparse
import configparser
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import urllib.request
import urllib.error


class DatabricksConfig:
    """Configuration loader with fallback chain: CLI -> ENV -> Config file."""

    def __init__(
        self,
        host: Optional[str] = None,
        token: Optional[str] = None,
        cluster_id: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        self.host = host
        self.token = token
        self.cluster_id = cluster_id
        self.profile = profile or os.environ.get("DATABRICKS_PROFILE", "DEFAULT")

        self._resolve_config()

    def _resolve_config(self) -> None:
        """Resolve configuration from environment and config file."""
        # Try environment variables first
        if not self.host:
            self.host = os.environ.get("DATABRICKS_HOST")
        if not self.token:
            self.token = os.environ.get("DATABRICKS_TOKEN")
        if not self.cluster_id:
            self.cluster_id = os.environ.get("DATABRICKS_CLUSTER_ID")

        # Fall back to config file
        if not self.host or not self.token:
            self._load_from_config_file()

    def _load_from_config_file(self) -> None:
        """Load missing values from ~/.databrickscfg."""
        config_path = Path.home() / ".databrickscfg"

        if not config_path.exists():
            return

        config = configparser.ConfigParser()
        config.read(config_path)

        if self.profile not in config:
            # Try DEFAULT profile
            if "DEFAULT" in config:
                self.profile = "DEFAULT"
            else:
                return

        section = config[self.profile]

        if not self.host:
            self.host = section.get("host", "").strip()
        if not self.token:
            self.token = section.get("token", "").strip()
        if not self.cluster_id:
            self.cluster_id = section.get("cluster_id", "").strip()

    def validate(self) -> None:
        """Validate that required configuration is present."""
        missing = []
        if not self.host:
            missing.append("host (DATABRICKS_HOST or --host)")
        if not self.token:
            missing.append("token (DATABRICKS_TOKEN or --token)")
        if not self.cluster_id:
            missing.append("cluster_id (DATABRICKS_CLUSTER_ID or --cluster-id)")

        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}\n"
                "Provide via CLI arguments, environment variables, or ~/.databrickscfg"
            )


def api_request(
    config: DatabricksConfig,
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 60,
) -> Dict[str, Any]:
    """Make a request to the Databricks REST API."""
    url = f"{config.host.rstrip('/')}{endpoint}"

    if params:
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query_string}"

    headers = {
        "Authorization": f"Bearer {config.token}",
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode("utf-8") if data else None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(f"API Error ({e.code}): {error_body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Connection Error: {e.reason}") from e


class ExecutionContext:
    """Manages a Databricks execution context for running code on a cluster."""

    SUPPORTED_LANGUAGES = ("python", "sql", "scala", "r")

    def __init__(
        self,
        config: DatabricksConfig,
        language: str = "python",
        poll_interval: float = 0.5,
        verbose: bool = False,
    ):
        self.config = config
        self.language = language.lower()
        self.poll_interval = poll_interval
        self.verbose = verbose
        self.context_id: Optional[str] = None

        if self.language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported: {', '.join(self.SUPPORTED_LANGUAGES)}"
            )

    def _log(self, message: str) -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[DEBUG] {message}", file=sys.stderr)

    def check_cluster_state(self) -> str:
        """Check if the cluster is running."""
        result = api_request(
            self.config,
            "GET",
            "/api/2.0/clusters/get",
            params={"cluster_id": self.config.cluster_id},
        )
        return result.get("state", "UNKNOWN")

    def create_context(self) -> str:
        """Create an execution context on the cluster."""
        self._log(f"Creating {self.language} execution context...")

        result = api_request(
            self.config,
            "POST",
            "/api/1.2/contexts/create",
            data={"language": self.language, "clusterId": self.config.cluster_id},
        )

        self.context_id = result.get("id")
        if not self.context_id:
            raise RuntimeError(f"Failed to create context: {result}")

        self._log(f"Context created: {self.context_id}")
        return self.context_id

    def destroy_context(self) -> None:
        """Destroy the execution context."""
        if not self.context_id:
            return

        self._log(f"Destroying context {self.context_id}...")
        try:
            api_request(
                self.config,
                "POST",
                "/api/1.2/contexts/destroy",
                data={"contextId": self.context_id, "clusterId": self.config.cluster_id},
            )
            self._log("Context destroyed.")
        except Exception as e:
            print(f"Warning: Failed to destroy context: {e}", file=sys.stderr)
        finally:
            self.context_id = None

    def execute(self, command: str) -> Dict[str, Any]:
        """Execute a command and wait for results."""
        if not self.context_id:
            self.create_context()

        self._log(f"Submitting command ({len(command)} chars)...")

        # Submit command
        result = api_request(
            self.config,
            "POST",
            "/api/1.2/commands/execute",
            data={
                "language": self.language,
                "contextId": self.context_id,
                "clusterId": self.config.cluster_id,
                "command": command,
            },
        )

        command_id = result.get("id")
        if not command_id:
            raise RuntimeError(f"Failed to submit command: {result}")

        self._log(f"Command submitted: {command_id}")

        # Poll for completion
        poll_count = 0
        while True:
            status_result = api_request(
                self.config,
                "GET",
                "/api/1.2/commands/status",
                params={
                    "clusterId": self.config.cluster_id,
                    "contextId": self.context_id,
                    "commandId": command_id,
                },
            )

            status = status_result.get("status", "")
            poll_count += 1

            if poll_count % 10 == 0:
                self._log(f"Still running... (poll #{poll_count})")

            if status in ("Finished", "Error", "Cancelled"):
                self._log(f"Command completed with status: {status}")
                return status_result
            elif status in ("Running", "Queued"):
                time.sleep(self.poll_interval)
            else:
                self._log(f"Unknown status: {status}")
                time.sleep(self.poll_interval)

    def cancel(self, command_id: str) -> None:
        """Cancel a running command."""
        api_request(
            self.config,
            "POST",
            "/api/1.2/commands/cancel",
            data={
                "clusterId": self.config.cluster_id,
                "contextId": self.context_id,
                "commandId": command_id,
            },
        )

    def __enter__(self):
        self.create_context()
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.destroy_context()
        return False


class OutputFormatter:
    """Format execution results for display."""

    @staticmethod
    def format(result: Dict[str, Any], output_format: str = "text") -> str:
        """Format execution result for display."""
        results = result.get("results", {})
        result_type = results.get("resultType", "")
        status = result.get("status", "")

        output_parts = []

        if status == "Error" or result_type == "error":
            cause = results.get("cause", "")
            summary = results.get("summary", "Unknown error")
            output_parts.append(f"ERROR: {summary}")
            if cause:
                output_parts.append(cause)
            return "\n".join(output_parts)

        if result_type == "text":
            data = results.get("data", "")
            if data:
                output_parts.append(str(data))

        elif result_type == "table":
            schema = results.get("schema", [])
            data = results.get("data", [])

            if output_format == "json":
                return json.dumps({"schema": schema, "data": data}, indent=2)
            elif output_format == "csv":
                headers = [col.get("name", f"col{i}") for i, col in enumerate(schema)]
                lines = [",".join(headers)]
                for row in data:
                    lines.append(",".join(str(v) if v is not None else "" for v in row))
                return "\n".join(lines)
            else:  # text/tabular
                if schema and data:
                    headers = [col.get("name", f"col{i}") for i, col in enumerate(schema)]
                    output_parts.append("\t".join(headers))
                    output_parts.append("-" * 60)
                    for row in data[:100]:
                        output_parts.append("\t".join(str(v) if v is not None else "NULL" for v in row))
                    if len(data) > 100:
                        output_parts.append(f"... ({len(data) - 100} more rows)")

        elif result_type == "images":
            output_parts.append("[Image output - not displayable in terminal]")

        else:
            # Fallback for unknown types
            data = results.get("data", "")
            if data:
                output_parts.append(str(data))

        return "\n".join(output_parts) if output_parts else "(No output)"


def run_command(ctx: ExecutionContext, command: str, output_format: str = "text") -> int:
    """Execute a single command and return exit code."""
    with ctx:
        result = ctx.execute(command)
        output = OutputFormatter.format(result, output_format)
        print(output)

        result_type = result.get("results", {}).get("resultType", "")
        return 1 if result_type == "error" or result.get("status") == "Error" else 0


def run_file(ctx: ExecutionContext, file_path: str, output_format: str = "text") -> int:
    """Execute a file and return exit code."""
    path = Path(file_path)

    if not path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    content = path.read_text()

    with ctx:
        if ctx.verbose:
            print(f"Executing file '{file_path}' ({len(content)} bytes)...", file=sys.stderr)

        result = ctx.execute(content)
        output = OutputFormatter.format(result, output_format)
        print(output)

        result_type = result.get("results", {}).get("resultType", "")
        return 1 if result_type == "error" or result.get("status") == "Error" else 0


def run_repl(ctx: ExecutionContext) -> None:
    """Run an interactive REPL session."""
    print("\nDatabricks Execution Context REPL")
    print(f"Language: {ctx.language} | Cluster: {ctx.config.cluster_id}")
    print("Type 'exit' or 'quit' to end session. Multi-line: end with blank line.\n")

    with ctx:
        while True:
            try:
                lines = []
                prompt = f"[{ctx.language}]>>> "

                while True:
                    try:
                        line = input(prompt)
                    except EOFError:
                        print("\nExiting...")
                        return

                    if line.lower() in ("exit", "quit") and not lines:
                        print("Exiting...")
                        return

                    lines.append(line)

                    # Single line command
                    if len(lines) == 1 and not line.endswith((":", "\\", ",")):
                        break

                    # Multi-line: blank line to execute
                    if line == "":
                        lines.pop()
                        break

                    prompt = "... "

                command = "\n".join(lines)
                if not command.strip():
                    continue

                print("Executing...", end=" ", flush=True)
                result = ctx.execute(command)
                print("Done.")

                output = OutputFormatter.format(result)
                print(output)
                print()

            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit' to quit.")
                continue


def main():
    parser = argparse.ArgumentParser(
        description="Execute code on Databricks clusters via Execution Context API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute Python command
  python databricks_exec.py -c "print(spark.version)"

  # Execute SQL query
  python databricks_exec.py --language sql -c "SHOW DATABASES"

  # Execute a file
  python databricks_exec.py -f my_script.py

  # Use specific profile
  python databricks_exec.py --profile DEV -c "print(1)"

  # Interactive REPL
  python databricks_exec.py --repl

  # Check cluster state
  python databricks_exec.py --check-cluster

Environment Variables:
  DATABRICKS_HOST       - Workspace URL (e.g., https://adb-xxx.azuredatabricks.net)
  DATABRICKS_TOKEN      - Personal access token
  DATABRICKS_CLUSTER_ID - Default cluster ID
  DATABRICKS_PROFILE    - Profile name in ~/.databrickscfg
        """,
    )

    # Connection arguments
    conn_group = parser.add_argument_group("Connection")
    conn_group.add_argument("--host", help="Databricks workspace URL")
    conn_group.add_argument("--token", help="Personal access token")
    conn_group.add_argument("--cluster-id", help="Cluster ID to execute on")
    conn_group.add_argument("--profile", help="Profile name in ~/.databrickscfg")

    # Execution arguments
    exec_group = parser.add_argument_group("Execution")
    exec_group.add_argument("-c", "--command", help="Command to execute")
    exec_group.add_argument("-f", "--file", help="File to execute")
    exec_group.add_argument("--repl", action="store_true", help="Start interactive REPL")
    exec_group.add_argument(
        "--language",
        choices=ExecutionContext.SUPPORTED_LANGUAGES,
        default="python",
        help="Language for execution (default: python)",
    )

    # Output arguments
    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "--output-format",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format for tabular results (default: text)",
    )
    output_group.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # Utility arguments
    util_group = parser.add_argument_group("Utilities")
    util_group.add_argument("--check-cluster", action="store_true", help="Check cluster state")
    util_group.add_argument(
        "--poll-interval",
        type=float,
        default=0.5,
        help="Polling interval in seconds (default: 0.5)",
    )

    args = parser.parse_args()

    # Build configuration
    try:
        config = DatabricksConfig(
            host=args.host,
            token=args.token,
            cluster_id=args.cluster_id,
            profile=args.profile,
        )
    except Exception as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1

    # Check cluster state if requested
    if args.check_cluster:
        try:
            config.validate()
            ctx = ExecutionContext(config, verbose=args.verbose)
            state = ctx.check_cluster_state()
            print(f"Cluster state: {state}")
            return 0 if state == "RUNNING" else 1
        except Exception as e:
            print(f"Error checking cluster: {e}", file=sys.stderr)
            return 1

    # Validate we have execution mode
    if not args.command and not args.file and not args.repl:
        parser.print_help()
        print("\nError: Must specify -c/--command, -f/--file, or --repl", file=sys.stderr)
        return 1

    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1

    # Create execution context
    ctx = ExecutionContext(
        config,
        language=args.language,
        poll_interval=args.poll_interval,
        verbose=args.verbose,
    )

    # Execute based on mode
    if args.repl:
        run_repl(ctx)
        return 0
    elif args.command:
        return run_command(ctx, args.command, args.output_format)
    elif args.file:
        return run_file(ctx, args.file, args.output_format)

    return 0


if __name__ == "__main__":
    sys.exit(main())
