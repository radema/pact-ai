import os
import json
import pytest
from typer.testing import CliRunner
from geas_ai.main import app
from geas_ai.core import ledger
from geas_ai.schemas.ledger import LedgerAction

runner = CliRunner()

@pytest.fixture
def setup_geas(tmp_path):
    """Sets up a temporary GEAS environment."""
    cwd = os.getcwd()
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    yield tmp_path
    os.chdir(cwd)

def test_seal_flow_new_ledger(setup_geas):
    # 1. Create Bolt
    result = runner.invoke(app, ["new", "test-bolt"])
    assert result.exit_code == 0
    bolt_path = setup_geas / ".geas/bolts/test-bolt"

    # Check lock.json initialized
    lock_file = bolt_path / "lock.json"
    assert lock_file.exists()

    # 2. Seal Req
    # req is created by 'new'
    result = runner.invoke(app, ["seal", "req"])
    assert result.exit_code == 0

    # Check Ledger
    l = ledger.LedgerManager.load_lock(bolt_path)
    assert len(l.events) == 1
    assert l.events[0].action == LedgerAction.SEAL_REQ

    # 3. Seal Specs (Create file first)
    (bolt_path / "02_specs.md").write_text("specs content")
    result = runner.invoke(app, ["seal", "specs"])
    assert result.exit_code == 0

    l = ledger.LedgerManager.load_lock(bolt_path)
    assert len(l.events) == 2
    assert l.events[1].action == LedgerAction.SEAL_SPECS
    assert l.events[1].prev_hash == l.events[0].event_hash

def test_seal_intent_missing_docs(setup_geas):
    runner.invoke(app, ["new", "test-bolt"])
    bolt_path = setup_geas / ".geas/bolts/test-bolt"

    # Missing specs and plan
    result = runner.invoke(app, ["seal", "intent", "--identity", "me"])
    assert result.exit_code == 1
    assert "Required document" in result.stdout

def test_seal_intent_no_identity(setup_geas):
    runner.invoke(app, ["new", "test-bolt"])
    result = runner.invoke(app, ["seal", "intent"])
    assert result.exit_code == 1
    assert "--identity is required" in result.stdout
