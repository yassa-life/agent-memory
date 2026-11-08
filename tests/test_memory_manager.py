import importlib.util
import json
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
        dashboard = (self.root / ".agents/memory/visualizer.html").read_text(encoding="utf-8")
        self.assertIn("File relationship graph", dashboard)
        self.assertIn("Edit history", dashboard)
        self.assertIn('id="projectSelect"', dashboard)
        self.assertIn('id="agentSelect"', dashboard)

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

    def test_builds_file_relationship_graph_and_related_query(self):
        (self.root / "src" / "utils.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.root / "src" / "main.py").write_text("from . import utils\nprint(utils.VALUE)\n", encoding="utf-8")
        data = memory_manager.scan(self.root)
        self.assertEqual(data["schema_version"], 3)
        self.assertGreaterEqual(data["graph"]["summary"]["edge_count"], 1)
        related = memory_manager.related_files(data["graph"], "src/main.py")
        self.assertTrue(related["found"])
        self.assertIn("src/utils.py", {node["path"] for node in related["related_nodes"]})

    def test_records_dated_change_history(self):
        memory_manager.scan(self.root)
        (self.root / "src" / "main.py").write_text("print('changed')\n", encoding="utf-8")
        data = memory_manager.scan(self.root)
        self.assertGreaterEqual(len(data["history"]), 2)
        self.assertIn("src/main.py", data["history"][-1]["changed"])

    def test_enables_agents_and_imports_chat_metadata(self):
        memory_manager.scan(self.root)
        agent = memory_manager.enable_agent(self.root, "claude")
        self.assertEqual(agent["name"], "Claude")
        self.assertTrue((self.root / "CLAUDE.md").exists())
        custom = memory_manager.register_agent(self.root, "Local Agent", ".local-agent/instructions.md")
        self.assertEqual(custom["instruction_file"], ".local-agent/instructions.md")
        self.assertTrue((self.root / ".local-agent/instructions.md").exists())
        transcript = self.root / "chat.jsonl"
        transcript.write_text('{"role":"user","text":"hello"}\n', encoding="utf-8")
        chat = memory_manager.import_chat(self.root, transcript, "Claude", "Architecture chat", "Selected the service boundary")
        self.assertEqual(chat["line_count"], 1)
        stored = memory_manager.load_memory(self.root)
        self.assertEqual(stored["chats"][0]["summary"], "Selected the service boundary")
        self.assertNotIn("hello", str(stored["chats"][0]))

    def test_tracks_another_project_from_its_memory(self):
        memory_manager.scan(self.root, display_name="Primary")
        with tempfile.TemporaryDirectory() as other_temp:
            other = Path(other_temp)
            (other / "app.py").write_text("print('other')\n", encoding="utf-8")
            memory_manager.scan(other, display_name="Other project")
            record = memory_manager.track_project(self.root, other)
            self.assertEqual(record["name"], "Other project")
            self.assertEqual(record["file_count"], 1)
            self.assertIn("graph", record["snapshot"])
            self.assertNotIn("files", record["snapshot"])
            self.assertNotIn("projects", record["snapshot"])

    def test_syncs_and_deduplicates_project_manifest(self):
        memory_manager.scan(self.root)
        with tempfile.TemporaryDirectory() as other_temp:
            other = Path(other_temp)
            manifest = self.root / "projects.local.json"
            manifest.write_text(json.dumps({"projects": [
                {"projectId": "one", "label": "First label", "path": str(other)},
                {"projectId": "two", "label": "Updated label", "path": str(other)},
            ]}), encoding="utf-8")
            records = memory_manager.sync_projects(self.root, manifest)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["name"], "Updated label")
            self.assertIn("snapshot", records[0])
            deep_records = memory_manager.sync_projects(self.root, manifest, deep_scan=True, max_files=100)
            self.assertEqual(len(deep_records), 1)
            project_id = deep_records[0]["id"]
            self.assertTrue((self.root / ".agents/memory/projects" / f"{project_id}.json").exists())
            self.assertTrue((self.root / ".agents/memory/projects" / f"{project_id}.html").exists())
            self.assertIn("dashboard_file", deep_records[0])


if __name__ == "__main__":
    unittest.main()
