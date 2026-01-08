import json
from geas_ai.state import StateManager


def test_state_initialization(setup_geas_environment):
    """Test that StateManager initializes state.json."""
    manager = StateManager(root_path=setup_geas_environment / ".geas")  # noqa: F841
    state_file = setup_geas_environment / ".geas/state.json"

    assert state_file.exists()
    data = json.loads(state_file.read_text())
    assert data["version"] == "1.0"
    assert data["bolts"] == {}
    assert data["active_bolt"] is None


def test_bolt_registration(setup_geas_environment):
    """Test registering and retrieving bolts."""
    manager = StateManager(root_path=setup_geas_environment / ".geas")

    manager.register_bolt("test-bolt", ".geas/bolts/test-bolt")
    bolt = manager.list_bolts().get("test-bolt")

    assert bolt is not None
    assert bolt["status"] == "draft"
    assert bolt["path"] == ".geas/bolts/test-bolt"


def test_active_bolt_switching(setup_geas_environment):
    """Test switching active bot."""
    manager = StateManager(root_path=setup_geas_environment / ".geas")
    manager.register_bolt("bolt-1", "path/1")
    manager.register_bolt("bolt-2", "path/2")

    manager.set_active_bolt("bolt-1")
    assert manager.get_active_bolt() == "bolt-1"

    manager.set_active_bolt("bolt-2")
    assert manager.get_active_bolt() == "bolt-2"


def test_context_sync(setup_geas_environment):
    """Test that active_context.md is updated (backward compatibility)."""
    manager = StateManager(root_path=setup_geas_environment / ".geas")
    manager.register_bolt("bolt-sync", ".geas/bolts/bolt-sync")
    manager.set_active_bolt("bolt-sync")

    ctx_file = setup_geas_environment / ".geas/active_context.md"
    assert ctx_file.exists()
    content = ctx_file.read_text()
    assert "Current Bolt:** bolt-sync" in content
