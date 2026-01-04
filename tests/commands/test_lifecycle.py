from geas_ai.main import app


def test_new_bolt_command(runner, setup_geas_environment):
    """Test 'geas new' creates a new bolt."""
    result = runner.invoke(app, ["new", "test-bolt"])
    assert result.exit_code == 0
    assert "Bolt Started!" in result.stdout

    bolt_path = setup_geas_environment / ".geas/bolts/test-bolt"
    assert bolt_path.exists()
    assert (bolt_path / "01_request.md").exists()

    # Check that context was switched
    ctx_file = setup_geas_environment / ".geas/active_context.md"
    assert "Current Bolt:** test-bolt" in ctx_file.read_text()


def test_checkout_command(runner, setup_geas_environment):
    """Test switching contexts."""
    runner.invoke(app, ["new", "bolt-a"])
    runner.invoke(app, ["new", "bolt-b"])

    # Switch back to A
    result = runner.invoke(app, ["checkout", "bolt-a"])
    assert result.exit_code == 0
    assert "Switched to bolt: bolt-a" in result.stdout

    ctx_file = setup_geas_environment / ".geas/active_context.md"
    assert "Current Bolt:** bolt-a" in ctx_file.read_text()
