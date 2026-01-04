from typing import Dict, List, Optional
from pathlib import Path
import hashlib
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

from geas_ai.schemas.ledger import Ledger, LedgerEvent, LedgerAction
from geas_ai.schemas.verification import (
    ValidationStatus,
    ViolationCode,
    Violation,
    ChainValidationResult,
    SignatureValidationResult,
    WorkflowValidationResult,
    ContentValidationResult,
)
from geas_ai.schemas.workflow import WorkflowConfig
from geas_ai.schemas.identity import IdentityStore
from geas_ai.core.hashing import calculate_event_hash, file_sha256
from geas_ai.utils.crypto import canonicalize_json, verify

# --- Chain Integrity ---

def validate_chain_integrity(ledger: Ledger) -> ChainValidationResult:
    """
    Validate the hash chain integrity of the ledger.
    """
    violations: List[Violation] = []

    if not ledger.events:
        return ChainValidationResult(valid=True, violations=[], event_count=0)

    # 1. Iterate events
    for i, event in enumerate(ledger.events):
        # Sequence check
        if event.sequence != i + 1:
             violations.append(Violation(
                code=ViolationCode.SEQUENCE_GAP,
                message=f"Event at index {i} has sequence {event.sequence}, expected {i+1}.",
                event_sequence=event.sequence
            ))

        # 2. Check prev_hash
        if i == 0:
            if event.prev_hash is not None:
                violations.append(Violation(
                    code=ViolationCode.CHAIN_BROKEN,
                    message="First event must have null prev_hash.",
                    event_sequence=event.sequence
                ))
        else:
            prev_event = ledger.events[i-1]
            if event.prev_hash != prev_event.event_hash:
                violations.append(Violation(
                    code=ViolationCode.CHAIN_BROKEN,
                    message=f"Event {event.sequence} prev_hash ({event.prev_hash}) does not match previous event hash ({prev_event.event_hash}).",
                    event_sequence=event.sequence,
                    details={"expected": prev_event.event_hash, "actual": event.prev_hash}
                ))

        # 3. Recalculate event_hash
        # Use model_dump(mode='json') to get ISO format strings for datetimes, matching what json.dump does (mostly)
        # Note: ledger.py logic is: event_dict = event.model_dump(mode='json'); del event_dict['event_hash']
        event_dict = event.model_dump(mode='json')
        stored_hash = event_dict.pop('event_hash')

        calculated_hash = calculate_event_hash(event_dict)
        if calculated_hash != stored_hash:
             violations.append(Violation(
                code=ViolationCode.EVENT_TAMPERED,
                message=f"Event {event.sequence} hash mismatch.",
                event_sequence=event.sequence,
                details={"expected": calculated_hash, "actual": stored_hash}
            ))

    # 4. Check head_hash matches last event
    if ledger.head_hash != ledger.events[-1].event_hash:
        violations.append(Violation(
            code=ViolationCode.HEAD_MISMATCH,
            message=f"Ledger head_hash ({ledger.head_hash}) does not match last event hash ({ledger.events[-1].event_hash}).",
            details={"expected": ledger.events[-1].event_hash, "actual": ledger.head_hash}
        ))

    return ChainValidationResult(
        valid=len(violations) == 0,
        violations=violations,
        event_count=len(ledger.events)
    )


# --- Signature Verification ---

def validate_signatures(ledger: Ledger, identities: IdentityStore) -> SignatureValidationResult:
    """
    Validate all event signatures in the ledger.
    """
    violations: List[Violation] = []
    verified_count = 0

    for event in ledger.events:
        if not event.identity:
             # Assuming unsigned events are not allowed in this strict mode
             violations.append(Violation(
                code=ViolationCode.IDENTITY_NOT_FOUND,
                message=f"Event {event.sequence} missing identity information.",
                event_sequence=event.sequence
            ))
             continue

        signer_id = event.identity.signer_id
        public_key_hex = event.identity.public_key
        signature_b64 = event.identity.signature

        # Look up identity
        identity_record = identities.get_by_name(signer_id)
        if not identity_record:
            violations.append(Violation(
                code=ViolationCode.IDENTITY_NOT_FOUND,
                message=f"Identity '{signer_id}' not found in store.",
                event_sequence=event.sequence
            ))
            continue

        # Check Revocation
        is_revoked = False
        if hasattr(identity_record, 'revoked_keys') and identity_record.revoked_keys:
             if public_key_hex in [k for k in identity_record.revoked_keys]:
                 is_revoked = True

        if is_revoked:
             violations.append(Violation(
                code=ViolationCode.KEY_REVOKED,
                message=f"Key for identity '{signer_id}' is revoked.",
                event_sequence=event.sequence
            ))
             continue

        # Check Active Key Match
        # In a real system we might allow old non-revoked keys, but here we strict check against active
        if public_key_hex != identity_record.active_key:
            violations.append(Violation(
                code=ViolationCode.KEY_MISMATCH,
                message=f"Key for identity '{signer_id}' does not match active key.",
                event_sequence=event.sequence
            ))
            continue

        # Reconstruct Canonical Payload
        # Logic derived from geas_ai.commands.seal
        try:
            data_to_sign: Dict[str, Any] = {}

            if event.action == LedgerAction.SEAL_INTENT:
                # Intent signs the whole payload
                data_to_sign = event.payload
            elif event.action in [
                LedgerAction.SEAL_REQ,
                LedgerAction.SEAL_SPECS,
                LedgerAction.SEAL_PLAN,
                LedgerAction.SEAL_MRP
            ]:
                # Artifacts sign {action, hash}
                # Note: event.action is an Enum, we need the string value if it was signed as string.
                # In seal.py: `data_to_sign = {"action": action, "hash": content_hash}`
                # where action was passed as LedgerAction enum member.
                # `canonicalize_json` dumps enums? Pydantic json dump handles enums.
                # `json.dumps` (used in canonicalize_json) does NOT handle Enums by default.
                # BUT `seal.py` imports `ledger_schemas`. `action` passed to `_create_event_signature` is `LedgerAction`.
                # Wait, `json.dumps` fails on Enum.
                # Does `seal.py` work currently?
                # If `seal.py` works, then `canonicalize_json` must handle it OR `action` passed is a string.
                # In `seal.py`: `mapping` defines `action` as `ledger_schemas.LedgerAction.SEAL_REQ`.
                # Then calls `_create_event_signature(..., action, ...)`
                # Then calls `_create_event_signature_from_payload(..., {"action": action, ...})`
                # Then calls `canonicalize_json(payload)`.
                # If `canonicalize_json` uses `json.dumps`, it will crash on Enum unless handled.
                # Check `utils/crypto.py`: `json.dumps(...)`. No default handler.
                # Check `utils/crypto.py` again.
                # If `seal.py` works, maybe `LedgerAction` (str, Enum) behaves as str in json.dumps?
                # Yes, `str, Enum` inherits from `str`. `json.dumps` treats it as string.

                data_to_sign = {
                    "action": event.action.value, # Explicitly use value to be safe, though instance works if mixed-in
                    "hash": event.payload.get("hash")
                }
            elif event.action == LedgerAction.APPROVE:
                # Assuming APPROVE signs its payload (cleaner)
                data_to_sign = event.payload
            else:
                 # Fallback: assume payload signed
                 data_to_sign = event.payload

            canonical_bytes = canonicalize_json(data_to_sign)

            if verify(public_key_hex, signature_b64, canonical_bytes):
                verified_count += 1
            else:
                violations.append(Violation(
                    code=ViolationCode.INVALID_SIGNATURE,
                    message=f"Signature verification failed for event {event.sequence}.",
                    event_sequence=event.sequence
                ))

        except Exception as e:
            violations.append(Violation(
                code=ViolationCode.INVALID_SIGNATURE,
                message=f"Signature verification error: {str(e)}",
                event_sequence=event.sequence
            ))

    return SignatureValidationResult(
        valid=len(violations) == 0,
        violations=violations,
        verified_count=verified_count
    )


# --- Workflow Compliance ---

def validate_workflow_compliance(
    ledger: Ledger,
    workflow: WorkflowConfig,
    identities: IdentityStore
) -> WorkflowValidationResult:
    """
    Validate Bolt against workflow requirements.
    """
    violations: List[Violation] = []
    completed_stages: List[str] = []
    missing_stages: List[str] = []

    # Map actions to events (use latest event for each action)
    events_by_action: Dict[str, LedgerEvent] = {}
    for event in ledger.events:
        events_by_action[event.action.value] = event

    for stage in workflow.stages:
        # Check existence
        if stage.action not in events_by_action:
            missing_stages.append(stage.id)
            violations.append(Violation(
                code=ViolationCode.STAGE_MISSING,
                message=f"Required stage '{stage.id}' ({stage.action}) not found in ledger.",
            ))
            continue

        event = events_by_action[stage.action]
        completed_stages.append(stage.id)

        # Check Role
        if event.identity:
            signer = identities.get_by_name(event.identity.signer_id)
            if signer:
                if signer.role != stage.required_role:
                     violations.append(Violation(
                        code=ViolationCode.ROLE_VIOLATION,
                        message=f"Stage '{stage.id}' requires role '{stage.required_role}', signed by '{signer.role.value}' ({signer.name}).",
                        event_sequence=event.sequence
                    ))

        # Check Prerequisite
        if stage.prerequisite:
            if stage.prerequisite not in completed_stages:
                 violations.append(Violation(
                    code=ViolationCode.PREREQUISITE_MISSING,
                    message=f"Stage '{stage.id}' completed before prerequisite '{stage.prerequisite}'.",
                    event_sequence=event.sequence
                ))

    return WorkflowValidationResult(
        valid=len(violations) == 0,
        violations=violations,
        completed_stages=completed_stages,
        missing_stages=missing_stages
    )


# --- Content Integrity ---

def validate_content_integrity(
    ledger: Ledger,
    bolt_path: Path
) -> ContentValidationResult:
    """
    Verify sealed files have not been modified.
    """
    violations: List[Violation] = []
    checked_files = 0
    modified_files = 0

    for event in ledger.events:
        # Check SEAL_INTENT (payload.hashes map)
        if event.action == LedgerAction.SEAL_INTENT and "hashes" in event.payload:
             hashes = event.payload["hashes"]
             if isinstance(hashes, dict):
                 for filename, stored_hash in hashes.items():
                    file_path = bolt_path / filename
                    if not file_path.exists():
                        violations.append(Violation(
                            code=ViolationCode.FILE_MISSING,
                            message=f"Sealed file '{filename}' (from intent) is missing.",
                            event_sequence=event.sequence
                        ))
                        modified_files += 1
                        continue

                    current_hash = file_sha256(file_path)
                    checked_files += 1
                    if current_hash != stored_hash:
                        violations.append(Violation(
                            code=ViolationCode.FILE_MODIFIED,
                            message=f"File '{filename}' (from intent) has been modified.",
                            event_sequence=event.sequence,
                            details={"expected": stored_hash, "actual": current_hash}
                        ))
                        modified_files += 1

        # Check Artifacts (SEAL_REQ, etc) -> payload.file + payload.hash
        elif event.action in [
            LedgerAction.SEAL_REQ,
            LedgerAction.SEAL_SPECS,
            LedgerAction.SEAL_PLAN,
            LedgerAction.SEAL_MRP
        ]:
            if "file" in event.payload and "hash" in event.payload:
                filename = event.payload["file"]
                stored_hash = event.payload["hash"]
                file_path = bolt_path / filename

                if not file_path.exists():
                        violations.append(Violation(
                            code=ViolationCode.FILE_MISSING,
                            message=f"Sealed file '{filename}' is missing.",
                            event_sequence=event.sequence
                        ))
                        modified_files += 1
                        continue

                current_hash = file_sha256(file_path)
                checked_files += 1
                if current_hash != stored_hash:
                    violations.append(Violation(
                        code=ViolationCode.FILE_MODIFIED,
                        message=f"File '{filename}' has been modified.",
                        event_sequence=event.sequence,
                        details={"expected": stored_hash, "actual": current_hash}
                    ))
                    modified_files += 1

        # Check SEAL_MRP (payload.files map) if it exists (legacy/future)
        if "files" in event.payload and isinstance(event.payload["files"], dict):
            files_map = event.payload["files"]
            for rel_path, stored_hash in files_map.items():
                file_path = bolt_path / rel_path

                if not file_path.exists():
                    violations.append(Violation(
                        code=ViolationCode.FILE_MISSING,
                        message=f"Sealed file '{rel_path}' is missing.",
                        event_sequence=event.sequence
                    ))
                    modified_files += 1
                    continue

                current_hash = file_sha256(file_path)
                checked_files += 1

                if current_hash != stored_hash:
                    violations.append(Violation(
                        code=ViolationCode.FILE_MODIFIED,
                        message=f"File '{rel_path}' has been modified.",
                        event_sequence=event.sequence,
                        details={"expected": stored_hash, "actual": current_hash}
                    ))
                    modified_files += 1

    return ContentValidationResult(
        valid=len(violations) == 0,
        violations=violations,
        checked_files=checked_files,
        modified_files=modified_files
    )
