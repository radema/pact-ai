from pact_cli.main import app


def test_agents_command_global(runner, setup_pact_environment):
    """
    Test that 'pact agents' correctly reads and displays the global configuration.
    """
    result = runner.invoke(app, ["agents"])
    assert result.exit_code == 0
    assert "PACT Agents Roster (Global)" in result.stdout
    assert "test_agent" in result.stdout
    assert "Test Role" in result.stdout
    assert "Test Goal" in result.stdout


def test_agents_command_no_pact(runner, tmp_path):
    """
    Test that 'pact agents' fails properly if not in a pact environment.
    """
    # Ensure we are in an empty temp dir and PACT is not initialized
    import os

    current_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        result = runner.invoke(app, ["agents"])
        assert result.exit_code == 1
        assert "PACT is not initialized" in result.stdout
    finally:
        os.chdir(current_cwd)
