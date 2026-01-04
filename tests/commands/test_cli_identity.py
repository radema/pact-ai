import os
import pytest
from geas_ai.core import content
from geas_ai.core.identity import IdentityManager

def test_init_creates_identities_yaml(runner, setup_geas_environment):
    """Test that 'geas init' creates config/identities.yaml."""
    pass

def test_init_clean(runner, tmp_path):
    """Test 'geas init' in a clean directory."""
    from geas_ai.main import app
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert (tmp_path / ".geas/config/identities.yaml").exists()
        assert (tmp_path / ".geas/config/identities.yaml").read_text() == content.DEFAULT_IDENTITIES_YAML
    finally:
        os.chdir(cwd)

def test_identity_add_human(runner, setup_geas_environment, monkeypatch):
    from geas_ai.main import app
    monkeypatch.setattr(os.path, "expanduser", lambda x: str(setup_geas_environment / x.replace("~/", "")))

    result = runner.invoke(app, ["identity", "add", "--name", "alice", "--role", "human"])
    assert result.exit_code == 0
    assert "Identity 'alice' created" in result.stdout

    key_path = setup_geas_environment / ".geas/keys/alice.key"
    assert key_path.exists()
    assert (key_path.stat().st_mode & 0o777) == 0o600

    yaml_path = setup_geas_environment / ".geas/config/identities.yaml"
    assert yaml_path.exists()
    assert "alice" in yaml_path.read_text()

def test_identity_add_agent(runner, setup_geas_environment, monkeypatch):
    from geas_ai.main import app
    monkeypatch.setattr(os.path, "expanduser", lambda x: str(setup_geas_environment / x.replace("~/", "")))

    result = runner.invoke(app, [
        "identity", "add",
        "--name", "bot",
        "--role", "agent",
        "--persona", "Dev",
        "--model", "gpt-4"
    ])
    assert result.exit_code == 0
    assert "export" in result.stdout
    assert "GEAS_KEY_BOT=" in result.stdout

def test_identity_add_duplicate(runner, setup_geas_environment, monkeypatch):
    from geas_ai.main import app
    monkeypatch.setattr(os.path, "expanduser", lambda x: str(setup_geas_environment / x.replace("~/", "")))

    runner.invoke(app, ["identity", "add", "--name", "bob", "--role", "human"])
    result = runner.invoke(app, ["identity", "add", "--name", "bob", "--role", "human"])
    assert result.exit_code == 1
    assert "already exists" in result.stdout

def test_identity_list(runner, setup_geas_environment, monkeypatch):
    from geas_ai.main import app
    monkeypatch.setattr(os.path, "expanduser", lambda x: str(setup_geas_environment / x.replace("~/", "")))

    runner.invoke(app, ["identity", "add", "--name", "charlie", "--role", "human"])
    result = runner.invoke(app, ["identity", "list"])
    assert result.exit_code == 0
    assert "charlie" in result.stdout
    assert "human" in result.stdout

def test_identity_show(runner, setup_geas_environment, monkeypatch):
    from geas_ai.main import app
    monkeypatch.setattr(os.path, "expanduser", lambda x: str(setup_geas_environment / x.replace("~/", "")))

    runner.invoke(app, ["identity", "add", "--name", "dave", "--role", "human"])

    result = runner.invoke(app, ["identity", "show", "dave"])
    assert result.exit_code == 0
    assert "Identity: dave" in result.stdout
    assert "Role: human" in result.stdout
    assert "Active Key:" in result.stdout

def test_identity_revoke(runner, setup_geas_environment, monkeypatch):
    from geas_ai.main import app
    monkeypatch.setattr(os.path, "expanduser", lambda x: str(setup_geas_environment / x.replace("~/", "")))

    # 1. Create Identity
    runner.invoke(app, ["identity", "add", "--name", "eve", "--role", "human"])

    # Get original key content
    key_path = setup_geas_environment / ".geas/keys/eve.key"
    original_key_content = key_path.read_bytes()

    # Get original active key from yaml
    manager = IdentityManager()
    store = manager.load()
    original_public_key = store.get_by_name("eve").active_key

    # 2. Revoke
    result = runner.invoke(app, ["identity", "revoke", "eve", "--yes"])
    assert result.exit_code == 0
    assert "rotated" in result.stdout

    # 3. Verify
    # Key file should have changed
    new_key_content = key_path.read_bytes()
    assert original_key_content != new_key_content

    # Yaml should update
    store = manager.load()
    eve = store.get_by_name("eve")

    assert eve.active_key != original_public_key
    assert original_public_key in eve.revoked_keys
    assert len(eve.revoked_keys) == 1
