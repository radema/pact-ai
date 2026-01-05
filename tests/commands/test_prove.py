import shutil
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from geas_ai.main import app
from geas_ai.core.manifest import TestResultInfo
from datetime import datetime, timezone

runner = CliRunner()

def setup_bolt(tmp_path, bolt_id="test-bolt", sealed=True):
    """Sets up a mock bolt environment."""
    # .geas structure
    geas_dir = tmp_path / ".geas"
    bolts_dir = geas_dir / "bolts"
    bolt_dir = bolts_dir / bolt_id
    bolt_dir.mkdir(parents=True)

    # Config pointing to active bolt
    config_dir = geas_dir / "config"
    config_dir.mkdir()
    (config_dir / "current_bolt").write_text(bolt_id)

    # Ledger
    ledger_path = geas_dir / "ledger.json"
    events = []

    # Add SEAL_INTENT event if requested
    if sealed:
        # Note: LedgerEvent schema uses 'action' (LedgerAction enum), not 'event_type'
        # And it needs 'identity'
        identity_json = '{"signer_id": "tester", "public_key": "key", "signature": "sig"}'
        events.append(f'{{"action": "SEAL_INTENT", "identity": {identity_json}, "sequence": 1, "timestamp": "2023-01-01T00:00:00Z", "event_hash": "abc", "prev_hash": "0000", "payload": {{}} }}')

    ledger_content = f'{{"bolt_id": "{bolt_id}", "created_at": "2023-01-01T00:00:00Z", "head_hash": "abc", "events": [' + ",".join(events) + ']}'

    # Save as lock.json in bolt dir, not ledger.json in geas root
    (bolt_dir / "lock.json").write_text(ledger_content)

    return bolt_dir

def test_prove_command_success(tmp_path):
    bolt_dir = setup_bolt(tmp_path)

    # Mock source files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("print('hello')")

    # Mock run_tests to pass
    with patch("geas_ai.commands.prove.run_tests") as mock_run:
        mock_run.return_value = TestResultInfo(
            passed=True,
            exit_code=0,
            duration_seconds=0.5,
            timestamp=datetime.now(timezone.utc),
            output="Tests Passed"
        )

        # Run command inside tmp_path
        with patch("geas_ai.commands.prove.ensure_geas_root", return_value=tmp_path):
            with patch("geas_ai.commands.prove.get_active_bolt_name", return_value="test-bolt"):
                # We must use proper scope that exists
                result = runner.invoke(app, ["prove", "--scope", "src"])

    assert result.exit_code == 0
    assert "Proof Generated Successfully" in result.stdout

    # Check artifacts
    mrp_dir = bolt_dir / "mrp"
    assert (mrp_dir / "manifest.json").exists()
    assert (mrp_dir / "tests.log").exists()
    assert "Tests Passed" in (mrp_dir / "tests.log").read_text()

def test_prove_command_test_failure(tmp_path):
    setup_bolt(tmp_path)

    # Mock source files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("print('hello')")

    # Mock run_tests to fail
    with patch("geas_ai.commands.prove.run_tests") as mock_run:
        mock_run.return_value = TestResultInfo(
            passed=False,
            exit_code=1,
            duration_seconds=0.5,
            timestamp=datetime.now(timezone.utc),
            output="Tests Failed"
        )

        with patch("geas_ai.commands.prove.ensure_geas_root", return_value=tmp_path):
            with patch("geas_ai.commands.prove.get_active_bolt_name", return_value="test-bolt"):
                result = runner.invoke(app, ["prove", "--scope", "src"])

    assert result.exit_code == 1
    assert "Tests Failed!" in result.stdout
    assert "Aborting proof generation" in result.stdout

def test_prove_command_unsealed_intent(tmp_path):
    # Setup unsealed bolt
    setup_bolt(tmp_path, sealed=False)

    with patch("geas_ai.commands.prove.ensure_geas_root", return_value=tmp_path):
        with patch("geas_ai.commands.prove.get_active_bolt_name", return_value="test-bolt"):
            result = runner.invoke(app, ["prove"])

    assert result.exit_code == 1
    assert "Intent not sealed" in result.stdout

def test_prove_command_skip_tests(tmp_path):
    bolt_dir = setup_bolt(tmp_path)
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "file.py").touch()

    with patch("geas_ai.commands.prove.ensure_geas_root", return_value=tmp_path):
        with patch("geas_ai.commands.prove.get_active_bolt_name", return_value="test-bolt"):
            # We don't mock run_tests because it shouldn't be called
            result = runner.invoke(app, ["prove", "--scope", "src", "--skip-tests"])

    assert result.exit_code == 0
    assert "Skipping tests" in result.stdout
    assert (bolt_dir / "mrp" / "manifest.json").exists()
