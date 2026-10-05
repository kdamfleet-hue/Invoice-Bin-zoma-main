import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.engineering_agent.core import (
    AgentError,
    dependency_levels,
    diff_paths,
    is_sensitive_path,
    resolve_safe,
    restore_files,
    scan_destructive_migrations,
    scan_secrets,
    snapshot_files,
    choose_model,
)


class EngineeringAgentCoreTests(unittest.TestCase):
    def test_model_router_uses_fast_profile_for_simple_low_risk_work(self):
        self.assertEqual(choose_model(1, "low", 1000, 0.7, "fast", "reasoning"), "fast")

    def test_model_router_uses_reasoning_profile_for_high_risk_or_complex_work(self):
        self.assertEqual(choose_model(2, "high", 1000, 0.7, "fast", "reasoning"), "reasoning")
        self.assertEqual(choose_model(5, "low", 1000, 0.7, "fast", "reasoning"), "reasoning")

    def test_dependency_levels_parallelize_independent_tasks(self):
        tasks = [
            {"id": "a", "depends_on": []},
            {"id": "b", "depends_on": []},
            {"id": "c", "depends_on": ["a", "b"]},
        ]
        self.assertEqual(dependency_levels(tasks), [["a", "b"], ["c"]])

    def test_dependency_cycles_and_unknown_dependencies_are_rejected(self):
        with self.assertRaises(AgentError):
            dependency_levels([{"id": "a", "depends_on": ["b"]}, {"id": "b", "depends_on": ["a"]}])
        with self.assertRaises(AgentError):
            dependency_levels([{"id": "a", "depends_on": ["missing"]}])

    def test_sensitive_paths_are_flagged(self):
        self.assertTrue(is_sensitive_path("routes/auth.py"))
        self.assertTrue(is_sensitive_path("migrations/versions/1.sql"))
        self.assertFalse(is_sensitive_path("services/analytics_service.py"))

    def test_path_traversal_and_sensitive_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text("safe")
            self.assertEqual(resolve_safe(root, "README.md"), root / "README.md")
            with self.assertRaises(AgentError):
                resolve_safe(root, "../outside.py")
            with self.assertRaises(AgentError):
                resolve_safe(root, "routes/auth.py")

    def test_diff_paths_require_text_add_or_modify_not_delete(self):
        patch = "diff --git a/README.md b/README.md\n--- a/README.md\n+++ b/README.md\n@@ -1 +1 @@\n-old\n+new\n"
        self.assertEqual(diff_paths(patch), ["README.md"])
        with self.assertRaises(AgentError):
            diff_paths("diff --git a/README.md b/README.md\n--- a/README.md\n+++ /dev/null\n")

    def test_secret_scan_reports_location_without_value(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sample.py").write_text('API_KEY = "sk-' + "A" * 30 + '"\n')
            findings = scan_secrets(root)
            self.assertEqual(len(findings), 1)
            self.assertNotIn("A" * 20, str(findings))

    def test_destructive_migration_scan_detects_drop_and_truncate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "migrations").mkdir()
            (root / "migrations" / "bad.sql").write_text("DROP TABLE fleet;\nTRUNCATE TABLE drivers;\n")
            findings = scan_destructive_migrations(root)
            self.assertEqual(len(findings), 2)

    def test_snapshot_restore_returns_only_target_files_to_checkpoint(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "notes.md"
            target.write_text("before")
            snapshot = snapshot_files(root, ["notes.md", "new.md"], allow_sensitive=False)
            target.write_text("after")
            (root / "new.md").write_text("new")
            restore_files(root, snapshot)
            self.assertEqual(target.read_text(), "before")
            self.assertFalse((root / "new.md").exists())

    def test_orchestrator_rolls_back_failed_attempt_then_verifies_retry(self):
        from tools.engineering_agent.orchestrator import EngineeringOrchestrator

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sample.py").write_text("value = 'old'\n")
            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Agent Test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "agent-test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "add", "sample.py"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "baseline"], cwd=root, check=True, capture_output=True)

            class FakeProvider:
                def plan(self, objective, project_map):
                    return {"complexity": 1, "risk": "low", "tasks": [
                        {"id": "edit", "files": ["sample.py"], "depends_on": []}], "checks": ["security"]}

                def patch(self, objective, plan, context, feedback):
                    return ("diff --git a/sample.py b/sample.py\n"
                            "--- a/sample.py\n+++ b/sample.py\n"
                            "@@ -1 +1 @@\n-value = 'old'\n+value = 'new'\n")

            failed = [{"name": "security", "status": "failed", "seconds": 0.01, "findings": [{"type": "test"}]}]
            passed = [{"name": "security", "status": "passed", "seconds": 0.01, "findings": []}]
            with patch("tools.engineering_agent.orchestrator.run_checks", side_effect=[failed, passed]):
                result = EngineeringOrchestrator(root, FakeProvider(), max_attempts=2).run("change sample value")

            self.assertEqual(result["status"], "verified")
            self.assertEqual(result["attempts"], 2)
            self.assertTrue(result["branch"].startswith("engineering-agent/"))
            self.assertEqual((root / "sample.py").read_text(), "value = 'new'\n")


if __name__ == "__main__":
    unittest.main()
