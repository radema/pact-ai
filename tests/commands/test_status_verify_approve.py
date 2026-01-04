import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path
from geas_ai.main import app
from geas_ai.schemas.ledger import Ledger, LedgerEvent, LedgerAction, EventIdentity
from geas_ai.schemas.verification import ChainValidationResult, SignatureValidationResult, WorkflowValidationResult, ContentValidationResult
from geas_ai.schemas.identity import Identity, IdentityRole, IdentityStore
from datetime import datetime, timezone

runner = CliRunner()

# --- Status Tests ---

@patch("geas_ai.commands.status.LedgerManager")
@patch("geas_ai.utils.get_active_bolt_path")
@patch("geas_ai.utils.get_geas_root")
def test_status_no_bolt(mock_utils, mock_bolt_path, mock_ledger_manager):
    mock_utils.return_value = Path("/mock/root")
    mock_bolt_path.return_value = Path("/mock/root/bolts/test-bolt")

    mock_ledger_manager.load_lock.return_value = None

    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "No ledger" in result.stdout

@patch("geas_ai.commands.status.LedgerManager")
@patch("geas_ai.utils.get_active_bolt_path")
@patch("geas_ai.utils.get_geas_root")
def test_status_with_events(mock_utils, mock_bolt_path, mock_ledger_manager):
    mock_utils.return_value = Path("/mock/root")
    mock_bolt_path.return_value = Path("/mock/root/bolts/test-bolt")

    event = LedgerEvent(
        sequence=1,
        timestamp=datetime.now(timezone.utc),
        action=LedgerAction.SEAL_REQ,
        payload={},
        event_hash="h1",
        identity=EventIdentity(signer_id="user1", public_key="k1", signature="s1")
    )
    ledger = Ledger(bolt_id="test-bolt", created_at=datetime.now(timezone.utc), events=[event])
    mock_ledger_manager.load_lock.return_value = ledger

    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "SEAL_REQ" in result.stdout
    assert "user1" in result.stdout

# --- Verify Tests ---

@patch("geas_ai.commands.verify.IdentityManager")
@patch("geas_ai.commands.verify.verification")
@patch("geas_ai.commands.verify.LedgerManager")
@patch("geas_ai.utils.get_active_bolt_path")
@patch("geas_ai.utils.get_geas_root")
def test_verify_success(mock_utils, mock_bolt_path, mock_ledger_manager, mock_verification, mock_identity_manager):
    mock_utils.return_value = Path("/mock/root")
    mock_bolt_path.return_value = Path("/mock/root/bolts/test-bolt")

    ledger = MagicMock(spec=Ledger)
    mock_ledger_manager.load_lock.return_value = ledger

    # Mock Verification Results (All Valid)
    mock_verification.validate_chain_integrity.return_value = ChainValidationResult(valid=True, violations=[], event_count=1)
    mock_verification.validate_signatures.return_value = SignatureValidationResult(valid=True, violations=[], verified_count=1)
    mock_verification.validate_workflow_compliance.return_value = WorkflowValidationResult(valid=True, violations=[], completed_stages=["req"], missing_stages=[])
    mock_verification.validate_content_integrity.return_value = ContentValidationResult(valid=True, violations=[], checked_files=0, modified_files=0)

    result = runner.invoke(app, ["verify"])
    assert result.exit_code == 0
    assert "All checks passed" in result.stdout

@patch("geas_ai.commands.verify.IdentityManager")
@patch("geas_ai.commands.verify.verification")
@patch("geas_ai.commands.verify.LedgerManager")
@patch("geas_ai.utils.get_active_bolt_path")
@patch("geas_ai.utils.get_geas_root")
def test_verify_fail(mock_utils, mock_bolt_path, mock_ledger_manager, mock_verification, mock_identity_manager):
    mock_utils.return_value = Path("/mock/root")
    mock_bolt_path.return_value = Path("/mock/root/bolts/test-bolt")

    ledger = MagicMock(spec=Ledger)
    mock_ledger_manager.load_lock.return_value = ledger

    from geas_ai.schemas.verification import Violation, ViolationCode
    mock_verification.validate_chain_integrity.return_value = ChainValidationResult(
        valid=False,
        violations=[Violation(code=ViolationCode.CHAIN_BROKEN, message="Broken")],
        event_count=1
    )
    mock_verification.validate_signatures.return_value = SignatureValidationResult(valid=True, violations=[], verified_count=1)
    mock_verification.validate_workflow_compliance.return_value = WorkflowValidationResult(valid=True, violations=[], completed_stages=[], missing_stages=[])

    result = runner.invoke(app, ["verify"])
    assert result.exit_code == 1
    assert "CHAIN_BROKEN" in result.stdout
    assert "Violations:" in result.stdout

@patch("geas_ai.commands.verify.IdentityManager")
@patch("geas_ai.commands.verify.verification")
@patch("geas_ai.commands.verify.LedgerManager")
@patch("geas_ai.utils.get_active_bolt_path")
@patch("geas_ai.utils.get_geas_root")
def test_verify_json(mock_utils, mock_bolt_path, mock_ledger_manager, mock_verification, mock_identity_manager):
    mock_utils.return_value = Path("/mock/root")
    mock_bolt_path.return_value = Path("/mock/root/bolts/test-bolt")

    ledger = MagicMock(spec=Ledger)
    mock_ledger_manager.load_lock.return_value = ledger

    mock_verification.validate_chain_integrity.return_value = ChainValidationResult(valid=True, violations=[], event_count=1)
    mock_verification.validate_signatures.return_value = SignatureValidationResult(valid=True, violations=[], verified_count=1)
    mock_verification.validate_workflow_compliance.return_value = WorkflowValidationResult(valid=True, violations=[], completed_stages=[], missing_stages=[])

    result = runner.invoke(app, ["verify", "--json"])
    assert result.exit_code == 0
    assert '"valid": true' in result.stdout

# --- Approve Tests ---

@patch("geas_ai.utils.crypto.sign")
@patch("geas_ai.core.identity.KeyManager")
@patch("geas_ai.core.identity.IdentityManager")
@patch("geas_ai.core.ledger.LedgerManager")
@patch("geas_ai.utils.get_active_bolt_path")
@patch("geas_ai.utils.get_geas_root")
def test_approve_success(mock_utils, mock_bolt_path, mock_ledger_manager, mock_identity_manager, mock_key_manager, mock_sign):
    mock_utils.return_value = Path("/mock/root")
    mock_bolt_path.return_value = Path("/mock/root/bolts/test-bolt")

    # Mock Ledger with MRP Sealed
    event = LedgerEvent(
        sequence=1,
        timestamp=datetime.now(timezone.utc),
        action=LedgerAction.SEAL_MRP,
        payload={},
        event_hash="hash_mrp",
        identity=EventIdentity(signer_id="agent", public_key="k", signature="s")
    )
    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[event])
    mock_ledger_manager.load_lock.return_value = ledger

    # Mock Identity
    mock_store = MagicMock()
    mock_store.get_by_name.return_value = Identity(
        name="human", role=IdentityRole.HUMAN, active_key="ssh-key"
    )
    mock_identity_manager.return_value.load.return_value = mock_store

    mock_key_manager.load_private_key.return_value = MagicMock()
    mock_sign.return_value = "signature"

    result = runner.invoke(app, ["approve", "--identity", "human"])
    assert result.exit_code == 0
    assert "Approved!" in result.stdout
    assert mock_ledger_manager.append_event.called

@patch("geas_ai.core.ledger.LedgerManager")
@patch("geas_ai.utils.get_active_bolt_path")
@patch("geas_ai.utils.get_geas_root")
def test_approve_fail_no_mrp(mock_utils, mock_bolt_path, mock_ledger_manager):
    mock_utils.return_value = Path("/mock/root")
    mock_bolt_path.return_value = Path("/mock/root/bolts/test-bolt")

    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[])
    mock_ledger_manager.load_lock.return_value = ledger

    result = runner.invoke(app, ["approve", "--identity", "human"])
    assert result.exit_code == 1
    assert "MRP is not yet sealed" in result.stdout

@patch("geas_ai.core.identity.IdentityManager")
@patch("geas_ai.core.ledger.LedgerManager")
@patch("geas_ai.utils.get_active_bolt_path")
@patch("geas_ai.utils.get_geas_root")
def test_approve_fail_wrong_role(mock_utils, mock_bolt_path, mock_ledger_manager, mock_identity_manager):
    mock_utils.return_value = Path("/mock/root")
    mock_bolt_path.return_value = Path("/mock/root/bolts/test-bolt")

    event = LedgerEvent(
        sequence=1,
        timestamp=datetime.now(timezone.utc),
        action=LedgerAction.SEAL_MRP,
        payload={},
        event_hash="hash_mrp",
        identity=EventIdentity(signer_id="agent", public_key="k", signature="s")
    )
    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[event])
    mock_ledger_manager.load_lock.return_value = ledger

    mock_store = MagicMock()
    mock_store.get_by_name.return_value = Identity(
        name="agent", role=IdentityRole.AGENT, active_key="ssh-key", persona="x", model="y"
    )
    mock_identity_manager.return_value.load.return_value = mock_store

    result = runner.invoke(app, ["approve", "--identity", "agent"])
    assert result.exit_code == 1
    assert "Only HUMAN identities can approve" in result.stdout
