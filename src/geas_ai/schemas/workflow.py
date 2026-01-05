from typing import List, Optional
from pydantic import BaseModel

class WorkflowStage(BaseModel):
    id: str
    action: str  # e.g., "SEAL_INTENT", "SEAL_MRP"
    required_role: str  # "human", "agent"
    prerequisite: Optional[str] = None
    description: Optional[str] = None

class IntentConfig(BaseModel):
    required: List[str]
    optional: List[str] = []

class WorkflowConfig(BaseModel):
    name: str
    version: str
    intent_documents: IntentConfig
    stages: List[WorkflowStage]
    test_command: str = "pytest"
    test_timeout: int = 300
