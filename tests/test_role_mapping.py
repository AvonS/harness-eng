import unittest
import os
import re

class TestRoleMapping(unittest.TestCase):
    def setUp(self):
        # Locate project root dynamically
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        # We check both local main repo AGENTS.md and dogfood CONSTITUTION.md if it exists
        self.agents_md_path = os.path.join(self.root, "AGENTS.md")
        
        # In testing environment, check .harness-eng relative to root
        self.constitution_path = os.path.join(self.root, ".harness-eng", "CONSTITUTION.md")
        if not os.path.exists(self.constitution_path):
            # Fallback for dogfood repository layout if tests run there
            self.constitution_path = os.path.join(self.root, "..", "harness-eng-dogfood", ".harness-eng", "CONSTITUTION.md")

    def test_logical_roles_in_documentation(self):
        """Verify that both AGENTS.md and CONSTITUTION.md contain reference to all 6 logical roles."""
        expected_roles = ["Manager", "Analyst", "Sr Architect", "Developer", "Sr Tech Lead", "Gatekeeper"]
        
        # 1. Check AGENTS.md
        self.assertTrue(os.path.exists(self.agents_md_path), f"Missing {self.agents_md_path}")
        with open(self.agents_md_path, "r", encoding="utf-8") as f:
            content = f.read()
        for role in expected_roles:
            self.assertIn(role, content, f"Logical role '{role}' not documented in AGENTS.md")
            
        # 2. Check CONSTITUTION.md
        self.assertTrue(os.path.exists(self.constitution_path), f"Missing {self.constitution_path}")
        with open(self.constitution_path, "r", encoding="utf-8") as f:
            const_content = f.read()
        for role in expected_roles:
            self.assertIn(role, const_content, f"Logical role '{role}' not documented in CONSTITUTION.md")

    def test_physical_agent_directories(self):
        """Verify that the 5 expected agent folders exist on disk."""
        agents_dir = os.path.join(self.root, "agents")
        self.assertTrue(os.path.exists(agents_dir), f"Missing agents folder: {agents_dir}")
        
        expected_dirs = ["collaborator", "developer", "gatekeeper", "sr-architect", "sr-tech-lead"]
        actual_dirs = [d for d in os.listdir(agents_dir) if os.path.isdir(os.path.join(agents_dir, d))]
        
        for d in expected_dirs:
            self.assertIn(d, actual_dirs, f"Physical agent folder 'agents/{d}' missing on disk")

if __name__ == "__main__":
    unittest.main()
