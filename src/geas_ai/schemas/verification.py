from enum import Enum
from typing import List, Optional, Any
from pydantic import BaseModel


class ValidationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"


class ViolationCode(str, Enum):
    CHAIN_BROKEN = "CHAIN_BROKEN"
    EVENT_TAMPERED = "EVENT_TAMPERED"
    HEAD_MISMATCH = "HEAD_MISMATCH"
    IDENTITY_NOT_FOUND = "IDENTITY_NOT_FOUND"
    KEY_MISMATCH = "KEY_MISMATCH"
    KEY_REVOKED = "KEY_REVOKED"
    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    STAGE_MISSING = "STAGE_MISSING"
    ROLE_VIOLATION = "ROLE_VIOLATION"
    PREREQUISITE_MISSING = "PREREQUISITE_MISSING"
    FILE_MODIFIED = "FILE_MODIFIED"
    FILE_MISSING = "FILE_MISSING"
    SEQUENCE_GAP = "SEQUENCE_GAP"


class Violation(BaseModel):
    code: ViolationCode
    message: str
    event_sequence: Optional[int] = None
    details: Optional[dict[str, Any]] = None


class ValidationResult(BaseModel):
    valid: bool
    violations: List[Violation]


class ChainValidationResult(ValidationResult):
    event_count: int


class SignatureValidationResult(ValidationResult):
    verified_count: int


class WorkflowValidationResult(ValidationResult):
    completed_stages: List[str]
    missing_stages: List[str]


class ContentValidationResult(ValidationResult):
    checked_files: int
    modified_files: int
