from pathlib import Path

import yaml

ROLES_DIR = Path(__file__).resolve().parents[1] / "roles"
REQUIRED = {"id", "name", "description", "system_prompt", "default_reasoning"}


def test_role_templates_are_valid():
    files = sorted(ROLES_DIR.glob("*.yaml"))
    assert files, "expected at least one role template"
    for f in files:
        data = yaml.safe_load(f.read_text())
        assert data.keys() >= REQUIRED, f"{f.name} missing {REQUIRED - data.keys()}"
        assert data["id"] == f.stem
        assert data["default_reasoning"] in {"off", "low", "medium", "high"}
