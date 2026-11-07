import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / ".agents" / "memory" / "memory_manager.py"
SPEC = importlib.util.spec_from_file_location("memory_manager", MODULE_PATH)
memory_manager = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(memory_manager)


class ProjectMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
        (self.root / "README.md").write_text("# Sample\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_scan_builds_agent_context_and_dashboard(self):
        data = memory_manager.scan(self.root, description="A sample project")
        self.assertEqual(data["summary"]["file_count"], 2)
        self.assertIn("Python", data["project"]["tech_stack"])
        self.assertIn("src/main.py", data["entrypoints"])
        self.assertTrue((self.root / ".agents/memory/context.md").exists())
        self.assertTrue((self.root / ".agents/memory/visualizer.html").exists())

    def test_scan_preserves_durable_records(self):
        memory_manager.scan(self.root)
        task = memory_manager.add_record(self.root, "tasks", {"title": "Ship it", "status": "pending"})
        memory_manager.add_record(self.root, "decisions", {"title": "Keep Python", "rationale": "No dependencies"})
        memory_manager.scan(self.root)
        data = memory_manager.load_memory(self.root)
        self.assertEqual(data["tasks"][0]["title"], "Ship it")
        self.assertEqual(data["decisions"][0]["title"], "Keep Python")
        memory_manager.update_task(self.root, task["id"], "done")
        self.assertEqual(memory_manager.load_memory(self.root)["tasks"][0]["status"], "done")

    def test_ignore_files_and_generated_outputs(self):
        (self.root / "secret.txt").write_text("not indexed", encoding="utf-8")
        (self.root / ".memoryignore").write_text("secret.txt\n", encoding="utf-8")
        first = memory_manager.scan(self.root)
        second = memory_manager.scan(self.root)
        paths = {item["path"] for item in second["files"]}
        self.assertNotIn("secret.txt", paths)
        self.assertNotIn(".agents/memory/memory.json", paths)
        self.assertEqual(first["summary"]["file_count"], second["summary"]["file_count"])


if __name__ == "__main__":
    unittest.main()
