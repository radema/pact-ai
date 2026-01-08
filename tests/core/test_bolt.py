import pytest
from geas_ai.bolt import Bolt
from geas_ai.state import StateManager


def test_bolt_creation(setup_geas_environment):
    """Test creating a new bolt."""
    bolt = Bolt.create("feature-x")

    assert bolt.name == "feature-x"
    assert bolt.path.exists()
    assert (bolt.path / "lock.json").exists()

    # Check state
    manager = StateManager()
    assert manager.get_active_bolt() == "feature-x"
    assert "feature-x" in manager.list_bolts()


def test_bolt_loading(setup_geas_environment):
    """Test loading a bolt from state."""
    Bolt.create("feature-y")

    loaded = Bolt.load("feature-y")
    assert loaded.name == "feature-y"
    assert loaded.status == "draft"
    assert loaded.path.name == "feature-y"


def test_bolt_deletion(setup_geas_environment):
    """Test deleting a bolt."""
    bolt = Bolt.create("feature-z")
    path = bolt.path

    assert path.exists()

    bolt.delete()

    assert not path.exists()
    manager = StateManager()
    assert "feature-z" not in manager.list_bolts()


def test_bolt_load_missing(setup_geas_environment):
    """Test error when loading non-existent bolt."""
    with pytest.raises(ValueError):
        Bolt.load("ghost-bolt")
