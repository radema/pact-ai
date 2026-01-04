import subprocess
import shlex
import time
from datetime import datetime, timezone
from geas_ai.core.manifest import TestResultInfo

def run_tests(command: str = "uv run pytest", timeout: int = 300) -> TestResultInfo:
    """
    Executes the test command and captures the result.

    Args:
        command: The shell command to run tests.
        timeout: Maximum execution time in seconds.

    Returns:
        TestResultInfo object containing execution details.
    """
    start_time = time.time()

    try:
        # Run the command
        # using shlex.split to properly parse command arguments
        # capture_output=True captures stdout and stderr
        # text=True decodes output as string
        result = subprocess.run(
            shlex.split(command),
            timeout=timeout,
            capture_output=True,
            text=True
        )

        duration = time.time() - start_time
        passed = result.returncode == 0

        return TestResultInfo(
            passed=passed,
            exit_code=result.returncode,
            duration_seconds=duration,
            timestamp=datetime.now(timezone.utc),
            output=result.stdout + "\n" + result.stderr
        )

    except subprocess.TimeoutExpired as e:
        duration = time.time() - start_time
        output = e.stdout.decode() if e.stdout else ""
        output += "\n" + (e.stderr.decode() if e.stderr else "")
        output += f"\nTimeout expired after {timeout} seconds."
        return TestResultInfo(
            passed=False,
            exit_code=124, # Standard timeout exit code
            duration_seconds=duration,
            timestamp=datetime.now(timezone.utc),
            output=output
        )
    except Exception as e:
        # Fallback for other errors (e.g. command not found)
        duration = time.time() - start_time
        return TestResultInfo(
            passed=False,
            exit_code=1,
            duration_seconds=duration,
            timestamp=datetime.now(timezone.utc),
            output=str(e)
        )
