import unittest
import os
import shutil
import subprocess

class TestSanityDiscovery(unittest.TestCase):
    def setUp(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.sanity_script = os.path.join(self.root, "scripts", "sanity-check.sh")
        
        # Determine the local skills directory (in dogfood repo since that's where the active state lives)
        self.skills_dir = os.path.join(self.root, ".harness-eng", "skills")
        if not os.path.exists(self.skills_dir):
            self.skills_dir = os.path.abspath(os.path.join(self.root, "..", "harness-eng-dogfood", ".harness-eng", "skills"))

        self.mock_skill_dir = os.path.join(self.skills_dir, "mockskilltest")

    def tearDown(self):
        # Cleanup mock skill
        if os.path.exists(self.mock_skill_dir):
            shutil.rmtree(self.mock_skill_dir)

    def test_dynamic_skills_discovery(self):
        """Verify that scripts/sanity-check.sh dynamically detects skills instead of hardcoding counts."""
        # Create a mock skill directory and file
        os.makedirs(self.mock_skill_dir, exist_ok=True)
        with open(os.path.join(self.mock_skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write("---\nname: mockskilltest\ndescription: test skill\n---\n")

        # Count actual skills on disk
        actual_skills_count = len([d for d in os.listdir(self.skills_dir) if os.path.isdir(os.path.join(self.skills_dir, d))])

        # Run sanity-check.sh
        # Note: We expect the script itself to pass or fail, but we parse its stdout for the count
        res = subprocess.run(["bash", self.sanity_script], cwd=self.root, capture_output=True, text=True)
        
        expected_output_fragment = f"{actual_skills_count} skills verified"
        self.assertIn(expected_output_fragment, res.stdout, f"Sanity check did not dynamically discover all {actual_skills_count} skills. Output: {res.stdout}")

if __name__ == "__main__":
    unittest.main()
