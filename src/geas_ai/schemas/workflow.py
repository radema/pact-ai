from typing import List, Optional, Dict
from pydantic import BaseModel

class WorkflowStage(BaseModel):
    id: str
    action: str
    required_role: str  # human/agent
    prerequisite: Optional[str] = None
    description: str

class WorkflowConfig(BaseModel):
    name: str
    version: str
    intent_documents: Dict[str, List[str]] # required: [], optional: []
    stages: List[WorkflowStage]
