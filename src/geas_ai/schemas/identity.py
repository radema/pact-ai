from enum import Enum
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator


class IdentityRole(str, Enum):
    HUMAN = "human"
    AGENT = "agent"


class Identity(BaseModel):
    name: str = Field(..., pattern=r"^[a-z0-9-]+$")
    role: IdentityRole
    persona: Optional[str] = None  # Required if role == AGENT
    model: Optional[str] = None  # Required if role == AGENT
    active_key: str  # SSH-format public key (e.g., "ssh-ed25519 ...")
    revoked_keys: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def validate_agent_fields(self) -> "Identity":
        if self.role == IdentityRole.AGENT:
            if not self.persona:
                raise ValueError("Field required for Agent role")
            if not self.model:
                raise ValueError("Field required for Agent role")
        return self


class IdentityStore(BaseModel):
    identities: List[Identity] = Field(default_factory=list)

    def get_by_name(self, name: str) -> Optional[Identity]:
        return next((i for i in self.identities if i.name == name), None)
