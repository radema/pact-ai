import os
from typer.testing import CliRunner
from geas_ai.main import app
from ruamel.yaml import YAML

runner = CliRunner()


def test_init_creates_workflow(tmp_path):
    """Test that geas init creates the workflow.yaml file with correct content."""

    # Change current working directory to tmp_path
    os.chdir(tmp_path)

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "GEAS initialized" in result.stdout

    workflow_path = tmp_path / ".geas" / "config" / "workflow.yaml"
    assert workflow_path.exists()

    # Verify content
    yaml = YAML()
    with open(workflow_path) as f:
        data = yaml.load(f)

    assert data["name"] == "standard_dev"
    assert "stages" in data

    stages = {s["id"]: s for s in data["stages"]}
    assert "req" in stages
    assert "specs" in stages
    assert "plan" in stages
    assert "mrp" in stages
    assert "approve" in stages

    assert stages["approve"]["action"] == "APPROVE"
    assert stages["approve"]["required_role"] == "human"
