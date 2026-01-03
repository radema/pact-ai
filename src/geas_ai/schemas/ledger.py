from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class LedgerAction(str, Enum):
    SEAL_REQ = "SEAL_REQ"
    SEAL_SPECS = "SEAL_SPECS"
    SEAL_PLAN = "SEAL_PLAN"
    SEAL_MRP = "SEAL_MRP"
    SEAL_INTENT = "SEAL_INTENT"
    APPROVE = "APPROVE"

class EventIdentity(BaseModel):
    signer_id: str
    public_key: str
    signature: str

class LedgerEvent(BaseModel):
    sequence: int
    timestamp: datetime
    action: LedgerAction
    payload: Dict[str, Any]
    prev_hash: Optional[str] = None
    identity: Optional[EventIdentity] = None
    event_hash: str

class Ledger(BaseModel):
    version: str = "3.1"
    bolt_id: str
    created_at: datetime
    head_hash: Optional[str] = None
    events: List[LedgerEvent] = Field(default_factory=list)
