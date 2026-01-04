import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch
from dataclasses import dataclass

from geas_ai.schemas.ledger import Ledger, LedgerEvent, LedgerAction, EventIdentity
from geas_ai.schemas.verification import (
    ViolationCode,
    ChainValidationResult,
    SignatureValidationResult,
    WorkflowValidationResult,
    ContentValidationResult
)
from geas_ai.schemas.workflow import WorkflowConfig, WorkflowStage, IntentConfig
from geas_ai.schemas.identity import IdentityStore, Identity, IdentityRole
from geas_ai.core import verification
from geas_ai.core.hashing import calculate_event_hash
from geas_ai.utils.crypto import generate_keypair, sign, canonicalize_json, load_private_key_from_bytes

# --- Fixtures ---

@dataclass
class TestContext:
    store: IdentityStore
    priv_human: bytes
    priv_agent: bytes

@pytest.fixture
def test_ctx():
    # Create keys for testing
    priv_human, pub_human = generate_keypair()
    priv_agent, pub_agent = generate_keypair()

    store = IdentityStore(identities=[
        Identity(name="human-dev", role=IdentityRole.HUMAN, active_key=pub_human),
        Identity(name="agent-ai", role=IdentityRole.AGENT, active_key=pub_agent, persona="coder", model="gpt-4"),
    ])

    return TestContext(store, priv_human, priv_agent)

@pytest.fixture
def mock_workflow():
    return WorkflowConfig(
        name="test_flow",
        version="1.0",
        intent_documents=IntentConfig(required=["req.md"]),
        stages=[
            WorkflowStage(id="req", action="SEAL_REQ", required_role="human"),
            WorkflowStage(id="specs", action="SEAL_SPECS", required_role="human", prerequisite="req"),
            WorkflowStage(id="plan", action="SEAL_PLAN", required_role="agent", prerequisite="specs"),
        ]
    )

def create_signed_event(sequence, prev_hash, action, payload, signer_name, ctx):
    """Helper to create a valid signed event."""
    # 1. Sign
    priv_key_bytes = None
    pub_key = None

    identity = ctx.store.get_by_name(signer_name)
    if signer_name == "human-dev":
        priv_key_bytes = ctx.priv_human
    elif signer_name == "agent-ai":
        priv_key_bytes = ctx.priv_agent

    pub_key = identity.active_key

    # Determine signed data based on action (mirroring implementation)
    if action == LedgerAction.SEAL_INTENT:
        data_to_sign = payload
    elif action in [LedgerAction.SEAL_REQ, LedgerAction.SEAL_SPECS, LedgerAction.SEAL_PLAN, LedgerAction.SEAL_MRP]:
        data_to_sign = {"action": action.value, "hash": payload.get("hash")}
    else:
        data_to_sign = payload

    canonical_bytes = canonicalize_json(data_to_sign)

    priv_key_obj = load_private_key_from_bytes(priv_key_bytes)
    signature = sign(priv_key_obj, canonical_bytes)

    event_identity = EventIdentity(
        signer_id=signer_name,
        public_key=pub_key,
        signature=signature
    )

    # 2. Create Event
    event = LedgerEvent(
        sequence=sequence,
        timestamp=datetime.now(timezone.utc),
        action=action,
        payload=payload,
        prev_hash=prev_hash,
        identity=event_identity,
        event_hash="" # placeholder
    )

    # 3. Hash
    event_dict = event.model_dump(mode='json')
    del event_dict['event_hash']
    event.event_hash = calculate_event_hash(event_dict)

    return event

# --- Tests ---

def test_chain_integrity_valid(test_ctx):
    """Test a valid chain passes integrity check."""
    e1 = create_signed_event(1, None, LedgerAction.SEAL_REQ, {"file": "req.md", "hash": "h1"}, "human-dev", test_ctx)
    e2 = create_signed_event(2, e1.event_hash, LedgerAction.SEAL_SPECS, {"file": "specs.md", "hash": "h2"}, "human-dev", test_ctx)

    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[e1, e2], head_hash=e2.event_hash)

    result = verification.validate_chain_integrity(ledger)
    assert result.valid
    assert result.event_count == 2
    assert len(result.violations) == 0

def test_chain_integrity_broken_link(test_ctx):
    """Test broken prev_hash link."""
    e1 = create_signed_event(1, None, LedgerAction.SEAL_REQ, {"file": "req.md", "hash": "h1"}, "human-dev", test_ctx)
    e2 = create_signed_event(2, "wrong_hash", LedgerAction.SEAL_SPECS, {"file": "specs.md", "hash": "h2"}, "human-dev", test_ctx)

    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[e1, e2], head_hash=e2.event_hash)

    result = verification.validate_chain_integrity(ledger)
    assert not result.valid
    assert any(v.code == ViolationCode.CHAIN_BROKEN for v in result.violations)

def test_chain_integrity_tampered_event(test_ctx):
    """Test content modification invalidates hash."""
    e1 = create_signed_event(1, None, LedgerAction.SEAL_REQ, {"file": "req.md", "hash": "h1"}, "human-dev", test_ctx)

    # Tamper with payload but keep hash
    e1.payload["hash"] = "h_tampered"

    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[e1], head_hash=e1.event_hash)

    result = verification.validate_chain_integrity(ledger)
    assert not result.valid
    assert any(v.code == ViolationCode.EVENT_TAMPERED for v in result.violations)

def test_signatures_valid(test_ctx):
    """Test valid signatures."""
    e1 = create_signed_event(1, None, LedgerAction.SEAL_REQ, {"file": "req.md", "hash": "h1"}, "human-dev", test_ctx)
    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[e1], head_hash=e1.event_hash)

    result = verification.validate_signatures(ledger, test_ctx.store)
    assert result.valid
    assert result.verified_count == 1

def test_signatures_invalid(test_ctx):
    """Test invalid signature (modified content)."""
    e1 = create_signed_event(1, None, LedgerAction.SEAL_REQ, {"file": "req.md", "hash": "h1"}, "human-dev", test_ctx)

    # Modify payload -> signature should fail because content changed
    e1.payload["hash"] = "h_tampered"

    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[e1], head_hash=e1.event_hash)

    result = verification.validate_signatures(ledger, test_ctx.store)
    assert not result.valid
    assert any(v.code == ViolationCode.INVALID_SIGNATURE for v in result.violations)

def test_signatures_revoked_key(test_ctx):
    """Test revoked key rejection."""
    # 1. Create event with human key
    e1 = create_signed_event(1, None, LedgerAction.SEAL_REQ, {"file": "req.md", "hash": "h1"}, "human-dev", test_ctx)

    # 2. Revoke the key in store
    identity = test_ctx.store.get_by_name("human-dev")
    identity.revoked_keys.append(identity.active_key)

    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[e1], head_hash=e1.event_hash)

    result = verification.validate_signatures(ledger, test_ctx.store)
    assert not result.valid
    assert any(v.code == ViolationCode.KEY_REVOKED for v in result.violations)

def test_workflow_compliance_valid(test_ctx, mock_workflow):
    """Test complete workflow compliance."""
    e1 = create_signed_event(1, None, LedgerAction.SEAL_REQ, {"file": "req.md", "hash": "h1"}, "human-dev", test_ctx)
    e2 = create_signed_event(2, e1.event_hash, LedgerAction.SEAL_SPECS, {"file": "specs.md", "hash": "h2"}, "human-dev", test_ctx)
    e3 = create_signed_event(3, e2.event_hash, LedgerAction.SEAL_PLAN, {"file": "plan.md", "hash": "h3"}, "agent-ai", test_ctx)

    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[e1, e2, e3], head_hash=e3.event_hash)

    result = verification.validate_workflow_compliance(ledger, mock_workflow, test_ctx.store)
    assert result.valid
    assert "req" in result.completed_stages
    assert "specs" in result.completed_stages
    assert "plan" in result.completed_stages

def test_workflow_missing_stage(test_ctx, mock_workflow):
    """Test missing required stage."""
    # Missing specs and plan
    e1 = create_signed_event(1, None, LedgerAction.SEAL_REQ, {"file": "req.md", "hash": "h1"}, "human-dev", test_ctx)

    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[e1], head_hash=e1.event_hash)

    result = verification.validate_workflow_compliance(ledger, mock_workflow, test_ctx.store)
    assert not result.valid
    assert "specs" in result.missing_stages
    assert any(v.code == ViolationCode.STAGE_MISSING for v in result.violations)

def test_workflow_role_violation(test_ctx, mock_workflow):
    """Test agent signing human stage."""
    # Specs requires HUMAN, we use AGENT
    e1 = create_signed_event(1, None, LedgerAction.SEAL_REQ, {"file": "req.md", "hash": "h1"}, "human-dev", test_ctx)
    e2 = create_signed_event(2, e1.event_hash, LedgerAction.SEAL_SPECS, {"file": "specs.md", "hash": "h2"}, "agent-ai", test_ctx)

    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[e1, e2], head_hash=e2.event_hash)

    result = verification.validate_workflow_compliance(ledger, mock_workflow, test_ctx.store)
    assert not result.valid
    assert any(v.code == ViolationCode.ROLE_VIOLATION for v in result.violations)

def test_workflow_prerequisite_missing(test_ctx, mock_workflow):
    """Test stage out of order."""
    # Plan (req: specs) done before Specs
    e1 = create_signed_event(1, None, LedgerAction.SEAL_REQ, {"file": "req.md", "hash": "h1"}, "human-dev", test_ctx)
    e2 = create_signed_event(2, e1.event_hash, LedgerAction.SEAL_PLAN, {"file": "plan.md", "hash": "h3"}, "agent-ai", test_ctx)

    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[e1, e2], head_hash=e2.event_hash)

    result = verification.validate_workflow_compliance(ledger, mock_workflow, test_ctx.store)
    assert not result.valid
    assert any(v.code == ViolationCode.PREREQUISITE_MISSING for v in result.violations)

def test_content_integrity(test_ctx, tmp_path):
    """Test file content verification."""
    # Create dummy files
    f1 = tmp_path / "req.md"
    f1.write_text("content1")
    # Actually let's use the real hashing function
    from geas_ai.core.hashing import file_sha256
    h1 = file_sha256(f1)

    e1 = create_signed_event(1, None, LedgerAction.SEAL_REQ, {"file": "req.md", "hash": h1}, "human-dev", test_ctx)

    ledger = Ledger(bolt_id="test", created_at=datetime.now(timezone.utc), events=[e1], head_hash=e1.event_hash)

    # Valid case
    result = verification.validate_content_integrity(ledger, tmp_path)
    assert result.valid
    assert result.checked_files == 1

    # Modified case
    f1.write_text("modified")
    result = verification.validate_content_integrity(ledger, tmp_path)
    assert not result.valid
    assert result.modified_files == 1
    assert any(v.code == ViolationCode.FILE_MODIFIED for v in result.violations)

    # Missing case
    f1.unlink()
    result = verification.validate_content_integrity(ledger, tmp_path)
    assert not result.valid
    assert any(v.code == ViolationCode.FILE_MISSING for v in result.violations)
