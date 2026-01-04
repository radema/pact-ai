import os
import pytest
from geas_ai.main import app
from geas_ai.core.identity import KeyManager, CryptoError


def test_show_non_existent(runner):
    result = runner.invoke(app, ["identity", "show", "ghost"])
    assert result.exit_code == 1
    assert "Identity 'ghost' not found" in result.stdout


def test_revoke_non_existent(runner):
    result = runner.invoke(app, ["identity", "revoke", "ghost", "--yes"])
    assert result.exit_code == 1
    assert "Identity 'ghost' not found" in result.stdout


def test_revoke_abort(runner, setup_geas_environment, monkeypatch):
    monkeypatch.setattr(
        os.path,
        "expanduser",
        lambda x: str(setup_geas_environment / x.replace("~/", "")),
    )

    # Add user
    runner.invoke(app, ["identity", "add", "--name", "alice", "--role", "human"])

    # Revoke with "n" input
    result = runner.invoke(app, ["identity", "revoke", "alice"], input="n\n")
    assert result.exit_code == 1
    assert "Are you sure" in result.stdout


def test_add_permission_error(runner, setup_geas_environment, monkeypatch):
    monkeypatch.setattr(
        os.path,
        "expanduser",
        lambda x: str(setup_geas_environment / x.replace("~/", "")),
    )

    # Mock os.open to raise PermissionError
    original_open = os.open

    def mock_open(path, flags, mode=0o777):
        if "keys" in str(path):
            raise PermissionError("Access denied")
        return original_open(path, flags, mode)

    monkeypatch.setattr(os, "open", mock_open)

    result = runner.invoke(
        app, ["identity", "add", "--name", "denied", "--role", "human"]
    )
    assert result.exit_code == 1
    assert "Access denied" in result.stdout


def test_load_corrupted_key_file(setup_geas_environment, monkeypatch, runner):
    """
    Test that KeyManager raises CryptoError (wrapped) or similar when file is garbage.
    Note: accessing via CLI doesn't use KeyManager to *load* private key usually,
    except maybe future commands. We verify KeyManager directly here for the edge case.
    """
    monkeypatch.setattr(
        os.path,
        "expanduser",
        lambda x: str(setup_geas_environment / x.replace("~/", "")),
    )

    # Create garbage key file
    keys_dir = setup_geas_environment / ".geas/keys"
    keys_dir.mkdir(parents=True, exist_ok=True)
    (keys_dir / "bad.key").write_bytes(b"DATA_GARBAGE_NOT_A_KEY")

    with pytest.raises(CryptoError):
        KeyManager.load_private_key("bad")
