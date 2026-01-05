from pathlib import Path
from typing import Optional
from ruamel.yaml import YAML
from geas_ai.schemas.workflow import WorkflowConfig, WorkflowStage, IntentConfig


class WorkflowManager:
    """Manages workflow configuration loading and validation."""

    DEFAULT_WORKFLOW = WorkflowConfig(
        name="standard_dev",
        version="1.0",
        intent_documents=IntentConfig(
            required=["01_request.md", "02_specs.md"], optional=["03_plan.md"]
        ),
        stages=[
            WorkflowStage(
                id="req",
                action="SEAL_REQ",
                required_role="human",
                description="Seal Requirements",
            ),
            WorkflowStage(
                id="specs",
                action="SEAL_SPECS",
                required_role="human",
                prerequisite="req",
                description="Seal Specifications",
            ),
            WorkflowStage(
                id="plan",
                action="SEAL_PLAN",
                required_role="agent",
                prerequisite="specs",
                description="Seal Implementation Plan",
            ),
            WorkflowStage(
                id="intent",
                action="SEAL_INTENT",
                required_role="human",
                prerequisite="plan",
                description="Seal Intent (Req + Specs + Plan)",
            ),
            WorkflowStage(
                id="mrp",
                action="SEAL_MRP",
                required_role="agent",
                prerequisite="intent",
                description="Seal Merge Request Package",
            ),
            WorkflowStage(
                id="approve",
                action="APPROVE",
                required_role="human",
                prerequisite="mrp",
                description="Approve for Merge",
            ),
        ],
    )

    @staticmethod
    def load_workflow(config_path: Optional[Path] = None) -> WorkflowConfig:
        """
        Loads the workflow configuration.
        Returns hardcoded default if file is missing.
        """
        if config_path and config_path.exists():
            # Use 'safe' loading to prevent arbitrary code execution from untrusted configs
            yaml = YAML(typ="safe")
            try:
                with open(config_path, "r") as f:
                    data = yaml.load(f)
                    return WorkflowConfig(**data)
            except Exception:
                # Log warning? For now fallback.
                pass

        return WorkflowManager.DEFAULT_WORKFLOW
