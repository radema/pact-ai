from unittest.mock import patch, MagicMock
import subprocess
from geas_ai.core.testing import run_tests


def test_run_tests_success():
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Test Output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = run_tests("echo test")

        assert result.passed is True
        assert result.exit_code == 0
        assert "Test Output" in result.output


def test_run_tests_failure():
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error"
        mock_run.return_value = mock_result

        result = run_tests("bad command")

        assert result.passed is False
        assert result.exit_code == 1
        assert "Error" in result.output


def test_run_tests_timeout():
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd="sleep", timeout=1, output=b"Part", stderr=b"Err"
        )

        result = run_tests("sleep", timeout=1)

        assert result.passed is False
        assert result.exit_code == 124
        assert "Timeout expired" in result.output
        assert "Part" in result.output  # stdout decoded


def test_run_tests_timeout_invalid_utf8():
    with patch("subprocess.run") as mock_run:
        # Simulate invalid UTF-8 in stdout/stderr during timeout
        # \x80 is invalid start byte in UTF-8
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd="bad_output", timeout=1, output=b"Valid\n\x80Invalid", stderr=b"Err\xff"
        )

        result = run_tests("bad_output", timeout=1)

        assert result.passed is False
        assert result.exit_code == 124
        # Should contain replacement character
        assert "Valid" in result.output
        assert "\ufffd" in result.output  # Replacement char
        assert "Timeout expired" in result.output
