#!/usr/bin/env python3
"""
check-agent-contracts.py — Validate that all commands have the correct YAML frontmatter schema.
"""

import sys
import yaml
from pathlib import Path

EXPECTED_PERSONAS = {
    "Manager",
    "Collaborator", 
    "Sr Architect", 
    "Developer", 
    "Jr Programmer", 
    "Sr Tech Lead", 
    "Gatekeeper"
}

def extract_yaml_frontmatter(text: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    yaml_lines = []
    for line in lines[1:]:
        if line.strip() == "---":
            return "\n".join(yaml_lines)
        yaml_lines.append(line)
    return None

def validate_command(cmd_path: Path) -> list[str]:
    errors = []
    text = cmd_path.read_text(encoding="utf-8")
    yaml_text = extract_yaml_frontmatter(text)
    
    if not yaml_text:
        return [f"{cmd_path.name}: Missing YAML frontmatter"]
    
    try:
        data = yaml.safe_load(yaml_text)
    except Exception as e:
        return [f"{cmd_path.name}: Invalid YAML syntax - {e}"]
        
    if not isinstance(data, dict):
        return [f"{cmd_path.name}: YAML frontmatter is not a dictionary"]

    # Validate name
    if "name" not in data:
        errors.append(f"{cmd_path.name}: Missing 'name'")
    
    # Validate persona
    if "persona" not in data:
        errors.append(f"{cmd_path.name}: Missing 'persona'")
    elif data["persona"] not in EXPECTED_PERSONAS:
        errors.append(f"{cmd_path.name}: Invalid persona '{data['persona']}'. Must be one of {EXPECTED_PERSONAS}")
        
    # Validate gates
    if "gates" in data:
        if not isinstance(data["gates"], list):
            errors.append(f"{cmd_path.name}: 'gates' must be a list")
        else:
            for i, gate in enumerate(data["gates"]):
                if not isinstance(gate, dict) or "check" not in gate or "on_fail" not in gate:
                    errors.append(f"{cmd_path.name}: gates[{i}] must be an object with 'check' and 'on_fail'")
    
    # Validate actions, must_do, must_not_do
    for field in ["actions", "must_do", "must_not_do"]:
        if field in data and not isinstance(data[field], list):
            errors.append(f"{cmd_path.name}: '{field}' must be a list")
            
    return errors

def main() -> int:
    root = Path(".")
    commands_dir = root / "commands"
    
    if not commands_dir.is_dir():
        print(f"Error: {commands_dir} not found.")
        return 1

    all_errors = []
    for cmd_path in sorted(commands_dir.glob("*.md")):
        all_errors.extend(validate_command(cmd_path))

    if all_errors:
        print("❌ Contract Validation Failed:\n")
        for error in all_errors:
            print(f"  - {error}")
        return 1
    else:
        print("✅ All command contracts valid.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
