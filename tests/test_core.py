from pact_cli.main import app
import os
import yaml


def test_init_command(runner, tmp_path):
    """Test 'pact init' creates the necessary structure."""
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "Success! PACT initialized" in result.stdout
        assert (tmp_path / ".pacts").exists()
        assert (tmp_path / ".pacts/config").exists()
        assert (tmp_path / ".pacts/bolts").exists()
        assert (tmp_path / ".pacts/config/agents.yaml").exists()
    finally:
        os.chdir(cwd)


def test_new_bolt_command(runner, setup_pact_environment):
    """Test 'pact new' creates a new bolt."""
    result = runner.invoke(app, ["new", "test-bolt"])
    assert result.exit_code == 0
    assert "Bolt Started!" in result.stdout

    bolt_path = setup_pact_environment / ".pacts/bolts/test-bolt"
    assert bolt_path.exists()
    assert (bolt_path / "01_request.md").exists()

    # Check that context was switched
    ctx_file = setup_pact_environment / ".pacts/active_context.md"
    assert "Current Bolt:** test-bolt" in ctx_file.read_text()


def test_seal_flow(runner, setup_pact_environment):
    """Test the sealing flow: req -> seal req -> verify."""
    # 1. Create bolt
    runner.invoke(app, ["new", "seal-test"])
    bolt_path = setup_pact_environment / ".pacts/bolts/seal-test"

    # 2. Seal Request
    result = runner.invoke(app, ["seal", "req"])
    assert result.exit_code == 0
    assert "Sealed req" in result.stdout

    # 3. Verify Lock Exists
    lock_file = bolt_path / "approved.lock"
    assert lock_file.exists()
    with open(lock_file) as f:
        data = yaml.safe_load(f)
    assert "req_hash" in data

    # 4. Verify Command
    result_verify = runner.invoke(app, ["verify"])
    assert result_verify.exit_code == 0
    # The output is a rich table, "req" and "PASS" might be separated by whitespace/borders
    assert "req" in result_verify.stdout
    assert "PASS" in result_verify.stdout


def test_status_command(runner, setup_pact_environment):
    """Test 'pact status' displays info."""
    import re

    runner.invoke(app, ["new", "status-test"])
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    # Since we haven't sealed anything, it says "No approved.lock found"
    assert "No approved.lock found" in result.stdout

    # Now seal something and check status again
    runner.invoke(app, ["seal", "req"])
    result_sealed = runner.invoke(app, ["status"])
    assert result_sealed.exit_code == 0
    assert "Seal Status" in result_sealed.stdout

    # Verify strict output format for sealed req:
    # Actual output structure: req | <timestamp> | <hash>
    pattern = r"req\s+│\s+202\d-.*│\s+[a-f0-9]+"
    match = re.search(pattern, result_sealed.stdout)
    assert match is not None, f"""
    req row missing Timestamp or Hash.
    Output matches pattern '{pattern}':\n{result_sealed.stdout}
    """


def test_checkout_command(runner, setup_pact_environment):
    """Test switching contexts."""
    runner.invoke(app, ["new", "bolt-a"])
    runner.invoke(app, ["new", "bolt-b"])

    # Switch back to A
    result = runner.invoke(app, ["checkout", "bolt-a"])
    assert result.exit_code == 0
    assert "Switched to bolt: bolt-a" in result.stdout

    ctx_file = setup_pact_environment / ".pacts/active_context.md"
    assert "Current Bolt:** bolt-a" in ctx_file.read_text()
