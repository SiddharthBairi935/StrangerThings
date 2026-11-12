import tempfile
import unittest
from pathlib import Path

from app.agents import route_agent
from app.brain import build_system_prompt
from app.database import (
    delete_memory,
    get_history,
    get_memories,
    init_db,
    save_memory,
    save_message,
)


class BrainFoundationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "eleven.db"
        init_db(self.database_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_conversation_history_is_ordered(self) -> None:
        save_message(self.database_path, "c1", "user", "Hello")
        save_message(self.database_path, "c1", "assistant", "Hi")
        self.assertEqual(
            [item["content"] for item in get_history(self.database_path, "c1")],
            ["Hello", "Hi"],
        )

    def test_memory_is_saved_and_deleted_per_profile(self) -> None:
        self.assertTrue(save_memory(self.database_path, "p1", "Prefers concise answers"))
        self.assertFalse(save_memory(self.database_path, "p1", "Prefers concise answers"))
        memory_id = get_memories(self.database_path, "p1")[0]["id"]
        self.assertEqual(get_memories(self.database_path, "p2"), [])
        self.assertTrue(delete_memory(self.database_path, "p1", memory_id))
        self.assertEqual(get_memories(self.database_path, "p1"), [])

    def test_agent_routing(self) -> None:
        self.assertEqual(route_agent("Help me debug this Python API"), "coding")
        self.assertEqual(route_agent("Compare two options"), "research")
        self.assertEqual(route_agent("Hello Eleven"), "general")

    def test_prompt_includes_user_approved_memory(self) -> None:
        prompt = build_system_prompt("general", [{"content": "Prefers Hindi"}])
        self.assertIn("Prefers Hindi", prompt)


if __name__ == "__main__":
    unittest.main()
